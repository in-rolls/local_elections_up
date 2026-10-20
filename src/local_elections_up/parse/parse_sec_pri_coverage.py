#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["beautifulsoup4", "pyarrow"]
# ///
"""Reconcile UP 2015 reservation counts with pinned official district dashboards."""

import argparse
import collections
import datetime as dt
import gzip
import hashlib
import json
import unicodedata
from pathlib import Path
from urllib.parse import urljoin, urlparse

import pyarrow as pa
import pyarrow.parquet as pq
from bs4 import BeautifulSoup

TIERS = {"2": "zp_member", "4": "block_member", "5": "gp_head", "6": "gp_ward"}
METRICS = (
    "seat_total",
    "results_declared",
    "unopposed",
    "contested",
    "remaining_vacancies",
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def norm(text):
    return " ".join(unicodedata.normalize("NFC", text).split())


def label_key(text):
    return norm(text).replace("\u093c", "")


def source(root, digest):
    path = root / "raw" / (digest + ".html.gz")
    data = gzip.decompress(path.read_bytes())
    if sha(data) != digest:
        raise ValueError("Source hash mismatch: " + str(path))
    return BeautifulSoup(data, "html.parser")


def metric_headers(noun, suffix=""):
    return [
        noun,
        "\u092a\u0930\u093f\u0923\u093e\u092e \u0918\u094b\u0937\u093f\u0924" + suffix,
        "\u0928\u093f\u0930\u094d\u0935\u093f\u0930\u094b\u0927" + suffix,
        "\u0938\u0935\u093f\u0930\u094b\u0927" + suffix,
        "\u0905\u0935\u0936\u0947\u0937 \u0930\u093f\u0915\u094d\u0924 \u092a\u0926"
        + suffix,
        "",
    ]


def district_table(soup, family):
    candidates = []
    for table in soup.find_all("table"):
        rows = [
            [
                norm(c.get_text(" ", strip=True))
                for c in tr.find_all(["th", "td"], recursive=False)
            ]
            for tr in table.find_all("tr")
            if tr.find_parent("table") is table
        ]
        if rows and rows[0][:4] == [
            "\u0915\u094d\u0930\u092e\u093e\u0902\u0915",
            "\u091c\u093f\u0932\u093e \u0915\u094b\u0921",
            "\u091c\u093f\u0932\u093e",
            "\u092c\u094d\u0932\u0949\u0915 \u0915\u0940 \u0938\u0902\u0966",
        ]:
            candidates.append(rows)
    if len(candidates) != 1:
        raise ValueError("Expected exactly one published district table")
    rows = candidates[0]
    expected = [
        "\u0915\u094d\u0930\u092e\u093e\u0902\u0915",
        "\u091c\u093f\u0932\u093e \u0915\u094b\u0921",
        "\u091c\u093f\u0932\u093e",
        "\u092c\u094d\u0932\u0949\u0915 \u0915\u0940 \u0938\u0902\u0966",
    ]
    if family == "members":
        expected += metric_headers(
            "\u091c\u093f\u0932\u093e \u092a\u0902\u091a\u093e\u092f\u0924"
            " \u0935\u093e\u0930\u094d\u0921"
        ) + metric_headers(
            "\u0915\u094d\u0937\u0947\u0924\u094d\u0930"
            " \u092a\u0902\u091a\u093e\u092f\u0924 \u0935\u093e\u0930\u094d\u0921"
        )
    elif family == "gp":
        expected += metric_headers(
            "\u0917\u094d\u0930\u093e\u092e \u092a\u0902\u091a\u093e\u092f\u0924",
            " (\u092a\u094d\u0930\u0927\u093e\u0928)",
        ) + metric_headers(
            "\u0917\u094d\u0930\u093e\u092e \u092a\u0902\u091a\u093e\u092f\u0924"
            " \u0935\u093e\u0930\u094d\u0921",
            " (\u0938\u0926\u0938\u094d\u092f)",
        )
    else:
        raise ValueError("Unknown dashboard family")
    if rows[0] != expected or len(rows) != 76 or any(len(r) != 16 for r in rows):
        raise ValueError("Published district table schema or 75-district frame changed")
    if [int(r[0]) for r in rows[1:]] != list(range(1, 76)):
        raise ValueError("Noncontiguous published district rows")
    if len({r[1] for r in rows[1:]}) != 75:
        raise ValueError("Duplicate published district codes")
    return rows[1:]


def reconcile(root, reservations, output):
    rules_bytes = (root / "source_rules.json").read_bytes()
    rules = json.loads(rules_bytes)
    if rules["election_year"] != 2015:
        raise ValueError("Unexpected election year")
    if sha(reservations.read_bytes()) != rules["reservation_sha256"]:
        raise ValueError("Reservation snapshot differs from the reviewed input")
    index = source(root, rules["index_sha256"])
    title = (
        "\u092a\u0902\u091a\u093e\u092f\u0924"
        " \u0938\u093e\u092e\u093e\u0928\u094d\u092f"
        " \u0928\u093f\u0930\u094d\u0935\u093e\u091a\u0928 2015-16 \u0915\u0947"
        " \u091a\u0941\u0928\u093e\u0935 \u0915\u093e"
        " \u0905\u0935\u0932\u094b\u0915\u0928"
    )
    if title not in [norm(h.get_text(" ", strip=True)) for h in index.find_all("h4")]:
        raise ValueError("Explicit 2015-16 source-year heading is absent")
    linked = {
        urlparse(urljoin(rules["index_url"], a["href"])).path.casefold()
        for a in index.find_all("a", href=True)
    }
    aliases = {
        label_key(k): label_key(v)
        for k, v in rules["source_to_observed_label_aliases"].items()
    }
    observed = pq.read_table(
        reservations,
        columns=[
            "observation_id",
            "portal",
            "election_year",
            "post_code",
            "district_filter_name_raw",
            "district_name_raw",
            "district_filter_code",
            "block_filter_code",
            "gp_code",
            "ward_code",
        ],
    ).to_pylist()
    if {r["election_year"] for r in observed} != {2015} or {
        r["portal"] for r in observed
    } != {"pri2015"}:
        raise ValueError("Reservation snapshot contains a different source or year")
    if len({r["observation_id"] for r in observed}) != len(observed):
        raise ValueError("Duplicate source-observation identities")
    counts = collections.Counter()
    keys = collections.defaultdict(set)
    observed_labels = collections.defaultdict(set)
    missing_keys = collections.Counter()
    for row in observed:
        post = row["post_code"]
        if post not in TIERS:
            continue
        raw_label = row["district_filter_name_raw"] or row["district_name_raw"] or ""
        label = label_key(raw_label)
        group = (post, label)
        counts[group] += 1
        observed_labels[label].add(raw_label)
        seat = row["gp_code"] if post == "5" else row["ward_code"]
        if seat is None:
            missing_keys[group] += 1
        keys[group].add((row["district_filter_code"], row["block_filter_code"], seat))
    records = []
    source_labels = set()
    for specification in rules["sources"]:
        if urlparse(specification["url"]).path.casefold() not in linked:
            raise ValueError("Dashboard not linked from the pinned 2015-16 index")
        family = specification["family"]
        pairs = [("2", 4), ("4", 10)] if family == "members" else [("5", 4), ("6", 10)]
        rows = district_table(source(root, specification["sha256"]), family)
        mapped_labels = [aliases.get(label_key(r[2]), label_key(r[2])) for r in rows]
        if len(set(mapped_labels)) != 75:
            raise ValueError("Ambiguous district comparison labels")
        source_labels.update(mapped_labels)
        for raw, label in zip(rows, mapped_labels, strict=False):
            for post, offset in pairs:
                values = [
                    int(x.replace(",", "")) if x else None
                    for x in raw[offset : offset + 5]
                ]
                if values[0] is None:
                    raise ValueError("Published seat total missing")
                group = (post, label)
                total_residual = (
                    values[0] - values[1] - values[4]
                    if all(values[i] is not None for i in (0, 1, 4))
                    else None
                )
                result_residual = (
                    values[1] - values[2] - values[3]
                    if all(values[i] is not None for i in (1, 2, 3))
                    else None
                )
                row = {
                    "election_year": 2015,
                    "election_cycle_raw": rules["election_cycle_raw"],
                    "tier": TIERS[post],
                    "post_code": post,
                    "district_code_raw": raw[1],
                    "district_name_raw": raw[2],
                    "comparison_label": label,
                    "observed_district_labels_raw": sorted(observed_labels[label]),
                    "label_alias_applied": label_key(raw[2]) in aliases,
                    "published_blocks": int(raw[3]),
                    "observed_rows": counts[group],
                    "observed_unique_scoped_keys": len(keys[group]),
                    "observed_missing_seat_codes": missing_keys[group],
                    "count_difference": counts[group] - values[0],
                    "comparison_status": (
                        "not_acquired"
                        if not counts[group]
                        else (
                            "count_match"
                            if counts[group] == values[0]
                            else "count_mismatch"
                        )
                    ),
                    "published_total_residual": total_residual,
                    "published_declared_result_residual": result_residual,
                    "source_url": specification["url"],
                    "source_sha256": specification["sha256"],
                    "source_table_row": int(raw[0]),
                    "year_index_sha256": rules["index_sha256"],
                    "reservation_snapshot_sha256": rules["reservation_sha256"],
                    "assignment_usable": False,
                }
                row.update(
                    {
                        "published_" + key: value
                        for key, value in zip(METRICS, values, strict=False)
                    }
                )
                records.append(row)
    if set(observed_labels) - source_labels:
        raise ValueError("Unmatched observed district labels")
    output.mkdir(parents=True, exist_ok=False)
    artifact = output / "district_coverage.parquet"
    pq.write_table(pa.Table.from_pylist(records), artifact, compression="zstd")
    summary = []
    for tier in TIERS.values():
        subset = [r for r in records if r["tier"] == tier]
        summary.append(
            {
                "tier": tier,
                "published_total": sum(r["published_seat_total"] for r in subset),
                "observed_rows": sum(r["observed_rows"] for r in subset),
                "district_count_matches": sum(
                    r["comparison_status"] == "count_match" for r in subset
                ),
                "district_count_mismatches": sum(
                    r["comparison_status"] == "count_mismatch" for r in subset
                ),
                "districts_not_acquired": sum(
                    r["comparison_status"] == "not_acquired" for r in subset
                ),
            }
        )
    receipt = {
        "created_utc": dt.datetime.now(dt.UTC).isoformat(),
        "district_tier_rows": len(records),
        "summary": summary,
        "artifact_sha256": sha(artifact.read_bytes()),
        "rules_sha256": sha(rules_bytes),
        "script_sha256": sha(Path(__file__).read_bytes()),
        "reservation_snapshot_sha256": rules["reservation_sha256"],
        "source_arithmetic_discrepancies": sum(
            r["published_total_residual"] not in (None, 0)
            or r["published_declared_result_residual"] not in (None, 0)
            for r in records
        ),
        "count_mismatches": [
            {
                k: r[k]
                for k in (
                    "tier",
                    "district_name_raw",
                    "published_seat_total",
                    "observed_rows",
                    "count_difference",
                )
            }
            for r in records
            if r["comparison_status"] == "count_mismatch"
        ],
        "scope": (
            "Count reconciliation only. Matching counts do not validate identities,"
            " category accuracy, administrative codes or election legality."
        ),
        "assignment_usable": False,
    }
    (output / "parse_receipt.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
    )
    (output / "dictionary.json").write_text(
        json.dumps(
            {
                "published_seat_total": (
                    "Dashboard seat universe, not declared winners."
                ),
                "published_results_declared": (
                    "Dashboard declared results; not used as the reservation-coverage"
                    " denominator."
                ),
                "published_total_residual": (
                    "Seat total minus declared results minus remaining vacancies."
                    " Nonzero source arithmetic is retained, not repaired."
                ),
                "published_declared_result_residual": (
                    "Declared results minus unopposed and contested results."
                ),
                "count_difference": (
                    "Acquired reservation observations minus published seats."
                ),
                "comparison_label": rules["label_normalization"],
                "district_code_raw": (
                    "Dashboard code, not assumed equal to reservation-portal filter"
                    " codes."
                ),
                "observed_unique_scoped_keys": (
                    "Distinct source district/block/seat tuples, not independently"
                    " validated administrative identities."
                ),
                "source_table_row": (
                    "One-based district data-row ordinal in the pinned dashboard."
                ),
                "assignment_usable": (
                    "Always false; this is a coverage diagnostic, not a canonical seat"
                    " dataset."
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )
    print(json.dumps({"output": str(output), **receipt}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--reservations", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    reconcile(args.source_root, args.reservations, args.output)


if __name__ == "__main__":
    main()
