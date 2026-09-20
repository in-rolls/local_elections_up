#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyarrow"]
# ///
"""Assemble UP's 2017 urban heads and district-partitioned ward results."""

import argparse
import collections
import datetime as dt
import hashlib
import json
import unicodedata
from pathlib import Path, PurePosixPath

import pyarrow as pa
import pyarrow.parquet as pq

REPO = Path(__file__).resolve().parents[2]
HEAD_POSTS = {"7", "9", "11"}
WARD_POSTS = {"8", "10", "12"}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def repo_path(path):
    return path.resolve().relative_to(REPO).as_posix()


def source_table(path):
    raw = path.read_bytes()
    receipt_path = path.with_name("parse_receipt.json")
    receipt_raw = receipt_path.read_bytes()
    receipt = json.loads(receipt_raw)
    if receipt["artifact_sha256"] != sha256(raw):
        raise ValueError("Input artifact differs from its parser receipt")
    rows = pq.read_table(pa.BufferReader(raw)).to_pylist()
    if receipt.get("rows", receipt.get("phase_rows")) != len(rows):
        raise ValueError("Input row count differs from its parser receipt")
    return (
        rows,
        receipt,
        {
            "path": repo_path(path),
            "sha256": sha256(raw),
            "receipt_path": repo_path(receipt_path),
            "receipt_sha256": sha256(receipt_raw),
        },
    )


def comparison_key(row):
    def normalize(value):
        return " ".join(
            unicodedata.normalize("NFC", value).replace("\u093c", "").split()
        )

    return tuple(
        normalize(row[field])
        for field in ("district_name_raw", "local_body_type_raw", "local_body_name_raw")
    )


