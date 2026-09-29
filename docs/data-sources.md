# Data Sources

The API serves static JSON files from `data/` at runtime. No upstream API calls are made during requests.

- `data/sources.json` is the machine-readable source registry for current datasets.
- `docs/source-compliance.md` is the detailed compliance matrix for licence, redistribution, attribution, and risk status.
- `docs/research/source-verification-evidence.md` records retained source-verification evidence.
- `docs/research/source-licence-questions.md` lists draft questions for source owners; questions are not sent automatically.
- Raw source material is handled offline.
- The checked-in JSON files under `data/` are the curated runtime inputs.
- Production requests read only those local JSON files.

| Dataset | Source | Coverage | Licence status | Redistribution status | Update cadence | Last checked | Notes | Remaining verification tasks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Regions | Eurostat LAU 2025 correspondence table | complete | Eurostat reuse terms; verify before redistribution. | verify before redistribution | Eurostat release cycle | `2026-05-27` | 8 Slovak regions verified offline. | Keep monitoring Eurostat reuse terms. |
| Districts | PortalVS classifier 10 (Okres), local REST export filtered to Slovak districts | complete | Source/licence verification pending; PortalVS terms may restrict reuse. | restricted / not open redistribution | Manual | `2026-07-20` | 79 Slovak districts imported from the classifier export; source also contains Czech and foreign rows. | Keep source terms on file and retain upstream notices. |
| Municipalities | PortalVS classifier 9 (Obce), local REST export filtered to current Slovak municipalities | complete | Source/licence verification pending; PortalVS terms may restrict reuse. | restricted / not open redistribution | Manual | `2026-09-07` | 2,927 current Slovak municipality rows; `districtCode` is derived from `code_su` and validated against districts. | Keep source terms on file and retain upstream notices. |
| PSC | PortalVS classifier 42 (PSČ obcí SR a ČR) | partial | Source/licence verification pending; PortalVS terms may restrict reuse. | restricted / not open redistribution | Unknown | `2026-09-07` | 1,420 PSC keys and 3,101 match records; `districtCode` is backfilled from `municipalityCode` using local municipality mappings; not national coverage. | Verify any allowed use, retain notices, and keep backfill provenance documented. |
| Banks | NBS directory of domestic payment system identification codes | complete | Source/licence verification pending. | pending verification | Manual refresh from NBS directory snapshots | `2026-09-12` | 30 domestic Slovak payment-system identification-code rows imported from NBS directory version 225, effective from `2026-05-18`; 21 active and 9 inactive. Foreign/non-SK BIC rows are excluded. | Keep source/licence terms on file and refresh from future NBS directory snapshots. |
| Holidays | NBS holidays page and Act 241/1993 | partial | NBS disclaimer allows reuse with attribution and no modification. | allowed with attribution and no modification | Annual legislative updates | `2026-05-25` | Curated 2024-2026 holiday lists. | Confirm any future update source and preserve attribution. |
| Companies | Verified public organizational contact pages; RPO research pending production approval | seed-backed | Seed sources verified individually; RPO API docs identify CC BY 4.0 but production acquisition/reuse evidence remains incomplete. | seed-backed only; RPO bulk/local snapshot redistribution pending acquisition-gate approval | Manual | `2026-09-18` | Small checked-in legal-entity seed dataset; not full RPO coverage; personal/stakeholder/person-role fields excluded. 0.14.0 kept production data unchanged. | Verify official or otherwise justified RPO bulk/local snapshot acquisition, redistribution terms, rate limits, provenance, and privacy filtering. |
| VAT registrations | Finančná správa SR `Zoznam daňových subjektov registrovaných pre DPH` | research/tooling only | Current PFS export page states CC0 for the relevant ZIP group; Open Data catalogue lists CC 4.0 international, discrepancy retained. | No production runtime dataset; privacy gate blocked. | Daily | `2026-09-28` | Official ZIP works and contains XML/XSD, but XML has no natural/legal subject marker and includes names/addresses. | Identify a reliable subject-type discriminator or approve a minimum-data privacy policy before production promotion. |
| Trade registrations / ŽRSR | Živnostenský register SR, human-facing search | research-only | No machine-readable source licence or reuse grant verified. | No production runtime dataset; acquisition/reuse/privacy gates blocked. | Unknown | `2026-09-29` | Only a public HTML search interface was verified. No official bulk export, open-data distribution, documented API, WSDL, CSV, XML, or JSON source was approved. | Find an official documented non-scraping source with clear reuse rights and deterministic privacy handling. |
| Phone areas | Úrad pre reguláciu elektronických komunikácií a poštových služieb numbering data | complete | Source/licence verification pending. | pending verification | Manual refresh from local regulator workbook snapshots | `2026-09-15` | 2,922 unique municipality-to-primary-area rows imported from retained workbook `30.xls`; 2,919 rows link to local municipality/district/region codes. | Verify licence/reuse terms and monitor unmatched source municipality codes. |
| Vehicle registration codes | Slov-Lex static text of Vyhláška Ministerstva vnútra SR č. 9/2009 Z. z., § 36 ods. 2 | complete | Source/licence verification pending. | pending verification | Historical/reference dataset; manual legal-text review only | `2026-09-15` | 93 legacy two-letter district abbreviations for vehicle registration numbers; 84 link to local district codes and all 93 link to local region codes. Not a current plate lookup. | Verify Slov-Lex legal-text reuse terms and retain exact attribution requirements. |
| School facility counts | MŠVVaM SR Register škôl a školských zariadení aggregate CSV | complete | Creative Commons BY as listed by source. | allowed with attribution, pending exact retained terms | Semiannual MŠVVaM open-data refresh | `2026-09-15` | 1,227 aggregate rows and 7,026 organizational units, valid as of `2025-09-15`; all rows link to local region and district codes. Not an institution-level school directory. | Retain exact CC BY attribution wording and monitor future semiannual refreshes. |

