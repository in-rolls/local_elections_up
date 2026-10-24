# Uttar Pradesh local elections

Election results, candidates, and seat-reservation observations for Uttar Pradesh's rural and urban local governments. The gram-panchayat head data cover 2005, 2010, 2015, and 2021. Additional office-specific observations cover selected years and districts; their coverage and unresolved source issues are recorded separately.

## Find the data

Published tables are in `data/release/`: each election has its own folder, `data/release/<year>/`, and products built across elections are in `data/release/linkage/`. Start with the **[data catalog](data/release/CATALOG.md)**. It lists every published table, its row count, election years, row unit, and validation status. The **[data dictionary](data/release/DICTIONARY.md)** lists columns and types; the **[data guide](data/README.md)** explains the layout, identifiers, reservations, provenance, and linkage.

Read these Parquet files directly. The inventory is generated from the release
manifest by `make data-summary`. Counts describe source records, not necessarily
unique seats; provisional office observations can overlap.

<!-- datasets:start -->

| File | Rows | Each row represents |
| --- | ---: | --- |
| [1995/panchayat_samiti_head_seat_reservation.parquet](data/release/1995/panchayat_samiti_head_seat_reservation.parquet) | 17 | one source observation; sources may overlap |
| [1995/zilla_parishad_member_seat_reservation.parquet](data/release/1995/zilla_parishad_member_seat_reservation.parquet) | 58 | one source observation; sources may overlap |
| [2000/panchayat_samiti_head_seat_reservation.parquet](data/release/2000/panchayat_samiti_head_seat_reservation.parquet) | 17 | one source observation; sources may overlap |
| [2000/zilla_parishad_member_seat_reservation.parquet](data/release/2000/zilla_parishad_member_seat_reservation.parquet) | 58 | one source observation; sources may overlap |
| [2005/gram_panchayat_head_declared_winner.parquet](data/release/2005/gram_panchayat_head_declared_winner.parquet) | 51,872 | one source observation; sources may overlap |
| [2005/gram_panchayat_head_winner_list.parquet](data/release/2005/gram_panchayat_head_winner_list.parquet) | 51,872 | one winner-list source record |
| [2005/panchayat_samiti_head_elected_official.parquet](data/release/2005/panchayat_samiti_head_elected_official.parquet) | 820 | one source observation; sources may overlap |
| [2005/panchayat_samiti_head_seat_reservation.parquet](data/release/2005/panchayat_samiti_head_seat_reservation.parquet) | 17 | one source observation; sources may overlap |
| [2005/panchayat_samiti_junior_deputy_elected_official.parquet](data/release/2005/panchayat_samiti_junior_deputy_elected_official.parquet) | 819 | one source observation; sources may overlap |
| [2005/panchayat_samiti_member_reported_official.parquet](data/release/2005/panchayat_samiti_member_reported_official.parquet) | 64,277 | one source observation; sources may overlap |
| [2005/panchayat_samiti_senior_deputy_elected_official.parquet](data/release/2005/panchayat_samiti_senior_deputy_elected_official.parquet) | 820 | one source observation; sources may overlap |
| [2005/zilla_parishad_head_elected_official.parquet](data/release/2005/zilla_parishad_head_elected_official.parquet) | 70 | one source observation; sources may overlap |
| [2005/zilla_parishad_member_elected_official.parquet](data/release/2005/zilla_parishad_member_elected_official.parquet) | 2,561 | one source observation; sources may overlap |
| [2005/zilla_parishad_member_seat_reservation.parquet](data/release/2005/zilla_parishad_member_seat_reservation.parquet) | 58 | one source observation; sources may overlap |
| [2006/municipal_corporation_mayor_candidate_record.parquet](data/release/2006/municipal_corporation_mayor_candidate_record.parquet) | 145 | one source observation; sources may overlap |
| [2006/municipal_corporation_ward_member_candidate_record.parquet](data/release/2006/municipal_corporation_ward_member_candidate_record.parquet) | 8,010 | one source observation; sources may overlap |
| [2006/municipal_council_chair_candidate_record.parquet](data/release/2006/municipal_council_chair_candidate_record.parquet) | 1,619 | one source observation; sources may overlap |
| [2006/municipal_council_ward_member_candidate_record.parquet](data/release/2006/municipal_council_ward_member_candidate_record.parquet) | 22,952 | one source observation; sources may overlap |
| [2006/nagar_panchayat_chair_candidate_record.parquet](data/release/2006/nagar_panchayat_chair_candidate_record.parquet) | 3,099 | one source observation; sources may overlap |
| [2006/nagar_panchayat_ward_member_candidate_record.parquet](data/release/2006/nagar_panchayat_ward_member_candidate_record.parquet) | 17,714 | one source observation; sources may overlap |
| [2010/gram_panchayat_head_declared_winner.parquet](data/release/2010/gram_panchayat_head_declared_winner.parquet) | 51,861 | one source observation; sources may overlap |
| [2010/gram_panchayat_head_winner_list.parquet](data/release/2010/gram_panchayat_head_winner_list.parquet) | 51,861 | one winner-list source record |
| [2010/panchayat_samiti_head_reported_official.parquet](data/release/2010/panchayat_samiti_head_reported_official.parquet) | 821 | one source observation; sources may overlap |
| [2010/panchayat_samiti_head_seat_reservation.parquet](data/release/2010/panchayat_samiti_head_seat_reservation.parquet) | 17 | one source observation; sources may overlap |
| [2010/panchayat_samiti_member_reported_official.parquet](data/release/2010/panchayat_samiti_member_reported_official.parquet) | 63,321 | one source observation; sources may overlap |
| [2010/panchayat_samiti_member_source_status_notice.parquet](data/release/2010/panchayat_samiti_member_source_status_notice.parquet) | 12 | one source observation; sources may overlap |
| [2010/zilla_parishad_head_reported_official.parquet](data/release/2010/zilla_parishad_head_reported_official.parquet) | 72 | one source observation; sources may overlap |
| [2010/zilla_parishad_member_reported_official.parquet](data/release/2010/zilla_parishad_member_reported_official.parquet) | 2,624 | one source observation; sources may overlap |
| [2010/zilla_parishad_member_seat_reservation.parquet](data/release/2010/zilla_parishad_member_seat_reservation.parquet) | 58 | one source observation; sources may overlap |
| [2012/municipal_corporation_mayor_declared_winner.parquet](data/release/2012/municipal_corporation_mayor_declared_winner.parquet) | 12 | one source observation; sources may overlap |
| [2012/municipal_corporation_mayor_seat_reservation.parquet](data/release/2012/municipal_corporation_mayor_seat_reservation.parquet) | 13 | one source observation; sources may overlap |
| [2012/municipal_corporation_ward_member_declared_winner.parquet](data/release/2012/municipal_corporation_ward_member_declared_winner.parquet) | 980 | one source observation; sources may overlap |
| [2012/municipal_corporation_ward_member_seat_reservation.parquet](data/release/2012/municipal_corporation_ward_member_seat_reservation.parquet) | 1,040 | one source observation; sources may overlap |
| [2012/municipal_council_chair_declared_winner.parquet](data/release/2012/municipal_council_chair_declared_winner.parquet) | 194 | one source observation; sources may overlap |
| [2012/municipal_council_chair_seat_reservation.parquet](data/release/2012/municipal_council_chair_seat_reservation.parquet) | 194 | one source observation; sources may overlap |
| [2012/municipal_council_ward_member_declared_winner.parquet](data/release/2012/municipal_council_ward_member_declared_winner.parquet) | 5,097 | one source observation; sources may overlap |
| [2012/municipal_council_ward_member_seat_reservation.parquet](data/release/2012/municipal_council_ward_member_seat_reservation.parquet) | 4,779 | one source observation; sources may overlap |
| [2012/nagar_panchayat_chair_declared_winner.parquet](data/release/2012/nagar_panchayat_chair_declared_winner.parquet) | 423 | one source observation; sources may overlap |
| [2012/nagar_panchayat_chair_seat_reservation.parquet](data/release/2012/nagar_panchayat_chair_seat_reservation.parquet) | 423 | one source observation; sources may overlap |
| [2012/nagar_panchayat_ward_member_declared_winner.parquet](data/release/2012/nagar_panchayat_ward_member_declared_winner.parquet) | 5,158 | one source observation; sources may overlap |
| [2012/nagar_panchayat_ward_member_seat_reservation.parquet](data/release/2012/nagar_panchayat_ward_member_seat_reservation.parquet) | 4,958 | one source observation; sources may overlap |
| [2015/gram_panchayat_head_declared_winner.parquet](data/release/2015/gram_panchayat_head_declared_winner.parquet) | 59,019 | one source observation; sources may overlap |
| [2015/gram_panchayat_head_seat_reservation.parquet](data/release/2015/gram_panchayat_head_seat_reservation.parquet) | 59,021 | one source observation; sources may overlap |
| [2015/gram_panchayat_head_winner_list.parquet](data/release/2015/gram_panchayat_head_winner_list.parquet) | 59,019 | one winner-list source record |
| [2015/gram_panchayat_member_seat_reservation.parquet](data/release/2015/gram_panchayat_member_seat_reservation.parquet) | 743,685 | one source observation; sources may overlap |
| [2015/panchayat_samiti_head_declared_winner.parquet](data/release/2015/panchayat_samiti_head_declared_winner.parquet) | 816 | one source observation; sources may overlap |
| [2015/panchayat_samiti_head_seat_reservation.parquet](data/release/2015/panchayat_samiti_head_seat_reservation.parquet) | 838 | one source observation; sources may overlap |
| [2015/panchayat_samiti_member_declared_winner.parquet](data/release/2015/panchayat_samiti_member_declared_winner.parquet) | 77,743 | one source observation; sources may overlap |
| [2015/panchayat_samiti_member_seat_reservation.parquet](data/release/2015/panchayat_samiti_member_seat_reservation.parquet) | 79,229 | one source observation; sources may overlap |
| [2015/zilla_parishad_head_declared_winner.parquet](data/release/2015/zilla_parishad_head_declared_winner.parquet) | 74 | one source observation; sources may overlap |
| [2015/zilla_parishad_head_seat_reservation.parquet](data/release/2015/zilla_parishad_head_seat_reservation.parquet) | 75 | one source observation; sources may overlap |
| [2015/zilla_parishad_member_declared_winner.parquet](data/release/2015/zilla_parishad_member_declared_winner.parquet) | 3,121 | one source observation; sources may overlap |
| [2015/zilla_parishad_member_seat_reservation.parquet](data/release/2015/zilla_parishad_member_seat_reservation.parquet) | 3,179 | one source observation; sources may overlap |
| [2017/municipal_corporation_mayor_declared_winner.parquet](data/release/2017/municipal_corporation_mayor_declared_winner.parquet) | 16 | one source observation; sources may overlap |
| [2017/municipal_corporation_ward_member_declared_winner.parquet](data/release/2017/municipal_corporation_ward_member_declared_winner.parquet) | 1,300 | one source observation; sources may overlap |
| [2017/municipal_council_chair_declared_winner.parquet](data/release/2017/municipal_council_chair_declared_winner.parquet) | 198 | one source observation; sources may overlap |
| [2017/municipal_council_ward_member_declared_winner.parquet](data/release/2017/municipal_council_ward_member_declared_winner.parquet) | 5,261 | one source observation; sources may overlap |
| [2017/nagar_panchayat_chair_declared_winner.parquet](data/release/2017/nagar_panchayat_chair_declared_winner.parquet) | 438 | one source observation; sources may overlap |
| [2017/nagar_panchayat_ward_member_declared_winner.parquet](data/release/2017/nagar_panchayat_ward_member_declared_winner.parquet) | 5,434 | one source observation; sources may overlap |
| [2021/gram_panchayat_head_candidate_record.parquet](data/release/2021/gram_panchayat_head_candidate_record.parquet) | 373,096 | one candidate |
| [2021/gram_panchayat_head_declared_winner.parquet](data/release/2021/gram_panchayat_head_declared_winner.parquet) | 49,773 | one source observation; sources may overlap |
| [2021/gram_panchayat_head_seat_reservation.parquet](data/release/2021/gram_panchayat_head_seat_reservation.parquet) | 405 | one source observation; sources may overlap |
| [2021/panchayat_samiti_head_seat_reservation.parquet](data/release/2021/panchayat_samiti_head_seat_reservation.parquet) | 27 | one source observation; sources may overlap |
| [2021/panchayat_samiti_member_seat_reservation.parquet](data/release/2021/panchayat_samiti_member_seat_reservation.parquet) | 1,764 | one source observation; sources may overlap |
| [2021/zilla_parishad_member_seat_reservation.parquet](data/release/2021/zilla_parishad_member_seat_reservation.parquet) | 92 | one source observation; sources may overlap |
| [2023/municipal_corporation_mayor_seat_reservation.parquet](data/release/2023/municipal_corporation_mayor_seat_reservation.parquet) | 17 | one source observation; sources may overlap |
| [2023/municipal_corporation_ward_member_seat_reservation.parquet](data/release/2023/municipal_corporation_ward_member_seat_reservation.parquet) | 1,420 | one source observation; sources may overlap |
| [2023/municipal_council_chair_seat_reservation.parquet](data/release/2023/municipal_council_chair_seat_reservation.parquet) | 200 | one source observation; sources may overlap |
| [2023/municipal_council_ward_member_seat_reservation.parquet](data/release/2023/municipal_council_ward_member_seat_reservation.parquet) | 5,352 | one source observation; sources may overlap |
| [2023/nagar_panchayat_chair_seat_reservation.parquet](data/release/2023/nagar_panchayat_chair_seat_reservation.parquet) | 544 | one source observation; sources may overlap |
| [2023/nagar_panchayat_ward_member_seat_reservation.parquet](data/release/2023/nagar_panchayat_ward_member_seat_reservation.parquet) | 7,177 | one source observation; sources may overlap |
| [linkage/gp_adjacent_links.parquet](data/release/linkage/gp_adjacent_links.parquet) | 128,687 | one accepted adjacent-wave link |
| [linkage/gp_four_election_links.parquet](data/release/linkage/gp_four_election_links.parquet) | 29,734 | one linked four-election history |
| [linkage/gp_head_election_records.parquet](data/release/linkage/gp_head_election_records.parquet) | 212,525 | one winner-list or winner-marked record |
| [linkage/gp_lgd_bridge.parquet](data/release/linkage/gp_lgd_bridge.parquet) | 157,186 | one historical panel row projected to the LGD vintage |
| [linkage/gp_link_candidates.parquet](data/release/linkage/gp_link_candidates.parquet) | 129,752 | one assessed adjacent-wave linkage candidate |
| [linkage/gp_panel_2005_2010.parquet](data/release/linkage/gp_panel_2005_2010.parquet) | 42,622 | one linked source-record pair or four-election history |
| [linkage/gp_panel_2005_2010_2015_2021.parquet](data/release/linkage/gp_panel_2005_2010_2015_2021.parquet) | 29,734 | one linked source-record pair or four-election history |
| [linkage/gp_panel_2010_2015.parquet](data/release/linkage/gp_panel_2010_2015.parquet) | 39,551 | one linked source-record pair or four-election history |
| [linkage/gp_panel_2015_2021.parquet](data/release/linkage/gp_panel_2015_2021.parquet) | 46,514 | one linked source-record pair or four-election history |
| [linkage/weaver_20250302_wide.parquet](data/release/linkage/weaver_20250302_wide.parquet) | 105,527 | one source GP identifier, wide across waves |
| [linkage/weaver_20250317_wide.parquet](data/release/linkage/weaver_20250317_wide.parquet) | 61,338 | one source GP identifier, wide across waves |

