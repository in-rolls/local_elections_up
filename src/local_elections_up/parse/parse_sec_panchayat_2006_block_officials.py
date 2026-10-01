# /// script
# requires-python = ">=3.11"
# dependencies = ["pyarrow>=14"]
# ///
"""Extract provenance-preserving observations from UP's archived 2006 KP list."""

import argparse
import bisect
import collections
import gzip
import hashlib
import json
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

SOURCE_SHA = "f574b4abb00c92a5cfc208b39ddc57a28be2ff58fa4118c8077d22979be445d2"
NS = {"x": "http://www.w3.org/1999/xhtml"}
COLUMNS = [
    ("block_serial", 90, 115),
    ("block_name", 115, 185),
    ("post_category", 185, 275),
    ("office", 275, 341),
    ("membership_ward_number", 341, 373),
    ("membership_ward_name", 373, 470),
    ("candidate_and_related_name", 470, 630),
    ("sex", 630, 665),
    ("candidate_category", 665, 765),
]
OFFICES = {
    "izeq[k": "block_chair",
    'T;s"Bmiizeq[k': "senior_deputy_block_chair",
    'dfu"Bmiizeq[k': "junior_deputy_block_chair",
}
CATEGORIES = {
    "vukjf{kr": ("NONE", False),
    "efgyk": ("NONE", True),
    "fiNM+htkfr": ("BC", False),
    "fiNM+htkfr&efgyk": ("BC", True),
    "vuqlwfprtkfr": ("SC", False),
    "vuqlwfprtkfr&efgyk": ("SC", True),
}
BASE_HOLDS = [
    "mixed_legacy_encodings_undecoded",
    "overprinted_glyphs_unreviewed",
    "independent_review_pending",
    "historical_geography_unmapped",
    "reservation_assignment_unadjudicated",
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def timestamp():
    return datetime.now(UTC).isoformat()


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2) + "\n")


def cell_text(words):
    lines = []
    for word in sorted(words, key=lambda w: (w["y_min"], w["x_min"])):
        if not lines or word["y_min"] - lines[-1][0]["y_min"] > 2.5:
            lines.append([])
        lines[-1].append(word)
    return (
        "\n".join(
            " ".join(
                w["text_encoded_raw"] for w in sorted(line, key=lambda w: w["x_min"])
            )
            for line in lines
        )
        or None
    )


def compact(value):
    return re.sub(r"\s+", "", value or "")


