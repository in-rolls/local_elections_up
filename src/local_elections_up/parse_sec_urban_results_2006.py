#!/usr/bin/env python3
"""Extract 2006 SEC urban candidate tables, retaining legacy text and geometry."""

import argparse
import gzip
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
COLUMNS = (
    ("printed_serial_raw", 10, 42),
    ("nomination_number_raw", 42, 82),
    ("candidate_name_encoded_raw", 82, 220),
    ("related_person_encoded_raw", 220, 358),
    ("sex_encoded_raw", 358, 393),
    ("age_raw", 393, 417),
    ("candidate_category_encoded_raw", 417, 520),
    ("party_encoded_raw", 520, 635),
    ("symbol_encoded_raw", 635, 770),
    ("valid_votes_raw", 770, 850),
)
BODY_TYPES = {
    (
        "\u00ae\u00e2\u00a3\u00fb\u2122\u00f9\u00ae\u00e2\u00a3\u00fb\u00b3\u00e2"
    ): "municipal_corporation",
    (
        "\u00ae\u00e2\u00a3\u00fb\u2122\u00af\u00e2\u00fb\u00f9\u00b6\u00e2\u00fd"
        "\u00f4\u00fb\u00af\u00e2\u00fc\u2122\u00b9\u00e2\u2014"
    ): ("municipal_council"),
    (
        "\u00ae\u00e2\u00a3\u00fb\u2122\u00af\u00e2\u2039\u00a5\u00e2\u00fb\u00b4"
        "\u00e2\u00ab\u00e2"
    ): ("nagar_panchayat"),
}
STRINGS = (
    "observation_id",
    "state",
    "office",
    "office_scope",
    "record_kind",
    "source_path",
    "source_sha256",
    "source_url",
    "district_name_english_raw",
    "body_type_encoded_raw",
    "body_name_encoded_raw",
    "ward_number_raw",
    "ward_name_encoded_raw",
    "office_label_encoded_raw",
    "seat_reservation_encoded_raw",
    "text_encoding",
    "cell_bboxes_json",
    "page_context_json",
    *tuple(name for name, _, _ in COLUMNS),
)
SCHEMA = pa.schema(
    [(name, pa.string()) for name in STRINGS]
    + [
        ("election_year", pa.int16()),
        ("source_page", pa.int32()),
        ("source_row_on_page", pa.int32()),
        ("printed_serial", pa.int32()),
        ("nomination_number", pa.int32()),
        ("age", pa.int32()),
        ("valid_votes", pa.int64()),
        ("ward_number", pa.int32()),
        ("is_winner", pa.bool_()),
        ("assignment_usable", pa.bool_()),
        ("quality_flags", pa.list_(pa.string())),
    ]
)


