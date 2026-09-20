"""Extract source-coordinate-preserving cells from Kanpur Dehat's scanned grids."""

import argparse
import csv
import fcntl
import gzip
import hashlib
import io
import json
import os
import re
import subprocess
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

CATEGORY_COLUMNS = ("STW", "ST", "SCW", "SC", "BCW", "BC", "URW", "UR")


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


def command(args):
    return subprocess.run(
        args,
        check=True,
        capture_output=True,
        text=True,
        timeout=180,
        env=dict(os.environ, OMP_THREAD_LIMIT="1"),
    )


def ink(image):
    return cv2.adaptiveThreshold(
        image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 15
    )


def clusters(indices):
    groups = []
    for index in indices:
        if groups and index - groups[-1][-1] <= 5:
            groups[-1].append(int(index))
        else:
            groups.append([int(index)])
    return [int(np.median(group)) for group in groups]


def boundaries(scores, extent, threshold):
    found = clusters(np.flatnonzero(scores > threshold))
    found = [value for value in found if 10 < value < extent - 11]
    return [0, *found, extent - 1]


def ruled_table_corners(binary, contour):
    x, y, width, height = cv2.boundingRect(contour)
    mask = np.zeros_like(binary)
    cv2.drawContours(mask, [contour], -1, 255, cv2.FILLED)
    pixels = cv2.bitwise_and(binary, mask)
    lines = cv2.HoughLinesP(
        pixels,
        1,
        np.pi / 1800,
        threshold=80,
        minLineLength=max(80, min(width, height) // 3),
        maxLineGap=max(12, width // 100),
    )
    if lines is None:
        raise ValueError("No sufficiently long ruled lines")
    horizontal, vertical = [], []
    center_x, center_y = x + width / 2, y + height / 2
    for x1, y1, x2, y2 in lines.reshape(-1, 4).astype(float):
        dx, dy = x2 - x1, y2 - y1
        equation = np.array([y1 - y2, x2 - x1, x1 * y2 - x2 * y1])
        if abs(dx) > width * 0.55 and abs(dy) < abs(dx) * 0.15:
            horizontal.append((y1 + (center_x - x1) * dy / dx, equation))
        if abs(dy) > height * 0.55 and abs(dx) < abs(dy) * 0.15:
            vertical.append((x1 + (center_y - y1) * dx / dy, equation))
    if len(horizontal) < 2 or len(vertical) < 2:
        raise ValueError("Insufficient long horizontal or vertical borders")
    top, bottom = (
        min(horizontal, key=lambda item: item[0]),
        max(horizontal, key=lambda item: item[0]),
    )
    left, right = (
        min(vertical, key=lambda item: item[0]),
        max(vertical, key=lambda item: item[0]),
    )
    if bottom[0] - top[0] < height * 0.65 or right[0] - left[0] < width * 0.80:
        raise ValueError("Ruled borders do not enclose most of the detected table")
    corners = []
    for first, second in ((top, left), (top, right), (bottom, right), (bottom, left)):
        point = np.cross(first[1], second[1])
        if abs(point[2]) < 1e-6:
            raise ValueError("Parallel borders cannot define a table corner")
        corners.append(point[:2] / point[2])
    quad = np.float32(corners)
    if (
        np.any(quad[:, 0] < x - 20)
        or np.any(quad[:, 0] > x + width + 20)
        or np.any(quad[:, 1] < y - 20)
        or np.any(quad[:, 1] > y + height + 20)
        or not cv2.isContourConvex(quad.reshape(4, 1, 2))
    ):
        raise ValueError("Extrapolated ruled corners leave the source table region")
    return quad


def table_grid(upright):
    binary = ink(upright)
    connected = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    contours, _ = cv2.findContours(connected, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    candidates = []
    for contour in contours:
        if cv2.contourArea(contour) < upright.size * 0.08:
            continue
        polygon = cv2.approxPolyDP(contour, cv2.arcLength(contour, True) * 0.015, True)
        if len(polygon) == 4 and cv2.isContourConvex(polygon):
            candidates.append((cv2.contourArea(contour), polygon.reshape(4, 2)))
    corner_method = "closed_quadrilateral"
    if candidates:
        _, points = max(candidates, key=lambda item: item[0])
        sums = points.sum(axis=1)
        differences = points[:, 0] - points[:, 1]
        quad = np.float32(
            [
                points[sums.argmin()],
                points[differences.argmax()],
                points[sums.argmax()],
                points[differences.argmin()],
            ]
        )
    else:
        if not contours:
            raise ValueError("No source contours found")
        contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(contour) < upright.size * 0.08:
            raise ValueError("No sufficiently large table component")
        quad = ruled_table_corners(binary, contour)
        corner_method = "intersections_of_long_ruled_borders"
    if len({tuple(point) for point in quad}) != 4:
        raise ValueError("Ambiguous table corners")
    width = round(
        max(np.linalg.norm(quad[1] - quad[0]), np.linalg.norm(quad[2] - quad[3]))
    )
    height = round(
        max(np.linalg.norm(quad[3] - quad[0]), np.linalg.norm(quad[2] - quad[1]))
    )
    if width < upright.shape[1] * 0.65 or height < 120:
        raise ValueError("Detected contour is not a full-width table")
    target = np.float32(
        [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]]
    )
    transform = cv2.getPerspectiveTransform(quad, target)
    image = cv2.warpPerspective(
        upright, transform, (width, height), flags=cv2.INTER_CUBIC, borderValue=255
    )
    binary = ink(image)
    horizontal = cv2.morphologyEx(
        binary,
        cv2.MORPH_OPEN,
        cv2.getStructuringElement(cv2.MORPH_RECT, (max(80, width // 8), 1)),
    )
    vertical = cv2.morphologyEx(
        binary,
        cv2.MORPH_OPEN,
        cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(50, height // 8))),
    )
    horizontal = cv2.dilate(horizontal, np.ones((3, 1), np.uint8))
    vertical = cv2.dilate(vertical, np.ones((1, 3), np.uint8))
    xs = boundaries((vertical > 0).sum(axis=0), width, height * 0.40)
    ys = boundaries((horizontal > 0).sum(axis=1), height, width * 0.65)
    geometry = dict(
        corner_method=corner_method,
        table_quad_upright_pixels=quad.tolist(),
        upright_to_grid=transform.tolist(),
        grid_to_upright=np.linalg.inv(transform).tolist(),
        grid_dimensions=[width, height],
        x_boundaries=xs,
        y_boundaries=ys,
    )
    if len(xs) != 14:
        raise ValueError(
            f"Expected 13 physical columns, found {len(xs) - 1};"
            f" geometry={json.dumps(geometry)}"
        )
    if len(ys) < 3 or any(np.diff(xs) < 25) or any(np.diff(ys) < 15):
        raise ValueError(
            f"Unreliable row or column boundaries; geometry={json.dumps(geometry)}"
        )
    return image, geometry


def numeric(raw):
    return int(raw) if re.fullmatch(r"[0-9]{1,3}", raw.strip()) else None


def lexical(raw):
    return any(character.isalpha() for character in raw)


def page_cells(source, page, orientation, orientation_path, root, out, method):
    label = f"{source['source_sha256']}-p{page:04d}"
    destination = out / label
    destination.mkdir(exist_ok=True)
    receipt_path = destination / "receipt.json"
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        if receipt["method_sha256"] != method:
            raise ValueError("Cached method changed; select a new output directory")
        for name, expected in receipt.get("artifacts", {}).items():
            if digest(destination / name) != expected:
                raise ValueError(f"Cached artifact changed: {label}/{name}")
        return receipt
    provenance = dict(
        source,
        source_page=page,
        method_sha256=method,
        orientation_receipt_sha256=digest(orientation_path),
        clockwise_rotation_degrees=orientation["clockwise_rotation_degrees"],
    )
    with tempfile.TemporaryDirectory(prefix="up-grid-cells-") as directory:
        temporary = Path(directory)
        render = temporary / "render"
        command(
            [
                "pdftoppm",
                "-f",
                str(page),
                "-l",
                str(page),
                "-singlefile",
                "-scale-to",
                "4000",
                "-gray",
                "-png",
                str(root / source["source_path"]),
                str(render),
            ]
        )
        original = cv2.imread(str(render.with_suffix(".png")), cv2.IMREAD_GRAYSCALE)
        if original is None:
            raise ValueError("Rendered source image could not be decoded")
        rotation = provenance["clockwise_rotation_degrees"]
        if rotation not in (0, 90, 180, 270):
            raise ValueError("Invalid source orientation")
        upright = np.rot90(original, k=(-rotation // 90) % 4).copy()
        provenance["original_dimensions"] = [original.shape[1], original.shape[0]]
        provenance["upright_dimensions"] = [upright.shape[1], upright.shape[0]]
        try:
            image, geometry = table_grid(upright)
        except ValueError as error:
            receipt = dict(
                provenance,
                status="held_grid_geometry",
                reason=str(error),
                paid_inference_usd=0,
            )
            save(receipt_path, receipt)
            return receipt
        geometry.update(provenance)
        save(destination / "geometry.json", geometry)
        xs, ys = geometry["x_boundaries"], geometry["y_boundaries"]
        cells = []
        artifacts = {"geometry.json": digest(destination / "geometry.json")}
        bands = len(ys) - 1
        slot_height = max(np.diff(ys)) + 24
        for column in range(13):
            width = xs[column + 1] - xs[column]
            atlas = np.full((int(slot_height * bands), width + 24), 255, np.uint8)
            column_cells = []
            for row in range(bands):
                x0, x1, y0, y1 = (
                    xs[column] + 6,
                    xs[column + 1] - 6,
                    ys[row] + 6,
                    ys[row + 1] - 6,
                )
                crop = image[y0:y1, x0:x1]
                top = int(row * slot_height + 12)
                atlas[top : top + crop.shape[0], 12 : 12 + crop.shape[1]] = crop
                corners = np.float32([[[x0, y0], [x1, y0], [x1, y1], [x0, y1]]])
                source_quad = cv2.perspectiveTransform(
                    corners, np.array(geometry["grid_to_upright"])
                ).tolist()[0]
                column_cells.append(
                    dict(
                        source_sha256=source["source_sha256"],
                        source_page=page,
                        block=source["block"],
                        grid_row=row + 1,
                        physical_column=column + 1,
                        grid_bbox=[x0, y0, x1, y1],
                        source_quad_upright=source_quad,
                        atlas_origin=[12, top],
                        raw_text="",
                        word_evidence=[],
                    )
                )
            atlas_path = temporary / f"column_{column + 1:02d}.png"
            if not cv2.imwrite(str(atlas_path), atlas):
                raise OSError("Could not write OCR atlas")
            arguments = [
                "tesseract",
                str(atlas_path),
                "stdout",
                "-l",
                "eng" if column in (0, 2) else "hin+eng",
                "--psm",
                "6",
            ]
            if column in (0, 2):
                arguments += ["-c", "tessedit_char_whitelist=0123456789"]
            arguments += ["tsv"]
            output = command(arguments)
            name = f"column_{column + 1:02d}.tsv.gz"
            (destination / name).write_bytes(
                gzip.compress(output.stdout.encode(), compresslevel=6, mtime=0)
            )
            artifacts[name] = digest(destination / name)
            for word in csv.DictReader(io.StringIO(output.stdout), delimiter="\t"):
                if word["level"] != "5" or not word["text"].strip():
                    continue
                center = int(word["top"]) + int(word["height"]) / 2
                row = int(center // slot_height)
                if not 0 <= row < bands:
                    raise ValueError("OCR word outside cell atlas")
                column_cells[row]["word_evidence"].append(dict(word))
            for cell in column_cells:
                cell["raw_text"] = " ".join(
                    word["text"] for word in cell["word_evidence"]
                )
                cell["word_evidence"] = json.dumps(
                    cell["word_evidence"], ensure_ascii=False
                )
            cells.extend(column_cells)
        rows = []
        indexed = {(cell["grid_row"], cell["physical_column"]): cell for cell in cells}
        for row in range(1, bands + 1):
            raw = [indexed[(row, col)]["raw_text"] for col in range(1, 14)]
            serial, ward = numeric(raw[0]), numeric(raw[2])
            category_cells = [
                index for index, value in enumerate(raw[5:]) if lexical(value)
            ]
            plausible = (
                serial is not None
                and ward is not None
                and lexical(raw[1])
                and lexical(raw[3])
            )
            flags = []
            if not plausible:
                flags.append("row_identity_unresolved_or_header")
            if len(category_cells) != 1:
                flags.append("category_column_unresolved")
            category = (
                CATEGORY_COLUMNS[category_cells[0]]
                if plausible and len(category_cells) == 1
                else None
            )
            rows.append(
                dict(
                    source_sha256=source["source_sha256"],
                    source_page=page,
                    source_url=source["source_url"],
                    block=source["block"],
                    grid_row=row,
                    printed_serial=serial,
                    ward=ward,
                    gram_panchayats_raw=raw[1],
                    territorial_ward_name_raw=raw[3],
                    boundary_description_raw=raw[4],
                    category_candidate=category,
                    category_assignment="physical column; source review required",
                    category_cells_raw=json.dumps(raw[5:], ensure_ascii=False),
                    woman_reserved_candidate=(
                        category.endswith("W") if category else None
                    ),
                    row_kind=(
                        "candidate_seat" if plausible else "unclassified_grid_band"
                    ),
                    quality_flags=";".join(flags),
                    review_status="research staging; not source-certified",
                )
            )
        for name, records in [
            ("source_cells.parquet", cells),
            ("reservation_rows.parquet", rows),
        ]:
            pd.DataFrame.from_records(records).to_parquet(
                destination / name, index=False
            )
            artifacts[name] = digest(destination / name)
        receipt = dict(
            provenance,
            status="grid_cells_extracted",
            cells=len(cells),
            bands=bands,
            candidate_rows=sum(row["row_kind"] == "candidate_seat" for row in rows),
            candidate_categories=sum(
                row["category_candidate"] is not None for row in rows
            ),
            artifacts=artifacts,
            paid_inference_usd=0,
            quality_status="accuracy not established",
        )
        save(receipt_path, receipt)
        return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--orientation-dir", type=Path, action="append", required=True)
    parser.add_argument(
        "--page-list",
        type=Path,
        required=True,
        help="JSON list or object keyed by source SHA and one-based page ID",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, choices=range(1, 9), default=4)
    args = parser.parse_args()
    cv2.setNumThreads(1)
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / "run.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with args.manifest.open(newline="") as stream:
            sources = {row["source_sha256"]: row for row in csv.DictReader(stream)}
        requested = list(json.loads(args.page_list.read_text()))
        work = []
        source_checked = set()
        for label in requested:
            match = re.fullmatch(r"([0-9a-f]{64})-p([0-9]{4})", label)
            if not match or match[1] not in sources:
                raise ValueError(f"Unknown requested page: {label}")
            source, page = sources[match[1]], int(match[2])
            if not 1 <= page <= int(source["pages"]):
                raise ValueError("Requested page exceeds source page count")
            if match[1] not in source_checked:
                if digest(args.root / source["source_path"]) != match[1]:
                    raise ValueError("Source PDF hash mismatch")
                source_checked.add(match[1])
            choices = []
            for folder in args.orientation_dir:
                path = folder / f"{label}.json"
                if path.exists():
                    receipt = json.loads(path.read_text())
                    if receipt.get("status") == "ocr_cached_not_structured":
                        if (
                            receipt["source_sha256"] != match[1]
                            or receipt["source_page"] != page
                        ):
                            raise ValueError("Orientation receipt identity mismatch")
                        choices.append((receipt, path))
            if (
                not choices
                or len({item[0]["clockwise_rotation_degrees"] for item in choices}) != 1
            ):
                raise ValueError(f"No unambiguous approved orientation for {label}")
            orientation, path = choices[-1]
            work.append((source, page, orientation, path))
        method = dict(
            script_sha256=digest(Path(__file__)),
            opencv=cv2.__version__,
            numpy=np.__version__,
            pandas=pd.__version__,
            manifest_sha256=digest(args.manifest),
            page_list_sha256=digest(args.page_list),
            orientation_receipts={path.name: digest(path) for _, _, _, path in work},
            tesseract=command(["tesseract", "--version"]).stdout.splitlines()[0],
            pdftoppm=command(["pdftoppm", "-v"]).stderr.splitlines()[0],
            traineddata_sha256={
                lang: digest(
                    Path("/opt/homebrew/share/tessdata") / f"{lang}.traineddata"
                )
                for lang in ("hin", "eng")
            },
            source_coordinates=(
                "upright 4000-long-edge render; inverse homography retained"
            ),
            quality_status="research staging; candidate categories are not certified",
        )
        identity = hashlib.sha256(
            json.dumps(method, sort_keys=True).encode()
        ).hexdigest()
        plan_path = args.output / "extraction_plan.json"
        if (
            plan_path.exists()
            and json.loads(plan_path.read_text())["method_sha256"] != identity
        ):
            raise ValueError("Output method changed; choose a new output directory")
        save(plan_path, dict(method=method, method_sha256=identity, pages=requested))
        statuses = Counter()
        receipts = []
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            jobs = {
                pool.submit(
                    page_cells,
                    source,
                    page,
                    orientation,
                    path,
                    args.root,
                    args.output,
                    identity,
                ): (source, page)
                for source, page, orientation, path in work
            }
            for future in as_completed(jobs):
                source, page = jobs[future]
                try:
                    receipt = future.result()
                except Exception as error:
                    receipt = dict(
                        status="failed",
                        source_sha256=source["source_sha256"],
                        source_page=page,
                        block=source["block"],
                        error=str(error),
                    )
                    save(
                        args.output
                        / f"{source['source_sha256']}-p{page:04d}.error.json",
                        receipt,
                    )
                receipts.append(receipt)
                statuses[receipt["status"]] += 1
                print(
                    json.dumps(
                        {
                            key: receipt[key]
                            for key in (
                                "status",
                                "block",
                                "source_page",
                                "cells",
                                "candidate_rows",
                                "candidate_categories",
                                "reason",
                                "error",
                            )
                            if key in receipt
                        }
                    ),
                    flush=True,
                )
        summary = dict(
            pages_requested=len(work),
            statuses=dict(statuses),
            cells=sum(receipt.get("cells", 0) for receipt in receipts),
            candidate_rows=sum(
                receipt.get("candidate_rows", 0) for receipt in receipts
            ),
            paid_inference_usd=0,
            quality_status="accuracy not established",
        )
        save(args.output / "extraction_summary.json", summary)
        print(json.dumps(summary), flush=True)
        return int(bool(statuses["failed"] or statuses["held_grid_geometry"]))


if __name__ == "__main__":
    raise SystemExit(main())
