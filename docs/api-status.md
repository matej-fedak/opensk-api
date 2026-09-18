# API Status

The runtime serves local JSON only and does not call upstream sources during requests.

OpenSK API is currently pre-1.0. Earlier `v1.x` labels were internal development milestones, not formal stable public releases. The `/v1` route prefix remains the API namespace and does not imply a finalized `1.0.0` contract.

## Public Endpoint Index

| Endpoint | Purpose | Coverage/status | Notes |
| --- | --- | --- | --- |
| `GET /` | Project metadata | service metadata | Distinguishes project SemVer from API namespace `v1`. |
| `GET /v1/health` | Health check | service metadata | Local service response. |
| `GET /v1/iban/validate/{iban}` | IBAN validation | validation endpoint | Uses local bank data only for Slovak bank resolution. |
| `GET /v1/regions`, `GET /v1/regions/{code}` | Region list and lookup | complete | Eurostat source terms tracked. |
| `GET /v1/districts`, `GET /v1/districts/{code}` | District list and lookup | complete imported | PortalVS terms may restrict reuse. |
| `GET /v1/municipalities`, `GET /v1/municipalities/{code}` | Municipality list and lookup | complete imported | PortalVS terms may restrict reuse. |
| `GET /v1/psc`, `GET /v1/psc/{psc}` | PSC list and lookup | partial imported | Local PSC coverage is not national coverage. |
| `GET /v1/psc/search`, `GET /v1/psc/stats` | PSC search and stats | partial imported | Static `/search` and `/stats` routes are intentionally registered before `/{psc}`. |
| `GET /v1/banks`, `GET /v1/banks/{code}` | Bank-code list and lookup | complete imported | NBS source/licence verification pending. |
| `GET /v1/holidays/{year}` | Holiday calendar | partial curated seed | Years outside the seed return 404. |
| `GET /v1/companies/{ico}`, `GET /v1/ico/{ico}` | Company lookup and IČO alias | seed-backed | Small local seed only, not full RPO coverage. |
| `GET /v1/phone-areas`, `GET /v1/phone-areas/{code}`, `GET /v1/phone-areas/search` | Phone-area list, lookup, and search | complete imported; 3 unmatched local geography links | Telecom regulator reuse verification pending. |
| `GET /v1/vehicle-registration-codes`, `GET /v1/vehicle-registration-codes/{code}`, `GET /v1/vehicle-registration-codes/search` | Legacy district-code reference | historical/reference | Not current plate lookup, full plate decoding, vehicle lookup, or owner lookup. |
| `GET /v1/school-facility-counts`, `GET /v1/school-facility-counts/stats` | Aggregate school facility counts and totals | aggregate imported | Not a school directory; no `/v1/schools`. |
| `/docs`, `/openapi.json` | Interactive docs and schema | platform | Useful for parameter-level details. |

## Seed-backed

| Endpoint | Status | Notes |
| --- | --- | --- |
| `GET /v1/holidays/{year}` | seed-backed | Local holiday dataset; reuse allowed with attribution and no modification |
| `GET /v1/companies/{ico}` | seed-backed | Local company lookup, backed by a small checked-in seed set |
| `GET /v1/ico/{ico}` | seed-backed | Alias for the local company lookup |

## Partial Dataset

| Endpoint | Status | Notes |
| --- | --- | --- |
| `GET /v1/psc` | partial dataset | Local PSC dataset; PortalVS source terms are restrictive |
| `GET /v1/psc/search` | partial dataset | Local PSC search; PortalVS source terms are restrictive |
| `GET /v1/psc/stats` | partial dataset | Local PSC stats; PortalVS source terms are restrictive |
| `GET /v1/psc/{psc}` | partial dataset | Local PSC lookup; PortalVS source terms are restrictive |

## Notes

- No endpoint fetches live upstream data at request time.
- Endpoint availability does not yet equal a stable `1.0.0` compatibility guarantee; see `docs/versioning.md`.
- Company lookup is backed by a small checked-in seed set; broader RPO coverage still awaits licence and privacy follow-up.
- Municipalities now carry district mappings from PortalVS classifier 9 after offline import, but PortalVS source terms remain restrictive and redistribution verification is still pending.
- PSC `districtCode` is backfilled from `municipalityCode` using local municipality mappings; no districtCode values are inferred from names or PSC patterns.
- Districts are now complete, but PortalVS source terms remain restrictive.
- Banks are imported from an offline NBS directory snapshot and include inactive rows; source/licence verification remains pending.
- Holidays and PSC remain partial or seed-backed datasets rather than exhaustive official registers.
- Phone areas are imported from the official telecom regulator Excel workbook, with licence/reuse verification still pending.
- Vehicle registration codes are historical district abbreviations only; the API does not expose `GET /v1/vehicles/{spz}` and does not decode full plates.
- School facility counts are aggregate RIS rows only; the API does not expose `/v1/schools` and does not include per-school, staff, director, pupil, email, or phone data.
- Dataset compliance status, retained evidence, and draft clarification questions are documented in `docs/source-compliance.md` and `docs/research/`.
