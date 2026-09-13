# Etah reservation research

These are source observations, not certified reservation assignments or a
statewide historical panel. They remain separate from `data/fin/`.

The archived 121-page Etah PDF prints retrospective reservation columns for
1995, 2000, and 2005, and a prospective 2010 allocation column. Its SHA-256 is
`53bfc78b35fb351dcf8f6fed54c3f07c0e51b51ea244266ed174e9ef3295fe29`;
the archive capture is `20101207092710`.

The extraction retains 8,168 physical observation/year rows and 2,044 exact
raw-name-group/year rows. The 511 raw block/name groups are not verified
administrative identities. Repeated printings, source-numbering contradictions,
blank cells, literal zero codes, and conflicting assignments are preserved.

## Rebuild dependencies

```sh
uv sync --all-groups
uv run pytest -q tests/test_etah_source_profile.py
```

The `research` dependency group pins the central `local-reservations` package
to a Git revision. Its shared KrutiDev decoder is used as code only: no central
corpus data is needed. Each generated manifest also records the decoder source
hash, helper source hash, input hash, and source-profile hash.

After restoring the source-evidence inputs, the frozen native extractor can
replay the PDF into a new directory:

```sh
uv run --group research python \
  data/interim/etah_reservations_2010_grid_v6/extractor_snapshot.py \
  --root . --output /tmp/etah_grid_replay
```

The `grid_v6` artifacts use the pinned PyArrow 23 writer. Their values and
dtypes match the earlier PyArrow 25 extraction, whose bytes are preserved in
the original research checkout. No reservation or name values changed in this
writer transition.

Run the decoder on each table in
`data/interim/etah_reservations_2010_grid_v6/` with `--columns block_raw gp_name_raw`
and `--profile data/catalogs/etah_2010_font_profile_v1.json`. Use a new output
directory; existing outputs and manifests are immutable. Then run
`scripts/apply_reservation_codebook.py` with
`data/catalogs/etah_2010_reservation_codebook.json`. The observation table uses
`--code-column reservation_raw`; the name-group table uses
`--code-column reservation_raw_agreed`.

## Source review boundaries

The Etah font profile corrects the leading colon-encoded glyph in two GP-name
labels, using source cells on PDF pages 34 and 104. It is scoped to this PDF
hash and the GP-name column. It does not import Sitapur's part-marker rules or
certify whole-name spelling, place identity, or historical boundaries.

The reservation codebook distinguishes section-supported interpretations from
inferred compound-code meanings. Two 2010 name-group conflicts and unresolved
zero codes remain explicit. All normalized outputs retain
`reservation_assignment_usable = false`; neither blanks nor conflicts are
silently converted to unreserved seats.

The JSON catalogs are the machine-readable review inputs. Larger raw and
intermediate artifacts belong in evidence archives, with checksums, rather
than Git history. Their publication does not promote them into `data/fin/`.
