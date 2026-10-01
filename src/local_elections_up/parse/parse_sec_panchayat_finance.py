# /// script
# requires-python = ">=3.11"
# dependencies = ["pyarrow>=14"]
# ///
"""Parse the acquired 1995/2000 SEC Panchayat financial tables without OCR."""

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
    "elec00_receipts.pdf": {
        "sha": "017a8dd041281517f642dab2851e2ab4fdb7ba8ac8da3f81850a050532cda908",
        "year": 2000,
        "kind": "receipts",
        "title": (
            "Districtwise amount received by Nomination/Security Deposit/Sale of"
            " Electoral Roll/ Addition/Deletion in Electoral Roll in Panchayat Election"
            " - 2000"
        ),
        "unit_raw": "(Rs.)",
        "unit": "INR",
        "multiplier": 1,
    },
    "elec00_exp_pan.pdf": {
        "sha": "c61fbb628e3d733faa4dc20526c0e5778872649b6d625a22889265d3547df99d",
        "year": 2000,
        "kind": "expenses",
        "title": "Districtwise Expenses in Panchayat Election-2000",
        "unit_raw": "Rs. In Lacks",
        "unit": "INR_lakh",
        "multiplier": 100000,
    },
    "elec95_per_voter_exp.pdf": {
        "sha": "56f917ad29728636aa701813d6b81cd53cca9145a053c94e9600792d99af4f62",
        "year": 1995,
        "kind": "per_voter",
        "title": "Details of Per Voter Expenses in Panchayat Election-1995",
        "unit_raw": None,
        "unit": None,
        "multiplier": None,
    },
}
RECEIPT_MEASURES = [
    ("nomination_receipts", "Amount Recd by Nomination"),
    ("security_deposit_receipts", "Amount Recd by Security Deposit"),
    ("electoral_roll_sale_receipts", "Amount Recd by Sale of Electoral Roll"),
    (
        "electoral_roll_change_receipts",
        "Amount Recd by Addition/Deletion in Electoral Roll",
    ),
    ("total_receipts", "Total"),
]
INTEGER = re.compile(r"\d+")
DECIMAL = re.compile(r"\d+\.\d{2}")
COMMISSION_LABEL = (
    "Expenses incurred for purchases of ballot paper & printing of ballot paper "
    "etc. by commission"
)
NA_NOTE = "NA = District created after 1995"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def text(words):
    return " ".join(w["text"] for w in words)


def bbox(words):
    return [
        min(w["box"][0] for w in words),
        min(w["box"][1] for w in words),
        max(w["box"][2] for w in words),
        max(w["box"][3] for w in words),
    ]


def page_lines(xml):
    document = ET.fromstring(xml)
    pages = [e for e in document.iter() if e.tag.rsplit("}", 1)[-1] == "page"]
    if len(pages) != 2:
        raise ValueError("Expected the two reviewed source pages")
    result = []
    for page in pages:
        words = []
        for e in page.iter():
            if e.tag.rsplit("}", 1)[-1] == "word":
                box = [float(e.attrib[k]) for k in ("xMin", "yMin", "xMax", "yMax")]
                words.append({"text": e.text or "", "box": box})
        lines = []
        for word in sorted(
            words, key=lambda w: ((w["box"][1] + w["box"][3]) / 2, w["box"][0])
        ):
            middle = (word["box"][1] + word["box"][3]) / 2
            if not lines or abs(middle - lines[-1][0]) > 2:
                lines.append((middle, []))
            lines[-1][1].append(word)
        result.append([sorted(line, key=lambda w: w["box"][0]) for _, line in lines])
    return result


