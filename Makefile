PY = .venv/bin/python
RUFF = .venv/bin/ruff

.PHONY: sync data release-data enrich-gp data-gp data-offices data-panels data-lgd data-weaver catalog data-summary lint check verify winner-lists-2015 verify-2015

sync:
	uv sync --frozen --all-groups

release-data: data

data: data-offices data-lgd data-weaver
	$(MAKE) catalog
	$(MAKE) verify

enrich-gp:
	$(PY) -m local_elections_up.parse.enrich_gp

data-gp:
	$(PY) -m local_elections_up.build.prepare_gp_sources
	$(PY) -m local_elections_up.build.standardize_gp

data-offices: data-gp
	$(PY) -m local_elections_up.build.standardize_offices

data-panels: data-gp
	$(PY) -m local_elections_up.build.link_elections

data-lgd: data-panels
	$(PY) -m local_elections_up.build.link_historical_lgd

data-weaver:
	$(PY) -m local_elections_up.build.prepare_weaver

catalog:
	$(PY) -m local_elections_up.build.release publish
	$(PY) -m local_elections_up.build.release build
	$(MAKE) data-summary

data-summary:
	$(PY) -m local_elections_up.build.release summary

lint:
	$(RUFF) check .
	$(RUFF) format --check .

verify:
	$(PY) -m local_elections_up.build.release verify

check: lint verify verify-2015

winner-lists-2015:
	$(PY) -m local_elections_up.parse.convert_winner_lists_2015

verify-2015:
	$(PY) -m local_elections_up.parse.convert_winner_lists_2015 --check
