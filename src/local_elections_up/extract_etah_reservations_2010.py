"""Extract Etah's retrospective reservation cells without decoding legacy fonts."""

import argparse
import bisect
import collections
import gzip
import hashlib
import itertools
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pdfplumber
import pyarrow as pa
import pyarrow.parquet as pq

SOURCE = (
    "data/discovery/2026-09-10/archived_reservations/raw/"
    "4ef7c2223a1030b9a888_53bfc78b35fb.pdf"
)
SHA256 = "53bfc78b35fb351dcf8f6fed54c3f07c0e51b51ea244266ed174e9ef3295fe29"
URL = "http://etah.nic.in:80/ZP-reservation2010/PRADHAN-RESERVATION-2010.pdf"
CAPTURE = "20101207092710"
FIELDS = (
    "printed_serial_raw",
    "district_raw",
    "block_raw",
    "gp_number_raw",
    "gp_name_raw",
    *(f"source_column_{i:02d}_raw" for i in range(6, 16)),
    "reservation_1995_raw",
    "reservation_2000_raw",
    "reservation_2005_raw",
    "reservation_2010_raw",
)
NS = {"x": "http://www.w3.org/1999/xhtml"}


def cluster(values, tolerance=1.5):
    groups = []
    for value in sorted(values):
        if groups and value - groups[-1][-1] <= tolerance:
            groups[-1].append(value)
        else:
            groups.append([value])
    return [sum(group) / len(group) for group in groups]


def words_for(page):
    return [
        {
            "text": word.text or "",
            **{k: float(word.attrib[k]) for k in ("xMin", "xMax", "yMin", "yMax")},
        }
        for word in page.findall(".//x:word", NS)
    ]


def center(word, axis):
    return (word[f"{axis}Min"] + word[f"{axis}Max"]) / 2


