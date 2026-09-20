import hashlib
import json

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from local_elections_up import prepare_gp_sources, release, standardize_offices


def checksum(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp(root):
    paths = sorted(
        p for p in root.rglob("*") if p.is_file() and p.name != "CHECKSUMS.sha256"
    )
    (root / "CHECKSUMS.sha256").write_text(
        "".join(f"{checksum(p)}  {p.relative_to(root)}\n" for p in paths)
    )


@pytest.fixture
def release_copy(tmp_path):
    folder = tmp_path / "offices"
    folder.mkdir()
    path = folder / "observations.parquet"
    table = pa.table({"record_id": ["one"], "assignment_usable": [False]})
    pq.write_table(table, path)
    manifest = {
        "files": [
            {
                "path": "offices/observations.parquet",
                "sha256": checksum(path),
                "rows": 1,
                "columns": [
                    {"name": f.name, "type": str(f.type)} for f in table.schema
                ],
                "validation_tier": "provisional_source_observations",
            }
        ]
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    stamp(tmp_path)
    return tmp_path


def test_release_accepts_complete_inventory(release_copy):
    release.verify(release_copy)


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "malformed"])
def test_release_rejects_bad_checksum_inventory(release_copy, mutation):
    path = release_copy / "CHECKSUMS.sha256"
    lines = path.read_text().splitlines()
    if mutation == "missing":
        lines = lines[1:]
    elif mutation == "duplicate":
        lines += lines[:1]
    else:
        lines[0] = "not a checksum"
    path.write_text("\n".join(lines) + "\n")
    with pytest.raises(ValueError):
        release.verify(release_copy)


def test_changed_release_bytes_fail(release_copy):
    with (release_copy / "offices/observations.parquet").open("ab") as stream:
        stream.write(b"changed")
    with pytest.raises(ValueError, match="hash changed"):
        release.verify(release_copy)


@pytest.fixture
def gp_inputs(tmp_path):
    incoming = tmp_path / "data/interim/gp_enriched"
    incoming.mkdir(parents=True)
    registry = tmp_path / "data/catalogs/gp_sources.json"
    registry.parent.mkdir(parents=True)
    path = incoming / "source.parquet"
    table = pa.table({"name": ["A"], "phone_number_2021": ["123"], "Unnamed: 15": [1]})
    pq.write_table(table, path)
    registry.write_text(
        json.dumps(
            {
                "files": [
                    {
                        "path": str(path.relative_to(tmp_path)),
                        "output": "source.parquet",
                        "sha256": checksum(path),
                        "rows": 1,
                        "columns": table.column_names,
                    }
                ]
            }
        )
    )
    return tmp_path, path


def test_gp_preparation_excludes_contact_aliases(gp_inputs):
    root, _ = gp_inputs
    prepare_gp_sources.prepare(root)
    output = root / "data/release/gp/source.parquet"
    assert pq.read_table(output).to_pylist() == [{"name": "A"}]
    first = checksum(output)
    prepare_gp_sources.prepare(root)
    assert checksum(output) == first


@pytest.mark.parametrize("mutation", ["missing", "extra", "changed", "stale"])
def test_gp_registry_rejects_uncontrolled_inputs(gp_inputs, mutation):
    root, source = gp_inputs
    if mutation == "missing":
        source.unlink()
    elif mutation == "extra":
        source.with_name("extra.parquet").write_bytes(source.read_bytes())
    elif mutation == "changed":
        source.write_bytes(b"changed")
    else:
        output = root / "data/release/gp"
        output.mkdir(parents=True)
        (output / "stale.parquet").write_bytes(source.read_bytes())
    with pytest.raises(ValueError):
        prepare_gp_sources.prepare(root)