def receipt_rows(pages):
    rows = []
    for page_number, lines in enumerate(pages, 1):
        selected = [
            line
            for line in lines
            if re.fullmatch(r"\d{4}", line[0]["text"])
            or (
                line[0]["text"] == "Total"
                and any(INTEGER.fullmatch(w["text"]) for w in line[1:])
            )
        ]
        anchors = [
            [w for w in line[1:] if INTEGER.fullmatch(w["text"])]
            for line in selected
            if re.fullmatch(r"\d{4}", line[0]["text"])
        ]
        anchor = next((values for values in anchors if len(values) == 5), None)
        if anchor is None:
            raise ValueError("No complete five-column receipt anchor")
        right_edges = [w["box"][2] for w in anchor]
        gap = min(b - a for a, b in itertools.pairwise(right_edges))
        if gap <= 20:
            raise ValueError("Receipt columns overlap")
        for row_number, line in enumerate(selected, 1):
            total = line[0]["text"] == "Total"
            code = None if total else line[0]["text"]
            remainder = line if total else line[1:]
            label_words = [w for w in remainder if not INTEGER.fullmatch(w["text"])]
            cells = [None] * 5
            for word in remainder:
                if not INTEGER.fullmatch(word["text"]):
                    continue
                column = min(
                    range(5), key=lambda i: abs(word["box"][2] - right_edges[i])
                )
                if (
                    abs(word["box"][2] - right_edges[column]) >= gap / 4
                    or cells[column] is not None
                ):
                    raise ValueError("Ambiguous receipt cell placement")
                cells[column] = word
            if (
                not label_words
                or cells[0] is None
                or cells[1] is None
                or cells[4] is None
            ):
                raise ValueError("Receipt district, mandatory amounts or total missing")
            rows.append(
                {
                    "page": page_number,
                    "row": row_number,
                    "code": code,
                    "serial": None,
                    "label": text(label_words),
                    "scope": "source_total" if total else "district",
                    "cells": cells,
                    "words": line,
                }
            )
    districts = [r for r in rows if r["scope"] == "district"]
    if (
        len(districts) != 71
        or len({r["code"] for r in districts}) != 71
        or len(rows) != 72
    ):
        raise ValueError("Expected 71 distinct source district codes and one total")
    if rows[-1]["scope"] != "source_total":
        raise ValueError("Source total is not the final receipt row")
    return rows


def single_value_rows(pages, kind):
    rows = []
    for page_number, lines in enumerate(pages, 1):
        ordinal = 0
        for line in lines:
            first, joined = line[0]["text"], text(line)
            serial = int(first) if re.fullmatch(r"\d{1,2}", first) else None
            total = kind == "expenses" and joined.startswith("Total Expenses ")
            if serial is not None or total:
                word = line[-1]
                if not DECIMAL.fullmatch(word["text"]) and not (
                    kind == "per_voter" and word["text"] == "NA"
                ):
                    raise ValueError("Unexpected expense or per-voter value")
                label_words = line[:-1] if total else line[1:-1]
                if not label_words:
                    raise ValueError("Missing source row label")
                ordinal += 1
                scope = (
                    "source_total"
                    if total
                    else (
                        "commission"
                        if kind == "expenses" and serial == 72
                        else "district"
                    )
                )
                rows.append(
                    {
                        "page": page_number,
                        "row": ordinal,
                        "code": None,
                        "serial": serial,
                        "label": text(label_words),
                        "scope": scope,
                        "cells": [word],
                        "words": list(line),
                    }
                )
            elif kind == "expenses" and rows and rows[-1]["scope"] == "commission":
                if joined in (
                    "ballot paper & printing of ballot paper",
                    "etc. by commission",
                ):
                    rows[-1]["label"] += " " + joined
                    rows[-1]["words"].extend(line)
    expected = 72 if kind == "expenses" else 71
    if [r["serial"] for r in rows if r["serial"] is not None] != list(
        range(1, expected + 1)
    ):
        raise ValueError("Missing, duplicated or reordered district/commission serial")
    if kind == "expenses":
        if (
            len(rows) != 73
            or rows[-1]["scope"] != "source_total"
            or rows[-2]["label"] != COMMISSION_LABEL
        ):
            raise ValueError("Commission continuation or final expense total missing")
    elif len(rows) != 71:
        raise ValueError("Expected 71 per-voter source rows")
    return rows


