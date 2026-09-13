# Uttar Pradesh: status as of 2026-09-10

## Bottom line

The repository supplies a four-wave GP-head dataset with documented gaps and conflicts. It is not a complete census of UP local elections. Historical reservation parsing remains unfinished.

| Election year | Central GP-head seat records | Input |
|---|---:|---|
| 2005 | 51,872 | Cleaned source CSV |
| 2010 | 51,861 | Cleaned source CSV with document/page references |
| 2015 | 59,019 | Hash-pinned published Parquet |
| 2021 | 49,772 | 373,096 candidates in a hash-pinned compressed CSV |
| Total | 212,524 | Four election years |

The central v0.5.1 release is still being prepared. These are the intended, previously checked UP counts, not a claim that the central release has been tagged. The clean-checkout input gap for 2021 is addressed by `data/raw/2021/gram_panchayat_pradhan_candidates.csv.gz`; a missing declared wave must stop the central adapter rather than silently reduce the dataset.

## What remains uncertain in the usable data

- One 2021 contest in Sonai, Kurawali block, Mainpuri has two publisher-marked winners, candidate IDs 202725 and 219438. The central table retains one contest and all 25 candidates, leaves the winner and elected indicators unknown, and flags the conflict.
- The state standardized table contains 212,525 source-derived records because it retains both winner-marked records in that contest. Its denormalized winner name is not independent evidence for resolving the conflict. Do not interpret the extra record as a confirmed extra seat.
- The state-table audit found 1,333 unknown reservation values, 527 unknown winner-sex values, and 879 records ineligible for the intended name-based linkage. These are state-table counts; do not substitute them for central harmonization diagnostics.
- The 2021 state table covers 67 district names and 728 district/block groups. It is not statewide coverage. The current 75-district/826-block discovery frame is not a historical boundary crosswalk.
- Provenance varies by wave. The 2010 input preserves document/page references; the legacy 2021 scrape did not record its acquisition URL or time. Its compressed source manifest pins the held bytes and explicitly records those missing fields.

## Discovery and preservation

All 75 current district hosts have completed archive-index queries, including continuation pages: 361,301 capture entries and 77,930 PDF URL/MIME candidates. This is an inventory of captures, not 77,930 distinct election PDFs. Historical host aliases and document contents have not been exhaustively reviewed.

The discovery frame contains 826 blocks. The new acquisition collections contain 554 downloaded PDF pages: 143 in the parallel search, 225 archived reservation pages, and 186 SEC result pages. This is an acquisition total, not deduplicated or validated statewide coverage.

The discovery evidence archive contains 312 files. It preserves 296,922,147 original bytes in 119,296,382 compressed bytes. Every member hash was checked after decompression, and GitHub's uploaded archive digest matches. Compact catalogs are in Git; the archive restores original paths and receipts. See [storage and restoration](data/source_archives/README.md).

The 2021 candidate CSV is separately preserved in Git as a 14,290,190-byte gzip file instead of the 115,938,310-byte original. Its decompressed bytes were verified exactly. See [its source manifest](data/raw/2021/source_manifest.json).

## Parsing: not finished

- Sitapur 2010: native extraction attempted all 90 pages across GP heads, block members, and district members. The local first pass produced 2,917 observations, but 1,328 carried additional extraction issues. Column-boundary errors were detected; no observations from that parser are promoted to release data.
- Etah 2010: 121 acquired pages contain retrospective reservation columns for 1995, 2000, and 2005. Category-sorted panels may repeat GPs. No validated assignment table has been released from this source.
- The two SEC 2010 result PDFs contain 186 pages with custom-font encoding. Native text exists, but it is not yet reliable structured data.
- Scanned sources remain evidence until visual/OCR comparison establishes their office, year, row boundaries, and reservation fields. No paid UP inference has been run in this effort.

## Next deliverables

1. Repair Sitapur's column segmentation and account for every printed row, then compare extracted cells with rendered source pages.
2. Decode and reconcile place names without overwriting the original font-encoded readings.
3. Parse Etah's historical panels while retaining repetitions, source pages, and uncertainty about each panel's role.
4. Expand historical-host and linked-document acquisition, recording attempted coverage separately from successful acquisition.
5. Publish validated source-specific tables before adding any new historical counts to the pooled master.
