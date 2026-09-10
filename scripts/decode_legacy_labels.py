"""Add Unicode candidate labels using the shared, hash-recorded KrutiDev decoder."""

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd
from local_reservations.common import krutidev

ROMAN_SUFFIX = re.compile(r"(\s+(?:I\s*){1,3})$")


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def decode(raw, profile=None):
    if not isinstance(raw, str) or not raw:
        return raw, False, False
    match = ROMAN_SUFFIX.search(raw)
    suffix = match[1] if match else ""
    base = raw[: match.start()] if match else raw
    if profile:
        marker = re.search(r"(\s*)(A(?:\s*A)*)(1?)$", raw)
        if marker:
            base = raw[: marker.start()]
            suffix = (
                marker[1]
                + marker[2].replace("A", profile["part_marker_unicode"])
                + marker[3]
            )
    converted = unicodedata.normalize("NFC", krutidev.to_unicode(base))
    if profile and base.startswith(":") and converted.startswith(":"):
        converted = profile["colon_prefix_unicode"] + converted[1:]
    unresolved = bool(
        re.search(r"[A-Za-z\ufffd\u0950]", converted) or converted.startswith(":")
    )
    return converted + suffix, unresolved, bool(suffix)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--columns", nargs="+", required=True)
    parser.add_argument("--profile", type=Path)
    args = parser.parse_args()
    profile = json.loads(args.profile.read_text()) if args.profile else None
    if args.output.exists() or args.output.with_suffix(".manifest.json").exists():
        raise FileExistsError("Choose a new output; existing enrichment is immutable")
    if args.input.suffix == ".csv":
        frame = pd.read_csv(args.input, dtype=str, keep_default_na=False)
    elif args.input.suffix == ".parquet":
        frame = pd.read_parquet(args.input)
    else:
        raise ValueError("Input must be CSV or Parquet")
    missing = set(args.columns) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing requested raw columns: {sorted(missing)}")
    if profile and "source_sha256" not in frame:
        raise ValueError(
            "A source-specific font profile requires source SHA-256 values"
        )
    metrics = {}
    any_unresolved = pd.Series(False, index=frame.index)
    decoder_sha = digest(Path(krutidev.__file__))
    for column in args.columns:
        target = column.removesuffix("_raw") + "_unicode_candidate"
        if target in frame:
            raise ValueError(f"Unicode output column already exists: {target}")
        scoped = (
            frame["source_sha256"].eq(profile["source_sha256"])
            if profile and column in profile["columns"]
            else pd.Series(False, index=frame.index)
        )
        pairs = list(zip(frame[column], scoped, strict=True))
        mapping = {
            (value, bool(selected)): decode(value, profile if selected else None)
            for value, selected in pairs
            if isinstance(value, str)
        }
        decoded = [
            mapping[(value, bool(selected))]
            if isinstance(value, str)
            else (value, False, False)
            for value, selected in pairs
        ]
        frame[target] = [item[0] for item in decoded]
        unresolved = pd.Series([item[1] for item in decoded], index=frame.index)
        roman = pd.Series([item[2] for item in decoded], index=frame.index)
        any_unresolved |= unresolved
        pairs = pd.DataFrame(
            {"raw": frame[column], "decoded": frame[target]}
        ).drop_duplicates()
        collisions = pairs.groupby("decoded", dropna=False)["raw"].nunique()
        metrics[column] = {
            "output_column": target,
            "distinct_raw_labels": len({value for value, _ in mapping}),
            "rows_with_ascii_or_replacement_characters": int(unresolved.sum()),
            "rows_with_preserved_or_profiled_part_markers": int(roman.sum()),
            "rows_in_source_profile_scope": int(scoped.sum()),
            "decoded_labels_shared_by_different_raw_strings": int(
                (collisions > 1).sum()
            ),
        }
    frame["legacy_decoder_sha256"] = decoder_sha
    frame["legacy_decode_review_status"] = "unicode_candidate_not_source_verified"
    frame.loc[any_unresolved, "legacy_decode_review_status"] = (
        "unicode_candidate_has_unresolved_characters"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(args.output, index=False)
    manifest = {
        "input_name": args.input.name,
        "input_sha256": digest(args.input),
        "output_name": args.output.name,
        "output_sha256": digest(args.output),
        "rows": len(frame),
        "columns_decoded": metrics,
        "decoder_module": "local_reservations.common.krutidev",
        "decoder_source_sha256": decoder_sha,
        "enricher_source_sha256": digest(Path(__file__)),
        "source_profile": profile,
        "source_profile_sha256": digest(args.profile) if args.profile else None,
        "build_dependency": (
            "local_elections shared decoder, pinned by its source SHA-256"
        ),
        "csv_input_policy": (
            "All CSV fields read as strings; blank strings and original "
            "label text preserved."
        ),
        "roman_suffix_policy": (
            "Preserve isolated trailing I/II/III labels. "
            "A source-specific profile may decode trailing A glyphs as "
            "printed part-marker strokes without inferring "
            "administrative identities."
        ),
        "raw_columns_preserved": True,
        "rows_deduplicated": False,
        "identities_merged": False,
        "category_codes_reinterpreted": False,
        "paid_inference_usd": 0,
        "quality_status": (
            "Legacy-font decoding candidates, not verified place "
            "identities. Existing review flags remain."
        ),
    }
    args.output.with_suffix(".manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    )
    print(json.dumps(manifest, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
