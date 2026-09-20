"""Parse cached Ghaziabad reservation tables without merging source occurrences.

Input is the provenance-linked pdfplumber cache under --source-root. Raw cells,
printed serials, constituency numbers, and shorthand codes remain distinct.
Outputs are research candidates, never canonical election or winner records.
"""

import argparse
import collections
import gzip
import hashlib
import io
import json
import re
from pathlib import Path

import pandas as pd
from local_reservations.common import krutidev

PROFILES = {
    "81615589": ("Muradnagar", "kshetra_panchayat_member", 13),
    "81615593": ("Rajapur", "kshetra_panchayat_member", 13),
    "81615599": ("Bhojpur", "kshetra_panchayat_member", 14),
    "81615602": ("Loni", "kshetra_panchayat_member", 13),
    "81615613": (None, "zila_panchayat_member", 13),
    "81615616": (None, "block_head", 10),
    "81615624": ("Bhojpur", "gram_pradhan", 10),
    "81615628": ("Loni", "gram_pradhan", 10),
    "81615630": ("Rajapur", "gram_pradhan", 10),
    "81615635": ("Muradnagar", "gram_pradhan", 10),
}
CATEGORY_COLUMNS = [
    ("ST", True),
    ("ST", False),
    ("SC", True),
    ("SC", False),
    ("BC", True),
    ("BC", False),
    ("NONE", True),
    ("NONE", False),
]
OBSERVED_CODES = {
    "UR": ("NONE", False),
    "OBC-L": ("BC", True),
    "OBC": ("BC", False),
    "SCL": ("SC", True),
    "SC": ("SC", False),
    "L": ("NONE", True),
}
EMPTY = {"", "-", "&", "\u2013", "\u2014"}
CELL_KEY = ["source_sha256", "source_page", "table_index", "row_index", "column_index"]


def integer(value):
    text = (value or "").strip()
    return int(text) if re.fullmatch(r"[0-9]+", text) else None


def label_category(raw):
    label = re.sub(r"\s+", " ", krutidev.to_unicode(raw))
    if "जनजात" in label:
        caste = "ST"
    elif "जात" in label:
        caste = "SC"
    elif "पिछ" in label:
        caste = "BC"
    elif "अनारक्षित" in label or "स्त्र" in label:
        caste = "NONE"
    else:
        return None
    return caste, "स्त्र" in label or "महिल" in label


