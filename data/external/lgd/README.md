# Historical LGD geography inputs

These files are attributed snapshots from
[`in-rolls/quota_raj` at `50fbe05662a8f2a84c66e5b262df4c6c0051503d`](https://github.com/in-rolls/quota_raj/tree/50fbe05662a8f2a84c66e5b262df4c6c0051503d).
`SOURCES.json` records their original paths and SHA-256 checksums, the originating
matching scripts, and the four immutable UP election-panel inputs.

- `lgd_up_block_gp.csv`: the processed LGD GP-to-block directory.
- `up_village_gp_mapping_2024.csv`: the received 2024 LGD village-to-GP directory,
  including administrative and Census identifier crosswalks. It contains no
  Census outcomes or SHRUG covariates.
- `../../crosswalks/active/up_block_xwalk.csv`: the reviewed historical election
  block-to-LGD crosswalk, distinct from the existing 2021 block crosswalk.

The historical bridge in `data/fin/up_gp_lgd_bridge.parquet` preserves the
reference matching universe: **2005–2010 linked election records with known
reservation in both waves**. This is an explicitly retained reference vintage,
not a full-2010 geographic directory. Later-panel projections likewise retain
the reference's known-reservation eligibility and ambiguous-name exclusions.

The producer also measures sensitivity to using all records in the linked
panels. Adding records changes which GPs compete for the same LGD destination
and expands the names available for propagation. That alternative is recorded
in `data/crosswalks/audit/up_lgd_full_linked_panel_sensitivity.csv`; it does not
replace the reference bridge. A full-2010-source bridge would be a further
linkage decision requiring separate validation.

Two inherited mixed-script identities are documented in
`../../crosswalks/active/up_historical_lgd_reviewed.csv`. The source names
`सखौलीकला` (Sultanpur/Lambhua) and `अलीपर कलां` (Muzaffarnagar/Baghra) agree in
both 2005 and 2010. The reviewed LGD blocks, village identifiers and comparisons
against all GPs in each block support their existing destinations. The CSV
records the original PDF/page fields as reported by the source, the native
names, LGD identities, reviewer, rationale, and both distance calculations.
These decisions are checked against the exact source anchor, names and block;
they cannot override a competing automatic assignment.

The Unicode-safe matcher preserves vowel marks. These two identity decisions
carry `gp_match_type = "reviewed"` and a `mapping_review_id`; their reported
`match_distance` uses the current vowel-preserving comparison. The legacy
scores remain in the review evidence only. They do not override current
scores or influence ranking.
