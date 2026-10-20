# Uttar Pradesh archive coverage audit

Date: 2026-09-10

## Finding

Complete district/block archive coverage is not established.

The pre-existing `data/archive_inventory.csv` records Uttar Pradesh as
`sec.uttarpradesh.gov.in`, zero PDFs, status `ok`. The working official SEC
website is `https://sec.up.nic.in/`. That old row is not evidence that the
correct SEC host or every district/block was searched. Preserve it as an
earlier observation, not an exhaustive negative finding.

The archive sweep's generated UP host candidates omit `sec.up.nic.in`.
Its listing also has a 5,000-URL limit without continuation handling, and
selects PDFs by a literal `.pdf` suffix. Even a successful sweep therefore
does not establish complete coverage of a large host or query-string PDF
downloads. No source-code change was made during this audit.

No archive.org, Wayback, or CDX matches were found in the targeted search of
UP CSV/JSONL discovery records, excluding request logs. This is a limited
search of recorded evidence, not proof that no earlier archive requests
were made elsewhere.

## Authoritative discovery routes

- District website directory: https://igod.gov.in/index.php/sg/UP/E042/organizations
- SEC district/body frame: https://sec.up.nic.in/site/rural_list.aspx
- Dated SEC results index: https://sec.up.nic.in/site/electionresult.aspx
- CDX pagination documentation: https://github.com/internetarchive/wayback/tree/master/wayback-cdx-server

The government directory reports 75 districts, but its initial visible page
contains only 25 district entries. Pagination must be acquired before any
75-district completion claim. The directory also links district block lists.
Present-day district/block lists are discovery frames, not historical boundary
crosswalks.

The SEC results index explicitly links `ElecLive/WinnerList.aspx` under
Panchayat General Election 2015. This supplies official year context for the
previously acquired native HTML table. It does not date every other endpoint
with a similar name. The index also links a 2010 block-head result PDF at
`https://sec.up.nic.in/site/fonts/KPP_result_2010.pdf`.

## Acquisition status

`seeds.csv` contains three official context URLs and two bounded CDX queries.
`context_receipts.json` preserves the initial five failed saves caused by an
omitted `raw/` directory. The approved rerun through the existing historical
harvester succeeded; `current_receipts.json` and `requests.jsonl` describe the
saved responses. The initial failures are not archive misses.

The correct SEC host returned 4,544 archived URL-key entries, including 1,652
PDF URL/MIME candidates, of which 1,481 have a recorded HTTP 200 capture. The
old hostname returned one archived homepage with HTTP 404. These are archive
discovery counts, not confirmed relevant documents or all historical captures.

The directory's pagination URLs redirect ordinary requests to its homepage.
`directory_pages/` retains those responses; they are not successful district
enumeration despite HTTP 200. Retrying with the public site's own
`X-Requested-With: XMLHttpRequest` and Referer headers returned the remaining
ten HTML fragments, saved under `directory_ajax/`. No Indian IP was needed.

The initial 25 district hosts have been queried, yielding 80,462 archived
URL-key entries and 17,997 PDF candidates. Two inventories require CDX
continuation; 23 returned entries without a continuation key. The 25 block
directory pages yielded 287 block names. These are present-day discovery
names, not a historical administrative crosswalk.

`district_archive_ledger.csv`, `district_archive_url_inventory.csv`,
`block_search_frame.csv`, and `cdx_continuations.csv` retain the measured
scope and unfinished queries. The attempt to extend enumeration to the
remaining 50 districts failed on a local list-versus-mapping receipt format
mismatch. Its correction was disclosed and is pending approval; the cached
directory fragments and first 25 districts' evidence remain intact.

No paid inference was used for this archive audit. The separately authorized
Haryana OCR budget does not authorize paid UP extraction.

## Coverage ledger requirements

Track district, block, office, election year, query route, host/alias,
request URL, retrieval time, response status, capture timestamp, source hash,
continuation state, and document-review state separately.

1. Enumerate every directory page and district's block frame with provenance.
2. Query the correct SEC host and all district hosts, retaining historical
   host aliases where supported by sources. Follow CDX continuation keys.
3. Inspect archived notice/index pages as well as PDF URLs; resolve linked
   CDN objects and query-string downloads from captured HTML.
4. Map recovered documents to their actual district/block, office, and years.
   A district-wide source can cover multiple blocks, but a host query alone
   does not establish block-level document coverage.
5. Search remaining block gaps using source spellings and historical names,
   including archived departmental pages and identifiable newspaper mirrors.
6. Keep `not_attempted`, `request_failed`, `partial_inventory`,
   `complete_query_no_matches`, `candidate_found`, `downloaded`, and
   `source_reviewed` distinct. An exhausted query is not proof that a
   historical reservation assignment never existed.

The earlier Ballia/Kanpur Dehat collection and existing UP holdings remain
separate acquisitions; no canonical data or old inventories were overwritten.

## State ownership and integration

The UP-owned reconciliation is in
`local_elections_up/data/integration/central_2026_09_10/`. It identifies the
59,019-row omitted 2015 wave and explains the 2021 one-row difference as two
winner-marked records under one candidate-seat key, not an established extra
seat. The released master and adapter have not been changed.

These central discovery acquisitions remain staging evidence until a
manifest-backed handoff to the UP repository. No source bytes have been
deleted, moved, or claimed as published release assets.

## Execution update after handoff

The local receipt-format issue has been resolved. All 75 district hosts were
queried, and all 20 returned continuation keys were followed to exhaustion.
The current block-directory frame contains 826 names across 75 districts,
with no discrepancy against the per-page directory counts.

Current counts, request outcomes, and unfinished historical scope are in
`district_sweep_summary.json`. `panchayat_source_queue.csv` narrows the broad
URL inventory; `non_election_url_triage.csv` records education/recruitment-like
URLs separately. Neither queue is a document-validation result.

The top 21 URLs mentioning both panchayats and reservation have been submitted
to the existing harvester under the sibling `archived_reservations/`
collection. Its acquisition receipts, not this note, determine download status.
All of these collections now reside in local_elections_up, not centrally.
