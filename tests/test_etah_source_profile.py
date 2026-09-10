"""Source-scoped legacy-font decoding and immutable research outputs."""

import json
import runpy
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "decode_legacy_labels.py"
PROFILE = ROOT / "data" / "catalogs" / "etah_2010_font_profile_v1.json"


@pytest.fixture(scope="module")
def decoder():
    return runpy.run_path(str(SCRIPT))["decode"]


@pytest.fixture(scope="module")
def profile():
    return json.loads(PROFILE.read_text(encoding="utf-8"))


@pytest.mark.parametrize("raw", [":Lrex<+", ":i/kuh"])
def test_reviewed_prefix_only(decoder, profile, raw):
    original, unresolved, suffix = decoder(raw)
    assert original.startswith(":")
    assert unresolved
    assert not suffix
    decoded, unresolved, suffix = decoder(raw, profile)
    assert decoded == "\u0930\u0942" + original[1:]
    assert not unresolved
    assert not suffix


def test_profile_does_not_borrow_sitapur_part_markers(decoder, profile):
    with pytest.raises(KeyError, match="part_marker_unicode"):
        decoder("ioZriqj A", profile)


def test_cli_scopes_by_source_and_column(tmp_path, profile):
    source = tmp_path / "input.parquet"
    output = tmp_path / "output.parquet"
    frame = pd.DataFrame(
        {
            "source_sha256": [profile["source_sha256"], "0" * 64],
            "block_raw": [":i/kuh", ":i/kuh"],
            "gp_name_raw": [":i/kuh", ":i/kuh"],
        }
    )
    frame.to_parquet(source, index=False)
    subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--input",
            str(source),
            "--output",
            str(output),
            "--columns",
            "block_raw",
            "gp_name_raw",
            "--profile",
            str(PROFILE),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    result = pd.read_parquet(output)
    unchanged = ":\u092a\u0927\u0928\u0940"
    corrected = "\u0930\u0942\u092a\u0927\u0928\u0940"
    assert result["block_unicode_candidate"].tolist() == [unchanged, unchanged]
    assert result["gp_name_unicode_candidate"].tolist() == [corrected, unchanged]
    pd.testing.assert_frame_equal(frame, result[frame.columns])
    manifest = json.loads(output.with_suffix(".manifest.json").read_text())
    assert manifest["source_profile"]["source_sha256"] == profile["source_sha256"]
    assert manifest["columns_decoded"]["block_raw"]["rows_in_source_profile_scope"] == 0
    assert (
        manifest["columns_decoded"]["gp_name_raw"]["rows_in_source_profile_scope"] == 1
    )


def test_cli_refuses_to_overwrite_output(tmp_path):
    output = tmp_path / "output.parquet"
    output.write_bytes(b"preserve existing evidence")
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--input",
            str(tmp_path / "absent.parquet"),
            "--output",
            str(output),
            "--columns",
            "gp_name_raw",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "existing enrichment is immutable" in result.stderr
    assert output.read_bytes() == b"preserve existing evidence"
    assert not output.with_suffix(".manifest.json").exists()
