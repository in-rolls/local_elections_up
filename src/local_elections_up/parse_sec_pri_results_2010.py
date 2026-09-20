# /// script
# requires-python = ">=3.11"
# dependencies = ["pyarrow"]
# ///
"""Extract source-linked 2010 PRI result cells without guessing legacy fonts."""

from __future__ import annotations

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
NS = {"x": "http://www.w3.org/1999/xhtml"}
SOURCES = {
    "KPP_result_2010.pdf": {
        "sha256": "b5a0b80963bade7becc1c6d5e5a35b9e6927f038c950e58d67453d470704d8f2",
        "office": "panchayat_samiti_head",
        "pages": 36,
        "bounds": [35, 66, 104, 187, 282, 370, 450, 552, 572, 595, 663, 842],
        "fields": [
            "printed_serial_raw",
            "body_number_raw",
            "body_name_encoded_raw",
            "seat_reservation_encoded_raw",
            "candidate_name_encoded_raw",
            "related_person_encoded_raw",
            "candidate_category_encoded_raw",
            "age_raw",
            "sex_encoded_raw",
            "education_encoded_raw",
            "address_encoded_raw",
        ],
        "bottom": 555,
    },
    "ZPA_FINALLIST_NEW.pdf": {
        "sha256": "3db351f3898464dd495221ae9a4698d2cf8a95e84582ba4663f3928a18a9d666",
        "office": "zilla_parishad_head",
        "pages": 3,
        "bounds": [54, 74, 107, 209, 322, 429, 510, 558],
        "fields": [
            "printed_serial_raw",
            "district_code_raw",
            "district_name_encoded_raw",
            "candidate_name_encoded_raw",
            "related_person_encoded_raw",
            "reported_category_encoded_raw",
            "remarks_encoded_raw",
        ],
        "bottom": 805,
    },
    "zpm_result_2010.pdf": {
        "sha256": "775fca2b859b843926ef7f07194c252699f0d2cbf19a60924e6c813a9235765f",
        "office": "zilla_parishad_member",
        "pages": 150,
        "bounds": [35, 66, 124, 236, 340, 426, 535, 558, 593, 663, 842],
        "fields": [
            "printed_serial_raw",
            "ward_number_raw",
            "seat_reservation_encoded_raw",
            "candidate_name_encoded_raw",
            "related_person_encoded_raw",
            "candidate_category_encoded_raw",
            "age_raw",
            "sex_encoded_raw",
            "education_encoded_raw",
            "address_encoded_raw",
        ],
        "bottom": 555,
    },
}
TEXT_FIELDS = sorted({field for spec in SOURCES.values() for field in spec["fields"]})
SCHEMA = pa.schema(
    [(field, pa.string()) for field in TEXT_FIELDS]
    + [
        (field, pa.string())
        for field in (
            "observation_id",
            "office",
            "source_path",
            "source_sha256",
            "source_url",
            "text_encoding",
            "district_context_name_encoded_raw",
            "district_context_code_raw",
            "cell_geometry_json",
            "record_kind",
        )
    ]
    + [
        (field, pa.int64())
        for field in (
            "election_year",
            "source_page",
            "source_row_number",
            "printed_serial",
            "district_context_page",
            "ward_number",
            "body_number",
        )
    ]
    + [
        ("assignment_usable", pa.bool_()),
        ("is_winner", pa.bool_()),
        ("quality_flags", pa.list_(pa.string())),
    ]
)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2) + "\n")


def words_on_page(page):
    return [
        {
            "text": word.text or "",
            **{
                axis: float(word.attrib[axis])
                for axis in ("xMin", "yMin", "xMax", "yMax")
            },
        }
        for word in page.findall(".//x:word", NS)
    ]


def cell_text(words):
    lines = []
    for word in sorted(words, key=lambda item: (item["yMin"], item["xMin"])):
        if not lines or word["yMin"] - lines[-1][0] > 3:
            lines.append((word["yMin"], []))
        lines[-1][1].append(word)
    return (
        "\n".join(
            " ".join(
                word["text"] for word in sorted(line, key=lambda item: item["xMin"])
            )
            for _, line in lines
        )
        or None
    )


