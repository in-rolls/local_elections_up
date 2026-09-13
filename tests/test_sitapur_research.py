"""Preserve source occurrences and scope Sitapur's font and number reviews."""

import copy
import json
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "extract_sitapur_reservations_2010.py"


@pytest.fixture(scope="module")
def annotate():
    return runpy.run_path(str(SCRIPT))["annotate_source_numbers"]


def observation(**overrides):
    row = {
        "tier": "block_member",
        "source_sha256": "a" * 64,
        "block_raw": "block",
        "printed_serial": "40",
        "unit_name_raw": "same encoded name",
        "caste_reservation": "BC",
        "woman_reserved": 0,
        "quality_flags": "place_names_font_encoded;visual_review_pending",
    }
    return row | overrides


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        ({}, {"source_printed_number_duplicate"}),
        (
            {"caste_reservation": "SC", "woman_reserved": 1},
            {
                "source_printed_number_duplicate",
                "source_printed_number_multiple_categories",
                "source_printed_number_same_name_category_conflict",
            },
        ),
        (
            {"unit_name_raw": "different encoded name"},
            {
                "source_printed_number_duplicate",
                "source_printed_number_multiple_names",
            },
        ),
        (
            {"unit_name_raw": "different encoded name", "caste_reservation": "SC"},
            {
                "source_printed_number_duplicate",
                "source_printed_number_multiple_names",
                "source_printed_number_multiple_categories",
            },
        ),
    ],
)
def test_duplicate_diagnostics_preserve_rows(annotate, changes, expected):
    rows = [
        observation(source_page=6, source_row_on_page=28),
        observation(source_page=6, source_row_on_page=29, **changes),
    ]
    before = copy.deepcopy(rows)
    assert annotate(rows) == rows
    assert len(rows) == 2
    for old, new in zip(before, rows, strict=True):
        previous_flags = set(old.pop("quality_flags").split(";"))
        observed_flags = set(new["quality_flags"].split(";"))
        assert observed_flags == previous_flags | expected
        assert {
            key: value for key, value in new.items() if key != "quality_flags"
        } == old
    first_flags = [row["quality_flags"] for row in rows]
    annotate(rows)
    assert [row["quality_flags"] for row in rows] == first_flags


@pytest.mark.parametrize(
    "changes",
    [
        {"source_sha256": "b" * 64},
        {"block_raw": "different block"},
        {"tier": "gp_head"},
        {"printed_serial": "41"},
    ],
)
def test_source_number_scope(annotate, changes):
    rows = [observation(), observation(**changes)]
    before = copy.deepcopy(rows)
    assert annotate(rows) == []
    assert rows == before


def test_missing_block_does_not_create_a_shared_identity(annotate):
    rows = [observation(block_raw=""), observation(block_raw="")]
    before = copy.deepcopy(rows)
    assert annotate(rows) == []
    assert rows == before


def test_native_extractor_refuses_existing_output(tmp_path):
    output = tmp_path / "existing"
    output.mkdir()
    evidence = output / "evidence.txt"
    evidence.write_text("preserve")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(tmp_path), "--out", str(output)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "FileExistsError" in result.stderr
    assert evidence.read_text() == "preserve"


@pytest.mark.parametrize(
    ("raw", "suffix"),
    [
        ("ioZriqj A", " \u0964"),
        ("jkedksVAAAA", "\u0964\u0964\u0964\u0964"),
        ("tgkxhjkckn AA1", " \u0964\u09641"),
        ("dljSyk A A", " \u0964 \u0964"),
    ],
)
def test_source_reviewed_part_markers(raw, suffix):
    decoder = runpy.run_path(str(ROOT / "scripts" / "decode_legacy_labels.py"))[
        "decode"
    ]
    profile = json.loads(
        (
            ROOT / "data" / "catalogs" / "sitapur_bdc_2010_font_profile_v3.json"
        ).read_text()
    )
    decoded, unresolved, marker = decoder(raw, profile)
    assert decoded.endswith(suffix)
    assert "\u0950" not in decoded
    assert not unresolved
    assert marker
