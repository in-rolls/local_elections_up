# Kanpur Dehat samiti source review

Six 2021 pages were held because Tesseract OSD confidence was below the routing threshold. Direct visual inspection of the source PDFs established a clockwise correction of 270 degrees for each. The original PDFs and the first OCR run remain unchanged.

`kanpur_dehat_samiti_2021_orientation_reviews.json` pins each decision to a PDF SHA-256 and one-based PDF page. The OCR wrapper records the review-file hash and retains the automatic OSD output alongside the explicit decision. Only the six reviewed pages are reprocessed in a separate output directory.

`kanpur_dehat_samiti_2021_reviewed_cells.csv` contains 56 source-transcribed rows from those pages. It covers printed serial, territorial ward number, category, and the women-reservation marker only. Names and boundary descriptions have not been certified. These are single-reviewer DIAGNOSE observations, not an independent holdout or a statewide accuracy estimate. `URW` denotes the women's-only unreserved category; it does not infer a candidate's gender.

## Layout findings

- Printed serial and territorial ward number are different fields. For example, Rajpur page 6 has serial 62 and territorial ward 61.
- Akbarpur page 6 prints column number 12 twice. Use the actual heading and physical grid column, not printed ordinal alone.
- Rasulabad page 3 omits the document title and numbered-column row. It retains the substantive category headings.
- Reservation labels occupy one of eight physical category columns. Dashes in other columns do not each create additional observations.
- Page-level OCR after orientation correction still loses digits and words on the Sandalpur diagnostic page. Rotation recovery alone is not sufficient for structured publication. Extraction needs grid-aware segmentation or a separately authorized visual-model pass, followed by field-level source comparisons.

The source manifest records original URLs and hashes. These reviews do not establish acquisition times or archive capture dates that were not recorded.
