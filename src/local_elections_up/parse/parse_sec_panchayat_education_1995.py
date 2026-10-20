# /// script
# requires-python = ">=3.11"
# dependencies = ["pyarrow>=14"]
# ///
"""Preserve the 1995 Panchayat education matrices without shifting blank cells."""

import argparse
import collections
import gzip
import hashlib
import itertools
import json
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

SPECS = {
    "elec95_cp_edu.pdf": {
        "sha": "cac313d8e4bdd872031240e375f45b4bcdfcce8ad7e65b3fbb681fcc1232aed3",
        "title": (
            "Percentage of Elected Chairpersons according to their Education Level in"
            " Panchayat General Election - 1995"
        ),
        "categories": [
            "Scheduled Tribes",
            "Scheduled Castes",
            "Backward Class",
            "General",
            "Total",
        ],
        "posts": [
            ("I. Pradhan", "gp_head"),
            ("II. Pramukh", "block_head"),
            ("III. Adhyaksha", "zp_head"),
        ],
    },
    "elec95_mem_edu.pdf": {
        "sha": "e146844f61087220eacb1c893b49b41bae9a8d775aaf67c982248441bd4d15aa",
        "title": (
            "Level of education of elected person of panchayat (General Election -"
            " 1995)"
        ),
        "categories": [
            "Scheduled Tribe",
            "Scheduled Caste",
            "Backward Class",
            "General",
            "Total",
        ],
        "posts": [
            ("I. Gram Panchayat", "gp_ward"),
            ("II. Kshetra Panchayat", "block_member"),
            ("III. Zila Panchayat", "zp_member"),
        ],
    },
}
SEX = ["MALE", "FEMALE", "TOTAL"]
EDUCATION = ["Upto Basic", "Upto Secondary", "Above Secondary", "Uneducated"]
NUMBER = re.compile(r"\d{1,3}(?:\.\d{1,2})?")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def parse_xml(xml, report, spec):
    categories = spec["categories"]
    columns = len(SEX) * len(EDUCATION)
    document = ET.fromstring(xml)
    pages = [e for e in document.iter() if e.tag.rsplit("}", 1)[-1] == "page"]
    if len(pages) != 1:
        raise ValueError("Expected one source page")
    words = []
    for element in pages[0].iter():
        if element.tag.rsplit("}", 1)[-1] == "word":
            box = [float(element.attrib[k]) for k in ("xMin", "yMin", "xMax", "yMax")]
            words.append(
                {
                    "text": element.text or "",
                    "box": box,
                    "x": (box[0] + box[2]) / 2,
                    "y": (box[1] + box[3]) / 2,
                }
            )
    lines = []
    for word in sorted(words, key=lambda w: (w["y"], w["box"][0])):
        if not lines or abs(word["y"] - lines[-1][0]["y"]) > 2:
            lines.append([])
        lines[-1].append(word)
    for line in lines:
        line.sort(key=lambda w: w["box"][0])
    joined = " ".join(w["text"] for line in lines for w in line)
    if spec["title"] not in joined:
        raise ValueError("Report title/year differs from reviewed source")
    headers = sorted((w for w in words if w["text"] in SEX), key=lambda w: w["x"])
    if [w["text"] for w in headers] != SEX:
        raise ValueError("Sex-column headings missing or reordered")
    anchors = [
        line
        for line in lines
        if " ".join(w["text"] for w in line).startswith(categories[0] + " ")
        and sum(bool(NUMBER.fullmatch(w["text"])) for w in line) == columns
    ]
    if not anchors:
        raise ValueError("No complete anchor row for twelve numeric columns")
    anchor = [w for w in anchors[0] if NUMBER.fullmatch(w["text"])]
    centers = [w["x"] for w in anchor]
    gap = min(b - a for a, b in itertools.pairwise(centers))
    if gap <= 15:
        raise ValueError("Numeric columns are not distinctly separated")
    left_boundary = anchor[0]["box"][0] - 10
    post_lookup = {name: (i, tier) for i, (name, tier) in enumerate(spec["posts"])}
    active = None
    table_rows = []
    for line in lines:
        label = " ".join(w["text"] for w in line if w["box"][0] < left_boundary)
        if label in post_lookup:
            active = (label, *post_lookup[label])
            continue
        numeric = [w for w in line if NUMBER.fullmatch(w["text"])]
        if label not in categories:
            if active is not None and numeric:
                raise ValueError("Unparsed numeric row inside the table")
            continue
        if active is None:
            raise ValueError("Category row without a post")
        post, post_index, tier = active
        ordinal = len(table_rows)
        if (
            ordinal >= 15
            or post_index != ordinal // 5
            or label != categories[ordinal % 5]
        ):
            raise ValueError("Missing, duplicated or reordered post/category row")
        unexpected = [
            w
            for w in line
            if w["box"][0] >= left_boundary and not NUMBER.fullmatch(w["text"])
        ]
        if unexpected:
            raise ValueError("Non-numeric content in percentage columns")
        cells = [None] * columns
        for word in numeric:
            column = min(range(columns), key=lambda i: abs(word["x"] - centers[i]))
            if abs(word["x"] - centers[column]) >= gap / 4 or cells[column] is not None:
                raise ValueError("Ambiguous percentage-column placement")
            if not Decimal(0) <= Decimal(word["text"]) <= Decimal(100):
                raise ValueError("Percentage outside 0..100")
            cells[column] = word
        row_box = [
            min(w["box"][0] for w in line),
            min(w["box"][1] for w in line),
            max(w["box"][2] for w in line),
            max(w["box"][3] for w in line),
        ]
        table_rows.append((post, tier, label, cells, row_box))
    if len(table_rows) != 15:
        raise ValueError("Expected all fifteen category rows")
    records = []
    for row_number, (post, tier, category, cells, row_box) in enumerate(table_rows, 1):
        for column, word in enumerate(cells):
            raw = word["text"] if word is not None else None
            coordinate = f"{report['source_sha256']}:1:{row_number}:{column + 2}"
            records.append(
                {
                    "observation_id": digest(coordinate.encode()),
                    "election_year": 1995,
                    "state": "Uttar Pradesh",
                    "tier": tier,
                    "post_raw": post,
                    "category_raw": category,
                    "sex_label_raw": SEX[column // len(EDUCATION)],
                    "education_level_order": column % len(EDUCATION) + 1,
                    "education_level_raw": EDUCATION[column % len(EDUCATION)],
                    "percentage_raw": raw,
                    "percentage": Decimal(raw) if raw is not None else None,
                    "measure": (
                        "reported_education_distribution_of_elected_officeholders"
                    ),
                    "source_url": report["url"],
                    "source_sha256": report["source_sha256"],
                    "source_response_path": report["source_response_path"],
                    "source_index_url": report["source_index_url"],
                    "source_index_sha256": report["source_index_sha256"],
                    "source_page": 1,
                    "source_table_row": row_number,
                    "source_column": column + 2,
                    "source_row_bbox": row_box,
                    "source_value_bbox": word["box"] if word is not None else None,
                    "quality_flags": (
                        "aggregate_not_seat_assignment;independent_review_pending"
                        + (";source_cell_blank" if word is None else "")
                    ),
                    "assignment_usable": False,
                }
            )
    return records, centers


def arithmetic(records):
    grouped = collections.defaultdict(list)
    for row in records:
        grouped[row["tier"], row["category_raw"], row["sex_label_raw"]].append(row)
    checks = []
    for (tier, category, sex), rows in grouped.items():
        complete = all(r["percentage"] is not None for r in rows)
        difference = (
            sum((r["percentage"] for r in rows), Decimal(0)) - 100 if complete else None
        )
        status = "incomplete_source_cells"
        if complete:
            status = (
                "agrees"
                if difference == 0
                else (
                    "small_reported_difference"
                    if abs(difference) <= Decimal("0.02")
                    else "source_arithmetic_discrepancy"
                )
            )
        if complete and difference != 0:
            for row in rows:
                row["quality_flags"] += ";" + status
        checks.append(
            {
                "tier": tier,
                "category_raw": category,
                "sex_label_raw": sex,
                "check": "four_reported_education_percentages_sum_to_100",
                "status": status,
                "difference_percentage_points": (
                    str(difference) if difference is not None else None
                ),
                "related_observation_ids": [r["observation_id"] for r in rows],
            }
        )
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.source_root.resolve()
    acquisition_bytes = (root / "acquisition_receipt.json").read_bytes()
    acquisition = json.loads(acquisition_bytes)
    records, inputs = [], []
    for filename, spec in SPECS.items():
        url = "https://sec.up.nic.in/site/fonts/" + filename
        matches = [r for r in acquisition["reports"] if r["url"] == url]
        if len(matches) != 1 or matches[0]["election_year"] != 1995:
            raise ValueError("Missing or ambiguous acquired 1995 report")
        report = matches[0]
        path = (root / report["source_response_path"]).resolve()
        if not path.is_relative_to(root):
            raise ValueError("Source path escapes acquisition root")
        data = gzip.decompress(path.read_bytes())
        if digest(data) != report["source_sha256"] or digest(data) != spec["sha"]:
            raise ValueError("PDF differs from the visually reviewed source version")
        with tempfile.TemporaryDirectory(prefix="up-education1995-") as temporary:
            pdf = Path(temporary) / "source.pdf"
            pdf.write_bytes(data)
            xml = subprocess.run(
                ["pdftotext", "-bbox", str(pdf), "-"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
        parsed, centers = parse_xml(xml, report, spec)
        records.extend(parsed)
        inputs.append(
            {
                "source_url": url,
                "source_sha256": report["source_sha256"],
                "numeric_column_centers": centers,
            }
        )
    checks = arithmetic(records)
    table = pa.Table.from_pylist(records)
    position = table.schema.get_field_index("percentage")
    table = table.set_column(
        position, "percentage", table["percentage"].cast(pa.decimal128(5, 2))
    )
    args.output.mkdir(parents=True, exist_ok=False)
    artifact = args.output / "reported_education_percentages.parquet"
    pq.write_table(table, artifact, compression="zstd")
    receipt = {
        "parsed_utc": datetime.now(UTC).isoformat(),
        "records": len(records),
        "source_reports": len(inputs),
        "blank_source_cells": sum(r["percentage"] is None for r in records),
        "acquisition_root": str(args.source_root),
        "acquisition_receipt_sha256": digest(acquisition_bytes),
        "inputs": inputs,
        "script_sha256": digest(Path(__file__).read_bytes()),
        "artifact_sha256": digest(artifact.read_bytes()),
        "arithmetic_status_counts": dict(
            collections.Counter(c["status"] for c in checks)
        ),
        "scope": (
            "Historical aggregate education percentages, not identified seat or"
            " candidate records."
        ),
        "blank_policy": (
            "Interior and entire-row blanks remain null, never shifted or filled with"
            " zero."
        ),
        "correction_policy": (
            "Printed discrepancies are retained; no inferred replacement values."
        ),
        "assignment_usable": False,
        "paid_api_cost_added_usd": 0,
    }
    dictionary = {
        "unit": (
            "One reported education-percentage cell or blank for a post/category/sex"
            " group."
        ),
        "percentage": "Decimal 0..100 percentage; null denotes a blank source cell.",
        "education_level_raw": (
            "Printed headings preserved; Upto Basic and Upto Secondary are not recoded"
            " as modern qualifications."
        ),
        "education_level_order": (
            "Left-to-right education-column ordinal within the printed sex group."
        ),
        "sex_label_raw": (
            "MALE, FEMALE or TOTAL as printed. TOTAL is not the sum of male/female"
            " percentages."
        ),
        "category_raw": (
            "Printed grouping of elected officeholders, not a seat reservation"
            " assignment."
        ),
        "source_coordinates": (
            "One-based PDF page, data-table row and column; bbox arrays are Poppler"
            " -bbox word coordinates."
        ),
        "source_value_bbox": (
            "Exact numeric word box, or null when the source cell is blank."
        ),
        "coordinate_caution": (
            "Poppler word coordinates may reflect page rotation differently from PDF"
            " page dimensions."
        ),
        "source_response_path": (
            "Compressed original PDF relative to acquisition_root in"
            " parse_receipt.json."
        ),
        "arithmetic": (
            "Four education-column sum checks within each sex/category only. Missing"
            " cells prevent comparison; differences never trigger corrections."
        ),
        "geography": (
            "Historical source scope; no equivalence to current Uttar Pradesh"
            " boundaries is asserted."
        ),
        "assignment_usable": (
            "Always false; do not convert aggregate percentages into identified seat"
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
