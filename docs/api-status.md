# API Status

The runtime serves local JSON only and does not call upstream sources during requests.

v1.0.0 was the first stable seed-backed public API release. This document keeps the deployed surface aligned with the v1.1.0 source/licence verification release.

## Stable

| Endpoint | Status | Notes |
| --- | --- | --- |
| `GET /` | stable | Project info |
| `GET /v1/health` | stable | Health check |
| `GET /v1/iban/validate/{iban}` | stable | Local IBAN validation |
| `GET /v1/regions` | stable | Local regions dataset |
| `GET /v1/regions/{code}` | stable | Local region lookup |
| `GET /v1/municipalities` | stable | Local municipalities dataset |
| `GET /v1/municipalities/{code}` | stable | Local municipality lookup |
| `/docs` | stable | Swagger UI |
| `/openapi.json` | stable | OpenAPI schema |

## Seed-backed

| Endpoint | Status | Notes |
| --- | --- | --- |
| `GET /v1/banks` | seed-backed | Local bank list; reuse allowed with attribution and no modification |
| `GET /v1/banks/{code}` | seed-backed | Local bank lookup; reuse allowed with attribution and no modification |
| `GET /v1/holidays/{year}` | seed-backed | Local holiday dataset; reuse allowed with attribution and no modification |
| `GET /v1/companies/{ico}` | seed-backed | Local company lookup, backed by a small checked-in seed set |
| `GET /v1/ico/{ico}` | seed-backed | Alias for the local company lookup |

## Partial Dataset

| Endpoint | Status | Notes |
| --- | --- | --- |
| `GET /v1/districts` | partial dataset | Local districts dataset with known coverage limits |
| `GET /v1/districts/{code}` | partial dataset | Local district lookup with known coverage limits |
| `GET /v1/psc` | partial dataset | Local PSC dataset; PortalVS source terms are restrictive |
| `GET /v1/psc/search` | partial dataset | Local PSC search; PortalVS source terms are restrictive |
| `GET /v1/psc/stats` | partial dataset | Local PSC stats; PortalVS source terms are restrictive |
| `GET /v1/psc/{psc}` | partial dataset | Local PSC lookup; PortalVS source terms are restrictive |

## Notes

- No endpoint fetches live upstream data at request time.
- Company lookup is backed by a small checked-in seed set; broader RPO coverage still awaits licence and privacy follow-up.
- Districts, banks, holidays, and PSC remain partial or seed-backed datasets rather than exhaustive official registers.
