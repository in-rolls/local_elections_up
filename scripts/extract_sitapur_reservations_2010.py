"""Extract source-linked reservation observations from Sitapur's 2010 PDFs.

Poppler supplies positioned native text; no OCR or name correction is applied.
Encoded names remain evidence, not Unicode identifiers suitable for linkage.
"""

import argparse
import bisect
import collections
import csv
import gzip
import hashlib
import itertools
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
TOTAL_MARKER = re.compile(r";\s*k\s*s\s*x")
BASE = Path("data/discovery/2026-09-10/archived_reservations")
SOURCES = [
    {
        "tier": "gp_head",
        "path": "raw/50a5ab7fd0620118953a_1082e4316551.pdf",
        "sha256": "1082e4316551207ef4c358b1a18604513128cc8dc4cc5f8767aa9c98abdb2822",
        "url": "http://sitapur.nic.in:80/Reservation_pradhan/Election%202010/Pradhan%20GP.pdf",
        "capture": "20100928113509",
        "headers": ["1", "2", "3", "4", "5"],
        "columns": [
            "printed_serial",
            "district_raw",
            "block_raw",
            "unit_name_raw",
            "reservation_raw",
        ],
    },
    {
        "tier": "block_member",
        "path": "raw/0df2ed118dc874203c5c_ae79974344f0.pdf",
        "sha256": "ae79974344f059ac5a19580bcbb05daeefbdf2c329e923ad149c2d7cf607a03d",
        "url": "http://sitapur.nic.in:80/Reservation_pradhan/Election%202010/BDC%20CHETRA%20PANCHAYAT.pdf",
        "capture": "20100928113446",
        "headers": ["1", "2", "3", "4"],
        "columns": ["block_raw", "printed_serial", "unit_name_raw", "reservation_raw"],
    },
    {
        "tier": "district_member",
        "path": "raw/38befc8ce7dced591445_a0b46de2ebe2.pdf",
        "sha256": "a0b46de2ebe2ee41523b2694391833fe1d712a88f91ed9c732b2fa60f8da18be",
        "url": "http://sitapur.nic.in:80/Reservation_pradhan/Election%202010/ZELA%20PANCHAYAT.pdf.....pdf",
        "capture": "20100928113512",
        "headers": ["1", "3", "4", "5", "6", "7"],
        "columns": [
            "printed_serial",
            "block_raw",
            "ward_number_raw",
            "unit_name_raw",
            "boundary_raw",
            "reservation_raw",
        ],
    },
]
CATEGORY = {
    "vukjf{kr": ("NONE", 0),
    "efgyk": ("NONE", 1),
    "fL=;kW": ("NONE", 1),
    "fiNMh tkfr": ("BC", 0),
    "fIkNMh tkfr": ("BC", 0),
    "fiNMh tkfr efgyk": ("BC", 1),
    "fIkNMh tkfr efgyk": ("BC", 1),
    "fiNMk oxZ": ("BC", 0),
    "fiNMs oxZ dh fL=;kW": ("BC", 1),
    "vuqlwfpr tkfr": ("SC", 0),
    "vuqlwfpr tkfr efgyk": ("SC", 1),
    "vuqlwfpr tkfr dh fL=;kW": ("SC", 1),
    "vuqlwfpr tkfr fL=;kW": ("SC", 1),
}
FIELDS = [
    "observation_id",
    "state",
    "district",
    "year",
    "tier",
    "printed_serial",
    "district_raw",
    "block_raw",
    "ward_number_raw",
    "unit_name_raw",
    "boundary_raw",
    "reservation_raw",
    "caste_reservation",
    "woman_reserved",
    "source_path",
    "source_sha256",
    "source_url",
    "wayback_timestamp",
    "source_page",
    "source_row_on_page",
    "row_y_min",
    "row_y_max",
    "extraction_path",
    "extraction_sha256",
    "quality_flags",
    "review_status",
]


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def word_center(word, axis):
    return (word[f"{axis}Min"] + word[f"{axis}Max"]) / 2


