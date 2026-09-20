# Data dictionary

See [interpretation and provenance](README.md) for category, identifier, and linkage rules. Null means unavailable or unresolved; it never implies unreserved.

Original source labels are retained. `_raw` fields preserve source readings; `_encoded_raw` fields preserve legacy-font text, not certified Unicode names. `_YEAR` suffixes identify election waves.

## gp/gp_head_candidates_2021

one candidate. Key: id.

| Column | Type | Meaning |
| --- | --- | --- |
| `district_name` | `string` | Source-specific field; interpret using its registered source. |
| `block_name` | `string` | Source-specific field; interpret using its registered source. |
| `gp` | `string` | Source-specific field; interpret using its registered source. |
| `gp_reservation_status` | `string` | Source-specific field; interpret using its registered source. |
| `id` | `int64` | Publisher candidate identifier in the 2021 candidate table. |
| `candidate` | `string` | Publisher's actual candidate name, distinct from the denormalized elected_sarpanch_name field. |
| `father_husband` | `string` | Source-specific field; interpret using its registered source. |
| `sex` | `string` | Source-specific field; interpret using its registered source. |
| `age` | `int64` | Source-specific field; interpret using its registered source. |
| `education` | `string` | Source-specific field; interpret using its registered source. |
| `candidate_reservation_status` | `string` | Source-specific field; interpret using its registered source. |
| `movable_property` | `int64` | Source-specific field; interpret using its registered source. |
| `immovable_property` | `int64` | Source-specific field; interpret using its registered source. |
| `criminal_history_2021` | `string` | Source-specific field; interpret using its registered source. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `result` | `string` | Source-specific field; interpret using its registered source. |
| `gp_reservation_status_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `candidate_reservation_status_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `gp_num` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name` | `string` | Source-specific field; interpret using its registered source. |
| `key` | `string` | Source-specific field; interpret using its registered source. |
| `elected_sarpanch_name` | `string` | Saved source winner-name field; 2021 values are denormalized and must not resolve conflicting candidate markers. |
| `gp_name_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `district_name_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `block_name_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `elected_sarpanch_name_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `husband_spouse_name_eng` | `string` | English transliteration or reviewed label; source text is retained. |

## gp/gp_head_election_records

one winner-list or winner-marked record. Key: election_gp_key.

| Column | Type | Meaning |
| --- | --- | --- |
| `election_gp_key` | `string` | Immutable source-election record key. Historical keys use source row ordinals; 2021 uses publisher candidate IDs. |
| `election_year` | `int32` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_file` | `string` | Source table filename; GP sources resolve within data/release/gp. |
| `source_row_number` | `int32` | One-based original source-table row before filtering winner markers. |
| `source_record_id` | `string` | Publisher candidate ID in 2021; unavailable for earlier GP records. |
| `winner_markers_conflict` | `bool` | More than one candidate carries a winner marker under the same 2021 source seat key. |
| `gp_number_raw` | `string` | Original block-local GP number/serial. It is not a global geographic identifier. |
| `district_name_hindi` | `string` | Source Hindi reading; see the related normalization and review flags. |
| `district_name_eng_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `district_name_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `district_name_std_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `district_name_alias_used` | `bool` | Whether an approved district-name alias was applied. |
| `block_name_hindi` | `string` | Source Hindi reading; see the related normalization and review flags. |
| `block_name_eng_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `block_name_std_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_xwalk_used` | `bool` | Whether an approved block crosswalk was applied. |
| `block_name_alias_used` | `bool` | Whether the reviewed block mapping changed the normalized block label. |
| `lgd_block_code` | `string` | Mapped LGD block code from the reviewed block correspondence. |
| `gp_name_hindi` | `string` | Source Hindi reading; see the related normalization and review flags. |
| `lgd_gp_code` | `string` | Mapped Local Government Directory GP code; not proof of unchanged historical boundaries. |
| `lgd_gp_name` | `string` | Name attached to the mapped LGD code in the registered directory vintage. |
| `lgd_gp_link_method` | `string` | Accepted exact or reviewed/scored geographic linkage method. |
| `lgd_gp_link_score` | `double` | Recorded similarity score for the linkage method, not a calibrated probability. |
| `lgd_gp_linked` | `bool` | Whether a GP linkage was accepted; an unlinked row is not a zero-valued match. |
| `gp_name_eng_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `gp_name_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `name_override_used` | `bool` | Whether a reviewed source-record-specific geographic name override was applied. |
| `district_name_std` | `string` | Normalized geographic label; raw suffix means before reviewed corrections. |
| `block_name_std` | `string` | Normalized geographic label; raw suffix means before reviewed corrections. |
| `gp_name_std` | `string` | Normalized geographic label; raw suffix means before reviewed corrections. |
| `normalized_name_key` | `string` | Election-year district/block/GP normalized-name combination; may collide. |
| `normalized_name_key_n` | `int32` | Number of records with this normalized-name key in the election year. |
| `link_eligible` | `bool` | True only where normalized district/block/GP components exist and their combined key is unique. |
| `reservation_status_hindi` | `string` | Source Hindi reading; see the related normalization and review flags. |
| `reservation_status_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `women_reserved` | `int32` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `pradhan_name_hindi` | `string` | Source person name. In 2021 uses the actual candidate field, preserving both conflicting names. |
| `pradhan_name_eng_raw` | `string` | Saved English transliteration; null when the denormalized name cannot identify a conflicting winner. |
| `winner_sex_hindi` | `string` | Original reported sex of the winner-marked/listed source person; does not resolve conflicting winner claims. |
| `winner_woman` | `int32` | 1 for a source-reported female winner, 0 for male, null for missing sex or a conflicting winner claim. |
| `result_status_hindi` | `string` | Contested/unopposed for 2015, publisher winner marker for 2021, missing in older GP sources. |

## gp/gp_head_winner_records_2005

one winner-list source record. Key: one-based physical row within the hash-pinned file.

| Column | Type | Meaning |
| --- | --- | --- |
| `order` | `int64` | Source-specific field; interpret using its registered source. |
| `page` | `int64` | Recorded page locator in the original parsed document. |
| `sr_no` | `string` | Source-specific field; interpret using its registered source. |
| `gp_code` | `string` | Source-local GP serial; never use alone as a cross-block identifier. |
| `gp_name` | `string` | Source-specific field; interpret using its registered source. |
| `gp_reservation_status` | `string` | Source-specific field; interpret using its registered source. |
| `elected_sarpanch_name` | `string` | Saved source winner-name field; 2021 values are denormalized and must not resolve conflicting candidate markers. |
| `sex` | `string` | Source-specific field; interpret using its registered source. |
| `candidate_res_status` | `string` | Source-specific field; interpret using its registered source. |
| `district_code` | `int64` | Source-specific field; interpret using its registered source. |
| `district_name` | `string` | Source-specific field; interpret using its registered source. |
| `block_code` | `double` | Source-specific field; interpret using its registered source. |
| `block_name` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_fin` | `string` | Source-specific field; interpret using its registered source. |
| `gp_res_status_fin` | `string` | Source-specific field; interpret using its registered source. |
| `gp_res_status_fin_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `candidate_res_status_fin` | `string` | Source-specific field; interpret using its registered source. |
| `age_t2` | `double` | Source-specific field; interpret using its registered source. |
| `cand_sex_fin` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `district_name_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `block_name_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `elected_sarpanch_name_eng` | `string` | English transliteration or reviewed label; source text is retained. |

## gp/gp_head_winner_records_2010

one winner-list source record. Key: one-based physical row within the hash-pinned file.

| Column | Type | Meaning |
| --- | --- | --- |
| `original_filename` | `string` | Original parsed document filename, retained for document/page provenance. |
| `page` | `int64` | Recorded page locator in the original parsed document. |
| `order` | `int64` | Source-specific field; interpret using its registered source. |
| `district_name` | `string` | Source-specific field; interpret using its registered source. |
| `sr_no` | `int64` | Source-specific field; interpret using its registered source. |
| `gp_code` | `double` | Source-local GP serial; never use alone as a cross-block identifier. |
| `block_code` | `int64` | Source-specific field; interpret using its registered source. |
| `block_name` | `string` | Source-specific field; interpret using its registered source. |
| `sr_gp_combo` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name` | `string` | Source-specific field; interpret using its registered source. |
| `gp_reservation_status` | `string` | Source-specific field; interpret using its registered source. |
| `elected_sarpanch_name` | `string` | Saved source winner-name field; 2021 values are denormalized and must not resolve conflicting candidate markers. |
| `husband_spouse_name` | `string` | Source-specific field; interpret using its registered source. |
| `candidate_res_status` | `string` | Source-specific field; interpret using its registered source. |
| `age` | `string` | Source-specific field; interpret using its registered source. |
| `sex` | `string` | Source-specific field; interpret using its registered source. |
| `education` | `string` | Source-specific field; interpret using its registered source. |
| `address` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_fin` | `string` | Source-specific field; interpret using its registered source. |
| `gp_res_status_fin` | `string` | Source-specific field; interpret using its registered source. |
| `gp_res_status_fin_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `candidate_res_status_fin` | `string` | Source-specific field; interpret using its registered source. |
| `cand_sex_fin` | `string` | Source-specific field; interpret using its registered source. |
| `age_fin` | `double` | Source-specific field; interpret using its registered source. |
| `educ_fin` | `string` | Source-specific field; interpret using its registered source. |
| `educ_fin_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `gp_name_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `district_name_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `block_name_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `elected_sarpanch_name_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `husband_spouse_name_eng` | `string` | English transliteration or reviewed label; source text is retained. |

## gp/gp_head_winner_records_2015

one winner-list source record. Key: one-based physical row within the hash-pinned file.

| Column | Type | Meaning |
| --- | --- | --- |
| `block` | `string` | Source-specific field; interpret using its registered source. |
| `gp` | `string` | Source-specific field; interpret using its registered source. |
| `gp_reservation_status` | `string` | Source-specific field; interpret using its registered source. |
| `elected_sarpanch_name` | `string` | Saved source winner-name field; 2021 values are denormalized and must not resolve conflicting candidate markers. |
| `father_husband` | `string` | Source-specific field; interpret using its registered source. |
| `candidate_reservation_status` | `string` | Source-specific field; interpret using its registered source. |
| `educational_qualification` | `string` | Source-specific field; interpret using its registered source. |
| `sex` | `string` | Source-specific field; interpret using its registered source. |
| `valid_votes_received` | `string` | Source-specific field; interpret using its registered source. |
| `votes_received_percent` | `string` | Source-specific field; interpret using its registered source. |
| `voting_percent` | `string` | Source-specific field; interpret using its registered source. |
| `result` | `string` | Source-specific field; interpret using its registered source. |
| `district_name` | `string` | Source-specific field; interpret using its registered source. |
| `block_num` | `string` | Source-specific field; interpret using its registered source. |
| `block_name` | `string` | Source-specific field; interpret using its registered source. |
| `gp_num` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name` | `string` | Source-specific field; interpret using its registered source. |
| `gp_reservation_status_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `candidate_reservation_status_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `gp_name_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `district_name_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `block_name_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `elected_sarpanch_name_eng` | `string` | English transliteration or reviewed label; source text is retained. |
| `husband_spouse_name_eng` | `string` | English transliteration or reviewed label; source text is retained. |

## offices/up_gram_panchayat_head_declared_winner

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_gram_panchayat_head_seat_reservation

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_gram_panchayat_member_seat_reservation

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_municipal_corporation_mayor_candidate_record

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_municipal_corporation_mayor_declared_winner

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_municipal_corporation_mayor_seat_reservation

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_municipal_corporation_ward_member_candidate_record

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_municipal_corporation_ward_member_declared_winner

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_municipal_corporation_ward_member_seat_reservation

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_municipal_council_chair_candidate_record

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_municipal_council_chair_declared_winner

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_municipal_council_chair_seat_reservation

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_municipal_council_ward_member_candidate_record

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_municipal_council_ward_member_declared_winner

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_municipal_council_ward_member_seat_reservation

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_nagar_panchayat_chair_candidate_record

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_nagar_panchayat_chair_declared_winner

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_nagar_panchayat_chair_seat_reservation

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_nagar_panchayat_ward_member_candidate_record

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_nagar_panchayat_ward_member_declared_winner

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_nagar_panchayat_ward_member_seat_reservation

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_panchayat_samiti_head_declared_winner

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_panchayat_samiti_head_elected_official

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_panchayat_samiti_head_reported_official

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_panchayat_samiti_head_seat_reservation

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_panchayat_samiti_junior_deputy_elected_official

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_panchayat_samiti_member_declared_winner

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_panchayat_samiti_member_reported_official

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_panchayat_samiti_member_seat_reservation

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_panchayat_samiti_member_source_status_notice

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_panchayat_samiti_senior_deputy_elected_official

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_zilla_parishad_head_declared_winner

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_zilla_parishad_head_elected_official

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_zilla_parishad_head_reported_official

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_zilla_parishad_head_seat_reservation

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_zilla_parishad_member_declared_winner

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_zilla_parishad_member_elected_official

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_zilla_parishad_member_reported_official

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## offices/up_zilla_parishad_member_seat_reservation

one source observation; sources may overlap. Key: record_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `source_printed_page_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_subject_temporality` | `string` | Source-specific field; interpret using its registered source. |
| `source_boundary_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_boundary_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_block_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_name_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_ward_number_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_family_counts_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_reservation_value` | `string` | Source-specific field; interpret using its registered source. |
| `source_review_evidence_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_unresolved_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `source_parent_observation_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `samiti_2005_source_status` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_text_role` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_group_id` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_duplicate_kind` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_source_key_review_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `samiti_2005_district_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_block_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_ward_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `samiti_2005_candidate_name_unicode_candidate` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_seat_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_candidate_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_sex_label_decode_status` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_path` | `string` | Source-specific field; interpret using its registered source. |
| `pri_2010_label_dictionary_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `pri_2010_source_fields_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `district_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_class` | `string` | Decoded candidate/person category; never substituted for the seat reservation. |
| `source_member_cell_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_notice_kind` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_adjudication_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_local_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_response_path_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_sha256_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_document_role` | `string` | Distinguishes original source documents, local exports, and derived intermediates. |
| `source_document_hash_basis` | `string` | Whether the hash covers stored bytes, decompressed gzip content, or an archive member. |
| `source_path_resolution_status` | `string` | hash_verified means the source locator resolved to matching bytes, not that its claims were validated. |
| `body_type_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `related_person_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_sex_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `party_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `symbol_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_age_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `nomination_number_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `record_id` | `string` | Unique release observation ID; identifies a source observation, not a geographic seat. |
| `office` | `string` | Standardized office label; rural heads, members, deputies and urban offices remain distinct. |
| `record_kind` | `string` | Source record unit: candidate, winner-marked/listed winner, official, reservation, or source-status notice. |
| `source_collection` | `string` | Source registry entry responsible for this observation. |
| `source_observation_id` | `string` | Original observation identifier retained from the registered parent artifact. |
| `source_artifact_path` | `string` | Repository-relative parent CSV or Parquet artifact used by the adapter. |
| `source_artifact_sha256` | `string` | SHA-256 of the exact parent artifact bytes. |
| `source_document_sha256` | `string` | Source content hash interpreted according to source_document_hash_basis. |
| `source_local_path` | `string` | Current source locator relative to the UP repository; archive members use archive#member. |
| `source_url` | `string` | Recorded source URL where available; a URL does not identify immutable bytes. |
| `source_response_path` | `string` | Saved acquisition response locator where available. |
| `source_row_field` | `string` | Name of the incoming field used for the source-row locator. |
| `source_copy_group` | `string` | Hash-based group of identical statewide source copies consolidated in the export. |
| `district_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `block_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `body_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_name_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `ward_code_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `membership_ward_label_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `candidate_name_raw` | `string` | Original candidate or official name attached to this source observation. |
| `related_person_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `reported_sex_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `party_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `education_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `seat_reservation_raw` | `string` | Original source seat-reservation label before normalization. |
| `candidate_category_raw` | `string` | Source candidate/person category, separate from the reservation of the seat. |
| `reservation_class` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `result_raw` | `string` | Source result label; for 2015 winner lists it means contested or unopposed. |
| `valid_votes_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `vote_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `poll_percentage_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `text_encoding` | `string` | Whether the reported labels are Unicode or retained legacy-font encodings. |
| `district_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `block_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `ward_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_and_related_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `seat_reservation_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `candidate_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `office_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `reported_category_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `body_name_encoded_raw` | `string` | Original legacy-font reading; decoding and identity remain unresolved. |
| `source_artifact_format` | `string` | Storage format of the parent artifact, such as csv or parquet. |
| `source_finality_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `name_review_status_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_image_path` | `string` | Source-specific field; interpret using its registered source. |
| `source_image_sha256` | `string` | SHA-256 pin for the named source or review artifact. |
| `source_printed_serial_raw` | `string` | Original source value, retained without certifying its interpretation. |
| `source_cell_bboxes_json` | `string` | Structured source/review metadata as JSON; retain its source schema. |
| `candidate_age` | `int64` | Source-reported age parsed as an integer where available. |
| `candidate_category_women_label` | `bool` | Whether the candidate-category label itself includes a women designation. |
| `block_context_source_page` | `int64` | Source-specific field; interpret using its registered source. |
| `block_context_source_y` | `double` | Source-specific field; interpret using its registered source. |
| `election_year` | `int16` | Election-cycle year attributed by the registered source; not an exact polling date. |
| `source_artifact_row` | `int64` | One-based physical row within the parent artifact. |
| `source_page` | `int64` | Recorded source page locator; null where page lineage is unavailable. |
| `source_row` | `int64` | Source row locator; its original field is named in source_row_field. |
| `source_csv_record` | `int64` | One-based CSV data-record ordinal, excluding the header. |
| `source_line_start` | `int64` | First physical line of the CSV record, including header offset. |
| `source_line_end` | `int64` | Last physical line of the CSV record; quoted multiline cells may span lines. |
| `ward_number` | `int64` | Parsed office ward number where the source supports that interpretation. |
| `membership_ward_number` | `int64` | Ward attached to membership; it is not necessarily the ward of the office described. |
| `valid_votes` | `int64` | Parsed count of valid votes where explicitly stated; invalid source tokens remain null and flagged. |
| `vote_percentage` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `poll_percentage` | `double` | Source-stated turnout percentage; values outside 0–100 remain unresolved. |
| `women_reserved` | `bool` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `is_winner` | `bool` | True for an asserted listed/elected winner; null for unresolved conflicts or sources that do not assert a winner. |
| `assignment_usable` | `bool` | False for all provisional office observations. Mechanical validation does not certify an assignment. |
| `quality_flags` | `list<element: string>` | Unresolved source, parsing, provenance, or interpretation conditions; multiple flags can apply. |
| `name_reading_uncertain` | `bool` | Whether the source-name reading remains uncertain; null does not certify identity. |
| `source_category_column` | `int64` | Source-specific field; interpret using its registered source. |

## panels/gp_adjacent_links

one accepted adjacent-wave link. Key: year_from, year_to, left_id, right_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `left_id` | `string` | Source-election record ID in the earlier wave of a geographic link. |
| `right_id` | `string` | Source-election record ID in the later wave of a geographic link. |
| `left_ties` | `double` | Source-specific field; interpret using its registered source. |
| `right_ties` | `double` | Source-specific field; interpret using its registered source. |
| `distance` | `double` | Source-specific field; interpret using its registered source. |
| `native_distance` | `double` | Source-specific field; interpret using its registered source. |
| `english_distance` | `double` | Source-specific field; interpret using its registered source. |
| `match_method` | `string` | Geographic comparison method used for a linkage decision. |
| `decision` | `string` | Linkage decision, including accepted, tied, competing-script, or nonreciprocal cases. |
| `year_from` | `int32` | Source-specific field; interpret using its registered source. |
| `year_to` | `int32` | Source-specific field; interpret using its registered source. |

## panels/gp_four_election_links

one linked four-election history. Key: election_id_2005, election_id_2010, election_id_2015, election_id_2021.

| Column | Type | Meaning |
| --- | --- | --- |
| `election_id_2005` | `string` | Source-specific field; interpret using its registered source. |
| `election_id_2010` | `string` | Source-specific field; interpret using its registered source. |
| `election_id_2015` | `string` | Source-specific field; interpret using its registered source. |
| `election_id_2021` | `string` | Source-specific field; interpret using its registered source. |

## panels/gp_lgd_bridge

one historical panel row projected to the LGD vintage. Key: panel, source_panel_row.

| Column | Type | Meaning |
| --- | --- | --- |
| `panel` | `string` | Election-wave combination represented by this linkage or historical LGD row. |
| `anchor_year` | `int32` | Election year supplying the historical geographic anchor. |
| `anchor_key` | `string` | Source-election ID chosen as the historical geographic anchor. |
| `key_2005` | `string` | Source-specific field; interpret using its registered source. |
| `key_2010` | `string` | Source-specific field; interpret using its registered source. |
| `source_panel_row` | `int32` | Source-specific field; interpret using its registered source. |
| `district` | `string` | Source-specific field; interpret using its registered source. |
| `block` | `string` | Source-specific field; interpret using its registered source. |
| `gp` | `string` | Source-specific field; interpret using its registered source. |
| `gp_native` | `string` | Source-specific field; interpret using its registered source. |
| `match_key` | `string` | Source-specific field; interpret using its registered source. |
| `english_key_records` | `int32` | Source-specific field; interpret using its registered source. |
| `english_key_ambiguous` | `bool` | Source-specific field; interpret using its registered source. |
| `mapping_anchor_key` | `string` | Source-specific field; interpret using its registered source. |
| `lgd_gp_code` | `double` | Mapped Local Government Directory GP code; not proof of unchanged historical boundaries. |
| `lgd_gp_name` | `string` | Name attached to the mapped LGD code in the registered directory vintage. |
| `lgd_block_code` | `double` | Mapped LGD block code from the reviewed block correspondence. |
| `lgd_block_name` | `string` | Source-specific field; interpret using its registered source. |
| `block_match_type` | `string` | Source-specific field; interpret using its registered source. |
| `gp_match_type` | `string` | Source-specific field; interpret using its registered source. |
| `match_distance` | `double` | String distance used by the stated matching method; smaller values indicate greater similarity. |
| `match_confidence` | `string` | Source-specific field; interpret using its registered source. |
| `mapping_review_id` | `string` | Reviewed identity decision supporting a historical LGD mapping, where present. |
| `key_2015` | `string` | Source-specific field; interpret using its registered source. |
| `key_2021` | `string` | Source-specific field; interpret using its registered source. |

## panels/gp_link_candidates

one assessed adjacent-wave linkage candidate. Key: year_from, year_to, left_id, right_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `left_id` | `string` | Source-election record ID in the earlier wave of a geographic link. |
| `right_id` | `string` | Source-election record ID in the later wave of a geographic link. |
| `left_ties` | `double` | Source-specific field; interpret using its registered source. |
| `right_ties` | `double` | Source-specific field; interpret using its registered source. |
| `distance` | `double` | Source-specific field; interpret using its registered source. |
| `native_distance` | `double` | Source-specific field; interpret using its registered source. |
| `english_distance` | `double` | Source-specific field; interpret using its registered source. |
| `match_method` | `string` | Geographic comparison method used for a linkage decision. |
| `decision` | `string` | Linkage decision, including accepted, tied, competing-script, or nonreciprocal cases. |
| `year_from` | `int32` | Source-specific field; interpret using its registered source. |
| `year_to` | `int32` | Source-specific field; interpret using its registered source. |

## panels/gp_panel_2005_2010

one linked source-record pair or four-election history. Key: key_2005, key_2010.

| Column | Type | Meaning |
| --- | --- | --- |
| `key_2005` | `string` | Source-specific field; interpret using its registered source. |
| `key_2010` | `string` | Source-specific field; interpret using its registered source. |
| `order_2005` | `int32` | Source-specific field; interpret using its registered source. |
| `page_2005` | `int32` | Recorded page locator in the original parsed document. |
| `sr_no_2005` | `string` | Source-specific field; interpret using its registered source. |
| `gp_code_2005` | `string` | Source-local GP serial; never use alone as a cross-block identifier. |
| `gp_name_2005` | `string` | Source-specific field; interpret using its registered source. |
| `gp_reservation_status_2005` | `string` | Source-specific field; interpret using its registered source. |
| `elected_sarpanch_name_2005` | `string` | Saved source winner-name field; 2021 values are denormalized and must not resolve conflicting candidate markers. |
| `sex_2005` | `string` | Source-specific field; interpret using its registered source. |
| `candidate_res_status_2005` | `string` | Source-specific field; interpret using its registered source. |
| `district_code_2005` | `int32` | Source-specific field; interpret using its registered source. |
| `district_name_2005` | `string` | Source-specific field; interpret using its registered source. |
| `block_code_2005` | `double` | Source-specific field; interpret using its registered source. |
| `block_name_2005` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_fin_2005` | `string` | Source-specific field; interpret using its registered source. |
| `gp_res_status_fin_2005` | `string` | Source-specific field; interpret using its registered source. |
| `gp_res_status_fin_eng_2005` | `string` | English transliteration or reviewed label; source text is retained. |
| `candidate_res_status_fin_2005` | `string` | Source-specific field; interpret using its registered source. |
| `age_t2_2005` | `double` | Source-specific field; interpret using its registered source. |
| `cand_sex_fin_2005` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_eng_2005` | `string` | English transliteration or reviewed label; source text is retained. |
| `district_name_eng_2005` | `string` | English transliteration or reviewed label; source text is retained. |
| `block_name_eng_2005` | `string` | English transliteration or reviewed label; source text is retained. |
| `elected_sarpanch_name_eng_2005` | `string` | English transliteration or reviewed label; source text is retained. |
| `source_row_number_2005` | `int32` | One-based original source-table row before filtering winner markers. |
| `election_gp_key_2005` | `string` | Immutable source-election record key. Historical keys use source row ordinals; 2021 uses publisher candidate IDs. |
| `women_reserved_2005` | `int32` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `winner_woman_2005` | `int32` | 1 for a source-reported female winner, 0 for male, null for missing sex or a conflicting winner claim. |
| `reservation_class_2005` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `original_filename_2010` | `string` | Original parsed document filename, retained for document/page provenance. |
| `page_2010` | `int32` | Recorded page locator in the original parsed document. |
| `order_2010` | `int32` | Source-specific field; interpret using its registered source. |
| `district_name_2010` | `string` | Source-specific field; interpret using its registered source. |
| `sr_no_2010` | `int32` | Source-specific field; interpret using its registered source. |
| `gp_code_2010` | `double` | Source-local GP serial; never use alone as a cross-block identifier. |
| `block_code_2010` | `int32` | Source-specific field; interpret using its registered source. |
| `block_name_2010` | `string` | Source-specific field; interpret using its registered source. |
| `sr_gp_combo_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_reservation_status_2010` | `string` | Source-specific field; interpret using its registered source. |
| `elected_sarpanch_name_2010` | `string` | Saved source winner-name field; 2021 values are denormalized and must not resolve conflicting candidate markers. |
| `husband_spouse_name_2010` | `string` | Source-specific field; interpret using its registered source. |
| `candidate_res_status_2010` | `string` | Source-specific field; interpret using its registered source. |
| `age_2010` | `string` | Source-specific field; interpret using its registered source. |
| `sex_2010` | `string` | Source-specific field; interpret using its registered source. |
| `education_2010` | `string` | Source-specific field; interpret using its registered source. |
| `address_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_fin_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_res_status_fin_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_res_status_fin_eng_2010` | `string` | English transliteration or reviewed label; source text is retained. |
| `candidate_res_status_fin_2010` | `string` | Source-specific field; interpret using its registered source. |
| `cand_sex_fin_2010` | `string` | Source-specific field; interpret using its registered source. |
| `age_fin_2010` | `double` | Source-specific field; interpret using its registered source. |
| `educ_fin_2010` | `string` | Source-specific field; interpret using its registered source. |
| `educ_fin_eng_2010` | `string` | English transliteration or reviewed label; source text is retained. |
| `gp_name_eng_2010` | `string` | English transliteration or reviewed label; source text is retained. |
| `district_name_eng_2010` | `string` | English transliteration or reviewed label; source text is retained. |
| `block_name_eng_2010` | `string` | English transliteration or reviewed label; source text is retained. |
| `elected_sarpanch_name_eng_2010` | `string` | English transliteration or reviewed label; source text is retained. |
| `husband_spouse_name_eng_2010` | `string` | English transliteration or reviewed label; source text is retained. |
| `source_row_number_2010` | `int32` | One-based original source-table row before filtering winner markers. |
| `election_gp_key_2010` | `string` | Immutable source-election record key. Historical keys use source row ordinals; 2021 uses publisher candidate IDs. |
| `women_reserved_2010` | `int32` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `winner_woman_2010` | `int32` | 1 for a source-reported female winner, 0 for male, null for missing sex or a conflicting winner claim. |
| `reservation_class_2010` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |

## panels/gp_panel_2005_2010_2015_2021

one linked source-record pair or four-election history. Key: key_2005, key_2010, key_2015, key_2021.

| Column | Type | Meaning |
| --- | --- | --- |
| `key_2005` | `string` | Source-specific field; interpret using its registered source. |
| `key_2010` | `string` | Source-specific field; interpret using its registered source. |
| `key_2015` | `string` | Source-specific field; interpret using its registered source. |
| `key_2021` | `string` | Source-specific field; interpret using its registered source. |
| `order_2005` | `int32` | Source-specific field; interpret using its registered source. |
| `page_2005` | `int32` | Recorded page locator in the original parsed document. |
| `sr_no_2005` | `string` | Source-specific field; interpret using its registered source. |
| `gp_code_2005` | `string` | Source-local GP serial; never use alone as a cross-block identifier. |
| `gp_name_2005` | `string` | Source-specific field; interpret using its registered source. |
| `gp_reservation_status_2005` | `string` | Source-specific field; interpret using its registered source. |
| `elected_sarpanch_name_2005` | `string` | Saved source winner-name field; 2021 values are denormalized and must not resolve conflicting candidate markers. |
| `sex_2005` | `string` | Source-specific field; interpret using its registered source. |
| `candidate_res_status_2005` | `string` | Source-specific field; interpret using its registered source. |
| `district_code_2005` | `int32` | Source-specific field; interpret using its registered source. |
| `district_name_2005` | `string` | Source-specific field; interpret using its registered source. |
| `block_code_2005` | `double` | Source-specific field; interpret using its registered source. |
| `block_name_2005` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_fin_2005` | `string` | Source-specific field; interpret using its registered source. |
| `gp_res_status_fin_2005` | `string` | Source-specific field; interpret using its registered source. |
| `gp_res_status_fin_eng_2005` | `string` | English transliteration or reviewed label; source text is retained. |
| `candidate_res_status_fin_2005` | `string` | Source-specific field; interpret using its registered source. |
| `age_t2_2005` | `double` | Source-specific field; interpret using its registered source. |
| `cand_sex_fin_2005` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_eng_2005` | `string` | English transliteration or reviewed label; source text is retained. |
| `district_name_eng_2005` | `string` | English transliteration or reviewed label; source text is retained. |
| `block_name_eng_2005` | `string` | English transliteration or reviewed label; source text is retained. |
| `elected_sarpanch_name_eng_2005` | `string` | English transliteration or reviewed label; source text is retained. |
| `source_row_number_2005` | `int32` | One-based original source-table row before filtering winner markers. |
| `election_gp_key_2005` | `string` | Immutable source-election record key. Historical keys use source row ordinals; 2021 uses publisher candidate IDs. |
| `women_reserved_2005` | `int32` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `winner_woman_2005` | `int32` | 1 for a source-reported female winner, 0 for male, null for missing sex or a conflicting winner claim. |
| `reservation_class_2005` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `original_filename_2010` | `string` | Original parsed document filename, retained for document/page provenance. |
| `page_2010` | `int32` | Recorded page locator in the original parsed document. |
| `order_2010` | `int32` | Source-specific field; interpret using its registered source. |
| `district_name_2010` | `string` | Source-specific field; interpret using its registered source. |
| `sr_no_2010` | `int32` | Source-specific field; interpret using its registered source. |
| `gp_code_2010` | `double` | Source-local GP serial; never use alone as a cross-block identifier. |
| `block_code_2010` | `int32` | Source-specific field; interpret using its registered source. |
| `block_name_2010` | `string` | Source-specific field; interpret using its registered source. |
| `sr_gp_combo_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_reservation_status_2010` | `string` | Source-specific field; interpret using its registered source. |
| `elected_sarpanch_name_2010` | `string` | Saved source winner-name field; 2021 values are denormalized and must not resolve conflicting candidate markers. |
| `husband_spouse_name_2010` | `string` | Source-specific field; interpret using its registered source. |
| `candidate_res_status_2010` | `string` | Source-specific field; interpret using its registered source. |
| `age_2010` | `string` | Source-specific field; interpret using its registered source. |
| `sex_2010` | `string` | Source-specific field; interpret using its registered source. |
| `education_2010` | `string` | Source-specific field; interpret using its registered source. |
| `address_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_fin_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_res_status_fin_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_res_status_fin_eng_2010` | `string` | English transliteration or reviewed label; source text is retained. |
| `candidate_res_status_fin_2010` | `string` | Source-specific field; interpret using its registered source. |
| `cand_sex_fin_2010` | `string` | Source-specific field; interpret using its registered source. |
| `age_fin_2010` | `double` | Source-specific field; interpret using its registered source. |
| `educ_fin_2010` | `string` | Source-specific field; interpret using its registered source. |
| `educ_fin_eng_2010` | `string` | English transliteration or reviewed label; source text is retained. |
| `gp_name_eng_2010` | `string` | English transliteration or reviewed label; source text is retained. |
| `district_name_eng_2010` | `string` | English transliteration or reviewed label; source text is retained. |
| `block_name_eng_2010` | `string` | English transliteration or reviewed label; source text is retained. |
| `elected_sarpanch_name_eng_2010` | `string` | English transliteration or reviewed label; source text is retained. |
| `husband_spouse_name_eng_2010` | `string` | English transliteration or reviewed label; source text is retained. |
| `source_row_number_2010` | `int32` | One-based original source-table row before filtering winner markers. |
| `election_gp_key_2010` | `string` | Immutable source-election record key. Historical keys use source row ordinals; 2021 uses publisher candidate IDs. |
| `women_reserved_2010` | `int32` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `winner_woman_2010` | `int32` | 1 for a source-reported female winner, 0 for male, null for missing sex or a conflicting winner claim. |
| `reservation_class_2010` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `block_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_reservation_status_2015` | `string` | Source-specific field; interpret using its registered source. |
| `elected_sarpanch_name_2015` | `string` | Saved source winner-name field; 2021 values are denormalized and must not resolve conflicting candidate markers. |
| `father_husband_2015` | `string` | Source-specific field; interpret using its registered source. |
| `candidate_reservation_status_2015` | `string` | Source-specific field; interpret using its registered source. |
| `educational_qualification_2015` | `string` | Source-specific field; interpret using its registered source. |
| `sex_2015` | `string` | Source-specific field; interpret using its registered source. |
| `valid_votes_received_2015` | `string` | Source-specific field; interpret using its registered source. |
| `votes_received_percent_2015` | `string` | Source-specific field; interpret using its registered source. |
| `voting_percent_2015` | `string` | Source-specific field; interpret using its registered source. |
| `result_2015` | `string` | Source-specific field; interpret using its registered source. |
| `district_name_2015` | `string` | Source-specific field; interpret using its registered source. |
| `block_num_2015` | `string` | Source-specific field; interpret using its registered source. |
| `block_name_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_num_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_reservation_status_eng_2015` | `string` | English transliteration or reviewed label; source text is retained. |
| `candidate_reservation_status_eng_2015` | `string` | English transliteration or reviewed label; source text is retained. |
| `gp_name_eng_2015` | `string` | English transliteration or reviewed label; source text is retained. |
| `district_name_eng_2015` | `string` | English transliteration or reviewed label; source text is retained. |
| `block_name_eng_2015` | `string` | English transliteration or reviewed label; source text is retained. |
| `elected_sarpanch_name_eng_2015` | `string` | English transliteration or reviewed label; source text is retained. |
| `husband_spouse_name_eng_2015` | `string` | English transliteration or reviewed label; source text is retained. |
| `source_row_number_2015` | `int32` | One-based original source-table row before filtering winner markers. |
| `election_gp_key_2015` | `string` | Immutable source-election record key. Historical keys use source row ordinals; 2021 uses publisher candidate IDs. |
| `women_reserved_2015` | `int32` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `winner_woman_2015` | `int32` | 1 for a source-reported female winner, 0 for male, null for missing sex or a conflicting winner claim. |
| `reservation_class_2015` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `district_name_2021` | `string` | Source-specific field; interpret using its registered source. |
| `block_name_2021` | `string` | Source-specific field; interpret using its registered source. |
| `gp_2021` | `string` | Source-specific field; interpret using its registered source. |
| `gp_reservation_status_2021` | `string` | Source-specific field; interpret using its registered source. |
| `id_2021` | `int32` | Publisher candidate identifier in the 2021 candidate table. |
| `candidate_2021` | `string` | Publisher's actual candidate name, distinct from the denormalized elected_sarpanch_name field. |
| `father_husband_2021` | `string` | Source-specific field; interpret using its registered source. |
| `sex_2021` | `string` | Source-specific field; interpret using its registered source. |
| `age_2021` | `int32` | Source-specific field; interpret using its registered source. |
| `education_2021` | `string` | Source-specific field; interpret using its registered source. |
| `candidate_reservation_status_2021` | `string` | Source-specific field; interpret using its registered source. |
| `movable_property_2021` | `int32` | Source-specific field; interpret using its registered source. |
| `immovable_property_2021` | `int32` | Source-specific field; interpret using its registered source. |
| `criminal_history_2021_2021` | `string` | Source-specific field; interpret using its registered source. |
| `vote_percentage_2021` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `result_2021` | `string` | Source-specific field; interpret using its registered source. |
| `gp_reservation_status_eng_2021` | `string` | English transliteration or reviewed label; source text is retained. |
| `candidate_reservation_status_eng_2021` | `string` | English transliteration or reviewed label; source text is retained. |
| `gp_num_2021` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_2021` | `string` | Source-specific field; interpret using its registered source. |
| `elected_sarpanch_name_2021` | `string` | Saved source winner-name field; 2021 values are denormalized and must not resolve conflicting candidate markers. |
| `gp_name_eng_2021` | `string` | English transliteration or reviewed label; source text is retained. |
| `district_name_eng_2021` | `string` | English transliteration or reviewed label; source text is retained. |
| `block_name_eng_2021` | `string` | English transliteration or reviewed label; source text is retained. |
| `elected_sarpanch_name_eng_2021` | `string` | English transliteration or reviewed label; source text is retained. |
| `husband_spouse_name_eng_2021` | `string` | English transliteration or reviewed label; source text is retained. |
| `source_row_number_2021` | `int32` | One-based original source-table row before filtering winner markers. |
| `election_gp_key_2021` | `string` | Immutable source-election record key. Historical keys use source row ordinals; 2021 uses publisher candidate IDs. |
| `women_reserved_2021` | `int32` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `winner_woman_2021` | `int32` | 1 for a source-reported female winner, 0 for male, null for missing sex or a conflicting winner claim. |
| `reservation_class_2021` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |

