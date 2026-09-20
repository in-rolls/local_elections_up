"""Publish the four pinned GP source preparations without contact fields."""

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path

import pyarrow.parquet as pq

from local_elections_up.fields import contact_field

ROOT = Path(__file__).resolve().parents[2]


def prepare(root=ROOT):
    sources = json.loads((root / "data/catalogs/gp_sources.json").read_text())["files"]
    output = root / "data/release/gp"
    declared = {root / s["path"] for s in sources}
    found = set((root / "data/interim/gp_enriched").glob("*.parquet"))
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
            pq.write_table(
                table.drop(excluded), staging / spec["output"], compression="zstd"
            )
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
