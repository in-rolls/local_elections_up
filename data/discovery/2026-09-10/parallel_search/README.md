# Uttar Pradesh parallel source discovery, 10 September 2026

Source acquisition runs independently of the Haryana OCR job. This collection
used the existing `historical_harvest` command, with no new scraper or provider
code and no metered inference. It is unreleased research material, not an
analysis-ready dataset or a claim of statewide coverage.

## Acquired sources

| Collection | Acquired | Interpretation |
| --- | --- | --- |
| Ballia newspaper-hosted government roster | 1 PDF, 50 pages | Mixed offices and retrospective reservation histories; 2021 is provisional |
| Kanpur Dehat official district index | 1 HTML page and all 22 linked PDFs, 93 pages | Notice dated 25 March 2021; unit labels cover GP heads, intermediate members, intermediate heads and a further roster requiring header confirmation |
| UP SEC result pages | 2 HTML pages | Native tables; precise office selection and election vintage require confirmation |
| SEC `/ElecLive/` directory URL | 1 HTTP error | Failure retained; not a successful source or proof of absent data |

There are 27 requested URLs, 23 PDF successes, three HTML successes and one
HTTP error. Saved response bytes total 89,589,966. Counts describe this bounded
link set, not unique offices or historical assignments.

The first three Ballia pages and the first page of every Kanpur Dehat PDF have
zero native-text characters. These samples require OCR or manual reading;
search-engine table renderings are not a substitute for archived source bytes.

## Primary evidence and caveats

Ballia's [50-page source](https://images1.livehindustan.com/uploadimage/static/document/2021/03/02/ballia_1614706707.pdf)
is preserved under SHA-256
`4769b16fc47ad32009ecb24129a3c34f73bd809121a6de9c48eeebccbbb7a7cf`.
Visual reading of page 1 confirms district-member offices and printed columns
for 1995, 2000, 2005, 2010, 2015 and 2021. The heading explicitly describes
provisional publication. The signature is dated 2 March 2021. Later GP-head
sections were reported by source search but have not yet been visually reviewed.

Two page-1 examples are retained in `source_examples.json`, with original ward
identifiers and printed codes. Ward `06` has `UR, UR, L, BC, SC` across the five
historical years. Ward `51` has `0, 0, 0, 0, STL`. These are transcribed source
examples, not normalized assignments. A printed zero is not unreserved; codes
such as `RL` and `RBC` need the document's own legend. Category-sorted sections
can repeat offices, and a later roster's historical claims do not establish
stable boundaries or contemporaneous validation.

The [Kanpur Dehat district notice](https://kanpurdehat.nic.in/hi/notice/%E0%A4%AA%E0%A4%82%E0%A4%9A%E0%A4%BE%E0%A4%AF%E0%A4%A4-%E0%A4%A8%E0%A4%BF%E0%A4%B0%E0%A5%8D%E0%A4%B5%E0%A4%BE%E0%A4%9A%E0%A4%A8-2021-%E0%A4%86%E0%A4%B0%E0%A4%95%E0%A5%8D%E0%A4%B7%E0%A4%A3/)
supplies the complete 22-link acquisition frame. The displayed office labels
are hints, not substitutes for document headers. Neither final/provisional
status nor historical columns have yet been established from these PDFs.

The SEC [main result table](https://sec.up.nic.in/ElecLive/WinnerList.aspx) and
[ward-linked result table](https://sec.up.nic.in/ElecLive/WinnerListZYC.aspx)
are preserved as HTML. Years in their navigation do not date individual rows.
Office reservation and a candidate's category are separate fields. Contact
numbers present in raw HTML are not needed for the intended analytical extract.

## Provenance and next work

- `source_inventory.csv`: URL, acquisition status, local path, hash, byte/page counts and contextual labels.
- `requests.jsonl` and `kanpur_dehat/requests.jsonl`: append-only fetch receipts, including failure evidence.
- `seeds.csv` and `kanpur_dehat_pdf_seeds.csv`: bounded acquisition inputs; the latter retains its discovery page.
- `discovery_profiles.json` and `kanpur_dehat_format_profiles.json`: initial format observations, not accuracy scores.
- `discovery_summary.json`: acquisition counts and unresolved scope.
- `search_queries.json`: executed query log; the state-level query CSV also records this pass.

Next, establish the SEC tables' election vintage from authoritative dated
context and map their selected offices before offline extraction. Inventory
Ballia's page sections, legends and repeated offices before defining an OCR
frame. Review a Kanpur Dehat sample to decide whether it adds historical
columns or only 2021 reservations. Do not use Haryana's spending authorization
for a separate UP metered run.

No election rows have been added to the released master.
