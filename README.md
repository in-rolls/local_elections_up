# Uttar Pradesh local-election data

[![CI](https://github.com/in-rolls/local_elections_up/actions/workflows/ci.yml/badge.svg)](https://github.com/in-rolls/local_elections_up/actions/workflows/ci.yml)

Source materials, collection and parsing tools, and standardized Uttar Pradesh local-election data. Holdings include Gram Panchayat records for 2005, 2010, 2015, and 2021, five-office winner lists from the collection labeled 2015, and 2012 urban local-body materials.

## Data

### Standardized outputs: `data/fin/`

`data/fin/` is what other repositories consume. Everything else in `data/` is
raw input or an intermediate. Four source files, one per election cycle, carry
the transliterated English columns. A fifth file is the canonical cross-wave
election table:

| file | rows | distinct panchayats | grain |
| --- | ---: | ---: | --- |
| `up_gp_sarpanch_2005_fixed_with_transliteration.parquet` | 51,872 | 51,711 | one row per seat |
| `up_gp_sarpanch_2010_fixed_with_transliteration.parquet` | 51,861 | 51,773 | one row per seat |
| `up_gp_sarpanch_2015_fixed_with_transliteration.parquet` | 59,019 | 58,994 | one row per seat |
| `up_gp_sarpanch_2021_fixed_with_transliteration.parquet` | 373,096 | 49,750 | one row per **candidate** |
| `up_gp_elections_standardized.parquet` | 212,525 | — | one row per seat/winner across all four waves |

Panchayat counts are distinct `(district_name, block_name, gp_name)` — see the
identifier warning below.

### Five-office winner-list collection

The [2015 collection](data/raw/2015/winner_lists/README.md) is now maintained here,
including all 226 original CSVs from `local_elections_up_2015`, its verified
converter, and its citation. The [source manifest](data/raw/2015/winner_lists/SOURCE_MANIFEST.json)
pins the original repository commit, file paths, and hashes. The source CSVs are
unchanged; derived tables omit mobile numbers.

| Derived file under `data/interim/winner_lists_2015/` | Records |
| --- | ---: |
| `gp_heads_2015.parquet` | 59,019 |
| `block_members_2015.parquet` | 77,743 |
| `district_members_2015.parquet` | 3,057 |
| `block_heads_2015.parquet` | 816 |
| `district_heads_2015.parquet` | 74 |

These are winner-list records with original file and row provenance. The source
label is recorded as `collection_year`; exact polling dates are not supplied by
the CSVs and may differ across offices. The source's contested/unopposed label
is preserved. [The dictionary](data/raw/2015/winner_lists/README.md#columns)
and [export manifest](data/interim/winner_lists_2015/MANIFEST.json) document the
schema and every omitted field. The separate newer SEC research collection in
[RESEARCH.md](RESEARCH.md) remains a distinct acquisition.

These intermediates are not appended to the multi-year release. In particular,
the 59,019 Gram Panchayat records do not represent an additional 2015 wave.
Existing standardized tables and consumer contracts are unchanged.

## Coverage and interpretation

*`gp_code` is not a panchayat identifier.* It is a serial within its block: 2005
has 51,872 rows but only 247 distinct `gp_code` values. A panchayat is identified
by district + block + name, and even that collides — in 2005, 97 such triples
carry more than one row (161 rows in excess of the distinct count, up to 14 on a
single triple). Join on it and you will silently fan out rows.

*`result` means different things in 2015 and 2021.* In 2015 it is
`सविरोध` / `निर्विरोध` — contested or unopposed — and every row is a seat. In 2021
it is `विजेता` / `उपविजेता` / blank — winner, runner-up, or neither — and rows are
candidates. Filtering 2021 to `विजेता` gives 49,773 winners; applying the same
filter to 2015 gives nothing.

*2021 carries three columns whose headers were lost*, `Unnamed: 15`,
`Unnamed: 16` and `Unnamed: 17`. They contain populated numeric and categorical
values and therefore are not junk, but their meanings have not been recovered
reliably enough to label or analyze. They remain unchanged in the source file
and are excluded from the standardized release.

### Canonical election table

`data/fin/up_gp_elections_standardized.parquet` standardizes identifiers,
reservation status, and winner sex without dropping ambiguous rows. The active
manual corrections and complete collision/missing-name queue live under
`data/crosswalks/`. See [`data/fin/STANDARDIZED.md`](data/fin/STANDARDIZED.md) for
the column contract.

```bash
make data
make check
```

## How collected

```
data/up_gp_sarpanch_{2005,2010}.csv          scripts/01a, 01b (parsed from data/2005/, data/2010/ PDFs)
  -> data/up_gp_sarpanch_{2005,2010}_fixed.csv
  -> data/transliteration/*_transliterate_out.csv    scripts/02, 03 (Gemini transliteration)
  -> data/fin/*.parquet                              scripts/04
```

`scripts/05_standardize_elections.R` reads the four source files and publishes
the canonical table, audit files, schema entry, and checksums.

### Verifying a copy

`data/fin/CHECKSUMS.sha256` pins the bytes and `data/fin/SCHEMA.json` records row
counts and column names. From `data/fin/`:

```bash
shasum -a 256 -c CHECKSUMS.sha256
```

Consumers should pin a tag and check against these rather than copying the files
and hoping they stay in step.

## Usage and development

```bash
uv sync --frozen --all-groups
make winner-lists-2015
make check
```

`make winner-lists-2015` converts the imported CSV collection offline;
`make verify-2015` verifies all retained values and schemas against the CSVs.
`make data` continues to build the existing multi-year R release. Neither build
collects new data or admits research outputs automatically.

`make check` runs Python and R lint, tests, pre-commit, source/output checks,
and published-release checksums. R checks require `arrow`, `digest`, `dplyr`,
`jsonlite`, `lintr`, and `stringi`. `make ci-docker` runs the Python checks in
standard Python 3.12/3.14 containers and R checks in the Rocker r2u container.
The declared research dependencies are included for the existing source tests.

## Citation

For the imported 2015 winner lists: Suriyan Laohaprapanon and Gaurav Sood,
*Uttar Pradesh local-election winners, 2015*. Identify the repository commit
and files used. [Collection citation metadata](data/raw/2015/winner_lists/CITATION.cff)
retains this author order. Other source collections have their own provenance;
the 2015 citation does not attribute every dataset in this repository.

## License

The imported 2015 converter and tests retain their
[MIT license](data/raw/2015/winner_lists/CODE_LICENSE).
Their election records originate with the Uttar Pradesh State Election
Commission; no separate source-data license is asserted by this import.

## 🔗 Adjacent Repositories

- [in-rolls/local_elections_kerala](https://github.com/in-rolls/local_elections_kerala) — Kerala Local Government Seat Reservation Data and Winner Attributes
- [in-rolls/local_elections_uttarakhand](https://github.com/in-rolls/local_elections_uttarakhand) — Data on Local Elections from Uttarakhand
- [in-rolls/local_elections_bihar](https://github.com/in-rolls/local_elections_bihar) — Candidate Info. + Valid Votes Won by Cands. in the 2016 Bihar Panchayat Elections
- [in-rolls/parse_unsearchable_rolls](https://github.com/in-rolls/parse_unsearchable_rolls) — Parse Unsearchable Electoral Rolls
- [in-rolls/mnrega_social](https://github.com/in-rolls/mnrega_social) — MNREGA Social Audit Data

## Repository organization and discovery ownership

New UP source discovery is owned here under `data/discovery/2026-09-10/`.
The `parallel_search/` and `archive_coverage/` collections were transferred
from the central repository without copying or rewriting raw evidence.
The central handoff ledger records original paths and pre-move hashes.

The shared organization contract is maintained in the central repository at
`state_repositories.md`. Published files remain under `data/fin/` until the
state release and central adapter are migrated together; new discovery is
not an implicit release input.

## Compact discovery evidence

[Source storage and restoration](data/source_archives/README.md) explains the checksummed archive. [Compact catalogs](data/catalogs/up_discovery_2026-09-10/catalog_manifest.json) remain in Git; raw evidence is a release asset. Discovery coverage is not equivalent to validated election data.

[Current UP status and remaining parsing work](STATUS.md) distinguishes usable tables from discovery evidence and unresolved extraction.

## Historical reservation research

Source-linked research artifacts, their uncertainty limits, and reproducible
build instructions are indexed in [RESEARCH.md](RESEARCH.md). These are separate
from the standardized final datasets.
