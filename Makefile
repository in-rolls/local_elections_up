PY = .venv/bin/python

.PHONY: sync restore-r data release-data data-gp data-offices data-panels data-lgd data-weaver catalog lint test check verify winner-lists-2015 verify-2015

sync:
	uv sync --frozen --all-groups

restore-r:
	Rscript -e 'if (!requireNamespace("renv", quietly=TRUE)) install.packages("renv", repos="https://cloud.r-project.org"); renv::restore(prompt=FALSE)'

release-data: data

data: data-offices data-lgd data-weaver
	$(MAKE) catalog

data-gp:
	$(PY) -m local_elections_up.build.prepare_gp_sources
	Rscript scripts/standardize_gp_elections.R

data-offices: data-gp
	$(PY) -m local_elections_up.build.standardize_offices

data-panels: data-gp
	Rscript scripts/link_gp_elections.R

data-lgd: data-panels
	Rscript scripts/link_historical_lgd.R

data-weaver:
	Rscript scripts/prepare_weaver.R

catalog:
	$(PY) -m local_elections_up.build.release publish
	$(PY) -m local_elections_up.build.release build

lint:
	Rscript -e 'l <- c(lintr::lint_dir("scripts"), lintr::lint_dir("R")); print(l); quit(status=as.integer(length(l)>0L))'
	.venv/bin/ruff check .
	.venv/bin/ruff format --check .

test:
	Rscript tests/test_standardized_release.R
	Rscript tests/test_election_panels.R
	Rscript tests/test_weaver_preparation.R
	Rscript tests/test_historical_lgd.R
	.venv/bin/pytest -q

verify:
	$(PY) -m local_elections_up.build.release verify

check: lint test

winner-lists-2015:
	$(PY) -m local_elections_up.parse.convert_winner_lists_2015

verify-2015:
	$(PY) -m local_elections_up.parse.convert_winner_lists_2015 --check
