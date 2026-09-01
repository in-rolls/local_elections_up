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
