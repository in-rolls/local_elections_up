"""Parse the pinned SEC 2005 elected samiti-member list, retaining source cells."""

import argparse
import gzip
import hashlib
import json
import re
import tarfile
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from local_elections_up.parse_sec_samiti_members_2010 import (
    compact,
    digest,
    dump,
    integer,
    region,
    text,
)

ROOT = Path(__file__).resolve().parents[2]
SOURCE_SHA = "3adc5b67a9f98c6529ba4bbb17dfd14ba6174527bdf0786df071fb563bfadfb8"
BANDS = (
    ("ward_number_raw", 90, 123),
    ("ward_name_encoded_raw", 123, 240),
    ("candidate_name_encoded_raw", 240, 385),
    ("reported_sex_encoded_raw", 385, 425),
    ("seat_reservation_encoded_raw", 425, 555),
)
CATEGORY_LABELS = {
    "vukjf{kr": ("unreserved", False),
    "vuqlwfprtkfr": ("sc", False),
    "vuqlwfprtkfr&efgyk": ("sc", True),
    "fiNM+htkfr": ("obc", False),
    "fiNM+htkfr&efgyk": ("obc", True),
    "efgyk": ("unknown", True),
    "vuqlwfprtutkfr": ("st", False),
    "vuqlwfprtutkfr&efgyk": ("st", True),
}
LABEL_REVIEW_PATH = ROOT / "data/reference/sec_samiti_members_2005_label_review.json.gz"
LABEL_REVIEW_SHA = "a1df09f394ef08f9238cef1d025c1a694c516a4d9c21f3767adfa9c4c68ebfae"
KEY_REVIEW_PATH = ROOT / "data/reference/sec_samiti_members_2005_key_review.json.gz"
KEY_REVIEW_SHA = "7009c86d594944668eb0ccecddd9dcfde3ef14059eddc1a3f37de374bea1c03c"
SOURCE_STATUS_LABELS = {"fufoZjks/k": "unopposed", "fjDr": "vacant"}
SEX_LABELS = {'iq#"k': "male", "efgyk": "female"}
STRINGS = (
    "observation_id",
    "state",
    "office",
    "record_kind",
    "result_raw",
    "source_status",
    "candidate_text_role",
    "source_duplicate_group_id",
    "source_duplicate_kind",
    "source_key_review_sha256",
    "source_path",
    "source_sha256",
    "source_url",
    "archive_capture_timestamp",
    "district_code_raw",
    "district_name_encoded_raw",
    "block_code_raw",
    "block_name_encoded_raw",
    "reported_sex",
    "reservation_class",
    "text_encoding",
    "cell_bboxes_json",
    *(name for name, _, _ in BANDS),
)
SCHEMA = pa.schema(
    [(name, pa.string()) for name in STRINGS]
    + [
        ("election_year", pa.int16()),
        ("source_page", pa.int32()),
        ("source_row_on_page", pa.int32()),
        ("ward_number", pa.int32()),
        ("block_context_source_page", pa.int32()),
        ("block_context_source_y", pa.float64()),
        ("women_reserved", pa.bool_()),
        ("is_winner", pa.bool_()),
        ("assignment_usable", pa.bool_()),
        ("quality_flags", pa.list_(pa.string())),
    ]
)


def load_source_review(path, expected_sha):
    if digest(path) != expected_sha:
        raise ValueError("Source-review packet checksum mismatch")
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        review = json.load(handle)
    if review["source_pdf_sha256"] != SOURCE_SHA:
        raise ValueError("Review evidence refers to another PDF")
    archive_spec = review["review_image_archive"]
    archive_path = (ROOT / archive_spec["path"]).resolve()
    if not archive_path.is_relative_to(ROOT.resolve()):
        raise ValueError("Review archive path escapes the source repository")
    if digest(archive_path) != archive_spec["sha256"]:
        raise ValueError("Reviewed image archive checksum mismatch")
    with tarfile.open(archive_path, "r:gz") as archive:
        for reviewed_image in review["images"]:
            handle = archive.extractfile(reviewed_image["member"])
            if handle is None:
                raise ValueError("Reviewed source-page image is missing")
            with handle:
                image_sha = hashlib.file_digest(handle, "sha256").hexdigest()
            if image_sha != reviewed_image["sha256"]:
                raise ValueError("Reviewed source-page image checksum mismatch")
    return review


