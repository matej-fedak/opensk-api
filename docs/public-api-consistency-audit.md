# Public API Consistency Audit

Audit date: 2026-09-18

Milestone: `0.12.0`

## Authoritative Surface

The authoritative route list comes from the FastAPI OpenAPI schema, not from hand-maintained docs. The current schema exposes 26 GET operations: `GET /` plus 25 `/v1` API operations. `/docs` and `/openapi.json` are platform routes.

## Findings Fixed

- README and API status docs did not present one concise endpoint index matching the actual OpenAPI surface.
- Root metadata exposed project SemVer but did not explicitly expose the API namespace/version as separate fields.
- Smoke tests covered the main domains but did not exercise enough representative detail/search routes or verify the project/API version split.
- Regression tests did not directly guard static `/search` and `/stats` routes against dynamic `/{code}` shadowing.
- OpenAPI tests did not require every public operation to have tags and summaries.

## Behavior Left Unchanged

- `metadata.version` remains `"v1"` and is not tied to application SemVer.
- `/v1` remains the API namespace; no `/v0` or `/v1/schools` route was added.
- Existing list/search pagination defaults and maximums remain unchanged to avoid unnecessary client-visible churn.
- Geography list endpoints still return arrays directly, while collection-style endpoints with larger/filterable result sets return `{ items, count, total, limit, offset }`.
- Seed-backed, partial, historical/reference, and aggregate dataset labels remain conservative.

## Current Pagination Pattern

- PSC, phone areas, vehicle registration codes, and school facility counts support `limit` and `offset`.
- List defaults are `limit=100` and `offset=0` where pagination is implemented.
- Search defaults are narrower where implemented, currently `limit=50` for PSC, phone areas, and vehicle registration code search.
- Existing maximums remain in place: `500` for list-style endpoints and `200` for search-style endpoints.

## Error Contract

- Malformed route/query values return an error envelope with HTTP 400 and `INVALID_FORMAT`.
- Unknown valid resource identifiers return an error envelope with HTTP 404 and `NOT_FOUND`.
- Dataset unavailable errors remain reserved for genuinely unavailable local datasets.

## Local-Only Runtime

Runtime API routes read checked-in local JSON or perform local validation only. Upstream sources are used by offline import/update tooling, not by request handlers.
