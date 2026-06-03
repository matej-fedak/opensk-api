# API Status

The runtime serves local JSON only and does not call upstream sources during requests.

## Stable

| Endpoint | Status | Notes |
| --- | --- | --- |
| `GET /` | stable | Project info |
| `GET /v1/health` | stable | Health check |
| `GET /v1/banks` | seed-backed | Local bank list |
| `GET /v1/banks/{code}` | seed-backed | Local bank lookup |
| `GET /v1/iban/validate/{iban}` | stable | Local IBAN validation |
| `GET /v1/holidays/{year}` | seed-backed | Local holiday dataset |
| `GET /v1/regions` | stable | Local regions dataset |
| `GET /v1/regions/{code}` | stable | Local region lookup |
| `GET /v1/districts` | seed-backed | Local districts dataset |
| `GET /v1/districts/{code}` | seed-backed | Local district lookup |
| `GET /v1/municipalities` | stable | Local municipalities dataset |
| `GET /v1/municipalities/{code}` | stable | Local municipality lookup |
| `GET /v1/psc` | partial dataset | Local PSC dataset |
| `GET /v1/psc/search` | partial dataset | Local PSC search |
| `GET /v1/psc/stats` | partial dataset | Local PSC stats |
| `GET /v1/psc/{psc}` | partial dataset | Local PSC lookup |

## Seed-backed

| Endpoint | Status | Notes |
| --- | --- | --- |
| `GET /v1/companies/{ico}` | seed-backed | Local company lookup, backed by a small checked-in seed set |
| `GET /v1/ico/{ico}` | seed-backed | Alias for the local company lookup |

## Notes

- No endpoint fetches live upstream data at request time.
- Company lookup is backed by a small checked-in seed set; broader coverage still awaits licence and privacy follow-up.
