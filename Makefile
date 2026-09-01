.PHONY: sync data link-gp lint test check

sync:
	uv sync --all-groups

data:
	Rscript scripts/05_standardize_elections.R

link-gp:
	uv run python scripts/06_link_2021_lgd.py
	Rscript scripts/05_standardize_elections.R

lint:
	Rscript -e 'l <- lintr::lint_dir("scripts"); print(l); quit(status = as.integer(length(l) > 0L))'
	.venv/bin/ruff check .
	.venv/bin/ruff format --check .

test:
	Rscript tests/test_standardized_release.R
	.venv/bin/pytest -q

check: lint test
	cd data/fin && shasum -a 256 -c CHECKSUMS.sha256
