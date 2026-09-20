# /// script
# requires-python = ">=3.11"
# dependencies = ["pyarrow>=14"]
# ///
"""Parse SEC's two 2000 Panchayat percentage reports, not individual seats."""

import argparse
import collections
import gzip
import hashlib
import json
import re
import subprocess
import tempfile
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

SPECS = {
    "elec00_percent_cp.pdf": {
        "title": (
            "Percentage of reservation category of Chairpersons in Panchayat"
            " Election-2000"
        ),
        "posts": [
            ("Pradhan Gram Panchayat", "gp_head"),
            ("Pramukh Khetra Panchayat", "block_head"),
            ("Adhyash Zila Panchayat", "zp_head"),
        ],
    },
    "elec00_percent_mem.pdf": {
        "title": (
            "Percentage of reservation category of Members in Panchayat Election-2000"
        ),
        "posts": [
            ("Member Gram Panchayat", "gp_ward"),
            ("Member Khetra Panchayat", "block_member"),
            ("Member Zila Panchayat", "zp_member"),
        ],
    },
}
CATEGORIES = [
    "Scheduled Tribe",
    "Scheduled Caste",
    "Backward Class",
    "General",
    "Total",
]
SEX = [("Female", "female"), ("Male", "male"), ("Total", "all")]
FLAGS = (
    "aggregate_not_seat_assignment;reservation_interpretation_unvalidated;"
    "independent_review_pending"
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def extract(data, report, spec):
    with tempfile.TemporaryDirectory(prefix="up-pri2000-") as temporary:
        pdf = Path(temporary) / "source.pdf"
        pdf.write_bytes(data)
        result = subprocess.run(
            ["pdftotext", "-layout", str(pdf), "-"],
            check=True,
            capture_output=True,
            text=True,
        )
    pages = [p for p in result.stdout.split("\f") if p.strip()]
    if len(pages) != 1:
        raise ValueError("Expected a single-page percentage table")
    text = pages[0]
    if spec["title"] not in text or not re.search(r"Female\s+Male\s+Total", text):
        raise ValueError("Percentage report title or column order differs")
    parsed = []
    serial = None
    for line_number, line in enumerate(text.splitlines(), 1):
        compact = " ".join(line.split())
        first = re.fullmatch(r"([123]) (.+?) (Scheduled Tribe)(.*)", compact)
        if first:
            serial = int(first[1])
            if first[2] != spec["posts"][serial - 1][0]:
                raise ValueError("Unexpected printed post")
            category, tail = first[3], first[4]
        else:
            other = re.fullmatch(
                r"(Scheduled Caste|Backward [Cc]lass|General|Total)(.*)", compact
            )
            if not other:
                if re.search(r"\d+\.\d{2}", compact):
                    raise ValueError("Unparsed numeric table line")
                continue
            if serial is None:
                raise ValueError("Category appears before its post")
            category, tail = other.groups()
        values = tail.split()
        if len(values) not in (0, 3):
            raise ValueError("Partial percentage row cannot be positioned safely")
        if any(not re.fullmatch(r"\d{1,3}\.\d{2}", v) for v in values):
            raise ValueError("Unexpected percentage token")
        numbers = [Decimal(v) for v in values]
        if any(not Decimal(0) <= n <= Decimal(100) for n in numbers):
            raise ValueError("Percentage outside 0..100")
        category_normalized = (
            "Backward Class" if category.lower() == "backward class" else category
        )
        expected_serial = len(parsed) // 5 + 1
        if (
            serial != expected_serial
            or category_normalized != CATEGORIES[len(parsed) % 5]
        ):
            raise ValueError(
                "Source post/category rows missing, duplicated or reordered"
            )
        post, tier = spec["posts"][serial - 1]
        parsed.append(
            {
                "post_raw": post,
                "tier": tier,
                "category_raw": category,
                "category_normalized": category_normalized,
                "source_text_line": line_number,
                "source_line_raw": line,
                "source_table_row": len(parsed) + 1,
                "values_raw": values or [None, None, None],
            }
        )
    if len(parsed) != 15:
        raise ValueError("Expected all 15 post/category rows")
    records = []
    for row in parsed:
        for offset, (sex_raw, sex) in enumerate(SEX):
            raw = row["values_raw"][offset]
            coordinate = (
                f"{report['source_sha256']}:1:{row['source_table_row']}:{offset + 4}"
            )
            records.append(
                {
                    "observation_id": digest(coordinate.encode()),
                    "election_year": 2000,
                    "state": "Uttar Pradesh",
                    "tier": row["tier"],
                    "post_raw": row["post_raw"],
                    "category_raw": row["category_raw"],
                    "category_normalized": row["category_normalized"],
                    "sex_label_raw": sex_raw,
                    "sex_label_normalized": sex,
                    "percentage_raw": raw,
                    "percentage": Decimal(raw) if raw is not None else None,
                    "measure": (
                        "reported_reservation_category_percentage_of_elected_officeholders"
                    ),
                    "source_url": report["url"],
                    "source_sha256": report["source_sha256"],
                    "source_response_path": report["source_response_path"],
                    "source_index_url": report["source_index_url"],
                    "source_index_sha256": report["source_index_sha256"],
                    "source_page": 1,
                    "source_table_row": row["source_table_row"],
                    "source_column": offset + 4,
                    "source_text_line": row["source_text_line"],
                    "source_line_raw": row["source_line_raw"],
                    "source_header_raw": "Female | Male | Total",
                    "quality_flags": (
                        FLAGS + (";source_cell_blank" if raw is None else "")
                    ),
                    "assignment_usable": False,
                }
            )
    return records


def arithmetic(records):
    groups = collections.defaultdict(dict)
    for row in records:
        groups[row["tier"]][
            (row["category_normalized"], row["sex_label_normalized"])
        ] = row
    checks = []

    def compare(tier, kind, label, components, total):
        values = [r["percentage"] for r in components]
        complete = (
            all(v is not None for v in values) and total["percentage"] is not None
        )
        residual = sum(values, Decimal(0)) - total["percentage"] if complete else None
        status = "incomplete_source_cells"
        if complete:
            status = (
                "agrees"
                if residual == 0
                else (
                    "small_reported_difference"
                    if abs(residual) <= Decimal("0.02")
                    else "source_arithmetic_discrepancy"
                )
            )
        check = {
            "tier": tier,
            "check": kind,
            "label": label,
            "status": status,
            "difference_percentage_points": (
                str(residual) if residual is not None else None
            ),
            "related_observation_ids": (
                [r["observation_id"] for r in components] + [total["observation_id"]]
            ),
        }
        checks.append(check)
        if complete and residual != 0:
            for row in [*components, total]:
                flag = ";" + status
                if flag not in row["quality_flags"]:
                    row["quality_flags"] += flag

    for tier, cells in groups.items():
        for category in CATEGORIES:
            compare(
                tier,
                "female_plus_male_equals_total",
                category,
                [cells[category, sex] for sex in ("female", "male")],
                cells[category, "all"],
            )
        for _, sex in SEX:
            compare(
                tier,
                "category_sum_equals_printed_total",
                sex,
                [cells[category, sex] for category in CATEGORIES[:-1]],
                cells["Total", sex],
            )
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.source_root.resolve()
    receipt_bytes = (root / "acquisition_receipt.json").read_bytes()
    acquisition = json.loads(receipt_bytes)
    records, inputs = [], []
    for filename, spec in SPECS.items():
        url = "https://sec.up.nic.in/site/fonts/" + filename
        matches = [r for r in acquisition["reports"] if r["url"] == url]
        if len(matches) != 1 or matches[0]["election_year"] != 2000:
            raise ValueError("Missing or ambiguous acquired 2000 source")
        report = matches[0]
        path = (root / report["source_response_path"]).resolve()
        if not path.is_relative_to(root):
            raise ValueError("Source path escapes acquisition root")
        data = gzip.decompress(path.read_bytes())
        if digest(data) != report["source_sha256"] or not data.startswith(b"%PDF-"):
            raise ValueError("Cached PDF does not match acquisition receipt")
        records.extend(extract(data, report, spec))
        inputs.append({"source_url": url, "source_sha256": report["source_sha256"]})
    checks = arithmetic(records)
    table = pa.Table.from_pylist(records)
    position = table.schema.get_field_index("percentage")
    table = table.set_column(
        position, "percentage", table["percentage"].cast(pa.decimal128(5, 2))
    )
    args.output.mkdir(parents=True, exist_ok=False)
    artifact = args.output / "reported_percentages.parquet"
    pq.write_table(table, artifact, compression="zstd")
    receipt = {
        "parsed_utc": datetime.now(UTC).isoformat(),
        "records": len(records),
        "source_reports": len(inputs),
        "blank_source_cells": sum(r["percentage"] is None for r in records),
        "acquisition_root": str(args.source_root),
        "acquisition_receipt_sha256": digest(receipt_bytes),
        "inputs": inputs,
        "script_sha256": digest(Path(__file__).read_bytes()),
        "artifact_sha256": digest(artifact.read_bytes()),
        "arithmetic_status_counts": dict(
            collections.Counter(c["status"] for c in checks)
        ),
        "scope": (
            "Published aggregate percentages, not seat allocations or individual"
            " records."
        ),
        "geographic_scope": (
            "As printed in the historical reports; no current-boundary equivalence"
            " asserted."
        ),
        "blank_policy": "Blank source cells remain null, never zero.",
        "correction_policy": (
            "Printed arithmetic discrepancies are retained, never silently corrected."
        ),
        "assignment_usable": False,
        "paid_api_cost_added_usd": 0,
    }
    dictionary = {
        "unit": (
            "One printed percentage cell, including explicit blank cells and total"
            " rows."
        ),
        "percentage": (
            "Decimal percentage on 0..100 scale; null only for a blank source cell."
        ),
        "percentage_raw": "Exact printed decimal token or null, not an inferred value.",
        "category_normalized": (
            "Printed grouping label with capitalization normalized, not a seat"
            " reservation assignment."
        ),
        "sex_label_normalized": (
            "Printed female, male or combined-total column; not inferred from names."
        ),
        "source_coordinates": (
            "One-based PDF page, table row, table column and pdftotext layout line."
        ),
        "source_response_path": (
            "Gzip-compressed original PDF, relative to acquisition_root in"
            " parse_receipt.json."
        ),
        "quality_flags": "Semicolon-delimited source and interpretation holds.",
        "arithmetic": (
            "Exact decimal comparisons; small_reported_difference is not a claim that"
            " rounding caused it."
        ),
        "assignment_usable": (
            "Always false; aggregates must not be joined as identified seat"
            " assignments."
        ),
        "schema": {field.name: str(field.type) for field in table.schema},
    }
    for filename, value in (
        ("parse_receipt.json", receipt),
        ("arithmetic_checks.json", checks),
        ("dictionary.json", dictionary),
    ):
        (args.output / filename).write_text(
            json.dumps(value, ensure_ascii=True, indent=2) + "\n"
        )
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
