#!/usr/bin/env python3
"""Apply a hash-scoped reservation codebook without promoting source assignments."""

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


def checksum(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def normalize(frame, codebook, code_column, codebook_sha256):
    required = {"source_sha256", "year", code_column}
    if not required.issubset(frame.columns):
        raise ValueError(
            f"Missing input columns: {sorted(required - set(frame.columns))}"
        )
    if not frame["source_sha256"].eq(codebook["source_sha256"]).fillna(False).all():
        raise ValueError("Input contains sources outside the codebook scope")
    if not frame["year"].isin(codebook["years"]).all():
        raise ValueError("Input contains years outside the codebook scope")
    codes = codebook["codes"]
    for raw, entry in codes.items():
        if not isinstance(raw, str):
            raise ValueError("Codebook keys must be exact strings")
        if entry["caste_reservation"] not in {None, "NONE", "BC", "SC", "ST"}:
            raise ValueError(f"Invalid caste code for {raw!r}")
        if (
            entry["woman_reserved"] is not None
            and type(entry["woman_reserved"]) is not bool
        ):
            raise ValueError(f"Invalid woman-reservation value for {raw!r}")
        if not isinstance(entry["review_status"], str) or not entry["review_status"]:
            raise ValueError(f"Missing review status for {raw!r}")
    raw = frame[code_column].fillna("")
    unknown = set(raw.unique()) - set(codes)
    if unknown:
        raise ValueError(f"Codes absent from the source codebook: {sorted(unknown)}")
    names = {
        "caste_reservation_candidate",
        "woman_reserved_candidate",
        "reservation_code_review_status",
        "reservation_codebook_id",
        "reservation_codebook_sha256",
        "reservation_assignment_usable",
    }
    if names.intersection(frame.columns):
        raise ValueError("Refusing to overwrite existing normalization columns")
    result = frame.copy()
    result["caste_reservation_candidate"] = raw.map(
        {k: v["caste_reservation"] for k, v in codes.items()}
    ).astype("string")
    result["woman_reserved_candidate"] = raw.map(
        {k: v["woman_reserved"] for k, v in codes.items()}
    ).astype("boolean")
    result["reservation_code_review_status"] = raw.map(
        {k: v["review_status"] for k, v in codes.items()}
    ).astype("string")
    conflicts = pd.Series(False, index=frame.index)
    conflict_column = codebook.get("conflict_column")
    if conflict_column in frame.columns:
        conflicts |= frame[conflict_column].eq(True).fillna(False)
    conflict_flag = codebook.get("conflict_flag")
    if conflict_flag and "quality_flags" in frame:
        conflicts |= (
            frame["quality_flags"]
            .fillna("")
            .map(lambda value: conflict_flag in value.split(";"))
        )
    result.loc[conflicts, "caste_reservation_candidate"] = pd.NA
    result.loc[conflicts, "woman_reserved_candidate"] = pd.NA
    result.loc[conflicts, "reservation_code_review_status"] = (
        "conflicting_source_assignments"
    )
    result["reservation_codebook_id"] = codebook["codebook_id"]
    result["reservation_codebook_sha256"] = codebook_sha256
    result["reservation_assignment_usable"] = False
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--codebook", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--code-column", default="reservation_raw")
    args = parser.parse_args()
    manifest_path = args.output.with_suffix(".manifest.json")
    if args.output.exists() or manifest_path.exists():
        raise FileExistsError(
            "Output or manifest already exists; use a new output version"
        )
    codebook = json.loads(args.codebook.read_text())
    codebook_hash = checksum(args.codebook)
    frame = pd.read_parquet(args.input)
    result = normalize(frame, codebook, args.code_column, codebook_hash)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as stream:
        result.to_parquet(stream, index=False, compression="zstd")
    manifest = {
        "input_path": str(args.input),
        "input_sha256": checksum(args.input),
        "output_name": args.output.name,
        "output_sha256": checksum(args.output),
        "codebook_path": str(args.codebook),
        "codebook_sha256": codebook_hash,
        "normalizer_sha256": checksum(Path(__file__)),
        "code_column": args.code_column,
        "rows": len(result),
        "normalized_candidate_cells": int(
            result["caste_reservation_candidate"].notna().sum()
        ),
        "review_status_counts": result["reservation_code_review_status"]
        .value_counts()
        .to_dict(),
        "rows_by_year": result.groupby("year").size().to_dict(),
        "source_columns_preserved": True,
        "rows_deduplicated": False,
        "identities_merged": False,
        "assignments_promoted": False,
        "additional_api_cost_usd": 0,
        "status": "Research candidates; identity and source-review flags retained",
    }
    with manifest_path.open("x") as stream:
        json.dump(manifest, stream, indent=2)
        stream.write("\n")
    print(json.dumps(manifest))


if __name__ == "__main__":
    main()
