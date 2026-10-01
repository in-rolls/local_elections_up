"""Cache orientation-aware local OCR, preserving source hashes and coordinates."""

import argparse
import csv
import fcntl
import gzip
import hashlib
import json
import os
import re
import subprocess
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PIL import Image


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(path)


def run(command):
    return subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
        timeout=180,
        env=dict(os.environ, OMP_THREAD_LIMIT="1"),
    )


def extract(source, page, root, out, method, overrides):
    label = f"{source['source_sha256']}-p{page:04d}"
    override = overrides.get(label)
    receipt_path = out / f"{label}.json"
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        if receipt["method_sha256"] != method:
            raise ValueError(f"Method changed for {label}; use a new output directory")
        for artifact in receipt.get("artifacts", []):
            if sha256(out / artifact["path"]) != artifact["sha256"]:
                raise ValueError(f"Cached artifact changed: {artifact['path']}")
        return receipt
    receipt = dict(
        source,
        source_page=page,
        method_sha256=method,
        paid_inference_usd=0,
        structured_accuracy="not established",
    )
    with tempfile.TemporaryDirectory(prefix="up-oriented-ocr-") as directory:
        base = Path(directory)
        render = base / "render"
        run(
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
        rendered = render.with_suffix(".png")
        receipt["original_render_sha256"] = sha256(rendered)
        osd = subprocess.run(
            ["tesseract", str(rendered), "stdout", "--psm", "0", "-l", "osd"],
            capture_output=True,
            text=True,
            timeout=180,
            env=dict(os.environ, OMP_THREAD_LIMIT="1"),
        )
        receipt["orientation_detection"] = {
            "stdout": osd.stdout,
            "stderr": osd.stderr,
            "returncode": osd.returncode,
        }
        rotation = re.search(r"^Rotate:\s*(\d+)\s*$", osd.stdout, re.MULTILINE)
        confidence = re.search(
            r"^Orientation confidence:\s*([\d.]+)", osd.stdout, re.MULTILINE
        )
        if override is None and (
            osd.returncode
            or not rotation
            or not confidence
            or int(rotation[1]) not in (0, 90, 180, 270)
            or float(confidence[1]) < 5
        ):
            receipt["status"] = "held_orientation_uncertain"
            save(receipt_path, receipt)
            return receipt
        degrees = (
            override["clockwise_rotation_degrees"] if override else int(rotation[1])
        )
        receipt["clockwise_rotation_degrees"] = degrees
        receipt["orientation_confidence"] = float(confidence[1]) if confidence else None
        receipt["orientation_override"] = override
        upright = base / "upright.png"
        with Image.open(rendered) as original:
            receipt["original_dimensions"] = list(original.size)
            transforms = {
                90: Image.Transpose.ROTATE_270,
                180: Image.Transpose.ROTATE_180,
                270: Image.Transpose.ROTATE_90,
            }
            corrected = original.transpose(transforms[degrees]) if degrees else original
            receipt["upright_dimensions"] = list(corrected.size)
            corrected.save(upright)
        receipt["upright_render_sha256"] = sha256(upright)
        receipt["coordinate_frame"] = "upright image pixels, origin top left"
        prefix = base / "text"
        result = run(
            [
                "tesseract",
                str(upright),
                str(prefix),
                "-l",
                "hin+eng",
                "--psm",
                "6",
                "txt",
                "tsv",
                "hocr",
            ]
        )
        receipt["ocr_stderr"] = result.stderr
        receipt["artifacts"] = []
        for suffix in ("txt", "tsv", "hocr"):
            raw = prefix.with_suffix("." + suffix).read_bytes()
            artifact = out / f"{label}.{suffix}.gz"
            artifact.write_bytes(gzip.compress(raw, compresslevel=6, mtime=0))
            receipt["artifacts"].append(
                {
                    "path": artifact.name,
                    "sha256": sha256(artifact),
                    "uncompressed_sha256": hashlib.sha256(raw).hexdigest(),
                    "uncompressed_bytes": len(raw),
                }
            )
        receipt["status"] = "ocr_cached_not_structured"
        save(receipt_path, receipt)
        return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, choices=range(1, 9), default=4)
    parser.add_argument("--orientation-overrides", type=Path)
    parser.add_argument("--only-reviewed", action="store_true")
    args = parser.parse_args()
    if args.only_reviewed and not args.orientation_overrides:
        parser.error("--only-reviewed requires --orientation-overrides")
    overrides = (
        json.loads(args.orientation_overrides.read_text())
        if args.orientation_overrides
        else {}
    )
    for label, override in overrides.items():
        if override.get("clockwise_rotation_degrees") not in (
            0,
            90,
            180,
            270,
        ) or not override.get("evidence"):
            raise ValueError(f"Invalid reviewed orientation: {label}")
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / "run.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with args.manifest.open(newline="") as stream:
            sources = list(csv.DictReader(stream))
        page_ids = {
            f"{source['source_sha256']}-p{page:04d}"
            for source in sources
            for page in range(1, int(source["pages"]) + 1)
        }
        if set(overrides) - page_ids:
            raise ValueError(
                "Orientation review includes a page outside the source frame"
            )
        for source in sources:
            if sha256(args.root / source["source_path"]) != source["source_sha256"]:
                raise ValueError(f"Source changed: {source['source_path']}")
        tessdata = Path("/opt/homebrew/share/tessdata")
        method = {
            "script_sha256": sha256(Path(__file__)),
            "manifest_sha256": sha256(args.manifest),
            "orientation_overrides_sha256": (
                sha256(args.orientation_overrides)
                if args.orientation_overrides
                else None
            ),
            "only_reviewed": args.only_reviewed,
            "tesseract_version": run(["tesseract", "--version"]).stdout.splitlines()[0],
            "pdftoppm_version": run(["pdftoppm", "-v"]).stderr.splitlines()[0],
            "traineddata_sha256": {
                language: sha256(tessdata / f"{language}.traineddata")
                for language in ("hin", "eng", "osd")
            },
            "render": {"long_edge": 4000, "grayscale": True, "format": "png"},
            "orientation": {
                "psm": 0,
                "minimum_confidence": 5,
                "correction": "lossless quarter-turn transpose",
            },
            "ocr": {"languages": "hin+eng", "psm": 6, "threads_per_worker": 1},
            "paid_inference_usd": 0,
            "quality_status": "raw OCR cache only; source accuracy not established",
        }
        identity = hashlib.sha256(
            json.dumps(method, sort_keys=True).encode()
        ).hexdigest()
        plan_path = args.output / "ocr_plan.json"
        if (
            plan_path.exists()
            and json.loads(plan_path.read_text())["method_sha256"] != identity
        ):
            raise ValueError(
                "Output belongs to a different method; choose a new directory"
            )
        save(plan_path, dict(method=method, method_sha256=identity, sources=sources))
        statuses = Counter()
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            jobs = {
                pool.submit(
                    extract, source, page, args.root, args.output, identity, overrides
                ): (source, page)
                for source in sources
                for page in range(1, int(source["pages"]) + 1)
                if not args.only_reviewed
                or f"{source['source_sha256']}-p{page:04d}" in overrides
            }
            for future in as_completed(jobs):
                source, page = jobs[future]
                try:
                    receipt = future.result()
                    status = receipt["status"]
                    event = {
                        key: receipt.get(key)
                        for key in (
                            "status",
                            "block",
                            "source_page",
                            "clockwise_rotation_degrees",
                            "orientation_confidence",
                        )
                    }
                except Exception as error:
                    status = "failed"
                    event = {
                        "status": status,
                        "block": source["block"],
                        "source_page": page,
                        "error": str(error),
                    }
                    save(
                        args.output
                        / f"{source['source_sha256']}-p{page:04d}.error.json",
                        event,
                    )
                statuses[status] += 1
                print(
                    json.dumps(dict(event, completed=sum(statuses.values()))),
                    flush=True,
                )
        summary = dict(
            pages_in_frame=len(jobs),
            statuses=dict(statuses),
            paid_inference_usd=0,
            method_sha256=identity,
            structured_accuracy="not established",
        )
        save(args.output / "run_status.json", summary)
        print(json.dumps(summary), flush=True)
        return int(bool(statuses["failed"] or statuses["held_orientation_uncertain"]))


if __name__ == "__main__":
    raise SystemExit(main())
