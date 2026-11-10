"""Checks against retained official sources, without network access."""

import gzip
import json
from functools import cache

import pandas as pd
import pytest

from local_elections_up.parse import parse_urban_council_sources as sources


@cache
def councilors():
    return pd.DataFrame(sources.parse_archive() + sources.parse_lucknow())


def test_coverage_and_missingness():
    data = councilors()
    assert data.groupby("city").size().to_dict() == {
        "अयोध्या": 60,
        "अलीगढ": 40,
        "लखनऊ": 110,
    }
    assert not data.duplicated(["year", "city", "ward_number"]).any()
    assert data.winner_woman.notna().sum() == 100
    lucknow = data.loc[data.city == "लखनऊ"]
    assert (
        lucknow[["winner_woman", "woman_reserved", "age", "education_raw", "votes"]]
        .isna()
        .all()
        .all()
    )
    assert not data.geography_validated.any()
    assert not data.loc[data.city == "अलीगढ", "is_complete_city"].any()
    for city, count in [("अयोध्या", 60), ("लखनऊ", 110)]:
        assert set(data.loc[data.city == city, "ward_number"]) == set(
            range(1, count + 1)
        )


def test_sex_is_separate_from_quota():
    data = councilors().dropna(subset=["winner_woman", "woman_reserved"])
    assert int(data.winner_woman.sum()) == 39
    assert int(data.woman_reserved.sum()) == 38
    assert len(data.loc[data.winner_woman & ~data.woman_reserved.astype(bool)]) == 1


def test_krutidev_content_order():
    row = (
        councilors()
        .loc[(councilors().city == "लखनऊ") & (councilors().ward_number == 2)]
        .iloc[0]
    )
    assert row.winner_name_raw == "nzksinh jkor"
    assert row.winner_name == "द्रोपदी रावत"
    assert not councilors().winner_name.str.contains(r"[A-Za-z]").any()


def test_all_archive_snapshots_agree_and_have_receipts():
    receipts = json.loads((sources.SOURCES / "archive_fetch.json").read_text())
    assert len(receipts) == 9
    baseline = None
    for receipt in receipts:
        payload = gzip.decompress((sources.ROOT / receipt["path"]).read_bytes())
        assert sources.sha(payload) == receipt["sha256"]
        assert len(payload) == receipt["bytes"]
        records = sources.archive_rows(payload)
        if baseline is None:
            baseline = records
        assert records == baseline
    with pytest.raises(ValueError, match="general-election heading"):
        sources.archive_rows(b"<html>District Planning Committee 2023</html>")


def test_all_historical_winner_fields_reproduce():
    data = sources.check_historical()
    assert data.groupby("year").size().to_dict() == {2012: 980, 2017: 1300}
    assert data.source_fields_reproduced.all()


def test_roster_disagreements_are_preserved():
    data = sources.compare_roster()
    both = data.loc[data._merge == "both"]
    assert len(both) == 980
    assert both.woman_reservation_agrees.sum() == 977
    conflicts = both.loc[~both.woman_reservation_agrees]
    assert set(zip(conflicts.district_key, conflicts.ward_number, strict=True)) == {
        ("गाजियाबाद", 43),
        ("गाजियाबाद", 77),
        ("बरेली", 20),
    }
    assert (data._merge == "right_only").sum() == 60
    assert not (data._merge == "left_only").any()
