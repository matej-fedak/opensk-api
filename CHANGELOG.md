# Changelog

## 0.11.0

- Added MŠVVaM `Register škôl a školských zariadení` as aggregate school facility count data, not an institution-level school directory.
- Added offline `scripts/import_school_facility_counts.py` for the confirmed local CSV and retained the 2025-09-15 source CSV under `data/raw/`.
- Added `data/school_facility_counts.json` with 1,227 aggregate rows and 7,026 total organizational units; all rows link to local region and district codes.
- Added `GET /v1/school-facility-counts` and `GET /v1/school-facility-counts/stats` endpoints.
- Intentionally did not add `/v1/schools` or per-school lookup routes because the confirmed source CSV contains aggregate rows only.
- Kept privacy guardrails: no school names, addresses, staff, directors, pupils, personal emails, or phone numbers are exposed.

## Unreleased / pre-1.0 stabilization

- Reset project-facing versioning to `0.10.0-dev` so future `1.0.0` can represent the first stable public API contract.
- Documented that earlier `v1.x` labels were internal development milestone labels, not formal stable releases.
- Kept all existing API functionality, endpoint paths, and response shapes unchanged.
- Reserved future `1.0.0` for a stabilization pass that includes source/compliance review and an intentional release process.

## v1.9.0

- Added MŠVVaM `Register škôl a školských zariadení` as aggregate school facility count data, not an institution-level school directory.
- Added offline `scripts/import_school_facility_counts.py` for the confirmed local CSV and retained the 2025-09-15 source CSV under `data/raw/`.
- Added `data/school_facility_counts.json` with 1,227 aggregate rows and 7,026 total organizational units; all rows link to local region and district codes.
- Added `GET /v1/school-facility-counts` and `GET /v1/school-facility-counts/stats` endpoints.
- Intentionally did not add `/v1/schools` or per-school lookup routes because the confirmed source CSV contains aggregate rows only.
- Kept privacy guardrails: no school names, addresses, staff, directors, pupils, personal emails, or phone numbers are exposed.

## v1.8.0

- Added `data/vehicle_registration_codes.json` with 93 legacy two-letter district abbreviations from Slov-Lex legal text for vehicle registration numbers.
- Added `GET /v1/vehicle-registration-codes`, `GET /v1/vehicle-registration-codes/{code}`, and `GET /v1/vehicle-registration-codes/search` endpoints.
- Linked 84 records to local district codes and all 93 records to local region codes; aggregate Bratislava and Košice abbreviations intentionally keep `districtCode: null`.
- Added validation, referential integrity checks, API tests, dataset tests, and smoke-test coverage.
- Kept wording conservative: this is historical/reference data only, not a full plate lookup, current vehicle lookup, owner lookup, or proof of current plate-to-district accuracy.

## v1.7.1

- Located and retained the official telecom regulator phone-area workbook source (`30.xls`) and converted its `List1` sheet to CSV for reproducible offline imports.
- Replaced the 5-row phone-area seed with 2,922 imported municipality-to-primary-area records.
- Linked 2,919 imported phone-area rows to local municipality, district, and region codes; retained 3 unmatched source rows with null local geography links.
- Updated phone-area source metadata, docs, validation expectations, and tests while keeping licence wording conservative.
- Kept runtime API behavior local/static with no upstream route calls and no new endpoint domains.

## v1.7.0

- Added seed-backed `data/phone_areas.json` with local municipality, district, and region links for initial phone-area lookup coverage.
- Added offline `scripts/import_phone_areas.py` support for local CSV/JSON/XLSX source files.
- Added `GET /v1/phone-areas`, `GET /v1/phone-areas/{code}`, and `GET /v1/phone-areas/search` endpoints.
- Added phone-area dataset validation, referential integrity checks, smoke tests, and API/import tests.
- Kept licence and source wording conservative pending retained telecom regulator workbook evidence.

## v1.6.0

- Added explicit source-compliance metadata to `data/sources.json`, including licence status, redistribution status, terms URL, attribution, risk level, and next action.
- Added `docs/source-compliance.md` with a dataset-by-dataset compliance matrix.
- Added retained-evidence and source-owner question docs under `docs/research/`.
- Updated validation to warn, not fail, for pending or high-risk source-compliance entries.
- Kept runtime behavior unchanged: no new endpoints, no new datasets, and no upstream calls from API routes.

