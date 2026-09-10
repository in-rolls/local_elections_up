# Sitapur 2010 reservation research

Three archived district PDFs provide 2,897 source observations across 90 pages:
1,329 gram-panchayat heads, 1,506 block/samiti-member printings, and 62
district-member printings. These are reservation lists, not election results.

The extraction uses native PDF words and drawn cell boundaries, not paid OCR.
All printed totals reconcile; there are no unclassified grid rows or cell-extraction
issues. Those checks do not establish the accuracy of every name or ward identity.

## Numbering conflicts

The samiti source contains 1,496 distinct combinations of source PDF, exact encoded
block label, and printed serial number. That is **not a verified ward count**.
Nineteen rows belong to nine duplicated-number groups. Source-cell inspection
confirmed the repeated numbers on seven PDF pages. Eight groups contain differing
reservation categories; one contains different names with the same category.

Every printing is retained. The extraction neither replaces missing numbers nor
chooses between conflicting categories. Group-level flags are diagnostic, not
instructions to discard records. Serial-sequence discrepancies remain unresolved.
The review covers these 19 rows only and is not an independent accuracy estimate.

See [the source-cell review](sitapur_2010_duplicate_number_source_review_v1.json)
and the bundled crops and row-coordinate queue for the evidence.

## Names and provenance

Raw encoded labels remain alongside Unicode candidates. The source-specific font
profile preserves 453 samiti name-part markers, including their spacing and literal
trailing digits. Zero suspicious-character flags does not certify place identities
or every decoded spelling. No name-based deduplication is performed.

Each observation retains its source URL, archive capture timestamp, PDF checksum,
page, row, and cell-band coordinates. Manifests identify extraction code, the shared
decoder, profile, inputs, and outputs. The bundle includes the original PDFs,
native extraction evidence, controls, review crops, code, and dependency lockfile.
Raw evidence and derived tables remain outside `data/fin`.

## Rebuild

From this repository, install the research dependency group with
`uv sync --all-groups`. Poppler's `pdftotext` must be available. Extract the source
bundle in an empty directory and check its included `CHECKSUMS.sha256`; its paths
are relative to that extraction directory. Pass that directory as `--root` below.
Use fresh output directories; the tools refuse to overwrite an existing output.

```sh
.venv/bin/python scripts/extract_sitapur_reservations_2010.py \
  --root /tmp/sitapur-evidence --out /tmp/sitapur-grid
.venv/bin/python scripts/decode_legacy_labels.py \
  --input /tmp/sitapur-grid/reservation_observations.csv \
  --output /tmp/sitapur-unicode/reservation_observations.parquet \
  --columns district_raw block_raw unit_name_raw \
  --profile data/catalogs/sitapur_bdc_2010_font_profile_v3.json
```

The output paths are provenance fields, so relocating a rebuild changes those
fields and its byte hashes. Compare source observations and controls separately
from location-dependent provenance. Run `make check` for the repository checks.

## Publication limits

This is a research-evidence bundle, not a final standardized release. It does not
establish complete Sitapur historical coverage, resolve the printed contradictions,
or supply verified ward identities. No paid API calls were used for this repair.
