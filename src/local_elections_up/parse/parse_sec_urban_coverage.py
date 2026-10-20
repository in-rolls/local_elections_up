# /// script
# requires-python = ">=3.11"
# dependencies = ["beautifulsoup4", "pyarrow"]
# ///
"""Parse source-pinned SEC urban district aggregates with reviewed font labels."""

import argparse
import gzip
import hashlib
import json
import re
import subprocess
import unicodedata
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urljoin

import pyarrow as pa
import pyarrow.parquet as pq
from bs4 import BeautifulSoup, NavigableString, Tag

METRICS = (
    "local_bodies",
    "wards",
    "elected_unreserved",
    "elected_women",
    "elected_bc",
    "elected_bc_women",
    "elected_sc",
    "elected_sc_women",
    "elected_st",
    "elected_st_women",
    "elected_non_women_total",
    "elected_women_total",
    "elected_total",
)
ROW = re.compile(r"^(.*?)\s{2,}([0-9]+(?:\s+[0-9]+){12})\s*$")
YEAR = re.compile(r"Local\s+Bodies\s+General\s+Election\s*-\s*(\d{4})", re.I)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def read_pinned(root, relative, expected):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Source path escapes the source root")
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    if sha256(raw) != expected:
        raise ValueError(f"Source changed: {relative}")
    return raw


def source_year(index, index_url, pdf_url):
    soup = BeautifulSoup(index, "html.parser")
    events = []
    for node in soup.descendants:
        if isinstance(node, Tag) and node.name == "a" and node.get("href"):
            events.append(f" SOURCE_LINK:{urljoin(index_url, node['href'])} ")
        elif isinstance(node, NavigableString):
            events.append(" ".join(str(node).split()))
    stream = " ".join(events)
    marker = f"SOURCE_LINK:{pdf_url} "
    if stream.count(marker) != 1:
        raise ValueError("Expected one PDF link in the official index")
    years = YEAR.findall(stream.split(marker)[0])
    if not years:
        raise ValueError("PDF has no preceding election-year section")
    return int(years[-1])


def arithmetic_issues(record):
    issues = []
    if sum(record[k] for k in METRICS[2:10]) != record["wards"]:
        issues.append("category_sum_differs_from_wards")
    if sum(record[k] for k in METRICS[2:10:2]) != record["elected_non_women_total"]:
        issues.append("non_women_total_disagrees")
    if sum(record[k] for k in METRICS[3:10:2]) != record["elected_women_total"]:
        issues.append("women_total_disagrees")
    if (
        record["elected_non_women_total"] + record["elected_women_total"]
        != record["elected_total"]
    ):
        issues.append("subtotals_disagree")
    if record["wards"] != record["elected_total"]:
        issues.append("ward_and_seat_totals_disagree")
    return issues


def normalize_label(value):
    return " ".join(unicodedata.normalize("NFC", value or "").split())


