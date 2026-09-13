# Standardized UP gram panchayat elections

`up_gp_elections_standardized.parquet` is the analysis-ready election table.
It has one row per elected gram panchayat seat in 2005, 2010, and 2015 and one
row per declared winner in 2021. It preserves 212,525 source rows; it does not
silently select one row when normalized place names collide.

## Keys and provenance

| Column | Meaning |
| --- | --- |
| `election_gp_key` | Unique release key: the 2021 candidate ID or a source-file row key for earlier waves. |
| `election_year` | Election year. |
| `source_file` | Published source Parquet from which the row was derived. |
| `source_row_number` | One-indexed row number in that source file. For 2021 this is the candidate-file row before winner filtering. |
| `source_record_id` | Source candidate ID in 2021; missing in earlier files. |
| `gp_number_raw` | Source GP code/serial. It is not unique outside its source context and is never used alone as a join key. |

## Names and linking

The `*_hindi` and `*_eng_raw` columns preserve source values. The canonical
`district_name_eng`, `block_name_eng`, and `gp_name_eng` fields apply only the
reviewed crosswalks under `data/crosswalks/active/`. The `*_std_raw` fields
normalize source names; the `*_std` fields normalize canonical names. Both use
ASCII lowercase text with punctuation removed and whitespace collapsed.

`district_name_alias_used`, `block_xwalk_used`, `block_name_alias_used`, and
`name_override_used` expose every correction on the released row.
`lgd_block_code` is populated for every 2021 block using a one-to-one reviewed
crosswalk. The crosswalk requires a unique best official block within a reviewed
district, at least two exact normalized GP-name overlaps, and an overlap margin
of at least two over the runner-up. The two mappings with fewer than four
overlaps were inspected manually.

`lgd_gp_code`, `lgd_gp_name`, `lgd_gp_link_method`, and `lgd_gp_link_score`
record the accepted 2021 election-to-LGD GP linkage. Exact normalized names are
accepted deterministically within reviewed blocks. Nonexact names use preclink's
Jaro-Winkler scoring and one-to-one Hungarian assignment within block, with a
candidate margin of at least 0.05. Only scores above 0.90 enter the active
crosswalk. A stratified clerical sample found 75 of 75 accepted-threshold links
to be matches; six uncertain cases occurred in the lower-score band, which
remains in the audit queue. `lgd_gp_linked` never treats an unlinked row as a
zero or as a match.

`normalized_name_key` joins district, block, and GP normalized names within an
election year. `normalized_name_key_n` reports its multiplicity.
`link_eligible` is true only when all three components exist and the key occurs
once. A false value is a review flag, not a dropped observation. Every flagged
row is published in
`data/crosswalks/audit/up_gp_elections_link_exceptions.csv`.

## Election variables

| Column | Meaning |
| --- | --- |
| `reservation_status_hindi`, `reservation_status_eng` | Source seat-reservation labels. |
| `reservation_class` | `general`, `obc`, `sc`, `st`, or `unknown`. |
| `women_reserved` | 1 for a women-reserved seat, 0 for a known non-women-reserved seat, and missing for unknown source labels. |
| `pradhan_name_hindi`, `pradhan_name_eng_raw` | Elected pradhan's name. |
| `winner_sex_hindi` | Cleaned source sex label. |
| `winner_woman` | 1 for `महिला`, 0 for `पुरुष`, and missing for every other value. |
| `result_status_hindi` | Contested/unopposed in 2015 and winner in 2021; unavailable in 2005 and 2010. |

Run `make data` to rebuild the table and its audits. Run `make check` to lint,
test the row-count and recode contracts, and verify every published Parquet
checksum.

## Historical LGD bridge

`up_gp_lgd_bridge.parquet` supplies the geographic projection formerly prepared
by `quota_raj`, without SHRUG or Census outcomes. Its source vintage, input
hashes and matching-method attribution are recorded in
`data/external/lgd/SOURCES.json`. The base mapping uses 2005–2010 linked records
with known reservation in both waves. Each projection retains the reference
panel's known-reservation eligibility; these exclusions are explicit and do
not change the underlying published election panels.

Join on **`panel` and `anchor_key`**. `anchor_key` is the stable `key_2010` for
panels containing 2010, and `key_2015` for `2015_2021`. The source `key_YEAR`
columns and `source_panel_row` are also retained. `mapping_anchor_key` identifies
the 2010 record supplying a matched LGD assignment. Geographic propagation
follows the reference's English district/block/GP names; ambiguous names remain
unmatched, and an unmatched GP carries missing block and GP match fields. The
bridge is unique on `panel` and `anchor_key`, not on `lgd_gp_code`.

| Panel | Rows | Matched to LGD |
|---|---:|---:|
| 2005–2010 | 41,890 | 32,612 |
| 2010–2015 | 39,529 | 27,748 |
| 2015–2021 | 46,514 | 18,018 |
| 2005–2010–2015–2021 | 29,253 | 24,188 |

The matcher restricts GP candidates to reviewed LGD blocks, excludes urban
labels, and uses exact matches followed by unique Jaro matches at distance
at most 0.20. It rejects tied best candidates and resolves destination collisions
within each historical election district/block label. A `unique` value in
`match_confidence` describes that candidate comparison; it does not assert that
an LGD code appears once in the bridge. The retained reference map has ten LGD GP
codes assigned to two 2005–2010 anchors each, all where the reviewed `Seekhar` and
`Seeti` historical labels map to LGD block 1993 (`Shikhar`). Later panels can
retain only one of those historical anchors. Numbers present on both sides must
agree, including Devanagari digits; Hindi vowel marks remain intact. Missing
numeral information retains the reference behavior and does not itself reject a
match.

`Rscript scripts/10_link_historical_lgd.R` verifies the pinned inputs and rebuilds
the bridge, release metadata and sensitivity tables. `make data-lgd` also
rebuilds the upstream election panels. Tests run with
`Rscript tests/test_historical_lgd.R`.

The full-linked-panel alternative changes 763 shared **panel-anchor rows**
(752 distinct election anchor keys): 740 gain a match and 23 lose one. No
previously matched destination is reassigned. Changes by panel are 8, 472, 278
and 5 in the order above. These alternatives remain in the sensitivity audit;
adopting broader coverage requires a linkage decision, rather than treating
it as an unchanged data handoff.

Two source-supported inherited identities have `mapping_review_id` populated;
they project to five panel-anchor rows and use `gp_match_type = "reviewed"`.
All reported distances use the current vowel-preserving comparison. The old
scores are retained only as evidence in the review crosswalk. See
`data/external/lgd/README.md`; source names remain unchanged.
