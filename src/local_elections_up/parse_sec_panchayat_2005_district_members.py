# /// script
# requires-python = ">=3.11"
# dependencies = ["pyarrow>=14"]
# ///
"""Extract source observations from the archived UP 2005 district-member PDF."""

import argparse
import bisect
import collections
import gzip
import hashlib
import itertools
import json
import os
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

PDF_SHA256 = "31c717dc34d4697fca586e02a1846ecb9a876f93aa6479336434f554407f5dad"
NS = {"x": "http://www.w3.org/1999/xhtml"}
TITLE = "lkekU; fuokZpu&2005 esa fuokZfpr v/;{k@lnL; ftyk iapk;r dh lwph"
COLUMNS = [
    ("ward_number", 90.0, 125.0, "okMZ la0"),
    ("ward_name", 125.0, 215.0, "okMZ dk uke"),
    ("candidate_name", 215.0, 345.0, "fot;h mEehnokj dk uke"),
    ("sex", 345.0, 383.0, "fyax"),
    ("category", 383.0, 495.0, "vkj{k.k Js.kh"),
    ("office", 495.0, 560.0, "in dk uke"),
]
BASE_HOLDS = [
    "legacy_text_names_undecoded",
    "independent_review_pending",
    "reservation_assignment_unadjudicated",
    "historical_geography_unmapped",
]


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def now():
    return datetime.now(UTC).isoformat()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2) + "\n")


def text_from_words(words):
    ordered = sorted(words, key=lambda w: (w["y_min"], w["x_min"], w["source_word"]))
    lines = []
    for word in ordered:
        if not lines or word["y_min"] - lines[-1][0]["y_min"] > 2.5:
            lines.append([])
        lines[-1].append(word)
    return "\n".join(
        " ".join(w["text_encoded_raw"] for w in sorted(line, key=lambda w: w["x_min"]))
        for line in lines
    )


def lookup_text(value):
    return " ".join(value.split()) if value else ""


def page_words(page, number):
    return [
        {
            "source_sha256": PDF_SHA256,
            "source_page": number,
            "source_word": ordinal,
            "text_encoded_raw": element.text or "",
            "x_min": float(element.attrib["xMin"]),
            "y_min": float(element.attrib["yMin"]),
            "x_max": float(element.attrib["xMax"]),
            "y_max": float(element.attrib["yMax"]),
            "observation_id": None,
            "column": None,
            "source_region": "unclassified",
        }
        for ordinal, element in enumerate(page.findall(".//x:word", NS), 1)
    ]