def extract_page(page, number, current):
    words = [
        {
            "source_sha256": SOURCE_SHA,
            "source_page": number,
            "source_word": index,
            "text_encoded_raw": word.text or "",
            "x_min": float(word.attrib["xMin"]),
            "x_max": float(word.attrib["xMax"]),
            "y_min": float(word.attrib["yMin"]),
            "y_max": float(word.attrib["yMax"]),
            "observation_id": None,
            "column": None,
        }
        for index, word in enumerate(page.findall(".//x:word", NS), 1)
    ]
    header = [w for w in words if 80 <= w["y_min"] < 105]
    codes = [
        w["text_encoded_raw"]
        for w in words
        if 105 <= w["y_min"] < 125
        and 180 <= w["x_min"] < 225
        and re.fullmatch(r"\d{4}", w["text_encoded_raw"])
    ]
    district = codes[0] if len(codes) == 1 else None
    district_name = cell_text(
        [w for w in words if 105 <= w["y_min"] < 125 and w["x_min"] >= 225]
    )
    flags = []
    if not any(w["text_encoded_raw"] == "fuokZpu&2006" for w in header):
        flags.append("year_heading_unresolved")
    if district is None or not district_name:
        flags.append("district_header_unresolved")
    for left, right, tokens in [
        (185, 275, {"in", "dh", "vkj{k.k", "Js.kh"}),
        (275, 341, {"in", "dk", "uke"}),
        (630, 665, {"fyax"}),
        (665, 765, {"mEehnokj", "dh", "vkj{k.k", "Js.kh"}),
    ]:
        found = {
            w["text_encoded_raw"]
            for w in words
            if 125 <= w["y_min"] < 177 and left <= w["x_min"] < right
        }
        if not tokens.issubset(found):
            flags.append("column_header_unresolved_" + str(left))
    body = [w for w in words if 177 <= w["y_min"] < 488]
    report = {
        "source_page": number,
        "district_code_raw": district,
        "district_name_encoded_raw": district_name,
        "media_width_raw": float(page.attrib["width"]),
        "media_height_raw": float(page.attrib["height"]),
        "page_flags": flags,
        "source_words": len(words),
        "observations": 0,
        "unassigned_body_words": 0,
    }
    if flags:
        report["unassigned_body_words"] = len(body)
        return words, [], report, None
    if current and current["district_code_raw"] != district:
        current = None
    anchor_words = [
        w
        for w in body
        if 275 <= w["x_min"] < 341
        or (341 <= w["x_min"] < 373 and re.fullmatch(r"\d+", w["text_encoded_raw"]))
    ]
    groups = []
    for word in sorted(anchor_words, key=lambda w: (w["y_min"], w["x_min"])):
        if not groups or word["y_min"] - groups[-1][0]["y_min"] > 3:
            groups.append([])
        groups[-1].append(word)
    if not groups:
        report["page_flags"].append("row_anchors_unresolved")
        report["unassigned_body_words"] = len(body)
        return words, [], report, None
    starts = [min(w["y_min"] for w in group) - 0.5 for group in groups]
    buckets = [[] for _ in groups]
    for word in body:
        index = bisect.bisect_right(starts, word["y_min"]) - 1
        if index < 0:
            report["unassigned_body_words"] += 1
        else:
            buckets[index].append(word)
    rows = []
    for ordinal, (group, bucket) in enumerate(zip(groups, buckets, strict=False), 1):
        anchor_word = min(w["source_word"] for w in group)
        observation_id = sha(f"{SOURCE_SHA}:{number}:{anchor_word}".encode())
        cells = {name: [] for name, _, _ in COLUMNS}
        issues = []
        for word in bucket:
            word["observation_id"] = observation_id
            column = next(
                (
                    (name, right)
                    for name, left, right in COLUMNS
                    if left <= word["x_min"] < right
                ),
                None,
            )
            if column is None:
                issues.append("word_outside_columns")
                continue
            name, right = column
            word["column"] = name
            cells[name].append(word)
            if word["x_max"] > right + 1:
                issues.append("column_overflow_" + name)
        raw = {name: cell_text(values) for name, values in cells.items()}
        serial = compact(raw["block_serial"])
        if serial:
            if re.fullmatch(r"\d+", serial):
                current = {
                    "district_code_raw": district,
                    "block_serial_raw": serial,
                    "block_name_encoded_raw": raw["block_name"],
                    "source_page": number,
                    "source_row_on_page": ordinal,
                    "source_observation_id": observation_id,
                }
            else:
                current = None
                issues.append("block_serial_unresolved")
        if current is None:
            issues.append("block_context_unresolved")
        if current and current["source_page"] != number:
            issues.append("cross_page_block_context_requires_review")
        office = OFFICES.get(compact(raw["office"]))
        if office is None:
            issues.append("office_unmapped")
        ward = compact(raw["membership_ward_number"])
        if not re.fullmatch(r"\d+", ward):
            issues.append("membership_ward_number_unresolved")
        candidate_category = CATEGORIES.get(compact(raw["candidate_category"]))
        post_category = CATEGORIES.get(compact(raw["post_category"]))
        if candidate_category is None:
            issues.append("candidate_category_unmapped")
        if raw["post_category"] and post_category is None:
            issues.append("post_category_unmapped")
        for field in ("candidate_and_related_name", "sex"):
            if not raw[field]:
                issues.append("missing_" + field)
        if report["unassigned_body_words"]:
            issues.append("page_contains_unassigned_body_words")
        row = {
            "observation_id": observation_id,
            "source_sha256": SOURCE_SHA,
            "source_page": number,
            "source_row_on_page": ordinal,
            "source_anchor_word": anchor_word,
            "election_year": 2006,
            "district_code_raw": district,
            "district_name_encoded_raw": district_name,
            **{name + "_encoded_raw": value for name, value in raw.items()},
            "office_normalized": office,
            "membership_ward_number": int(ward) if re.fullmatch(r"\d+", ward) else None,
            "reported_candidate_caste": (
                candidate_category[0] if candidate_category else None
            ),
            "reported_candidate_woman": (
                candidate_category[1] if candidate_category else None
            ),
            "printed_post_caste": post_category[0] if post_category else None,
            "printed_post_woman": post_category[1] if post_category else None,
            "block_context_serial_raw": (
                current["block_serial_raw"] if current else None
            ),
            "block_context_name_encoded_raw": (
                current["block_name_encoded_raw"] if current else None
            ),
            "block_context_source_observation_id": (
                current["source_observation_id"] if current else None
            ),
            "block_context_source_page": current["source_page"] if current else None,
            "block_context_source_row": (
                current["source_row_on_page"] if current else None
            ),
            "source_word_count": len(bucket),
            "row_y_min": min(w["y_min"] for w in bucket),
            "row_y_max": max(w["y_max"] for w in bucket),
            "structural_flags": sorted(set(issues)),
            "quality_flags": BASE_HOLDS + sorted(set(issues)),
            "assignment_usable": False,
        }
        rows.append(row)
    report["observations"] = len(rows)
    return words, rows, report, current


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    args = parser.parse_args()
    root = args.source_root.resolve()
    events = [
        json.loads(line)
        for line in (root / "downloads.jsonl").read_text().splitlines()
        if line.strip()
    ]
    sources = [
        event
        for event in events
        if event.get("status") == "pdf_acquired"
        and event.get("body", {}).get("sha256") == SOURCE_SHA
    ]
    if not sources:
        parser.error("Supported PDF has no successful acquisition receipt")
    source = (root / sources[0]["body"]["path"]).resolve()
    if not source.is_relative_to(root):
        parser.error("Source path escapes acquisition root")
    data = gzip.decompress(source.read_bytes())
    if sha(data) != SOURCE_SHA:
        parser.error("Acquired PDF differs from supported source hash")
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    output = root / "parsed_officials_2006" / stamp
    output.mkdir(parents=True, exist_ok=False)
    receipt = {
        "started_utc": timestamp(),
        "status": "incomplete",
        "source_sha256": SOURCE_SHA,
        "acquisition_events": sources,
        "script_sha256": sha(Path(__file__).read_bytes()),
        "output": str(output),
        "assignment_usable": False,
        "new_paid_api_cost_usd": 0,
    }
    save_json(output / "parse_receipt.json", receipt)
    try:
        with tempfile.TemporaryDirectory(prefix="up-kp2006-") as directory:
            pdf = Path(directory) / "source.pdf"
            pdf.write_bytes(data)
            result = subprocess.run(
                ["pdftotext", "-bbox-layout", "-enc", "UTF-8", str(pdf), "-"],
                capture_output=True,
                check=True,
            )
        (output / "source_bbox.xhtml.gz").write_bytes(
            gzip.compress(result.stdout, mtime=0)
        )
        receipt["bbox_sha256"] = sha(result.stdout)
        receipt["pdftotext_stderr_raw"] = result.stderr.decode(
            "utf-8", errors="replace"
        )
        pages = ET.fromstring(result.stdout).findall(".//x:page", NS)
        if len(pages) != 179:
            raise ValueError("Supported PDF must yield 179 pages")
        words, rows, coverage, current = [], [], [], None
        for number, page in enumerate(pages, 1):
            page_words, page_rows, report, current = extract_page(page, number, current)
            words.extend(page_words)
            rows.extend(page_rows)
            coverage.append(report)
        pq.write_table(
            pa.Table.from_pylist(words),
            output / "source_words.parquet",
            compression="zstd",
        )
        if rows:
            pq.write_table(
                pa.Table.from_pylist(rows),
                output / "official_observations.parquet",
                compression="zstd",
            )
        save_json(output / "page_coverage.json", coverage)
        save_json(
            output / "dictionary.json",
            {
                "scope": (
                    "Printed 2006 block chairs and senior/junior deputies in one"
                    " archived PDF, not all block ward members or certified statewide"
                    " coverage."
                ),
                "encoded_raw": (
                    "PDF text fragments retained, including overlapping glyph fragments"
                    " and mixed legacy encodings; not decoded Hindi."
                ),
                "source_words": (
                    "Every extracted PDF word and bounding box, including words not"
                    " assigned to a row."
                ),
                "coordinates": (
                    "Unmodified Poppler text coordinates; this rotated PDF's text"
                    " coordinates can exceed the unrotated media-box width. Do not clip"
                    " at that width."
                ),
                "block_context": (
                    "Most recent explicit numeric block anchor within an uninterrupted"
                    " district. Source row retained; cross-page carry remains flagged."
                ),
                "post_category": (
                    "Only the category physically printed in this row's post-category"
                    " column. Never filled down from chair to deputy."
                ),
                "candidate_category": (
                    "Separate source-reported candidate category, not a substitute for"
                    " post reservation."
                ),
                "membership_ward": (
                    "Ward of which the elected official is a member, not automatically"
                    " a ward identifier for the chair/deputy office."
                ),
                "names": (
                    "Combined candidate/related-name field retained without speculative"
                    " splitting or Unicode conversion."
                ),
                "assignment_usable": (
                    "False throughout; extraction is not adjudication or independent"
                    " validation."
                ),
            },
        )
        receipt.update(
            finished_utc=timestamp(),
            status=(
                "parsed_with_page_holds"
                if any(p["page_flags"] for p in coverage)
                else "parsed"
            ),
            pages=len(pages),
            parsed_pages=sum(not p["page_flags"] for p in coverage),
            observations=len(rows),
            source_words=len(words),
            office_counts=dict(
                collections.Counter(r["office_normalized"] for r in rows)
            ),
            observed_district_codes=len({r["district_code_raw"] for r in rows}),
            unassigned_body_words=sum(p["unassigned_body_words"] for p in coverage),
            structural_flag_counts=dict(
                collections.Counter(f for r in rows for f in r["structural_flags"])
            ),
            unresolved_offices=dict(
                collections.Counter(
                    r["office_encoded_raw"] or "<blank>"
                    for r in rows
                    if r["office_normalized"] is None
                )
            ),
            artifacts={
                name: sha((output / name).read_bytes())
                for name in (
                    "official_observations.parquet",
                    "source_words.parquet",
                    "page_coverage.json",
                    "dictionary.json",
                )
                if (output / name).exists()
            },
        )
        save_json(output / "parse_receipt.json", receipt)
        print(json.dumps(receipt, ensure_ascii=True), flush=True)
    except Exception as error:
        receipt.update(finished_utc=timestamp(), status="failed", error=str(error))
        save_json(output / "parse_receipt.json", receipt)
        raise


if __name__ == "__main__":
    main()
