# /// script
# requires-python = ">=3.11"
# dependencies = ["pyarrow"]
# ///
"""Compare pinned urban reservation and winner sources without merging assignments."""

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq


def norm(value):
    return " ".join(unicodedata.normalize("NFC", value or "").split())


def read_source(path, expected):
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected:
        raise ValueError(f"Source artifact changed: {path}")
    return pq.read_table(pa.BufferReader(raw)).to_pylist(), digest


def result_body_context(rows):
    groups = defaultdict(list)
    for row in rows:
        code = row.get("local_body_code_raw")
        if not isinstance(code, str) or not code.strip():
            continue
        key = (
            row["election_year"],
            norm(row["district_name_raw"]),
            norm(row["local_body_type_raw"]),
            code,
        )
        groups[key].append(row)
    context = {}
    for group in groups.values():
        heads = [r for r in group if r["tier"] == "ulb_head"]
        labels = {
            norm(r["local_body_name_raw"])
            for r in group
            if norm(r["local_body_name_raw"])
        }
        if len(heads) != 1 or len(labels) != 1:
            continue
        head = heads[0]
        body = norm(head["local_body_name_raw"])
        if not body or labels != {body}:
            continue
        for row in group:
            if row["tier"] == "ulb_ward" and not norm(row["local_body_name_raw"]):
                context[row["observation_id"]] = {
                    "body": body,
                    "head_id": head["observation_id"],
                    "head_source_sha256": head["source_sha256"],
                }
    return context


def source_key(row, kind, aliases, context):
    district = norm(row["district_name_raw"])
    district = aliases.get(district, district)
    body_type = norm(row["local_body_type_raw"])
    body = norm(row["local_body_name_raw"])
    if not body and kind == "results":
        body = context.get(row["observation_id"], {}).get("body", "")
    tier = row["tier"]
    if not all((district, body_type, body)) or tier not in ("ulb_head", "ulb_ward"):
        return None
    ward = None
    if tier == "ulb_ward":
        raw = str(row["ward_code"] if kind == "reservations" else row["ward_raw"])
        if not re.fullmatch(r"[0-9]+", raw.strip()) or int(raw) < 1:
            return None
        ward = int(raw)
    return district, body_type, body, tier, ward


def category(row, kind):
    caste = row[
        "reservation_category" if kind == "reservations" else "caste_reservation"
    ]
    woman = row["reserved_for_women" if kind == "reservations" else "woman_reserved"]
    if caste not in ("NONE", "BC", "SC", "ST") or type(woman) is not bool:
        return None
    return caste, woman


