# UP discovery, 2026-09-10

Owner: local_elections_up. Status: research evidence, not released data.

## Collections

- `parallel_search/`: Ballia historical scans, Kanpur Dehat notices and PDFs,
  and native SEC result tables.
- `archive_coverage/`: the complete current district directory and block-name
  frame, SEC and district Wayback inventories, and prioritized source queues.
- `sec_results/`: official 2010 block-head and district-member result PDFs,
  with native-text extractions and source-hash provenance.
- `archived_reservations/`: exact-capture downloads selected from the
  panchayat-reservation archive queue; acquisition receipts record progress.

## Scope and remaining work

The current-host district inventory and all returned continuation requests
have completed. Counts and scope limitations are recorded in
`archive_coverage/district_sweep_summary.json`. This is not evidence that all
historical host aliases, election documents, or block-year assignments have
been recovered. `block_search_frame.csv` keeps source coverage unresolved.

The 2010 SEC result PDFs contain text, but the embedded fonts lack Unicode
mappings. Their extracted text is not analysis-ready. Recover the font mapping
or establish an OCR method before interpreting the records. No paid UP
inference has been run.

Raw files inside these bundles are immutable. Working inventories and notes
are derived research artifacts. Production parsers must consume explicit
manifest entries, never every file found recursively under this directory.

The original central handoff ledger is
`local_elections/data/source_search/national/uttar_pradesh/up_source_handoff_2026-09-10.json`.
It records source and destination paths, pre-move hashes, and metadata edits
for the transferred collections. Subsequent acquisitions and derived outputs
are recorded by each collection's receipts and manifests, not that old ledger.

Published artifacts remain separate under `data/fin/`. Central adapter changes
are documented in `data/integration/central_2026_09_10/`; implementation alone
is not a published-data rebuild or successful validation.