def test_office_registry_rejects_changed_input(tmp_path, monkeypatch):
    monkeypatch.setattr(standardize_offices, "ROOT", tmp_path)
    source = tmp_path / "source.csv"
    source.write_text("value\n1\n")
    spec = {"id": "source", "path": "source.csv", "sha256": checksum(source)}
    assert standardize_offices.source_path(spec) == source
    source.write_text("value\n2\n")
    with pytest.raises(ValueError, match="hash changed"):
        standardize_offices.source_path(spec)


def test_release_rejects_duplicate_manifest_dataset(release_copy):
    path = release_copy / "manifest.json"
    manifest = json.loads(path.read_text())
    manifest["files"] *= 2
    path.write_text(json.dumps(manifest))
    stamp(release_copy)
    with pytest.raises(ValueError, match="Duplicate dataset"):
        release.verify(release_copy)


def test_release_rejects_unlisted_nested_table(release_copy):
    folder = release_copy / "offices/nested"
    folder.mkdir()
    pq.write_table(pa.table({"value": [1]}), folder / "extra.parquet")
    stamp(release_copy)
    with pytest.raises(ValueError, match="inventory differs"):
        release.verify(release_copy)


@pytest.mark.parametrize(
    ("column", "values", "error"),
    [
        ("source_json", ['{"nested": {"phone_number": "123"}}'], "embedded"),
        ("record_id", [None], "observation IDs"),
        ("assignment_usable", [True], "promoted without review"),
    ],
)
def test_release_rejects_unsafe_observations(release_copy, column, values, error):
    path = release_copy / "offices/observations.parquet"
    columns = {"record_id": ["one"], "assignment_usable": [False], column: values}
    table = pa.table(columns)
    pq.write_table(table, path)
    manifest_path = release_copy / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    entry = manifest["files"][0]
    entry["sha256"] = checksum(path)
    entry["columns"] = [{"name": f.name, "type": str(f.type)} for f in table.schema]
    manifest_path.write_text(json.dumps(manifest))
    stamp(release_copy)
    with pytest.raises(ValueError, match=error):
        release.verify(release_copy)


def test_observation_identity_survives_parent_reordering_and_relocation():
    record = {
        "source_observation_id": None,
        "source_collection": "collection",
        "source_document_sha256": "a" * 64,
        "source_page": 3,
        "source_row": 2,
        "source_csv_record": None,
        "source_category_column": "reservation",
        "election_year": 2010,
        "office": "gram_panchayat_head",
    }
    relocated = record | {"source_path": "new/location", "parent_row": 100}
    standardize_offices.ensure_observation_id(record, "source")
    standardize_offices.ensure_observation_id(relocated, "source")
    assert record["record_id"] == relocated["record_id"]
    assert record["source_observation_id"] == relocated["source_observation_id"]
    distinct = record | {"source_observation_id": None, "source_row": 3}
    standardize_offices.ensure_observation_id(distinct, "source")
    assert distinct["record_id"] != record["record_id"]


def test_observation_without_a_source_locator_fails():
    record = dict.fromkeys(
        [
            "source_observation_id",
            "source_collection",
            "source_document_sha256",
            "source_page",
            "source_row",
            "source_csv_record",
            "source_category_column",
            "election_year",
            "office",
        ]
    )
    with pytest.raises(ValueError, match="stable source locator"):
        standardize_offices.ensure_observation_id(record, "source")


@pytest.mark.parametrize("keys", [["missing"], ["value"]])
def test_release_rejects_invalid_declared_keys(release_copy, keys):
    path = release_copy / "offices/observations.parquet"
    table = pa.table({"value": [1, 1]})
    pq.write_table(table, path)
    manifest_path = release_copy / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    entry = manifest["files"][0]
    entry.update(
        sha256=checksum(path),
        rows=2,
        key=keys,
        validation_tier="geographic_linkage",
        columns=[{"name": f.name, "type": str(f.type)} for f in table.schema],
    )
    manifest_path.write_text(json.dumps(manifest))
    stamp(release_copy)
    with pytest.raises(ValueError, match="[Kk]ey"):
        release.verify(release_copy)
