# Research evidence

Research artifacts are separate from the standardized datasets in `data/fin/`.
They retain unresolved source, naming, geography, and interpretation flags.
Availability here does not certify the records or establish statewide coverage.

## Etah historical reservations

- [Source, scope, and rebuild instructions](data/catalogs/etah_2010_readme.md)
- [Machine-readable bundle inventory](data/catalogs/etah_2010_research_bundle.json)
- [Local validation evidence](data/catalogs/etah_2010_rebuild_validation.json)
- [Download the research bundle](https://github.com/in-rolls/local_elections_up/releases/download/source-evidence-2026-09-10/etah-2010-research-2026-09-10.tar.gz)
- [Payload checksums](data/source_archives/etah-2010-research-2026-09-10.CHECKSUMS.sha256)

The bundle preserves the archived PDF, native extraction, source-cell images,
font profile, reservation codebook, typed research tables, executable helper
snapshots, and dependency lock. Its checksum list uses repository-relative
paths. Extract into an empty directory and verify the payload there:

```sh
tar -xzf etah-2010-research-2026-09-10.tar.gz
shasum -a 256 -c data/source_archives/etah-2010-research-2026-09-10.CHECKSUMS.sha256
```

The font repair is not whole-name or identity validation. Conflicting allocation
printings, unknown zero codes, and unvalidated compound-code meanings remain
explicit; no research assignment has been promoted into the final data.
# Sitapur 2010 reservation lists

The [Sitapur research notes](data/catalogs/sitapur_2010_readme.md) describe 2,897
source observations, including 1,506 samiti-member printings. All printed totals
reconcile, but 19 rows have source-confirmed duplicate-number diagnostics.
These printings must not be reported as a verified ward count.

The [bundle catalog](data/catalogs/sitapur_2010_research_bundle.json) records hashes
and source-evidence paths. The
[source-cell review](data/catalogs/sitapur_2010_duplicate_number_source_review_v1.json)
documents the nine unresolved duplicate-number groups. This material remains
separate from the standardized final datasets.