def observations(rows, report, spec):
    records = []
    for row in rows:
        for column, word in enumerate(row["cells"]):
            raw = word["text"] if word is not None else None
            value = Decimal(raw) if raw is not None and raw != "NA" else None
            if value is not None and value < 0:
                raise ValueError("Negative reported financial amount")
            if spec["kind"] == "receipts":
                measure, measure_raw = RECEIPT_MEASURES[column]
            else:
                measure, measure_raw = (
                    ("election_expenses", "Amount (Rs.)")
                    if spec["kind"] == "expenses"
                    else ("per_voter_expenses", "Per Voter Expenses")
                )
            flags = [
                "aggregate_not_seat_assignment",
                "independent_review_pending",
                "historical_geography_unvalidated",
            ]
            if raw is None:
                flags.append("source_cell_blank")
            if raw == "NA":
                flags.append("source_reported_na")
            if spec["unit"] is None:
                flags.append("currency_unit_not_stated")
            source_column = column + 3
            coordinate = (
                f"{report['source_sha256']}:{row['page']}:{row['row']}:{source_column}"
            )
            records.append(
                {
                    "observation_id": digest(coordinate.encode()),
                    "election_year": spec["year"],
                    "state": "Uttar Pradesh",
                    "report_kind": spec["kind"],
                    "row_scope": row["scope"],
                    "district_code_raw": row["code"],
                    "source_serial_raw": (
                        str(row["serial"]) if row["serial"] is not None else None
                    ),
                    "district_name_raw": (
                        row["label"] if row["scope"] == "district" else None
                    ),
                    "row_label_raw": row["label"],
                    "measure": measure,
                    "measure_label_raw": measure_raw,
                    "value_raw": raw,
                    "value": value,
                    "unit_source_raw": spec["unit_raw"],
                    "unit": spec["unit"],
                    "unit_source_page": 1 if spec["unit_raw"] else None,
                    "unit_multiplier_to_inr": spec["multiplier"],
                    "amount_inr": (
                        value * spec["multiplier"]
                        if value is not None and spec["multiplier"] is not None
                        else None
                    ),
                    "missing_reason": (
                        "source_cell_blank"
                        if raw is None
                        else ("source_reported_na" if raw == "NA" else None)
                    ),
                    "source_na_note_raw": (
                        NA_NOTE if spec["kind"] == "per_voter" else None
                    ),
                    "source_na_note_page": 2 if spec["kind"] == "per_voter" else None,
                    "source_url": report["url"],
                    "source_sha256": report["source_sha256"],
                    "source_response_path": report["source_response_path"],
                    "source_index_url": report["source_index_url"],
                    "source_index_sha256": report["source_index_sha256"],
                    "source_page": row["page"],
                    "source_table_row": row["row"],
                    "source_column": source_column,
                    "source_row_bbox": bbox(row["words"]),
                    "source_value_bbox": word["box"] if word is not None else None,
                    "source_row_words_json": json.dumps(
                        row["words"], ensure_ascii=True, separators=(",", ":")
                    ),
                    "quality_flags": ";".join(flags),
                    "assignment_usable": False,
                }
            )
    return records


