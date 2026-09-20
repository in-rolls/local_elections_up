# Changes

## v2.0 — 2026-09-20

- Move consumer data to `data/release/`, with a generated catalog and dictionary, explicit row units, and a unified manifest. Consumers must update their paths.
- Preserve the expanded office observations from 23 registered source collections as provisional data. Do not interpret their counts as distinct seats or their presence as complete statewide coverage.
- Correct 140,773 consolidated 2015 office observations from candidate to winner-list semantics; decode stated seat reservations separately from candidate categories.
- Preserve both actual candidate names in the 2021 Mainpuri/Kurawali/Sonai conflicting-winner contest. Do not assert either as the resolved winner.
- Remove phone numbers and unrecovered headers from analytical tables; preserve original evidence.
- Pin release inputs, move Python code into an importable package, lock R dependencies, and add local/container release checks.

Validation includes 75 Python tests, four R checks, Linux Docker checks, independent review, and an offline rebuild reproducing all 54 table hashes.
