# Weaver UP panchayat panel

Gram-panchayat–level panel for Uttar Pradesh, **provided by Jeffrey Weaver
(University of Southern California)**, collected for:

> Narasimhan, Veda, and Jeffrey Weaver. 2024. "Polity Size and Local Government
> Performance: Evidence from India." *American Economic Review* 114 (11):
> 3385–3426. <https://doi.org/10.1257/aer.20221712>

Please cite that article in any work using these files, and credit Jeffrey Weaver
for the data.

These are **working files shared directly**, not the paper's published replication
package — that is archived separately at openICPSR (project 202444, "Data and Code
for: Polity size and local government performance: evidence from India"). Because
these particular files have no public archive of their own, this repository is
their custodian.

Stored gzipped. `haven::read_dta()` reads a `.dta.gz` directly, so no
decompression step is needed:

```r
jeff <- haven::read_dta(here("data/external/weaver/weaver_data.dta.gz"))
```

## The two vintages are not interchangeable

| file | received | rows | cols | carries |
| --- | --- | ---: | ---: | --- |
| `weaver_data.dta.gz` | 2025-03-02 | 161,871 | 97 | electoral-competition measures: `effective_candidates`, `effective_candidates_pc`, `candidates_pc`, `hhi_percent`; also `gp_code_ele15`, `gp_code_ele20` |
| `weaver_data_2.dta.gz` | 2025-03-17 | 176,736 | 100 | the SHRUG/census crosswalk: `shrid`, `pc11_state_id`, `pc11_district_id`, `pc11_subdistrict_id`, `pc11_cdblock_id` |

88 columns are shared. The second is not a strict replacement for the first: it
adds 14,865 rows and the SHRUG linkage, and it **drops** the competition measures.
Pick by which of those you need. Both retain `gp_code_jj11`, `gp_code_lgd21` and
`election`.

## Five files, three vintages

`nw_*` are the earlier files that came with the Narasimhan--Weaver working
material; `weaver_data*` are the later panel. They overlap heavily, and the
overlap is the reason they sit together rather than in whichever repo happened
to receive them:

| file | received | rows | relationship |
| --- | --- | ---: | --- |
| `nw_election10.dta.gz` | 2024-04 | 48,293 | **exactly the 2010 wave of `weaver_data.dta.gz`** — 100.00% key match on `gp_code_jj11`, zero disagreements on any shared column |
| `nw_elections_analysis.dta.gz` | 2024-04 | 116,335 | an **earlier vintage** of the 2015/2020 waves of `weaver_data.dta.gz`, which supersedes it |
| `nw_up_nregs.dta.gz` | 2024-04 | 465,870 | **distinct** — the MGNREGA outcome table, 2016--2020, sharing only `gp_code_jj11`, `gp_code_lgd21` and `blockcode_lgd21` with the panel |
| `weaver_data.dta.gz` | 2025-03-02 | 161,871 | 2010/2015/2020, with the electoral-competition measures |
| `weaver_data_2.dta.gz` | 2025-03-17 | 176,736 | adds the SHRUG/PC11 crosswalk, drops the competition measures |

`nw_up_nregs` looks at first like a stray MGNREGA file rather than Weaver's.
It is his: it shares the other two files' Stata timestamp to the minute
(5 Apr 2024 11:48, so one do-file wrote all three); it is keyed on
`gp_code_jj11`, his own identifier rather than a standard LGD or SHRUG code;
and its constructed variables — `solo_gp95`, `solo_gp15`, `closestpop_1000`,
`noncompliant_district_2015`, `performance_z` — are the polity-size design of
Narasimhan and Weaver (2024), for which MGNREGA performance is the outcome. It
is entirely Uttar Pradesh (SHRUG prefix 11-09) and shares **no** columns with
the separate MGNREGA collection in `quota/data/mnrega/`.

So `nw_election10` is fully redundant and kept only as the received artefact;
`nw_elections_analysis` is what a 2024 analysis would have used, and is what
`quota/scripts/99_narasimhan_weaver.R` reads, which is why it must not be
silently swapped for the later panel.

## Identifiers — notes from Jeff

> The variable `gp_code_jj11` should be the unique identifier for the 2010
> elections, while `gp_code_lgd21` will be the one for the 2015 and 2021
> elections. The 2010 data isn't as good quality since we didn't really use that
> much for our project, but the 2015-2021 match should be better.

`election` is coded `-1`, `0`, `1` for 2010, 2015 and 2020 respectively, and
carries Stata value labels. Read it with `haven` and convert with
`as.numeric()` before recoding — converting via character would give `NA`. This
is also why the files are kept as Stata rather than Parquet: the `.dta` holds six
value-label sets that Parquet would silently drop.

## Verifying

```bash
shasum -a 256 -c CHECKSUMS.sha256
```

The checksums are of the **gzipped** files as stored here. Both were confirmed to
decompress byte-identically to the originals they were made from.

## Consumers

`quota` and `quota_raj` both read these. They previously held their own copies
under `data/up/`; those are being replaced by a pinned fetch from this repository
so the two cannot drift apart.