def arithmetic(records):
    checks = []

    def compare(name, parts, total):
        complete = all(r["value"] is not None for r in [*parts, total])
        difference = (
            sum((r["value"] for r in parts), Decimal(0)) - total["value"]
            if complete
            else None
        )
        status = (
            "incomplete_source_cells"
            if not complete
            else ("agrees" if difference == 0 else "source_arithmetic_discrepancy")
        )
        related = [*parts, total]
        if status == "source_arithmetic_discrepancy":
            for row in related:
                if status not in row["quality_flags"].split(";"):
                    row["quality_flags"] += ";" + status
        checks.append(
            {
                "check": name,
                "status": status,
                "unit": total["unit"],
                "difference_in_source_unit": (
                    str(difference) if difference is not None else None
                ),
                "source_sha256": total["source_sha256"],
                "related_observation_ids": [r["observation_id"] for r in related],
            }
        )

    receipts = [r for r in records if r["report_kind"] == "receipts"]
    grouped = collections.defaultdict(list)
    for row in receipts:
        grouped[row["source_page"], row["source_table_row"]].append(row)
    for values in grouped.values():
        compare("four_receipt_components_equal_reported_total", values[:4], values[4])
    for measure, _ in RECEIPT_MEASURES:
        parts = [
            r
            for r in receipts
            if r["measure"] == measure and r["row_scope"] == "district"
        ]
        totals = [
            r
            for r in receipts
            if r["measure"] == measure and r["row_scope"] == "source_total"
        ]
        if len(totals) != 1:
            raise ValueError("Missing or ambiguous receipt grand total")
        compare(
            "district_receipts_equal_reported_grand_total:" + measure, parts, totals[0]
        )
    expenses = [r for r in records if r["report_kind"] == "expenses"]
    compare(
        "district_and_commission_expenses_equal_reported_total",
        [r for r in expenses if r["row_scope"] != "source_total"],
        next(r for r in expenses if r["row_scope"] == "source_total"),
    )
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.source_root.resolve()
    acquisition_bytes = (root / "acquisition_receipt.json").read_bytes()
    acquisition = json.loads(acquisition_bytes)
    records, inputs = [], []
    for filename, spec in SPECS.items():
        url = "https://sec.up.nic.in/site/fonts/" + filename
        matches = [r for r in acquisition["reports"] if r["url"] == url]
        if len(matches) != 1 or matches[0]["election_year"] != spec["year"]:
            raise ValueError("Missing or ambiguous acquired financial report")
        report = matches[0]
        source = (root / report["source_response_path"]).resolve()
        if not source.is_relative_to(root):
            raise ValueError("Source path escapes acquisition root")
        pdf_bytes = gzip.decompress(source.read_bytes())
        if (
            digest(pdf_bytes) != spec["sha"]
            or digest(pdf_bytes) != report["source_sha256"]
        ):
            raise ValueError("PDF differs from the reviewed source")
        with tempfile.TemporaryDirectory(prefix="up-finance-") as temporary:
            pdf = Path(temporary) / "source.pdf"
            pdf.write_bytes(pdf_bytes)
            xml = subprocess.run(
                ["pdftotext", "-bbox", str(pdf), "-"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
        pages = page_lines(xml)
        joined = " ".join(text(line) for lines in pages for line in lines)
        if spec["title"] not in joined or (
            spec["unit_raw"] and spec["unit_raw"] not in joined
        ):
            raise ValueError("Financial source title or unit changed")
        if spec["kind"] == "per_voter" and NA_NOTE not in joined:
            raise ValueError("Source NA explanation missing")
        rows = (
            receipt_rows(pages)
            if spec["kind"] == "receipts"
            else single_value_rows(pages, spec["kind"])
        )
        parsed = observations(rows, report, spec)
        records.extend(parsed)
        inputs.append(
            {
                "source_url": url,
                "source_sha256": report["source_sha256"],
                "source_rows": len(rows),
                "observations": len(parsed),
                "report_kind": spec["kind"],
            }
        )
    checks = arithmetic(records)
    table = pa.Table.from_pylist(records)
    for name in ("value", "amount_inr"):
        position = table.schema.get_field_index(name)
        table = table.set_column(position, name, table[name].cast(pa.decimal128(18, 2)))
    args.output.mkdir(parents=True, exist_ok=False)
    artifact = args.output / "reported_election_finances.parquet"
    pq.write_table(table, artifact, compression="zstd")
    receipt = {
        "parsed_utc": datetime.now(UTC).isoformat(),
        "records": len(records),
        "source_reports": len(inputs),
        "inputs": inputs,
        "blank_source_cells": sum(r["value_raw"] is None for r in records),
        "source_reported_na_cells": sum(r["value_raw"] == "NA" for r in records),
        "acquisition_root": str(args.source_root),
        "acquisition_receipt_sha256": digest(acquisition_bytes),
        "script_sha256": digest(Path(__file__).read_bytes()),
        "artifact_sha256": digest(artifact.read_bytes()),
        "arithmetic_status_counts": dict(
            collections.Counter(c["status"] for c in checks)
        ),
        "scope": (
            "Historical financial aggregates, not identified seats or reservation"
            " assignments."
        ),
        "assignment_usable": False,
        "paid_api_cost_added_usd": 0,
    }
    dictionary = {
        "unit_of_observation": (
            "One printed amount cell, explicit NA, or blank; source totals remain"
            " separate."
        ),
        "value": (
            "Decimal in the printed source unit; blanks and explicit NA remain null,"
            " never zero."
        ),
        "amount_inr": (
            "Receipts unchanged; expenses multiplied by 100000 following Rs. In Lacks."
            " Per-voter currency is not stated and is not inferred."
        ),
        "row_scope": (
            "district, commission or source_total; commission spending is not a"
            " district."
        ),
        "district_code_raw": (
            "Only the 2000 receipt report supplies district codes. Preserve leading"
            " zeroes; not LGD."
        ),
        "source_serial_raw": "Printed row ordinal, not a district identifier.",
        "geography": (
            "Historical labels retained, including Haridwar. No conversion to current"
            " Uttar Pradesh boundaries or district creations."
        ),
        "source_na_note_raw": (
            "The report's explanation, not independently certified district history. Do"
            " not infer creation dates from NA."
        ),
        "source_column": (
            "One-based logical table column; row labels occupy column 2 and values"
            " begin at column 3."
        ),
        "source_coordinates": (
            "One-based PDF page and page-local data row; bbox arrays and word JSON use"
            " Poppler -bbox coordinates."
        ),
        "source_response_path": (
            "Gzipped exact source PDF relative to acquisition_root in"
            " parse_receipt.json."
        ),
        "arithmetic": (
            "Exact Decimal comparisons only when all needed cells are present. Printed"
            " discrepancies remain unchanged. Per-voter rates are not summed or"
            " averaged."
        ),
        "assignment_usable": (
            "Always false: no financial aggregate becomes a seat assignment."
        ),
        "schema": {field.name: str(field.type) for field in table.schema},
    }
    for name, value in (
        ("parse_receipt.json", receipt),
        ("arithmetic_checks.json", checks),
        ("dictionary.json", dictionary),
    ):
        (args.output / name).write_text(
            json.dumps(value, ensure_ascii=True, indent=2) + "\n"
        )
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
