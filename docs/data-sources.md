# Data Sources

The API serves static JSON files from `data/` at runtime. No upstream API calls are made during requests.

- `data/sources.json` is the machine-readable source registry for current datasets.
- Raw source material is handled offline.
- The checked-in JSON files under `data/` are the curated runtime inputs.
- Production requests read only those local JSON files.

| Dataset | Source | Coverage | Licence status | Redistribution status | Update cadence | Last checked | Notes | Remaining verification tasks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Regions | Eurostat LAU 2025 correspondence table | complete | Eurostat reuse terms; verify before redistribution. | verify before redistribution | Eurostat release cycle | `2026-05-27` | 8 Slovak regions verified offline. | Keep monitoring Eurostat reuse terms. |
| Districts | PortalVS classifier 10 (Okres), local REST export filtered to Slovak districts | complete | Source/licence verification pending; PortalVS terms may restrict reuse. | restricted / not open redistribution | Manual | `2026-07-20` | 79 Slovak districts imported from the classifier export; source also contains Czech and foreign rows. | Keep source terms on file and retain upstream notices. |
| Municipalities | PortalVS classifier 9 (Obce), local REST export filtered to current Slovak municipalities | complete | Source/licence verification pending; PortalVS terms may restrict reuse. | restricted / not open redistribution | Manual | `2026-09-07` | 2,927 current Slovak municipality rows; `districtCode` is derived from `code_su` and validated against districts. | Keep source terms on file and retain upstream notices. |
| PSC | PortalVS classifier 42 (PSČ obcí SR a ČR) | partial | PortalVS site terms are restrictive; preserve notices; non-commercial use only. | restricted / not open redistribution | Unknown | `2026-06-02` | 1,420 PSC keys and 3,101 match records; `districtCode` is null throughout; not national coverage. | Verify any allowed use, retain notices, and confirm districtCode mapping. |
| Banks | NBS directory of domestic payment system identification codes | seed-backed | NBS disclaimer allows reuse with attribution and no modification. | allowed with attribution and no modification | Irregular / manual refresh | `2026-05-25` | 5-bank non-exhaustive seed set. | Expand or formally document the current seed scope. |
| Holidays | NBS holidays page and Act 241/1993 | partial | NBS disclaimer allows reuse with attribution and no modification. | allowed with attribution and no modification | Annual legislative updates | `2026-05-25` | Curated 2024-2026 holiday lists. | Confirm any future update source and preserve attribution. |
| Companies | Verified public organizational contact pages | seed-backed | Source/licence verification pending for broader redistribution. | pending verification | Manual | `2026-06-03` | Small checked-in legal-entity seed dataset; not full RPO coverage; personal/stakeholder fields excluded. | Verify RPO/privacy terms and future import terms. |

Notes:

- Regions cover the 8 Slovak self-governing regions and are verified against the Eurostat LAU 2025 correspondence table.
- Municipalities are sourced from PortalVS classifier 9 (`Obce`) and the runtime dataset currently covers 2,927 regular Slovak municipality rows with district mappings derived from `code_su`.
- PortalVS source/licence verification remains pending, so the municipality dataset should not be treated as open redistribution material.
- Districts are now complete in coverage, but PortalVS terms may restrict reuse.
- PSC is expanded beyond the original tiny sample, but it is still not national coverage.
- The checked-in PSC dataset currently contains 1,420 PSC keys and 3,101 match records, with repeated postal codes preserved via `matchCount` and `matches`.
- PSC source terms are restrictive; redistribution is limited and source notices must be preserved.
- PSC geography expansion is local and static; it does not call upstream services.
- Company/IČO work uses a small checked-in local seed dataset and is exposed only as a seed-backed local lookup contract.
- Company/IČO notes intentionally exclude personal, stakeholder, and other role-holder fields.
- RPO licence and privacy verification remain pending; see `docs/research/rpo-licence.md` and `docs/verification-backlog.md`.
- The proposed company schema and source notes live in `docs/dataset-format.md` and `docs/research/ico-sources.md`.
- Record provenance should be checked before any production expansion or redistribution.
- ORSR and ŽRSR remain reference-only in the research notes and are not scraped.