## panels/gp_panel_2010_2015

one linked source-record pair or four-election history. Key: key_2010, key_2015.

| Column | Type | Meaning |
| --- | --- | --- |
| `key_2010` | `string` | Source-specific field; interpret using its registered source. |
| `key_2015` | `string` | Source-specific field; interpret using its registered source. |
| `original_filename_2010` | `string` | Original parsed document filename, retained for document/page provenance. |
| `page_2010` | `int32` | Recorded page locator in the original parsed document. |
| `order_2010` | `int32` | Source-specific field; interpret using its registered source. |
| `district_name_2010` | `string` | Source-specific field; interpret using its registered source. |
| `sr_no_2010` | `int32` | Source-specific field; interpret using its registered source. |
| `gp_code_2010` | `double` | Source-local GP serial; never use alone as a cross-block identifier. |
| `block_code_2010` | `int32` | Source-specific field; interpret using its registered source. |
| `block_name_2010` | `string` | Source-specific field; interpret using its registered source. |
| `sr_gp_combo_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_reservation_status_2010` | `string` | Source-specific field; interpret using its registered source. |
| `elected_sarpanch_name_2010` | `string` | Saved source winner-name field; 2021 values are denormalized and must not resolve conflicting candidate markers. |
| `husband_spouse_name_2010` | `string` | Source-specific field; interpret using its registered source. |
| `candidate_res_status_2010` | `string` | Source-specific field; interpret using its registered source. |
| `age_2010` | `string` | Source-specific field; interpret using its registered source. |
| `sex_2010` | `string` | Source-specific field; interpret using its registered source. |
| `education_2010` | `string` | Source-specific field; interpret using its registered source. |
| `address_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_fin_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_res_status_fin_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_res_status_fin_eng_2010` | `string` | English transliteration or reviewed label; source text is retained. |
| `candidate_res_status_fin_2010` | `string` | Source-specific field; interpret using its registered source. |
| `cand_sex_fin_2010` | `string` | Source-specific field; interpret using its registered source. |
| `age_fin_2010` | `double` | Source-specific field; interpret using its registered source. |
| `educ_fin_2010` | `string` | Source-specific field; interpret using its registered source. |
| `educ_fin_eng_2010` | `string` | English transliteration or reviewed label; source text is retained. |
| `gp_name_eng_2010` | `string` | English transliteration or reviewed label; source text is retained. |
| `district_name_eng_2010` | `string` | English transliteration or reviewed label; source text is retained. |
| `block_name_eng_2010` | `string` | English transliteration or reviewed label; source text is retained. |
| `elected_sarpanch_name_eng_2010` | `string` | English transliteration or reviewed label; source text is retained. |
| `husband_spouse_name_eng_2010` | `string` | English transliteration or reviewed label; source text is retained. |
| `source_row_number_2010` | `int32` | One-based original source-table row before filtering winner markers. |
| `election_gp_key_2010` | `string` | Immutable source-election record key. Historical keys use source row ordinals; 2021 uses publisher candidate IDs. |
| `women_reserved_2010` | `int32` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `winner_woman_2010` | `int32` | 1 for a source-reported female winner, 0 for male, null for missing sex or a conflicting winner claim. |
| `reservation_class_2010` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `block_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_reservation_status_2015` | `string` | Source-specific field; interpret using its registered source. |
| `elected_sarpanch_name_2015` | `string` | Saved source winner-name field; 2021 values are denormalized and must not resolve conflicting candidate markers. |
| `father_husband_2015` | `string` | Source-specific field; interpret using its registered source. |
| `candidate_reservation_status_2015` | `string` | Source-specific field; interpret using its registered source. |
| `educational_qualification_2015` | `string` | Source-specific field; interpret using its registered source. |
| `sex_2015` | `string` | Source-specific field; interpret using its registered source. |
| `valid_votes_received_2015` | `string` | Source-specific field; interpret using its registered source. |
| `votes_received_percent_2015` | `string` | Source-specific field; interpret using its registered source. |
| `voting_percent_2015` | `string` | Source-specific field; interpret using its registered source. |
| `result_2015` | `string` | Source-specific field; interpret using its registered source. |
| `district_name_2015` | `string` | Source-specific field; interpret using its registered source. |
| `block_num_2015` | `string` | Source-specific field; interpret using its registered source. |
| `block_name_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_num_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_reservation_status_eng_2015` | `string` | English transliteration or reviewed label; source text is retained. |
| `candidate_reservation_status_eng_2015` | `string` | English transliteration or reviewed label; source text is retained. |
| `gp_name_eng_2015` | `string` | English transliteration or reviewed label; source text is retained. |
| `district_name_eng_2015` | `string` | English transliteration or reviewed label; source text is retained. |
| `block_name_eng_2015` | `string` | English transliteration or reviewed label; source text is retained. |
| `elected_sarpanch_name_eng_2015` | `string` | English transliteration or reviewed label; source text is retained. |
| `husband_spouse_name_eng_2015` | `string` | English transliteration or reviewed label; source text is retained. |
| `source_row_number_2015` | `int32` | One-based original source-table row before filtering winner markers. |
| `election_gp_key_2015` | `string` | Immutable source-election record key. Historical keys use source row ordinals; 2021 uses publisher candidate IDs. |
| `women_reserved_2015` | `int32` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `winner_woman_2015` | `int32` | 1 for a source-reported female winner, 0 for male, null for missing sex or a conflicting winner claim. |
| `reservation_class_2015` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |

