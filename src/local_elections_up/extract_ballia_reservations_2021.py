"""Extract the pinned Ballia PDF into resumable, source-linked cell observations.

Run with:
uv run --with img2table==2.0.0 python scripts/extract_ballia_reservations_2021.py \
    --source-root data/recovery/ballia_media_reservations_2021 --pages 2 37 74

No API calls. Requires local Tesseract with eng and hin data. Outputs are
research staging, not canonical allocations. Numeric slots remain positional
until their page headers have been source-reviewed.
"""

import argparse
import csv
import datetime as dt
import fcntl
import gzip
import hashlib
import io
import json
import os
import re
import subprocess
import tempfile
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from importlib.metadata import version
from pathlib import Path

import cv2
import pandas as pd
from img2table.document import PDF, Image

SOURCE_SHA = "685743d6d929e860720ae655909f4659f12f5c67b356946a62e072ee79de4b16"
SOURCE_FILE = "acquisition/raw/a7cdcc048fb757b6c9e5_685743d6d929.pdf"
SOURCE_URL = "https://navbharattimes.indiatimes.com/photo/81621873.cms"
CODES = {"UR", "L", "BC", "BCL", "SC", "SCL", "ST", "STL"}
MODES = {
    "header": ("hin+eng", 6, None),
    "header_number": ("eng", 7, "0123456789"),
    "text": ("hin+eng", 7, None),
    "number": ("eng", 7, "0123456789"),
    "code": ("eng", 7, "BCLSURT"),
}
SLOTS = [f"column_{i:02d}_raw" for i in range(1, 12)]
ROW_COLUMNS = [
    "source_sha256",
    "source_url",
    "source_page",
    "printed_page",
    "table_index",
    "geometry_row_index",
    "row_kind",
    "quality_flags",
    "assignment_usable",
    *SLOTS,
]


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def packed(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True).encode()


def write_bytes(path, payload):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)
    return digest(payload)


def write_json(path, value):
    return write_bytes(path, packed(value))


def bbox(cell):
    b = cell.bbox
    return [int(b.x1), int(b.y1), int(b.x2), int(b.y2)]


def batch_ocr(mode, items, temporary, folder):
    language, psm, whitelist = MODES[mode]
    listing = temporary / f"{mode}.txt"
    listing.write_text("".join(str(item["image_file"]) + "\n" for item in items))
    command = ["tesseract", str(listing), "stdout", "-l", language, "--psm", str(psm)]
    if whitelist:
        command += ["-c", f"tessedit_char_whitelist={whitelist}"]
    command += ["tsv"]
    result = subprocess.run(
        command,
        capture_output=True,
        check=True,
        timeout=240,
        env=os.environ | {"OMP_THREAD_LIMIT": "1"},
    )
    raw = gzip.compress(result.stdout, mtime=0)
    raw_sha = write_bytes(folder / f"{mode}.tsv.gz", raw)
    write_bytes(folder / f"{mode}.stderr.log", result.stderr)
    words = defaultdict(list)
    seen = set()
    for row in csv.DictReader(
        io.StringIO(result.stdout.decode()), delimiter="\t", quoting=csv.QUOTE_NONE
    ):
        number = int(row["page_num"])
        if row["level"] == "1":
            seen.add(number)
        if row["level"] == "5" and row["text"].strip():
            words[number].append(row)
    if seen != set(range(1, len(items) + 1)):
        raise ValueError(f"{mode}: image/TSV page mapping is incomplete")
    output = {}
    for number, item in enumerate(items, 1):
        output[item["key"]] = {
            "text_raw": " ".join(row["text"] for row in words[number]),
            "words": words[number],
            "batch_image_index": number,
            "batch_file": f"{mode}.tsv.gz",
            "batch_sha256": raw_sha,
            "mode": mode,
            "crop_sha256": item["crop_sha256"],
        }
    return output


def find_tables(document):
    detected = document.extract_tables(
        ocr=None,
        implicit_rows=False,
        implicit_columns=False,
        borderless_tables=False,
        min_confidence=1,
    )
    if isinstance(detected, dict):
        return [table for found in detected.values() for table in found]
    return detected