def block_heading(words, y, page, district):
    line = region(words, 90, 555, y - 4, y + 5)
    label = compact(text(line))
    if district is None or not all(part in label for part in ("Cykd", "dksM", "uke&")):
        return None
    code = text(region(line, 185, 225, y - 4, y + 5)).strip()
    name = text(region(line, 240, 555, y - 4, y + 5)).strip()
    if integer(code) is None or not name:
        return None
    return {
        "district_code_raw": district,
        "block_code_raw": code,
        "block_name_encoded_raw": name,
        "block_context_source_page": page,
        "block_context_source_y": y,
    }


def parse_page(page, number, previous, source):
    words = [
        {
            "text": node.text or "",
            "x0": float(node.attrib["xMin"]),
            "x1": float(node.attrib["xMax"]),
            "y0": float(node.attrib["yMin"]),
            "y1": float(node.attrib["yMax"]),
        }
        for node in page.iter()
        if node.tag.endswith("}word")
    ]
    info = {
        "source_sha256": SOURCE_SHA,
        "source_page": number,
        "page_attributes": page.attrib.copy(),
        "words": words,
        "issues": [],
        "sections": [],
    }
    title = compact(text(region(words, 180, 555, 72, 94)))
    winner_header = compact(text(region(words, 240, 385, 110, 132)))
    category_header = compact(text(region(words, 425, 555, 110, 132)))
    if not (
        float(page.attrib["width"]) == 595
        and float(page.attrib["height"]) == 842
        and all(part in title for part in ("2005", "fuokZfpr", "{ks=k", "iapk;r"))
        and "fot;h" in winner_header
        and "vkj{k.k" in category_header
    ):
        info["issues"].append("source_layout_or_elected_member_header_unrecognized")
        return [], info, None
    district = text(region(words, 185, 215, 94, 112)).strip()
    if not re.fullmatch(r"[0-9]{4}", district):
        district = None
        info["issues"].append("district_code_unresolved")
    district_name = text(region(words, 215, 555, 94, 112)) or None
    current = previous
    if current and current["district_code_raw"] != district:
        current = None
    left = sorted(region(words, 90, 123, 130, 745), key=lambda word: word["y0"])
    anchors = [word for word in left if re.match(r"^[0-9]", word["text"])]
    barriers = []
    for word in left:
        if re.match(r"^[0-9]", word["text"]):
            continue
        if not barriers or abs(word["y0"] - barriers[-1]["y0"]) > 3:
            barriers.append(word)
    events = sorted(
        [(word["y0"], 1) for word in anchors] + [(word["y0"], 0) for word in barriers]
    )
    rows = []
    for index, (y, kind) in enumerate(events):
        if kind == 0:
            current = block_heading(words, y, number, district)
            info["sections"].append({"y": y, "context": current})
            if current is None:
                info["issues"].append("unrecognized_row_or_section_prefix")
            continue
        top = y - 6
        bottom = events[index + 1][0] - 6 if index + 1 < len(events) else 745
        cells = {
            name: region(words, left, right, top, bottom) for name, left, right in BANDS
        }
        values = {name: text(cell) or None for name, cell in cells.items()}
        row = {field.name: None for field in SCHEMA}
        row.update(values)
        flags = ["legacy_name_decode_pending", "independent_source_review_pending"]
        if current:
            row.update(current)
            if current["block_context_source_page"] != number:
                flags.append("block_context_carried_from_source_heading_page")
        else:
            flags.append("block_context_unresolved")
        row.update(
            observation_id=hashlib.sha256(
                f"{SOURCE_SHA}:{number}:{len(rows) + 1}".encode()
            ).hexdigest(),
            state="Uttar Pradesh",
            office="panchayat_samiti_member",
            election_year=2005,
            record_kind="reported_official",
            result_raw="listed_in_source_elected_member_table",
            source_path=source["source_path"],
            source_sha256=SOURCE_SHA,
            source_url=source["source_url"],
            archive_capture_timestamp=source["archive_capture_timestamp"],
            source_page=number,
            source_row_on_page=len(rows) + 1,
            district_code_raw=district,
            district_name_encoded_raw=district_name,
            ward_number=integer(values["ward_number_raw"]),
            text_encoding="mixed_embedded_legacy_fonts",
            assignment_usable=False,
            is_winner=None,
            cell_bboxes_json=json.dumps(
                cells, ensure_ascii=True, separators=(",", ":")
            ),
        )
        category_label = compact(values["seat_reservation_encoded_raw"])
        category = CATEGORY_LABELS.get(category_label)
        row["source_status"] = SOURCE_STATUS_LABELS.get(category_label)
        if row["source_status"] == "vacant":
            row["candidate_text_role"] = "printed_vacancy_notice"
            flags.append("candidate_cell_contains_vacancy_notice")
        row["reservation_class"] = category[0] if category else "unknown"
        row["women_reserved"] = category[1] if category else None
        row["reported_sex"] = SEX_LABELS.get(
            compact(values["reported_sex_encoded_raw"])
        )
        if category is None:
            if row["source_status"] is not None:
                flags.append("noncategory_status_in_reservation_cell")
            elif not category_label:
                flags.append("seat_reservation_cell_empty")
            else:
                flags.append("seat_reservation_label_unmapped")
        elif category[0] == "unknown":
            flags.append("reservation_class_not_explicit_in_source")
        if row["reported_sex"] is None:
            flags.append("reported_sex_label_unmapped")
        if row["ward_number"] is None or row["ward_number"] <= 0:
            flags.append("ward_number_unresolved_or_nonpositive")
        if not row["candidate_name_encoded_raw"]:
            flags.append("candidate_name_missing")
        for name, _, right in BANDS:
            if any(word["x1"] > right + 1 for word in cells[name]):
                flags.append(name + "_crosses_column_boundary")
        reviewed_key = source["key_reviews"].get((number, len(rows) + 1))
        if reviewed_key:
            if row["observation_id"] != reviewed_key["observation_id"] or any(
                row[field] != value
                for field, value in reviewed_key["expected_raw"].items()
            ):
                raise ValueError("Reviewed repeated source row changed")
            if [
                row["district_code_raw"],
                row["block_code_raw"],
                row["ward_number"],
            ] != reviewed_key["source_key"]:
                raise ValueError("Reviewed source seat key changed")
            row["source_duplicate_group_id"] = reviewed_key["group_id"]
            row["source_duplicate_kind"] = reviewed_key["kind"]
            row["source_key_review_sha256"] = KEY_REVIEW_SHA
            flags.append("source_repeated_key_reviewed")
            flags.append(
                {
                    "exact_repeated_source_row": "duplicate_source_row",
                    "same_candidate_ward_name_variant": (
                        "duplicate_source_ward_name_variant"
                    ),
                    "conflicting_source_records": "conflicting_source_seat_key",
                }[reviewed_key["kind"]]
            )
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
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--extraction-root", type=Path, required=True)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ROOT / "data/interim/sec_samiti_members_2005",
    )
    args = parser.parse_args()
    extraction_receipt = args.extraction_root / "extraction_receipt.json"
    receipt_bytes = extraction_receipt.read_bytes()
    extraction = json.loads(receipt_bytes)
    matches = [
        item for item in extraction["sources"] if item["source_sha256"] == SOURCE_SHA
    ]
    if len(matches) != 1 or matches[0]["pages"] != 1585:
        raise ValueError("Pinned 2005 source missing or ambiguous")
    source = matches[0]
    pdf_path = args.source_root / source["source_path"]
    with gzip.open(pdf_path, "rb") as stream:
        source_hash = hashlib.file_digest(stream, "sha256").hexdigest()
    if source_hash != SOURCE_SHA:
        raise ValueError("Original PDF checksum mismatch")
    xmls = [item for item in source["artifacts"] if item["path"].endswith(".xhtml.gz")]
    if len(xmls) != 1:
        raise ValueError("Native word-coordinate artifact is ambiguous")
    xml_path = args.extraction_root / xmls[0]["path"]
    if digest(xml_path) != xmls[0]["sha256"]:
        raise ValueError("Native extraction checksum mismatch")
    label_review = load_source_review(LABEL_REVIEW_PATH, LABEL_REVIEW_SHA)
    if (
        any(
            CATEGORY_LABELS.get(label) != tuple(value)
            for label, value in label_review["category_mappings"].items()
        )
        or label_review["source_status_mappings"] != SOURCE_STATUS_LABELS
    ):
        raise ValueError("Parser mappings differ from reviewed source evidence")
    key_review = load_source_review(KEY_REVIEW_PATH, KEY_REVIEW_SHA)
    key_rows = {}
    for group in key_review["groups"]:
        if group["kind"] not in {
            "exact_repeated_source_row",
            "same_candidate_ward_name_variant",
            "conflicting_source_records",
        }:
            raise ValueError("Unrecognized source duplicate classification")
        for observation in group["observations"]:
            key = (observation["source_page"], observation["source_row_on_page"])
            if key in key_rows:
                raise ValueError("A source row belongs to multiple reviewed key groups")
            key_rows[key] = observation | {
                "source_key": group["source_key"],
                "group_id": group["group_id"],
                "kind": group["kind"],
            }
    image = source["page_one_image"]
    if digest(args.extraction_root / image["path"]) != image["sha256"]:
        raise ValueError("Source label-review image checksum mismatch")
    source = dict(source)
    source["key_reviews"] = key_rows
    source["source_path"] = pdf_path.resolve().relative_to(ROOT.resolve()).as_posix()
    output = args.output_root / datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    output.mkdir(parents=True, exist_ok=False)
    receipt = {
        "status": "incomplete",
        "source_sha256": SOURCE_SHA,
        "source_path": source["source_path"],
        "source_url": source["source_url"],
        "archive_capture_timestamp": source["archive_capture_timestamp"],
        "extraction_receipt_path": str(extraction_receipt.resolve()),
        "extraction_receipt_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
        "native_xml_sha256": xmls[0]["sha256"],
        "parser_sha256": digest(Path(__file__)),
        "helper_parser_sha256": digest(
            Path(__file__).with_name("parse_sec_samiti_members_2010.py")
        ),
        "label_evidence": image,
        "additional_label_review_path": str(LABEL_REVIEW_PATH.relative_to(ROOT)),
        "additional_label_review_sha256": LABEL_REVIEW_SHA,
        "source_status_labels": SOURCE_STATUS_LABELS,
        "source_key_review_path": str(KEY_REVIEW_PATH.relative_to(ROOT)),
        "source_key_review_sha256": KEY_REVIEW_SHA,
        "category_labels": CATEGORY_LABELS,
        "sex_labels": SEX_LABELS,
        "assignment_usable": False,
        "new_paid_api_cost_usd": 0,
    }
    dump(output / "INCOMPLETE.json", receipt)
    flags, classes, labels, sexes, keys, districts, blocks = (
        Counter() for _ in range(7)
    )
    buffer, page_issues, current = [], [], None
    page_count = row_count = 0
    with (
        gzip.open(xml_path, "rb") as xml_stream,
        pq.ParquetWriter(
            output / "member_observations.parquet", SCHEMA, compression="zstd"
        ) as writer,
        (output / "pages.jsonl.gz").open("wb") as page_file,
        gzip.GzipFile(filename="", mode="wb", fileobj=page_file, mtime=0) as pages,
    ):
        for _, page in ET.iterparse(xml_stream, events=("end",)):
            if not page.tag.endswith("}page"):
                continue
            page_count += 1
            rows, info, current = parse_page(page, page_count, current, source)
            pages.write((json.dumps(info, ensure_ascii=True) + "\n").encode())
            if info["issues"]:
                page_issues.append({"page": page_count, "issues": info["issues"]})
            for row in rows:
                flags.update(row["quality_flags"])
                classes.update([row["reservation_class"]])
                labels.update([row["seat_reservation_encoded_raw"]])
                sexes.update([row["reported_sex_encoded_raw"]])
                districts.update([row["district_code_raw"]])
                key = (
                    row["district_code_raw"],
                    row["block_code_raw"],
                    row["ward_number"],
                )
                if all(value is not None for value in key):
                    keys.update([key])
                    blocks.update([key[:2]])
            row_count += len(rows)
            buffer.extend(rows)
            if len(buffer) >= 5000:
                writer.write_table(pa.Table.from_pylist(buffer, schema=SCHEMA))
                buffer.clear()
            page.clear()
            if page_count % 100 == 0:
                print(json.dumps({"pages": page_count, "rows": row_count}), flush=True)
        if buffer:
            writer.write_table(pa.Table.from_pylist(buffer, schema=SCHEMA))
    if page_count != 1585:
        raise ValueError("Pinned source page count changed")
    if flags["source_repeated_key_reviewed"] != len(key_rows):
        raise ValueError("Not all reviewed repeated source rows were found")
    receipt.update(
        status="parsed_pending_source_review",
        pages=page_count,
        rows=row_count,
        reservation_classes=dict(classes),
        quality_flags=dict(flags),
        raw_category_labels=[
            {"raw": key, "rows": count} for key, count in labels.items()
        ],
        raw_sex_labels=[{"raw": key, "rows": count} for key, count in sexes.items()],
        district_codes=[
            {"raw": key, "rows": count} for key, count in districts.items()
        ],
        district_block_pairs=len(blocks),
        key_collisions=[
            {
                "district_code_raw": key[0],
                "block_code_raw": key[1],
                "ward_number": key[2],
                "observations": count,
            }
            for key, count in keys.items()
            if count > 1
        ],
        page_issues=page_issues,
        parquet_sha256=digest(output / "member_observations.parquet"),
        page_evidence_sha256=digest(output / "pages.jsonl.gz"),
        election_year_policy=(
            "2005 must occur in each parsed page's elected-member heading."
        ),
        context_policy=(
            "Block context follows source headings only; resets after an unrecognized "
            "page, district change, or unrecognized left-column prefix."
        ),
        category_policy=(
            "Only source-reviewed labels are mapped. Woman-only labels retain an "
            "unknown caste class; reported sex and noncategory notices are separate "
            "axes."
        ),
        identity_policy=(
            "Printed district, block and ward codes are source identifiers, not a "
            "certified administrative crosswalk."
        ),
        duplicate_policy=(
            "All rows retained. Source-reviewed repeats and conflicting keys carry "
            "group IDs and evidence hashes; no automatic deletion, ward renumbering "
            "or winner selection."
        ),
        winner_policy=(
            "The source lists elected members; names and non-person notices still "
            "need review, so is_winner remains null."
        ),
    )
    dictionary = {
        "schema": {field.name: str(field.type) for field in SCHEMA},
        "raw_fields": (
            "Encoded source text, including line breaks, is preserved without spelling "
            "correction."
        ),
        "observation_id": (
            "SHA256 of source PDF SHA256, one-based page and one-based extracted row, "
            "separated by colons."
        ),
        "source_sha256": (
            "Hash of the uncompressed original PDF; source_path points to its lossless "
            "gzip container."
        ),
        "ward_number": (
            "Numeric reading of the printed ward field; nonpositive and nonnumeric "
            "values are flagged."
        ),
        "ward_name_encoded_raw": "Printed ward name, not a Gram Panchayat identifier.",
        "block_context_source_page": (
            "Page of the explicit block heading used for this row."
        ),
        "block_context_source_y": "Heading top coordinate in PDF points.",
        "reservation_class": (
            "Source seat label: unreserved, sc, st, obc, or unknown. Woman-only labels "
            "leave caste class unknown; no inferred caste."
        ),
        "women_reserved": (
            "Source seat category axis, never inferred from the officeholder's sex."
        ),
        "reported_sex": (
            "Literal source label mapped to male/female; not inferred from names."
        ),
        "source_status": (
            "Literal noncategory notice in the reservation cell: unopposed or vacant; "
            "null otherwise."
        ),
        "candidate_text_role": (
            "printed_vacancy_notice for the source-reviewed vacant seat; null is not "
            "a certification of a person name."
        ),
        "is_winner": (
            "Null; source-list membership does not certify a reviewed person as a "
            "winner."
        ),
        "assignment_usable": "False: this native extraction is provisional.",
        "cell_bboxes_json": (
            "Original word text and x0, x1, y0, y1 coordinates by source column."
        ),
        "source_duplicate_group_id": (
            "SHA256 of the source PDF and printed district/block/ward key for a "
            "reviewed repeated-key group."
        ),
        "source_duplicate_kind": (
            "exact_repeated_source_row, same_candidate_ward_name_variant, or "
            "conflicting_source_records; null outside reviewed groups."
        ),
        "source_key_review_sha256": (
            "Checksum of the review packet containing raw-cell guards and archived "
            "source-page evidence."
        ),
        "quality_flags": (
            "Unresolved source, label, geometry, context and review conditions."
        ),
    }
    dump(output / "dictionary.json", dictionary)
    dump(output / "receipt.json", receipt)
    (output / "INCOMPLETE.json").unlink()
    print(
        json.dumps(
            {
                "output": str(output),
                "rows": row_count,
                "pages": page_count,
                "district_codes": len([code for code in districts if code is not None]),
                "district_block_pairs": len(blocks),
                "key_collisions": len(receipt["key_collisions"]),
                "pages_with_issues": len(page_issues),
                "quality_flags": dict(flags),
                "reservation_classes": dict(classes),
                "new_paid_api_cost_usd": 0,
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
