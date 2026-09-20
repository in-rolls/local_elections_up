"""Extract source-linked raw rows from four SEC UP 2012 urban member lists."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

SOURCES = {
    "d1ed7797675ddab1ef522c813ece68e1024cbc911fedc83dba7fbb368cbf158c": (
        "kanpurnagar",
        "0805",
    ),
    "c2be0387f89ee98b993e2f5d2f41c73e32cf7d64c7d5df3fdd5c85006d850434": (
        "hamirpur",
        "1002",
    ),
    "1bf7488972f4a77000f5177e062072e67fc1bc507d8c2bcd15eb7a79e2c74281": (
        "kaushambi",
        "1102",
    ),
    "450560febfbc559af9cf4447f426c3ea11fd5505742108396ec72812bde7e908": (
        "deoria",
        "1604",
    ),
}
BANDS = {
    "body_type_encoded_raw": (38, 113),
    "body_name_encoded_raw": (113, 215),
    "ward_number_raw": (215, 259),
    "ward_name_encoded_raw": (259, 353),
    "person_and_relation_encoded_raw": (353, 490),
    "reported_sex_and_age_encoded_raw": (675, 704),
    "party_and_reservation_encoded_raw": (704, 832),
}


def sha256(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def inside(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"Source path escapes root: {relative}")
    return path


def packed(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def write_json(path, value):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=True, indent=2, sort_keys=True)
        handle.write("\n")


def select(words, left, right, top, bottom):
    return [
        word
        for word in words
        if left <= word["xMin"] < right and top <= word["yMin"] < bottom
    ]


def lines(words):
    grouped = []
    for word in sorted(words, key=lambda value: (value["yMin"], value["xMin"])):
        if not grouped or word["yMin"] - grouped[-1][0]["yMin"] > 3:
            grouped.append([])
        grouped[-1].append(word)
    return "\n".join(
        " ".join(word["text"] for word in sorted(line, key=lambda value: value["xMin"]))
        for line in grouped
    )


def pages(path):
    with gzip.open(path, "rb") as handle:
        number = 0
        for _, element in ET.iterparse(handle, events=("end",)):
            if element.tag.rsplit("}", 1)[-1] != "page":
                continue
            number += 1
            words = [
                {
                    "text": "".join(word.itertext()),
                    **{
                        key: float(word.attrib[key])
                        for key in ("xMin", "xMax", "yMin", "yMax")
                    },
                }
                for word in element.iter()
                if word.tag.rsplit("}", 1)[-1] == "word"
            ]
            yield (
                number,
                float(element.attrib["width"]),
                float(element.attrib["height"]),
                words,
            )
            element.clear()


def parse_source(spec, source_root, extraction_root, extraction_receipt_sha):
    source_sha = spec["source_sha256"]
    name, expected_district = SOURCES[source_sha]
    original = inside(source_root, spec["source_path"])
    with gzip.open(original, "rb") as handle:
        if hashlib.file_digest(handle, "sha256").hexdigest() != source_sha:
            raise ValueError(f"Original PDF checksum mismatch: {name}")
    artifact = next(
        item for item in spec["artifacts"] if item["path"] == f"{name}.xhtml.gz"
    )
    geometry = inside(extraction_root, artifact["path"])
    if sha256(geometry) != artifact["sha256"]:
        raise ValueError(f"Native extraction checksum mismatch: {name}")
    records, page_records = [], []
    district_name_raw = None
    district_code_raw = None
    previous = None
    for page, width, height, words in pages(geometry):
        if not (593 <= width <= 597 and 840 <= height <= 844):
            raise ValueError(f"Unexpected page geometry: {name} page {page}")
        heading = lines(select(words, 230, 700, 0, 30))
        if "2012" not in heading or "fuokZfpr" not in heading:
            raise ValueError(f"Unrecognized election heading: {name} page {page}")
        if page == 1:
            district_code_raw = lines(select(words, 110, 145, 65, 91))
            if district_code_raw != expected_district:
                raise ValueError(
                    f"District heading mismatch: {name}: {district_code_raw!r}"
                )
            district_name_raw = lines(select(words, 145, 320, 65, 91))
        anchors = sorted(
            [
                word
                for word in select(words, 0, 38, 65, 555)
                if re.fullmatch(r"[0-9]+", word["text"])
            ],
            key=lambda word: word["yMin"],
        )
        gaps = []
        for index, anchor in enumerate(anchors):
            serial = int(anchor["text"])
            top = anchor["yMin"] - 8
            bottom = anchors[index + 1]["yMin"] - 8 if index + 1 < len(anchors) else 555
            if bottom <= top or (
                index and anchor["yMin"] - anchors[index - 1]["yMin"] < 20
            ):
                raise ValueError(f"Ambiguous serial anchors: {name} page {page}")
            cells = {
                field: select(words, left, right, top, bottom)
                for field, (left, right) in BANDS.items()
            }
            flags = [
                "legacy_font_decoding_unreviewed",
                "compound_person_relation_and_category_cells",
                "office_subtype_unresolved",
                "independent_source_review_pending",
                "existing_winner_overlap_unreconciled",
            ]
            if previous is not None and serial != previous["serial"] + 1:
                gap = {
                    "previous_page": previous["page"],
                    "previous_serial": previous["serial"],
                    "next_page": page,
                    "next_serial": serial,
                }
                gaps.append(gap)
                flags.append("source_serial_discontinuity")
            previous = {"page": page, "serial": serial}
            raw = {field: lines(cell) or None for field, cell in cells.items()}
            ward_raw = raw["ward_number_raw"]
            ward = (
                int(ward_raw)
                if ward_raw and re.fullmatch(r"[0-9]+", ward_raw)
                else None
            )
            if ward is None:
                flags.append("ward_number_unresolved")
            for field, cell in cells.items():
                if not cell:
                    flags.append(f"{field}_empty")
                if any(word["xMax"] > BANDS[field][1] + 0.5 for word in cell):
                    flags.append(f"{field}_crosses_column_boundary")
            key = f"{source_sha}:{page}:{index + 1}"
            records.append(
                {
                    "record_id": hashlib.sha256(key.encode("ascii")).hexdigest(),
                    "source_sha256": source_sha,
                    "source_path": spec["source_path"],
                    "source_url": spec["source_url"],
                    "archive_capture_timestamp": spec["archive_capture_timestamp"],
                    "source_geometry_path": artifact["path"],
                    "source_geometry_sha256": artifact["sha256"],
                    "extraction_receipt_sha256": extraction_receipt_sha,
                    "source_page": page,
                    "source_row_on_page": index + 1,
                    "source_serial_raw": anchor["text"],
                    "source_serial": serial,
                    "row_top": top,
                    "row_bottom": bottom,
                    "district_source": name,
                    "district_code_raw": district_code_raw,
                    "district_name_encoded_raw": district_name_raw,
                    "district_context_source_page": 1,
                    "election_year": 2012,
                    "office_family": "urban_ward_member",
                    "record_kind": "elected_member_list_observation",
                    "ward_number": ward,
                    **raw,
                    "raw_cells_geometry_json": packed(cells),
                    "assignment_usable": False,
                    "quality_flags": sorted(flags),
                }
            )
        page_records.append(
            {
                "source_sha256": source_sha,
                "source": name,
                "page": page,
                "width": width,
                "height": height,
                "heading_encoded_raw": heading,
                "rows": len(anchors),
                "first_serial": int(anchors[0]["text"]) if anchors else None,
                "last_serial": int(anchors[-1]["text"]) if anchors else None,
                "above_previous_y90_window": sum(
                    word["yMin"] <= 90 for word in anchors
                ),
                "serial_discontinuities": gaps,
                "anchors": anchors,
            }
        )
    if len(page_records) != spec["pages"]:
        raise ValueError(f"Page-count mismatch: {name}")
    return records, page_records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--extraction-root", type=Path, required=True)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("data/interim/sec_urban_member_lists_2012"),
    )
    args = parser.parse_args()
    receipt_path = args.extraction_root / "extraction_receipt.json"
    receipt_bytes = receipt_path.read_bytes()
    extraction_receipt_sha = hashlib.sha256(receipt_bytes).hexdigest()
    inputs = json.loads(receipt_bytes)
    selected = [item for item in inputs["sources"] if item["source_sha256"] in SOURCES]
    if len(selected) != len(SOURCES) or len(
        {item["source_sha256"] for item in selected}
    ) != len(SOURCES):
        raise ValueError("Expected exactly the four pinned urban-member PDFs.")
    rows, page_records = [], []
    for spec in selected:
        source_rows, source_pages = parse_source(
            spec, args.source_root, args.extraction_root, extraction_receipt_sha
        )
        rows.extend(source_rows)
        page_records.extend(source_pages)
    if not rows:
        raise ValueError("No source rows found.")
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    output = args.output_root / stamp
    output.mkdir(parents=True, exist_ok=False)
    row_path = output / "member_observations.parquet"
    table = pa.Table.from_pylist(rows)
    pq.write_table(table, row_path, compression="zstd")
    page_path = output / "pages.jsonl.gz"
    with gzip.open(page_path, "wt", encoding="utf-8") as handle:
        for item in page_records:
            handle.write(packed(item) + "\n")
    dictionary = {
        "format_version": 1,
        "row_semantics": (
            "One printed numeric-serial source row; not a new unique seat or "
            "reconciled winner."
        ),
        "source_root": str(args.source_root.resolve()),
        "extraction_root": str(args.extraction_root.resolve()),
        "columns": {field.name: {"type": str(field.type)} for field in table.schema},
        "cell_policy": (
            "Encoded words grouped within three PDF points vertically, joined by "
            "spaces within each line. Exact words and coordinates retained in "
            "raw_cells_geometry_json."
        ),
        "compound_fields": {
            "person_and_relation_encoded_raw": (
                "Candidate and father/husband text retained together; no person split "
                "certified."
            ),
            "reported_sex_and_age_encoded_raw": (
                "Reported sex and age retained together; never used to infer "
                "reservation."
            ),
            "party_and_reservation_encoded_raw": (
                "Party and reservation text retained together; no category mapping "
                "applied."
            ),
        },
        "geometry": {
            "units": "PDF points, Poppler xMin/yMin with top-left origin",
            "column_bands": BANDS,
            "serial_anchor_bounds": [0, 38, 65, 555],
            "row_top": "serial yMin minus 8",
            "row_bottom": "next serial yMin minus 8; last row ends at y=555",
        },
        "district_context": (
            "Four-digit first-page heading, checked against pinned source; repeated "
            "as source-level context with page 1 citation."
        ),
        "privacy_policy": (
            "Address and telephone columns omitted from derived rows; original PDFs "
            "retained."
        ),
        "assignment_usable": False,
    }
    dictionary_path = output / "dictionary.json"
    write_json(dictionary_path, dictionary)
    counts = Counter(row["district_source"] for row in rows)
    result = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "status": "raw_source_rows_parsed_decoding_and_overlap_review_pending",
        "output": str(output.resolve()),
        "rows": len(rows),
        "pages": len(page_records),
        "rows_by_source": dict(counts),
        "rows_above_previous_y90_window": sum(
            page["above_previous_y90_window"] for page in page_records
        ),
        "serial_discontinuities": [
            {"source": page["source"], **gap}
            for page in page_records
            for gap in page["serial_discontinuities"]
        ],
        "quality_flags": dict(
            Counter(flag for row in rows for flag in row["quality_flags"])
        ),
        "source_pins": [
            {
                key: spec[key]
                for key in (
                    "source_sha256",
                    "source_path",
                    "source_url",
                    "archive_capture_timestamp",
                    "pages",
                )
            }
            for spec in selected
        ],
        "extraction_receipt": str(receipt_path.resolve()),
        "extraction_receipt_sha256": extraction_receipt_sha,
        "parser_sha256": sha256(Path(__file__)),
        "artifacts": [
            {"path": path.name, "sha256": sha256(path), "bytes": path.stat().st_size}
            for path in (row_path, page_path, dictionary_path)
        ],
        "central_integration_performed": False,
        "unique_seat_coverage_certified": False,
        "assignment_usable": False,
        "new_paid_api_cost_usd": 0,
    }
    write_json(output / "receipt.json", result)
    print(json.dumps(result, ensure_ascii=True), flush=True)


if __name__ == "__main__":
    main()
