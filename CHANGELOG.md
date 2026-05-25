# Changelog

## v0.2.0

- Added `GET /v1/banks` and `GET /v1/banks/{code}` from a static Slovak bank seed dataset.
- Added `GET /v1/iban/validate/{iban}` for local Slovak IBAN validation and bank resolution.
- Documented the new endpoints and dataset limitations.

## Unreleased

- No additional public data endpoints planned.

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