def save_parquet(out, name, rows, columns=None):
    frame = pd.DataFrame(rows, columns=columns)
    buffer = io.BytesIO()
    frame.to_parquet(buffer, index=False, compression="zstd")
    payload = buffer.getvalue()
    with (out / name).open("xb") as handle:
        handle.write(payload)
    return {
        "rows": len(frame),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.source_root
    extraction = json.loads(
        (root / "native_extraction/extraction_receipt.json").read_text()
    )
    controls = json.loads((root / "source_layout_review/controls.json").read_text())
    blank = json.loads(
        (root / "pages_without_text_review/classification.json").read_text()
    )
    documents = {doc["media_id"]: doc for doc in extraction["documents"]}
    if set(documents) != set(PROFILES):
        raise ValueError("Source set differs from the ten profiled documents")
    decoded_path = root / "native_decoding/krutidev_cells_decoded.parquet"
    decoded = pd.read_parquet(decoded_path)
    if decoded.duplicated(CELL_KEY).any():
        raise ValueError("Decoded cell locator is not unique")
    labels = {
        tuple(row[key] for key in CELL_KEY): row["text_unicode_candidate"]
        for row in decoded.to_dict("records")
    }
    rows = []
    appendix_rows = []
    code_strips = []
    excluded = collections.Counter()
    cache_inputs = []
    finality_ids = {item["media_id"] for item in controls["documents"]}
    for media_id, (block, tier, expected_width) in PROFILES.items():
        doc = documents[media_id]
        if (
            media_id == "81615593"
            and doc["source_sha256"]
            != "df8a3f00903977213f731ad9a7e1211c548e310d54e8d0416f55223f6f86acb5"
        ):
            raise ValueError("Rajapur source differs from the visually partitioned PDF")
        cache = root / "native_extraction" / doc["cache"]
        payload = cache.read_bytes()
        cache_sha = hashlib.sha256(payload).hexdigest()
        if cache_sha != doc["cache_sha256"]:
            raise ValueError(f"Native cache hash differs: {media_id}")
        cache_inputs.append({"file": str(cache.relative_to(root)), "sha256": cache_sha})
        member = tier.endswith("_member")
        category_start = 5 if member else 2
        for line in gzip.decompress(payload).decode("utf-8").splitlines():
            page = json.loads(line)
            if page["source_sha256"] != doc["source_sha256"]:
                raise ValueError("Page/source hash association differs")
            if (
                page["source_sha256"] == blank["source_sha256"]
                and page["source_page"] in blank["source_pages"]
            ):
                excluded["source_confirmed_blank_pages"] += 1
                continue
            if page.get("extraction_error"):
                raise ValueError(f"Unresolved native extraction error: {media_id}")
            for table in page["tables"]:
                for native_row in table["rows"]:
                    cells = native_row["cells"]
                    values = [cell["text_raw"] for cell in cells]
                    if len(values) >= 10 and values[:10] == [
                        str(i) for i in range(1, 11)
                    ]:
                        excluded["printed_column_number_rows"] += 1
                        continue
                    source_page = int(page["source_page"])
                    appendix = media_id == "81615593" and (
                        (source_page == 8 and table["table_index"] == 1)
                        or 9 <= source_page <= 13
                    )
                    strip = media_id == "81615593" and 14 <= source_page <= 21
                    if appendix or strip:
                        serial = integer(values[0]) if values else None
                        if appendix and serial is None:
                            excluded["appendix_header_rows"] += 1
                            continue
                        prefix = (
                            doc["source_sha256"],
                            source_page,
                            table["table_index"],
                            native_row["row_index"],
                        )
                        evidence = {
                            "state": "UP",
                            "district_context": "Ghaziabad",
                            "block_context": block,
                            "media_id": media_id,
                            "source_sha256": doc["source_sha256"],
                            "source_url": doc["source_url"],
                            "source_pdf_path": doc["source_pdf_path"],
                            "source_page": source_page,
                            "table_index": table["table_index"],
                            "row_index": native_row["row_index"],
                            "raw_cells_json": json.dumps(values, ensure_ascii=False),
                            "cell_bboxes_json": json.dumps(
                                [cell["bbox"] for cell in cells]
                            ),
                            "observed_row_width": len(values),
                            "year_context": None,
                            "assignment_usable": False,
                            "record_type": (
                                "undated_coded_appendix"
                                if appendix
                                else "unlinked_code_strip"
                            ),
                            "linked_current_record": None,
                            "source_review_evidence": (
                                "historical_table_review/source_schema_findings.json"
                            ),
                        }
                        if appendix:
                            evidence.update(
                                {
                                    "column_01_raw": values[0],
                                    "place_name_raw": (
                                        values[1] if len(values) > 1 else None
                                    ),
                                    "place_name_unicode_candidate": labels.get(
                                        (*prefix, 1)
                                    ),
                                    "column_03_raw": (
                                        values[2] if len(values) > 2 else None
                                    ),
                                    "column_04_raw": (
                                        values[3] if len(values) > 3 else None
                                    ),
                                    "area_description_raw": (
                                        values[4] if len(values) > 4 else None
                                    ),
                                    "area_description_unicode_candidate": labels.get(
                                        (*prefix, 4)
                                    ),
                                    "numeric_measure_raw": (
                                        values[5] if len(values) > 5 else None
                                    ),
                                    "numeric_measure_meaning": None,
                                    "code_columns_json": json.dumps(
                                        {
                                            str(i + 1): value
                                            for i, value in enumerate(values)
                                            if i >= 6
                                        },
                                        ensure_ascii=False,
                                    ),
                                    "code_column_years": None,
                                    "quality_flags": (
                                        "appendix_schema_semantics_unresolved;independent_row_review_pending"
                                    ),
                                }
                            )
                            appendix_rows.append(evidence)
                        else:
                            evidence["quality_flags"] = (
                                "strip_to_row_alignment_unresolved;independent_row_review_pending"
                            )
                            code_strips.append(evidence)
                        continue
                    serial = integer(values[0]) if values else None
                    if serial is None:
                        excluded["unnumbered_header_or_fragment_rows"] += 1
                        continue
                    flags = {"independent_row_review_pending"}
                    width_ok = len(values) == expected_width
                    if not width_ok:
                        flags.add("row_width_mismatch")
                    ward = integer(values[2]) if member and len(values) > 2 else None
                    if member and ward is None:
                        flags.add("constituency_number_missing")
                    category_cells = (
                        values[category_start : category_start + 8] if width_ok else []
                    )
                    active = [
                        (i, text)
                        for i, text in enumerate(category_cells)
                        if text is not None and text.strip() not in EMPTY
                    ]
                    if width_ok and any(text is None for text in category_cells):
                        flags.add("category_cell_missing")
                    if width_ok and len(active) != 1:
                        flags.add("active_category_count_not_one")
                    caste = woman = active_column = active_raw = None
                    if width_ok and len(active) == 1:
                        index, active_raw = active[0]
                        active_column = category_start + index + 1
                        mapped = CATEGORY_COLUMNS[index]
                        if label_category(active_raw) != mapped:
                            flags.add("category_text_column_disagreement")
                        elif "category_cell_missing" not in flags:
                            caste, woman = mapped
                    shorthand = (
                        values[13] if expected_width == 14 and width_ok else None
                    )
                    shorthand_status = "not_present"
                    if shorthand is not None:
                        code = shorthand.strip().upper()
                        if code not in OBSERVED_CODES:
                            shorthand_status = "code_not_in_visually_observed_mapping"
                        elif caste is None:
                            shorthand_status = "primary_category_unresolved"
                        elif OBSERVED_CODES[code] != (caste, woman):
                            shorthand_status = "disagrees_with_primary_category"
                            flags.add("supplemental_code_disagreement")
                        else:
                            shorthand_status = "agrees_with_primary_category"
                    if shorthand_status == "disagrees_with_primary_category":
                        caste = woman = None
                    prefix = (
                        doc["source_sha256"],
                        page["source_page"],
                        table["table_index"],
                        native_row["row_index"],
                    )

                    def cell_value(index, row_values=values):
                        return row_values[index] if index < len(row_values) else None

                    record = {
                        "state": "UP",
                        "district_context": "Ghaziabad",
                        "year_context": 2021,
                        "block_context": block,
                        "tier": tier,
                        "media_id": media_id,
                        "source_sha256": doc["source_sha256"],
                        "source_url": doc["source_url"],
                        "source_pdf_path": doc["source_pdf_path"],
                        "source_page": page["source_page"],
                        "table_index": table["table_index"],
                        "row_index": native_row["row_index"],
                        "printed_serial": serial,
                        "constituency_number": ward,
                        "serial_differs_from_constituency_number": (
                            member and serial != ward
                        ),
                        "place_name_raw": cell_value(1),
                        "place_name_unicode_candidate": labels.get((*prefix, 1)),
                        "constituency_name_raw": cell_value(3) if member else None,
                        "constituency_name_unicode_candidate": (
                            labels.get((*prefix, 3)) if member else None
                        ),
                        "area_description_raw": cell_value(4) if member else None,
                        "area_description_unicode_candidate": (
                            labels.get((*prefix, 4)) if member else None
                        ),
                        "raw_cells_json": json.dumps(values, ensure_ascii=False),
                        "cell_bboxes_json": json.dumps(
                            [cell["bbox"] for cell in cells]
                        ),
                        "observed_row_width": len(values),
                        "expected_row_width": expected_width,
                        "active_category_column": active_column,
                        "active_category_text_raw": active_raw,
                        "caste_reservation_candidate": caste,
                        "woman_reserved_candidate": woman,
                        "supplemental_code_raw": shorthand,
                        "supplemental_code_status": shorthand_status,
                        "source_finality": (
                            "final_as_printed_on_reviewed_first_page_media_copy"
                            if media_id in finality_ids
                            else "printed_finality_not_visually_reviewed"
                        ),
                        "document_date": None,
                        "election_date": None,
                        "assignment_usable": False,
                        "duplicate_group_id": None,
                        "_flags": flags,
                    }
                    if record["place_name_unicode_candidate"] is None:
                        flags.add("place_name_unicode_candidate_unavailable")
                    rows.append(record)
    groups = collections.defaultdict(list)
    for record in rows:
        if record["constituency_number"] is not None:
            groups[(record["source_sha256"], record["constituency_number"])].append(
                record
            )
    duplicates = []
    for key, members in groups.items():
        if len(members) < 2:
            continue
        group_id = hashlib.sha256(json.dumps(key).encode()).hexdigest()[:20]
        categories = {
            (row["caste_reservation_candidate"], row["woman_reserved_candidate"])
            for row in members
            if row["caste_reservation_candidate"] is not None
        }
        for row in members:
            row["duplicate_group_id"] = group_id
            row["_flags"].add("repeated_constituency_occurrence")
            if len(categories) > 1:
                row["_flags"].add("repeated_constituency_category_disagreement")
        duplicates.append(
            {
                "duplicate_group_id": group_id,
                "source_sha256": key[0],
                "constituency_number": key[1],
                "occurrences": len(members),
                "category_variants": len(categories),
                "all_occurrences_category_resolved": all(
                    row["caste_reservation_candidate"] is not None for row in members
                ),
                "locators_json": json.dumps(
                    [
                        [row["source_page"], row["table_index"], row["row_index"]]
                        for row in members
                    ]
                ),
            }
        )
    control_results = []
    for control in controls["documents"]:
        by_serial = {
            row["printed_serial"]: row
            for row in rows
            if row["media_id"] == control["media_id"] and row["source_page"] == 1
        }
        for serial, expected in enumerate(control["active_category_columns"], start=1):
            row = by_serial.get(serial)
            matches = row is not None and row["active_category_column"] == expected
            control_results.append(
                {
                    "media_id": control["media_id"],
                    "source_page": 1,
                    "printed_serial": serial,
                    "expected_active_category_column": expected,
                    "extracted_active_category_column": (
                        row["active_category_column"] if row else None
                    ),
                    "matches": matches,
                    "source_image_sha256": control["image_sha256"],
                }
            )
            if row is not None and not matches:
                row["_flags"].add("visual_source_control_failed")
                row["caste_reservation_candidate"] = None
                row["woman_reserved_candidate"] = None
    flag_counts = collections.Counter()
    for row in rows:
        flag_counts.update(row["_flags"])
        row["quality_flags"] = ";".join(sorted(row.pop("_flags")))
    args.output.mkdir(exist_ok=False)
    artifacts = {
        "reservation_rows.parquet": save_parquet(
            args.output, "reservation_rows.parquet", rows
        ),
        "repeated_constituencies.parquet": save_parquet(
            args.output,
            "repeated_constituencies.parquet",
            duplicates,
            columns=[
                "duplicate_group_id",
                "source_sha256",
                "constituency_number",
                "occurrences",
                "category_variants",
                "all_occurrences_category_resolved",
                "locators_json",
            ],
        ),
        "coded_appendix_rows.parquet": save_parquet(
            args.output, "coded_appendix_rows.parquet", appendix_rows
        ),
        "unlinked_code_strips.parquet": save_parquet(
            args.output, "unlinked_code_strips.parquet", code_strips
        ),
    }
    by_source = []
    for media_id in PROFILES:
        selected = [row for row in rows if row["media_id"] == media_id]
        serials = {row["printed_serial"] for row in selected}
        wards = {
            row["constituency_number"]
            for row in selected
            if row["constituency_number"] is not None
        }
        by_source.append(
            {
                "media_id": media_id,
                "tier": PROFILES[media_id][1],
                "block_context": PROFILES[media_id][0],
                "observations": len(selected),
                "distinct_printed_serials": len(serials),
                "distinct_printed_constituency_numbers": len(wards),
                "internal_serial_gaps": (
                    sorted(set(range(1, max(serials) + 1)) - serials)
                    if serials
                    else None
                ),
            }
        )
    receipt = {
        "observations": len(rows),
        "by_source": by_source,
        "coded_appendix_rows": len(appendix_rows),
        "unlinked_code_strip_rows": len(code_strips),
        "partition_evidence": "historical_table_review/source_schema_findings.json",
        "supplemental_L_mapping_evidence": (
            "Bhojpur ward 23, physical page 2; women-only primary category and code L"
            " visually corroborated."
        ),
        "tier_observations": dict(collections.Counter(row["tier"] for row in rows)),
        "rows_with_category_candidates": sum(
            row["caste_reservation_candidate"] is not None for row in rows
        ),
        "quality_flags": dict(flag_counts),
        "duplicate_groups": len(duplicates),
        "source_control_rows": len(control_results),
        "source_controls_matching": sum(row["matches"] for row in control_results),
        "source_controls": control_results,
        "exclusions": dict(excluded),
        "native_cache_inputs": cache_inputs,
        "artifacts": artifacts,
        "parser_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "shared_decoder_sha256": (
            hashlib.sha256(Path(krutidev.__file__).read_bytes()).hexdigest()
        ),
        "decoded_cells_sha256": hashlib.sha256(decoded_path.read_bytes()).hexdigest(),
        "source_path_base": str(root),
        "assignment_usable": False,
        "rows_deduplicated": False,
        "new_paid_api_cost_usd": 0,
        "limitations": [
            "Distinct printed numbers are not independently certified coverage.",
            "Controls are a convenience selection of 39 rows, not an accuracy sample.",
            (
                "Media copies with final headings are not independently authenticated"
                " official originals."
            ),
            (
                "Names are decoded candidates; mixed-font or excluded cells remain"
                " unavailable."
            ),
            (
                "Seven-column category slices are not shifted or padded into valid"
                " assignments."
            ),
            (
                "Rajapur coded appendix years and numeric-measure semantics remain"
                " unknown."
            ),
            "Isolated code strips are retained without guessed row attachments.",
        ],
    }
    with (args.output / "parse_receipt.json").open("x") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
    print(
        json.dumps(
            {
                key: receipt[key]
                for key in (
                    "observations",
                    "by_source",
                    "tier_observations",
                    "rows_with_category_candidates",
                    "quality_flags",
                    "duplicate_groups",
                    "source_control_rows",
                    "source_controls_matching",
                    "coded_appendix_rows",
                    "unlinked_code_strip_rows",
                    "artifacts",
                    "new_paid_api_cost_usd",
                )
            },
            ensure_ascii=False,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
