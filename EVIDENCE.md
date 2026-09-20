# Source evidence

What this repository publishes is the parsed result, its inputs and the proofs
that tie one to the other. The bytes that were fetched to get there are larger
than a git repository should carry, so they are listed here with their sizes and
digests and deposited separately. Nothing below is needed to rebuild the
release; everything below is what you would check the release against.

## Held in this repository

| Path | Size | What it proves |
|---|---|---|
| `data/archives/up-historical-sources-2006-2015-20260911.tar.gz` | 78 MB | The historical source documents for 2006-2015, with `.sha256` and a verification report beside it |
| `data/discovery/2026-09-10/` | 24 MB | What was searched for on 2026-09-10 and what was found: the coverage inventory (gzipped), the catalogs, and the per-district findings |
| `data/source_archives/` | 5 files | The checksummed archives the pipeline reads |
| `data/release/CHECKSUMS.sha256` | - | A digest for every published table |

## Deposited, not committed

| What | Size | Files | SHA-256 |
|---|---|---|---|
| `data/recovery/` | 4.5 GB | 473103 | per-file digests in the deposit |
| `data/source_archives/up_discovery_2026-09-10.tar.gz` | 114 MB | 1 | `7bbf0c3987a6500f69084aeb50e895451210d21edb20beceb13b8964ed46da88` |
| `data/discovery/**/raw/` | 151 MB | 247 | per-file digests in the deposit |
| `data/discovery/.../district_archive_url_inventory.csv` (uncompressed) | 124 MB | 1 | `029fe65b098c9f65742c53228f3636cb3e1ac7b787ee1316eaf94b7f63824083` |

The last one is committed in its gzipped form, which is a tenth of the size and
the same bytes once expanded. GitHub refuses any file over 100 MB, which is why
the first two cannot live here whatever their merit.

## Not kept

`data/interim/` holds build intermediates: 2.1 GB of it is twenty dated
snapshots of the release that `data/release` carries the current copy of, and
the rest the pipeline rebuilds from the committed inputs.
