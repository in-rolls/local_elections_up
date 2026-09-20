# Source evidence

Consumer tables live under `data/release/`. Original source bytes and saved extraction outputs are separately preserved; they are needed to rebuild and audit the release.

See the [source archive inventory](data/catalogs/evidence_archives.json) for asset sizes and SHA-256 hashes, and the [restoration instructions](data/catalogs/SOURCES.md). The compressed member inventory records individual source hashes. The recovery archive is split into ordered parts because a complete archive exceeds the per-asset size limit.

Older discovery and reviewed research bundles are documented in [data/source_archives/README.md](data/source_archives/README.md) and [RESEARCH.md](RESEARCH.md). Their acquisition receipts and original paths remain unchanged.

Superseded office-build snapshots are preserved in the separate split zstd archive listed in the [snapshot inventory](data/catalogs/superseded_snapshots.json). All 713 member hashes were checked locally, and every archive part was downloaded from GitHub and hash-verified before removing the redundant local snapshot cache. These snapshots are audit evidence, not production inputs.