## v1.5.0

- Expanded `data/banks.json` from the NBS domestic payment-system identification-code directory snapshot effective `2026-05-18`.
- Added the offline `scripts/import_banks.py` importer with dry-run/write modes, CSV/JSON support, and active-party marker normalization.
- Hardened bank dataset validation for BIC/SWIFT, active-party fields, country codes, and duplicate identifiers.
- Kept IBAN validation and bank-code resolution fully local with no runtime upstream calls.
- Kept source/licence wording conservative: `Source/licence verification pending.`

## v1.4.0

- Backfilled PSC `districtCode` from `municipalityCode` using verified local municipality district mappings.
- Verified PSC `districtCode` coverage is 100% for the current local PSC records, with 0 unresolved municipality codes and 0 region conflicts.
- Kept PSC source as PortalVS classifier 42 and did not infer districtCode values from names or PSC patterns.
- Kept PortalVS licence/reuse wording conservative and added no new endpoints.

## v1.3.0

- Populated municipality district mappings from PortalVS classifier 9 (`Obce`) for the checked-in runtime dataset.
- Kept municipality codes stable and validated municipality region alignment against the local districts dataset.
- Kept PSC `districtCode` coverage unchanged for the v1.4.0 backfill milestone.
- No new endpoints or response-envelope changes were introduced.

## v1.2.0

- Expanded the district dataset to the verified 79 Slovak districts imported from PortalVS classifier 10.
- Updated district source, coverage, and validation metadata to reflect the complete district dataset.
- Kept PSC districtCode coverage unchanged.
- No API behavior changes were introduced.

## v1.1.0

- Improved the dataset source registry and aligned it with current coverage and verification status.
- Added and updated source verification documentation for PSC, company, bank, district, holiday, and geography datasets.
- Clarified licence and redistribution statuses without changing API behavior.
- Added a verification backlog for unresolved source tasks.
- No API behavior changes were introduced.

## v1.0.1

- Fixed post-release version and status references in the app metadata and docs.
- Aligned the README and API status docs with the shipped v1.0.0 stable seed-backed release.
- Verified the public smoke-test expectations against the deployed surface.
- No API behavior changes were introduced.
- No new endpoints were added.

## v1.0.0-rc.6

- Finalized release verification and aligned endpoint status documentation with the shipped local data model.
- Expanded smoke-test coverage for the documented public surface and confirmed the seed-backed company lookup.
- Kept the release feature set unchanged and added no new public endpoints.
- Bumped the application version to `v1.0.0-rc.6`.

## v1.0.0-rc.5

- Added a small checked-in company seed dataset and activated local company lookups for known IČOs.
- Updated the smoke test and dataset/docs to reflect seed-backed company coverage.
- Bumped the application version to `v1.0.0-rc.5`.

## v1.0.0-rc.4

- Added `docs/api-status.md`, `docs/known-limitations.md`, and the RPO verification follow-up notes.
- Added the public smoke-test script and the data source verification issue template.
- Tightened the README into stable vs experimental endpoint sections and refreshed public-readiness guidance.
- Bumped the application version to `v1.0.0-rc.4`.
- No new public endpoints were added.

## v1.0.0-rc.3

- Added an RPO licence verification note and kept the company dataset withheld because official redistribution terms remain unverified.
- Hardened company dataset validation against forbidden personal/stakeholder fields.
- Kept the company lookup endpoint fail-closed with `503 DATASET_UNAVAILABLE` until a local dataset is approved.
- Bumped the application version to `v1.0.0-rc.3`.

## v1.0.0-rc.2

- Added a local company lookup service with canonical `/v1/companies/{ico}` and alias `/v1/ico/{ico}` routes.
- Added IČO normalization/validation and offline company dataset validation helpers.
- Kept company data local/offline only with `503 DATASET_UNAVAILABLE` when the dataset is absent.
- Kept personal, stakeholder, and statutory-body fields out of the public response shape.
- Updated the docs to keep the runtime scope offline-only and honest about partial PSC coverage.
- Clarified that source/licence verification is still pending for datasets that need it.
- Bumped the application version to `v1.0.0-rc.2`.