def compare_winners(records, path, review):
    raw = path.read_bytes()
    winners = pq.read_table(pa.BufferReader(raw)).to_pylist()
    years = {r["election_year"] for r in records}
    if not winners or {r["election_year"] for r in winners} != years:
        raise ValueError("Winner and aggregate election years differ")
    labels = [
        "अनारक्षित",
        "महिला",
        "पिछडा वर्ग",
        "पिछडा वर्ग - महिला",
        "अनुसूचित जाति",
        "अनुसूचित जाति - महिला",
        "अनुसूचित जनजाति",
        "अनुसूचित जनजाति - महिला",
    ]
    category_map = {normalize_label(label): i for i, label in enumerate(labels)}
    seat_labels = [
        "अनारक्षित",
        "महिला",
        "अन्य पिछड़ा वर्ग",
        "अन्य पिछड़ा वर्ग महिला",
        "अनुसूचित जाति",
        "अनुसूचित जाति महिला",
        "अनुसूचित जनजाति",
        "अनुसूचित जनजाति महिला",
    ]
    seat_map = {normalize_label(label): i for i, label in enumerate(seat_labels)}
    body_types = {
        "नगर पालिका परिषद": "nagar_palika_parishad",
        "नगर पंचायत": "nagar_panchayat",
    }
    aliases = {
        normalize_label(k): normalize_label(v)
        for k, v in review.get("winner_district_label_aliases", {}).items()
    }
    strategies = (
        "candidate_label",
        "candidate_caste_and_reported_sex",
        "candidate_caste_and_either_woman_indicator",
        "seat_reservation",
    )
    groups = defaultdict(
        lambda: {"rows": 0, "source_labels": set(), **{s: [0] * 8 for s in strategies}}
    )
    missing_categories, sex_conflicts, unknown_sexes, unknown_seat_categories = (
        [],
        [],
        [],
        [],
    )
    provenance = (
        "district_name_raw",
        "local_body_type_raw",
        "local_body_name_raw",
        "ward_raw",
        "candidate_category_raw",
        "gender_raw",
        "seat_reservation_raw",
        "source_sha256",
        "source_page",
        "source_row_on_page",
        "observation_id",
    )
    for winner in winners:
        body_type = body_types.get(winner["local_body_type_raw"])
        if winner["tier"] != "ulb_ward" or body_type is None:
            continue
        district = normalize_label(winner["district_name_raw"])
        group = groups[(body_type, aliases.get(district, district))]
        group["source_labels"].add(district)
        if len(group["source_labels"]) != 1:
            raise ValueError(
                "District spelling aliases collapse distinct result labels"
            )
        group["rows"] += 1
        evidence = {key: winner.get(key) for key in provenance}
        seat = seat_map.get(normalize_label(winner["seat_reservation_raw"]))
        if seat is None:
            unknown_seat_categories.append(evidence)
        else:
            group["seat_reservation"][seat] += 1
        category = category_map.get(normalize_label(winner["candidate_category_raw"]))
        sex = normalize_label(winner["gender_raw"])
        if sex not in ("पुरुष", "महिला"):
            unknown_sexes.append(evidence)
        if category is None:
            missing_categories.append(evidence)
            continue
        group["candidate_label"][category] += 1
        caste_offset = category // 2 * 2
        if sex in ("पुरुष", "महिला"):
            group["candidate_caste_and_reported_sex"][
                caste_offset + int(sex == "महिला")
            ] += 1
        if category % 2 or sex in ("पुरुष", "महिला"):
            woman_indicator = bool(category % 2) or sex == "महिला"
            group["candidate_caste_and_either_woman_indicator"][
                caste_offset + int(woman_indicator)
            ] += 1
        if category % 2 and sex == "पुरुष":
            sex_conflicts.append(evidence)
    comparisons = []
    for record in records:
        district = normalize_label(record["district_name_source_review_raw"])
        matching = [
            g
            for (body, name), g in groups.items()
            if body == record["local_body_type"]
            and (record["is_statewide_total"] or name == district)
        ]
        printed = [record[k] for k in METRICS[2:10]]
        counts = {
            s: [sum(g[s][i] for g in matching) for i in range(8)] for s in strategies
        }
        comparisons.append(
            {
                "local_body_type": record["local_body_type"],
                "district_name_source_review_raw": district,
                "is_statewide_total": record["is_statewide_total"],
                "source_sha256": record["source_sha256"],
                "source_page": record["source_page"],
                "source_data_row_on_page": record["source_data_row_on_page"],
                "matched_result_groups": len(matching),
                "printed_wards": record["wards"],
                "result_rows": sum(g["rows"] for g in matching),
                "printed_classification": printed,
                "observed_classifications": counts,
                "differences": {
                    s: [n - printed[i] for i, n in enumerate(counts[s])]
                    for s in strategies
                },
            }
        )
    districts = [r for r in comparisons if not r["is_statewide_total"]]
    return {
        "winner_input": str(path.resolve()),
        "winner_input_sha256": sha256(raw),
        "winner_input_rows": len(winners),
        "classification_columns": list(METRICS[2:10]),
        "district_label_aliases": aliases,
        "district_body_cells": len(districts),
        "exact_district_matches": {
            s: sum(
                r["matched_result_groups"] == 1 and not any(r["differences"][s])
                for r in districts
            )
            for s in strategies
        },
        "comparisons": comparisons,
        "missing_candidate_categories": missing_categories,
        "female_category_male_sex_conflicts": sex_conflicts,
        "unrecognized_reported_sexes": unknown_sexes,
        "unrecognized_seat_categories": unknown_seat_categories,
        "interpretation": (
            "Published elected-candidate classifications, not seat reservations. The"
            " either-woman-indicator calculation is a source-reconciliation hypothesis,"
            " not a correction of reported sex or a claim about a person's sex."
            " Contradictions and missing values remain unresolved."
        ),
        "assignment_usable": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--winner-results", type=Path)
    args = parser.parse_args()
    review_raw = args.review.read_bytes()
    review = json.loads(review_raw)
    index_spec = review["index"]
    index = read_pinned(args.source_root, index_spec["path"], index_spec["sha256"])
    records, sources, layouts = [], [], []
    for spec in review["sources"]:
        read_pinned(args.source_root, spec["path"], spec["sha256"])
        year = source_year(index, index_spec["url"], spec["url"])
        if year != spec["election_year"]:
            raise ValueError("Reviewed year disagrees with the official index section")
        result = subprocess.run(
            ["pdftotext", "-layout", str(args.source_root / spec["path"]), "-"],
            capture_output=True,
            text=True,
            check=True,
        )
        layout = result.stdout
        layouts.append((spec["sha256"], layout.encode("utf-8")))
        source_records = []
        pages = [page for page in layout.split("\f") if page.strip()]
        if len(pages) != len(spec["district_labels_by_page"]):
            raise ValueError("PDF page count differs from the visual review")
        for page_number, page in enumerate(pages, 1):
            labels = spec["district_labels_by_page"][str(page_number)]
            ordinal = 0
            for line_number, line in enumerate(page.splitlines(), 1):
                match = ROW.fullmatch(line)
                if match is None:
                    continue
                label, values = match.groups()
                total = label.strip() == "egk ;ksx"
                if not total:
                    ordinal += 1
                    if ordinal > len(labels):
                        raise ValueError(
                            "More source rows than visually reviewed labels"
                        )
                record = dict(zip(METRICS, map(int, values.split()), strict=True))
                record.update(
                    election_year=year,
                    local_body_type=spec["local_body_type"],
                    district_name_source_review_raw=(
                        "महा योग" if total else labels[ordinal - 1]
                    ),
                    district_name_native_raw=label.strip(),
                    is_statewide_total=total,
                    source_sha256=spec["sha256"],
                    source_path=spec["path"],
                    source_url=spec["url"],
                    source_page=page_number,
                    source_line=line_number,
                    source_data_row_on_page=ordinal + int(total),
                    source_line_raw=line,
                    label_review_sha256=sha256(review_raw),
                    year_source_sha256=index_spec["sha256"],
                    assignment_usable=False,
                    record_unit="district_body_type_elected_aggregate",
                    metric_scope="published_elected_candidate_classification",
                )
                record["quality_flags"] = ";".join(arithmetic_issues(record))
                source_records.append(record)
            if ordinal != len(labels):
                raise ValueError(
                    "Source row count differs from the visual label review"
                )
        totals = [r for r in source_records if r["is_statewide_total"]]
        districts = [r for r in source_records if not r["is_statewide_total"]]
        if len(totals) != 1 or not districts:
            raise ValueError("Expected district rows and one statewide total")
        grand_total = totals[0]
        reconciliation = {
            metric: sum(row[metric] for row in districts) - grand_total[metric]
            for metric in METRICS
        }
        sources.append(
            {
                "source_sha256": spec["sha256"],
                "source_url": spec["url"],
                "local_body_type": spec["local_body_type"],
                "election_year": year,
                "district_rows": len(districts),
                "statewide_totals": {k: grand_total[k] for k in METRICS},
                "district_sum_minus_printed_total": reconciliation,
                "rows_with_arithmetic_issues": sum(
                    bool(r["quality_flags"]) for r in source_records
                ),
            }
        )
        records.extend(source_records)
    comparison = (
        compare_winners(records, args.winner_results, review)
        if args.winner_results
        else None
    )
    args.output.mkdir(parents=True, exist_ok=False)
    for digest, layout in layouts:
        (args.output / f"{digest}.layout.txt.gz").write_bytes(
            gzip.compress(layout, mtime=0)
        )
    table = pa.Table.from_pylist(records)
    artifact = args.output / "district_urban_elected_counts.parquet"
    pq.write_table(table, artifact, compression="zstd")
    dictionary = {
        "record_unit": (
            "One printed district/body-type aggregate or statewide total; not a seat."
        ),
        "district_name_native_raw": (
            "Unmodified legacy-font text returned by pdftotext."
        ),
        "district_name_source_review_raw": (
            "Visual source transcription pinned by PDF, page and row; not a canonical"
            " identifier."
        ),
        "election_year": (
            "Year of the preceding election section in the pinned official link index;"
            " not a PDF publication date."
        ),
        "metric_scope": (
            "Published classification of elected candidates, not reservation of the"
            " seats they won; not independently verified sex or caste."
        ),
        "elected_unreserved": (
            "Printed unreserved candidate-classification column, excluding the"
            " separately reported women column; not an unreserved-seat count."
        ),
        "elected_women": (
            "Printed women candidate-classification column, excluding separately"
            " reported BC/SC/ST women columns."
        ),
        "elected_bc/elected_sc/elected_st": (
            "Printed elected-candidate classification excluding the corresponding women"
            " columns; not seat reservations."
        ),
        "elected_bc_women/elected_sc_women/elected_st_women": (
            "Printed women subdivisions of elected-candidate classifications;"
            " conflicting individual category and sex fields are not resolved by these"
            " totals."
        ),
        "elected_non_women_total": (
            "Printed total labelled total unreserved, summing non-women classification"
            " columns across castes; not UR caste alone or independently verified men."
        ),
        "elected_women_total": (
            "Sum of the four printed women classification columns; not women-reserved"
            " seats."
        ),
        "elected_total": (
            "Printed total of elected-candidate classifications, compared with the"
            " printed ward total."
        ),
        "assignment_usable": (
            "Always false: aggregates cannot be substituted for missing ward"
            " assignments."
        ),
        "quality_flags": (
            "Arithmetic discrepancies are retained rather than silently corrected; an"
            " empty value is not an independent accuracy certification."
        ),
    }
    (args.output / "dictionary.json").write_text(
        json.dumps(dictionary, indent=2) + "\n"
    )
    if comparison is not None:
        (args.output / "winner_classification_comparison.json").write_text(
            json.dumps(comparison, ensure_ascii=False, indent=2) + "\n"
        )
    with artifact.open("rb") as stream:
        artifact_sha = hashlib.file_digest(stream, "sha256").hexdigest()
    receipt = {
        "finished_utc": datetime.now(UTC).isoformat(),
        "output": str(args.output.resolve()),
        "rows": len(records),
        "sources": sources,
        "label_review_sha256": sha256(review_raw),
        "artifact_sha256": artifact_sha,
        "year_index_sha256": index_spec["sha256"],
        "new_paid_api_cost_usd": 0,
        "assignment_usable": False,
        "schema_version": 2,
        "metric_scope": "published_elected_candidate_classification",
        "winner_comparison": (
            None
            if comparison is None
            else {
                "winner_input_sha256": comparison["winner_input_sha256"],
                "district_body_cells": comparison["district_body_cells"],
                "exact_district_matches": comparison["exact_district_matches"],
                "missing_candidate_categories": len(
                    comparison["missing_candidate_categories"]
                ),
                "female_category_male_sex_conflicts": len(
                    comparison["female_category_male_sex_conflicts"]
                ),
            }
        ),
        "status": (
            "Source-derived elected-candidate aggregates; not seat reservations."
            " Independent review and geographic crosswalk pending."
        ),
    }
    (args.output / "parse_receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n"
    )
    print(json.dumps(receipt), flush=True)


if __name__ == "__main__":
    main()
