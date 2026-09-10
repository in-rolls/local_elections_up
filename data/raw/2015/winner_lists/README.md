# Uttar Pradesh local-election winners, 2015

This collection is maintained within the [UP local-election repository](../../../../README.md).

Winner lists for five Uttar Pradesh offices, saved from the State Election Commission under the original 2015 collection label. This collection contains 226 original CSVs and five Parquet files with 140,709 records. Each Parquet row retains its source filename and row number.

## Data

| Parquet file | Office | Rows | Source CSVs | Unopposed |
| --- | --- | ---: | ---: | ---: |
| [gp_heads_2015.parquet](../../../interim/winner_lists_2015/gp_heads_2015.parquet) | Gram Panchayat Pradhan | 59,019 | 75 | 201 |
| [block_members_2015.parquet](../../../interim/winner_lists_2015/block_members_2015.parquet) | Kshetra Panchayat member | 77,743 | 75 | 2,017 |
| [district_members_2015.parquet](../../../interim/winner_lists_2015/district_members_2015.parquet) | Zila Panchayat member | 3,057 | 74 | 18 |
| [block_heads_2015.parquet](../../../interim/winner_lists_2015/block_heads_2015.parquet) | Kshetra Panchayat Pramukh | 816 | 1 | 385 |
| [district_heads_2015.parquet](../../../interim/winner_lists_2015/district_heads_2015.parquet) | Zila Panchayat Adhyaksh | 74 | 1 | 38 |

The first three offices have district-specific CSVs. The last two have one statewide CSV each, with district or district-panchayat labels in their columns. [MANIFEST.json](../../../interim/winner_lists_2015/MANIFEST.json) records file hashes, source hashes, schemas, and counts. [columns.json](columns.json) maps every original filename and Hindi column heading to its export.

The broader [UP local-election dataset](https://github.com/in-rolls/local_elections_up) provides standardized Gram Panchayat records across election years. This directory preserves the five-office source collection.

## Columns

A row is a record from the commission's **winner list**. `परिणाम` describes whether the election was contested (`सविरोध`) or unopposed (`निर्विरोध`). It does not label winners and losers. Derived tables omit the source mobile-number column. Other original values remain strings, including votes and percentages; empty cells become null. Whitespace and spelling are retained. Original CSV bytes, including the omitted column, are preserved in this directory.

| Column | Meaning |
| --- | --- |
| `collection_year` | 2015, the source collection label; exact polling dates are not recorded by these CSVs |
| `post` | Office, using its original Hindi label |
| `district_from_filename` | District label from a district-specific CSV's filename; null for the two statewide files |
| `district_raw`, `district_body_raw` | District or district-panchayat label printed in a statewide file |
| `block_raw`, `block_body_raw` | Block or Kshetra Panchayat label, where supplied |
| `gram_panchayat_raw` | Gram Panchayat label for Pradhan records |
| `block_ward_raw`, `district_ward_raw` | Ward label for the corresponding member office |
| `seat_reservation_raw` | Reservation of the seat (`पद का आरक्षण`) |
| `winner_name_raw`, `relation_name_raw` | Listed winner and father/husband name |
| `candidate_reservation_raw` | Candidate's reservation category (`प्रत्याशी का आरक्षण`), distinct from seat reservation |
| `education_raw`, `gender_raw` | Source-reported education and gender |
| `valid_votes_raw` | `प्राप्त वैध मत`, valid votes received |
| `vote_percent_raw` | `प्राप्त मत %`, votes received as a percentage |
| `turnout_percent_raw` | `मतदान %`, turnout percentage |
| `contest_status_raw`, `unopposed` | Original contested/unopposed label and its Boolean mapping |
| `source_file`, `source_row` | Original CSV filename and one-based data-row number, excluding the header |
| `winner_missing` | Whether the source winner name is blank; false for every currently published row |

Geographic columns vary by office. The exact column set and Arrow types for each file are in the manifest. Source labels are not stable administrative identifiers, and filenames can use district names adopted after 2015.

## Coverage and known gaps

The files cover five offices, with 75 district files for Pradhans and block members and 74 for district members. These are counts of saved files, not a verified completeness assessment against the electoral roll or all seats. The collection does not include losing candidates.

The original collector did not save page responses, acquisition logs, or capture timestamps. Its notebook visited district and office selections on the commission's winner-list page. The exports preserve every saved row, including repeated records, and do not repair source spellings or infer missing administrative identifiers. The 138,050 contested and 2,659 unopposed records describe these files; they should not be treated as validated statewide totals.

## How collected

| Stage | Source and method | Output |
| --- | --- | --- |
| Collection | District and office selections at the [UP State Election Commission winner-list page](http://sec.up.nic.in/ElecLive/WinnerList.aspx), using the original notebook | 226 CSVs in this directory |
| Conversion | Offline header checks, explicit field mapping, and source provenance | Five Parquet files and a manifest under `data/interim/winner_lists_2015/` |
| Verification | Compare every retained Parquet field and schema with its CSV inputs, then check source and output hashes | `make verify-2015` |

The original collection notebook is available at [commit 7894623](https://github.com/in-rolls/local_elections_up_2015/tree/789462339f5661aa31dd4c05c56bce5f46b5bb94/scripts). The current tools operate on saved files.

## Usage

Run from the UP repository root:

```bash
uv sync --frozen --all-groups
make winner-lists-2015
make verify-2015
```

For a separate output directory:

```bash
uv run --all-groups python scripts/convert_winner_lists_2015.py --out /tmp/up-winner-lists
```

The converter rejects unknown headers, unknown contest-status labels, empty
files, and missing or unlisted CSVs. Each output is replaced atomically. Tests
verify original source hashes and every retained field in all exported rows.
These tables are source-derived intermediates; rebuilding them does not change
the existing multi-year release under `data/fin/`.

The [source manifest](SOURCE_MANIFEST.json) pins the original repository commit,
paths, byte counts, and SHA-256 hashes. Capture timestamps are unknown. Exact
polling dates may differ across offices; `collection_year` records the original
collection label rather than inferring a polling date.

## Citation

Suriyan Laohaprapanon and Gaurav Sood, *Uttar Pradesh local-election winners, 2015*. Identify the repository commit used. [CITATION.cff](CITATION.cff) provides machine-readable citation metadata.

## License

The imported converter and tests are distributed under the [MIT License](CODE_LICENSE). Election records originate with the Uttar Pradesh State Election Commission; this repository does not assert a separate license over the source data.