def parse_page(page, number, words, vocabulary):
    flags = []
    if (
        abs(float(page.attrib["width"]) - 595) > 0.1
        or abs(float(page.attrib["height"]) - 842) > 0.1
    ):
        flags.append("unexpected_page_geometry")
    title = text_from_words([w for w in words if 80 <= w["y_min"] < 100])
    if lookup_text(title) != TITLE:
        flags.append("unexpected_title")
    district_codes = [
        w["text_encoded_raw"]
        for w in words
        if 100 <= w["y_min"] < 125
        and 190 <= w["x_min"] < 235
        and re.fullmatch(r"\d{4}", w["text_encoded_raw"])
    ]
    district_name = text_from_words(
        [w for w in words if 100 <= w["y_min"] < 125 and w["x_min"] >= 235]
    )
    if len(district_codes) != 1 or not district_name:
        flags.append("district_header_unresolved")
    for name, left, right, expected in COLUMNS:
        header = text_from_words(
            [w for w in words if 125 <= w["y_min"] < 145 and left <= w["x_min"] < right]
        )
        if lookup_text(header) != expected:
            flags.append("unexpected_header_" + name)
    footer = [
        w["text_encoded_raw"]
        for w in words
        if 740 <= w["y_min"] < 770
        and 300 <= w["x_min"] < 335
        and re.fullmatch(r"\d+", w["text_encoded_raw"])
    ]
    printed_page = footer[0] if len(footer) == 1 else None
    if printed_page is None:
        flags.append("printed_page_unresolved")
    for word in words:
        y = word["y_min"]
        word["source_region"] = (
            "title"
            if 80 <= y < 100
            else (
                "district_header"
                if 100 <= y < 125
                else (
                    "column_header"
                    if 125 <= y < 145
                    else (
                        "body"
                        if 145 <= y < 735
                        else "footer"
                        if 740 <= y < 770
                        else "outside_expected_regions"
                    )
                )
            )
        )
    report = {
        "source_page": number,
        "printed_page_raw": printed_page,
        "district_code_raw": district_codes[0] if len(district_codes) == 1 else None,
        "district_name_encoded_raw": district_name or None,
        "source_words": len(words),
        "page_flags": flags,
        "row_observations": 0,
        "unassigned_body_words": 0,
    }
    body = [w for w in words if w["source_region"] == "body"]
    if flags:
        report["unassigned_body_words"] = len(body)
        return [], report
    anchors = sorted(
        [
            w
            for w in body
            if 90 <= w["x_min"] < 125 and re.fullmatch(r"\d+", w["text_encoded_raw"])
        ],
        key=lambda w: (w["y_min"], w["x_min"]),
    )
    if not anchors or any(
        second["y_min"] - first["y_min"] < 5
        for first, second in itertools.pairwise(anchors)
    ):
        report["page_flags"].append("ward_row_anchors_unresolved")
        report["unassigned_body_words"] = len(body)
        return [], report
    starts = [w["y_min"] - 3.0 for w in anchors]
    buckets = [[] for _ in anchors]
    for word in body:
        position = bisect.bisect_right(starts, word["y_min"]) - 1
        if position < 0:
            report["unassigned_body_words"] += 1
        else:
            buckets[position].append(word)
    rows = []
    for ordinal, (anchor, bucket) in enumerate(zip(anchors, buckets, strict=False), 1):
        identity = f"{PDF_SHA256}:{number}:{anchor['source_word']}"
        observation_id = sha256(identity.encode())
        cells = {name: [] for name, *_ in COLUMNS}
        row_flags = []
        for word in bucket:
            word["observation_id"] = observation_id
            column = next(
                (
                    (name, right)
                    for name, left, right, _ in COLUMNS
                    if left <= word["x_min"] < right
                ),
                None,
            )
            if column is None:
                row_flags.append("word_outside_columns")
                continue
            name, right = column
            word["column"] = name
            cells[name].append(word)
            if word["x_max"] > right + 1:
                row_flags.append("column_overflow_" + name)
        raw = {name: text_from_words(values) or None for name, values in cells.items()}
        for name, value in raw.items():
            if value is None:
                row_flags.append("missing_" + name)
        if raw["ward_number"] != anchor["text_encoded_raw"]:
            row_flags.append("ambiguous_ward_number_cell")
        office = vocabulary["office"].get(lookup_text(raw["office"]))
        sex = vocabulary["sex"].get(lookup_text(raw["sex"]))
        category = vocabulary["category"].get(lookup_text(raw["category"]))
        for name, entry in (("office", office), ("sex", sex), ("category", category)):
            if entry is None:
                row_flags.append("unmapped_" + name)
        if report["unassigned_body_words"]:
            row_flags.append("page_contains_unassigned_body_words")
        rows.append(
            {
                "observation_id": observation_id,
                "source_sha256": PDF_SHA256,
                "source_page": number,
                "source_row_on_page": ordinal,
                "source_anchor_word": anchor["source_word"],
                "printed_page_raw": printed_page,
                "election_year": 2005,
                "district_code_raw": district_codes[0],
                "district_name_encoded_raw": district_name,
                "ward_number_raw": raw["ward_number"],
                "ward_number_in_result": int(anchor["text_encoded_raw"]),
                "ward_name_encoded_raw": raw["ward_name"],
                "candidate_name_encoded_raw": raw["candidate_name"],
                "sex_encoded_raw": raw["sex"],
                "category_encoded_raw": raw["category"],
                "office_encoded_raw": raw["office"],
                "office_normalized": office["normalized"] if office else None,
                "reported_sex": sex["normalized"] if sex else None,
                "reported_category_caste": category["caste"] if category else None,
                "reported_category_woman": category["woman"] if category else None,
                "district_name": None,
                "ward_name": None,
                "candidate_name": None,
                "row_x_min": min(w["x_min"] for w in bucket),
                "row_y_min": min(w["y_min"] for w in bucket),
                "row_x_max": max(w["x_max"] for w in bucket),
                "row_y_max": max(w["y_max"] for w in bucket),
                "source_word_count": len(bucket),
                "row_structure_usable": not row_flags,
                "structural_flags": sorted(set(row_flags)),
                "quality_flags": BASE_HOLDS + sorted(set(row_flags)),
                "assignment_usable": False,
            }
        )
    report["row_observations"] = len(rows)
    return rows, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--fontconfig", type=Path)
    args = parser.parse_args()
    root = args.source_root.resolve()
    ledger = root / "downloads.jsonl"
    events = [
        json.loads(line) for line in ledger.read_text().splitlines() if line.strip()
    ]
    sources = [
        event
        for event in events
        if event.get("status") == "pdf_acquired"
        and event.get("body", {}).get("sha256") == PDF_SHA256
    ]
    if not sources:
        parser.error(
            "No successful acquisition of the supported PDF in downloads.jsonl"
        )
    source = (root / sources[0]["body"]["path"]).resolve()
    if not source.is_relative_to(root):
        parser.error("Source path escapes the acquisition root")
    pdf_bytes = gzip.decompress(source.read_bytes())
    if sha256(pdf_bytes) != PDF_SHA256:
        parser.error("Cached source PDF differs from the supported SHA-256")
    vocabulary_path = root / "arjun_first_page_vocabulary.json"
    vocabulary_bytes = vocabulary_path.read_bytes()
    review = json.loads(vocabulary_bytes)
    if review["source_sha256"] != PDF_SHA256 or review["source_page"] != 1:
        parser.error("Categorical vocabulary refers to a different source")
    vocabulary = {"office": {}, "sex": {}, "category": {}}
    for entry in review["entries"]:
        field, key = entry["field"], entry["encoded_raw"]
        if field not in vocabulary or key in vocabulary[field]:
            parser.error("Invalid or duplicate categorical vocabulary entry")
        vocabulary[field][key] = entry
    environment = dict(os.environ)
    fontconfig_sha = None
    if args.fontconfig:
        fontconfig_sha = sha256(args.fontconfig.read_bytes())
        environment["FONTCONFIG_FILE"] = str(args.fontconfig.resolve())
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    output = root / "parsed_members_2005" / stamp
    output.mkdir(parents=True, exist_ok=False)
    receipt = {
        "started_utc": now(),
        "status": "incomplete",
        "source_sha256": PDF_SHA256,
        "source_response_path": str(source),
        "acquisition_events": sources,
        "vocabulary_sha256": sha256(vocabulary_bytes),
        "vocabulary_path": str(vocabulary_path),
        "fontconfig_sha256": fontconfig_sha,
        "fontconfig_path": str(args.fontconfig.resolve()) if args.fontconfig else None,
        "script_sha256": sha256(Path(__file__).read_bytes()),
        "output": str(output),
        "assignment_usable": False,
        "new_paid_api_cost_usd": 0,
    }
    write_json(output / "parse_receipt.json", receipt)
    try:
        with tempfile.TemporaryDirectory(prefix="up-zp2005-") as directory:
            pdf = Path(directory) / "source.pdf"
            pdf.write_bytes(pdf_bytes)
            command = ["pdftotext", "-bbox-layout", "-enc", "UTF-8", str(pdf), "-"]
            result = subprocess.run(
                command, capture_output=True, env=environment, check=True
            )
        xml_bytes = result.stdout
        (output / "source_bbox.xhtml.gz").write_bytes(gzip.compress(xml_bytes, mtime=0))
        receipt["bbox_sha256"] = sha256(xml_bytes)
        receipt["pdftotext_stderr_raw"] = result.stderr.decode(
            "utf-8", errors="replace"
        )
        xml = ET.fromstring(xml_bytes)
        pages = xml.findall(".//x:page", NS)
        if len(pages) != 109:
            raise ValueError(f"Expected 109 source pages, found {len(pages)}")
        all_words, rows, page_reports = [], [], []
        for number, page in enumerate(pages, 1):
            words = page_words(page, number)
            observations, report = parse_page(page, number, words, vocabulary)
            all_words.extend(words)
            rows.extend(observations)
            page_reports.append(report)
        keys = collections.Counter(
            (
                row["district_code_raw"],
                row["office_normalized"],
                row["ward_number_in_result"],
            )
            for row in rows
        )
        for row in rows:
            key = (
                row["district_code_raw"],
                row["office_normalized"],
                row["ward_number_in_result"],
            )
            if keys[key] > 1:
                row["structural_flags"].append("duplicate_reported_office_ward_key")
                row["quality_flags"].append("duplicate_reported_office_ward_key")
                row["row_structure_usable"] = False
        words_table = pa.Table.from_pylist(all_words)
        for field in ("observation_id", "column"):
            index = words_table.schema.get_field_index(field)
            words_table = words_table.set_column(
                index, field, words_table[field].cast(pa.string())
            )
        pq.write_table(words_table, output / "source_words.parquet", compression="zstd")
        if rows:
            table = pa.Table.from_pylist(rows)
            for field in ("district_name", "ward_name", "candidate_name"):
                index = table.schema.get_field_index(field)
                table = table.set_column(index, field, table[field].cast(pa.string()))
            pq.write_table(
                table, output / "member_observations.parquet", compression="zstd"
            )
        write_json(output / "page_coverage.json", page_reports)
        write_json(
            output / "dictionary.json",
            {
                "scope": (
                    "Observations in one archived 2005 PDF; not certified statewide"
                    " election coverage."
                ),
                "encoded_raw": (
                    "Legacy-font text extracted from PDF character codes, not readable"
                    " Unicode Hindi."
                ),
                "text_order": (
                    "Words ordered by coordinates within a cell; wrapped lines retained"
                    " as newlines."
                ),
                "categorical_lookup": (
                    "Exact reviewed strings after whitespace-only joining; unmatched"
                    " values held."
                ),
                "source_words.parquet": (
                    "Every extracted word, including headers, footers and unassigned"
                    " text, with original coordinates."
                ),
                "ward_number_in_result": (
                    "Printed result ward. A chair row's ward is not automatically the"
                    " identifier of the chair office."
                ),
                "reported_category": (
                    "Source-reported category. Not adjudicated against independently"
                    " published seat reservations."
                ),
                "district_code_raw": (
                    "SEC source code with leading zeroes retained; not asserted to be"
                    " an LGD code."
                ),
                "row_structure_usable": (
                    "Parser structural checks only, not independent transcription"
                    " validation."
                ),
                "assignment_usable": (
                    "False for every observation pending decoding, source review,"
                    " historical identity and reservation adjudication."
                ),
                "coordinates": (
                    "PDF points, top-left origin, per-page source coordinates."
                ),
            },
        )
        receipt.update(
            finished_utc=now(),
            status=(
                "parsed_with_page_holds"
                if any(p["page_flags"] for p in page_reports)
                else "parsed"
            ),
            pages=len(pages),
            parsed_pages=sum(not p["page_flags"] for p in page_reports),
            observations=len(rows),
            office_counts=dict(
                collections.Counter(r["office_normalized"] for r in rows)
            ),
            observed_district_codes=len({r["district_code_raw"] for r in rows}),
            row_structure_usable=sum(r["row_structure_usable"] for r in rows),
            structural_flag_counts=dict(
                collections.Counter(
                    flag for row in rows for flag in row["structural_flags"]
                )
            ),
            unassigned_body_words=sum(p["unassigned_body_words"] for p in page_reports),
            source_words=len(all_words),
            unresolved_categories=dict(
                collections.Counter(
                    r["category_encoded_raw"] or "<blank>"
                    for r in rows
                    if r["reported_category_caste"] is None
                )
            ),
            unresolved_examples=[
                {
                    key: row[key]
                    for key in (
                        "source_page",
                        "source_row_on_page",
                        "district_code_raw",
                        "ward_number_raw",
                        "category_encoded_raw",
                        "structural_flags",
                    )
                }
                for row in rows
                if row["structural_flags"]
            ][:20],
            artifacts={
                name: sha256((output / name).read_bytes())
                for name in (
                    "source_words.parquet",
                    "member_observations.parquet",
                    "page_coverage.json",
                    "dictionary.json",
                )
                if (output / name).exists()
            },
        )
        write_json(output / "parse_receipt.json", receipt)
        print(json.dumps(receipt, ensure_ascii=True), flush=True)
    except Exception as error:
        receipt.update(finished_utc=now(), status="failed", error=str(error))
        write_json(output / "parse_receipt.json", receipt)
        raise


if __name__ == "__main__":
    main()
