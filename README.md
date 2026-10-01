# Uttar Pradesh local elections

Election results, candidates, and seat-reservation observations for Uttar Pradesh's rural and urban local governments. The gram-panchayat head data cover 2005, 2010, 2015, and 2021. Additional office-specific observations cover selected years and districts; their coverage and unresolved source issues are recorded separately.

## Find the data

Each election has its own folder, `data/<year>/`; products built across elections are in `data/panels/`. Start with the **[data catalog](data/CATALOG.md)**. It lists every published table, its row count, election years, row unit, and validation status. The **[data dictionary](data/DICTIONARY.md)** lists columns and types; the **[data guide](data/README.md)** explains the layout, identifiers, reservations, provenance, and linkage.

| I need… | Use |
| --- | --- |
| One election's GP-head winners | [2005](data/2005/gram_panchayat_head_declared_winner.parquet), [2010](data/2010/gram_panchayat_head_declared_winner.parquet), [2015](data/2015/gram_panchayat_head_declared_winner.parquet); 2021 winners are marked among [2021 candidates](data/2021/gram_panchayat_head_candidate_record.parquet) |
| GP-head results harmonized across four elections | [GP election records](data/panels/gp_head_election_records.parquet) |
| Results or reservations for another office | That election's folder, via the [catalog](data/CATALOG.md); check the office, record kind, and flags |
| Adjacent-election or four-election links | [Panels](data/panels/) |
| The two Weaver source preparations | [Panels](data/panels/) and [source documentation](data/external/weaver/README.md) |
| Exact inputs and output hashes | [Manifest](data/manifest.json) and [checksums](data/CHECKSUMS.sha256) |

Download a tagged [GitHub release](https://github.com/in-rolls/local_elections_up/releases), retaining its manifest and checksums. The central [local_elections](https://github.com/in-rolls/local_elections) repository harmonizes a pinned UP release with other states.

```python
import pandas as pd

records = pd.read_parquet("data/panels/gp_head_election_records.parquet")
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
  1995/ … 2023/ One folder per election: that election's tables
  panels/       Products derived across elections: harmonized GP-head records,
                links, wide panels, LGD bridge, Weaver preparations
  CATALOG.md, DICTIONARY.md, manifest.json, CHECKSUMS.sha256
  raw/<year>/   Registered source bytes and source manifests
  interim/      Saved extraction outputs; interim/release/ is the git-ignored build area
  discovery/    Sources not admitted to production
  catalogs/     Source registry, label dictionaries, and relocation ledger
  crosswalks/   Reviewed geographic mappings and correction decisions
  external/     Attributed outside sources (LGD, Weaver, reservation-with-Census)
src/local_elections_up/
  acquire/              Network fetches into data/raw and data/recovery (run once; not part of make data)
  parse/                Saved source bytes → registered extractions
  build/                Registered extractions → build area → published tables (release.py)
R/                      Shared R transformations
scripts/                R build entry points, run in Makefile order
notebooks/              Historical 2005/2010 cleaning and transliteration; not part of the build
tests/                  Parser, grain, recode, and provenance checks
vendor/                 Hash-pinned shared research-code wheel
```

Historical source receipts retain their original paths, including `data/recovery/`. Archive restoration preserves those locators. Discovery does not enter a release unless explicitly registered. [The relocation ledger](data/catalogs/relocations.json) records moved files without changing their source identities.

## Reproduce and verify

The data are distributed through GitHub releases. The Python package supplies checkout utilities; it is not a PyPI data package. Run the build commands from this repository.

Python dependencies are locked in `uv.lock`; R dependencies are locked in `renv.lock`. Install R and uv, then run:

```sh
make sync
make restore-r
make check
```

`make data` rebuilds from saved, registered inputs. Source restoration is required for a fresh checkout that has no extraction cache; follow the [source-evidence instructions](data/catalogs/SOURCES.md). Release assembly makes no network or paid-model calls. Historical notebooks are retained for provenance and are not part of the release command.

`make ci-docker` runs Python and R checks in standard containers. `make winner-lists-2015` rebuilds the five-office 2015 intermediate exports; `make verify-2015` compares every retained field with its source CSV.

## Changes in this release

v3 organizes the published tables by election: `data/<year>/` replaces `data/release/{gp,offices}/`, multi-year office tables are split by election, and cross-election products move to `data/panels/`. Each GP-head election is published once, from its best source. Raw source files move under `data/raw/<year>/`. Three Weaver panchayat names that ended or began with a stray byte (invalid UTF-8; six cells per preparation) now read cleanly. Consumers must update their paths; see [CHANGELOG.md](CHANGELOG.md).

See [CHANGELOG.md](CHANGELOG.md) for the release record and [Weaver attribution](data/external/weaver/README.md) for external source terms.

## Research and historical geography

[Research evidence](RESEARCH.md) describes the Etah and Sitapur reservation bundles and the SEC 2015–16 block-head printings. These retain unresolved source and identity flags.

The [historical LGD bridge](data/panels/gp_lgd_bridge.parquet) maps linked election records to the attributed LGD vintage. Read [its source and matching rules](data/external/lgd/README.md) before joining: multiple historical records can map to one later GP, and names do not prove unchanged boundaries. `make data-lgd` rebuilds it.

<!-- adjacent:start -->

## 🔗 Adjacent Repositories

- [in-rolls/local_elections_uttarakhand](https://github.com/in-rolls/local_elections_uttarakhand) — Data on Local Elections from Uttarakhand
- [in-rolls/local_elections_kerala](https://github.com/in-rolls/local_elections_kerala) — Kerala Local Government Seat Reservation Data and Winner Attributes
- [in-rolls/local_elections_bihar](https://github.com/in-rolls/local_elections_bihar) — Bihar panchayat elections: 2016 candidates and votes for six offices; 2021 mukhiya candidates, results, winners and seat reservations
- [in-rolls/local_elections_rajasthan](https://github.com/in-rolls/local_elections_rajasthan) — Rajasthan GP Election Reservation Status and Results for 2020--2022
- [in-rolls/electoral_rolls_up_2023](https://github.com/in-rolls/electoral_rolls_up_2023) — Uttar Pradesh Electoral Rolls 2023

_Powered by [Adjacent](https://github.com/gojiplus/adjacent)_

<!-- adjacent:end -->
