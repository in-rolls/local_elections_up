# /// script
# requires-python = ">=3.11"
# dependencies = ["pyarrow"]
# ///
"""Build provenance-linked UP exports partitioned by office and record type."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from local_elections_up.office_provenance import STRINGS as PROVENANCE_STRINGS
from local_elections_up.office_provenance import SourceProvenance
from local_elections_up.parse_sec_candidate_csvs import LABELS, LABELS_BYTES, number
from local_elections_up.standardize_sec_samiti_2010 import FIELDS as SAMITI_FIELDS
from local_elections_up.standardize_sec_samiti_2010 import STRINGS as SAMITI_STRINGS
from local_elections_up.standardize_sec_samiti_2010 import (
    load_context as samiti_context,
)
from local_elections_up.standardize_sec_samiti_2010 import normalize as normalize_samiti

ROOT = Path(__file__).resolve().parents[2]
PRI_LABEL_PATH = ROOT / "data/catalogs/pri_2010_category_labels.json"
PRI_LABEL_BYTES = PRI_LABEL_PATH.read_bytes()
PRI_LABELS = json.loads(PRI_LABEL_BYTES)
PRI_LABEL_SHA = hashlib.sha256(PRI_LABEL_BYTES).hexdigest()
if PRI_LABELS["format_version"] != 1:
    raise ValueError("Unsupported PRI 2010 label dictionary")
URBAN_LABELS = LABELS["urban_post_labels"]
URBAN_BODIES = LABELS["urban_body_tiers"]
RURAL = {
    "gp_head": "gram_panchayat_head",
    "gp_ward": "gram_panchayat_member",
    "block_head": "panchayat_samiti_head",
    "block_member": "panchayat_samiti_member",
    "zp_head": "zilla_parishad_head",
    "zp_member": "zilla_parishad_member",
    "gram_pradhan": "gram_panchayat_head",
    "kshetra_panchayat_member": "panchayat_samiti_member",
    "kshetra_panchayat_pramukh": "panchayat_samiti_head",
    "zila_panchayat_member": "zilla_parishad_member",
}
ARCHIVE_OFFICES = {
    "district_chair": "zilla_parishad_head",
    "district_member": "zilla_parishad_member",
    "block_chair": "panchayat_samiti_head",
    "senior_deputy_block_chair": "panchayat_samiti_senior_deputy",
    "junior_deputy_block_chair": "panchayat_samiti_junior_deputy",
}
SHARED_HEADS = {"panchayat_samiti_head", "zilla_parishad_head"}
STRINGS = [
    "source_printed_page_raw",
    "source_boundary_review_status_raw",
    "source_fields_json",
    "source_subject_temporality",
    "source_boundary_raw",
    "source_boundary_value",
    "source_block_name_value",
    "source_ward_name_value",
    "source_ward_number_value",
    "source_family_counts_json",
    "source_reservation_value",
    "source_review_evidence_json",
    "source_unresolved_fields_json",
    "source_parent_observation_id",
    "samiti_2005_source_fields_json",
    "samiti_2005_source_status",
    "samiti_2005_candidate_text_role",
    "samiti_2005_source_duplicate_group_id",
    "samiti_2005_source_duplicate_kind",
    "samiti_2005_source_key_review_sha256",
    "samiti_2005_district_name_unicode_candidate",
    "samiti_2005_block_name_unicode_candidate",
    "samiti_2005_ward_name_unicode_candidate",
    "samiti_2005_candidate_name_unicode_candidate",
    "pri_2010_seat_label_decode_status",
    "pri_2010_candidate_label_decode_status",
    "pri_2010_sex_label_decode_status",
    "pri_2010_label_dictionary_path",
    "pri_2010_label_dictionary_sha256",
    "pri_2010_source_fields_json",
    *SAMITI_STRINGS,
    *PROVENANCE_STRINGS,
    "body_type_encoded_raw",
    "related_person_encoded_raw",
    "reported_sex_encoded_raw",
    "party_encoded_raw",
    "symbol_encoded_raw",
    "candidate_age_raw",
    "nomination_number_raw",
    "record_id",
    "office",
    "record_kind",
    "source_collection",
    "source_observation_id",
    "source_artifact_path",
    "source_artifact_sha256",
    "source_document_sha256",
    "source_local_path",
    "source_url",
    "source_response_path",
    "source_row_field",
    "source_copy_group",
    "district_name_raw",
    "block_name_raw",
    "body_name_raw",
    "body_code_raw",
    "ward_name_raw",
    "ward_code_raw",
    "membership_ward_label_raw",
    "candidate_name_raw",
    "related_person_raw",
    "reported_sex_raw",
    "party_raw",
    "education_raw",
    "seat_reservation_raw",
    "candidate_category_raw",
    "reservation_class",
    "result_raw",
    "valid_votes_raw",
    "vote_percentage_raw",
    "poll_percentage_raw",
    "text_encoding",
    "district_name_encoded_raw",
    "block_name_encoded_raw",
    "ward_name_encoded_raw",
    "candidate_name_encoded_raw",
    "candidate_and_related_name_encoded_raw",
    "seat_reservation_encoded_raw",
    "candidate_category_encoded_raw",
    "office_encoded_raw",
    "reported_category_encoded_raw",
    "body_name_encoded_raw",
    "source_artifact_format",
    "source_finality_raw",
    "source_review_status_raw",
    "name_review_status_raw",
    "source_image_path",
    "source_image_sha256",
    "source_printed_serial_raw",
    "source_cell_bboxes_json",
]
SCHEMA = pa.schema(
    [(name, pa.string()) for name in STRINGS]
    + SAMITI_FIELDS
    + [
        ("election_year", pa.int16()),
        ("source_artifact_row", pa.int64()),
        ("source_page", pa.int64()),
        ("source_row", pa.int64()),
        ("source_csv_record", pa.int64()),
        ("source_line_start", pa.int64()),
        ("source_line_end", pa.int64()),
        ("ward_number", pa.int64()),
        ("membership_ward_number", pa.int64()),
        ("valid_votes", pa.int64()),
        ("vote_percentage", pa.float64()),
        ("poll_percentage", pa.float64()),
        ("women_reserved", pa.bool_()),
        ("is_winner", pa.bool_()),
        ("assignment_usable", pa.bool_()),
        ("quality_flags", pa.list_(pa.string())),
        ("name_reading_uncertain", pa.bool_()),
        ("source_category_column", pa.int64()),
    ]
)


def file_hash(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2) + "\n")


def pick(row, *keys):
    return next((row[key] for key in keys if row.get(key) is not None), None)


def flags(value):
    if value is None:
        return []
    if isinstance(value, list):
        return list(value)
    return [item for item in str(value).split(";") if item]


def resolve_office(row, adapter):
    if adapter == "pri_2010":
        return row["office"]
    if adapter == "gp":
        return "gram_panchayat_head"
    if adapter in {"csv", "urban_2006", "samiti_2010", "samiti_2005"}:
        return row["office"]
    if adapter in {"zp_archive", "block_archive"}:
        return ARCHIVE_OFFICES[row["office_normalized"]]
    tier = row.get("tier")
    if tier in RURAL:
        return RURAL[tier]
    label = pick(row, "post_name_raw", "post_label_raw")
    if label in URBAN_LABELS:
        return URBAN_LABELS[label]
    return URBAN_BODIES[row["local_body_type_raw"]][tier]


def reservation_class(value):
    if value is None:
        return "unknown"
    return {
        "SC": "sc",
        "ST": "st",
        "OBC": "obc",
        "BC": "obc",
        "GENERAL": "general",
        "UNRESERVED": "general",
        "NONE": "general",
        "sc": "sc",
        "st": "st",
        "obc": "obc",
        "general": "general",
    }.get(value, "unknown")


def regional_row(original, source):
    row = dict(original)
    quality = flags(row.get("quality_flags"))
    row["election_year"] = int(pick(row, "election_year", "year_context", "year"))
    row["district_name_raw"] = row.get("district_context")
    row["block_name_raw"] = pick(row, "block_name_transcribed", "block_context")
    office = RURAL[row["tier"]]
    if office == "panchayat_samiti_head" and row["block_name_raw"] is None:
        row["block_name_raw"] = row.get("place_name_unicode_candidate")
    if office == "gram_panchayat_head":
        row["gp_name_raw"] = pick(
            row, "gram_panchayat_name_candidate", "place_name_unicode_candidate"
        )
    if office.endswith("_member"):
        row["ward_name_raw"] = row.get("constituency_name_unicode_candidate")
        raw_number = pick(row, "ward_number", "constituency_number")
        if raw_number is not None and str(raw_number).strip():
            try:
                numeric = float(raw_number)
                if not numeric.is_integer() or numeric < 1:
                    raise ValueError("Not a positive ward number")
                row["ward"] = int(numeric)
            except (ValueError, OverflowError):
                row["ward"] = None
                quality.append("ward_number_unresolved")
    row["reservation_category"] = pick(
        row, "caste_reservation_candidate", "caste_reservation"
    )
    raw_woman = pick(row, "woman_reserved_candidate", "woman_reserved")
    if isinstance(raw_woman, bool) or raw_woman is None:
        row["reserved_for_women"] = raw_woman
    elif str(raw_woman).lower() in {"true", "false"}:
        row["reserved_for_women"] = str(raw_woman).lower() == "true"
    else:
        row["reserved_for_women"] = None
        quality.append("women_reservation_unresolved")
    for key in (
        "source_page",
        "source_row_on_page",
        "row_index",
        "category_source_column",
    ):
        value = row.get(key)
        if value is not None and str(value).strip():
            row[key] = int(value)
        else:
            row[key] = None
    base = Path(source["source_base"])
    local = pick(row, "source_pdf_path", "source_path")
    if local:
        row["source_path"] = (base / local).as_posix()
    if row.get("source_image_path"):
        row["source_image_path"] = (base / row["source_image_path"]).as_posix()
    row["quality_flags"] = quality
    return row


def source_batches(path):
    if path.suffix != ".csv":
        for batch in pq.ParquetFile(path).iter_batches(batch_size=5000):
            yield batch.to_pylist()
        return
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None or len(set(reader.fieldnames)) != len(
            reader.fieldnames
        ):
            raise ValueError(f"Invalid CSV header: {path}")
        previous_line = reader.line_num
        records = []
        for index, row in enumerate(reader, 1):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"CSV field-count mismatch: {path}, record {index}")
            row["source_csv_record"] = index
            row["source_line_start"] = previous_line + 1
            row["source_line_end"] = reader.line_num
            previous_line = reader.line_num
            records.append(row)
            if len(records) == 5000:
                yield records
                records = []
        if records:
            yield records


def normalize(row, source, path, parent_sha, position, context=None):
    adapter = source["adapter"]
    if adapter == "pri_2010" and (
        parent_sha != source["expected_sha256"]
        or row["office"] != source["office"]
        or row["record_kind"] != source["record_kind"]
        or row["assignment_usable"] is not False
        or row["is_winner"] is not None
    ):
        raise ValueError("PRI 2010 source pin, office, or provisional status changed")
    if adapter == "regional":
        row = regional_row(row, source)
    office = resolve_office(row, adapter)
    quality = flags(row.get("quality_flags")) + flags(row.get("structural_flags"))
    observation = pick(row, "observation_id", "election_gp_key")
    if observation is None:
        observation = (
            str(row.get("source_sha256") or parent_sha)
            + ":"
            + str(row.get("source_csv_record") or position)
        )
    out = {field.name: None for field in SCHEMA}
    out.update(
        record_id=hashlib.sha256(f"{source['id']}\0{observation}".encode()).hexdigest(),
        office=office,
        record_kind=source["record_kind"],
        source_collection=source["id"],
        source_observation_id=pick(row, "observation_id", "election_gp_key"),
        source_artifact_path=path.relative_to(ROOT).as_posix(),
        source_artifact_sha256=parent_sha,
        source_artifact_row=position,
        source_document_sha256=row.get("source_sha256"),
        source_local_path=pick(row, "source_path", "source_file"),
        source_url=row.get("source_url"),
        source_response_path=pick(
            row, "source_response_repo_path", "source_response_path"
        ),
        source_page=pick(row, "source_page", "result_page"),
        source_csv_record=row.get("source_csv_record"),
        source_line_start=row.get("source_line_start"),
        source_line_end=row.get("source_line_end"),
        election_year=int(row["election_year"]),
        district_name_raw=pick(
            row, "district_name_raw", "district_name_hindi", "district_filter_name_raw"
        ),
        block_name_raw=pick(
            row,
            "block_name_raw",
            "block_name_hindi",
            "block_filter_name_raw",
            "block_raw",
        ),
        body_name_raw=pick(
            row,
            "gp_filter_name_raw",
            "gp_name_raw",
            "gp_name_hindi",
            "local_body_name_raw",
            "body_raw",
        ),
        body_code_raw=pick(row, "gp_filter_code", "local_body_code"),
        ward_name_raw=pick(row, "ward_name_raw", "ward_label_raw"),
        ward_code_raw=row.get("ward_code"),
        candidate_name_raw=pick(
            row,
            "candidate_name_raw",
            "winner_name_raw",
            "pradhan_name_hindi",
            "candidate_name",
        ),
        related_person_raw=pick(row, "related_person_raw", "relation_name_raw"),
        reported_sex_raw=pick(
            row, "sex_raw", "gender_raw", "winner_sex_hindi", "reported_sex"
        ),
        party_raw=pick(row, "party_name_raw", "party_raw"),
        education_raw=row.get("education_raw"),
        seat_reservation_raw=pick(
            row, "seat_reservation_raw", "reservation_raw", "reservation_status_hindi"
        ),
        candidate_category_raw=row.get("candidate_category_raw"),
        reservation_class=reservation_class(
            pick(
                row,
                "reservation_class",
                "reservation_category",
                "caste_reservation",
                "printed_post_caste",
            )
        ),
        women_reserved=pick(
            row,
            "reserved_for_women",
            "woman_reserved",
            "women_reserved",
            "printed_post_woman",
        ),
        result_raw=pick(row, "result_raw", "result_status_raw", "result_status_hindi"),
        valid_votes_raw=row.get("valid_votes_raw"),
        vote_percentage_raw=pick(row, "vote_percentage_raw", "vote_share_raw"),
        poll_percentage_raw=pick(row, "poll_percentage_raw", "turnout_raw"),
        is_winner=True
        if source["record_kind"] in {"declared_winner", "elected_official"}
        else row.get("is_winner"),
        assignment_usable=False,
        text_encoding="unicode",
        source_artifact_format=path.suffix.lstrip("."),
        source_finality_raw=pick(row, "source_finality", "publication_status"),
        source_review_status_raw=row.get("review_status"),
        name_review_status_raw=row.get("name_review_status"),
        name_reading_uncertain=row.get("name_reading_uncertain"),
        source_image_path=row.get("source_image_path"),
        source_image_sha256=row.get("source_image_sha256"),
        source_category_column=pick(
            row, "category_source_column", "active_category_column"
        ),
        source_printed_serial_raw=str(row["printed_serial"])
        if row.get("printed_serial") is not None
        else None,
        source_cell_bboxes_json=row.get("cell_bboxes_json"),
    )
    if adapter == "csv":
        if out["result_raw"] not in {"सविरोध", "निर्विरोध"}:
            raise ValueError("2015 winner-list contest status changed")
        label = out["seat_reservation_raw"]
        known = {
            "अनारक्षित": ("general", False),
            "महिला": ("general", True),
            "अनुसूचित जाति": ("sc", False),
            "अनुसूचित जाति महिला": ("sc", True),
            "अनुसूचित जनजाति": ("st", False),
            "अनुसूचित जनजाति महिला": ("st", True),
            "अन्य पिछड़ा वर्ग": ("obc", False),
            "अन्य पिछड़ा वर्ग महिला": ("obc", True),
        }
        if label in known:
            out["reservation_class"], out["women_reserved"] = known[label]
        else:
            quality.append("unmapped_seat_reservation_label")
    if adapter == "gp" and row.get("winner_markers_conflict"):
        out["is_winner"] = None
        quality.append("winner_markers_conflict")
    if out["women_reserved"] is not None:
        out["women_reserved"] = bool(out["women_reserved"])
    for key in (
        "source_row_on_page",
        "table_row_index",
        "source_row_number",
        "row_index",
    ):
        if row.get(key) is not None:
            out["source_row"] = int(row[key])
            out["source_row_field"] = key
            break
    for target, candidates in (
        ("valid_votes", ("valid_votes",)),
        ("vote_percentage", ("vote_percentage", "vote_share")),
        ("poll_percentage", ("poll_percentage", "turnout")),
    ):
        value = pick(row, *candidates)
        out[target] = (
            value
            if value is not None
            else number(
                out[target + "_raw"],
                target,
                quality,
                percentage=target != "valid_votes",
            )
        )
    if adapter == "csv":
        out["district_name_raw"] = (
            row.get("body_raw")
            if office == "zilla_parishad_head"
            else pick(row, "district_field_raw", "district_filename_raw")
        )
        if office in SHARED_HEADS:
            out["source_copy_group"] = row["source_sha256"]
    if adapter in {"zp_archive", "block_archive"}:
        out["text_encoding"] = "legacy_arjun"
        for key in (
            "district_name_encoded_raw",
            "block_name_encoded_raw",
            "ward_name_encoded_raw",
            "candidate_name_encoded_raw",
            "candidate_and_related_name_encoded_raw",
            "office_encoded_raw",
            "candidate_category_encoded_raw",
        ):
            out[key] = row.get(key)
        out["block_name_encoded_raw"] = pick(
            row, "block_context_name_encoded_raw", "block_name_encoded_raw"
        )
        out["seat_reservation_encoded_raw"] = row.get("post_category_encoded_raw")
        out["reported_category_encoded_raw"] = row.get("category_encoded_raw")
        if adapter == "zp_archive":
            if office == "zilla_parishad_member":
                out["ward_number"] = row.get("ward_number_in_result")
            else:
                out["membership_ward_number"] = row.get("ward_number_in_result")
                out["membership_ward_label_raw"] = row.get("ward_name_encoded_raw")
        else:
            out["membership_ward_number"] = row.get("membership_ward_number")
            out["membership_ward_label_raw"] = row.get(
                "membership_ward_name_encoded_raw"
            )
    elif office.endswith("_member"):
        out["ward_number"] = row.get("ward")
    if adapter == "regional":
        if row.get("place_name_raw") is not None:
            out["text_encoding"] = "legacy_krutidev_with_decoded_candidates"
            out["body_name_encoded_raw"] = row.get("place_name_raw")
            out["ward_name_encoded_raw"] = row.get("constituency_name_raw")
            out["seat_reservation_encoded_raw"] = row.get("active_category_text_raw")
            quality.append("decoded_name_candidate_not_certified")
        if row.get("name_reading_uncertain"):
            quality.append("name_reading_uncertain")
    if adapter == "gp":
        out["body_code_raw"] = row.get("gp_number_raw")
    if adapter == "pri_2010":
        out.update(
            text_encoding=row["text_encoding"],
            district_name_encoded_raw=pick(
                row, "district_name_encoded_raw", "district_context_name_encoded_raw"
            ),
            block_name_encoded_raw=row["body_name_encoded_raw"]
            if office == "panchayat_samiti_head"
            else None,
            body_name_encoded_raw=row["body_name_encoded_raw"],
            body_code_raw=row["body_number_raw"],
            candidate_name_encoded_raw=row["candidate_name_encoded_raw"],
            seat_reservation_encoded_raw=row["seat_reservation_encoded_raw"],
            candidate_category_encoded_raw=row["candidate_category_encoded_raw"],
            reported_category_encoded_raw=row["reported_category_encoded_raw"],
            source_cell_bboxes_json=row["cell_geometry_json"],
            source_printed_serial_raw=row["printed_serial_raw"],
            ward_number=row["ward_number"]
            if office == "zilla_parishad_member"
            else None,
            pri_2010_source_fields_json=json.dumps(
                {
                    key: value
                    for key, value in row.items()
                    if key != "cell_geometry_json"
                },
                ensure_ascii=True,
                separators=(",", ":"),
            ),
        )
        apply_pri_2010_labels(out, row, quality)
        if row["source_url"] is None:
            quality.append("original_http_source_provenance_unresolved")
    if adapter == "urban_2006":
        out["text_encoding"] = row["text_encoding"]
        out["district_name_raw"] = row["district_name_english_raw"]
        out["ward_number"] = row["ward_number"]
        out["source_printed_serial_raw"] = row["printed_serial_raw"]
        for key in (
            "body_type_encoded_raw",
            "body_name_encoded_raw",
            "ward_name_encoded_raw",
            "candidate_name_encoded_raw",
            "related_person_encoded_raw",
            "candidate_category_encoded_raw",
            "seat_reservation_encoded_raw",
            "party_encoded_raw",
            "symbol_encoded_raw",
            "nomination_number_raw",
        ):
            out[key] = row[key]
        out["reported_sex_encoded_raw"] = row["sex_encoded_raw"]
        out["office_encoded_raw"] = row["office_label_encoded_raw"]
        out["candidate_age_raw"] = row["age_raw"]
    if adapter == "samiti_2010":
        normalize_samiti(row, out, quality, context)
    if adapter == "samiti_2005":
        normalize_samiti_2005(row, out, quality, source, parent_sha)
    if not out["district_name_raw"] and not out["district_name_encoded_raw"]:
        quality.append("district_name_unresolved")
    quality.append("independent_office_release_validation_pending")
    out["quality_flags"] = list(dict.fromkeys(quality))
    return out


def normalize_samiti_2005(row, out, quality, source, parent_sha):
    if (
        parent_sha != source["expected_sha256"]
        or row["source_sha256"] != source["source_document_sha256"]
        or row["election_year"] != source["election_year"]
        or row["office"] != source["office"]
        or row["record_kind"] != source["record_kind"]
        or row["assignment_usable"] is not False
        or row["is_winner"] is not None
        or row["reservation_class"] not in {"unreserved", "sc", "st", "obc", "unknown"}
    ):
        raise ValueError("Samiti 2005 source pin or provisional semantics changed")
    out.update(
        text_encoding="mixed_legacy_fonts_with_unreviewed_unicode_candidates",
        ward_number=row["ward_number"],
        ward_code_raw=row["ward_number_raw"],
        body_code_raw=row["block_code_raw"],
        reservation_class="general"
        if row["reservation_class"] == "unreserved"
        else row["reservation_class"],
        is_winner=None,
        assignment_usable=False,
        name_review_status_raw="unicode_candidates_pending_source_review",
        samiti_2005_source_fields_json=json.dumps(
            row, ensure_ascii=True, separators=(",", ":")
        ),
    )
    for field in (
        "district_name_encoded_raw",
        "block_name_encoded_raw",
        "ward_name_encoded_raw",
        "candidate_name_encoded_raw",
        "reported_sex_encoded_raw",
        "seat_reservation_encoded_raw",
    ):
        out[field] = row[field]
    for field in (
        "source_status",
        "candidate_text_role",
        "source_duplicate_group_id",
        "source_duplicate_kind",
        "source_key_review_sha256",
    ):
        out[f"samiti_2005_{field}"] = row[field]
    for field in ("district_name", "block_name", "ward_name", "candidate_name"):
        out[f"samiti_2005_{field}_unicode_candidate"] = row[
            f"{field}_encoded_unicode_candidate"
        ]
    quality.append("decoded_name_candidate_not_certified")


def apply_pri_2010_labels(out, row, quality):
    if row["source_sha256"] not in PRI_LABELS["source_documents"]:
        return
    out["pri_2010_label_dictionary_path"] = PRI_LABEL_PATH.relative_to(ROOT).as_posix()
    out["pri_2010_label_dictionary_sha256"] = PRI_LABEL_SHA
    for kind in ("seat", "candidate"):
        field = (
            "seat_reservation_encoded_raw"
            if kind == "seat"
            else "candidate_category_encoded_raw"
        )
        raw = row[field]
        label = PRI_LABELS["category_labels"].get(raw)
        out[f"pri_2010_{kind}_label_decode_status"] = (
            "missing"
            if raw is None
            else "unmapped"
            if label is None
            else "source_reviewed_exact_match"
        )
        if label is None:
            quality.append(f"pri_2010_{kind}_label_unresolved")
            continue
        if (
            not isinstance(label["label"], str)
            or not label["label"]
            or label["reservation_class"]
            not in {"general", "sc", "st", "obc", "unknown"}
            or type(label["women_reserved"]) is not bool
        ):
            raise ValueError("Invalid PRI 2010 category dictionary entry")
        if kind == "seat":
            out["seat_reservation_raw"] = label["label"]
            out["reservation_class"] = label["reservation_class"]
            out["women_reserved"] = label["women_reserved"]
            if label["reservation_class"] == "unknown":
                quality.append("seat_caste_axis_not_explicit")
        else:
            out["candidate_category_raw"] = label["label"]
    raw_sex = row["sex_encoded_raw"]
    out["reported_sex_raw"] = PRI_LABELS["sex_labels"].get(raw_sex)
    out["pri_2010_sex_label_decode_status"] = (
        "missing"
        if raw_sex is None
        else "unmapped"
        if out["reported_sex_raw"] is None
        else "source_reviewed_exact_match"
    )
    if out["reported_sex_raw"] is None:
        quality.append("pri_2010_sex_label_unresolved")
    quality.append("source_reviewed_label_dictionary_applied")


def source_path(source):
    path = (ROOT / source["path"]).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError(f"Missing registered input: {source['id']}")
    if file_hash(path) != source["sha256"]:
        raise ValueError(f"Registered input hash changed: {source['id']}")
    return path


def copy_groups(path):
    receipt = json.loads((path.parent / "receipt.json").read_text())
    groups = defaultdict(list)
    for source in receipt["sources"]:
        if source["office"] in SHARED_HEADS:
            groups[source["source_sha256"]].append(source["source_path"])
    return {sha: sorted(paths) for sha, paths in groups.items()}


def main():
    from local_elections_up.office_ballia import BalliaHistoricalSource, BalliaSource

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--registry", type=Path, default=ROOT / "data/catalogs/office_sources.json"
    )
    parser.add_argument(
        "--output-root", type=Path, default=ROOT / "data/release/offices"
    )
    args = parser.parse_args()
    registry_bytes = args.registry.read_bytes()
    registry = json.loads(registry_bytes)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    output = args.output_root.parent / f".offices-{stamp}"
    output.mkdir(parents=True, exist_ok=False)
    manifest = {
        "status": "incomplete",
        "created_utc": datetime.now(UTC).isoformat(),
        "registry_sha256": hashlib.sha256(registry_bytes).hexdigest(),
        "label_schema_sha256": hashlib.sha256(LABELS_BYTES).hexdigest(),
        "parser_sha256": file_hash(Path(__file__)),
        "pri_2010_label_dictionary": {
            "path": PRI_LABEL_PATH.relative_to(ROOT).as_posix(),
            "sha256": PRI_LABEL_SHA,
        },
        "pyarrow_version": pa.__version__,
        "schema": {field.name: str(field.type) for field in SCHEMA},
        "sources": [],
        "files": [],
        "identical_head_source_copies": {},
        "pending_source_adapters": registry["pending_source_adapters"],
        "assignment_usable": False,
        "new_paid_api_cost_usd": 0,
    }
    dump(output / "INCOMPLETE.json", manifest)
    writers, buffers = {}, defaultdict(list)
    counts, years, flags_by_file = Counter(), defaultdict(Counter), defaultdict(Counter)

    def emit(key):
        records = buffers[key]
        if not records:
            return
        if key not in writers:
            filename = "up_" + "_".join(key) + ".parquet"
            writers[key] = pq.ParquetWriter(
                output / filename, SCHEMA, compression="zstd"
            )
        writers[key].write_table(pa.Table.from_pylist(records, schema=SCHEMA))
        records.clear()

    try:
        for source in registry["sources"]:
            path = source_path(source)
            parent_sha = file_hash(path)
            if source["adapter"] == "samiti_2005":
                if parent_sha != source["expected_sha256"]:
                    raise ValueError("Samiti 2005 input checksum changed")
                for evidence in source["review_evidence"]:
                    evidence_path = (ROOT / evidence["path"]).resolve()
                    if not evidence_path.is_relative_to(ROOT.resolve()):
                        raise ValueError("Samiti 2005 evidence escapes repository")
                    if file_hash(evidence_path) != evidence["sha256"]:
                        raise ValueError("Samiti 2005 review evidence checksum changed")
            ballia = None
            if source["adapter"] == "ballia":
                ballia = BalliaSource(ROOT, source, path, parent_sha)
            elif source["adapter"] == "ballia_historical":
                ballia = BalliaHistoricalSource(ROOT, source, path, parent_sha)
            provenance = SourceProvenance(ROOT, source, path)
            context = (
                samiti_context(ROOT, source, path, parent_sha)
                if source["adapter"] == "samiti_2010"
                else None
            )
            aliases = copy_groups(path) if source["adapter"] == "csv" else {}
            manifest["identical_head_source_copies"].update(aliases)
            tally = Counter()
            position = 0
            for batch in source_batches(path):
                for row in batch:
                    position += 1
                    if (
                        source["adapter"] == "ballia"
                        and row["row_kind"] != "seat_candidate"
                    ):
                        tally["excluded_non_seat_rows"] += 1
                        continue
                    if int(
                        source["election_year"]
                        if source["adapter"] == "ballia"
                        else pick(
                            row,
                            "election_year",
                            "year_context",
                            "year",
                            "subject_year",
                        )
                    ) in source.get("exclude_years", []):
                        tally["excluded_overlapping_year"] += 1
                        continue
                    if (
                        "portals" in source
                        and row.get("portal") not in source["portals"]
                    ):
                        tally["excluded_other_portal"] += 1
                        continue
                    if source["adapter"] == "csv" and row["office"] in SHARED_HEADS:
                        if row["source_path"] != aliases[row["source_sha256"]][0]:
                            tally["identical_statewide_copy_rows"] += 1
                            continue
                    record = (
                        ballia.normalize(row, position, SCHEMA.names)
                        if ballia is not None
                        else normalize(row, source, path, parent_sha, position, context)
                    )
                    provenance.apply(record)
                    key = (record["office"], record["record_kind"])
                    buffers[key].append(record)
                    counts[key] += 1
                    years[key][record["election_year"]] += 1
                    flags_by_file[key].update(record["quality_flags"])
                    tally["exported_rows"] += 1
                    if len(buffers[key]) >= 5000:
                        emit(key)
            if source["adapter"] == "samiti_2005" and (
                position != source["expected_rows"]
                or tally["exported_rows"] != source["expected_rows"]
            ):
                raise ValueError("Samiti 2005 observation count changed")
            if ballia is not None:
                ballia.check_counts(position, tally["exported_rows"])
            manifest["sources"].append(
                {
                    **source,
                    "resolved_path": path.relative_to(ROOT).as_posix(),
                    "sha256": parent_sha,
                    "input_rows": position,
                    "source_provenance": provenance.manifest(),
                    "source_adapter_evidence": (
                        ballia.manifest() if ballia is not None else None
                    ),
                    "source_adjudication": (
                        context["provenance"] if context is not None else None
                    ),
                    **tally,
                }
            )
        for key in buffers:
            emit(key)
    except Exception as exc:
        manifest["error"] = f"{type(exc).__name__}: {exc}"
        dump(output / "INCOMPLETE.json", manifest)
        raise
    finally:
        for writer in writers.values():
            writer.close()
    checksums = []
    for key in sorted(writers):
        filename = "up_" + "_".join(key) + ".parquet"
        sha = file_hash(output / filename)
        checksums.append(f"{sha}  {filename}")
        manifest["files"].append(
            {
                "path": filename,
                "sha256": sha,
                "office": key[0],
                "record_kind": key[1],
                "rows": counts[key],
                "rows_by_year": dict(years[key]),
                "quality_flags": dict(flags_by_file[key]),
            }
        )
    manifest["status"] = "standardized_source_observations_pending_validation"
    manifest["offices"] = sorted({key[0] for key in writers})
    dump(output / "manifest.json", manifest)
    (output / "CHECKSUMS.sha256").write_text("\n".join(checksums) + "\n")
    (output / "INCOMPLETE.json").unlink()
    backup = args.output_root.parent / f".offices-backup-{stamp}"
    if args.output_root.exists():
        os.replace(args.output_root, backup)
    try:
        os.replace(output, args.output_root)
    except BaseException:
        if backup.exists():
            os.replace(backup, args.output_root)
        raise
    if backup.exists():
        shutil.rmtree(backup)
    output = args.output_root
    print(
        json.dumps(
            {
                "output": str(output),
                "offices": manifest["offices"],
                "files": len(writers),
                "rows": sum(counts.values()),
                "rows_by_office": {
                    office: sum(n for (kind, _), n in counts.items() if kind == office)
                    for office in manifest["offices"]
                },
                "source_consolidation": [
                    {
                        key: item[key]
                        for key in (
                            "id",
                            "input_rows",
                            "exported_rows",
                            "identical_statewide_copy_rows",
                            "excluded_overlapping_year",
                        )
                        if key in item
                    }
                    for item in manifest["sources"]
                ],
                "pending_source_adapters": len(registry["pending_source_adapters"]),
                "assignment_usable": False,
                "new_paid_api_cost_usd": 0,
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
