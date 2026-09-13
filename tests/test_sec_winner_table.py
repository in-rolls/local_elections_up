import gzip
import hashlib
import importlib.util
import io
import json
import sys
from html import escape
from pathlib import Path

import pandas as pd
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/extract_sec_winner_table.py"
UNOPPOSED = "\u0928\u093f\u0930\u094d\u0935\u093f\u0930\u094b\u0927"


@pytest.fixture
def parser_module():
    spec = importlib.util.spec_from_file_location("sec_winner_table_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def source_case(tmp_path, monkeypatch, parser_module):
    module = parser_module
    unreserved = next(k for k, v in module.RESERVATIONS.items() if v == ("NONE", False))
    candidate = next(k for k, v in module.RESERVATIONS.items() if v == ("BC", False))
    office = next(k for k, v in module.OFFICES.items() if v == "block_head")
    cells = [
        "DISTRICT",
        "1 - BLOCK",
        unreserved,
        "WINNER",
        "RELATION",
        candidate,
        "EDUCATION",
        "GENDER",
        "PHONE_MUST_NOT_BE_PUBLISHED",
        "12",
        "60",
        "50",
        "CONTESTED",
    ]

    def prepare(*, row=None, headers=None, scope=False):
        values = cells if row is None else row
        labels = module.HEADERS if headers is None else headers
        html = (
            '<h1>Panchayat 2015</h1><select id="office">'
            f"<option selected>{escape(office)}</option></select>"
            f'<table id="{module.TABLE_ID}"><tr>'
            + "".join(f"<th>{escape(value)}</th>" for value in labels)
            + "</tr><tr>"
            + "".join(f"<td>{escape(value)}</td>" for value in values)
            + "</tr></table>"
        )
        source = tmp_path / "source.html"
        source.write_text(html)
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        monkeypatch.setattr(module, "SOURCE_PATH", source.name)
        monkeypatch.setattr(module, "SOURCE_SHA256", digest)
        args = [str(SCRIPT), "--root", str(tmp_path), "--output", str(tmp_path / "out")]
        scope_path = None
        if scope:
            evidence = b"Fixture for the hash-linked scope contract"
            compressed = gzip.compress(evidence, mtime=0)
            (tmp_path / "scope.html.gz").write_bytes(compressed)
            scope_path = tmp_path / "scope.json"
            scope_path.write_text(
                json.dumps(
                    {
                        "target_source_sha256": digest,
                        "target_source_url": "https://sec.up.nic.in/ElecLive/WinnerList.aspx",
                        "tier": "block_head",
                        "election_cycle_year": 2015,
                        "election_cycle_label": "2015-16",
                        "election_date": None,
                        "evidence": [{"finding": "Synthetic scope-contract fixture"}],
                        "artifacts": [
                            {
                                "path": "scope.html.gz",
                                "source_sha256": hashlib.sha256(evidence).hexdigest(),
                                "compressed_sha256": hashlib.sha256(
                                    compressed
                                ).hexdigest(),
                            }
                        ],
                    }
                )
            )
            args.extend(["--scope", str(scope_path)])
        monkeypatch.setattr(sys, "argv", args)
        return html, tmp_path / "out", scope_path

    return module, cells, prepare


@pytest.mark.parametrize("scope", [False, True])
def test_export_preserves_cells_but_excludes_phone(source_case, capsys, scope):
    module, _, prepare = source_case
    html, out, _ = prepare(scope=scope)
    module.main()
    table = pd.read_parquet(out / "winner_printings.parquet")
    independent = pd.read_html(
        io.StringIO(html),
        flavor="lxml",
        attrs={"id": module.TABLE_ID},
        converters=dict.fromkeys(range(13), str),
        keep_default_na=False,
    )[0]
    assert len(table) == 1
    for index, field in enumerate(module.FIELDS):
        if field:
            assert table.iloc[0][field] == independent.iloc[0, index]
    assert table.iloc[0].seat_caste_reservation == "NONE"
    assert table.iloc[0].candidate_caste_reservation == "BC"
    assert table.iloc[0].year == 2015
    assert pd.isna(table.iloc[0].election_date)
    assert "PHONE_MUST_NOT_BE_PUBLISHED" not in table.to_json()
    assert "PHONE_MUST_NOT_BE_PUBLISHED" not in capsys.readouterr().out
    if scope:
        assert table.iloc[0].election_cycle_label == "2015-16"
        assert "cycle scope reviewed" in table.iloc[0].review_status


def test_unopposed_missing_votes_are_not_zero(source_case):
    module, cells, prepare = source_case
    cells[9:12] = ["-", "-", "-"]
    cells[12] = UNOPPOSED
    _, out, _ = prepare()
    module.main()
    row = pd.read_parquet(out / "winner_printings.parquet").iloc[0]
    for field in ("votes", "vote_share", "turnout"):
        assert pd.isna(row[field])
        assert row[f"{field}_missing_reason"] == "not_reported_for_unopposed_winner"


@pytest.mark.parametrize("bad_header", [False, True])
def test_header_or_cell_shift_is_rejected(source_case, bad_header):
    module, cells, prepare = source_case
    if bad_header:
        prepare(headers=list(reversed(module.HEADERS)))
        message = "header"
    else:
        prepare(row=cells[:-1])
        message = "row width"
    with pytest.raises(ValueError, match=message):
        module.main()


def test_existing_output_directory_is_immutable(source_case):
    module, _, prepare = source_case
    _, out, _ = prepare()
    out.mkdir()
    with pytest.raises(FileExistsError, match="immutable"):
        module.main()


def test_changed_scope_evidence_is_rejected(source_case):
    module, _, prepare = source_case
    _, out, scope_path = prepare(scope=True)
    (scope_path.parent / "scope.html.gz").write_bytes(b"changed")
    with pytest.raises(ValueError, match="scope evidence changed"):
        module.main()
    assert not out.exists()


@pytest.mark.parametrize(
    ("raw", "percentage", "expected"),
    [
        ("12", False, 12),
        ("\u0967\u0968", False, 12),
        ("12.5%", True, 12.5),
        ("-", False, None),
        ("NaN", True, None),
        ("-1", False, None),
        ("1,234", False, None),
        ("", True, None),
    ],
)
def test_numeric_cells_fail_closed(parser_module, raw, percentage, expected):
    assert parser_module.number(raw, percentage) == expected
