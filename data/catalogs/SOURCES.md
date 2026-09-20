# Restore the saved release inputs

The source registry in `office_sources.json` selects an explicit saved artifact for each collection and pins its SHA-256. It does not select the newest extraction. The GP source preparations are saved under `data/interim/gp_enriched/`; their original parsing and transliteration notebooks are historical evidence.

The [evidence inventory](evidence_archives.json) lists the source-evidence release and checksummed assets. `evidence_members.jsonl.gz` records each archived file's hash and whether it matches the current path or is a historical snapshot. The archive preserves 473,103 recovery files and the legacy 2015 source bytes removed during consolidation.

Install the GitHub CLI, then download the source assets into `dist/source-evidence`:

```sh
gh release download source-evidence-2026-09-19 --repo in-rolls/local_elections_up --dir dist/source-evidence
(cd dist/source-evidence && shasum -a 256 -c CHECKSUMS.sha256)
cat dist/source-evidence/up_inputs.tar.gz.chunk-* | tar -xz data/interim data/raw data/archives data/transliteration data/reference
cat dist/source-evidence/up_recovery.tar.gz.chunk-* | tar -xz --exclude='*/._*'
make data
make check
```

Run these commands from the matching tagged checkout. Extraction restores the original relative evidence paths. Do not extract a historical snapshot over newer work. The separate `up_legacy_inputs.tar` is preserved for audit and is not an active build input. The archived LGD source manifest predates the v2 relocation; the current tracked manifest records both historical and current input pins.

A missing or changed registered input stops assembly. Acquisition and paid OCR are separate from this offline build. Category decoding, source-byte verification, and substantive assignment validation are distinct checks.

Superseded office builds are archived separately in `up_superseded_snapshots.tar.zst.chunk-*`. They are not build inputs. The [snapshot inventory](superseded_snapshots.json) records every original member hash. To inspect them, install zstd and extract into an empty audit directory:

```sh
mkdir -p dist/snapshot-audit
cat dist/source-evidence/up_superseded_snapshots.tar.zst.chunk-* | zstd -d --long=29 | tar -x -C dist/snapshot-audit
```
