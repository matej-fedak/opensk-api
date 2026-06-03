# API Status

The runtime serves local JSON only and does not call upstream sources during requests.

## Stable

| Endpoint | Status | Notes |
| --- | --- | --- |
| `GET /` | stable | Project info |
| `GET /v1/health` | stable | Health check |
| `GET /v1/banks` | stable | Local bank list |
| `GET /v1/banks/{code}` | stable | Local bank lookup |
| `GET /v1/iban/validate/{iban}` | stable | Local IBAN validation |
| `GET /v1/holidays/{year}` | stable | Local holiday dataset |
| `GET /v1/regions` | stable | Local regions dataset |
| `GET /v1/regions/{code}` | stable | Local region lookup |
| `GET /v1/districts` | stable | Local districts dataset |
| `GET /v1/districts/{code}` | stable | Local district lookup |
| `GET /v1/municipalities` | stable | Local municipalities dataset |
| `GET /v1/municipalities/{code}` | stable | Local municipality lookup |
| `GET /v1/psc` | stable | Local PSC dataset |
| `GET /v1/psc/search` | stable | Local PSC search |
| `GET /v1/psc/stats` | stable | Local PSC stats |
| `GET /v1/psc/{psc}` | stable | Local PSC lookup |

## Experimental

| Endpoint | Status | Notes |
| --- | --- | --- |
| `GET /v1/companies/{ico}` | experimental / dataset pending | Local company lookup, 503 until a dataset is approved |
| `GET /v1/ico/{ico}` | experimental / dataset pending | Alias for the local company lookup |

## Notes

- No endpoint fetches live upstream data at request time.
- Company lookup remains dataset-pending until licence and privacy follow-up are complete.