def file_hash(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def dump(path, value):
    path.write_text(
        json.dumps(value, ensure_ascii=True, indent=2) + "\n", encoding="utf-8"
    )


def text(words):
    return " ".join(w["text"] for w in sorted(words, key=lambda w: (w["y0"], w["x0"])))


def region(words, x0, x1, y0, y1):
    return [word for word in words if x0 <= word["x0"] < x1 and y0 <= word["y0"] < y1]


def after(value, prefix):
    return value.split(prefix, 1)[1].strip() if prefix in value else None


def integer(value):
    value = (value or "").strip()
    return int(value) if re.fullmatch(r"[0-9]+", value) else None


def context(words, scope):
    district = text(region(words, 0, 250, 32, 65))
    english = re.search(r"\(([^()]+)\)", district)
    body = after(text(region(words, 250, 490, 32, 48)), "fudk; dk uke&")
    body_type = BODY_TYPES.get(re.sub(r"\s+", "", body or ""))
    office = None
    if body_type == "municipal_corporation":
        office = (
            "municipal_corporation_mayor"
            if scope == "head"
            else "municipal_corporation_ward_member"
        )
    elif body_type:
        office = body_type + ("_chair" if scope == "head" else "_ward_member")
    reservation_zone = (490, 735, 45, 65) if scope == "head" else (620, 850, 32, 48)
    reservation = after(text(region(words, *reservation_zone)), "in dk vkj{k.k &")
    ward = after(text(region(words, 490, 625, 32, 48)), "okMZ la[;k&")
    return {
        "office": office,
        "district_name_english_raw": english.group(1) if english else None,
        "body_type_encoded_raw": body,
        "body_name_encoded_raw": text(region(words, 250, 490, 48, 65)) or None,
        "ward_number_raw": ward if scope == "member" else None,
        "ward_name_encoded_raw": (
            after(text(region(words, 490, 625, 48, 65)), "okMZ dk uke&")
            if scope == "member"
            else None
        ),
        "office_label_encoded_raw": after(
            text(region(words, 490, 725, 15, 33)), "in dk uke&"
        ),
        "seat_reservation_encoded_raw": reservation or None,
        "district_heading_encoded_raw": district,
    }


def parse_page(page, source, source_sha, number, scope):
    words = [
        {
            "text": word.text or "",
            "x0": float(word.attrib["xMin"]),
            "x1": float(word.attrib["xMax"]),
            "y0": float(word.attrib["yMin"]),
            "y1": float(word.attrib["yMax"]),
        }
        for word in page.iter()
        if word.tag.endswith("}word")
    ]
    info = {
        "source_path": source,
        "source_sha256": source_sha,
        "source_page": number,
        "page_attributes": page.attrib,
        "words": words,
        "issues": [],
    }
    if "mEehnokj dk uke" not in text(region(words, 82, 220, 64, 81)):
        info["issues"].append("candidate_table_header_unrecognized")
        return [], info
    if "izkIr" not in text(region(words, 770, 850, 64, 81)):
        info["issues"].append("votes_column_header_unrecognized")
        return [], info
    anchors = sorted(
        [
            word
            for word in region(words, 10, 42, 115, 800)
            if integer(word["text"]) is not None
        ],
        key=lambda word: word["y0"],
    )
    ctx = context(words, scope)
    info["context"] = ctx
    totals = [
        word
        for word in words
        if word["text"] == ";ksx" and word["x0"] > 600 and word["y0"] > 115
    ]
    rows = []
    for index, anchor in enumerate(anchors):
        top = anchor["y0"] - 4
        bottom = (
            anchors[index + 1]["y0"] - 4
            if index + 1 < len(anchors)
            else anchor["y0"] + 36
        )
        next_total = [w["y0"] for w in totals if w["y0"] > anchor["y0"]]
        if next_total:
            bottom = min(bottom, min(next_total))
        cells = {
            name: region(words, left, right, top, bottom)
            for name, left, right in COLUMNS
        }
        values = {name: text(cell) or None for name, cell in cells.items()}
        flags = [
            "legacy_font_decode_pending",
            "independent_source_review_pending",
            "candidate_record_not_explicit_winner",
        ]
        if ctx["office"] is None:
            flags.append("urban_body_type_unresolved")
        if ctx["seat_reservation_encoded_raw"] is None:
            flags.append("seat_reservation_not_read")
        for field in (
            "printed_serial_raw",
            "nomination_number_raw",
            "age_raw",
            "valid_votes_raw",
        ):
            if integer(values[field]) is None:
                flags.append(field + "_not_integer")
        for name, _left, right in COLUMNS:
            if any(w["x1"] > right + 1 for w in cells[name]):
                flags.append(name + "_crosses_column_boundary")
        if not values["candidate_name_encoded_raw"]:
            flags.append("candidate_name_missing")
        if scope == "member" and integer(ctx["ward_number_raw"]) is None:
            flags.append("ward_identifier_unresolved")
        row = {field.name: None for field in SCHEMA}
        row.update({key: value for key, value in ctx.items() if key in row})
        row.update(values)
        row.update(
            observation_id=hashlib.sha256(
                f"{source_sha}:{number}:{index + 1}".encode()
            ).hexdigest(),
            state="Uttar Pradesh",
            election_year=2006,
            office_scope=scope,
            record_kind="candidate_record",
            source_path=source,
            source_sha256=source_sha,
            source_page=number,
            source_row_on_page=index + 1,
            text_encoding="legacy_pdf_font_encoding_unresolved",
            printed_serial=integer(values["printed_serial_raw"]),
            nomination_number=integer(values["nomination_number_raw"]),
            age=integer(values["age_raw"]),
            valid_votes=integer(values["valid_votes_raw"]),
            ward_number=integer(ctx["ward_number_raw"]),
            assignment_usable=False,
            is_winner=None,
            quality_flags=flags,
            cell_bboxes_json=json.dumps(cells, ensure_ascii=True),
            page_context_json=json.dumps(ctx, ensure_ascii=True),
        )
        rows.append(row)
    info["candidate_rows"] = len(rows)
    info["candidate_vote_sum"] = sum(row["valid_votes"] or 0 for row in rows)
    info["printed_totals"] = [
        {
            "label_bbox": total,
            "value_raw": text(
                [w for w in region(words, 770, 850, total["y0"] - 4, total["y1"] + 4)]
            ),
        }
        for total in totals
    ]
    if not rows:
        info["issues"].append("no_candidate_row_anchors")
    serials = [row["printed_serial"] for row in rows]
    if rows and serials != list(range(serials[0], serials[0] + len(rows))):
        info["issues"].append("printed_serial_sequence_disagrees")
    info["vote_sum_check"] = "not_applicable_or_incomplete_table"
    if (
        rows
        and serials[0] == 1
        and len(totals) == 1
        and all(row["valid_votes"] is not None for row in rows)
    ):
        declared = integer(info["printed_totals"][0]["value_raw"])
        if declared is not None:
            agrees = declared == info["candidate_vote_sum"]
            info["vote_sum_check"] = "agrees" if agrees else "disagrees"
            if not agrees:
                info["issues"].append("candidate_votes_disagree_with_printed_total")
    for row in rows:
        row["quality_flags"].extend(info["issues"])
    return rows, info


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-root", type=Path, default=ROOT / "data/interim/sec_urban_results_2006"
    )
    parser.add_argument(
        "--source", action="append", help="Repo-relative PDF; repeatable"
    )
    args = parser.parse_args()
    sources = (
        [ROOT / relative for relative in args.source]
        if args.source
        else sorted((ROOT / "data/2006").glob("ulb_*/*.pdf"))
    )
    if not sources:
        raise ValueError("No 2006 urban PDFs found")
    for source in sources:
        if source.parent.name not in {"ulb_chairperson", "ulb_member"}:
            raise ValueError(f"Unknown source family: {source}")
        source.resolve().relative_to(ROOT.resolve())
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    output = args.output_root / stamp
    output.mkdir(parents=True, exist_ok=False)
    receipt = {
        "status": "incomplete",
        "assignment_usable": False,
        "parser_sha256": file_hash(Path(__file__)),
        "sources": [],
        "new_paid_api_cost_usd": 0,
        "schema": {field.name: str(field.type) for field in SCHEMA},
        "notes": [
            (
                "Candidate rows, not declared winners; do not infer election from row"
                " order."
            ),
            "Candidate category is not the seat-reservation category.",
            (
                "Original PDFs remain at source_path; bbox XHTML and page words are"
                " cached."
            ),
            (
                "Coordinates use Poppler output without clipping to its rotated-page"
                " width."
            ),
            "Body-type mappings cover three source-image-reviewed labels.",
        ],
    }
    dump(output / "INCOMPLETE.json", receipt)
    buffer, quality, offices, page_checks = [], Counter(), Counter(), Counter()
    failures = 0
    with (
        pq.ParquetWriter(
            output / "candidate_observations.parquet", SCHEMA, compression="zstd"
        ) as writer,
        gzip.open(output / "pages.jsonl.gz", "wt", encoding="utf-8") as pages_stream,
    ):
        for source in sources:
            sha = file_hash(source)
            scope = "head" if source.parent.name == "ulb_chairperson" else "member"
            relative = source.relative_to(ROOT).as_posix()
            item = {
                "source_path": relative,
                "source_sha256": sha,
                "office_scope": scope,
            }
            try:
                result = subprocess.run(
                    ["pdftotext", "-bbox-layout", str(source), "-"],
                    capture_output=True,
                    check=True,
                    timeout=120,
                )
                (output / f"{sha}.xhtml.gz").write_bytes(
                    gzip.compress(result.stdout, mtime=0)
                )
                tree = ET.fromstring(result.stdout)
                pages = [node for node in tree.iter() if node.tag.endswith("}page")]
                item.update(pages=len(pages), rows=0, page_issues=Counter())
                for number, page in enumerate(pages, 1):
                    rows, info = parse_page(page, relative, sha, number, scope)
                    item["rows"] += len(rows)
                    item["page_issues"].update(info["issues"])
                    page_checks.update([info.get("vote_sum_check", "unparsed_page")])
                    pages_stream.write(json.dumps(info, ensure_ascii=True) + "\n")
                    for row in rows:
                        quality.update(row["quality_flags"])
                        offices.update([row["office"] or "unresolved"])
                    buffer.extend(rows)
                    if len(buffer) >= 5000:
                        writer.write_table(pa.Table.from_pylist(buffer, schema=SCHEMA))
                        buffer.clear()
                item["status"] = "parsed_pending_validation"
                if result.stderr:
                    item["poppler_stderr"] = result.stderr.decode(
                        "utf-8", errors="replace"
                    )
            except (subprocess.SubprocessError, ET.ParseError) as error:
                failures += 1
                item.update(status="source_failed", error=str(error))
            receipt["sources"].append(item)
            print(
                json.dumps(
                    {
                        key: item[key]
                        for key in ("source_path", "status", "rows")
                        if key in item
                    }
                ),
                flush=True,
            )
        if buffer:
            writer.write_table(pa.Table.from_pylist(buffer, schema=SCHEMA))
    receipt.update(
        status=(
            "parsed_with_source_failures" if failures else "parsed_pending_validation"
        ),
        rows=sum(offices.values()),
        rows_by_office=dict(offices),
        quality_flags=dict(quality),
        page_vote_checks=dict(page_checks),
        source_failures=failures,
        parquet_sha256=file_hash(output / "candidate_observations.parquet"),
        pages_sha256=file_hash(output / "pages.jsonl.gz"),
    )
    dump(output / "receipt.json", receipt)
    if not failures:
        (output / "INCOMPLETE.json").unlink()
    print(
        json.dumps(
            {
                "output": str(output),
                "rows": receipt["rows"],
                "files": len(sources),
                "source_failures": failures,
                "rows_by_office": dict(offices),
                "page_vote_checks": dict(page_checks),
                "assignment_usable": False,
                "new_paid_api_cost_usd": 0,
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
