"""Build and verify the consumer catalog from the actual released tables."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / "data/release"


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def describe(path, office_files):
    relative = path.relative_to(RELEASE).as_posix()
    schema = pq.read_schema(path)
    metadata = pq.read_metadata(path)
    entry = {
        "dataset_id": relative.removesuffix(".parquet"),
        "path": relative,
        "sha256": digest(path),
        "rows": metadata.num_rows,
        "columns": [{"name": f.name, "type": str(f.type)} for f in schema],
        "validation_tier": "contract_checked",
        "assignment_usable": None,
    }
    if relative.startswith("offices/"):
        detail = office_files[path.name]
        entry.update(
            {
                k: detail[k]
                for k in ("office", "record_kind", "rows_by_year", "quality_flags")
            }
        )
        entry.update(
            grain="one source observation; sources may overlap",
            key=["record_id"],
            validation_tier="provisional_source_observations",
            assignment_usable=False,
        )
    elif relative.startswith("gp/"):
        entry["office"] = "gram_panchayat_head"
        if "candidates" in path.name:
            entry.update(
                grain="one candidate", key=["id"], rows_by_year={"2021": entry["rows"]}
            )
        elif "election_records" in path.name:
            table = pq.read_table(path, columns=["election_year"])
            counts = (
                table.group_by("election_year")
                .aggregate([("election_year", "count")])
                .to_pylist()
            )
            entry.update(
                grain="one winner-list or winner-marked record",
                key=["election_gp_key"],
                rows_by_year={
                    str(r["election_year"]): r["election_year_count"] for r in counts
                },
            )
        else:
            year = path.stem.rsplit("_", 1)[-1]
            entry.update(
                grain="one winner-list source record",
                key=["source_row_number (one-based physical row)"],
                rows_by_year={year: entry["rows"]},
            )
    elif relative.startswith("weaver/"):
        entry.update(
            grain="one source GP identifier, wide across waves",
            key=["gp_id"],
            validation_tier="external_source_preparation",
        )
    else:
        entry.update(
            grain="one linkage candidate"
            if "candidates" in path.name
            else "one linked source-record pair or history",
            key=["source-election IDs; see dictionary"],
            validation_tier="geographic_linkage",
        )
    return entry


def build():
    office = json.loads((RELEASE / "offices/manifest.json").read_text())
    files = {x["path"]: x for x in office["files"]}
    entries = [describe(p, files) for p in sorted(RELEASE.glob("*/*.parquet"))]
    manifest = {
        "schema_version": 2,
        "release": "v2.0",
        "code_revision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "source_registry_sha256": digest(ROOT / "data/catalogs/office_sources.json"),
        "grain_policy": (
            "Source records, candidates, linked records and unique seats "
            "are distinct units."
        ),
        "files": entries,
    }
    dump(RELEASE / "manifest.json", manifest)
    lines = [
        "# Data catalog",
        "",
        (
            "Counts describe records, not necessarily distinct seats. "
            "Contract checks do not certify source accuracy."
        ),
        "",
        "| Table | Rows | Years | Grain | Validation |",
        "| --- | ---: | --- | --- | --- |",
    ]
    dictionary = [
        "# Data dictionary",
        "",
        (
            "See [interpretation and provenance](README.md) for category, "
            "identifier, and linkage rules. Null means unavailable or unresolved; "
            "it never implies unreserved."
        ),
        "",
        (
            "Original source labels are retained. `_raw` fields preserve source "
            "readings; `_encoded_raw` fields preserve legacy-font text, not "
            "certified Unicode names. `_YEAR` suffixes identify election waves."
        ),
        "",
    ]
    for e in entries:
        years = (
            ", ".join(sorted(e.get("rows_by_year", {}))) or "see source documentation"
        )
        lines.append(
            f"| [{e['dataset_id']}]({e['path']}) | {e['rows']:,} | {years} | "
            f"{e['grain']} | {e['validation_tier']} |"
        )
        dictionary.extend(
            [
                f"## {e['dataset_id']}",
                "",
                f"{e['grain']}. Key: {', '.join(e['key'])}.",
                "",
                "| Column | Type |",
                "| --- | --- |",
            ]
        )
        dictionary.extend(f"| `{f['name']}` | `{f['type']}` |" for f in e["columns"])
        dictionary.append("")
    (RELEASE / "CATALOG.md").write_text("\n".join(lines) + "\n")
    (RELEASE / "DICTIONARY.md").write_text("\n".join(dictionary) + "\n")
    paths = sorted(
        p for p in RELEASE.rglob("*") if p.is_file() and p.name != "CHECKSUMS.sha256"
    )
    (RELEASE / "CHECKSUMS.sha256").write_text(
        "".join(f"{digest(p)}  {p.relative_to(RELEASE).as_posix()}\n" for p in paths)
    )
    print(f"Cataloged {len(entries)} tables")


def verify(directory=RELEASE):
    directory = directory.resolve()
    manifest = json.loads((directory / "manifest.json").read_text())
    for entry in manifest["files"]:
        path = (directory / entry["path"]).resolve()
        if not path.is_relative_to(directory):
            raise ValueError("Release path escapes its root")
        if digest(path) != entry["sha256"]:
            raise ValueError(f"Release hash changed: {entry['path']}")
        if pq.read_metadata(path).num_rows != entry["rows"]:
            raise ValueError(f"Release row count changed: {entry['path']}")
        schema = pq.read_schema(path)
        for name in schema.names:
            if name.split("_20", 1)[0] in {
                "mobile_number",
                "mobile",
                "mobile_no",
                "phone",
                "phone_number",
            }:
                raise ValueError(
                    f"Contact field in analytical export: {entry['path']}:{name}"
                )
        if entry["validation_tier"] == "provisional_source_observations":
            for batch in pq.ParquetFile(path).iter_batches(
                columns=["assignment_usable", "record_id"]
            ):
                if any(v is not False for v in batch.column(0).to_pylist()):
                    raise ValueError("Provisional observation promoted without review")
    declared = {e["path"] for e in manifest["files"]}
    actual = {
        p.relative_to(directory).as_posix() for p in directory.glob("*/*.parquet")
    }
    if declared != actual:
        raise ValueError("Release inventory differs from manifest")
    for line in (directory / "CHECKSUMS.sha256").read_text().splitlines():
        sha, relative = line.split("  ", 1)
        path = (directory / relative).resolve()
        if not path.is_relative_to(directory) or digest(path) != sha:
            raise ValueError(f"Checksum mismatch: {relative}")
    print(f"Verified {len(declared)} tables and release metadata")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["build", "verify"])
    parser.add_argument("--directory", type=Path, default=RELEASE)
    args = parser.parse_args()
    if args.command == "build":
        build()
    else:
        verify(args.directory)


if __name__ == "__main__":
    main()
