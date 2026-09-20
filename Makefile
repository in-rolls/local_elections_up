PY = .venv/bin/python

.PHONY: sync restore-r data release-data data-gp data-offices data-panels data-lgd data-weaver catalog lint test check verify winner-lists-2015 verify-2015 ci-docker

sync:
	uv sync --frozen --all-groups

restore-r:
	Rscript -e 'if (!requireNamespace("renv", quietly=TRUE)) install.packages("renv", repos="https://cloud.r-project.org"); renv::restore(prompt=FALSE)'

release-data: data

data: data-offices data-lgd data-weaver
	$(MAKE) catalog

data-gp:
	$(PY) -m local_elections_up.prepare_gp_sources
	Rscript scripts/05_standardize_elections.R

data-offices: data-gp
	$(PY) -m local_elections_up.standardize_offices

data-panels: data-gp
	Rscript scripts/08_link_elections.R

data-lgd: data-panels
	Rscript scripts/10_link_historical_lgd.R

data-weaver:
	Rscript scripts/09_prepare_weaver.R

catalog:
	$(PY) -m local_elections_up.release build

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
	$(PY) -m local_elections_up.release verify

check: lint test verify verify-2015

winner-lists-2015:
	$(PY) -m local_elections_up.convert_winner_lists_2015

verify-2015:
	$(PY) -m local_elections_up.convert_winner_lists_2015 --check

ci-docker:
	docker run --rm --mount type=bind,source="$(CURDIR)",target=/workspace --workdir /workspace --env UV_PROJECT_ENVIRONMENT=/tmp/up-venv python:3.12-slim sh -c 'pip install --no-cache-dir uv && uv sync --frozen --all-groups && uv run ruff check . && uv run ruff format --check . && uv run pytest -q && uv run python -m local_elections_up.release verify'
	docker run --rm --mount type=bind,source="$(CURDIR)",target=/workspace --workdir /workspace --env RENV_PATHS_LIBRARY=/tmp/up-r-library --env NOT_CRAN=true --mount type=volume,source=up-renv-cache,target=/root/.cache/R/renv rocker/r-ver:4.6.0 sh -c 'apt-get update && apt-get install -y libxml2-dev libcurl4-openssl-dev libssl-dev libuv1-dev cmake pkg-config zlib1g-dev libicu-dev && Rscript -e '\''renv::restore(prompt=FALSE)'\'' && Rscript -e '\''l <- c(lintr::lint_dir("scripts"), lintr::lint_dir("R")); print(l); stopifnot(length(l)==0); source("tests/test_standardized_release.R"); source("tests/test_election_panels.R"); source("tests/test_weaver_preparation.R"); source("tests/test_historical_lgd.R")'\'''
