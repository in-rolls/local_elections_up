"""Source-specific normalization for the held UP 2010 samiti-member lists."""

import hashlib
import json

import pyarrow as pa

STRINGS = [
    "district_code_raw",
    "block_code_raw",
    "ward_number_raw",
    "education_encoded_raw",
    "candidate_category_class",
    "source_member_cell_encoded_raw",
    "source_notice_encoded_raw",
    "source_notice_kind",
    "source_adjudication_path",
    "source_adjudication_sha256",
]
FIELDS = [
    ("candidate_age", pa.int64()),
    ("candidate_category_women_label", pa.bool_()),
    ("block_context_source_page", pa.int64()),
    ("block_context_source_y", pa.float64()),
]
COPY_FIELDS = [
    "district_code_raw",
    "block_code_raw",
    "district_name_encoded_raw",
    "block_name_encoded_raw",
    "ward_number_raw",
    "candidate_name_encoded_raw",
    "related_person_encoded_raw",
    "seat_reservation_encoded_raw",
    "candidate_category_encoded_raw",
    "candidate_category_class",
    "candidate_category_women_label",
    "candidate_age_raw",
    "candidate_age",
    "reported_sex_encoded_raw",
    "education_encoded_raw",
    "block_context_source_page",
    "block_context_source_y",
    "text_encoding",
]


def compact(value):
    return "".join((value or "").split())


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load_context(root, source, path, parent_sha):
    review_path = root / source["dispositions_path"]
    review_bytes = review_path.read_bytes()
    review = json.loads(review_bytes)
    receipt_path = path.parent / "receipt.json"
    receipt_bytes = receipt_path.read_bytes()
    receipt = json.loads(receipt_bytes)
    if review["input_sha256"] != parent_sha:
        raise ValueError("Samiti dispositions refer to a different extraction")
    if hashlib.sha256(receipt_bytes).hexdigest() != review["receipt_sha256"]:
        raise ValueError("Samiti extraction receipt checksum mismatch")
    if (
        receipt["parquet_sha256"] != parent_sha
        or receipt["source_failures"]
        or receipt["status"] != "parsed_pending_validation"
    ):
        raise ValueError("Samiti extraction is incomplete or mismatched")
    evidence = {item["id"]: item for item in review["evidence"]}
    checked = {}
    for item in evidence.values():
        for path_key, sha_key in (
            ("source_path", "source_sha256"),
            ("image_path", "image_sha256"),
        ):
            relative = item[path_key]
            if relative not in checked:
                checked[relative] = digest(root / relative)
            if checked[relative] != item[sha_key]:
                raise ValueError(f"Samiti review evidence changed: {relative}")
    status_labels = {}
    for item in review["status_labels"]:
        key = compact(item["encoded_raw"])
        if not key or key in status_labels or item["evidence_id"] not in evidence:
            raise ValueError("Invalid or repeated samiti status label")
        status_labels[key] = item
    return {
        "status_labels": status_labels,
        "evidence": list(evidence.values()),
        "collision_keys": {
            (item["district_code_raw"], item["block_code_raw"], item["ward_number"])
            for item in receipt["key_collisions"]
        },
        "row_holds": {
            (
                item["source_sha256"],
                item["source_page"],
                item["source_row_on_page"],
            ): item["flag"]
            for item in review["row_holds"]
        },
        "provenance": {
            "path": source["dispositions_path"],
            "sha256": hashlib.sha256(review_bytes).hexdigest(),
            "status": review["status"],
            "receipt_path": receipt_path.relative_to(root).as_posix(),
            "receipt_sha256": review["receipt_sha256"],
            "input_sha256": parent_sha,
        },
    }


def normalize(row, out, quality, context):
    for field in COPY_FIELDS:
        out[field] = row[field]
    out["source_printed_serial_raw"] = row["printed_serial_raw"]
    out["source_member_cell_encoded_raw"] = row["candidate_name_encoded_raw"]
    out["source_adjudication_path"] = context["provenance"]["path"]
    out["source_adjudication_sha256"] = context["provenance"]["sha256"]
    ward = row["ward_number"]
    out["ward_number"] = ward if ward is not None and ward > 0 else None
    if ward is None or ward <= 0:
        quality.append("ward_number_unresolved")
        if ward is not None:
            quality.append("source_ward_number_nonpositive")
    key = (row["district_code_raw"], row["block_code_raw"], ward)
    if key in context["collision_keys"]:
        quality.append("source_seat_key_collision")
    if row["candidate_age"] is not None and row["candidate_age"] <= 0:
        out["candidate_age"] = None
        quality.append("source_candidate_age_nonpositive")
    row_key = (row["source_sha256"], row["source_page"], row["source_row_on_page"])
    if row_key in context["row_holds"]:
        quality.append(context["row_holds"][row_key])
    for evidence in context["evidence"]:
        if (
            evidence["source_sha256"] == row["source_sha256"]
            and evidence["source_page"] == row["source_page"]
        ):
            out["source_image_path"] = evidence["image_path"]
            out["source_image_sha256"] = evidence["image_sha256"]
    notice = context["status_labels"].get(compact(row["candidate_name_encoded_raw"]))
    if notice:
        out["record_kind"] = "source_status_notice"
        out["source_notice_kind"] = notice["notice_kind"]
        out["source_notice_encoded_raw"] = row["candidate_name_encoded_raw"]
        for field in (
            "candidate_name_raw",
            "candidate_name_encoded_raw",
            "related_person_raw",
            "reported_sex_raw",
            "candidate_age",
            "candidate_category_raw",
            "candidate_category_class",
            "candidate_category_women_label",
            "education_raw",
        ):
            out[field] = None
        quality.extend(
            [
                "non_person_source_row",
                "source_status_label_pending_independent_review",
            ]
        )
    out["is_winner"] = None
    out["assignment_usable"] = False