def extract_page(page, pdf_page, template=None):
    words = words_for(page)
    verticals = [
        edge
        for edge in pdf_page.edges
        if abs(edge["x0"] - edge["x1"]) < 1 and edge["height"] > 10
    ]
    minimum_height = max((edge["height"] for edge in verticals), default=0) * 0.1
    xs = cluster([edge["x0"] for edge in verticals if edge["height"] >= minimum_height])
    if len(xs) not in (15, 16):
        return [], {"status": "column_grid_unrecognized", "x_boundaries": xs}
    column_count = len(xs) - 1
    labels = None
    for anchor in words:
        if anchor["text"] != "1" or center(anchor, "y") > pdf_page.height * 0.65:
            continue
        candidate = sorted(
            [
                word
                for word in words
                if abs(center(word, "y") - center(anchor, "y")) < 3
                and word["text"].isdigit()
            ],
            key=lambda word: center(word, "x"),
        )
        numbers = [int(word["text"]) for word in candidate]
        if (
            len(numbers) in (column_count, column_count - 1)
            and numbers[0] == 1
            and numbers[-1] <= column_count + 1
            and all(left < right for left, right in itertools.pairwise(numbers))
        ):
            labels = candidate
            break
    if labels is None:
        if template is None:
            return [], {
                "status": "continuation_without_preceding_header",
                "x_boundaries": xs,
            }
        if len(xs) != len(template["x_boundaries"]) or any(
            abs(x - expected) > 1.5
            for x, expected in zip(xs, template["x_boundaries"], strict=True)
        ):
            return [], {
                "status": "continuation_grid_differs_from_header",
                "x_boundaries": xs,
            }
        header_y = -1
        header_basis = "preceding_header_with_matching_drawn_columns"
        header_source_page = template["source_page"]
        year_columns = template["year_columns"]
        year_evidence = template["year_header_evidence"]
        printed_header_numbers = template["printed_header_numbers"]
    else:
        if [bisect.bisect_right(xs, center(w, "x")) - 1 for w in labels] != list(
            range(len(labels))
        ):
            return [], {
                "status": "header_columns_do_not_match_grid",
                "x_boundaries": xs,
            }
        header_y = sum(center(word, "y") for word in labels) / len(labels)
        header_basis = "numbered_header_on_page"
        header_source_page = None
        printed_header_numbers = [word["text"] for word in labels]
        year_evidence = {str(year): [] for year in (1995, 2000, 2005, 2010)}
        for word in words:
            if center(word, "y") >= header_y:
                continue
            for year in re.findall(
                r"(?<![0-9])(1995|2000|2005|2010)(?![0-9])", word["text"]
            ):
                year_evidence[year].append(
                    {
                        "source_column": bisect.bisect_right(xs, center(word, "x")),
                        **word,
                    }
                )
        year_columns = {}
        for year, evidence in year_evidence.items():
            columns = {item["source_column"] for item in evidence}
            if len(columns) == 1:
                year_columns[year] = columns.pop()
        expected = dict(
            zip(
                ("1995", "2000", "2005", "2010"),
                range(column_count - 3, column_count + 1),
                strict=True,
            )
        )
        if year_columns != expected:
            return [], {
                "status": "year_header_columns_unrecognized",
                "x_boundaries": xs,
                "year_columns": year_columns,
                "year_header_evidence": year_evidence,
            }
    ys = [
        y
        for y in cluster(
            [
                edge["top"]
                for edge in pdf_page.edges
                if abs(edge["top"] - edge["bottom"]) < 1
                and edge["width"] >= 0.9 * (xs[-1] - xs[0])
            ]
        )
        if y > header_y
    ]
    if len(ys) < 2:
        return [], {"status": "row_grid_unrecognized", "y_boundaries": ys}
    cells = collections.defaultdict(list)
    outside = []
    for word in words:
        x, y = center(word, "x"), center(word, "y")
        if xs[0] <= x < xs[-1] and ys[0] <= y < ys[-1]:
            cells[
                bisect.bisect_right(ys, y) - 1, bisect.bisect_right(xs, x) - 1
            ].append(word)
        else:
            outside.append(word["text"])
    rows = []
    for row_number in range(len(ys) - 1):
        cell_text = [
            " ".join(
                word["text"]
                for word in sorted(
                    cells[row_number, col],
                    key=lambda word: (round(word["yMin"] / 3), word["xMin"]),
                )
            )
            for col in range(column_count)
        ]
        raw = dict.fromkeys(FIELDS, "")
        raw.update(zip(FIELDS[:5], cell_text[:5], strict=True))
        raw.update(
            {
                f"source_column_{col + 1:02d}_raw": cell_text[col]
                for col in range(5, column_count)
            }
        )
        raw.update(
            {
                f"reservation_{year}_raw": cell_text[col - 1]
                for year, col in year_columns.items()
            }
        )
        if not any(raw.values()):
            continue
        rows.append(
            raw
            | {
                "source_grid_row": row_number + 1,
                "source_y_min": ys[row_number],
                "source_y_max": ys[row_number + 1],
                "is_gp_observation": (
                    raw["printed_serial_raw"].isdigit()
                    and raw["gp_number_raw"].isdigit()
                ),
            }
        )
    return rows, {
        "status": "grid_extracted_pending_review",
        "x_boundaries": xs,
        "header_basis": header_basis,
        "header_source_page": header_source_page,
        "source_column_count": column_count,
        "year_columns": year_columns,
        "year_header_evidence": year_evidence,
        "printed_header_numbers": printed_header_numbers,
        "source_header_numbering_irregular": (
            printed_header_numbers
            != [str(i) for i in range(1, len(printed_header_numbers) + 1)]
        ),
        "y_boundaries": ys,
        "outside_grid_text_raw": " ".join(outside),
        "native_word_count": len(words),
        "grid_rows": len(rows),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/interim/etah_reservations_2010_grid_v5"),
    )
    args = parser.parse_args()
    source = args.root / SOURCE
    if hashlib.sha256(source.read_bytes()).hexdigest() != SHA256:
        raise ValueError("Source PDF differs from the archived acquisition")
    command = ["pdftotext", "-bbox-layout", str(source), "-"]
    extracted = subprocess.run(command, check=True, capture_output=True).stdout
    native_sha = hashlib.sha256(extracted).hexdigest()
    pages = ET.fromstring(extracted).findall(".//x:page", NS)
    output = args.root / args.output
    output.mkdir(parents=True, exist_ok=False)
    native_path = output / "native_text.xhtml.gz"
    native_path.write_bytes(gzip.compress(extracted, compresslevel=6, mtime=0))
    rows, profiles = [], []
    template = None
    with pdfplumber.open(source) as pdf:
        if len(pages) != len(pdf.pages) or len(pages) != 121:
            raise ValueError("Unexpected source or native-text page count")
        for number, (page, pdf_page) in enumerate(
            zip(pages, pdf.pages, strict=True), 1
        ):
            extracted_rows, profile = extract_page(page, pdf_page, template)
            if profile.get("header_basis") == "numbered_header_on_page":
                profile["header_source_page"] = number
                template = {
                    "source_page": number,
                    "x_boundaries": profile["x_boundaries"],
                    "year_columns": profile["year_columns"],
                    "year_header_evidence": profile["year_header_evidence"],
                    "printed_header_numbers": profile["printed_header_numbers"],
                }
            elif profile["status"] != "grid_extracted_pending_review":
                template = None
            profiles.append({"source_page": number, **profile})
            for row in extracted_rows:
                identity = f"{SHA256}:{number}:{row['source_grid_row']}"
                rows.append(
                    {
                        "observation_id": (
                            hashlib.sha256(identity.encode()).hexdigest()[:24]
                        ),
                        "source_path": SOURCE,
                        "source_sha256": SHA256,
                        "source_url": URL,
                        "archive_capture": CAPTURE,
                        "source_page": number,
                        "native_text_sha256": native_sha,
                        "header_source_page": profile["header_source_page"],
                        "source_column_count": profile["source_column_count"],
                        "source_header_numbering_irregular": profile[
                            "source_header_numbering_irregular"
                        ],
                        "year_column_map_json": json.dumps(
                            profile["year_columns"], sort_keys=True
                        ),
                        "state": "Uttar Pradesh",
                        "district": "Etah",
                        "tier": "gp_head",
                        "reference_geography_year": 2010,
                        **row,
                    }
                )
            if number % 20 == 0:
                print(
                    json.dumps({"pages_processed": number, "grid_rows": len(rows)}),
                    flush=True,
                )
            pdf_page.close()
    eligible = [row for row in rows if row["is_gp_observation"]]
    occurrences = collections.defaultdict(list)
    code_names = collections.defaultdict(set)
    name_codes = collections.defaultdict(set)
    code_counts = collections.Counter()
    for row in eligible:
        occurrences[row["block_raw"], row["gp_name_raw"]].append(row)
        code_names[row["block_raw"], row["gp_number_raw"]].add(row["gp_name_raw"])
        name_codes[row["block_raw"], row["gp_name_raw"]].add(row["gp_number_raw"])
        code_counts[row["block_raw"], row["gp_number_raw"]] += 1
    history = []
    for row in eligible:
        repeats = occurrences[row["block_raw"], row["gp_name_raw"]]
        for year in (1995, 2000, 2005, 2010):
            raw = row[f"reservation_{year}_raw"]
            flags = [
                "visual_review_pending",
                "legacy_font_names_unresolved",
                "code_legend_unvalidated",
            ]
            if row["source_header_numbering_irregular"]:
                flags.append("source_header_numbering_irregular")
            if not raw:
                flags.append("reservation_cell_blank")
            if not row["block_raw"] or not row["gp_name_raw"]:
                flags.append("geography_cell_missing")
            if len(repeats) > 1:
                flags.append("repeated_raw_block_name_group")
            if len(code_names[row["block_raw"], row["gp_number_raw"]]) > 1:
                flags.append("source_gp_number_shared_by_different_names")
            if len(name_codes[row["block_raw"], row["gp_name_raw"]]) > 1:
                flags.append("same_raw_name_printed_with_multiple_gp_numbers")
            if (
                len(
                    {
                        item[f"reservation_{year}_raw"]
                        for item in repeats
                        if item[f"reservation_{year}_raw"]
                    }
                )
                > 1
            ):
                flags.append("conflicting_nonblank_reservation_cells")
            if raw == "0":
                flags.append("zero_code_meaning_unresolved")
            history.append(
                {key: value for key, value in row.items() if key not in FIELDS}
                | {
                    "year": year,
                    "reservation_raw": raw,
                    "block_raw": row["block_raw"],
                    "gp_number_raw": row["gp_number_raw"],
                    "gp_name_raw": row["gp_name_raw"],
                    "printed_serial_raw": row["printed_serial_raw"],
                    "retrospective": year < 2010,
                    "source_key_occurrences": len(repeats),
                    "source_key_basis": (
                        "exact_raw_block_and_gp_name_not_verified_identity"
                    ),
                    "review_status": "needs_review",
                    "quality_flags": ";".join(flags),
                    "assignment_status": (
                        "retrospective_report"
                        if year < 2010
                        else "prospective_column_unvalidated"
                    ),
                }
            )
    name_groups = []
    for (block, name), evidence in sorted(occurrences.items()):
        for year in (1995, 2000, 2005, 2010):
            codes = sorted(
                {
                    item[f"reservation_{year}_raw"]
                    for item in evidence
                    if item[f"reservation_{year}_raw"]
                }
            )
            agreed = codes[0] if len(codes) == 1 else None
            source_numbers = sorted(name_codes[block, name])
            shared_numbers = [
                number
                for number in source_numbers
                if len(code_names[block, number]) > 1
            ]
            group_identity = json.dumps([SHA256, block, name, year], ensure_ascii=True)
            name_groups.append(
                {
                    "name_group_id": (
                        hashlib.sha256(group_identity.encode()).hexdigest()[:24]
                    ),
                    "state": "Uttar Pradesh",
                    "district": "Etah",
                    "tier": "gp_head",
                    "block_raw": block,
                    "gp_name_raw": name,
                    "year": year,
                    "reference_geography_year": 2010,
                    "retrospective": year < 2010,
                    "grouping_basis": (
                        "exact_raw_block_and_gp_name_not_verified_identity"
                    ),
                    "source_sha256": SHA256,
                    "source_path": SOURCE,
                    "source_url": URL,
                    "archive_capture": CAPTURE,
                    "gp_numbers_raw": source_numbers,
                    "gp_numbers_shared_with_other_names": shared_numbers,
                    "observed_nonblank_codes_raw": codes,
                    "reservation_raw_agreed": agreed,
                    "conflicting_nonblank_readings": len(codes) > 1,
                    "zero_code_meaning_unresolved": agreed == "0",
                    "blank_printings": sum(
                        not item[f"reservation_{year}_raw"] for item in evidence
                    ),
                    "source_printings": len(evidence),
                    "source_observation_ids": [
                        item["observation_id"] for item in evidence
                    ],
                    "source_pages": sorted({item["source_page"] for item in evidence}),
                    "review_status": "identity_font_and_code_legend_review_pending",
                    "validated_assignment": False,
                }
            )
    pq.write_table(
        pa.Table.from_pylist(name_groups),
        output / "reservation_name_groups.parquet",
        compression="zstd",
    )
    pq.write_table(
        pa.Table.from_pylist(rows),
        output / "source_grid_rows.parquet",
        compression="zstd",
    )
    pq.write_table(
        pa.Table.from_pylist(history),
        output / "reservation_observations.parquet",
        compression="zstd",
    )
    manifest = {
        "extractor": "extract_etah_reservations_2010",
        "extractor_version": 5,
        "source_path": SOURCE,
        "source_sha256": SHA256,
        "source_url": URL,
        "archive_capture": CAPTURE,
        "native_text_sha256": native_sha,
        "native_text_hash_semantics": "decompressed Poppler XHTML bytes",
        "native_text_path": "native_text.xhtml.gz",
        "pages": len(pages),
        "page_statuses": dict(collections.Counter(p["status"] for p in profiles)),
        "source_grid_rows": len(rows),
        "gp_observation_printings": len(eligible),
        "distinct_raw_block_gp_keys": len(code_names),
        "repeated_raw_block_gp_keys": sum(count > 1 for count in code_counts.values()),
        "distinct_raw_block_name_groups": len(occurrences),
        "gp_numbers_shared_by_different_names": sum(
            len(names) > 1 for names in code_names.values()
        ),
        "raw_names_printed_with_multiple_gp_numbers": sum(
            len(codes) > 1 for codes in name_codes.values()
        ),
        "conflicting_name_groups_by_year": {
            str(year): sum(
                item["conflicting_nonblank_readings"]
                for item in name_groups
                if item["year"] == year
            )
            for year in (1995, 2000, 2005, 2010)
        },
        "historical_cells_including_blanks": sum(
            row["retrospective"] for row in history
        ),
        "nonempty_cells_by_year": dict(
            collections.Counter(
                row["year"] for row in history if row["reservation_raw"]
            )
        ),
        "quality_flags": dict(
            collections.Counter(
                flag for row in history for flag in row["quality_flags"].split(";")
            )
        ),
        "deduplication": (
            "none; physical printings retained; blank cells never interpreted as"
            " unreserved"
        ),
        "release_ready": False,
        "status": "research staging; source comparison and legend validation pending",
        "page_profiles": profiles,
    }
    (output / "extraction_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )
    print(
        json.dumps(
            {key: value for key, value in manifest.items() if key != "page_profiles"}
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
