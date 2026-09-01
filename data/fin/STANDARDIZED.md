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
