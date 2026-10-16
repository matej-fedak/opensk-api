# API Status

The runtime serves local JSON only and does not call upstream sources during requests.

OpenSK API is currently pre-1.0. Earlier `v1.x` labels were internal development milestones, not formal stable public releases. The `/v1` route prefix remains the API namespace and does not imply a finalized `1.0.0` contract.

The candidate `1.0.0` scope is defined in `docs/1-0-scope.md`. Some existing routes are intended stable only after source-compliance fixes; research-only domains without routes are excluded from the first stable release.

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
| `GET /v1/banks`, `GET /v1/banks/{code}` | Bank-code list and lookup | complete domestic v226 snapshot, effective 2026-10-08 | Downloaded 2026-10-15T16:23:00Z; direct NBS attribution/version/effective/download/hash metadata. NBS terms, not MIT data licensing. |
| `GET /v1/holidays/{year}` | Holiday calendar | partial curated seed | Years outside the seed return 404. |
| `GET /v1/companies/{ico}`, `GET /v1/ico/{ico}` | Company lookup and IČO alias | seed-backed | Small local seed only, not full RPO coverage; 0.14.0 did not approve RPO production import. |
| `GET /v1/vat/{ico}` | VAT registration lookup | not implemented | 0.15.0 verified the official Finančná správa ZIP/XML source but blocked production import on privacy grounds. |
| `GET /v1/trades/{ico}` | Trade registration lookup | not implemented | 0.16.0 found no safe official machine-readable ŽRSR source and did not add a public endpoint. |
| `GET /v1/streets` | Street list/search | not implemented | 0.17.0 researched Register adries but did not approve a production source or endpoint. |
| `GET /v1/healthcare-facilities` | Healthcare facility/provider lookup | not implemented | 0.18.0 researched NCZI NR PZS and e-VUC but did not approve a production source or endpoint. |
| `GET /v1/schools` | Institution-level school lookup | not implemented | 0.20.0 researched MŠVVaM/RIS/CVTI candidates but did not approve production import or an endpoint. |
| `GET /v1/court-decisions` | Court-decision list/search/detail | not implemented | 0.22.0 verified a Ministry OpenAPI decision endpoint, but reuse/redistribution and privacy gates block production data. |
| `GET /v1/phone-areas`, `GET /v1/phone-areas/{code}`, `GET /v1/phone-areas/search` | Phone-area list, lookup, and search | complete imported; 3 unmatched local geography links | Telecom regulator reuse verification pending. |
| `GET /v1/vehicle-registration-codes`, `GET /v1/vehicle-registration-codes/{code}`, `GET /v1/vehicle-registration-codes/search` | Legacy district-code reference | historical/reference | Not current plate lookup, full plate decoding, vehicle lookup, or owner lookup. |
| `GET /v1/school-facility-counts`, `GET /v1/school-facility-counts/stats` | Aggregate school facility counts and totals | aggregate imported | Not a school directory; no `/v1/schools`. |
| `GET /v1/procurement-notices`, `GET /v1/procurement-notices/{id}`, `GET /v1/procurement-notices/search`, `GET /v1/procurement-notices/stats` | Public procurement notice list, lookup, search, and stats | partial imported | 100-record TED_PARTIAL snapshot only; not the complete ÚVO national register. |
| `GET /v1/sources`, `GET /v1/sources/{id}` | Curated public source/licence provenance catalogue | 20 registered domains | Typed public projection; internal maintainer fields excluded; elections stays research-only pending rights; exchangeRates and euFunds are production (euFunds partial, verified catalogue CC BY, version not separately identified). |
| `GET /v1/business-days/check`, `GET /v1/business-days/add`, `GET /v1/business-days/between` | Slovak business-day check, arithmetic, and counting | supported years 2024-2026 | Derived from the local holiday dataset; strict `UNSUPPORTED_YEAR` error outside coverage. |
| `GET /v1/exchange-rates/latest`, `GET /v1/exchange-rates/{date}` | ECB EUR reference rates (latest in snapshot; exact publication date) | complete (full ECB history 1999-01-04 onwards) | Decimal-string rates; exact dates only, 404 with no fallback; `?currency=` filter; informational use only, not live/tradable prices. |
| `GET /v1/eu-funds/projects`, `GET /v1/eu-funds/projects/{projectCode}` | ITMS21+ project-reference list/code lookup | partial, reviewed legal-entity projects only; 2021–2027 | 4,561 public projects from 4,574 acquired; titles/unsafe projects entirely omitted; manual 2026-10-15 snapshot, not all Slovak funds. MIRRI / generic CC BY; OpenSK transformed/minimized. Contract: `docs/eu-funds.md`. |
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

## 1.0 Scope Status

| Route/domain | Scope status | Requirement before 1.0 |
| --- | --- | --- |
| `/`, `/v1/health`, `/v1/iban/validate/{iban}` | stable candidate | Final deployment verification. |
| Regions, banks, phone areas | stable candidate after evidence | Retain exact source/reuse evidence. |
| Districts, municipalities, PSC | `INCLUDE_AFTER_COMPLIANCE_FIX` | Resolve PortalVS reuse/redistribution/commercial-use terms or exclude from stable contract. |
| Holidays, companies/IČO, vehicle registration codes, school facility counts, procurement notices | limited stable candidate | Keep limitations explicit and retain source evidence. |
| VAT, ŽRSR, streets, healthcare facilities, institution-level schools, court decisions | excluded from 1.0 | Not blockers while excluded. |

