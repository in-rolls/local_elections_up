PY = .venv/bin/python
RUFF = .venv/bin/ruff

.PHONY: sync fetch-sources data release-data enrich-gp data-gp data-offices data-panels data-lgd data-weaver catalog data-summary lint check verify winner-lists-2015 verify-2015

sync:
	uv sync --frozen --all-groups

release-data: data

data: data-offices data-lgd data-weaver
	$(MAKE) catalog
	$(PY) -m local_elections_up.build.fetch_log
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
	$(PY) -m local_elections_up.build.fetch_log --check

check: lint verify verify-2015

# The ~62,000 SEC portal captures behind the office provenance are not in the
# repository; data/manual/catalogs/archived_source_resolutions.jsonl.gz records their
# hashes. This restores the bytes from the source-evidence release so `make data`
# hashes them again (about 3 GB downloaded, 4.3 GB extracted).
EVIDENCE_RELEASE = source-evidence-2026-09-19
fetch-sources:
	gh release download $(EVIDENCE_RELEASE) --repo in-rolls/local_elections_up --dir dist/source-evidence --skip-existing --pattern 'up_recovery.tar.gz.chunk-*' --pattern CHECKSUMS.sha256
	cd dist/source-evidence && grep ' up_recovery' CHECKSUMS.sha256 | shasum -a 256 -c --quiet
	cat dist/source-evidence/up_recovery.tar.gz.chunk-* | tar -xz --exclude='*/._*'

winner-lists-2015:
	$(PY) -m local_elections_up.parse.convert_winner_lists_2015

verify-2015:
	$(PY) -m local_elections_up.parse.convert_winner_lists_2015 --check
