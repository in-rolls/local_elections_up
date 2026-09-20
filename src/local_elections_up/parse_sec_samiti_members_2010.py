#!/usr/bin/env python3
"""Parse the held SEC 2010 samiti-member lists with source-heading provenance."""

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
LABEL_PATH = ROOT / "data/catalogs/samiti_2010_labels.json"
BANDS = (
    ("printed_serial_raw", 30, 66),
    ("ward_number_raw", 66, 118),
    ("seat_reservation_encoded_raw", 118, 235),
    ("candidate_name_encoded_raw", 235, 340),
    ("related_person_encoded_raw", 340, 425),
    ("candidate_category_encoded_raw", 425, 532),
    ("candidate_age_raw", 532, 560),
    ("reported_sex_encoded_raw", 560, 591),
    ("education_encoded_raw", 591, 665),
)
STRINGS = (
    "observation_id",
    "state",
    "office",
    "record_kind",
    "result_raw",
    "source_path",
    "source_sha256",
    "source_url",
    "district_code_raw",
    "district_name_encoded_raw",
    "block_code_raw",
    "block_name_encoded_raw",
    "reservation_class",
    "candidate_category_class",
    "reported_sex",
    "text_encoding",
    "cell_bboxes_json",
    *(name for name, _, _ in BANDS),
)
SCHEMA = pa.schema(
    [
        *((name, pa.string()) for name in STRINGS),
        ("election_year", pa.int16()),
        ("source_page", pa.int32()),
        ("source_row_on_page", pa.int32()),
        ("ward_number", pa.int32()),
        ("candidate_age", pa.int32()),
        ("block_context_source_page", pa.int32()),
        ("block_context_source_y", pa.float64()),
        ("women_reserved", pa.bool_()),
        ("candidate_category_women_label", pa.bool_()),
        ("is_winner", pa.bool_()),
        ("assignment_usable", pa.bool_()),
        ("quality_flags", pa.list_(pa.string())),
    ]
)


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def dump(path, value):
    path.write_text(
        json.dumps(value, ensure_ascii=True, indent=2) + "\n", encoding="utf-8"
    )


def compact(value):
    return re.sub(r"\s+", "", value or "")


def integer(value):
    value = (value or "").strip()
    return int(value) if re.fullmatch(r"[0-9]+", value) else None


def region(words, left, right, top, bottom):
    return [
        word
        for word in words
        if left <= word["x0"] < right and top <= word["y0"] < bottom
    ]


def text(words):
    lines = []
    for word in sorted(words, key=lambda item: (item["y0"], item["x0"])):
        if not lines or word["y0"] - lines[-1][0]["y0"] > 2:
            lines.append([])
        lines[-1].append(word)
    return "\n".join(
        " ".join(word["text"] for word in sorted(line, key=lambda item: item["x0"]))
        for line in lines
    )


def section(words, y, page, district):
    line = sorted(
        [word for word in words if abs(word["y0"] - y) <= 4],
        key=lambda word: word["x0"],
    )
    raw = text(line)
    ampersands = [word for word in line if word["text"] == "&"]
    if "fodkl" not in raw or len(ampersands) != 2:
        return None
    codes = [
        word["text"]
        for word in line
        if ampersands[0]["x1"] <= word["x0"] < ampersands[1]["x0"]
        and integer(word["text"]) is not None
    ]
    name = text([word for word in line if word["x0"] >= ampersands[1]["x1"]])
    if len(codes) != 1 or not name or district is None:
        return None
    return {
        "block_code_raw": codes[0],
        "block_name_encoded_raw": name,
        "block_context_source_page": page,
        "block_context_source_y": y,
        "district_code_raw": district,
    }


