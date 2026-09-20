# /// script
# requires-python = ">=3.11"
# dependencies = ["pyarrow"]
# ///
"""Ingest existing UP 2015 candidate CSVs without recrawling or seat inference."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import io
import json
import re
from collections import Counter
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

LABELS_BYTES = (
    Path(__file__).resolve().parents[2] / "data/catalogs/office_labels.json"
).read_bytes()
LABELS = json.loads(LABELS_BYTES)
OFFICES = LABELS["candidate_offices"]
RAW_FIELDS = LABELS["candidate_columns"]
PHONE_HEADER = LABELS["phone_column"]
COUNT_TOKEN = re.compile(
    r"(?:[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+|[0-9]{1,2}(?:,[0-9]{2})*,[0-9]{3})"
)
PERCENT_TOKEN = re.compile(r"[0-9]+(?:\.[0-9]+)?")
STRING_FIELDS = [
    "observation_id",
    "source_path",
    "source_sha256",
    "office",
    "office_label_raw",
    "district_filename_raw",
    "block_raw",
    "body_raw",
    "ward_label_raw",
    "ward_code",
    *RAW_FIELDS,
]
SCHEMA = pa.schema(
    [(name, pa.string()) for name in STRING_FIELDS]
    + [
        ("election_year", pa.int16()),
        ("source_csv_record", pa.int64()),
        ("source_line_start", pa.int64()),
        ("source_line_end", pa.int64()),
        ("valid_votes", pa.int64()),
        ("vote_percentage", pa.float64()),
        ("poll_percentage", pa.float64()),
        ("is_winner", pa.bool_()),
        ("assignment_usable", pa.bool_()),
        ("row_structure_usable", pa.bool_()),
        ("quality_flags", pa.list_(pa.string())),
    ]
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def dump_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2) + "\n")


def number(raw, field, flags, percentage=False):
    if raw is None or not raw.strip():
        return None
    token = raw.strip()
    if percentage:
        if token.endswith("%"):
            token = token[:-1].strip()
        if not PERCENT_TOKEN.fullmatch(token):
            flags.append(field + ":unparsed_numeric_token")
            return None
        try:
            value = Decimal(token)
        except InvalidOperation:
            flags.append(field + ":unparsed_numeric_token")
            return None
        if not 0 <= value <= 100:
            flags.append(field + ":outside_percentage_range")
            return None
        return float(value)
    if not COUNT_TOKEN.fullmatch(token):
        flags.append(field + ":unparsed_numeric_token")
        return None
    value = int(token.replace(",", ""))
    if value > 9223372036854775807:
        flags.append(field + ":outside_int64_range")
        return None
    return value


def ingest_file(path, source_root, writer):
    data = path.read_bytes()
    source_sha = digest(data)
    relative = path.relative_to(source_root).as_posix()
    if path.stem in OFFICES:
        district, office_label = None, path.stem
    else:
        district, separator, office_label = path.stem.partition("-")
        if not separator or office_label not in OFFICES:
            raise ValueError(f"Unrecognized source filename: {relative}")
    office = OFFICES[office_label]
    text = data.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(text, newline=""))
    header = next(reader)
    if len(set(header)) != len(header):
        raise ValueError(f"Duplicate source column names: {relative}")
    essential = [
        RAW_FIELDS[name]
        for name in (
            "seat_reservation_raw",
            "candidate_name_raw",
            "candidate_category_raw",
            "result_raw",
        )
    ]
    essential += [office[key] for key in ("block", "body", "ward") if office[key]]
    missing = [name for name in essential if name not in header]
    if missing:
        raise ValueError(f"Missing essential columns in {relative}: {missing}")
    allowed = set(RAW_FIELDS.values()) | {
        office[key] for key in ("block", "body", "ward") if office[key]
    }
    buffers = []
    count = 0
    flags_count = Counter()
    result_counts = Counter()
    seat_categories = Counter()
    candidate_categories = Counter()
    previous_line = reader.line_num
    for record_number, cells in enumerate(reader, 1):
        line_start = previous_line + 1
        previous_line = reader.line_num
        flags = []
        if len(cells) != len(header):
            flags.append("csv_field_count_mismatch")
        values = dict(zip(header, cells, strict=False))
        record = {
            "observation_id": digest(
                (relative + "\0" + source_sha + "\0" + str(record_number)).encode()
            ),
            "source_path": relative,
            "source_sha256": source_sha,
            "office": office["office"],
            "office_label_raw": office_label,
            "district_filename_raw": district,
            "election_year": 2015,
            "source_csv_record": record_number,
            "source_line_start": line_start,
            "source_line_end": previous_line,
            "block_raw": values.get(office["block"]),
            "body_raw": values.get(office["body"]),
            "ward_label_raw": values.get(office["ward"]),
            "ward_code": None,
            "is_winner": None,
            "assignment_usable": False,
        }
        record.update({name: values.get(label) for name, label in RAW_FIELDS.items()})
        for field in ("candidate_name_raw", "seat_reservation_raw"):
            if not (record[field] or "").strip():
                flags.append(field + ":blank_or_absent")
        if len(cells) == len(header):
            record["valid_votes"] = number(
                record["valid_votes_raw"], "valid_votes", flags
            )
            record["vote_percentage"] = number(
                record["vote_percentage_raw"], "vote_percentage", flags, percentage=True
            )
            record["poll_percentage"] = number(
                record["poll_percentage_raw"], "poll_percentage", flags, percentage=True
            )
        else:
            for field in ("valid_votes", "vote_percentage", "poll_percentage"):
                record[field] = None
        record["quality_flags"] = flags
        record["row_structure_usable"] = len(cells) == len(header)
        buffers.append(record)
        count += 1
        flags_count.update(flags)
        result_counts.update([record["result_raw"]])
        seat_categories.update([record["seat_reservation_raw"]])
        candidate_categories.update([record["candidate_category_raw"]])
        if len(buffers) == 5000:
            writer.write_table(pa.Table.from_pylist(buffers, schema=SCHEMA))
            buffers.clear()
    if buffers:
        writer.write_table(pa.Table.from_pylist(buffers, schema=SCHEMA))
    return {
        "source_path": relative,
        "source_sha256": source_sha,
        "bytes": len(data),
        "district_filename_raw": district,
        "office": office["office"],
        "office_label_raw": office_label,
        "source_columns": header,
        "rows": count,
        "quality_flags": dict(flags_count),
        "result_values": [
            {"raw": key, "rows": value} for key, value in result_counts.items()
        ],
        "seat_reservation_values": [
            {"raw": key, "rows": value} for key, value in seat_categories.items()
        ],
        "candidate_category_values": [
            {"raw": key, "rows": value} for key, value in candidate_categories.items()
        ],
        "excluded_phone_column_present": PHONE_HEADER in header,
        "other_unmapped_columns": [
            key for key in header if key not in allowed and key != PHONE_HEADER
        ],
        "original_url": None,
        "upstream_http_provenance_status": "not_linked_by_this_ingestion",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-root", type=Path, default=Path("data/raw/2015/winner_lists")
    )
    parser.add_argument(
        "--output-root", type=Path, default=Path("data/interim/sec_candidate_csvs_2015")
    )
    args = parser.parse_args()
    source_root = args.source_root.resolve()
    files = sorted(source_root.glob("*.csv"))
    if not files:
        raise ValueError("No input CSVs")
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    output = args.output_root.resolve() / stamp
    output.mkdir(parents=True, exist_ok=False)
    receipt = {
        "started_utc": datetime.now(UTC).isoformat(),
        "status": "ingestion_incomplete",
        "source_root": str(source_root),
        "parser_sha256": digest(Path(__file__).read_bytes()),
        "label_schema_sha256": digest(LABELS_BYTES),
        "pyarrow_version": importlib.metadata.version("pyarrow"),
        "sources": [],
        "assignment_usable": False,
        "new_paid_api_cost_usd": 0,
        "schema": {field.name: str(field.type) for field in SCHEMA},
        "scope": [
            "Existing local 2015 CSVs only; no web requests or LLM calls.",
            "Candidate observations are not deduplicated or treated as distinct seats.",
            "Seat reservation and candidate category are kept separate.",
            "Filename district labels are not modern geographic identifiers.",
            "Source ward labels are not assigned ward codes.",
            "Result strings are retained; no winner classification is imposed.",
            "Phone numbers are excluded from derived rows.",
            "Exact source files remain in place; file hashes and "
            "physical CSV line spans are retained.",
            "CSV provenance is not proof of original HTTP response provenance.",
            "No independent validation or release promotion is performed.",
        ],
    }
    dump_json(output / "INGESTION_INCOMPLETE.json", receipt)
    try:
        with pq.ParquetWriter(
            output / "candidate_observations.parquet", SCHEMA, compression="zstd"
        ) as writer:
            for path in files:
                receipt["sources"].append(ingest_file(path, source_root, writer))
    except Exception as exc:
        receipt["error"] = f"{type(exc).__name__}: {exc}"
        dump_json(output / "INGESTION_INCOMPLETE.json", receipt)
        raise
    totals = Counter()
    flag_totals = Counter()
    file_totals = Counter()
    for source in receipt["sources"]:
        totals[source["office"]] += source["rows"]
        file_totals[source["office"]] += 1
        flag_totals.update(source["quality_flags"])
    receipt.update(
        status="ingested_pending_independent_review",
        finished_utc=datetime.now(UTC).isoformat(),
        rows_by_office=dict(totals),
        files_by_office=dict(file_totals),
        quality_flags=dict(flag_totals),
        output_file="candidate_observations.parquet",
    )
    dump_json(output / "receipt.json", receipt)
    (output / "INGESTION_INCOMPLETE.json").unlink()
    print(
        json.dumps(
            {
                "output": str(output),
                "files": len(files),
                "rows": sum(totals.values()),
                "rows_by_office": dict(totals),
                "files_by_office": dict(file_totals),
                "quality_flags": dict(flag_totals),
                "new_paid_api_cost_usd": 0,
                "assignment_usable": False,
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