def supported_table(table, column_count=11):
    rows = list(table.content.values())
    return len(rows) >= 4 and all(len(row) == column_count for row in rows)


def recover_table(document, tables, column_count=11):
    original = cv2.cvtColor(document.images[0], cv2.COLOR_RGB2GRAY)
    evidence = {
        "method": "original_page_raster",
        "source_raster_gray_pixels_sha256": digest(original.tobytes()),
        "source_raster_shape": list(original.shape),
        "coordinate_frame": "original_200_dpi_page_raster_pixels",
    }
    height, width = original.shape
    mask = cv2.threshold(original, 200, 255, cv2.THRESH_BINARY_INV)[1]
    horizontal = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        cv2.getStructuringElement(cv2.MORPH_RECT, (width // 30, 1)),
    )
    vertical = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        cv2.getStructuringElement(cv2.MORPH_RECT, (1, height // 40)),
    )
    contours = cv2.findContours(
        cv2.bitwise_or(horizontal, vertical),
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )[0]
    boxes = [cv2.boundingRect(contour) for contour in contours]
    boxes = [box for box in boxes if box[2] > width * 0.5 and box[3] > 100]
    if len(boxes) != 1:
        evidence["recovery_not_applied"] = "grid_crop_absent_or_ambiguous"
        evidence["grid_candidates"] = len(boxes)
        return document, tables, evidence
    x, y, box_width, box_height = boxes[0]
    left, top = max(0, x - 20), max(0, y - 20)
    right, bottom = min(width, x + box_width + 20), min(height, y + box_height + 20)
    crop = original[top:bottom, left:right]
    ok, encoded = cv2.imencode(".png", crop)
    if not ok:
        raise ValueError("Could not encode the source grid crop")
    payload = encoded.tobytes()
    recovered = Image(src=payload, detect_rotation=True)
    recovered_tables = find_tables(recovered)
    if not any(supported_table(table, column_count) for table in recovered_tables):
        evidence["recovery_not_applied"] = "cropped_rotated_grid_unsupported"
        return document, tables, evidence
    evidence.update(
        method="table_crop_then_rotation",
        source_crop_bbox=[left, top, right, bottom],
        source_crop_png_sha256=digest(payload),
        coordinate_frame="saved_rotation_corrected_crop_raster_pixels",
        coordinate_warning=(
            "Cell boxes refer to geometry_raster.png, not directly to the PDF "
            "or unrotated source raster. Crop coordinates are recorded separately."
        ),
        raster_file="geometry_raster.png",
    )
    return recovered, recovered_tables, evidence


def extract_page(source, page, out, signature, layouts, workers):
    folder = out / f"page_{page:04d}"
    folder.mkdir(exist_ok=True)
    receipt_file = folder / "receipt.json"
    if receipt_file.exists():
        old = json.loads(receipt_file.read_text())
        if old.get("signature") != signature:
            raise ValueError("Existing page belongs to different extraction settings")
        if old.get("status") == "extracted_unvalidated":
            if all(
                digest((folder / name).read_bytes()) == sha
                for name, sha in old["outputs"].items()
            ):
                return pd.read_parquet(folder / "rows.parquet").to_dict("records"), old
            raise ValueError("Cached page changed; preserve it for investigation")

    document = PDF(
        src=source, pages=[page - 1], detect_rotation=False, pdf_text_extraction=False
    )
    document, tables, geometry_recovery = recover_table(document, find_tables(document))
    geometry = [
        {
            "table_index": i,
            "bbox": [
                int(table.bbox.x1),
                int(table.bbox.y1),
                int(table.bbox.x2),
                int(table.bbox.y2),
            ],
            "rows": [[bbox(cell) for cell in row] for row in table.content.values()],
        }
        for i, table in enumerate(tables)
    ]
    outputs = {}
    outputs["geometry.json.gz"] = write_bytes(
        folder / "geometry.json.gz", gzip.compress(packed(geometry), mtime=0)
    )
    gray = cv2.cvtColor(document.images[0], cv2.COLOR_RGB2GRAY)
    if geometry_recovery["method"] == "table_crop_then_rotation":
        ok, encoded = cv2.imencode(".png", gray)
        if not ok:
            raise ValueError("Could not preserve the geometry reference raster")
        outputs["geometry_raster.png"] = write_bytes(
            folder / "geometry_raster.png", encoded.tobytes()
        )
    locators, groups, unique = [], defaultdict(list), {}
    with tempfile.TemporaryDirectory(prefix="ballia-cells-") as temporary_name:
        temporary = Path(temporary_name)
        for table in geometry:
            ti = table["table_index"]
            rows = table["rows"]
            if len(rows) < 4 or any(len(row) != 11 for row in rows):
                continue
            for ri, row in enumerate(rows):
                for ci, box in enumerate(row):
                    mode = (
                        "header"
                        if ri < 2
                        else (
                            "number"
                            if ri == 2 or ci in {1, 4, 5, 6, 7, 8}
                            else "code"
                            if ci in {9, 10}
                            else "text"
                        )
                    )
                    key = (mode, *box)
                    if box[2] - box[0] <= 6 or box[3] - box[1] <= 6:
                        locators.append(
                            {
                                "table_index": ti,
                                "geometry_row_index": ri,
                                "column_index": ci,
                                "bbox": box,
                                "key": None,
                            }
                        )
                        continue
                    if key not in unique:
                        x1, y1, x2, y2 = box
                        crop = gray[y1 + 3 : y2 - 3, x1 + 3 : x2 - 3]
                        if crop.size == 0:
                            raise ValueError("Empty cell interior")
                        crop = cv2.copyMakeBorder(
                            crop, 8, 8, 8, 8, cv2.BORDER_CONSTANT, value=255
                        )
                        ok, encoded = cv2.imencode(".png", crop)
                        if not ok:
                            raise ValueError("Could not encode cell")
                        payload = encoded.tobytes()
                        image_file = temporary / f"cell_{len(unique):05d}.png"
                        image_file.write_bytes(payload)
                        item = {
                            "key": key,
                            "image_file": image_file,
                            "crop_sha256": digest(payload),
                        }
                        unique[key] = item
                        groups[mode].append(item)
                    locators.append(
                        {
                            "table_index": ti,
                            "geometry_row_index": ri,
                            "column_index": ci,
                            "bbox": box,
                            "key": key,
                        }
                    )
                    if ri < 8:
                        header_key = ("header_number", *box)
                        if header_key not in unique:
                            item = unique[key] | {"key": header_key}
                            unique[header_key] = item
                            groups["header_number"].append(item)
        recognized = {}
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [
                executor.submit(batch_ocr, mode, items, temporary, folder)
                for mode, items in groups.items()
            ]
            for future in futures:
                recognized.update(future.result())

    cells = []
    by_row = defaultdict(dict)
    header_by_row = defaultdict(dict)
    for locator in locators:
        if locator["key"] is None:
            result = {
                "text_raw": "",
                "words": [],
                "mode": "unreadable",
                "crop_status": "empty_cell_interior",
                "crop_sha256": None,
            }
        else:
            result = recognized[locator["key"]]
        cell = {k: v for k, v in locator.items() if k != "key"} | result
        if locator["key"] is not None and locator["geometry_row_index"] < 8:
            probe = recognized[("header_number", *locator["bbox"])]
            cell["header_number_ocr"] = probe
            header_by_row[(cell["table_index"], cell["geometry_row_index"])][
                cell["column_index"]
            ] = probe["text_raw"]
        cell.update(source_sha256=SOURCE_SHA, source_page=page)
        cells.append(cell)
        by_row[(cell["table_index"], cell["geometry_row_index"])][
            cell["column_index"]
        ] = cell["text_raw"]
    for mode in groups:
        outputs[f"{mode}.tsv.gz"] = next(
            item["batch_sha256"] for item in recognized.values() if item["mode"] == mode
        )
    outputs["cells.jsonl.gz"] = write_bytes(
        folder / "cells.jsonl.gz",
        gzip.compress(b"\n".join(packed(cell) for cell in cells) + b"\n", mtime=0),
    )
    reviewed = layouts.get(str(page))
    numbered_headers = {}
    for ti in range(len(geometry)):
        candidates = []
        for (table_index, ri), row in header_by_row.items():
            if table_index == ti and ri < 8:
                matches = sum(row.get(ci) == str(ci + 1) for ci in range(11))
                if matches >= 8:
                    candidates.append(ri)
        if len(candidates) == 1:
            numbered_headers[ti] = candidates[0]
    records = []
    for (ti, ri), row in sorted(by_row.items()):
        header_index = numbered_headers.get(ti)
        if ri <= (header_index if header_index is not None else 2):
            continue
        values = [row.get(ci, "") for ci in range(11)]
        header = header_by_row.get((ti, header_index), {})
        header_matches = sum(header.get(ci) == str(ci + 1) for ci in range(11))
        total = any("\u092f\u094b\u0917" in value for value in values[:4])
        number = values[1]
        flags = ["independent_review_pending", "names_and_boundaries_unvalidated"]
        if geometry_recovery["method"] == "table_crop_then_rotation":
            flags.append("recovered_table_geometry_requires_review")
        if not reviewed:
            flags.append("header_semantics_pending")
        if header_matches < 8:
            flags.append("column_number_header_unresolved")
        if total:
            kind = "total"
        elif (
            header_matches >= 8 and re.fullmatch(r"[0-9]+", number) and int(number) > 0
        ):
            kind = "seat_candidate"
        else:
            kind = "unresolved_row"
        if kind != "total":
            for ci in (9, 10):
                if values[ci] not in CODES:
                    flags.append(f"column_{ci + 1}_code_unresolved")
        counts = values[4:9]
        if all(re.fullmatch(r"[0-9]+", value) for value in counts):
            if int(counts[0]) != sum(map(int, counts[1:])):
                flags.append("family_count_sum_mismatch")
        else:
            flags.append("family_count_unresolved")
        records.append(
            {
                "source_sha256": SOURCE_SHA,
                "source_url": SOURCE_URL,
                "source_page": page,
                "printed_page": reviewed["printed_page"] if reviewed else None,
                "table_index": ti,
                "geometry_row_index": ri,
                "row_kind": kind,
                "quality_flags": ";".join(flags),
                "assignment_usable": False,
                **dict(zip(SLOTS, values, strict=True)),
            }
        )
    frame = pd.DataFrame(records, columns=ROW_COLUMNS)
    parquet = frame.to_parquet(index=False, compression="zstd")
    outputs["rows.parquet"] = write_bytes(folder / "rows.parquet", parquet)
    issues = []
    if any(table["table_index"] not in numbered_headers for table in geometry):
        issues.append("numbered_header_unresolved")
    if not geometry:
        issues.append("no_table_found")
    if len(geometry) != sum(
        len(table["rows"]) >= 4 and all(len(row) == 11 for row in table["rows"])
        for table in geometry
    ):
        issues.append("unsupported_table_geometry")
    if reviewed:
        count = sum(row["row_kind"] == "seat_candidate" for row in records)
        if count != reviewed["seat_rows"]:
            issues.append("reviewed_page_seat_count_disagreement")
    receipt = {
        "signature": signature,
        "source_sha256": SOURCE_SHA,
        "source_page": page,
        "status": "extracted_unvalidated",
        "table_count": len(geometry),
        "row_kinds": dict(Counter(row["row_kind"] for row in records)),
        "cells": len(cells),
        "issues": issues,
        "outputs": outputs,
        "numbered_header_rows": numbered_headers,
        "uncroppable_cells": sum(
            cell.get("crop_status") == "empty_cell_interior" for cell in cells
        ),
        "raster_dpi": 200,
        "geometry_recovery": geometry_recovery,
        "raster_shape": list(gray.shape),
        "raster_gray_pixels_sha256": digest(gray.tobytes()),
        "crop_inset_pixels": 3,
        "crop_padding_pixels": 8,
        "assignment_usable": False,
        "new_paid_api_cost_usd": 0,
    }
    write_json(receipt_file, receipt)
    return records, receipt


def numeric_code_quality(row):
    if row["row_kind"] == "header_fragment":
        return ""
    flags = []
    if row["row_kind"] == "unresolved_row":
        flags.append("row_classification_unresolved")
    reviewed = json.loads(row["source_reviewed_cells_json"])
    if row["row_kind"] != "total":
        for number in (10, 11):
            value = row[f"column_{number:02d}_value"]
            if value not in CODES:
                evidence = reviewed.get(f"column_{number:02d}_raw", {})
                if evidence.get("after") == value:
                    flags.append("source_reservation_code_literal_unmapped")
                else:
                    flags.append(f"column_{number}_code_unresolved")
    counts = [row[f"column_{number:02d}_value"] for number in range(5, 10)]
    if all(
        isinstance(value, str) and re.fullmatch(r"[0-9]+", value) for value in counts
    ):
        if int(counts[0]) != sum(map(int, counts[1:])):
            flags.append("family_count_sum_mismatch")
    else:
        flags.append("family_count_unresolved")
    return ";".join(flags)


def reconcile_cell_reviews(root, input_path, review_path, output):
    """Apply pinned visual readings while preserving raw cells and row classes."""
    import tarfile

    root = root.resolve()

    def inside(path):
        path = path.resolve()
        if not path.is_relative_to(root):
            raise ValueError("Reconciliation path escapes the source collection")
        return path

    input_path = inside(input_path)
    review_path = inside(review_path)
    output = inside(output)
    input_bytes = input_path.read_bytes()
    review_bytes = review_path.read_bytes()
    review = json.loads(review_bytes)
    if review["source_sha256"] != SOURCE_SHA:
        raise ValueError("Review belongs to a different source")
    if digest(input_bytes) != review["input_sha256"]:
        raise ValueError("Reviewed input checksum changed")
    archive_path = inside(review_path.parent / review["image_archive"])
    archive_bytes = archive_path.read_bytes()
    if digest(archive_bytes) != review["image_archive_sha256"]:
        raise ValueError("Review image archive changed")
    images = review["images"]
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
        for name, expected in images.items():
            member = archive.getmember(name)
            if not member.isfile():
                raise ValueError("Review image is not a regular archive member")
            with archive.extractfile(member) as stream:
                if digest(stream.read()) != expected:
                    raise ValueError("Review image checksum changed")
    frame = pd.read_parquet(io.BytesIO(input_bytes))
    if not frame.source_sha256.eq(SOURCE_SHA).all():
        raise ValueError("Input contains a different source")
    before = frame.copy(deep=True)
    touched = set()
    changes = []
    column_numbers = tuple(review.get("reviewed_columns", range(5, 12)))
    if column_numbers not in ((1, 2), (3, 4), (4,), (5, 6, 7, 8, 9, 10, 11)):
        raise ValueError(
            "Review must select block/ward, name/boundary, boundary-only, "
            "or numeric/code columns"
        )
    fields = {f"column_{number:02d}_value" for number in column_numbers}
    for item in review["rows"]:
        if "source_data_row" in item:
            if (
                not isinstance(item["source_data_row"], int)
                or item["source_data_row"] < 1
            ):
                raise ValueError("Manual source row must be a positive integer")
            locator = {
                "source_page": item["source_page"],
                "source_data_row": item["source_data_row"],
            }
            key = (item["source_page"], "manual", item["source_data_row"])
            mask = (
                frame.source_page.eq(item["source_page"])
                & frame.source_data_row.eq(item["source_data_row"])
                & frame.extraction_method.eq("visual_numeric_code_transcription")
                & frame.row_kind.eq("seat_candidate")
            )
        else:
            locator = {
                field: item[field]
                for field in ("source_page", "table_index", "geometry_row_index")
            }
            key = (
                item["source_page"],
                item["table_index"],
                item["geometry_row_index"],
            )
            mask = (
                frame.source_page.eq(key[0])
                & frame.table_index.eq(key[1])
                & frame.geometry_row_index.eq(key[2])
            )
        if key in touched:
            raise ValueError("Duplicate review locator")
        touched.add(key)
        indexes = frame.index[mask].tolist()
        if len(indexes) != 1:
            raise ValueError("Review locator is missing or ambiguous")
        if item["source_image"] not in images:
            raise ValueError("Review references an unverified image")
        if set(item["observed"]) != fields or set(item["expected"]) != fields:
            raise ValueError("Review must cover every selected source column")
        index = indexes[0]
        evidence = json.loads(frame.at[index, "source_reviewed_cells_json"])
        for field in sorted(fields):
            old = frame.at[index, field]
            expected = item["expected"][field]
            old = None if pd.isna(old) else old
            expected = None if pd.isna(expected) else expected
            new = item["observed"][field]
            if old != expected or not isinstance(new, str):
                raise ValueError("Review cell precondition changed")
            cell = {
                "before": old,
                "after": new,
                "source_image": item["source_image"],
                "source_image_sha256": images[item["source_image"]],
                "review_path": review_path.relative_to(root).as_posix(),
                "review_sha256": digest(review_bytes),
                "method": "visual_source_cell_reading",
                "independent_review_pending": True,
            }
            evidence[field.replace("_value", "_raw")] = cell
            if old != new:
                changes.append(locator | {"field": field, "before": old, "after": new})
            frame.at[index, field] = new
        frame.at[index, "source_reviewed_cells_json"] = json.dumps(
            evidence, ensure_ascii=False, sort_keys=True
        )
    frame["effective_numeric_code_quality_flags"] = [
        numeric_code_quality(row) for row in frame.to_dict("records")
    ]
    mutable = fields | {
        "source_reviewed_cells_json",
        "effective_numeric_code_quality_flags",
    }
    protected = [column for column in before if column not in mutable]
    pd.testing.assert_frame_equal(before[protected], frame[protected], check_exact=True)
    if frame.assignment_usable.any():
        raise ValueError("Source review cannot promote assignment usability")
    output.mkdir(parents=True, exist_ok=False)
    rows_bytes = frame.to_parquet(index=False, compression="zstd")
    queue = frame[frame.effective_numeric_code_quality_flags != ""]
    queue_bytes = queue.to_parquet(index=False, compression="zstd")
    write_bytes(output / "rows.parquet", rows_bytes)
    write_bytes(output / "numeric_code_review_queue.parquet", queue_bytes)
    receipt = {
        "status": "visual_cell_reviews_applied_not_canonical",
        "source_sha256": SOURCE_SHA,
        "input_path": input_path.relative_to(root).as_posix(),
        "input_sha256": digest(input_bytes),
        "review_path": review_path.relative_to(root).as_posix(),
        "review_sha256": digest(review_bytes),
        "script_sha256": digest(Path(__file__).read_bytes()),
        "output_path": "rows.parquet",
        "output_sha256": digest(rows_bytes),
        "output_rows": len(frame),
        "row_kinds": dict(Counter(frame.row_kind)),
        "reviewed_rows": len(touched),
        "reviewed_columns": list(column_numbers),
        "reviewed_cells": len(touched) * len(fields),
        "effective_cell_corrections": len(changes),
        "changes": changes,
        "protected_columns_preserved": len(protected),
        "raw_ocr_cells_unchanged": True,
        "numeric_code_review_queue_rows": len(queue),
        "numeric_code_review_queue_path": "numeric_code_review_queue.parquet",
        "numeric_code_review_queue_sha256": digest(queue_bytes),
        "assignment_usable": False,
        "new_paid_api_cost_usd": 0,
        "limits": [
            "Visual correction of flagged cells is not an accuracy estimate.",
            "Names, boundaries, other headers and independent review remain.",
            "Central office exports are not changed by this command.",
        ],
    }
    write_json(output / "reconciliation_receipt.json", receipt)
    return {
        "output": str(output),
        "reviewed_rows": len(touched),
        "reviewed_columns": list(column_numbers),
        "effective_cell_corrections": len(changes),
        "numeric_code_review_queue_rows": len(queue),
        "new_paid_api_cost_usd": 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pages", type=int, nargs="+", default=list(range(1, 75)))
    parser.add_argument("--workers", type=int, choices=range(1, 5), default=4)
    parser.add_argument("--reconcile-input", type=Path)
    parser.add_argument("--cell-review", type=Path)
    args = parser.parse_args()
    if args.reconcile_input is not None or args.cell_review is not None:
        if not (args.reconcile_input and args.cell_review and args.output):
            parser.error("Cell reconciliation requires input, review and output")
        result = reconcile_cell_reviews(
            args.source_root, args.reconcile_input, args.cell_review, args.output
        )
        print(json.dumps(result), flush=True)
        return
    pages = list(dict.fromkeys(args.pages))
    if any(page < 1 or page > 74 for page in pages):
        parser.error("Physical PDF page numbers must be between 1 and 74")
    root = args.source_root.resolve()
    out = (args.output or root / "cell_extraction").resolve()
    out.mkdir(parents=True, exist_ok=True)
    with (out / ".run.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        source = (root / SOURCE_FILE).read_bytes()
        if digest(source) != SOURCE_SHA:
            raise ValueError("Source SHA does not match the pinned Ballia PDF")
        layout_bytes = (root / "layout_review/layouts.json").read_bytes()
        layouts = json.loads(layout_bytes)
        if layouts["source_sha256"] != SOURCE_SHA:
            raise ValueError("Layout evidence belongs to a different source")
        settings = {
            "source_sha256": SOURCE_SHA,
            "script_sha256": digest(Path(__file__).read_bytes()),
            "layout_sha256": digest(layout_bytes),
            "img2table": version("img2table"),
            "tesseract": (
                subprocess.check_output(
                    ["tesseract", "--version"], text=True
                ).splitlines()[0]
            ),
            "modes": MODES,
            "dpi": 200,
            "table_recovery": {
                "method": "unique_grid_crop_then_img2table_rotation",
                "threshold": 200,
                "horizontal_kernel_width_fraction": 30,
                "vertical_kernel_height_fraction": 40,
                "minimum_grid_width_fraction": 0.5,
                "minimum_grid_height_pixels": 100,
                "crop_margin_pixels": 20,
                "only_without_supported_original_table": False,
                "fallback_to_original_when_recovery_unsupported": True,
            },
            "inset": 3,
            "padding": 8,
        }
        signature = digest(packed(settings))
        stamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%S%fZ")
        run = out / "runs" / stamp
        run.mkdir(parents=True)
        write_json(
            run / "manifest.json",
            {
                "settings": settings,
                "signature": signature,
                "requested_pages": pages,
                "publication_status": "provisional; no final allocation claims",
                "new_paid_api_cost_usd": 0,
            },
        )
        records, receipts = [], []
        for page in pages:
            try:
                rows, receipt = extract_page(
                    source, page, out, signature, layouts["pages"], args.workers
                )
                records.extend(rows)
            except Exception as error:
                receipt = {
                    "source_page": page,
                    "status": "failed",
                    "error": str(error),
                    "error_type": type(error).__name__,
                }
            receipts.append(receipt)
            with (run / "progress.jsonl").open("a") as stream:
                stream.write(json.dumps(receipt) + "\n")
            print(
                json.dumps(
                    {"completed": len(receipts), "requested": len(pages), **receipt}
                ),
                flush=True,
            )
        frame = pd.DataFrame(records, columns=ROW_COLUMNS)
        output_sha = write_bytes(
            run / "rows.parquet", frame.to_parquet(index=False, compression="zstd")
        )
        failed = [item for item in receipts if item["status"] == "failed"]
        summary = {
            "requested_pages": pages,
            "processed_pages": len(receipts) - len(failed),
            "failed_pages": failed,
            "row_kinds": dict(Counter(row["row_kind"] for row in records)),
            "row_count": len(records),
            "rows_sha256": output_sha,
            "receipts": receipts,
            "assignment_usable": False,
            "new_paid_api_cost_usd": 0,
            "scope": (
                "Raw staged observations; no name linking or accepted allocations."
            ),
        }
        write_json(run / "summary.json", summary)
        write_json(out / "latest_run.json", {"run": str(run.relative_to(out))})
        print(
            json.dumps(
                {
                    "run": str(run),
                    "processed_pages": summary["processed_pages"],
                    "row_kinds": summary["row_kinds"],
                    "failed_pages": failed,
                    "new_paid_api_cost_usd": 0,
                }
            ),
            flush=True,
        )
        if failed:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
