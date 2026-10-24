"""Publish the four pinned GP source preparations without contact fields."""

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path

import pyarrow.parquet as pq

from local_elections_up import paths
from local_elections_up.fields import contact_field

ROOT = paths.ROOT


# The legacy preparations' seat and sex columns, to NAMING.md's names. The input
# files keep their headers (their hashes are pinned); the published copies and
# everything built on them use these.
SOURCE_NAMES = {
    "gp_reservation_status": "reserved_raw",
    "gp_reservation_status_eng": "reserved_raw_english",
    "gp_res_status_fin": "reserved_raw_cleaned",
    "gp_res_status_fin_eng": "reserved_raw_cleaned_english",
    "candidate_reservation_status": "candidate_caste_raw",
    "candidate_res_status": "candidate_caste_raw",
    "candidate_res_status_fin": "candidate_caste_raw_cleaned",
    "candidate_reservation_status_eng": "candidate_caste_raw_english",
    "cand_sex_fin": "winner_woman_raw_cleaned",
}


def published_names(columns, output):
    # the 2021 file lists every candidate; the others list winners only
    person = "candidate" if "candidates" in output else "winner"
    names = SOURCE_NAMES | {"sex": f"{person}_woman_raw"}
    return [names.get(c, c) for c in columns]


def prepare(root=ROOT):
    sources = json.loads((root / "data/manual/catalogs/gp_sources.json").read_text())[
        "files"
    ]
    output = root / "data/build/release/gp"
    declared = {root / s["path"] for s in sources}
    found = set((root / "data/build/gp_enriched").glob("*.parquet"))
    if found != declared:
        raise ValueError("GP input inventory differs from the pinned registry")
    output.mkdir(parents=True, exist_ok=True)
    preserved = {"gp_head_election_records.parquet", "SCHEMA.json", "CHECKSUMS.sha256"}
    if {p.name for p in output.iterdir()} - preserved - {s["output"] for s in sources}:
        raise ValueError("Unexpected GP output; refusing to retain a stale table")
    with tempfile.TemporaryDirectory(prefix=".gp-", dir=output.parent) as temporary:
        staging = Path(temporary)
        for spec in sources:
            path = root / spec["path"]
            if not path.resolve().is_relative_to(root.resolve()):
                raise ValueError("GP input path escapes its repository")
            if Path(spec["output"]).name != spec["output"]:
                raise ValueError("GP output must be a filename")
            with path.open("rb") as stream:
                actual = hashlib.file_digest(stream, "sha256").hexdigest()
            if actual != spec["sha256"]:
                raise ValueError(f"GP source hash changed: {path}")
            table = pq.read_table(path)
            if table.num_rows != spec["rows"] or table.column_names != spec["columns"]:
                raise ValueError(f"GP source schema or grain changed: {path}")
            excluded = [
                n
                for n in table.column_names
                if contact_field(n) or n.startswith("Unnamed:")
            ]
            table = table.drop(excluded)
            table = table.rename_columns(
                published_names(table.column_names, spec["output"])
            )
            pq.write_table(table, staging / spec["output"], compression="zstd")
        for name in preserved:
            if (output / name).is_file():
                shutil.copy2(output / name, staging / name)
        backup = staging.parent / (staging.name + "-previous")
        os.replace(output, backup)
        try:
            os.replace(staging, output)
        except BaseException:
            os.replace(backup, output)
            raise
        shutil.rmtree(backup)


def main():
    prepare()


if __name__ == "__main__":
    main()