## panels/gp_panel_2015_2021

one linked source-record pair or four-election history. Key: key_2015, key_2021.

| Column | Type | Meaning |
| --- | --- | --- |
| `key_2015` | `string` | Source-specific field; interpret using its registered source. |
| `key_2021` | `string` | Source-specific field; interpret using its registered source. |
| `block_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_reservation_status_2015` | `string` | Source-specific field; interpret using its registered source. |
| `elected_sarpanch_name_2015` | `string` | Saved source winner-name field; 2021 values are denormalized and must not resolve conflicting candidate markers. |
| `father_husband_2015` | `string` | Source-specific field; interpret using its registered source. |
| `candidate_reservation_status_2015` | `string` | Source-specific field; interpret using its registered source. |
| `educational_qualification_2015` | `string` | Source-specific field; interpret using its registered source. |
| `sex_2015` | `string` | Source-specific field; interpret using its registered source. |
| `valid_votes_received_2015` | `string` | Source-specific field; interpret using its registered source. |
| `votes_received_percent_2015` | `string` | Source-specific field; interpret using its registered source. |
| `voting_percent_2015` | `string` | Source-specific field; interpret using its registered source. |
| `result_2015` | `string` | Source-specific field; interpret using its registered source. |
| `district_name_2015` | `string` | Source-specific field; interpret using its registered source. |
| `block_num_2015` | `string` | Source-specific field; interpret using its registered source. |
| `block_name_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_num_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_reservation_status_eng_2015` | `string` | English transliteration or reviewed label; source text is retained. |
| `candidate_reservation_status_eng_2015` | `string` | English transliteration or reviewed label; source text is retained. |
| `gp_name_eng_2015` | `string` | English transliteration or reviewed label; source text is retained. |
| `district_name_eng_2015` | `string` | English transliteration or reviewed label; source text is retained. |
| `block_name_eng_2015` | `string` | English transliteration or reviewed label; source text is retained. |
| `elected_sarpanch_name_eng_2015` | `string` | English transliteration or reviewed label; source text is retained. |
| `husband_spouse_name_eng_2015` | `string` | English transliteration or reviewed label; source text is retained. |
| `source_row_number_2015` | `int32` | One-based original source-table row before filtering winner markers. |
| `election_gp_key_2015` | `string` | Immutable source-election record key. Historical keys use source row ordinals; 2021 uses publisher candidate IDs. |
| `women_reserved_2015` | `int32` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `winner_woman_2015` | `int32` | 1 for a source-reported female winner, 0 for male, null for missing sex or a conflicting winner claim. |
| `reservation_class_2015` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |
| `district_name_2021` | `string` | Source-specific field; interpret using its registered source. |
| `block_name_2021` | `string` | Source-specific field; interpret using its registered source. |
| `gp_2021` | `string` | Source-specific field; interpret using its registered source. |
| `gp_reservation_status_2021` | `string` | Source-specific field; interpret using its registered source. |
| `id_2021` | `int32` | Publisher candidate identifier in the 2021 candidate table. |
| `candidate_2021` | `string` | Publisher's actual candidate name, distinct from the denormalized elected_sarpanch_name field. |
| `father_husband_2021` | `string` | Source-specific field; interpret using its registered source. |
| `sex_2021` | `string` | Source-specific field; interpret using its registered source. |
| `age_2021` | `int32` | Source-specific field; interpret using its registered source. |
| `education_2021` | `string` | Source-specific field; interpret using its registered source. |
| `candidate_reservation_status_2021` | `string` | Source-specific field; interpret using its registered source. |
| `movable_property_2021` | `int32` | Source-specific field; interpret using its registered source. |
| `immovable_property_2021` | `int32` | Source-specific field; interpret using its registered source. |
| `criminal_history_2021_2021` | `string` | Source-specific field; interpret using its registered source. |
| `vote_percentage_2021` | `double` | Source-stated vote share in percentage points, not a vote count. |
| `result_2021` | `string` | Source-specific field; interpret using its registered source. |
| `gp_reservation_status_eng_2021` | `string` | English transliteration or reviewed label; source text is retained. |
| `candidate_reservation_status_eng_2021` | `string` | English transliteration or reviewed label; source text is retained. |
| `gp_num_2021` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_2021` | `string` | Source-specific field; interpret using its registered source. |
| `elected_sarpanch_name_2021` | `string` | Saved source winner-name field; 2021 values are denormalized and must not resolve conflicting candidate markers. |
| `gp_name_eng_2021` | `string` | English transliteration or reviewed label; source text is retained. |
| `district_name_eng_2021` | `string` | English transliteration or reviewed label; source text is retained. |
| `block_name_eng_2021` | `string` | English transliteration or reviewed label; source text is retained. |
| `elected_sarpanch_name_eng_2021` | `string` | English transliteration or reviewed label; source text is retained. |
| `husband_spouse_name_eng_2021` | `string` | English transliteration or reviewed label; source text is retained. |
| `source_row_number_2021` | `int32` | One-based original source-table row before filtering winner markers. |
| `election_gp_key_2021` | `string` | Immutable source-election record key. Historical keys use source row ordinals; 2021 uses publisher candidate IDs. |
| `women_reserved_2021` | `int32` | True/1 for a women-reserved seat, false/0 for a known non-women-reserved seat, null if unknown. |
| `winner_woman_2021` | `int32` | 1 for a source-reported female winner, 0 for male, null for missing sex or a conflicting winner claim. |
| `reservation_class_2021` | `string` | general, obc, sc, st, or unknown seat reservation. Unknown is not general/unreserved. |

## weaver/weaver_20250302_wide

one source GP identifier, wide across waves. Key: gp_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `gp_id` | `string` | Identifier within the external Weaver source vintage; cross-wave meaning differs between vintages. |
| `districtname_lgd21_2010` | `string` | Source-specific field; interpret using its registered source. |
| `districtname_lgd21_2015` | `string` | Source-specific field; interpret using its registered source. |
| `districtname_lgd21_2020` | `string` | Source-specific field; interpret using its registered source. |
| `districtcode_lgd21_2010` | `string` | Source-specific field; interpret using its registered source. |
| `districtcode_lgd21_2015` | `string` | Source-specific field; interpret using its registered source. |
| `districtcode_lgd21_2020` | `string` | Source-specific field; interpret using its registered source. |
| `blockcode_lgd21_2010` | `string` | Source-specific field; interpret using its registered source. |
| `blockcode_lgd21_2015` | `string` | Source-specific field; interpret using its registered source. |
| `blockcode_lgd21_2020` | `string` | Source-specific field; interpret using its registered source. |
| `gp_code_ele20_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_code_ele20_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_code_ele20_2020` | `string` | Source-specific field; interpret using its registered source. |
| `gp_code_ele15_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_code_ele15_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_code_ele15_2020` | `string` | Source-specific field; interpret using its registered source. |
| `gp_code_lgd21_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_code_lgd21_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_code_lgd21_2020` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_lgd21_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_lgd21_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_lgd21_2020` | `string` | Source-specific field; interpret using its registered source. |
| `reservation_2010` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_2015` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_2020` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_female_2010` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_female_2015` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_female_2020` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_cancelled_2010` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_cancelled_2015` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_cancelled_2020` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_returned_2010` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_returned_2015` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_returned_2020` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_2010` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_2015` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_2020` | `double` | Source-specific field; interpret using its registered source. |
| `result_type_2010` | `double` | Source-specific field; interpret using its registered source. |
| `result_type_2015` | `double` | Source-specific field; interpret using its registered source. |
| `result_type_2020` | `double` | Source-specific field; interpret using its registered source. |
| `total_electorate_2010` | `double` | Source-specific field; interpret using its registered source. |
| `total_electorate_2015` | `double` | Source-specific field; interpret using its registered source. |
| `total_electorate_2020` | `double` | Source-specific field; interpret using its registered source. |
| `total_votes_2010` | `double` | Source-specific field; interpret using its registered source. |
| `total_votes_2015` | `double` | Source-specific field; interpret using its registered source. |
| `total_votes_2020` | `double` | Source-specific field; interpret using its registered source. |
| `total_votes_valid_2010` | `double` | Source-specific field; interpret using its registered source. |
| `total_votes_valid_2015` | `double` | Source-specific field; interpret using its registered source. |
| `total_votes_valid_2020` | `double` | Source-specific field; interpret using its registered source. |
| `total_votes_invalid_2010` | `double` | Source-specific field; interpret using its registered source. |
| `total_votes_invalid_2015` | `double` | Source-specific field; interpret using its registered source. |
| `total_votes_invalid_2020` | `double` | Source-specific field; interpret using its registered source. |
| `turnout_2010` | `double` | Source-specific field; interpret using its registered source. |
| `turnout_2015` | `double` | Source-specific field; interpret using its registered source. |
| `turnout_2020` | `double` | Source-specific field; interpret using its registered source. |
| `margin_of_victory_2010` | `double` | Source-specific field; interpret using its registered source. |
| `margin_of_victory_2015` | `double` | Source-specific field; interpret using its registered source. |
| `margin_of_victory_2020` | `double` | Source-specific field; interpret using its registered source. |
| `margin_of_victory_votes_2010` | `double` | Source-specific field; interpret using its registered source. |
| `margin_of_victory_votes_2015` | `double` | Source-specific field; interpret using its registered source. |
| `margin_of_victory_votes_2020` | `double` | Source-specific field; interpret using its registered source. |
| `effective_candidates_2010` | `double` | Source-specific field; interpret using its registered source. |
| `effective_candidates_2015` | `double` | Source-specific field; interpret using its registered source. |
| `effective_candidates_2020` | `double` | Source-specific field; interpret using its registered source. |
| `hhi_percent_2010` | `double` | Source-specific field; interpret using its registered source. |
| `hhi_percent_2015` | `double` | Source-specific field; interpret using its registered source. |
| `hhi_percent_2020` | `double` | Source-specific field; interpret using its registered source. |
| `candidates_pc_2010` | `double` | Source-specific field; interpret using its registered source. |
| `candidates_pc_2015` | `double` | Source-specific field; interpret using its registered source. |
| `candidates_pc_2020` | `double` | Source-specific field; interpret using its registered source. |
| `effective_candidates_pc_2010` | `double` | Source-specific field; interpret using its registered source. |
| `effective_candidates_pc_2015` | `double` | Source-specific field; interpret using its registered source. |
| `effective_candidates_pc_2020` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_sc_2010` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_sc_2015` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_sc_2020` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_st_2010` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_st_2015` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_st_2020` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_obc_2010` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_obc_2015` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_obc_2020` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_gen_2010` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_gen_2015` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_gen_2020` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_female_2010` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_female_2015` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_female_2020` | `double` | Source-specific field; interpret using its registered source. |
| `avg_education_2010` | `double` | Source-specific field; interpret using its registered source. |
| `avg_education_2015` | `double` | Source-specific field; interpret using its registered source. |
| `avg_education_2020` | `double` | Source-specific field; interpret using its registered source. |
| `avg_criminal_history_2010` | `double` | Source-specific field; interpret using its registered source. |
| `avg_criminal_history_2015` | `double` | Source-specific field; interpret using its registered source. |
| `avg_criminal_history_2020` | `double` | Source-specific field; interpret using its registered source. |
| `avg_total_assets_asinh_2010` | `double` | Source-specific field; interpret using its registered source. |
| `avg_total_assets_asinh_2015` | `double` | Source-specific field; interpret using its registered source. |
| `avg_total_assets_asinh_2020` | `double` | Source-specific field; interpret using its registered source. |
| `avg_zero_moveable_2010` | `double` | Source-specific field; interpret using its registered source. |
| `avg_zero_moveable_2015` | `double` | Source-specific field; interpret using its registered source. |
| `avg_zero_moveable_2020` | `double` | Source-specific field; interpret using its registered source. |
| `avg_zero_immoveable_2010` | `double` | Source-specific field; interpret using its registered source. |
| `avg_zero_immoveable_2015` | `double` | Source-specific field; interpret using its registered source. |
| `avg_zero_immoveable_2020` | `double` | Source-specific field; interpret using its registered source. |
| `avg_age_2010` | `double` | Source-specific field; interpret using its registered source. |
| `avg_age_2015` | `double` | Source-specific field; interpret using its registered source. |
| `avg_age_2020` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_sc_2010` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_sc_2015` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_sc_2020` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_st_2010` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_st_2015` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_st_2020` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_obc_2010` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_obc_2015` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_obc_2020` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_highcaste_2010` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_highcaste_2015` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_highcaste_2020` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_female_2010` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_female_2015` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_female_2020` | `double` | Source-specific field; interpret using its registered source. |
| `avg_m_education_2010` | `double` | Source-specific field; interpret using its registered source. |
| `avg_m_education_2015` | `double` | Source-specific field; interpret using its registered source. |
| `avg_m_education_2020` | `double` | Source-specific field; interpret using its registered source. |
| `avg_m_criminal_history_2010` | `double` | Source-specific field; interpret using its registered source. |
| `avg_m_criminal_history_2015` | `double` | Source-specific field; interpret using its registered source. |
| `avg_m_criminal_history_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_female_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_female_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_female_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_female_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_female_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_female_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_age_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_age_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_age_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_age_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_age_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_age_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_education_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_education_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_education_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_education_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_education_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_education_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_caste_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_caste_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_caste_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_caste_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_caste_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_caste_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_moveable_assets_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_moveable_assets_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_moveable_assets_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_moveable_assets_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_moveable_assets_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_moveable_assets_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_moveable_assets_asinh_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_moveable_assets_asinh_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_moveable_assets_asinh_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_moveable_assets_asinh_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_moveable_assets_asinh_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_moveable_assets_asinh_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_immoveable_assets_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_immoveable_assets_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_immoveable_assets_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_immoveable_assets_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_immoveable_assets_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_immoveable_assets_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_immoveable_assets_asinh_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_immoveable_assets_asinh_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_immoveable_assets_asinh_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_immoveable_assets_asinh_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_immoveable_assets_asinh_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_immoveable_assets_asinh_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_total_assets_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_total_assets_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_total_assets_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_total_assets_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_total_assets_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_total_assets_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_total_assets_asinh_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_total_assets_asinh_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_total_assets_asinh_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_total_assets_asinh_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_total_assets_asinh_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_total_assets_asinh_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_criminal_history_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_criminal_history_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_criminal_history_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_criminal_history_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_criminal_history_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_criminal_history_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_votes_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_votes_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_votes_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_votes_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_votes_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_votes_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_percent_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_percent_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_percent_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_percent_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_percent_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_percent_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_deposit_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_deposit_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_deposit_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_deposit_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_deposit_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_deposit_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_sc_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_sc_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_sc_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_sc_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_sc_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_sc_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_obc_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_obc_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_obc_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_obc_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_obc_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_obc_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_gen_caste_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_gen_caste_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_gen_caste_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_gen_caste_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_gen_caste_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_gen_caste_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_st_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_st_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_st_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_st_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_st_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_st_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_m_education_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_m_education_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_m_education_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_m_education_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_m_education_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_m_education_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_m_criminal_history_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_m_criminal_history_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_m_criminal_history_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_m_criminal_history_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_m_criminal_history_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_m_criminal_history_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_zero_moveable_assets_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_zero_moveable_assets_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_zero_moveable_assets_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_zero_moveable_assets_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_zero_moveable_assets_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_zero_moveable_assets_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_zero_immoveable_assets_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_zero_immoveable_assets_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_zero_immoveable_assets_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_zero_immoveable_assets_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_zero_immoveable_assets_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_zero_immoveable_assets_2020` | `double` | Source-specific field; interpret using its registered source. |
| `district_code_ele15_2010` | `string` | Source-specific field; interpret using its registered source. |
| `district_code_ele15_2015` | `string` | Source-specific field; interpret using its registered source. |
| `district_code_ele15_2020` | `string` | Source-specific field; interpret using its registered source. |
| `block_code_ele15_2010` | `string` | Source-specific field; interpret using its registered source. |
| `block_code_ele15_2015` | `string` | Source-specific field; interpret using its registered source. |
| `block_code_ele15_2020` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_ele15_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_ele15_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_ele15_2020` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_ele15_t_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_ele15_t_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_ele15_t_2020` | `string` | Source-specific field; interpret using its registered source. |
| `reservation_obc_2010` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_obc_2015` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_obc_2020` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_sc_2010` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_sc_2015` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_sc_2020` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_st_2010` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_st_2015` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_st_2020` | `double` | Source-specific field; interpret using its registered source. |
| `gp_code_jj11_2010` | `double` | Source-specific field; interpret using its registered source. |
| `gp_code_jj11_2015` | `double` | Source-specific field; interpret using its registered source. |
| `gp_code_jj11_2020` | `double` | Source-specific field; interpret using its registered source. |
| `gp_name_jj11_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_jj11_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_jj11_2020` | `string` | Source-specific field; interpret using its registered source. |
| `source_election_code_2010` | `double` | Source-specific field; interpret using its registered source. |
| `source_election_code_2015` | `double` | Source-specific field; interpret using its registered source. |
| `source_election_code_2020` | `double` | Source-specific field; interpret using its registered source. |
| `source_anchor_year` | `int32` | Source-specific field; interpret using its registered source. |
| `source_vintage` | `string` | Source-specific field; interpret using its registered source. |