def header(words, expected, height):
    numbers = [w for w in words if w["text"].isdigit() and w["yMin"] < height * 0.4]
    groups = []
    for word in sorted(numbers, key=lambda w: w["yMin"]):
        if not groups or abs(word["yMin"] - groups[-1][0]["yMin"]) > 2:
            groups.append([])
        groups[-1].append(word)
    for group in groups:
        group.sort(key=lambda w: w["xMin"])
        if [w["text"] for w in group] == expected:
            return group
    return None


def clustered(values, tolerance=1.5):
    groups = []
    for value in sorted(values):
        if not groups or value - groups[-1][-1] > tolerance:
            groups.append([])
        groups[-1].append(value)
    return [sum(group) / len(group) for group in groups]


def drawn_grid(pdf_page, labels, columns):
    xs = clustered(
        edge["x0"]
        for edge in pdf_page.edges
        if abs(edge["x0"] - edge["x1"]) < 1 and edge["height"] > 10
    )
    if len(xs) != len(columns) + 1:
        raise ValueError(
            f"Unexpected grid columns on page {pdf_page.page_number}: {xs}"
        )
    if [bisect.bisect_right(xs, word_center(w, "x")) - 1 for w in labels] != list(
        range(len(columns))
    ):
        raise ValueError(f"Header/grid disagreement on page {pdf_page.page_number}")
    ys = clustered(
        edge["top"]
        for edge in pdf_page.edges
        if abs(edge["top"] - edge["bottom"]) < 1
        and edge["width"] >= 0.9 * (xs[-1] - xs[0])
    )
    header_center = sum(word_center(w, "y") for w in labels) / len(labels)
    ys = [value for value in ys if value > header_center]
    if len(ys) < 2:
        raise ValueError(f"No body row grid on page {pdf_page.page_number}")
    return xs, ys


def parse_page(page, spec, pdf_page):
    words = [
        {
            "text": word.text or "",
            **{key: float(value) for key, value in word.attrib.items()},
        }
        for word in page.findall(".//{*}word")
    ]
    labels = header(words, spec["headers"], float(page.attrib["height"]))
    if labels is None:
        raise ValueError(
            f"Numbered column header missing on page {pdf_page.page_number}"
        )
    xs, ys = drawn_grid(pdf_page, labels, spec["columns"])
    cells = collections.defaultdict(list)
    for word in words:
        x, y = word_center(word, "x"), word_center(word, "y")
        if xs[0] <= x < xs[-1] and ys[0] <= y < ys[-1]:
            cells[
                (bisect.bisect_right(ys, y) - 1, bisect.bisect_right(xs, x) - 1)
            ].append(word)
    rows, totals, unclassified = [], [], []
    for index, (start, end) in enumerate(itertools.pairwise(ys)):
        row = {}
        for column_index, column in enumerate(spec["columns"]):
            ordered = sorted(
                cells[(index, column_index)],
                key=lambda w: (round(w["yMin"] / 3), w["xMin"]),
            )
            row[column] = " ".join(w["text"] for w in ordered)
        raw_text = " ".join(value for value in row.values() if value)
        if not raw_text:
            continue
        location = dict(
            source_row_on_page=index + 1,
            row_y_min=round(start, 3),
            row_y_max=round(end, 3),
        )
        if TOTAL_MARKER.search(raw_text):
            numbers = [word for word in raw_text.split() if word.isdigit()]
            totals.append(
                dict(
                    location,
                    label_raw=row.get("block_raw", "") or raw_text,
                    raw_text=raw_text,
                    reported_count=int(numbers[-1]) if numbers else None,
                )
            )
            continue
        if not row["printed_serial"].isdigit():
            unclassified.append(dict(location, raw_text=raw_text))
            continue
        flags = ["place_names_font_encoded", "visual_review_pending"]
        category = CATEGORY.get(row["reservation_raw"])
        row["caste_reservation"], row["woman_reserved"] = category or ("", "")
        if category is None:
            flags.append("reservation_unrecognized")
        if not row.get("block_raw") or not row.get("unit_name_raw"):
            flags.append("place_cell_missing")
        row.update(
            location, quality_flags=";".join(flags), review_status="needs_review"
        )
        rows.append(row)
    return rows, {
        "status": "grid_extracted_pending_review",
        "native_words": len(words),
        "rows": len(rows),
        "columns_x": xs,
        "rows_y": ys,
        "totals": totals,
        "unclassified": unclassified,
    }


