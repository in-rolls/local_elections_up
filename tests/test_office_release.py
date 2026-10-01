import json
from collections import Counter
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EXPECTED_HISTORICAL = {
    "ballia_samiti_head_historical_reservations": {
        "file": "panchayat_samiti_head_seat_reservation.parquet",
        "rows": 102,
        "rows_per_year": 17,
        "uncertain_names": 6,
    },
    "ballia_zilla_parishad_member_historical_reservations": {
        "file": "zilla_parishad_member_seat_reservation.parquet",
        "rows": 348,
        "rows_per_year": 58,
        "uncertain_names": 18,
    },
}


def office_build():
    return json.loads((DATA / "manifest.json").read_text())["office_build"]


def source_rows(name, source_id):
    """Rows of one source across every election-cycle folder holding the table.

    The 2005 and 2010 GP-head winner lists share a name but not the office schema.
    """
    paths = sorted(DATA.glob(f"*/{name}"))
    table = pa.concat_tables(
        pq.read_table(p)
        for p in paths
        if "source_collection" in pq.read_schema(p).names
    )
    return table.filter(pc.equal(table["source_collection"], source_id))


def test_historical_ballia_sources_are_complete_and_explicitly_provisional():
    sources = {item["id"]: item for item in office_build()["sources"]}
    for source_id, expected in EXPECTED_HISTORICAL.items():
        source = sources[source_id]
        assert source["input_rows"] == expected["rows"]
        assert source["exported_rows"] == expected["rows"]
        assert (
            source["source_adapter_evidence"]["literal_code_mapping_applied"] is False
        )
        assert (
            source["source_adapter_evidence"]["geographic_identity_mapping_applied"]
            is False
        )

        rows = source_rows(expected["file"], source_id)
        assert rows.num_rows == expected["rows"]
        assert Counter(rows["election_year"].to_pylist()) == {
            year: expected["rows_per_year"]
            for year in (1995, 2000, 2005, 2010, 2015, 2021)
        }
        assert set(rows["reservation_class"].to_pylist()) == {"unknown"}
        assert set(rows["assignment_usable"].to_pylist()) == {False}
        assert (
            sum(rows["name_reading_uncertain"].to_pylist())
            == expected["uncertain_names"]
        )
        assert set(rows["source_path_resolution_status"].to_pylist()) == {
            "hash_verified"
        }
        assert set(rows["source_document_hash_basis"].to_pylist()) == {"stored_bytes"}


def test_compacted_2015_csvs_retain_member_level_provenance():
    rows = source_rows(
        "gram_panchayat_head_declared_winner.parquet", "candidate_csvs_2015"
    )
    assert rows.num_rows > 0
    assert set(rows["source_document_hash_basis"].to_pylist()) == {"tar_member"}
    assert all(
        value.startswith(
            "data/archives/up-historical-sources-2006-2015-20260911.tar.gz#2015/"
        )
        for value in rows["source_local_path"].to_pylist()
    )
    assert set(rows["source_path_resolution_status"].to_pylist()) == {"hash_verified"}


def test_2015_winner_lists_have_correct_grain_and_decoded_reservations():
    expected = {
        "gram_panchayat_head": 59019,
        "panchayat_samiti_head": 816,
        "panchayat_samiti_member": 77743,
        "zilla_parishad_head": 74,
        "zilla_parishad_member": 3121,
    }
    for office, count in expected.items():
        rows = source_rows(f"{office}_declared_winner.parquet", "candidate_csvs_2015")
        assert rows.num_rows == count
        assert set(rows["is_winner"].to_pylist()) == {True}
        assert "unknown" not in rows["reservation_class"].to_pylist()
        assert None not in rows["women_reserved"].to_pylist()
        assert set(rows["result_raw"].to_pylist()) <= {"सविरोध", "निर्विरोध"}
        assert set(rows["assignment_usable"].to_pylist()) == {False}
    assert len(office_build()["sources"]) == 23


def test_conflicting_2021_markers_preserve_both_names():
    table = pq.read_table(DATA / "panels/gp_head_election_records.parquet")
    rows = table.filter(
        pc.is_in(
            table["election_gp_key"],
            value_set=pa.array(["up2021__202725", "up2021__219438"]),
        )
    ).to_pylist()
    assert len(rows) == 2
    assert {r["pradhan_name_hindi"] for r in rows} == {"देवेंद्र कुमार", "सुधाकर यादव"}
    assert all(r["winner_markers_conflict"] for r in rows)


def test_each_gp_head_cycle_is_published_once_from_its_best_source():
    winners = {
        int(p.parent.name): pq.read_table(p)
        for p in DATA.glob("*/gram_panchayat_head_declared_winner.parquet")
    }
    assert sorted(winners) == [2005, 2010, 2015]
    assert {y: t.num_rows for y, t in winners.items()} == {
        2005: 51872,
        2010: 51861,
        2015: 59019,
    }
    assert "candidate_res_status" in winners[2005].column_names
    assert set(winners[2015]["source_collection"].to_pylist()) == {
        "candidate_csvs_2015"
    }
    assert (DATA / "2021/gram_panchayat_head_candidate_record.parquet").exists()
