# Data Sources

The API serves static JSON files from `data/` at runtime. No upstream API calls are made during requests.

| Dataset | File | Source name | Source URL | Licence / terms | lastUpdated used by API | Coverage | Imported or curated |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Banks | `data/banks.json` | Manual MVP seed dataset | Source/licence verification pending. | Source/licence verification pending. | `2026-05-25` | Small, non-exhaustive seed set | Manually curated |
| Holidays | `data/holidays.json` | Static holiday dataset | Source/licence verification pending. | Source/licence verification pending. | `2026-05-25` | 2024-2026 holiday lists | Manually curated |
| Regions | `data/regions.json` | Manual geography seed dataset | Source/licence verification pending. | Source/licence verification pending. | `2026-05-27` | Complete 8-region set | Manually curated |
| Districts | `data/districts.json` | Manual geography seed dataset | Source/licence verification pending. | Source/licence verification pending. | `2026-05-27` | Seed coverage only | Manually curated |
| Municipalities | `data/municipalities.json` | Manual geography seed dataset | Source/licence verification pending. | Source/licence verification pending. | `2026-05-27` | Seed-only and incomplete | Manually curated |
| PSC | `data/psc.json` | Static PSC seed dataset | Source/licence verification pending. | Source/licence verification pending. | `2026-05-27` | Partial seed coverage with local geography links where available | Manually curated |

Notes:

- Regions are complete for the 8 Slovak self-governing regions.
- Districts, municipalities, and PSC entries are intentionally incomplete seed data.
- PSC geography expansion is local and static; it does not call upstream services.
- Record provenance should be checked before any production expansion or redistribution.