Notes:

- Regions cover the 8 Slovak self-governing regions and are verified against the Eurostat LAU 2025 correspondence table.
- Municipalities are sourced from PortalVS classifier 9 (`Obce`) and the runtime dataset currently covers 2,927 regular Slovak municipality rows with district mappings derived from `code_su`.
- PortalVS source/licence verification remains pending, so the municipality dataset should not be treated as open redistribution material.
- Districts are now complete in coverage, but PortalVS terms may restrict reuse.
- PSC is expanded beyond the original tiny sample, but it is still not national coverage.
- The checked-in PSC dataset currently contains 1,420 PSC keys and 3,101 match records, with repeated postal codes preserved via `matchCount` and `matches`.
- PSC `districtCode` coverage is 100% for current local PSC records after local backfill from `municipalityCode`; no values are inferred from names or PSC patterns.
- PSC source terms are restrictive; redistribution is limited and source notices must be preserved.
- Banks are imported from an offline NBS CSV snapshot; the API does not call NBS from runtime routes.
- Bank `activePartyMarker` preserves the normalized party marker: `C` and `K` are active, `Ø` is inactive.
- PSC geography expansion is local and static; it does not call upstream services.
- Company/IČO work uses a small checked-in local seed dataset and is exposed only as a seed-backed local lookup contract.
- Company/IČO notes intentionally exclude personal, stakeholder, and other role-holder fields.
- VAT registration work is tooling-only; no `data/vat_registrations.json` or public VAT endpoint is present because privacy import is blocked.
- ŽRSR/trade-register work is research-only; no importer, `data/trade_registrations.json`, or public trade endpoint is present because source acquisition is blocked.
- Phone areas are served locally from `data/phone_areas.json`; API routes do not call the telecom regulator.
- Phone-area municipality links are present for 2,919 of 2,922 imported rows; unmatched source municipality codes are retained as rows with null local geography codes.
- Vehicle registration codes are served locally from `data/vehicle_registration_codes.json`; this is historical/reference data only and does not decode full plates or identify current vehicles/owners.
- Bratislava and Košice vehicle-registration abbreviations represent aggregate legal-table rows, so their `districtCode` is null rather than invented from current city district splits.
- School facility counts are served locally from `data/school_facility_counts.json`; source is the MŠVVaM Register škôl a školských zariadení CSV from RIS.
- The school-facility dataset is aggregate count data, not a school directory; `/v1/schools` was intentionally not implemented and no personal staff/pupil data is exposed.
- RPO licence, acquisition, and privacy verification remain pending for production expansion; see `docs/research/rpo-acquisition-decision.md`, `docs/research/rpo-licence.md`, and `docs/verification-backlog.md`.
- The proposed company schema and source notes live in `docs/dataset-format.md` and `docs/research/ico-sources.md`.
- Record provenance should be checked before any production expansion or redistribution.
- ORSR and ŽRSR remain reference-only in the research notes and are not scraped.
- Keep source-compliance warnings until source-owner terms are retained or clarified.