def reconcile_totals(observations, pages):
    controls = []
    for page in pages:
        for total in page["totals"]:
            label = TOTAL_MARKER.sub("", total["label_raw"]).strip()
            match_key = "".join(label.split())
            district = "tuin" in label
            matches = [
                row
                for row in observations
                if row["tier"] == page["tier"]
                and (district or "".join(row["block_raw"].split()) == match_key)
            ]
            controls.append(
                dict(
                    tier=page["tier"],
                    source_page=page["source_page"],
                    scope="district" if district else "block",
                    block_raw="" if district else label,
                    label_raw=total["label_raw"],
                    block_match_key="" if district else match_key,
                    matching_rule="whitespace_insensitive_total_label_only",
                    reported_count=total["reported_count"],
                    extracted_count=len(matches),
                    matches=total["reported_count"] == len(matches),
                )
            )
    sequences = []
    grouped = collections.defaultdict(list)
    for row in observations:
        key = (
            row["tier"],
            "" if row["tier"] == "district_member" else row["block_raw"],
        )
        grouped[key].append(int(row["printed_serial"]))
    for (tier, block), serials in sorted(grouped.items()):
        sequences.append(
            dict(
                tier=tier,
                block_raw=block,
                rows=len(serials),
                contiguous_from_one=sorted(serials) == list(range(1, len(serials) + 1)),
            )
        )
    return controls, sequences


def annotate_source_numbers(observations):
    """Flag repeated samiti printed numbers without asserting ward identities."""
    grouped = collections.defaultdict(list)
    for row in observations:
        if row["tier"] == "block_member" and row["block_raw"]:
            key = (row["source_sha256"], row["block_raw"], row["printed_serial"])
            grouped[key].append(row)
    annotations = {}
    for key, rows in grouped.items():
        if len(rows) < 2:
            continue
        flags = ["source_printed_number_duplicate"]
        categories = set()
        named_categories = collections.defaultdict(set)
        names = set()
        for row in rows:
            name = row["unit_name_raw"]
            if name:
                names.add(name)
            if row["caste_reservation"] and row["woman_reserved"] != "":
                category = (row["caste_reservation"], row["woman_reserved"])
                categories.add(category)
                if name:
                    named_categories[name].add(category)
        if len(names) > 1:
            flags.append("source_printed_number_multiple_names")
        if len(categories) > 1:
            flags.append("source_printed_number_multiple_categories")
        if any(len(values) > 1 for values in named_categories.values()):
            flags.append("source_printed_number_same_name_category_conflict")
        annotations[key] = flags
    issues = []
    for row in observations:
        if row["tier"] != "block_member" or not row["block_raw"]:
            continue
        key = (row["source_sha256"], row["block_raw"], row["printed_serial"])
        if key not in annotations:
            continue
        existing = [flag for flag in row["quality_flags"].split(";") if flag]
        row["quality_flags"] = ";".join(dict.fromkeys(existing + annotations[key]))
        issues.append(row)
    return issues


