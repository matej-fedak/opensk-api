# 1.0 Readiness Audit

Audit date: 2026-09-18

Application version prepared by this milestone: `0.13.0`

## Readiness Conclusion

OpenSK API is not ready to become `1.0.0` today. The API behavior is close to a stable candidate, but source/licence redistribution evidence and final operational release gates are not yet strong enough for a truthful stable release.

The largest blockers are not new endpoints or data modeling work. They are source/licence decisions, scope decisions for partial or seed-backed datasets, and release operations.

## Public API Inventory

This inventory is generated from the FastAPI/OpenAPI route surface. It has 26 GET operations total: root plus 25 `/v1` operations.

| Method | Path | Purpose | Domain | Response shape | Stability status | Coverage | Source status | Known limitations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GET | `/` | Project metadata | meta | envelope object | candidate stable | service metadata | local | Project SemVer is separate from API version. |
| GET | `/v1/health` | Health check | health | envelope object | candidate stable | service metadata | local | No deep dependency checks. |
| GET | `/v1/iban/validate/{iban}` | Validate IBAN and resolve Slovak bank when possible | IBAN/banks | envelope object | candidate stable | validation endpoint | local bank data | Not a bank-account existence check. |
| GET | `/v1/regions` | List regions | geography | envelope array | candidate stable | complete | Eurostat terms tracked | Redistribution wording still needs retained evidence. |
| GET | `/v1/regions/{code}` | Region lookup | geography | envelope object | candidate stable | complete | Eurostat terms tracked | Same as regions source. |
| GET | `/v1/districts` | List districts, optional region filter | geography | envelope array | candidate stable if source cleared | complete imported | PortalVS pending/restricted | Redistribution uncertainty. |
| GET | `/v1/districts/{code}` | District lookup | geography | envelope object | candidate stable if source cleared | complete imported | PortalVS pending/restricted | Redistribution uncertainty. |
| GET | `/v1/municipalities` | List municipalities, optional region/district filters | geography | envelope array | candidate stable if source cleared | complete imported | PortalVS pending/restricted | Redistribution uncertainty; special-purpose rows excluded. |
| GET | `/v1/municipalities/{code}` | Municipality lookup | geography | envelope object | candidate stable if source cleared | complete imported | PortalVS pending/restricted | Redistribution uncertainty. |
| GET | `/v1/psc` | List PSC records | PSC | paginated envelope object | 1.0 blocker until source/scope decision | partial imported | PortalVS high risk | Not national coverage. |
| GET | `/v1/psc/{psc}` | PSC lookup | PSC | envelope object | 1.0 blocker until source/scope decision | partial imported | PortalVS high risk | Unknown valid PSC may return 404 due to partial coverage. |
| GET | `/v1/psc/search` | PSC search | PSC | paginated envelope object | 1.0 blocker until source/scope decision | partial imported | PortalVS high risk | Search only covers local partial dataset. |
| GET | `/v1/psc/stats` | PSC stats | PSC | envelope object | 1.0 blocker until source/scope decision | partial imported | PortalVS high risk | Stats describe local dataset only. |
| GET | `/v1/banks` | List bank codes | banks | envelope array | candidate stable if source cleared | complete imported | NBS pending | Includes inactive rows; foreign BIC rows excluded. |
| GET | `/v1/banks/{code}` | Bank lookup | banks | envelope object | candidate stable if source cleared | complete imported | NBS pending | Not an account validation endpoint. |
| GET | `/v1/holidays/{year}` | Holiday calendar by year | holidays | envelope array | candidate stable with explicit seed years | partial curated seed | NBS/legal act medium risk | Only checked-in years are available. |
| GET | `/v1/companies/{ico}` | Company lookup | companies | envelope object | scope decision required | seed-backed | source/licence/privacy pending | Not full RPO coverage. |
| GET | `/v1/ico/{ico}` | Company lookup alias | companies | envelope object | scope decision required | seed-backed | source/licence/privacy pending | Alias permanence should be decided before 1.0. |
| GET | `/v1/phone-areas` | List phone-area rows | phone areas | paginated envelope object | candidate stable if source cleared | complete imported | licence pending | 3 rows lack local municipality links. |
| GET | `/v1/phone-areas/{code}` | Phone-area lookup | phone areas | envelope object with items | candidate stable if source cleared | complete imported | licence pending | Same unmatched-row limitation. |
| GET | `/v1/phone-areas/search` | Phone-area search | phone areas | paginated envelope object | candidate stable if source cleared | complete imported | licence pending | Searches local dataset only. |
| GET | `/v1/vehicle-registration-codes` | List legacy vehicle registration codes | vehicle registration | paginated envelope object | candidate stable if source cleared | historical/reference | Slov-Lex pending | Not current plate lookup. |
| GET | `/v1/vehicle-registration-codes/{code}` | Legacy code lookup | vehicle registration | envelope object | candidate stable if source cleared | historical/reference | Slov-Lex pending | Does not decode full plates or identify vehicles/owners. |
| GET | `/v1/vehicle-registration-codes/search` | Legacy code search | vehicle registration | paginated envelope object | candidate stable if source cleared | historical/reference | Slov-Lex pending | Same historical limitation. |
| GET | `/v1/school-facility-counts` | List aggregate school facility counts | school aggregates | paginated envelope object | candidate stable | aggregate imported | MŠVVaM CC BY listed | Not a school directory. |
| GET | `/v1/school-facility-counts/stats` | Aggregate school facility stats | school aggregates | envelope object | candidate stable | aggregate imported | MŠVVaM CC BY listed | No per-school records. |

## Dataset Readiness Matrix

