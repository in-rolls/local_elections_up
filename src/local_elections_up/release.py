"""Build and verify the consumer catalog from the actual released tables."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

import pyarrow.parquet as pq

from local_elections_up.fields import contact_field, contact_payload

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


def column_meaning(name, definitions):
    base = re.sub(r"_(?:19|20)\d{2}$", "", name)
    if base in definitions:
        return definitions[base]
    if base.endswith("_encoded_raw"):
        return "Original legacy-font reading; decoding and identity remain unresolved."
    if base.endswith("_sha256"):
        return "SHA-256 pin for the named source or review artifact."
    if base.endswith("_json"):
        return "Structured source/review metadata as JSON; retain its source schema."
    if base.endswith("_raw"):
        return "Original source value, retained without certifying its interpretation."
    if base.endswith("_std") or base.endswith("_std_raw"):
        return (
            "Normalized geographic label; raw suffix means before reviewed corrections."
        )
    if base.endswith("_eng") or base.endswith("_eng_raw"):
        return "English transliteration or reviewed label; source text is retained."
    if base.endswith("_hindi"):
        return "Source Hindi reading; see the related normalization and review flags."
    return "Source-specific field; interpret using its registered source."


def build():
    office = json.loads((RELEASE / "offices/manifest.json").read_text())
    files = {x["path"]: x for x in office["files"]}
    expected = {"offices/" + name for name in files}
    expected.update(
        "gp/" + name
        for name in (
            "gp_head_election_records.parquet",
            "gp_head_candidates_2021.parquet",
            *(f"gp_head_winner_records_{year}.parquet" for year in (2005, 2010, 2015)),
        )
    )
    expected.update(
        "panels/" + name + ".parquet"
        for name in (
            "gp_adjacent_links",
            "gp_four_election_links",
            "gp_link_candidates",
            "gp_lgd_bridge",
            "gp_panel_2005_2010",
            "gp_panel_2010_2015",
            "gp_panel_2015_2021",
            "gp_panel_2005_2010_2015_2021",
        )
    )
    expected.update(f"weaver/weaver_{v}_wide.parquet" for v in (20250302, 20250317))
    actual = {p.relative_to(RELEASE).as_posix() for p in RELEASE.rglob("*.parquet")}
    if actual != expected:
        raise ValueError("Release tables differ from the declared product inventory")
    entries = [describe(RELEASE / name, files) for name in sorted(expected)]
    manifest = {
        "schema_version": 2,
        "release": "v2.0",
        "code_revision": subprocess.check_output(
            [
                "git",
                "log",
                "-1",
                "--format=%H",
                "--",
                "src",
                "R",
                "scripts",
                "pyproject.toml",
                "uv.lock",
                "renv.lock",
            ],
            cwd=ROOT,
            text=True,
        ).strip(),
        "source_registry_sha256": digest(ROOT / "data/catalogs/office_sources.json"),
        "code_sha256": {
            p.relative_to(ROOT).as_posix(): digest(p)
            for directory in ("src", "R", "scripts")
            for p in sorted((ROOT / directory).rglob("*"))
            if p.is_file() and p.suffix in {".py", ".R"}
        },
        "environment_sha256": {
            name: digest(ROOT / name) for name in ("uv.lock", "renv.lock")
        },
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
    definitions = json.loads(
        (ROOT / "data/catalogs/column_definitions.json").read_text()
    )
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
                "| Column | Type | Meaning |",
                "| --- | --- | --- |",
            ]
        )
        dictionary.extend(
            f"| `{f['name']}` | `{f['type']}` | "
            f"{column_meaning(f['name'], definitions)} |"
            for f in e["columns"]
        )
        dictionary.append("")
    (RELEASE / "CATALOG.md").write_text("\n".join(lines) + "\n")
    (RELEASE / "DICTIONARY.md").write_text("\n".join(dictionary) + "\n")
    paths = sorted(
        p
        for p in RELEASE.rglob("*")
        if p.is_file() and p != RELEASE / "CHECKSUMS.sha256"
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
        actual_columns = [{"name": f.name, "type": str(f.type)} for f in schema]
        if actual_columns != entry["columns"]:
            raise ValueError(f"Release schema differs: {entry['path']}")
        for name in schema.names:
            if contact_field(name):
                raise ValueError(f"Contact field in analytical export: {name}")
        json_columns = [n for n in schema.names if n.endswith("_json")]
        if json_columns:
            for batch in pq.ParquetFile(path).iter_batches(columns=json_columns):
                for column in batch.columns:
                    for raw in column.to_pylist():
                        if raw and contact_payload(json.loads(raw)):
                            raise ValueError("Contact field in embedded source JSON")
        if entry["validation_tier"] == "provisional_source_observations":
            seen = set()
            for batch in pq.ParquetFile(path).iter_batches(
                columns=["assignment_usable", "record_id"]
            ):
                ids = batch.column(1).to_pylist()
                if None in ids or len(set(ids)) != len(ids) or seen.intersection(ids):
                    raise ValueError(f"Invalid observation IDs: {entry['path']}")
                seen.update(ids)
                if any(v is not False for v in batch.column(0).to_pylist()):
                    raise ValueError("Provisional observation promoted without review")
    declared = {e["path"] for e in manifest["files"]}
    if len(declared) != len(manifest["files"]):
        raise ValueError("Duplicate dataset in manifest")
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob("*.parquet")}
    if declared != actual:
        raise ValueError("Release inventory differs from manifest")
    expected_checksums = {
        p.relative_to(directory).as_posix()
        for p in directory.rglob("*")
        if p.is_file() and p != directory / "CHECKSUMS.sha256"
    }
    checked = set()
    for line in (directory / "CHECKSUMS.sha256").read_text().splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if match is None:
            raise ValueError("Malformed checksum entry")
        sha, relative = match.groups()
        if relative in checked:
            raise ValueError(f"Duplicate checksum entry: {relative}")
        checked.add(relative)
        path = (directory / relative).resolve()
        if not path.is_relative_to(directory) or digest(path) != sha:
            raise ValueError(f"Checksum mismatch: {relative}")
    if checked != expected_checksums:
        raise ValueError("Checksum inventory is incomplete or contains extra entries")
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