def write_csv(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    args.root = args.root.resolve()
    args.out = (
        args.out or args.root / "data/interim/sitapur_reservations_2010_grid_v3"
    ).resolve()
    args.out.mkdir(parents=True)
    extraction_dir = args.out / "native_text"
    extraction_dir.mkdir(exist_ok=True)
    observations, pages, inputs = [], [], []
    for spec in SOURCES:
        path = args.root / BASE / spec["path"]
        if sha256(path) != spec["sha256"]:
            raise ValueError(f"Source hash mismatch: {path}")
        extraction = extraction_dir / f"{spec['tier']}.xhtml.gz"
        command = ["pdftotext", "-bbox-layout", str(path), "-"]
        result = subprocess.run(command, check=True, capture_output=True)
        extraction.write_bytes(gzip.compress(result.stdout, compresslevel=6, mtime=0))
        extraction_hash = hashlib.sha256(result.stdout).hexdigest()
        document = ET.fromstring(result.stdout)
        source_pages = document.findall(".//{*}page")
        inputs.append(
            dict(spec, pages=len(source_pages), extraction_sha256=extraction_hash)
        )
        with pdfplumber.open(path) as pdf:
            geometry = list(pdf.pages)
            page_results = [
                parse_page(page, spec, geometry[i])
                for i, page in enumerate(source_pages)
            ]
        for page_no, (rows, profile) in enumerate(page_results, 1):
            pages.append(dict(tier=spec["tier"], source_page=page_no, **profile))
            for row in rows:
                locator = f"{spec['sha256']}:{page_no}:{row['source_row_on_page']}"
                row.update(
                    observation_id=hashlib.sha256(locator.encode()).hexdigest()[:24],
                    state="Uttar Pradesh",
                    district="Sitapur",
                    year=2010,
                    tier=spec["tier"],
                    source_path=str(BASE / spec["path"]),
                    source_sha256=spec["sha256"],
                    source_url=spec["url"],
                    wayback_timestamp=spec["capture"],
                    source_page=page_no,
                    extraction_path=str(
                        extraction.relative_to(args.root)
                        if extraction.is_relative_to(args.root)
                        else extraction
                    ),
                    extraction_sha256=extraction_hash,
                )
                observations.append(row)
    flagged = [
        r
        for r in observations
        if r["quality_flags"] != "place_names_font_encoded;visual_review_pending"
    ]
    write_csv(args.out / "extraction_issues.csv", flagged, FIELDS)
    source_number_issues = annotate_source_numbers(observations)
    write_csv(args.out / "reservation_observations.csv", observations, FIELDS)
    write_csv(args.out / "source_number_issues.csv", source_number_issues, FIELDS)
    controls, sequences = reconcile_totals(observations, pages)
    write_csv(
        args.out / "printed_total_checks.csv",
        controls,
        [
            "tier",
            "source_page",
            "scope",
            "block_raw",
            "label_raw",
            "block_match_key",
            "matching_rule",
            "reported_count",
            "extracted_count",
            "matches",
        ],
    )
    write_csv(
        args.out / "serial_sequence_checks.csv",
        sequences,
        ["tier", "block_raw", "rows", "contiguous_from_one"],
    )
    summary = {
        "status": "research_observations_not_release_data",
        "method": "pdftotext_native_words_with_pdf_drawn_grid",
        "paid_inference_usd": 0,
        "rows": len(observations),
        "rows_with_extraction_issues": len(flagged),
        "source_number_issue_rows": len(source_number_issues),
        "source_number_issue_counts": dict(
            collections.Counter(
                flag
                for row in source_number_issues
                for flag in row["quality_flags"].split(";")
                if flag.startswith("source_printed_number_")
            )
        ),
        "distinct_block_member_source_number_keys": len(
            {
                (row["source_sha256"], row["block_raw"], row["printed_serial"])
                for row in observations
                if row["tier"] == "block_member"
            }
        ),
        "source_number_key_policy": (
            "Exact source PDF, encoded block label, and printed-number token; "
            "not a verified ward identifier. No deduplication or renumbering."
        ),
        "rows_by_tier": dict(collections.Counter(r["tier"] for r in observations)),
        "page_statuses": dict(collections.Counter(p["status"] for p in pages)),
        "printed_total_checks": controls,
        "serial_sequence_checks": sequences,
        "all_printed_totals_match": bool(controls)
        and all(c["matches"] for c in controls),
        "all_serial_sequences_complete": all(
            c["contiguous_from_one"] for c in sequences
        ),
        "unclassified_grid_rows": sum(len(page["unclassified"]) for page in pages),
        "extraction_hash_semantics": "SHA-256 of decompressed native XHTML bytes",
        "sources": inputs,
        "pages": pages,
        "parser_sha256": sha256(Path(__file__)),
        "poppler_version": subprocess.run(
            ["pdftotext", "-v"], capture_output=True, text=True, check=True
        ).stderr.strip(),
        "release_gate": (
            "Visual source comparison, encoded-name decoding, and "
            "cross-source reconciliation remain required."
        ),
    }
    (args.out / "extraction_manifest.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print(
        json.dumps(
            {
                key: summary[key]
                for key in [
                    "status",
                    "rows",
                    "rows_with_extraction_issues",
                    "source_number_issue_rows",
                    "source_number_issue_counts",
                    "distinct_block_member_source_number_keys",
                    "rows_by_tier",
                    "page_statuses",
                    "paid_inference_usd",
                    "all_printed_totals_match",
                    "all_serial_sequences_complete",
                    "unclassified_grid_rows",
                ]
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