def compare(reservations, results, rules):
    aliases = {norm(k): norm(v) for k, v in rules["district_label_aliases"].items()}
    context = result_body_context(results)
    holds = {
        (norm(r["district"]), norm(r["body_type"]), norm(r["body"])): r["reason"]
        for r in rules.get("result_body_holds", [])
    }
    indexes = {"reservations": defaultdict(list), "results": defaultdict(list)}
    invalid = []
    for kind, rows in (("reservations", reservations), ("results", results)):
        ids = set()
        for row in rows:
            if row["election_year"] != rules["election_year"]:
                raise ValueError("Mixed election years in source comparison")
            if row["observation_id"] in ids:
                raise ValueError("Duplicate source observation identifier")
            ids.add(row["observation_id"])
            key = source_key(row, kind, aliases, context)
            if key is None:
                invalid.append(
                    {
                        "source": kind,
                        "observation_id": row["observation_id"],
                        "source_sha256": row["source_sha256"],
                        "reason": "missing_or_unparsed_source_key",
                    }
                )
            else:
                indexes[kind][key].append(row)
    keys = set(indexes["reservations"]) | set(indexes["results"])
    comparisons = []
    for key in sorted(keys, key=lambda k: (k[:4], k[4] or 0)):
        left, right = indexes["reservations"][key], indexes["results"][key]
        flags = []
        body_evidence = [
            context[r["observation_id"]]
            for r in right
            if r["observation_id"] in context
        ]
        if body_evidence:
            flags.append("blank_body_label_context_from_same_source_head")
        if len(left) > 1 or len(right) > 1:
            status = "ambiguous_source_key"
        elif left and right:
            a, b = category(left[0], "reservations"), category(right[0], "results")
            status = (
                "category_missing"
                if a is None or b is None
                else ("category_agreement" if a == b else "category_conflict")
            )
        else:
            status = "reservation_only" if left else "result_only"
        if right and key[:3] in holds:
            flags.append(holds[key[:3]])
        head_key = (*key[:3], "ulb_head", None)
        left_heads, right_heads = (
            indexes["reservations"].get(head_key, []),
            indexes["results"].get(head_key, []),
        )
        head_link = len(left_heads) == len(right_heads) == 1
        if head_link and right and key[3] == "ulb_ward":
            head_link = all(
                r["local_body_code_raw"] == right_heads[0]["local_body_code_raw"]
                for r in right
            )
        if not head_link:
            flags.append("unique_head_link_unestablished")
        ward_names_equal = None
        if key[3] == "ulb_ward" and len(left) == len(right) == 1:
            a, b = norm(left[0]["ward_name_raw"]), norm(right[0]["ward_name_raw"])
            ward_names_equal = bool(a and b and a == b)
            if not ward_names_equal:
                flags.append("ward_name_missing_or_different")
        if any(norm(r["district_name_raw"]) != key[0] for r in left + right):
            flags.append("reviewed_district_label_alias_used")
        comparisons.append(
            {
                "district_comparison_label": key[0],
                "local_body_type_raw": key[1],
                "body_comparison_label": key[2],
                "tier": key[3],
                "ward": key[4],
                "comparison_status": status,
                "reservation_observation_ids": [r["observation_id"] for r in left],
                "result_observation_ids": [r["observation_id"] for r in right],
                "reservation_source_sha256": [r["source_sha256"] for r in left],
                "result_source_sha256": [r["source_sha256"] for r in right],
                "result_body_names_raw": [r["local_body_name_raw"] for r in right],
                "result_body_context_head_ids": [r["head_id"] for r in body_evidence],
                "result_body_context_head_source_sha256": [
                    r["head_source_sha256"] for r in body_evidence
                ],
                "reservation_labels_raw": [r["reservation_raw"] for r in left],
                "result_seat_labels_raw": [r["seat_reservation_raw"] for r in right],
                "reservation_ward_names_raw": [r["ward_name_raw"] for r in left],
                "result_ward_names_raw": [r["ward_name_raw"] for r in right],
                "ward_names_exactly_equal": ward_names_equal,
                "unique_head_label_link": head_link,
                "reservation_head_ids": [r["observation_id"] for r in left_heads],
                "result_head_ids": [r["observation_id"] for r in right_heads],
                "reservation_head_codes_raw": [
                    r["local_body_code"] for r in left_heads
                ],
                "result_head_codes_raw": [
                    r["local_body_code_raw"] for r in right_heads
                ],
                "result_only_with_head_link": (
                    status == "result_only"
                    and key[3] == "ulb_ward"
                    and head_link
                    and key[:3] not in holds
                ),
                "quality_flags": ";".join(sorted(flags)),
                "assignment_usable": False,
            }
        )
    for kind, rows in (("reservations", reservations), ("results", results)):
        field = (
            "reservation_observation_ids"
            if kind == "reservations"
            else "result_observation_ids"
        )
        represented = sum(len(r[field]) for r in comparisons)
        represented += sum(r["source"] == kind for r in invalid)
        if represented != len(rows):
            raise ValueError("Comparison lost or duplicated source observations")
    return comparisons, invalid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reservations", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--rules", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rules_raw = args.rules.read_bytes()
    rules = json.loads(rules_raw)
    reservations, reservation_sha = read_source(
        args.reservations, rules["reservation_artifact_sha256"]
    )
    reservations = [r for r in reservations if r["portal"] == "ulb2012"]
    results, result_sha = read_source(args.results, rules["result_artifact_sha256"])
    if not reservations or not results:
        raise ValueError("Both source scopes must contain observations")
    if any(r["election_label_raw"] != "General Election May 2012" for r in results):
        raise ValueError("Winner source contains a different election cohort")
    comparisons, invalid = compare(reservations, results, rules)
    args.output.mkdir(parents=True, exist_ok=False)
    table = pa.Table.from_pylist(comparisons)
    index = table.schema.get_field_index("ward")
    table = table.set_column(index, "ward", table["ward"].cast(pa.int64()))
    artifact = args.output / "seat_source_comparisons.parquet"
    pq.write_table(table, artifact, compression="zstd")
    (args.output / "invalid_source_keys.json").write_text(
        json.dumps(invalid, ensure_ascii=False, indent=2) + "\n"
    )
    counts = Counter((r["tier"], r["comparison_status"]) for r in comparisons)
    dictionary = {
        "record_unit": (
            "One comparison key, not an accepted assignment. Ambiguous keys retain all"
            " source observation IDs without a Cartesian join."
        ),
        "key": (
            "NFC/whitespace-normalized district and body labels, printed body type,"
            " tier and positive numeric ward. Only explicit source-pinned district"
            " spelling aliases are used."
        ),
        "result_body_context_head_ids": (
            "For blank result body-name cells only: the unique named head within the"
            " same result election year, district, body type and literal body code"
            " supplies comparison context. All nonblank labels in that group must"
            " agree. Original blank cells remain unchanged."
        ),
        "result_body_names_raw": (
            "Original result body labels, including blanks; never overwritten by"
            " contextual labels."
        ),
        "unique_head_label_link": (
            "One head printing in each source has the same district/body/type label;"
            " result ward and result head codes also agree within their own source. No"
            " global or cross-year code equivalence is asserted."
        ),
        "result_only_with_head_link": (
            "Missing-row review candidate, not a recovered or accepted reservation"
            " assignment."
        ),
        "category_agreement": (
            "Typed printed seat-reservation labels agree; candidate category and sex"
            " are never used. Agreement is not independent validation."
        ),
        "ward_names_exactly_equal": (
            "NFC and whitespace comparison only; mismatches require review even when"
            " ward numbers and categories agree."
        ),
        "quality_flags": (
            "Explicit geographic, head-link and ward-name holds. All rows additionally"
            " remain unavailable for assignment pending independent source and"
            " geographic review."
        ),
        "provenance": (
            "Observation IDs and raw-response hashes point into the two SHA-pinned"
            " input artifacts in parse_receipt.json."
        ),
        "assignment_usable": (
            "Always false. This comparison does not publish assignments or resolve"
            " source conflicts."
        ),
    }
    (args.output / "dictionary.json").write_text(
        json.dumps(dictionary, indent=2) + "\n"
    )
    receipt = {
        "finished_utc": datetime.now(UTC).isoformat(),
        "inputs": [
            {
                "path": str(args.reservations.resolve()),
                "sha256": reservation_sha,
                "selected_rows": len(reservations),
            },
            {
                "path": str(args.results.resolve()),
                "sha256": result_sha,
                "selected_rows": len(results),
            },
        ],
        "rules_sha256": hashlib.sha256(rules_raw).hexdigest(),
        "output": str(args.output.resolve()),
        "comparison_rows": len(comparisons),
        "artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
        "counts_by_tier_and_status": [
            {"tier": k[0], "status": k[1], "rows": v} for k, v in sorted(counts.items())
        ],
        "invalid_source_keys": len(invalid),
        "result_rows_with_body_context": sum(
            len(r["result_body_context_head_ids"]) for r in comparisons
        ),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "result_only_wards_with_head_link": sum(
            r["result_only_with_head_link"] for r in comparisons
        ),
        "quality_flags": dict(
            Counter(f for r in comparisons for f in r["quality_flags"].split(";") if f)
        ),
        "assignment_usable": False,
        "new_paid_api_cost_usd": 0,
    }
    (args.output / "parse_receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n"
    )
    print(json.dumps(receipt), flush=True)


if __name__ == "__main__":
    main()
