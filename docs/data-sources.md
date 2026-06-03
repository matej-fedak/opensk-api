# Data Sources

The API serves static JSON files from `data/` at runtime. No upstream API calls are made during requests.

- `data/sources.json` records the machine-readable source registry for current datasets.
- Raw source material is handled offline.
- The checked-in JSON files under `data/` are the generated/curated runtime inputs.
- Production requests read only those local JSON files.

| Dataset | File | Source name | Source file | Source URL | Licence / terms | lastUpdated used by API | Coverage | Imported or curated |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Banks | `data/banks.json` | Manual MVP seed dataset | n/a | Source/licence verification pending. | Source/licence verification pending. | `2026-05-25` | Small, non-exhaustive seed set | Manually curated |
| Holidays | `data/holidays.json` | Static holiday dataset | n/a | Source/licence verification pending. | Source/licence verification pending. | `2026-05-25` | 2024-2026 holiday lists | Manually curated |
| Regions | `data/regions.json` | Eurostat LAU 2025 correspondence table | `EU-27-LAU-2025-NUTS-2024.xlsx` | https://ec.europa.eu/eurostat/web/nuts/local-administrative-units | Eurostat reuse terms; verify before redistribution. | `2026-05-30` | 8-region set | Verified offline |
| Districts | `data/districts.json` | Unverified district seed dataset | n/a | Source/licence verification pending. | Source/licence verification pending. | `2026-05-27` | Seed coverage only | Manually curated |
| Municipalities | `data/municipalities.json` | Eurostat LAU 2025 correspondence table | `EU-27-LAU-2025-NUTS-2024.xlsx` | https://ec.europa.eu/eurostat/web/nuts/local-administrative-units | Eurostat reuse terms; verify before redistribution. | `2026-05-30` | Expanded LAU coverage; district codes remain null in the imported file | Imported and verified offline |
| PSC | `data/psc.json` | PortalVS Číselníky classifier 42 | `https://ciselniky.portalvs.sk/api/rest/json/42` | Source/licence verification pending. | Source/licence verification pending. | `2026-06-02` | 5 checked-in postal codes with partial geography links; imported PSC records currently have `districtCode: null`; not national coverage | Manually curated |
| Companies | local JSON pending | IČO/company research prototype | n/a | Source/licence verification pending. | Source/licence verification pending. | `2026-06-03` | Prototype-only local company lookup; no checked-in production company dataset; personal/stakeholder fields intentionally out of scope | Experimental / dataset pending |

Notes:

- Regions cover the 8 Slovak self-governing regions and are verified against the Eurostat LAU 2025 correspondence table.
- Municipalities are expanded from the Eurostat LAU 2025 workbook, but district codes remain null because the source does not provide district mappings.
- Districts remain seed-only and the district-level source is unverified.
- PSC is expanded beyond the original tiny seed-only sample, but it is still not national coverage.
- The checked-in PSC file currently contains 5 codes; geography links are only present where local mappings exist.
- Imported PSC records currently have `districtCode: null` because the source data does not provide a reliable district mapping.
- PSC source/licence verification is still pending.
- PSC source rows may repeat the same postal code; the importer/preview should preserve that ambiguity with `matchCount` and `matches`.
- PSC geography expansion is local and static; it does not call upstream services.
- Company/IČO work is research-only and is exposed only as an experimental local lookup contract.
- Company/IČO notes intentionally exclude personal, stakeholder, and other role-holder fields.
- The proposed company schema and source notes live in `docs/dataset-format.md` and `docs/research/ico-sources.md`.
- Record provenance should be checked before any production expansion or redistribution.
- ORSR and ŽRSR remain reference-only in the research notes and are not scraped.
