# Source evidence

Consumer tables live under `data/release/`. Original source bytes and saved extraction outputs are separately preserved; they are needed to rebuild and audit the release.

See the [source archive inventory](data/catalogs/evidence_archives.json) for asset sizes and SHA-256 hashes, and the [restoration instructions](data/catalogs/SOURCES.md). The compressed member inventory records individual source hashes. The recovery archive is split into ordered parts because a complete archive exceeds the per-asset size limit.

Older discovery and reviewed research bundles are documented in [data/source_archives/README.md](data/source_archives/README.md) and [RESEARCH.md](RESEARCH.md). Their acquisition receipts and original paths remain unchanged.

Superseded office-build snapshots remain in the local `data/interim/release_snapshots/` cache until their separate archive has been verified remotely. They are not production inputs and are not represented as published evidence assets.
