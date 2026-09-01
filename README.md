## UP Local Elections Repository

Data for 2005, 2010, 2015, and 2021 Sarpanch Elections and 2012 ULB.

## Published data: `data/fin/`

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

**Three things that will bite you if you assume otherwise.**

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

### How it is produced

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

## 🔗 Adjacent Repositories

- [in-rolls/local_elections_kerala](https://github.com/in-rolls/local_elections_kerala) — Kerala Local Government Seat Reservation Data and Winner Attributes
- [in-rolls/local_elections_uttarakhand](https://github.com/in-rolls/local_elections_uttarakhand) — Data on Local Elections from Uttarakhand
- [in-rolls/local_elections_bihar](https://github.com/in-rolls/local_elections_bihar) — Candidate Info. + Valid Votes Won by Cands. in the 2016 Bihar Panchayat Elections
- [in-rolls/parse_unsearchable_rolls](https://github.com/in-rolls/parse_unsearchable_rolls) — Parse Unsearchable Electoral Rolls
- [in-rolls/mnrega_social](https://github.com/in-rolls/mnrega_social) — MNREGA Social Audit Data
