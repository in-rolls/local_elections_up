"""Adapt pinned Ballia source cells without certifying reservation assignments."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import ClassVar

SOURCE_SHA = "685743d6d929e860720ae655909f4659f12f5c67b356946a62e072ee79de4b16"
SOURCE_URL = "https://navbharattimes.indiatimes.com/photo/81621873.cms"
HISTORICAL_SOURCE_SHA = (
    "4769b16fc47ad32009ecb24129a3c34f73bd809121a6de9c48eeebccbbb7a7cf"
)
HISTORICAL_SOURCE_URL = (
    "https://images1.livehindustan.com/uploadimage/static/document/2021/03/02/"
    "ballia_1614706707.pdf"
)
FAMILY_MEASURES = {
    5: "total_families",
    6: "scheduled_tribe_families",
    7: "scheduled_caste_families",
    8: "backward_caste_families",
    9: "general_category_families",
}


def packed(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, allow_nan=False)


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


class BalliaSource:
    def __init__(self, root, source, artifact, parent_sha):
        self.root = root.resolve()
        self.source = source
        self.artifact = artifact.resolve()
        self.base = self.inside(source["source_base"])
        self.year = source["election_year"]
        self.column = source["category_column"]
        if (
            parent_sha != source["expected_sha256"]
            or source["source_document_sha256"] != SOURCE_SHA
            or (self.year, self.column) not in {(2015, 10), (2021, 11)}
            or source["office"] != "panchayat_samiti_member"
            or source["record_kind"] != "seat_reservation"
            or not self.artifact.is_relative_to(self.base)
        ):
            raise ValueError("Ballia source pin or year-column contract changed")
        self.parent_sha = parent_sha
        receipt_path = self.artifact.with_name("reconciliation_receipt.json")
        self.receipt_sha = digest(receipt_path)
        if self.receipt_sha != source["reconciliation_receipt_sha256"]:
            raise ValueError("Ballia reconciliation receipt checksum changed")
        receipt = json.loads(receipt_path.read_bytes())
        if (
            receipt["output_sha256"] != parent_sha
            or receipt["source_sha256"] != SOURCE_SHA
            or receipt["output_rows"] != source["expected_input_rows"]
            or receipt["assignment_usable"] is not False
        ):
            raise ValueError("Ballia reconciliation receipt does not match input")
        self.receipt_path = receipt_path.relative_to(self.root).as_posix()
        self.document_path = self.inside(source["source_document_path"])
        if digest(self.document_path) != SOURCE_SHA:
            raise ValueError("Ballia original PDF checksum changed")
        self.evidence = []
        for item in source["review_evidence"]:
            path = self.inside(item["path"])
            if digest(path) != item["sha256"]:
                raise ValueError("Ballia review evidence checksum changed")
            self.evidence.append(item)
        self.seen = set()

    def inside(self, relative):
        path = (self.root / relative).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError("Ballia evidence path escapes the state repository")
        return path

    def normalize(self, row, position, schema_names):
        if (
            row["row_kind"] != "seat_candidate"
            or row["source_sha256"] != SOURCE_SHA
            or row["source_url"] != SOURCE_URL
            or row["assignment_usable"] is not False
        ):
            raise ValueError("Ballia row violates the source observation contract")
        manual = row["extraction_method"] == "visual_numeric_code_transcription"
        if manual:
            locator = {
                "source_page": row["source_page"],
                "source_data_row": row["source_data_row"],
            }
            row_field = "source_data_row"
        else:
            locator = {
                "source_page": row["source_page"],
                "table_index": row["table_index"],
                "geometry_row_index": row["geometry_row_index"],
            }
            row_field = "geometry_row_index"
        if any(type(value) is not int or value < 0 for value in locator.values()):
            raise ValueError("Ballia source locator is missing or invalid")
        if manual and locator["source_data_row"] < 1:
            raise ValueError("Manual Ballia row numbers must be positive")
        parent_id = hashlib.sha256(
            packed([SOURCE_SHA, locator]).encode("ascii")
        ).hexdigest()
        if parent_id in self.seen:
            raise ValueError("Duplicate Ballia source locator")
        self.seen.add(parent_id)
        observation_id = hashlib.sha256(
            packed([parent_id, self.column, self.year]).encode("ascii")
        ).hexdigest()
        cells = json.loads(row["source_reviewed_cells_json"])
        name_reviewed = "column_03_raw" in cells
        boundary_reviewed = "column_04_raw" in cells
        code = row[f"column_{self.column:02d}_value"]
        ward = row["column_02_value"]
        ward_number = (
            int(ward)
            if isinstance(ward, str) and re.fullmatch(r"[0-9]+", ward)
            else None
        )
        quality = [
            "independent_review_pending",
            "provisional_publication",
            "reservation_code_semantics_unmapped",
            "not_canonical_allocations",
            "raw_quality_flags_preserved_in_source_fields",
        ]
        unresolved = ["reservation_class", "women_reserved"]
        if not name_reviewed:
            quality.append("name_source_reading_unresolved")
            unresolved.append("ward_name")
        if not boundary_reviewed:
            quality.append("boundary_source_reading_unresolved")
            unresolved.append("boundary")
        if ward_number is None or ward_number < 1:
            quality.append("ward_number_unresolved")
            unresolved.append("ward_number")
            ward_number = None
        if row["effective_numeric_code_quality_flags"]:
            quality.append("source_numeric_code_issue_retained")
        if self.year == 2015:
            quality.append("retrospective_2015_not_independent_source")
        family_columns = {}
        for column in range(5, 10):
            raw = row[f"column_{column:02d}_raw"]
            value = row[f"column_{column:02d}_value"]
            number = (
                int(value)
                if isinstance(value, str) and re.fullmatch(r"[0-9]+", value)
                else None
            )
            family_columns[str(column)] = {
                "measure": FAMILY_MEASURES[column],
                "raw": raw,
                "value": value,
                "integer_candidate": number,
                "header_descending_order_note": column == 9,
            }
        evidence = {
            "reconciliation_receipt": {
                "path": self.receipt_path,
                "sha256": self.receipt_sha,
            },
            "source_row_locator": locator,
            "cell_reviews_json": row["source_reviewed_cells_json"],
            "review_evidence": self.evidence,
            "geometry_path": (
                None
                if manual
                else (
                    self.base
                    / "cell_extraction_v5_header_probe"
                    / f"page_{row['source_page']:04d}"
                    / "geometry.json.gz"
                )
                .relative_to(self.root)
                .as_posix()
            ),
        }
        out = dict.fromkeys(schema_names)
        out.update(
            record_id=observation_id,
            office=self.source["office"],
            record_kind=self.source["record_kind"],
            source_collection=self.source["id"],
            source_observation_id=observation_id,
            source_parent_observation_id=parent_id,
            source_artifact_path=self.artifact.relative_to(self.root).as_posix(),
            source_artifact_sha256=self.parent_sha,
            source_artifact_format="parquet",
            source_artifact_row=position,
            source_document_sha256=SOURCE_SHA,
            source_local_path=self.document_path.relative_to(self.root).as_posix(),
            source_response_path=None,
            source_url=SOURCE_URL,
            source_page=row["source_page"],
            source_row=row[row_field],
            source_row_field=row_field,
            source_category_column=self.column,
            source_printed_page_raw=(
                None if row["printed_page"] is None else str(row["printed_page"])
            ),
            election_year=self.year,
            district_name_raw=self.source["district_name"],
            block_name_raw=row["column_01_raw"],
            body_name_raw=row["column_01_raw"],
            ward_name_raw=row["column_03_raw"],
            ward_number_raw=row["column_02_raw"],
            ward_code_raw=row["column_02_raw"],
            ward_number=ward_number,
            source_boundary_raw=row["column_04_raw"],
            source_boundary_value=row["column_04_value"],
            source_block_name_value=row["column_01_value"],
            source_ward_name_value=row["column_03_value"],
            source_ward_number_value=ward,
            seat_reservation_raw=row[f"column_{self.column:02d}_raw"],
            source_reservation_value=code,
            reservation_class="unknown",
            women_reserved=None,
            is_winner=None,
            assignment_usable=False,
            source_subject_temporality=(
                "retrospective_2015_column_in_2021_publication"
                if self.year == 2015
                else "provisional_2021_reservation_column"
            ),
            source_finality_raw="provisional_publication",
            source_review_status_raw="source_cell_reconciled_independent_review_pending",
            name_review_status_raw=(
                "single_reviewer_source_reading"
                if name_reviewed
                else "unresolved_source_reading"
            ),
            source_boundary_review_status_raw=(
                "source_reviewed" if boundary_reviewed else "unresolved_source_reading"
            ),
            name_reading_uncertain=not name_reviewed,
            text_encoding="unicode_ocr_with_source_reviewed_values",
            source_fields_json=packed(row),
            source_family_counts_json=packed(family_columns),
            source_review_evidence_json=packed(evidence),
            source_unresolved_fields_json=packed(unresolved),
            quality_flags=quality,
        )
        return out

    def check_counts(self, position, exported):
        if (
            position != self.source["expected_input_rows"]
            or exported != self.source["expected_rows"]
            or len(self.seen) != exported
        ):
            raise ValueError("Ballia source or exported observation count changed")

    def manifest(self):
        return {
            "adapter_sha256": digest(Path(__file__)),
            "reconciliation_receipt_path": self.receipt_path,
            "reconciliation_receipt_sha256": self.receipt_sha,
            "source_year": 2021,
            "subject_year": self.year,
            "category_column": self.column,
            "code_mapping_applied": False,
            "raw_cells_and_review_provenance_preserved": True,
            "non_seat_rows_retained_in_parent_artifact": True,
        }


class BalliaHistoricalSource:
    """Adapt reviewed multi-year Ballia tables as provisional source observations."""

    CONTRACTS: ClassVar[dict[str, tuple[str, int]]] = {
        "samiti_head": ("panchayat_samiti_head", 102),
        "zp_member": ("zilla_parishad_member", 348),
        "gp_head": ("gram_panchayat_head", 5640),
    }

    def __init__(self, root, source, artifact, parent_sha):
        self.root = root.resolve()
        self.source = source
        self.artifact = artifact.resolve()
        self.kind = source["historical_table"]
        expected_office, expected_rows = self.CONTRACTS[self.kind]
        if (
            parent_sha != source["expected_sha256"]
            or source["source_document_sha256"] != HISTORICAL_SOURCE_SHA
            or source["office"] != expected_office
            or source["record_kind"] != "seat_reservation"
            or source["expected_rows"] != expected_rows
            or not self.artifact.is_relative_to(self.root)
        ):
            raise ValueError("Historical Ballia source contract changed")
        self.parent_sha = parent_sha
        self.document_path = self.inside(source["source_document_path"])
        if digest(self.document_path) != HISTORICAL_SOURCE_SHA:
            raise ValueError("Historical Ballia original PDF checksum changed")
        self.receipt_path = self.inside(source["receipt_path"])
        self.receipt_sha = digest(self.receipt_path)
        if self.receipt_sha != source["receipt_sha256"]:
            raise ValueError("Historical Ballia receipt checksum changed")
        self.expected_years = {
            int(year): count for year, count in source["expected_rows_by_year"].items()
        }
        if set(self.expected_years) != set(source["years"]):
            raise ValueError("Historical Ballia year contract changed")
        self.seen = set()
        self.years = {}

    def inside(self, relative):
        path = (self.root / relative).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError("Historical Ballia evidence path escapes repository")
        return path

    @staticmethod
    def row_flags(row):
        value = row.get("quality_flags")
        if value is None:
            return []
        if isinstance(value, list):
            return list(value)
        return [item for item in value.split(";") if item]

    def normalize(self, row, position, schema_names):
        source_id = row["observation_id"]
        year = int(row.get("subject_year", row.get("year")))
        if (
            row["source_sha256"] != HISTORICAL_SOURCE_SHA
            or row["assignment_usable"] is not False
            or not isinstance(source_id, str)
            or not source_id
            or year not in self.expected_years
            or source_id in self.seen
        ):
            raise ValueError("Historical Ballia row violates source contract")
        self.seen.add(source_id)
        self.years[year] = self.years.get(year, 0) + 1
        page = int(row.get("source_page", row.get("physical_page")))
        source_row = int(row["source_data_row"])
        if page < 1 or source_row < 1:
            raise ValueError("Historical Ballia source locator is invalid")

        code = row.get("reservation_code_value", row.get("reservation_code_literal"))
        raw_code = row.get(
            "reservation_code_raw", row.get("reservation_code_raw_literal", code)
        )
        block = row.get("source_block_name_candidate", row.get("block_name_literal"))
        body = row.get(
            "gp_name_literal",
            row.get("kshetra_panchayat_name_literal", block),
        )
        if self.kind == "samiti_head":
            name_unresolved = (
                row["source_block_name_review_status"]
                == "held_reader_disagreement_or_uncertainty"
            )
        elif self.kind == "zp_member":
            name_unresolved = row["source_name_unresolved"]
        else:
            name_unresolved = row["name_context_unresolved"]
        if name_unresolved:
            block = None if self.kind != "zp_member" else block
            body = None
        code_unresolved = bool(row.get("code_unresolved", code is None))
        unresolved = []
        quality = self.row_flags(row)
        quality.extend(
            [
                "provisional_publication",
                "reservation_codes_unmapped",
                "not_canonical_allocations",
            ]
        )
        if name_unresolved:
            unresolved.append("geographic_name")
            quality.append("name_source_reading_unresolved")
        if code_unresolved:
            unresolved.extend(["reservation_class", "women_reserved"])
            quality.append("reservation_code_source_reading_unresolved")
        else:
            unresolved.extend(["reservation_class", "women_reserved"])

        ward_raw = row.get("printed_ward_literal")
        ward_number = (
            int(ward_raw)
            if isinstance(ward_raw, str) and re.fullmatch(r"[0-9]+", ward_raw)
            else None
        )
        column = row.get("source_reservation_column", row.get("source_column"))
        if isinstance(column, str):
            match = re.fullmatch(r"column_([0-9]+)", column)
            column = int(match.group(1)) if match else None
        evidence = {
            "receipt_path": self.receipt_path.relative_to(self.root).as_posix(),
            "receipt_sha256": self.receipt_sha,
            "historical_table": self.kind,
        }
        out = dict.fromkeys(schema_names)
        out.update(
            record_id=hashlib.sha256(
                packed([self.source["id"], source_id]).encode("ascii")
            ).hexdigest(),
            office=self.source["office"],
            record_kind=self.source["record_kind"],
            source_collection=self.source["id"],
            source_observation_id=source_id,
            source_parent_observation_id=row.get(
                "source_parent_observation_id", row.get("source_row_id")
            ),
            source_artifact_path=self.artifact.relative_to(self.root).as_posix(),
            source_artifact_sha256=self.parent_sha,
            source_artifact_format="parquet",
            source_artifact_row=position,
            source_document_sha256=HISTORICAL_SOURCE_SHA,
            source_local_path=self.document_path.relative_to(self.root).as_posix(),
            source_url=row.get("source_url", HISTORICAL_SOURCE_URL),
            source_page=page,
            source_row=source_row,
            source_row_field="source_data_row",
            source_category_column=column,
            source_printed_serial_raw=row.get(
                "source_printed_serial_raw", row.get("source_serial_literal")
            ),
            election_year=year,
            district_name_raw=self.source["district_name"],
            block_name_raw=block,
            body_name_raw=body,
            body_code_raw=row.get("source_serial_literal"),
            ward_name_raw=body if self.kind == "zp_member" else None,
            ward_code_raw=ward_raw,
            ward_number=ward_number if self.kind == "zp_member" else None,
            seat_reservation_raw=raw_code,
            source_reservation_value=code,
            reservation_class="unknown",
            women_reserved=None,
            is_winner=None,
            assignment_usable=False,
            source_subject_temporality=row.get(
                "subject_temporality", row.get("year_status")
            ),
            source_finality_raw=row.get(
                "source_publication_status", "provisional_publication"
            ),
            source_review_status_raw=row.get(
                "review_status",
                row.get("code_decision_status", row.get("literal_status")),
            ),
            name_review_status_raw=(
                "unresolved_source_reading"
                if name_unresolved
                else "source_reading_retained"
            ),
            name_reading_uncertain=name_unresolved,
            text_encoding="unicode_ocr_with_source_reviewed_values",
            source_fields_json=packed(row),
            source_review_evidence_json=packed(evidence),
            source_unresolved_fields_json=packed(unresolved),
            source_block_name_value=block,
            source_ward_name_value=body if self.kind == "zp_member" else None,
            source_ward_number_value=ward_raw,
            quality_flags=list(dict.fromkeys(quality)),
        )
        return out

    def check_counts(self, position, exported):
        if (
            position != self.source["expected_rows"]
            or exported != self.source["expected_rows"]
            or len(self.seen) != exported
            or self.years != self.expected_years
        ):
            raise ValueError("Historical Ballia observation count changed")

    def manifest(self):
        return {
            "adapter_sha256": digest(Path(__file__)),
            "receipt_path": self.receipt_path.relative_to(self.root).as_posix(),
            "receipt_sha256": self.receipt_sha,
            "historical_table": self.kind,
            "years": sorted(self.expected_years),
            "literal_code_mapping_applied": False,
            "geographic_identity_mapping_applied": False,
            "unresolved_values_quarantined_in_row_flags": True,
        }