| Dataset | Production file | Records | Coverage classification | Source freshness / last updated | Licence and redistribution status | Import reproducibility | Referential integrity | Remaining risk | 1.0 readiness |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- |
| Regions | `data/regions.json` | 8 | complete | checked 2026-05-27 | Eurostat reuse terms identified; exact retained wording pending | static/verified local data | valid | medium source evidence risk | candidate if evidence retained |
| Districts | `data/districts.json` | 79 | complete imported | checked 2026-07-20 | PortalVS pending/restricted | importer exists for geography data | valid | high legal/source risk | blocker until source strategy resolved |
| Municipalities | `data/municipalities.json` | 2,927 | complete imported | checked 2026-09-07 | PortalVS pending/restricted | importer exists for geography data | valid | high legal/source risk | blocker until source strategy resolved |
| PSC | `data/psc.json` | 1,420 PSC records; 3,101 matches | partial imported | checked 2026-09-07 | PortalVS pending/restricted; risk high | importer/backfill tooling exists | valid for local rows | high legal/source and coverage risk | blocker unless excluded or clearly scoped |
| Banks | `data/banks.json` | 30 | complete imported | NBS directory v225 effective 2026-05-18 | licence/redistribution pending | importer exists | valid | medium source/licence risk | candidate after evidence retained |
| Holidays | `data/holidays.json` | 45 holiday rows | partial curated seed | checked 2026-05-25 | NBS disclaimer noted; exact evidence pending | manual/curated | not geography-linked | medium evidence risk | candidate if seed scope explicit |
| Companies | `data/companies.json` | 4 | seed-backed | checked 2026-06-03 | broader RPO/source/privacy pending | manual seed | not geography-linked | scope and privacy expansion risk | blocker until scope decision |
| Phone areas | `data/phone_areas.json` | 2,922 | complete imported | checked 2026-09-15 | licence/redistribution pending | importer and raw workbook retained | 2,919/2,922 linked | medium source/licence risk; 3 unmatched rows | candidate after source evidence or explicit warning |
| Vehicle registration codes | `data/vehicle_registration_codes.json` | 93 | historical/reference | checked 2026-09-15 | Slov-Lex reuse pending | source text retained in docs | 84 district links; 93 region links | medium source/licence risk | candidate if historical scope explicit and source cleared |
| School facility counts | `data/school_facility_counts.json` | 1,227 | aggregate-only imported | validity 2025-09-15; checked 2026-09-15 | Creative Commons BY listed; exact version/wording pending | importer and raw CSV retained | 1,227/1,227 linked | medium attribution-version risk | candidate after attribution wording retained |

## Source And Licence Readiness

| Source group | Evidence quality | Unresolved questions | 1.0 decision |
| --- | --- | --- | --- |
| PortalVS classifiers 9, 10, 42 | source identified, low legal confidence | caching, transformation, redistribution, commercial use, attribution | must resolve or exclude affected endpoints |
| RPO/company sources | seed pages identified, RPO expansion not cleared | redistribution, privacy, natural-person entrepreneurs, role-holder fields | must choose seed-only scope or defer |
| NBS bank directory | official source identified, medium confidence | exact terms, transformation, redistribution, commercial use | should resolve before 1.0 |
| NBS holidays | source and legal act identified, medium confidence | exact disclaimer and curated JSON permission | should resolve before 1.0 |
| Telecom regulator workbook | source and raw file retained, medium confidence | reuse and redistribution terms | should resolve before 1.0 |
| Slov-Lex legal text | official legal text identified, medium confidence | reuse/transformation/redistribution terms | should resolve before 1.0 |
| MŠVVaM school aggregates | official source page lists CC BY, medium confidence | exact CC BY version and attribution wording | should resolve before 1.0 |
| Eurostat LAU | official source identified, medium confidence | exact workbook reuse notice | should resolve before 1.0 |

## Breaking Change Audit

| Issue | Decision | Reason |
| --- | --- | --- |
| Direct-array list responses for regions, districts, municipalities, banks, and holidays differ from paginated wrappers | B: preserve intentionally unless changed before 1.0 | Existing behavior is simple and tested; changing after 1.0 would be breaking, so final decision must be made before release. |
| `/v1/ico/{ico}` duplicates `/v1/companies/{ico}` | A or B before 1.0 | Decide whether it is a permanent alias. If kept, document as stable. |
| PSC endpoint exposes partial dataset with lookup-like route | A before 1.0 | Must decide whether partial PSC is in 1.0 scope and document 404 semantics clearly. |
| `metadata.version` is `v1` while project version is `0.x` | B preserve intentionally | This is already documented as API namespace/contract marker. |
| School facility endpoint name is aggregate-specific instead of `/schools` | B preserve intentionally | Correctly avoids implying an institution-level directory. |
| Vehicle registration code endpoint does not decode full plates | B preserve intentionally | Historical/reference limitation is documented and safer than overclaiming. |

## Must Fix Before 1.0

See `docs/release-readiness.md` for the canonical blocker table. In short: resolve PortalVS/PSC redistribution risk or exclude those endpoints, decide company scope, retain exact source/licence evidence, require CI gates, and verify production deployment from final `main`.

## Should Fix Before 1.0

Resolve non-PortalVS evidence gaps, decide response-shape and alias permanence, clarify partial dataset scope, and document operational ownership.

## Acceptable Post-1.0 Work

Broader company/RPO imports, national PSC expansion, scheduled refresh automation, additional endpoint domains, and a future `/v2` cleanup can wait if the 1.0 scope is narrow and honest.

## Intentionally Out Of Scope

- New public dataset domains.
- `/v1/schools` or institution-level school records.
- Current vehicle plate decoding, vehicle lookup, or owner lookup.
- Live upstream API proxying at request time.
- Databases, Redis, queues, or other runtime infrastructure.
