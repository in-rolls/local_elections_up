# UP SEC block-head winners, 2015-16 cycle

This extract contains 816 winner printings for Kshetra Panchayat Pramukh
(block head), across 74 printed district labels. There are 431 contested and
385 unopposed results, with no duplicated district/block label combinations.
These are block-head results, not samiti ward-member results.

The official SEC results navigation links this table from its 2015 panchayat
election section. The linked overview calls the cycle 2015-16. Accordingly,
`year` is 2015, `election_cycle_label` is `2015-16`, and `election_date` remains
null. Neither the selected table nor the cached overview supplies an independent
statewide total against which these 816 printings have been reconciled. Do not
interpret 74 district labels as a verified complete district inventory.

## Parsing and checks

The parser requires the original HTML checksum, one exact table ID, the complete
ordered 13-column header, and consistent row widths. Seat reservation and
candidate category remain separate. Unreserved categories use `NONE`, not `UR`.
Missing vote statistics for unopposed winners remain missing, not zero.

A second HTML implementation, pandas with lxml, matched all 9,792 retained source
cells. The previous extract and this one agree on all source text, rows, votes,
identifiers, and provenance. Changes are limited to the two canonical category
codes and the reviewed-scope status. This is a parser cross-check, not independent
confirmation that the source itself reports every result correctly.

See [the validation receipt](sec_winner_table_2015_validation.json),
[cycle-scope evidence](sec_winner_table_scope.json), and
[the data dictionary](sec_winner_table_2015_dictionary.md).

## Source handling

The public bundle excludes the original winner-table HTML because it contains a
mobile-number column. It includes phone-free derived observations, source hashes,
row ordinals, parsing code, and the two compressed official navigation/overview
pages supporting the cycle attribution. The original winner HTML is retained
locally for audit; its bytes are not included in this new bundle.

The source URL is `https://sec.up.nic.in/ElecLive/WinnerList.aspx`, captured on
2026-09-10. Its contents can change. Rebuilding requires a source copy matching
the pinned checksum, not merely another successful download from that URL.
The bundle catalog lists every included file and its checksum.

## Rebuild

From the UP repository, run `uv sync --all-groups`. Provide a source root containing
the pinned winner HTML and the two scope artifacts at the paths in the scope
catalog. Use a fresh output directory:

```sh
.venv/bin/python scripts/extract_sec_winner_table.py \
  --root /path/to/source-root \
  --scope data/catalogs/sec_winner_table_scope.json \
  --output /tmp/sec-winners-2015-rebuild
```

Run `make check` for the repository checks. This research bundle does not modify
`data/fin`, establish exact poll dates, certify statewide completeness, or add
samiti ward-level coverage. No paid inference was used.