def assemble(args):
    head_source, _head_receipt, head_input = source_table(args.heads)
    wards, ward_receipt, ward_input = source_table(args.wards)
    phases, _schedule_receipt, schedule_input = source_table(args.schedule)
    heads = [row for row in head_source if row["post_code_raw"] in HEAD_POSTS]
    excluded = [row for row in head_source if row["post_code_raw"] not in HEAD_POSTS]
    if (
        not heads
        or not wards
        or any(row["post_code_raw"] not in WARD_POSTS for row in wards + excluded)
    ):
        raise ValueError("Unexpected head/ward input partition")
    if {row["post_code_raw"] for row in heads} != HEAD_POSTS:
        raise ValueError("A head post type is absent")
    if {row["post_code_raw"] for row in wards} != WARD_POSTS:
        raise ValueError("A ward post type is absent")
    if (
        not ward_receipt["all_planned_queries_complete"]
        or ward_receipt["planned_queries"] != 225
        or ward_receipt["completed_queries"] != 225
        or ward_receipt["queries_at_source_cap"]
    ):
        raise ValueError("District ward acquisition is incomplete or possibly capped")
    if len(phases) != 3 or {row["phase"] for row in phases} != {1, 2, 3}:
        raise ValueError("Expected three official schedule phases")
    if any(row["election_year"] != 2017 for row in heads + wards + phases):
        raise ValueError("Mixed election years")
    records = []
    for role, rows, source_root, artifact in (
        ("statewide_heads", heads, args.head_root, args.heads),
        ("district_wards", wards, args.ward_root, args.wards),
    ):
        for source in rows:
            if source["assignment_usable"] or not source["source_query_complete"]:
                raise ValueError("Unexpected assignment or query-completion status")
            path = PurePosixPath(source["source_response_path"])
            if (
                path.is_absolute()
                or ".." in path.parts
                or str(path) != f"raw/{source['source_sha256']}.html.gz"
            ):
                raise ValueError("Unexpected source-response path")
            records.append(
                {
                    **source,
                    "source_partition": role,
                    "source_acquisition_root": repo_path(source_root),
                    "source_response_repo_path": repo_path(source_root / str(path)),
                    "source_parsed_artifact": repo_path(artifact),
                }
            )
    if len({row["observation_id"] for row in records}) != len(records):
        raise ValueError("Duplicate source observation")
    grouped = collections.defaultdict(list)
    for row in records:
        grouped[comparison_key(row)].append(row)
    coverage = []
    for key, body_rows in sorted(grouped.items()):
        head_rows = [row for row in body_rows if row["tier"] == "ulb_head"]
        ward_rows = [row for row in body_rows if row["tier"] == "ulb_ward"]
        if len(head_rows) + len(ward_rows) != len(body_rows):
            raise ValueError("Unexpected urban tier")
        numbers = [row["ward"] for row in ward_rows]
        if any(
            type(number) is not int or not 1 <= number <= 10000 for number in numbers
        ):
            raise ValueError("Unresolved ward number")
        gaps = sorted(set(range(1, max(numbers, default=0) + 1)) - set(numbers))
        duplicates = len(numbers) - len(set(numbers))
        body_match = len(head_rows) == 1 and bool(ward_rows)
        for row in body_rows:
            flags = set(filter(None, row["quality_flags"].split(";")))
            if not body_match:
                flags.add("head_ward_body_context_requires_review")
            if gaps or duplicates:
                flags.add("observed_ward_sequence_requires_review")
            row["quality_flags"] = ";".join(sorted(flags))
        coverage.append(
            {
                "district_comparison_key": key[0],
                "body_type_comparison_key": key[1],
                "body_name_comparison_key": key[2],
                "head_observations": len(head_rows),
                "ward_observations": len(ward_rows),
                "one_head_with_observed_wards": body_match,
                "ward_min": min(numbers, default=None),
                "ward_max": max(numbers, default=None),
                "missing_observed_ward_numbers": gaps,
                "duplicate_ward_numbers": duplicates,
                "assignment_usable": False,
            }
        )
    expected_heads = sum(row["scheduled_bodies"] for row in phases)
    expected_wards = sum(row["scheduled_wards"] for row in phases)
    repo_path(args.output)
    args.output.mkdir(parents=True, exist_ok=False)
    artifact = args.output / "winner_reservations.parquet"
    fields = list(dict.fromkeys(field for row in records for field in row))
    pq.write_table(
        pa.Table.from_pylist(
            [{field: row.get(field) for field in fields} for row in records]
        ),
        artifact,
        compression="zstd",
    )
    coverage_artifact = args.output / "coverage_by_body.parquet"
    pq.write_table(
        pa.Table.from_pylist(coverage), coverage_artifact, compression="zstd"
    )
    receipt = {
        "combined_utc": dt.datetime.now(dt.UTC).isoformat(),
        "election_year": 2017,
        "rows": len(records),
        "head_rows": len(heads),
        "ward_rows": len(wards),
        "excluded_statewide_ward_rows": len(excluded),
        "rows_by_post": dict(
            collections.Counter(row["post_code_raw"] for row in records)
        ),
        "scheduled_bodies": expected_heads,
        "scheduled_wards": expected_wards,
        "scheduled_head_count_matches": len(heads) == expected_heads,
        "scheduled_ward_count_matches": len(wards) == expected_wards,
        "source_body_comparison_keys": len(coverage),
        "bodies_with_one_head_and_wards": sum(
            row["one_head_with_observed_wards"] for row in coverage
        ),
        "bodies_with_ward_sequence_issues": sum(
            bool(row["missing_observed_ward_numbers"] or row["duplicate_ward_numbers"])
            for row in coverage
        ),
        "quality_flags": dict(
            collections.Counter(
                flag for row in records for flag in row["quality_flags"].split(";")
            )
        ),
        "inputs": {
            "heads": head_input,
            "wards": ward_input,
            "schedule": schedule_input,
        },
        "artifact_sha256": sha256(artifact.read_bytes()),
        "coverage_sha256": sha256(coverage_artifact.read_bytes()),
        "script_sha256": sha256(Path(__file__).read_bytes()),
        "assignment_usable": False,
        "scope": (
            "Source-count and within-source body/ward reconciliation only. Matching"
            " totals and contiguous wards do not certify categories, administrative"
            " identity, election authority or independent accuracy."
        ),
    }
    (args.output / "combine_receipt.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
    )
    (args.output / "dictionary.json").write_text(
        json.dumps(
            {
                "input_dictionaries": [
                    repo_path(path.with_name("dictionary.json"))
                    for path in (args.heads, args.wards)
                ],
                "source_partition": (
                    "Statewide head queries or district-partitioned ward queries;"
                    " capped statewide ward rows are excluded."
                ),
                "source_acquisition_root": (
                    "Repository-relative root for the original source_response_path."
                ),
                "source_response_repo_path": (
                    "Repository-relative original gzip HTTP response, without copying"
                    " source bytes."
                ),
                "source_parsed_artifact": (
                    "Repository-relative parser output from which this observation was"
                    " selected."
                ),
                "comparison_keys": (
                    "NFC, collapsed whitespace and removed nukta for comparison only;"
                    " raw source labels remain unchanged. These are not administrative"
                    " codes."
                ),
                "ward_sequence": (
                    "Gaps and repeated integers among observed wards within a source"
                    " body key; not a published body-level ward universe."
                ),
                "assignment_usable": (
                    "Always false pending independent review and administrative"
                    " reconciliation."
                ),
            },
            indent=2,
        )
        + "\n"
    )
    print(
        json.dumps({"output": str(args.output), **receipt}, ensure_ascii=False),
        flush=True,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("heads", "wards", "schedule", "head-root", "ward-root", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    assemble(parser.parse_args())


if __name__ == "__main__":
    main()
