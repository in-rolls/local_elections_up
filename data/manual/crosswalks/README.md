# Election crosswalks and review files

`active/` contains reviewed corrections that change published election fields.
Every row has a status and review trail. `audit/` is regenerated from the source
data and contains the complete manual-review queue; those rows remain in the
standardized release.

The rule is intentionally conservative: normalization can create candidate
links, but it cannot resolve a collision. A collision becomes linkable only
after a reviewed mapping identifies the intended record.

`active/up_2021_block_xwalk.csv` maps all 728 election district-block groups to
728 distinct current LGD blocks. Candidate blocks were restricted to reviewed
district aliases and ranked without reservation or outcome fields, using exact
normalized GP-name overlap and block-name similarity. Every approved target has
at least two overlaps and a runner-up margin of at least two. The table retains
the evidence and reviewer for each decision.

`active/up_2021_lgd_gp_xwalk.parquet` contains the accepted one-to-one GP links.
The score-stratified labels in `active/up_2021_lgd_gp_validation.csv` gate the
fuzzy threshold. Lower-score proposals, unlinked election rows, unclaimed LGD
rows, and a linkage profile are retained under `audit/`.