## Notes

- 0.23.10 rematerializes **districts + municipalities only** from a fresh 2026-10-16 successor county/town acquisition. 79 / 2,927 records, all IDs/relationships preserved; only municipality names `504173` and `504742` receive reviewed suffix corrections. PSC bytes/provenance/freshness/grouping stay unchanged and legacy-backed (`NO_GO_SUCCESSOR_PSC`); no street/detail import. Still **39 GET operations**, `/v1`, metadata version `v1`; rights unresolved. Geography `lastUpdated`/Last-Modified is acquisition date, with unchanged static Cache-Control and conditional ETags.
- No endpoint fetches live upstream data at request time.
- 0.23.7 promotes title-free ITMS21+ project references with exactly two routes: **39 GET operations** total, source `euFunds` production/partial/verified. Exact filters: programmeCode, callCode, beneficiaryIco, inImplementation, completed, nuts; default/max limit 50/200. Decimal-string `contractedTotal` does not claim currency or payments. Static caching and standard 400/404 envelopes; excluded and unknown codes are indistinguishable. No ITMS2014+ or rich domains.
- 0.23.2 adds no public elections results route or production dataset. Only the curated research entry `/v1/sources/elections` is added to the catalogue; OpenAPI remains 35 GET operations. See `docs/research/elections-spike.md`.
- 0.23.3 adds no public exchange-rate (or elections) route or production dataset. Only the curated research entry `/v1/sources/exchangeRates` is added; OpenAPI remains 35 GET operations. See `docs/research/exchange-rates-spike.md`.
- 0.23.4 adds `GET /v1/exchange-rates/latest` and `GET /v1/exchange-rates/{date}` backed by the materialized full-history ECB snapshot; OpenAPI is 37 GET operations. `/v1/sources/exchangeRates` is promoted to production; elections remain research-only.
- 0.23.5 adds the application rate limiter (100 requests/60 s/client-IP on `GET /` and `/v1/*`; 429 `RATE_LIMITED` envelope with `Retry-After`; `X-RateLimit-*` headers; `/v1/health` exempt; enabled on Render by default) and daily scheduled public smoke monitoring. No endpoint changes; endpoint availability limits/semantics unchanged. Policy: `docs/rate-limiting-contract.md`.
- 0.23.1 adds deterministic ETag/Last-Modified conditional caching on GET routes (`docs/http-caching.md`); root and error envelopes now report `metadata.lastUpdated: null` when no dataset is involved.
- Endpoint availability does not yet equal a stable `1.0.0` compatibility guarantee; see `docs/versioning.md`.
- Company lookup is backed by a small checked-in seed set; broader RPO coverage still awaits a verified production acquisition method, retained reuse evidence, and privacy approval.
- VAT/DPH lookup is not exposed in 0.15.0 because the official XML has no reliable natural/legal subject marker.
- ŽRSR/trade-register lookup is not exposed in 0.16.0 because only a human-facing search interface was verified.
- Streets/address lookup is not exposed in 0.17.0 because no approved anonymous reproducible source and reuse path was verified.
- Healthcare-facility lookup is not exposed in 0.18.0 because no approved machine-readable non-scraping source with reuse rights and deterministic privacy filtering was verified.
- Public procurement lookup is exposed in 0.19.0 as a 100-record TED_PARTIAL snapshot only. It does not claim ÚVO national coverage and excludes personal/contact/address/winner fields.
- Institution-level school lookup is not exposed in 0.20.0 because the confirmed open-data CSV is aggregate-only and the RIS/CVTI institution-level candidates still lack verified reuse, documented acquisition, stable identifier, coverage, and privacy gates.
- Court-decision lookup is not exposed in 0.22.0 because Ministry OpenAPI output lacks verified local-caching/transformation/redistribution terms and requires a strict metadata-only privacy projection before any production snapshot.
- Municipalities now carry district mappings verified from successor town composite codes and county evidence (classifier 9 `code_su` was the historical import). PortalVS source terms remain restrictive and redistribution verification pending.
- PSC `districtCode` is backfilled from `municipalityCode` using local municipality mappings; no districtCode values are inferred from names or PSC patterns.
- Districts are now complete, but PortalVS source terms remain restrictive.
- Banks refreshed in 0.23.8 to NBS **v226 / effective 2026-10-08**, downloaded 2026-10-15T16:23:00Z. Two names/one BIC changed, still 30 domestic rows. Bank/IBAN metadata directly exposes source/version/effective/download/URLs/hash/attribution/transformation; checksum validation remains OpenSK/ISO, not NBS. Participation derives from CSV `Systém SIPS`, not HTML `Akt. úč.` or general operating status. Still 39 GET operations, standard metadata/version and bank data shapes retained. Audit/rights: `research/nbs-bank-reuse-clarification.md`.
- Holidays and PSC remain partial or seed-backed datasets rather than exhaustive official registers.
- Phone areas are imported from the official telecom regulator Excel workbook, with licence/reuse verification still pending.
- Vehicle registration codes are historical district abbreviations only; the API does not expose `GET /v1/vehicles/{spz}` and does not decode full plates.
- School facility counts are aggregate RIS rows only; the API does not expose `/v1/schools` and does not include per-school, staff, director, pupil, email, or phone data.
- Dataset compliance status, retained evidence, and draft clarification questions are documented in `docs/source-compliance.md` and `docs/research/`.
