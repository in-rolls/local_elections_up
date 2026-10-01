"""Publish the built tables by election cycle, then catalog and verify them."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

from local_elections_up import paths

import pyarrow as pa
import pyarrow.parquet as pq

from local_elections_up.fields import contact_field, contact_payload

ROOT = paths.ROOT
DATA = ROOT / "data"
BUILD = DATA / "interim/release"
METADATA = ("manifest.json", "CATALOG.md", "DICTIONARY.md")
RURAL = ("gram_panchayat_", "panchayat_samiti_", "zilla_parishad_")
# The SEC GP-head winner lists and 2021 candidates, as received apart from
# contact fields. The office build's GP-head observations are published too:
# each representation holds values the other lacks (English labels here;
# per-row source hashes and decoded reservations there).
GP_TABLES = {
    **{
        f"gp_head_winner_records_{year}.parquet": (
            f"{year}/gram_panchayat_head_winner_list.parquet"
        )
        for year in (2005, 2010, 2015)
    },
    "gp_head_candidates_2021.parquet": (
        "2021/gram_panchayat_head_candidate_record.parquet"
    ),
    "gp_head_election_records.parquet": "panels/gp_head_election_records.parquet",
}


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def cycle(office, year):
    """The general election a record belongs to.

    Samiti heads and deputies elected indirectly in 2006 follow the 2005 polls.
    """
    return 2005 if year == 2006 and office.startswith(RURAL) else year


def published_dirs(directory):
    return sorted(
        p
        for p in directory.iterdir()
        if p.is_dir() and (re.fullmatch(r"\d{4}", p.name) or p.name == "panels")
    )


def office_build(build=BUILD):
    return json.loads((build / "offices/manifest.json").read_text())


def plan(build=BUILD):
    """Every published table: (source, destination, cycle or None)."""
    steps = [(build / "gp" / name, dest, None) for name, dest in GP_TABLES.items()]
    for folder in ("panels", "weaver"):
        steps += [
            (path, f"panels/{path.name}", None)
            for path in sorted((build / folder).glob("*.parquet"))
        ]
    for entry in office_build(build)["files"]:
        name = f"{entry['office']}_{entry['record_kind']}.parquet"
        cycles = {cycle(entry["office"], int(y)) for y in entry["rows_by_year"]}
        steps += [
            (build / "offices" / entry["path"], f"{year}/{name}", year)
            for year in sorted(cycles)
        ]
    return steps


def publish(directory=DATA, build=BUILD):
    steps = plan(build)
    for folder in published_dirs(directory):
        stray = [p for p in folder.rglob("*") if p.is_file() and p.suffix != ".parquet"]
        if stray:
            raise ValueError(f"Refusing to clear {folder}: holds {stray[0].name}")
        shutil.rmtree(folder)
    for source, destination, year in steps:
        target = directory / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        if year is None:
            shutil.copyfile(source, target)
            continue
        table = pq.read_table(source)
        office = table.column("office")[0].as_py()
        keep = pa.array(
            [
                cycle(office, y) == year
                for y in table.column("election_year").to_pylist()
            ]
        )
        pq.write_table(table.filter(keep), target, compression="zstd")
    print(f"Published {len(steps)} tables")


def rows_by_year(path, column="election_year"):
    years = pq.read_table(path, columns=[column]).column(0).to_pylist()
    return {str(y): n for y, n in sorted(collections.Counter(years).items())}


def describe(path, directory, offices):
    """`offices` maps each published office-build table to (office, kind)."""
    relative = path.relative_to(directory).as_posix()
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
    folder = relative.split("/", 1)[0]
    if relative in offices:
        office, kind = offices[relative]
        flags = collections.Counter(
            flag
            for row in pq.read_table(path, columns=["quality_flags"])
            .column(0)
            .to_pylist()
            for flag in row or []
        )
        entry.update(
            office=office,
            record_kind=kind,
            rows_by_year=rows_by_year(path),
            quality_flags=dict(sorted(flags.items())),
            grain="one source observation; sources may overlap",
            key=["record_id"],
            validation_tier="provisional_source_observations",
            assignment_usable=False,
        )
    elif path.stem.startswith("gram_panchayat_head_"):
        entry["office"] = "gram_panchayat_head"
        if "candidate" in path.name:
            entry.update(grain="one candidate", key=["id"])
        else:
            entry.update(
                grain="one winner-list source record",
                key=[],
                row_locator="one-based physical row within the hash-pinned file",
            )
        entry["rows_by_year"] = {folder: entry["rows"]}
    elif path.stem == "gp_head_election_records":
        entry.update(
            office="gram_panchayat_head",
            grain="one winner-list or winner-marked record",
            key=["election_gp_key"],
            rows_by_year=rows_by_year(path),
        )
    elif path.stem.startswith("weaver_"):
        entry.update(
            grain="one source GP identifier, wide across waves",
            key=["gp_id"],
            validation_tier="external_source_preparation",
        )
    else:
        if path.stem == "gp_lgd_bridge":
            grain = "one historical panel row projected to the LGD vintage"
            keys = ["panel", "source_panel_row"]
        elif path.stem in {"gp_adjacent_links", "gp_link_candidates"}:
            grain = (
                "one accepted adjacent-wave link"
                if path.stem == "gp_adjacent_links"
                else "one assessed adjacent-wave linkage candidate"
            )
            keys = ["year_from", "year_to", "left_id", "right_id"]
        elif path.stem == "gp_four_election_links":
            grain = "one linked four-election history"
            keys = [f"election_id_{year}" for year in (2005, 2010, 2015, 2021)]
        else:
            grain = "one linked source-record pair or four-election history"
            keys = [name for name in schema.names if name.startswith("key_")]
        entry.update(grain=grain, key=keys, validation_tier="geographic_linkage")
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


def published(directory):
    return sorted(
        p.relative_to(directory).as_posix()
        for folder in published_dirs(directory)
        for p in folder.rglob("*.parquet")
    )


def build(directory=DATA, build=BUILD):
    office = office_build(build)
    steps = plan(build)
    expected = sorted(dest for _, dest, _ in steps)
    if published(directory) != expected:
        raise ValueError("Published tables differ from the declared product inventory")
    kinds = {f["path"]: (f["office"], f["record_kind"]) for f in office["files"]}
    offices = {
        dest: kinds[source.name] for source, dest, year in steps if year is not None
    }
    entries = [describe(directory / name, directory, offices) for name in expected]
    manifest = {
        "schema_version": 3,
        "release": "v3.0",
        "layout": (
            "One folder per election cycle holds that election's source tables; "
            "panels/ holds cross-election links and harmonized records derived "
            "from them."
        ),
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
        "input_registries_sha256": {
            name: digest(ROOT / "data/catalogs" / name)
            for name in ("office_sources.json", "gp_sources.json")
        },
        "office_build": {k: v for k, v in office.items() if k != "files"},
        "code_sha256": {
            p.relative_to(ROOT).as_posix(): digest(p)
            for folder in ("src", "R", "scripts")
            for p in sorted((ROOT / folder).rglob("*"))
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
    dump(directory / "manifest.json", manifest)
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
                f"{e['grain']}. Key: {', '.join(e['key']) or e['row_locator']}.",
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
    (directory / "CATALOG.md").write_text("\n".join(lines) + "\n")
    (directory / "DICTIONARY.md").write_text("\n".join(dictionary) + "\n")
    paths = [directory / name for name in expected + list(METADATA)]
    (directory / "CHECKSUMS.sha256").write_text(
        "".join(
            f"{digest(p)}  {p.relative_to(directory).as_posix()}\n"
            for p in sorted(paths)
        )
    )
    print(f"Cataloged {len(entries)} tables")


def verify(directory=DATA):
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
        keys = entry.get("key", [])
        if keys and entry["validation_tier"] != "provisional_source_observations":
            if not set(keys).issubset(schema.names):
                raise ValueError(f"Declared key columns missing: {entry['path']}")
            key_rows = pq.read_table(path, columns=keys).to_pandas()
            if key_rows.isna().any().any() or key_rows.duplicated().any():
                raise ValueError(f"Invalid declared key: {entry['path']}")
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
    if declared != set(published(directory)):
        raise ValueError("Release inventory differs from manifest")
    expected_checksums = declared | set(METADATA)
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
    parser.add_argument("command", choices=["publish", "build", "verify"])
    parser.add_argument("--directory", type=Path, default=DATA)
    args = parser.parse_args()
    if args.command == "publish":
        publish(args.directory)
    elif args.command == "build":
        build(args.directory)
    else:
        verify(args.directory)


if __name__ == "__main__":
    main()
