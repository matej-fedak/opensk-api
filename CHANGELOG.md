# Changelog

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
