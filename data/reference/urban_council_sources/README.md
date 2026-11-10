# UP corporation councilor sources

This packet adds official 2023 councilor records and checks the existing 2012 and 2017 handoffs. It concerns municipal corporation **ward members**, not mayors or municipal chairpersons. Sources were retrieved November 9, 2026 UTC. No effects are estimated here.

## Coverage

| Election/source | Winner rows | Explicit winner sex | Reservation | Scope |
|---|---:|---:|---:|---|
| Existing 2012 SEC release | 980 | 980 | 980 | Corporation winners held in this repository |
| Existing 2017 SEC release | 1,300 | 1,300 | 1,300 | Corporation winners held in this repository |
| Recovered 2023 SEC results | 100 | 100 | 100 | All 60 Ayodhya wards; 40 of 90 Aligarh wards |
| Recovered 2023 Lucknow municipal PDF | 110 | 0 | 0 | All 110 Lucknow wards |

The 2023 supplement has 210 distinct `(year, city, ward_number)` keys. Sex, education, age, reservation, and votes are printed in the SEC table. The Lucknow PDF prints ward numbers, names, winners, and parties; it does not print sex, education, age, reservation, or votes. Those fields remain missing. Sex is never inferred from names or from seat reservation. The SEC table records 39 women and 38 women-reserved wards, confirming that these are distinct variables.

The existing 2023 reservation roster covers 1,420 corporation wards. This supplement does **not** recover 1,420 winners. Nine archived captures from May 2023 through July 2026 all contain the same first 100 results; they are not nine different samples. Aligarh remains incomplete, and no new 2023 Kanpur or Varanasi winner list was recovered in this pass. Live SEC endpoints timed out during collection. The archived result page's pagination does not supply the missing pages.

`ZYCResults2023.aspx` concerns the District Planning Committee election. Its education/sex fields must not be mistaken for a general municipal councilor census.

## Checks on earlier data

The parser verifies the saved HTML hashes and reproduces six fields for all 2,280 historical winners: name, sex, reservation, education, ward name, and body name. This checks the handoff against the retained source; it does not establish that every source entry is correct.

For 2012, a one-to-one merge of winners and the independently held reservation roster uses normalized district name and the printed ward number. In the roster, that number is held in `ward_code_raw`; `ward_number` is empty. The comparison matches all 980 winners and leaves 60 Saharanpur roster wards without a winner record. Women-quota status agrees for 977 winners. The three disagreements are Ghaziabad wards 43 and 77 and Bareilly ward 20: the result page prints OBC without a women qualifier, whereas the roster prints women. Neither source silently replaces the other. Lucknow (110), Kanpur (110), and Varanasi (90) have no quota disagreement in this within-election check.

Two source body labels need a separate canonical label. The source itself prints `नगर निगम लखनऊô` and, for 70 Aligarh records, `बिसौली`. These are not extraction errors. `body_label_review.csv` records the reviewed labels without changing the originals. The Aligarh identification rests on the printed district and a separate Aligarh reservation roster: all 70 ward numbers and quota statuses agree, and 69 ward names agree after whitespace normalization. The remaining ward name is a spelling difference (खैर/खौर रोड). This identifies the municipality; it is not evidence of continuity across elections.

## Geographic eligibility

No cross-election ward link is validated by this packet. Matching a ward number or name, or observing the same number of wards, is insufficient. In particular, Lucknow has 110 wards in both historical releases, but ward 1 has different names in 2012 and 2017.

The retained Lucknow notification dated September 6, 2017 explicitly divides the corporation into 110 wards after consideration of objections and supplies ward extents in its annex. Its first page was visually checked. The earlier English PDF hosted under a May 2017 filename has blank notification/date fields and should not be cited as the final notification. The 2022 final delimitation PDF and the state urban delimitation order are also preserved. They provide primary material for constructing geographic links, not an already validated crosswalk. Kanpur and Varanasi continuity likewise remains unverified.

Consequently, these records are usable for descriptive comparisons within their stated source coverage. They do not yet justify new longitudinal persistence estimates. In particular, Lucknow's newly recovered 2023 names do not supply a female-winner outcome. Aligarh's 40 rows must not be treated as a complete city.

## Files and reproduction

`acquisition_log.json` documents five primary PDFs, their URLs, retrieval dates, sizes, and SHA-256 hashes. `archive_search.json` retains the bounded archive search. `archive_fetch.json` documents nine replayed HTML payloads and exact capture/replay URLs; hashes refer to decompressed bytes. Archive discovery/replay used the standard Python `wayback` client. Retained HTML is compressed once; PDF originals are unchanged. Existing historical HTML stays in its original collection location and is not copied into this packet.

From the repository root, with the project dependencies installed:

```sh
PYTHONPATH=src python -m local_elections_up.parse.parse_urban_council_sources
PYTHONPATH=src python -m pytest -q tests/test_urban_council_sources.py
ruff check src/local_elections_up/parse/parse_urban_council_sources.py tests/test_urban_council_sources.py
```

The parser is offline and writes `data/build/urban_council_sources/`: a typed 2023 Parquet supplement, historical source checks, the 2012 reservation comparison, schema, and checksums. This is a source supplement, not a replacement of the established release files. `dictionary.csv` defines its fields. The parser preserves Kruti Dev bytes from the Lucknow PDF and decodes winner names in PDF content-stream order; spatial glyph sorting corrupts some names. Raw ward and party text from that PDF remains in the original font encoding and should not be used as Unicode labels without decoding and review. No transliteration or name-based sex inference is performed.