## weaver/weaver_20250317_wide

one source GP identifier, wide across waves. Key: gp_id.

| Column | Type | Meaning |
| --- | --- | --- |
| `gp_id` | `string` | Identifier within the external Weaver source vintage; cross-wave meaning differs between vintages. |
| `gp_code_lgd21_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_code_lgd21_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_code_lgd21_2020` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_jj11_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_jj11_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_jj11_2020` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_lgd21_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_lgd21_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_lgd21_2020` | `string` | Source-specific field; interpret using its registered source. |
| `reservation_2010` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_2015` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_2020` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_female_2010` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_female_2015` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_female_2020` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_cancelled_2010` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_cancelled_2015` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_cancelled_2020` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_returned_2010` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_returned_2015` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_returned_2020` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_2010` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_2015` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_2020` | `double` | Source-specific field; interpret using its registered source. |
| `result_type_2010` | `double` | Source-specific field; interpret using its registered source. |
| `result_type_2015` | `double` | Source-specific field; interpret using its registered source. |
| `result_type_2020` | `double` | Source-specific field; interpret using its registered source. |
| `total_electorate_2010` | `double` | Source-specific field; interpret using its registered source. |
| `total_electorate_2015` | `double` | Source-specific field; interpret using its registered source. |
| `total_electorate_2020` | `double` | Source-specific field; interpret using its registered source. |
| `total_votes_2010` | `double` | Source-specific field; interpret using its registered source. |
| `total_votes_2015` | `double` | Source-specific field; interpret using its registered source. |
| `total_votes_2020` | `double` | Source-specific field; interpret using its registered source. |
| `total_votes_valid_2010` | `double` | Source-specific field; interpret using its registered source. |
| `total_votes_valid_2015` | `double` | Source-specific field; interpret using its registered source. |
| `total_votes_valid_2020` | `double` | Source-specific field; interpret using its registered source. |
| `total_votes_invalid_2010` | `double` | Source-specific field; interpret using its registered source. |
| `total_votes_invalid_2015` | `double` | Source-specific field; interpret using its registered source. |
| `total_votes_invalid_2020` | `double` | Source-specific field; interpret using its registered source. |
| `turnout_2010` | `double` | Source-specific field; interpret using its registered source. |
| `turnout_2015` | `double` | Source-specific field; interpret using its registered source. |
| `turnout_2020` | `double` | Source-specific field; interpret using its registered source. |
| `margin_of_victory_2010` | `double` | Source-specific field; interpret using its registered source. |
| `margin_of_victory_2015` | `double` | Source-specific field; interpret using its registered source. |
| `margin_of_victory_2020` | `double` | Source-specific field; interpret using its registered source. |
| `margin_of_victory_votes_2010` | `double` | Source-specific field; interpret using its registered source. |
| `margin_of_victory_votes_2015` | `double` | Source-specific field; interpret using its registered source. |
| `margin_of_victory_votes_2020` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_sc_2010` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_sc_2015` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_sc_2020` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_st_2010` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_st_2015` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_st_2020` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_obc_2010` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_obc_2015` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_obc_2020` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_gen_2010` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_gen_2015` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_gen_2020` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_female_2010` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_female_2015` | `double` | Source-specific field; interpret using its registered source. |
| `total_candidates_female_2020` | `double` | Source-specific field; interpret using its registered source. |
| `avg_education_2010` | `double` | Source-specific field; interpret using its registered source. |
| `avg_education_2015` | `double` | Source-specific field; interpret using its registered source. |
| `avg_education_2020` | `double` | Source-specific field; interpret using its registered source. |
| `avg_criminal_history_2010` | `double` | Source-specific field; interpret using its registered source. |
| `avg_criminal_history_2015` | `double` | Source-specific field; interpret using its registered source. |
| `avg_criminal_history_2020` | `double` | Source-specific field; interpret using its registered source. |
| `avg_total_assets_asinh_2010` | `double` | Source-specific field; interpret using its registered source. |
| `avg_total_assets_asinh_2015` | `double` | Source-specific field; interpret using its registered source. |
| `avg_total_assets_asinh_2020` | `double` | Source-specific field; interpret using its registered source. |
| `avg_zero_moveable_2010` | `double` | Source-specific field; interpret using its registered source. |
| `avg_zero_moveable_2015` | `double` | Source-specific field; interpret using its registered source. |
| `avg_zero_moveable_2020` | `double` | Source-specific field; interpret using its registered source. |
| `avg_zero_immoveable_2010` | `double` | Source-specific field; interpret using its registered source. |
| `avg_zero_immoveable_2015` | `double` | Source-specific field; interpret using its registered source. |
| `avg_zero_immoveable_2020` | `double` | Source-specific field; interpret using its registered source. |
| `avg_age_2010` | `double` | Source-specific field; interpret using its registered source. |
| `avg_age_2015` | `double` | Source-specific field; interpret using its registered source. |
| `avg_age_2020` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_sc_2010` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_sc_2015` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_sc_2020` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_st_2010` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_st_2015` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_st_2020` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_obc_2010` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_obc_2015` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_obc_2020` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_highcaste_2010` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_highcaste_2015` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_highcaste_2020` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_female_2010` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_female_2015` | `double` | Source-specific field; interpret using its registered source. |
| `frac_candidates_female_2020` | `double` | Source-specific field; interpret using its registered source. |
| `avg_m_education_2010` | `double` | Source-specific field; interpret using its registered source. |
| `avg_m_education_2015` | `double` | Source-specific field; interpret using its registered source. |
| `avg_m_education_2020` | `double` | Source-specific field; interpret using its registered source. |
| `avg_m_criminal_history_2010` | `double` | Source-specific field; interpret using its registered source. |
| `avg_m_criminal_history_2015` | `double` | Source-specific field; interpret using its registered source. |
| `avg_m_criminal_history_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_female_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_female_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_female_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_female_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_female_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_female_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_age_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_age_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_age_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_age_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_age_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_age_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_education_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_education_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_education_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_education_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_education_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_education_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_caste_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_caste_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_caste_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_caste_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_caste_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_caste_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_moveable_assets_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_moveable_assets_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_moveable_assets_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_moveable_assets_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_moveable_assets_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_moveable_assets_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_moveable_assets_asinh_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_moveable_assets_asinh_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_moveable_assets_asinh_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_moveable_assets_asinh_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_moveable_assets_asinh_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_moveable_assets_asinh_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_immoveable_assets_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_immoveable_assets_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_immoveable_assets_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_immoveable_assets_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_immoveable_assets_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_immoveable_assets_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_immoveable_assets_asinh_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_immoveable_assets_asinh_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_immoveable_assets_asinh_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_immoveable_assets_asinh_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_immoveable_assets_asinh_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_immoveable_assets_asinh_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_total_assets_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_total_assets_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_total_assets_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_total_assets_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_total_assets_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_total_assets_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_total_assets_asinh_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_total_assets_asinh_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_total_assets_asinh_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_total_assets_asinh_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_total_assets_asinh_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_total_assets_asinh_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_criminal_history_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_criminal_history_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_criminal_history_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_criminal_history_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_criminal_history_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_criminal_history_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_votes_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_votes_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_votes_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_votes_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_votes_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_votes_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_percent_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_percent_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_percent_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_percent_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_percent_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_percent_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_deposit_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_deposit_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_deposit_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_deposit_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_deposit_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_deposit_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_sc_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_sc_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_sc_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_sc_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_sc_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_sc_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_obc_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_obc_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_obc_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_obc_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_obc_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_obc_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_gen_caste_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_gen_caste_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_gen_caste_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_gen_caste_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_gen_caste_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_gen_caste_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_st_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_st_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_st_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_st_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_st_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_st_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_m_education_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_m_education_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_m_education_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_m_education_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_m_education_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_m_education_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_m_criminal_history_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_m_criminal_history_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_m_criminal_history_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_m_criminal_history_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_m_criminal_history_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_m_criminal_history_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_zero_moveable_assets_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_zero_moveable_assets_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_zero_moveable_assets_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_zero_moveable_assets_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_zero_moveable_assets_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_zero_moveable_assets_2020` | `double` | Source-specific field; interpret using its registered source. |
| `winner_zero_immoveable_assets_2010` | `double` | Source-specific field; interpret using its registered source. |
| `winner_zero_immoveable_assets_2015` | `double` | Source-specific field; interpret using its registered source. |
| `winner_zero_immoveable_assets_2020` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_zero_immoveable_assets_2010` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_zero_immoveable_assets_2015` | `double` | Source-specific field; interpret using its registered source. |
| `runnerup_zero_immoveable_assets_2020` | `double` | Source-specific field; interpret using its registered source. |
| `district_code_ele15_2010` | `string` | Source-specific field; interpret using its registered source. |
| `district_code_ele15_2015` | `string` | Source-specific field; interpret using its registered source. |
| `district_code_ele15_2020` | `string` | Source-specific field; interpret using its registered source. |
| `block_code_ele15_2010` | `string` | Source-specific field; interpret using its registered source. |
| `block_code_ele15_2015` | `string` | Source-specific field; interpret using its registered source. |
| `block_code_ele15_2020` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_ele15_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_ele15_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_ele15_2020` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_ele15_t_2010` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_ele15_t_2015` | `string` | Source-specific field; interpret using its registered source. |
| `gp_name_ele15_t_2020` | `string` | Source-specific field; interpret using its registered source. |
| `reservation_obc_2010` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_obc_2015` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_obc_2020` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_sc_2010` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_sc_2015` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_sc_2020` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_st_2010` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_st_2015` | `double` | Source-specific field; interpret using its registered source. |
| `reservation_st_2020` | `double` | Source-specific field; interpret using its registered source. |
| `shrid_2010` | `string` | Source-specific field; interpret using its registered source. |
| `shrid_2015` | `string` | Source-specific field; interpret using its registered source. |
| `shrid_2020` | `string` | Source-specific field; interpret using its registered source. |
| `statename_2010` | `string` | Source-specific field; interpret using its registered source. |
| `statename_2015` | `string` | Source-specific field; interpret using its registered source. |
| `statename_2020` | `string` | Source-specific field; interpret using its registered source. |
| `gp_code_jj11_2010` | `double` | Source-specific field; interpret using its registered source. |
| `gp_code_jj11_2015` | `double` | Source-specific field; interpret using its registered source. |
| `gp_code_jj11_2020` | `double` | Source-specific field; interpret using its registered source. |
| `pc11_state_id_2010` | `string` | Source-specific field; interpret using its registered source. |
| `pc11_state_id_2015` | `string` | Source-specific field; interpret using its registered source. |
| `pc11_state_id_2020` | `string` | Source-specific field; interpret using its registered source. |
| `pc11_district_id_2010` | `string` | Source-specific field; interpret using its registered source. |
| `pc11_district_id_2015` | `string` | Source-specific field; interpret using its registered source. |
| `pc11_district_id_2020` | `string` | Source-specific field; interpret using its registered source. |
| `pc11_district_id_num_2010` | `double` | Source-specific field; interpret using its registered source. |
| `pc11_district_id_num_2015` | `double` | Source-specific field; interpret using its registered source. |
| `pc11_district_id_num_2020` | `double` | Source-specific field; interpret using its registered source. |
| `pc11_subdistrict_id_2010` | `string` | Source-specific field; interpret using its registered source. |
| `pc11_subdistrict_id_2015` | `string` | Source-specific field; interpret using its registered source. |
| `pc11_subdistrict_id_2020` | `string` | Source-specific field; interpret using its registered source. |
| `pc11_cdblock_id_2010` | `string` | Source-specific field; interpret using its registered source. |
| `pc11_cdblock_id_2015` | `string` | Source-specific field; interpret using its registered source. |
| `pc11_cdblock_id_2020` | `string` | Source-specific field; interpret using its registered source. |
| `pc11_cdblock_id_num_2010` | `double` | Source-specific field; interpret using its registered source. |
| `pc11_cdblock_id_num_2015` | `double` | Source-specific field; interpret using its registered source. |
| `pc11_cdblock_id_num_2020` | `double` | Source-specific field; interpret using its registered source. |
| `pc11_cdblock_name_2010` | `string` | Source-specific field; interpret using its registered source. |
| `pc11_cdblock_name_2015` | `string` | Source-specific field; interpret using its registered source. |
| `pc11_cdblock_name_2020` | `string` | Source-specific field; interpret using its registered source. |
| `subdistrictcode_lgd21_2010` | `string` | Source-specific field; interpret using its registered source. |
| `subdistrictcode_lgd21_2015` | `string` | Source-specific field; interpret using its registered source. |
| `subdistrictcode_lgd21_2020` | `string` | Source-specific field; interpret using its registered source. |
| `subdistrictname_lgd21_2010` | `string` | Source-specific field; interpret using its registered source. |
| `subdistrictname_lgd21_2015` | `string` | Source-specific field; interpret using its registered source. |
| `subdistrictname_lgd21_2020` | `string` | Source-specific field; interpret using its registered source. |
| `blockname_lgd21_2010` | `string` | Source-specific field; interpret using its registered source. |
| `blockname_lgd21_2015` | `string` | Source-specific field; interpret using its registered source. |
| `blockname_lgd21_2020` | `string` | Source-specific field; interpret using its registered source. |
| `source_election_code_2010` | `double` | Source-specific field; interpret using its registered source. |
| `source_election_code_2015` | `double` | Source-specific field; interpret using its registered source. |
| `source_election_code_2020` | `double` | Source-specific field; interpret using its registered source. |
| `source_anchor_year` | `int32` | Source-specific field; interpret using its registered source. |
| `anchor_pc11_district_id` | `string` | Source-specific field; interpret using its registered source. |
| `anchor_pc11_cdblock_id` | `string` | Source-specific field; interpret using its registered source. |
| `source_vintage` | `string` | Source-specific field; interpret using its registered source. |
| `pc11_district_id_conflict` | `bool` | Source-specific field; interpret using its registered source. |
| `pc11_cdblock_id_conflict` | `bool` | Source-specific field; interpret using its registered source. |