def positive_integer(raw):
    return int(raw) if raw and re.fullmatch(r"[1-9][0-9]*", raw) else None


def extract_pages(xml, spec, source_path):
    pages = ET.fromstring(xml).findall(".//x:page", NS)
    if len(pages) != spec["pages"]:
        raise ValueError("Pinned source page count changed")
    records, page_receipts = [], []
    context = None
    bounds, fields = spec["bounds"], spec["fields"]
    for page_number, page in enumerate(pages, 1):
        words = words_on_page(page)
        if spec["office"] == "zilla_parishad_member":
            context = None
        anchors = sorted(
            [
                word
                for word in words
                if bounds[0] <= word["xMin"] < bounds[1]
                and 100 < word["yMin"] < spec["bottom"]
                and positive_integer(word["text"]) is not None
            ],
            key=lambda item: item["yMin"],
        )
        body_bottom = spec["bottom"]
        footnote_words = []
        if spec["office"] == "zilla_parishad_head" and page_number == 3:
            starts = [
                word
                for word in words
                if word["text"].startswith("*tuin")
                and bounds[0] <= word["xMin"] < bounds[1]
                and anchors
                and word["yMin"] > anchors[-1]["yMax"]
            ]
            if len(starts) != 1:
                raise ValueError("Pinned ZP-chair footnote boundary is not unique")
            body_bottom = starts[0]["yMin"] - 3
            footnote_words = [
                word for word in words if body_bottom <= word["yMin"] < spec["bottom"]
            ]
        headers = []
        for word in words:
            if word["text"] != "ftys" or word["xMin"] >= 50:
                continue
            line = [item for item in words if abs(item["yMin"] - word["yMin"]) < 4]
            codes = [
                item["text"]
                for item in line
                if 100 <= item["xMin"] < 145 and re.fullmatch(r"[0-9]{4}", item["text"])
            ]
            headers.append(
                {
                    "y": word["yMin"],
                    "page": page_number,
                    "code": codes[0] if len(codes) == 1 else None,
                    "name": cell_text([item for item in line if item["xMin"] >= 205]),
                }
            )
        headers.sort(key=lambda item: item["y"])
        page_receipts.append(
            {
                "source_page": page_number,
                "anchors": len(anchors),
                "district_headers": headers,
                "page_text_encoded_raw": cell_text(words),
                "footnote_text_encoded_raw": cell_text(footnote_words),
                "footnote_word_geometry": footnote_words,
            }
        )
        for index, anchor in enumerate(anchors):
            preceding = [header for header in headers if header["y"] < anchor["yMin"]]
            if preceding:
                context = preceding[-1]
            top = anchor["yMin"] - 6
            bottom = (
                anchors[index + 1]["yMin"] - 6
                if index + 1 < len(anchors)
                else body_bottom
            )
            following = [
                header["y"] - 3 for header in headers if header["y"] > anchor["yMin"]
            ]
            if following:
                bottom = min(bottom, min(following))
            cells = {}
            quality = ["legacy_font_decoding_pending", "independent_row_review_pending"]
            record = {field.name: None for field in SCHEMA}
            for column, field in enumerate(fields):
                selected = [
                    word
                    for word in words
                    if top <= word["yMin"] < bottom
                    and bounds[column] <= word["xMin"] < bounds[column + 1]
                ]
                record[field] = cell_text(selected)
                cells[field] = selected
                if any(word["xMax"] > bounds[column + 1] + 2 for word in selected):
                    quality.append("cell_text_crosses_column_boundary")
            record.update(
                observation_id=digest(
                    f"{spec['sha256']}:{page_number}:{index + 1}".encode()
                ),
                office=spec["office"],
                election_year=2010,
                source_path=source_path,
                source_sha256=spec["sha256"],
                source_page=page_number,
                source_row_number=index + 1,
                printed_serial=positive_integer(record["printed_serial_raw"]),
                text_encoding="embedded_legacy_font_unresolved",
                record_kind="reported_official",
                assignment_usable=False,
                cell_geometry_json=json.dumps(
                    cells, ensure_ascii=True, separators=(",", ":")
                ),
            )
            if spec["office"] == "zilla_parishad_head":
                quality.append("reported_category_axis_unresolved")
                if "*" in (record["district_name_encoded_raw"] or ""):
                    quality.append("district_election_abeyance_footnote")
            elif context:
                record.update(
                    district_context_code_raw=context["code"],
                    district_context_name_encoded_raw=context["name"],
                    district_context_page=context["page"],
                )
            else:
                quality.append("district_context_unresolved")
            for target in ("ward_number", "body_number"):
                record[target] = positive_integer(record[target + "_raw"])
                if record[target + "_raw"] and record[target] is None:
                    quality.append(target + "_unparsed")
            if record["printed_serial"] is None:
                quality.append("printed_serial_unparsed")
            record["quality_flags"] = sorted(set(quality))
            records.append(record)
    return records, page_receipts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-root", type=Path, default=ROOT / "data/interim/sec_pri_results_2010"
    )
    args = parser.parse_args()
    output = args.output_root / datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    output.mkdir(parents=True, exist_ok=False)
    receipt = {
        "status": "incomplete",
        "parser_sha256": digest(Path(__file__).read_bytes()),
        "sources": [],
        "assignment_usable": False,
        "new_paid_api_cost_usd": 0,
        "source_url_policy": (
            "Unknown original HTTP URLs remain null; local PDF hashes are retained."
        ),
        "geometry_policy": (
            "Poppler word coordinates, including rotated-page coordinates, "
            "are preserved without scaling."
        ),
        "zpa_qualification": (
            "Printed starred districts Etah and Kanshiram Nagar have an "
            "election-abeyance footnote on page 3; listed officials are not "
            "certified winners."
        ),
    }
    write_json(output / "INCOMPLETE.json", receipt)
    for filename, spec in SOURCES.items():
        relative = "data/2010/" + filename
        path = ROOT / relative
        if digest(path.read_bytes()) != spec["sha256"]:
            raise ValueError(f"Source hash changed: {relative}")
        xml = subprocess.run(
            ["pdftotext", "-bbox-layout", str(path), "-"],
            check=True,
            capture_output=True,
        ).stdout
        fonts = subprocess.run(
            ["pdffonts", str(path)],
            check=True,
            capture_output=True,
        ).stdout
        prefix = spec["office"]
        (output / (prefix + ".xhtml.gz")).write_bytes(gzip.compress(xml, mtime=0))
        (output / (prefix + ".fonts.txt")).write_bytes(fonts)
        records, pages = extract_pages(xml, spec, relative)
        artifact = output / (prefix + ".parquet")
        pq.write_table(
            pa.Table.from_pylist(records, schema=SCHEMA), artifact, compression="zstd"
        )
        page_bytes = "".join(
            json.dumps(page, ensure_ascii=True) + "\n" for page in pages
        ).encode()
        (output / (prefix + ".pages.jsonl.gz")).write_bytes(
            gzip.compress(page_bytes, mtime=0)
        )
        receipt["sources"].append(
            {
                "path": relative,
                **spec,
                "rows": len(records),
                "artifact": artifact.name,
                "artifact_sha256": digest(artifact.read_bytes()),
                "extracted_xml_sha256": digest(xml),
                "flags": dict(
                    Counter(flag for row in records for flag in row["quality_flags"])
                ),
                "pages_without_row_anchors": [
                    page["source_page"] for page in pages if not page["anchors"]
                ],
            }
        )
    receipt["status"] = "parsed_pending_review"
    write_json(output / "receipt.json", receipt)
    (output / "INCOMPLETE.json").unlink()
    print(
        json.dumps({"output": str(output), "sources": receipt["sources"]}), flush=True
    )


if __name__ == "__main__":
    main()
