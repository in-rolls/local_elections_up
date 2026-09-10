# UP discovery evidence, 2026-09-10

The compact catalogs in `data/catalogs/up_discovery_2026-09-10` describe the search frame and acquired sources. The full discovery tree is preserved in `up_discovery_2026-09-10.tar.gz`, not duplicated in Git.

The archive contains 312 files: 296,922,147 original bytes compressed to 119,296,382 bytes, a 59.8% reduction. Every member was decompressed and checked against its original SHA-256. Filenames and contents are unchanged; archive timestamps and ownership are normalized.

Download the archive from the repository's `source-evidence-2026-09-10` release into `data/source_archives`, then restore it from the repository root:

```sh
gh release download source-evidence-2026-09-10 --repo in-rolls/local_elections_up --pattern up_discovery_2026-09-10.tar.gz --dir data/source_archives
tar -xzf data/source_archives/up_discovery_2026-09-10.tar.gz
```

The manifest records the archive hash, original member paths, byte counts, and file hashes. Acquisition receipts and raw responses remain unchanged inside the archive. The directory layout is restored exactly, so receipts still resolve to their evidence.

This is a source-evidence snapshot, not a new analysis-ready release. The current-host archive search covers all 75 districts and the discovery frame lists 826 blocks, but historical aliases and document contents are not exhaustively reviewed. The 2010 Sitapur extraction remains local staging because column-boundary errors were detected; those parser outputs are not part of this snapshot. Haryana OCR is unrelated and excluded.
