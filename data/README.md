# Data layout

For analysis, start with [release/CATALOG.md](release/CATALOG.md). It lists the row unit, years, counts, and status of each table. [release/DICTIONARY.md](release/DICTIONARY.md) describes its columns and keys.

| Directory | Contents | Role in a build |
| --- | --- | --- |
| `release/` | GP records, office observations, panels, and Weaver preparations | Published outputs |
| `catalogs/` | Explicit input paths, hashes, definitions, and archive inventories | Selects and documents inputs |
| `raw/` | Registered source files and acquisition manifests | Source evidence |
| `interim/` | Saved parsing and enrichment outputs | Registered build inputs; most restored from archives |
| `crosswalks/` | Reviewed geographic matches and corrections | Transformation inputs |
| `external/` | Attributed Weaver and LGD sources | External inputs |
| `discovery/` | Leads and exploratory source collections | Excluded unless explicitly registered |
| `recovery/` | Restored historical source responses | Evidence at original receipt paths |
| `source_archives/` | Research archive documentation | Separate evidence bundles |

Older year-named directories and loose source files retain their receipt paths. They are source evidence, not the current analytical tables. Original paths are also preserved inside the [source archives](catalogs/SOURCES.md); moving them without updating the registry would break provenance checks.

The build follows **source bytes → saved extraction → registered transformation → release table**. A candidate row, a reported winner, a reservation statement, and a geographic link have different units. Check the catalog before counting or joining them. Office observations remain provisional (`assignment_usable=false`).
