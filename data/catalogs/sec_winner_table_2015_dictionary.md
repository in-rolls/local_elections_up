# SEC winner-table data dictionary

One row is one winner printing in the hash-pinned HTML table. Identifiers are
source-observation keys, not cross-year person or administrative-unit identifiers.
The accompanying `SCHEMA.json` records the actual Parquet field types.

## Source cell text

These strings preserve the parser's source cell text after HTML entity decoding
and whitespace collapse. They are not reconstructions of the original HTML markup.

| Field | Meaning |
| --- | --- |
| `district_raw` | Printed district label; not harmonized to another year's geography. |
| `block_raw` | Printed block number and name together. |
| `seat_reservation_raw` | Reservation of the contested office, not the winner's category. |
| `winner_name_raw` | Printed elected candidate name. |
| `relation_name_raw` | Printed father/husband name; relation type is not inferred. |
| `candidate_category_raw` | Candidate's reported category, separate from seat reservation. |
| `education_raw` | Printed educational qualification; not recoded. |
| `gender_raw` | Source-reported gender label; not inferred from names or categories. |
| `votes_raw` | Printed valid votes received. |
| `vote_share_raw` | Printed percentage of valid votes received. |
| `turnout_raw` | Printed poll percentage. |
| `result_raw` | Printed contested/unopposed result label. |

## Parsed values

| Field | Meaning |
| --- | --- |
| `source_block_number` | Integer prefix of the printed block label, scoped by district and source. |
| `block_name_raw` | Remaining printed block name after that prefix. |
| `seat_caste_reservation` | Exact-label mapping to `NONE`, `BC`, `SC`, or `ST`; unknown labels remain null and flagged. |
| `seat_woman_category` | Woman marker in the seat-reservation label, not the winner's gender. |
| `candidate_caste_reservation` | Same code set applied to the separate candidate-category cell. |
| `candidate_woman_category` | Woman marker in the candidate-category cell; not inferred gender. |
| `votes` | Parsed nonnegative integer or null. |
| `vote_share` | Parsed percentage or null; values outside 0-100 are flagged. |
| `turnout` | Parsed percentage or null; values outside 0-100 are flagged. |
| `votes_missing_reason` | `not_reported_for_unopposed_winner` for the source's missing-value notation on unopposed rows; otherwise null. |
| `vote_share_missing_reason` | Same missing-value rule for vote share. |
| `turnout_missing_reason` | Same missing-value rule for turnout. |

## Scope, provenance, and review

| Field | Meaning |
| --- | --- |
| `year` | Election-cycle starting year, 2015; not an exact poll year for every office. |
| `election_cycle_label` | Reviewed official cycle label, `2015-16`. |
| `election_date` | Exact poll date, unknown and null for every observation. |
| `office_raw` | Selected office label from the source HTML control. |
| `tier` | `block_head`; not `block_member`. |
| `source_sha256` | SHA-256 of the original, unmodified winner HTML. |
| `source_path` | Source-root-relative path to the retained original HTML. |
| `source_url` | Official acquisition URL. |
| `retrieved_utc` | Recorded original acquisition time. |
| `source_table_id` | Exact HTML table ID selected by the parser. |
| `source_row_on_table` | One-based data-row ordinal, excluding the header. |
| `source_html_tr_ordinal` | One-based table row ordinal including the header. |
| `source_observation_id` | SHA-256 of source hash, table ID, and data-row ordinal. |
| `source_scope_sha256` | SHA-256 of the reviewed cycle-scope catalog. |
| `quality_flags` | Semicolon-separated parsing/coverage diagnostics; an empty string is not a completeness certificate. |
| `review_status` | Research-staging and source-scope review status. |

The mobile-number source column is deliberately excluded. No contact-number field
or substitute identifier derived from it is exported.