def parse_page(page, path, sha, number, previous, categories, sexes):
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
        "source_path": path,
        "source_sha256": sha,
        "source_page": number,
        "page_attributes": page.attrib,
        "words": words,
        "issues": [],
        "sections": [],
    }
    title = text(region(words, 30, 650, 20, 48))
    seat_header = text(region(words, 118, 235, 70, 113))
    winner_header = text(region(words, 235, 340, 70, 113))
    if not (
        "2010" in title
        and "fuokZfpr" in title
        and "vkj{k.k" in seat_header
        and "fuokZfpr" in winner_header
    ):
        info["issues"].append("elected_member_table_header_unrecognized")
        return [], info, None
    district = text(region(words, 105, 150, 48, 72)).strip()
    if integer(district) is None:
        district = None
        info["issues"].append("district_code_unresolved")
    district_name = text(region(words, 215, 650, 48, 72)) or None
    filename_code = Path(path).stem.rsplit("_", 1)[-1]
    if filename_code.isdigit() and district != filename_code:
        info["issues"].append("district_code_disagrees_with_filename")
    current = previous
    if current and current["district_code_raw"] != district:
        current = None
    left_words = sorted(region(words, 0, 66, 119, 800), key=lambda word: word["y0"])
    anchors = [word for word in left_words if integer(word["text"]) is not None]
    barriers = []
    for word in left_words:
        if integer(word["text"]) is not None:
            continue
        if not barriers or abs(word["y0"] - barriers[-1]["y0"]) > 3:
            barriers.append(word)
    events = sorted(
        [
            *((word["y0"], 1, word) for word in anchors),
            *((word["y0"], 0, word) for word in barriers),
        ],
        key=lambda item: (item[0], item[1]),
    )
    rows = []
    for event_index, (y, kind, _anchor) in enumerate(events):
        if kind == 0:
            current = section(words, y, number, district)
            info["sections"].append({"y": y, "context": current})
            if current is None:
                info["issues"].append("unrecognized_row_or_section_prefix")
            continue
        top = y - 4
        bottom = (
            events[event_index + 1][0] - 4 if event_index + 1 < len(events) else y + 36
        )
        cells = {
            name: region(words, left, right, top, bottom) for name, left, right in BANDS
        }
        values = {name: text(cell) or None for name, cell in cells.items()}
        flags = ["legacy_name_decode_pending", "independent_source_review_pending"]
        row = {field.name: None for field in SCHEMA}
        row.update(values)
        if current:
            row.update(current)
            if current["block_context_source_page"] != number:
                flags.append("block_context_carried_from_source_heading_page")
        else:
            flags.append("block_context_unresolved")
        row.update(
            observation_id=hashlib.sha256(
                f"{sha}:{number}:{len(rows) + 1}".encode()
            ).hexdigest(),
            state="Uttar Pradesh",
            election_year=2010,
            office="panchayat_samiti_member",
            record_kind="reported_official",
            result_raw="listed_in_source_elected_member_table",
            source_path=path,
            source_sha256=sha,
            source_page=number,
            source_row_on_page=len(rows) + 1,
            district_code_raw=district,
            district_name_encoded_raw=district_name,
            ward_number=integer(values["ward_number_raw"]),
            candidate_age=integer(values["candidate_age_raw"]),
            text_encoding="legacy_pdf_font_with_reviewed_category_labels",
            assignment_usable=False,
            is_winner=None,
            cell_bboxes_json=json.dumps(cells, ensure_ascii=True),
        )
        for raw_field, caste_field, woman_field in (
            ("seat_reservation_encoded_raw", "reservation_class", "women_reserved"),
            (
                "candidate_category_encoded_raw",
                "candidate_category_class",
                "candidate_category_women_label",
            ),
        ):
            normalized = categories.get(compact(values[raw_field]))
            row[caste_field] = (
                normalized["reservation_class"] if normalized else "unknown"
            )
            row[woman_field] = normalized["women_reserved"] if normalized else None
            if normalized is None:
                flags.append(raw_field + "_unmapped")
        row["reported_sex"] = sexes.get(compact(values["reported_sex_encoded_raw"]))
        if row["reported_sex"] is None:
            flags.append("reported_sex_unmapped")
        if row["ward_number"] is None:
            flags.append("ward_number_unresolved")
        if row["candidate_age"] is None:
            flags.append("candidate_age_unresolved")
        if not row["candidate_name_encoded_raw"]:
            flags.append("candidate_name_missing")
        for name, _left, right in BANDS:
            if any(word["x1"] > right + 1 for word in cells[name]):
                flags.append(name + "_crosses_column_boundary")
        row["quality_flags"] = flags
        rows.append(row)
    if not rows:
        info["issues"].append("no_member_row_anchors")
    info["candidate_rows"] = len(rows)
    info["issues"] = sorted(set(info["issues"]))
    for row in rows:
        row["quality_flags"].extend(info["issues"])
    return rows, info, current


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", action="append", help="Repo-relative PDF")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ROOT / "data/interim/sec_samiti_members_2010",
    )
    args = parser.parse_args()
    label_bytes = LABEL_PATH.read_bytes()
    labels = json.loads(label_bytes)
    categories = {
        compact(key): value for key, value in labels["category_labels"].items()
    }
    sexes = {compact(key): value for key, value in labels["sex_labels"].items()}
    sources = (
        [ROOT / relative for relative in args.source]
        if args.source
        else sorted((ROOT / "data/2010/area_panchayat_member").glob("*.pdf"))
    )
    if not sources:
        raise ValueError("No samiti-member PDFs found")
    output = args.output_root / datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    output.mkdir(parents=True, exist_ok=False)
    receipt = {
        "status": "incomplete",
        "assignment_usable": False,
        "parser_sha256": digest(Path(__file__)),
        "labels_path": LABEL_PATH.relative_to(ROOT).as_posix(),
        "labels_sha256": hashlib.sha256(label_bytes).hexdigest(),
        "sources": [],
        "new_paid_api_cost_usd": 0,
        "schema": {field.name: str(field.type) for field in SCHEMA},
        "notes": [
            "The printed list describes elected samiti members.",
            "Reported-official observations are not independently certified winners.",
            "Seat and candidate categories are kept on separate axes.",
            "Addresses are excluded from the typed table and its cell geometry.",
            "Original PDFs and compressed extraction evidence retain source context.",
            "Block context never crosses a document or unrecognized page.",
        ],
    }
    dump(output / "INCOMPLETE.json", receipt)
    buffer, quality, classes, seat_keys = [], Counter(), Counter(), Counter()
    failures = 0
    with (
        pq.ParquetWriter(
            output / "member_observations.parquet", SCHEMA, compression="zstd"
        ) as writer,
        gzip.open(output / "pages.jsonl.gz", "wt", encoding="utf-8") as page_stream,
    ):
        for source in sources:
            relative = source.resolve().relative_to(ROOT.resolve()).as_posix()
            sha = digest(source)
            item = {"source_path": relative, "source_sha256": sha}
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
                current = None
                for number, page in enumerate(pages, 1):
                    rows, info, current = parse_page(
                        page, relative, sha, number, current, categories, sexes
                    )
                    item["rows"] += len(rows)
                    item["page_issues"].update(info["issues"])
                    page_stream.write(json.dumps(info, ensure_ascii=True) + "\n")
                    for row in rows:
                        quality.update(row["quality_flags"])
                        classes.update([row["reservation_class"]])
                        key = (
                            row["district_code_raw"],
                            row["block_code_raw"],
                            row["ward_number"],
                        )
                        if all(value is not None for value in key):
                            seat_keys[key] += 1
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
    collisions = [
        {
            "district_code_raw": key[0],
            "block_code_raw": key[1],
            "ward_number": key[2],
            "observations": count,
        }
        for key, count in seat_keys.items()
        if count > 1
    ]
    receipt.update(
        status="parsed_with_source_failures"
        if failures
        else "parsed_pending_validation",
        rows=sum(classes.values()),
        reservation_classes=dict(classes),
        quality_flags=dict(quality),
        source_failures=failures,
        key_collisions=collisions,
        parquet_sha256=digest(output / "member_observations.parquet"),
        page_evidence_sha256=digest(output / "pages.jsonl.gz"),
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
                "reservation_classes": dict(classes),
                "key_collisions": len(collisions),
                "quality_flags": dict(quality),
                "assignment_usable": False,
                "new_paid_api_cost_usd": 0,
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