## v1.0.0-rc.1

- Added IČO/company research notes under `docs/research/ico-sources.md`.
- Documented the proposed normalized company schema and offline prototype import flow.
- Added a research-only company source entry to `data/sources.json`.
- Updated the README and source inventory to keep company work prototype-only.
- Bumped the application version to `v1.0.0-rc.1`.
- No public company endpoint was added.

## v0.9.0

- Documented the PSC collection surface, including list, search, and stats endpoints.
- Documented PSC pagination with `limit` and `offset`.
- Clarified that imported PSC data currently has `districtCode: null` and that source/licence verification is still pending.
- Bumped the application version to `v0.9.0`.

## v0.8.0

- Expanded the checked-in PSC dataset beyond the original tiny seed-only sample.
- Documented the current PSC coverage, importer workflow, and source/licence verification status.
- Updated the PSC documentation to explain repeated source codes and the `matchCount` / `matches` preview shape.
- Bumped the application version to `v0.8.0`.

## v0.7.0

- Expanded `data/municipalities.json` from the Eurostat LAU 2025 workbook.
- Updated `data/regions.json` to the current Eurostat NUTS 2024 code mapping.
- Kept district provenance explicitly unverified and documented the offline-only import/runtime flow.
- Bumped the application version to `v0.7.0`.
- No runtime upstream calls were added.

## v0.6.0

- Added `data/sources.json` as the source registry.
- Added `data/raw/` and `data/generated/` storage conventions for import work.
- Added `scripts/import_geography.py`, `scripts/import_utils.py`, and `scripts/fetch_source.py` for offline import and optional source fetching.
- Added `docs/import-pipeline.md` to document the offline raw-to-generated-to-runtime flow.
- Added importer tests for dry-run, write, validation, and referential checks.
- No new public endpoints were added.

## v0.5.0

- Added `docs/data-sources.md` with the current dataset inventory, coverage notes, and provenance placeholders.
- Added `docs/dataset-format.md` with the local JSON file shapes and shared metadata conventions.
- Updated the README with dataset tooling guidance.
- No new public endpoints were added in this release.

## v0.2.0

- Added `GET /v1/banks` and `GET /v1/banks/{code}` from a static Slovak bank seed dataset.
- Added `GET /v1/iban/validate/{iban}` for local Slovak IBAN validation and bank resolution.
- Documented the new endpoints and dataset limitations.

## v0.4.0

- Added PSC geography code fields and optional geography expansion.
- Added `GET /v1/psc/{psc}?include=geography` for nested local geography objects.
- Linked PSC seed records to the local regions, districts, and municipalities datasets where available.
- Updated tests and docs for PSC geography integration.

## v0.3.0

- Added `GET /v1/regions` and `GET /v1/regions/{code}`.
- Added `GET /v1/districts` and `GET /v1/districts/{code}`, including `regionCode` filtering.
- Added `GET /v1/municipalities` and `GET /v1/municipalities/{code}`, including `regionCode` and `districtCode` filtering.
- Added static geography datasets with honest seed/full coverage notes.

## v0.2.0

- Added `GET /v1/banks` and `GET /v1/banks/{code}` from a static Slovak bank seed dataset.
- Added `GET /v1/iban/validate/{iban}` for local Slovak IBAN validation and bank resolution.
- Documented the new endpoints and dataset limitations.

## v0.1.1

- Fixed README deployment URLs and markdown formatting.
- Added consistent enveloped API error responses.
- Added stable dataset freshness metadata for holidays and PSC.
- Added `Cache-Control` headers for static dataset endpoints.

## v0.1.0

- Added `GET /v1/health` for basic service checks.
- Added `GET /v1/holidays/2026` from a static holiday dataset.
- Added `GET /v1/psc/81101` and a small static PSC seed dataset.
- Added Swagger docs at `/docs` and OpenAPI at `/openapi.json`.
- Enabled global CORS for browser clients.
- Added tests and CI for local and GitHub Actions verification.
