"""Shared data-build invariants and Unicode normalization."""

import hashlib
import json
import re
import unicodedata

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from rapidfuzz import process
from rapidfuzz.distance import Jaro


def require(condition, message):
    if not condition:
        raise ValueError(message)


def assert_unique(frame, columns, label):
    require(not frame.duplicated(columns).any(), f"{label} is not unique on {columns}")


def empty_to_na(values):
    return values.astype("string").str.strip().replace("", pd.NA)


def latin_ascii(value):
    if pd.isna(value):
        return None
    # Decompose Latin letters only: decomposing the whole name loses Hindi marks.
    text = str(value)
    return "".join(
        "".join(
            c for c in unicodedata.normalize("NFKD", ch) if not unicodedata.combining(c)
        )
        if "LATIN" in unicodedata.name(ch, "")
        else ch
        for ch in text
    ).translate(
        str.maketrans(
            {
                "\u00d7": "*",
                "\u0131": "i",
                "ø": "o",
                "Ø": "O",
                "ł": "l",
                "Ł": "L",
                "ß": "ss",
                "æ": "ae",
                "Æ": "AE",
                "œ": "oe",
                "Œ": "OE",
            }
        )
    )


def normalize_name(value):
    value = latin_ascii(value)
    if value is None:
        return None
    value = "".join(c if c.isalnum() else " " for c in value.lower())
    return re.sub(r"\s+", " ", value).strip() or None


def normalize_link_name(value):
    value = (
        latin_ascii(unicodedata.normalize("NFC", str(value)))
        if pd.notna(value)
        else None
    )
    if value is None:
        return None
    value = "".join(
        " " if unicodedata.category(c).startswith("P") else c for c in value.lower()
    )
    return re.sub(r"\s+", " ", value).strip() or None


def normalize_lgd_name(value):
    value = (
        latin_ascii(unicodedata.normalize("NFC", str(value)))
        if pd.notna(value)
        else None
    )
    if value is None:
        return None
    value = re.sub(r"\s+", " ", value.lower()).strip()
    return "".join(c for c in value if unicodedata.category(c)[0] not in "PS")


def link_digits(value):
    if pd.isna(value):
        return ""
    groups = re.findall(r"[^\W\D_]+", value)
    return "|".join(groups).translate(str.maketrans("०१२३४५६७८९", "0123456789"))


def jaro_distance(left, right):
    """Code-point Jaro distance with fractional (not floored) transpositions.

    The published stringdist implementation counts each out-of-order matched
    character as half a transposition. RapidFuzz floors that count, which can
    admit additional links at the release thresholds.
    """
    if pd.isna(left) or pd.isna(right):
        return np.inf
    if left == right:
        return 0.0
    radius = max(max(len(left), len(right)) // 2 - 1, 0)
    matched_left, used = [], [False] * len(right)
    for i, char in enumerate(left):
        for j in range(max(0, i - radius), min(len(right), i + radius + 1)):
            if not used[j] and char == right[j]:
                matched_left.append(char)
                used[j] = True
                break
    count = len(matched_left)
    if not count:
        return 1.0
    matched_right = [char for char, found in zip(right, used, strict=True) if found]
    transpositions = (
        sum(a != b for a, b in zip(matched_left, matched_right, strict=True)) / 2
    )
    return (
        1
        - (count / len(left) + count / len(right) + (count - transpositions) / count)
        / 3
    )


def distances(left, right, threshold):
    """Exact eligible distances; infinity for candidates beyond the threshold.

    RapidFuzz supplies a lower bound, so pruning cannot discard an eligible
    fractional-transposition match. Selected pairs' raw script distances are
    calculated separately for the audit output.
    """
    a, b = list(left), list(right)
    result = process.cdist(
        [x if pd.notna(x) else "" for x in a],
        [x if pd.notna(x) else "" for x in b],
        scorer=Jaro.distance,
        dtype=np.float64,
    )
    result[pd.isna(a), :] = np.inf
    result[:, pd.isna(b)] = np.inf
    result[result > threshold + 1e-12] = np.inf
    ii, jj = np.where(np.isfinite(result) & (result > 0))
    for i, j in zip(ii, jj, strict=True):
        result[i, j] = jaro_distance(a[i], b[j])
    return result


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_table(frame, path, schema=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if schema is None:
        inferred = pa.Schema.from_pandas(frame, preserve_index=False)
        schema = pa.schema(
            [
                pa.field(
                    f.name, pa.string() if pa.types.is_large_string(f.type) else f.type
                )
                for f in inferred
            ]
        )
    table = pa.Table.from_pandas(frame, schema=schema, preserve_index=False)
    pq.write_table(table, path, compression="zstd")


def write_metadata(paths):
    directory = paths[0].parent
    require(all(p.parent == directory for p in paths), "Mixed output directories")
    schema_path = directory / "SCHEMA.json"
    schema = json.loads(schema_path.read_text()) if schema_path.exists() else {}
    for path in paths:
        table = pq.read_table(path)
        schema[path.name] = dict(
            sha256=digest(path),
            rows=table.num_rows,
            cols=table.num_columns,
            bytes=path.stat().st_size,
            columns=table.column_names,
        )
    schema_path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n")
    (directory / "CHECKSUMS.sha256").write_text(
        "".join(f"{digest(p)}  {p.name}\n" for p in sorted(directory.glob("*.parquet")))
    )
