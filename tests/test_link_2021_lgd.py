from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts/06_link_2021_lgd.py"
SPEC = spec_from_file_location("link_2021_lgd", SCRIPT)
assert SPEC and SPEC.loader
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_normalize_name() -> None:
    assert MODULE.normalize_name(" Rāe-Bareli ") == "rae bareli"
    assert MODULE.normalize_name("Mau  Aima") == "mau aima"
    assert MODULE.normalize_name(None) is None


def test_default_lgd_is_owned_upstream(monkeypatch) -> None:
    monkeypatch.delenv("UP_LGD_GP_FILE", raising=False)
    expected = MODULE.PROJECT_ROOT / "data/external/lgd/lgd_up_block_gp.csv"
    assert MODULE.resolve_lgd_file() == expected.resolve()


def test_changed_lgd_override_is_rejected(tmp_path, monkeypatch) -> None:
    import pytest

    changed = tmp_path / "lgd.csv"
    changed.write_text("gp_code,gp_name\n45,GP44\n")
    monkeypatch.setenv("UP_LGD_GP_FILE", str(changed))
    with pytest.raises(ValueError, match="LGD hierarchy hash mismatch"):
        MODULE.resolve_lgd_file()
