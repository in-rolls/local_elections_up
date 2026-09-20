# Uttar Pradesh local elections

Election results, candidates, and seat-reservation observations for Uttar Pradesh's rural and urban local governments. The gram-panchayat head data cover 2005, 2010, 2015, and 2021. Additional office-specific observations cover selected years and districts; their coverage and unresolved source issues are recorded separately.

## Find the data

Start with the **[data catalog](data/release/CATALOG.md)**. It lists every published table, its row count, election years, row unit, and validation status. The **[data dictionary](data/release/DICTIONARY.md)** lists columns and types; the **[interpretation guide](data/release/README.md)** explains identifiers, reservations, provenance, and linkage.

| I need… | Use |
| --- | --- |
| GP-head results across four elections | [GP election records](data/release/gp/gp_head_election_records.parquet) |
| Every 2021 GP-head candidate | [2021 candidates](data/release/gp/gp_head_candidates_2021.parquet) |
| Results or reservations for another office | [Office catalog](data/release/CATALOG.md); check the office, record kind, year, and flags |
| Adjacent-election or four-election links | [Shared panels](data/release/panels/) |
| The two Weaver source preparations | [Weaver tables](data/release/weaver/) and [source documentation](data/external/weaver/README.md) |
| Exact inputs and output hashes | [Release manifest](data/release/manifest.json) and [checksums](data/release/CHECKSUMS.sha256) |

Download a tagged [GitHub release](https://github.com/in-rolls/local_elections_up/releases), retaining its manifest and checksums. The central [local_elections](https://github.com/in-rolls/local_elections) repository harmonizes a pinned UP release with other states.

```python
import pandas as pd

records = pd.read_parquet("data/release/gp/gp_head_election_records.parquet")
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
  raw/          Registered source bytes and source manifests
  interim/      Saved extraction outputs and historical build snapshots
  discovery/    Sources not admitted to production
  catalogs/     Source registry, label dictionaries, and relocation ledger
  crosswalks/   Reviewed geographic mappings and correction decisions
  release/      Consumer tables, catalog, dictionary, and checksums
    gp/         GP-head source records and standardized election records
    offices/    Office-specific provisional observations
    panels/     Geographic links and wide election panels
    weaver/     Separate preparations of the two external vintages
src/local_elections_up/  Python acquisition, parsing, and release code
R/                      Shared R transformations
scripts/                R build entry points
notebooks/              Historical parsing and transliteration work
tests/                 Parser, grain, recode, and provenance checks
```

Historical source receipts retain their original paths, including `data/recovery/`. Archive restoration preserves those locators. Discovery does not enter a release unless explicitly registered. [The relocation ledger](data/catalogs/relocations.json) records moved files without changing their source identities.

## Reproduce and verify

Python dependencies are locked in `uv.lock`; R dependencies are locked in `renv.lock`. Install R and uv, then run:

```sh
make sync
make restore-r
make check
```

`make data` rebuilds from saved, registered inputs. Source restoration is required for a fresh checkout that has no extraction cache; follow the [source-evidence instructions](data/catalogs/SOURCES.md). Release assembly makes no network or paid-model calls. Historical notebooks are retained for provenance and are not part of the release command.

`make ci-docker` runs Python and R checks in standard containers. `make winner-lists-2015` rebuilds the five-office 2015 intermediate exports; `make verify-2015` compares every retained field with its source CSV.

## Changes in this release

The v2 layout replaces `data/fin/` with `data/release/`. Consumer filenames describe their contents and row unit. The 2015 office records now have winner-list semantics and decoded seat-reservation categories. The known 2021 conflicting winner names are retained correctly. Analytical exports omit phone numbers and the three 2021 columns whose headers were not recovered. Original source evidence is preserved separately.

See [CHANGELOG.md](CHANGELOG.md) for the release record and [Weaver attribution](data/external/weaver/README.md) for external source terms.

## Research and historical geography

[Research evidence](RESEARCH.md) describes the Etah and Sitapur reservation bundles and the SEC 2015–16 block-head printings. These retain unresolved source and identity flags.

The [historical LGD bridge](data/release/panels/gp_lgd_bridge.parquet) maps linked election records to the attributed LGD vintage. Read [its source and matching rules](data/external/lgd/README.md) before joining: multiple historical records can map to one later GP, and names do not prove unchanged boundaries. `make data-lgd` rebuilds it.