<!-- datasets:end -->

Download a tagged [GitHub release](https://github.com/in-rolls/local_elections_up/releases), retaining its manifest and checksums. The central [local_elections](https://github.com/in-rolls/local_elections) repository harmonizes a pinned UP release with other states.

```python
import pandas as pd

records = pd.read_parquet("data/release/linkage/gp_head_election_records.parquet")
print(records.groupby("election_year").size())
review = records.loc[records["winner_markers_conflict"]]
```

## Understand the row before counting it

The four-wave GP table preserves 212,525 winner-list or winner-marked source records. This is not a count of distinct seats. In 2021, 373,096 candidates belong to 49,772 source seat groups, and one group has two conflicting winner markers. Both source records and their actual candidate names survive; the winner remains unresolved.

`gp_code` is a block-local serial, not a geographic identifier. District/block/GP names also collide. Use the documented source-record keys and check join cardinality. Unknown reservation is missing information, not an unreserved seat. In 2015, `सविरोध` and `निर्विरोध` mean contested and unopposed; the collection is a winner list.

Office exports are **provisional source observations**. Their `assignment_usable=false` flag remains in force even where category labels are decoded. Alternate sources can describe the same seat. Candidate, winner, official, and reservation records must not be pooled into a seat count. Historical encoded names, uncertain readings, and source conflicts remain visible.

## Repository layout

```text
data/
  release/      The published tables
    1995/ … 2023/  One folder per election: that election's tables
    linkage/        Products derived across elections: harmonized GP-head records,
                   links, wide panels, LGD bridge, Weaver preparations
    CATALOG.md, DICTIONARY.md, MANIFEST.json, CHECKSUMS.sha256
  raw/<year>/   Registered source bytes and source manifests; raw/fetch_log.csv
  collections/  Harvested SEC, district and media captures, one folder each
  extracted/    Saved extraction outputs
  build/        Enriched preparations, transliterations; build/release/ is the git-ignored build area
  manual/       Source registry, label dictionaries, reviewed crosswalks
  reference/    Attributed outside sources (LGD, Weaver, reservation-with-Census)
  search_log/   Sources not admitted to production
  checks/       Reconciliation records
src/local_elections_up/
  acquire/              Network fetches into data/raw and data/collections (run once; not part of make data)
  parse/                Saved source bytes → registered extractions
  build/                Registered extractions → build area → published tables (release.py)
```

Discovery does not enter a release unless explicitly registered. [The relocation ledger](data/manual/catalogs/relocations.json) records moved files without changing their source identities.

## Reproduce and verify

The data are distributed through GitHub releases. The Python package supplies checkout utilities; it is not a PyPI data package. Run the build commands from this repository.

Python dependencies are locked in `uv.lock`. Install uv, then run:

```sh
make sync
make check
```

`make data` rebuilds from saved, registered inputs. Source restoration is required for a fresh checkout that has no extraction cache; follow the [source-evidence instructions](data/manual/catalogs/SOURCES.md). Release assembly makes no network or paid-model calls. The former notebooks and R code remain available at [the pre-migration commit](https://github.com/in-rolls/local_elections_up/tree/42fb6190469688fd558596460aef44282e37f6d2).

`make data` rebuilds every published table from the committed inputs, and `make check` lints the code and verifies published data, including source-record and panel relationships. A clean clone needs nothing else. The office provenance re-hashes about 62,000 saved SEC portal captures when they are present; without them it uses the hashes recorded in `data/manual/catalogs/archived_source_resolutions.jsonl.gz`. `make fetch-sources` restores the captures (about 3 GB) from the source-evidence release. `make winner-lists-2015` rebuilds the five-office 2015 intermediate exports; `make verify-2015` compares every retained field with its source CSV.

`make enrich-gp` reconstructs all four enriched preparations from pinned CSVs and saved transliterations into `data/extracted/gp_rebuilt/`. It compares every value and row position with the registered preparations, and writes an unresolved-transliteration list. It makes no API calls and does not replace registered inputs. The [enrichment registry](data/manual/catalogs/gp_enrichment.json) records source hashes, transliteration precedence, and historical ordering exceptions.

The Kruti Dev decoder is included as readable Python source with [attribution](THIRD_PARTY_NOTICES) and a [provenance receipt](data/manual/catalogs/shared_decoder.json).


## Changes in this release

v3.1 moves the published tables under `data/release/` (`data/release/<year>/`, `data/release/linkage/`) and makes the build reproducible from a clean clone: the parsed inputs it reads are now committed, and the SEC portal captures behind the office provenance are pinned by recorded hash, with their bytes in the `source-evidence-2026-09-19` release (`make fetch-sources`). Every table is byte-identical to v3.0. Consumers must update their paths; see [CHANGELOG.md](CHANGELOG.md).

See [CHANGELOG.md](CHANGELOG.md) for the release record and [Weaver attribution](data/reference/weaver/README.md) for external source terms.

## Research and historical geography

[Research evidence](docs/research.md) describes the Etah and Sitapur reservation bundles and the SEC 2015–16 block-head printings. These retain unresolved source and identity flags.

The [historical LGD bridge](data/release/linkage/gp_lgd_bridge.parquet) maps linked election records to the attributed LGD vintage. Read [its source and matching rules](data/reference/lgd/README.md) before joining: multiple historical records can map to one later GP, and names do not prove unchanged boundaries. `make data-lgd` rebuilds it.

<!-- adjacent:start -->

## 🔗 Adjacent Repositories

- [in-rolls/local_elections_uttarakhand](https://github.com/in-rolls/local_elections_uttarakhand) — Data on Local Elections from Uttarakhand
- [in-rolls/local_elections_kerala](https://github.com/in-rolls/local_elections_kerala) — Kerala Local Government Seat Reservation Data and Winner Attributes
- [in-rolls/local_elections_bihar](https://github.com/in-rolls/local_elections_bihar) — Bihar panchayat elections: 2016 candidates and votes for six offices; 2021 mukhiya candidates, results, winners and seat reservations
- [in-rolls/local_elections_rajasthan](https://github.com/in-rolls/local_elections_rajasthan) — Rajasthan GP Election Reservation Status and Results for 2020--2022
- [in-rolls/electoral_rolls_up_2023](https://github.com/in-rolls/electoral_rolls_up_2023) — Uttar Pradesh Electoral Rolls 2023

_Powered by [Adjacent](https://github.com/gojiplus/adjacent)_

<!-- adjacent:end -->

## Maintenance

This is a point-in-time data collection; see the [shared maintenance policy](https://github.com/soodoku/data-repos#maintenance-policy). Run the affected parsers on retained inputs when code changes and the relevant data validators when inputs or outputs change. Full-data checks and publication are explicit operations. Routine edits do not require hosted CI, Docker, a Python-version matrix, Preen or pre-commit.
