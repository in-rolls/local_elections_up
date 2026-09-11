.PHONY: sync data link-gp lint test check winner-lists-2015 verify-2015 ci-docker ci-python ci-r

sync:
	uv sync --frozen --all-groups

data:
	Rscript scripts/05_standardize_elections.R

link-gp:
	uv run python scripts/06_link_2021_lgd.py
	Rscript scripts/05_standardize_elections.R

lint:
	Rscript -e 'l <- lintr::lint_dir("scripts"); print(l); quit(status = as.integer(length(l) > 0L))'
	uv run --all-groups ruff check .
	uv run --all-groups ruff format --check .

test:
	Rscript tests/test_standardized_release.R
	uv run --all-groups pytest -q

check: lint test verify-2015
	uv run --all-groups pre-commit run --all-files
	cd data/fin && shasum -a 256 -c CHECKSUMS.sha256

winner-lists-2015:
	uv run --all-groups python scripts/convert_winner_lists_2015.py

verify-2015:
	uv run --all-groups python scripts/convert_winner_lists_2015.py --check

ci-docker: ci-python ci-r

ci-python:
	@for version in 3.12 3.14; do \
	  COPYFILE_DISABLE=1 tar --no-xattrs --exclude=._* --exclude=.git --exclude=.venv --exclude=__pycache__ --exclude=.pytest_cache --exclude=.ruff_cache --exclude=.DS_Store -cf - . | \
	  docker run --rm -i -v "$$HOME/.cache/uv:/root/.cache/uv" python:$$version-slim sh -ec 'mkdir /work; tar -xf - -C /work; cd /work; apt-get update -qq; apt-get install -y --no-install-recommends git; pip install -q uv; uv sync --frozen --all-groups; uv run --all-groups ruff check .; uv run --all-groups ruff format --check .; uv run --all-groups pytest -q; uv run --all-groups python scripts/convert_winner_lists_2015.py --check' || exit $$?; \
	done

ci-r:
	COPYFILE_DISABLE=1 tar --no-xattrs --exclude=._* --exclude=.git --exclude=.venv --exclude=__pycache__ --exclude=.pytest_cache --exclude=.ruff_cache --exclude=.DS_Store -cf - . | \
	  docker run --rm -i rocker/r2u:24.04 sh -ec 'mkdir /work; tar -xf - -C /work; cd /work; Rscript -e "install.packages(c(\"arrow\", \"digest\", \"dplyr\", \"jsonlite\", \"lintr\", \"stringi\"))"; Rscript -e "l <- lintr::lint_dir(\"scripts\"); print(l); quit(status = as.integer(length(l) > 0L))"; Rscript tests/test_standardized_release.R; cd data/fin; sha256sum -c CHECKSUMS.sha256'
