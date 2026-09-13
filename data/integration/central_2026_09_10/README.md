# Central UP integration reconciliation

Date: 2026-09-10. Owner: local_elections_up.

The published state table has 212,525 source rows; the central master has
153,505 rows. The difference is explained, but the two grains must not be
made identical by silently adding or dropping a row.

## Findings

- 2005: 51,872 rows in each output. This establishes count agreement only.
- 2010: 51,861 rows in each output. This establishes count agreement only.
- 2015: 59,019 published state rows; the central adapter does not import this wave.
- 2021: 49,773 winner-marked state rows versus 49,772 central candidate-seat groups.

One 2021 source key, Mainpuri / Kurawali / Sonai / serial 22, has 25 candidate
records and two different candidates marked as winners: IDs 202725 and 219438.
The central collapse retains one seat without selecting either winner. The
state standardized file preserves both winner-marked records. Neither counting
them as two confirmed seats nor arbitrarily choosing one winner is justified.

The candidate-level published input also gives both winner-marked records the
same denormalized `elected_sarpanch_name`, although their `candidate` fields
are different. The standardized builder reads that denormalized name. The
source conflict therefore requires explicit treatment before replacing the
central 2021 import with the standardized table.

## Files

- `wave_reconciliation.csv`: counts, observed administrative coverage, unknown
  reservation counts, and linking exclusions by election year.
- `2021_winner_conflict.csv`: the two conflicting source records and IDs.
- `central_2021_conflict_seat.csv`: corresponding central output, without
  inventing a winner or claiming a second seat.
- `reconciliation_summary.json`: paths, the state schema's declared checksum,
  central output's recorded source commit, and execution scope.

## Import contract to implement

1. The UP repository owns the versioned state output and correction decisions.
2. Central imports a pinned state release, not an unrecorded moving checkout.
3. Add the omitted 2015 wave while retaining its contested/unopposed semantics.
4. Preserve all 373,096 candidate records in the 2021 candidate product and
   distinguish source winner records from unique seat groups.
5. Keep the conflict in a review queue with both source candidate IDs. Do not
   resolve it from a denormalized name or infer a winner from caste or sex.
6. Preserve existing 2010 document/page lineage when changing input formats.
7. Retain upstream name/linking flags and unknown reservation values.

The central discovery collections remain intact under
`local_elections/data/source_search/national/uttar_pradesh/`. Their transfer to
state-owned immutable source assets is a separate manifest-backed handoff;
this reconciliation does not copy, delete, or publish those source bytes.

No adapters, released datasets, or source corrections were changed. No code
tests or checksum verification were run. This is an inspection of actual
Parquet data and the published build logic, not an equivalence certification.

## Subsequent source handoff

The two new discovery collections have since moved to this repository under
`data/discovery/2026-09-10/parallel_search/` and `archive_coverage/`.
The original central locations named above describe the pre-handoff state.
No release or adapter migration accompanied this move.

## Adapter implementation update

The central adapter now declares the missing 2015 published Parquet input,
pinned to the state schema's SHA-256. It retains source row ordinals, the
raw seat reservation, winner attributes, stated votes, and contested/unopposed
status without exporting phone numbers. Existing 2005/2010 parsing and page
lineage remain unchanged during this bounded migration.

For 2021, publisher candidate IDs are retained as candidate_no. Multiple
winner markers under a seat key now produce winner_markers_conflict and retain
the conflicting IDs in extras. Candidate elected values remain unknown for
that ambiguous group instead of asserting that every candidate lost.

Dictionary declarations include the new provenance and conflict fields.
No pooled release has been rebuilt and no code checks have been run yet.
The full switch to standardized state outputs, release pin coordination,
generated documentation, and published-file renaming remain separate work.

## Pooled rebuild completed, 2026-09-10

`pooled_rebuild.json` records the completed rebuild and supersedes the earlier pending-check status. The central working dataset now contains 212,524 UP seat records, including all 59,019 records from 2015, and 373,096 candidates. All 29 targeted tests passed; lint, formatting, publication hashes, and pooled row-count checks passed. Other states were preserved.

The remaining one-row difference from the state table is the documented 2021 conflicting-winner contest, not a confirmed missing seat. Both publisher-marked candidate IDs and all 25 candidates are retained, with the winner and elected indicators unknown. Source-file hashes and implementation hashes are in the linked central receipt. The source checkout is dirty; no clean release is claimed.
