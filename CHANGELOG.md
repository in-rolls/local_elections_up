# Changes

## v3.0 — 2026-10-01

- Organize published tables by election: `data/<year>/<office>_<record kind>.parquet` replaces `data/release/gp/` and `data/release/offices/`. Multi-year office tables are split on `election_year`; every split table reassembles exactly to its v2.0 predecessor. Samiti heads and deputies elected in 2006 sit with the 2005 election; Ballia's 1995–2021 reservation history is split across its cycles.
- Move cross-election products (harmonized GP-head records, links, panels, LGD bridge, Weaver preparations) to `data/panels/`; they are byte-identical to v2.0 except Weaver (below).
- Publish each GP-head election once, from its best source: the 2005 and 2010 winner lists (which carry the winner's category; v2.0's office copies omitted it), the 2015 SEC candidate CSVs (category, education, votes), and the 2021 candidates. The office build's 2005, 2010 and 2021 GP-head rows (153,506), re-reads of those sources, are no longer published; `gp_head_winner_records_2015` is superseded by the 2015 office table with the same seats and people.
- Drop the dangling byte from three Weaver panchayat names whose bytes were invalid UTF-8 (six cells per preparation), so every published table reads in strict readers.
- Move raw sources from top-level `data/<year>/` and loose CSVs to `data/raw/<year>/`; office provenance resolves the old paths and still verifies bytes. Move the unreferenced Stata file to `data/external/gp_reservation_census/`.
- Build into the git-ignored `data/interim/release/` and publish with `release.py publish`; the manifest, catalog, dictionary and checksums move to `data/`, and the manifest embeds the office build's source provenance. Sort `rows_by_year` so the manifest is reproducible.
- Group the Python package by pipeline stage (`acquire/`, `parse/`, `build/`) and name the R entry points for what they do instead of by gappy numbers; module paths change (e.g. `python -m local_elections_up.build.release`). Standalone `uv run` scripts stay free of package imports. A rebuild publishes byte-identical tables.
- Consumers must update their paths.

## v2.0 — 2026-09-20

- Move consumer data to `data/release/`, with a generated catalog and dictionary, explicit row units, and a unified manifest. Consumers must update their paths.
- Preserve the expanded office observations from 23 registered source collections as provisional data. Do not interpret their counts as distinct seats or their presence as complete statewide coverage.
- Correct 140,773 consolidated 2015 office observations from candidate to winner-list semantics; decode stated seat reservations separately from candidate categories.
- Preserve both actual candidate names in the 2021 Mainpuri/Kurawali/Sonai conflicting-winner contest. Do not assert either as the resolved winner.
- Remove phone numbers and unrecovered headers from analytical tables; preserve original evidence.
- Pin release inputs, move Python code into an importable package, lock R dependencies, and add local/container release checks.

Validation includes 75 Python tests, four R checks, Linux Docker checks, independent review, and an offline rebuild reproducing all 54 table hashes.
