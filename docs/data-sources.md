# Data Sources

The API serves static JSON files from `data/` at runtime. No upstream API calls are made during requests.

- `data/sources.json` is the machine-readable source registry for current datasets.
- Raw source material is handled offline.
- The checked-in JSON files under `data/` are the curated runtime inputs.
- Production requests read only those local JSON files.

| Dataset | Source | Coverage | Licence status | Redistribution status | Update cadence | Last checked | Notes | Remaining verification tasks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Regions | Eurostat LAU 2025 correspondence table | complete | verify before redistribution | verify before redistribution | Eurostat release cycle | `2026-05-27` | 8 Slovak regions verified offline. | Keep monitoring Eurostat reuse terms. |
| Districts | PortalVS classifier 10 (Okres) / unverified district seed dataset | seed-backed | Source/licence verification pending. | pending verification | Manual | `2026-06-03` | 9-record seed-only set; not authoritative yet. | Confirm exact upstream provenance and redistribution terms. |
| Municipalities | Eurostat LAU 2025 correspondence table | partial | verify before redistribution | verify before redistribution | Eurostat release cycle | `2026-05-30` | 2,927 municipalities; `districtCode` remains null because the source does not provide district mappings. | Document any future district enrichment source. |
| PSC | PortalVS classifier 42 (PSČ obcí SR a ČR) | partial | Source/licence verification pending. | pending verification | Unknown | `2026-06-02` | 1,420 PSC keys and 3,101 match records; `districtCode` remains null where no reliable mapping exists; not national coverage. | Verify PSC licence/redistribution terms and districtCode mapping. |
| Banks | NBS directory of domestic payment system identification codes | seed-backed | Source/licence verification pending. | pending verification | Irregular / manual refresh | `2026-05-25` | 5-bank non-exhaustive seed set. | Expand or formally document the current seed scope. |
| Holidays | NBS holidays page and Act 241/1993 | partial | Source/licence verification pending. | pending verification | Annual legislative updates | `2026-05-25` | Curated 2024-2026 holiday lists. | Confirm redistribution terms and future update source. |
| Companies | Verified public organizational contact pages | seed-backed | Source/licence verification pending for broader redistribution. | pending verification | Manual | `2026-06-03` | Small checked-in legal-entity seed dataset; not full RPO coverage; personal/stakeholder fields excluded. | Verify RPO/privacy terms and future import terms. |

Notes:

- Regions cover the 8 Slovak self-governing regions and are verified against the Eurostat LAU 2025 correspondence table.
- Municipalities are expanded from the Eurostat LAU 2025 workbook, but district codes remain null because the source does not provide district mappings.
- Districts remain seed-only and the district-level source is still being verified.
- PSC is expanded beyond the original tiny sample, but it is still not national coverage.
- The checked-in PSC dataset currently contains 1,420 PSC keys and 3,101 match records, with repeated postal codes preserved via `matchCount` and `matches`.
- PSC source/licence verification is still pending.
- PSC geography expansion is local and static; it does not call upstream services.
- Company/IČO work uses a small checked-in local seed dataset and is exposed only as a seed-backed local lookup contract.
- Company/IČO notes intentionally exclude personal, stakeholder, and other role-holder fields.
- RPO licence and privacy verification remain pending; see `docs/research/rpo-licence.md` and `docs/verification-backlog.md`.
- The proposed company schema and source notes live in `docs/dataset-format.md` and `docs/research/ico-sources.md`.
- Record provenance should be checked before any production expansion or redistribution.
- ORSR and ŽRSR remain reference-only in the research notes and are not scraped.
