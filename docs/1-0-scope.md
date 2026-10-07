# Candidate 1.0 Scope

Date: 2026-10-07

This document freezes the intended first stable `1.0.0` scope candidate. It does not release `1.0.0`; it defines what must be stabilized or excluded before that release.

## Included In 1.0

These domains are intended to receive a stable compatibility commitment if the listed source evidence is retained before release:

| Domain | Routes | Scope decision | Required pre-1.0 work |
| --- | --- | --- | --- |
| Project metadata and health | `/`, `/v1/health` | Include | Final deployment verification. |
| IBAN validation | `/v1/iban/validate/{iban}` | Include | Keep local validation semantics documented. |
| Regions | `/v1/regions`, `/v1/regions/{code}` | Include after evidence | Retain exact Eurostat reuse/attribution evidence. |
| Banks | `/v1/banks`, `/v1/banks/{code}` | Include after evidence | Retain exact NBS directory reuse/attribution evidence. |
| Phone areas | `/v1/phone-areas`, `/v1/phone-areas/{code}`, `/v1/phone-areas/search` | Include after evidence | Verify telecom regulator workbook reuse terms and document 3 unmatched rows. |

## Included With Documented Limitations

These domains may be stable if limitations remain explicit and source rights are acceptable:

| Domain | Routes | Scope decision | Limitation |
| --- | --- | --- | --- |
| Districts | `/v1/districts`, `/v1/districts/{code}` | `INCLUDE_AFTER_COMPLIANCE_FIX` | Complete data, but PortalVS redistribution terms must be resolved. |
| Municipalities | `/v1/municipalities`, `/v1/municipalities/{code}` | `INCLUDE_AFTER_COMPLIANCE_FIX` | Complete runtime dataset, but PortalVS redistribution terms must be resolved. |
| PSC | `/v1/psc`, `/v1/psc/{psc}`, `/v1/psc/search`, `/v1/psc/stats` | `INCLUDE_AFTER_COMPLIANCE_FIX` | Partial coverage and PortalVS classifier 42 rights must be resolved. |
| Public holidays | `/v1/holidays/{year}` | Include as limited seed | Only checked-in years are stable; exact source evidence must be retained. |
| Company/IČO | `/v1/companies/{ico}`, `/v1/ico/{ico}` | `INCLUDE_AS_SEED_BACKED` | Compatibility applies to endpoint semantics only, not national RPO completeness. |
| Vehicle registration codes | `/v1/vehicle-registration-codes`, `/v1/vehicle-registration-codes/{code}`, `/v1/vehicle-registration-codes/search` | Include as reference-only after evidence | Historical district abbreviations only; no current plate, vehicle, or owner lookup. |
| School facility counts | `/v1/school-facility-counts`, `/v1/school-facility-counts/stats` | Include as aggregate-only after evidence | Aggregate counts only; no institution-level school directory. |
| Public procurement notices | `/v1/procurement-notices`, `/v1/procurement-notices/{id}`, `/v1/procurement-notices/search`, `/v1/procurement-notices/stats` | Include as TED_PARTIAL after evidence | 100-record TED Slovak-buyer snapshot, not national ÚVO coverage. |

## Excluded From 1.0

These roadmap domains are explicitly outside the first stable release. They do not block `1.0.0` while excluded.

| Domain | Reason |
| --- | --- |
| Broader RPO/company import | Acquisition, provenance, redistribution, and privacy gates remain unresolved. |
| ŽRSR/trade registrations | No approved machine-readable non-scraping source with reuse rights and privacy strategy. |
| VAT/DPH endpoint | Official source verified, but no reliable natural/legal subject discriminator. |
| Streets/Register adries | No approved anonymous reusable street distribution; address-point privacy risk. |
| Healthcare facilities/providers | No approved record-level source with reuse rights and deterministic facility-only privacy filtering. |
| Institution-level schools/universities | RIS/CVTI candidates lack reuse, acquisition, identifier, coverage, and privacy gates. |
| Court decisions | Not researched or implemented in this repository. |
| National statistics endpoints | Not implemented; future source-discovery candidate only. |
| Current vehicle plate decoding | Deliberately excluded; only historical district abbreviations exist. |

## Experimental / Pre-1.0 If Compliance Is Not Fixed

If PortalVS source rights are not resolved before final `1.0.0`, these routes must be excluded from the stable contract or explicitly marked experimental/pre-1.0 before release:

- `/v1/districts`
- `/v1/districts/{code}`
- `/v1/municipalities`
- `/v1/municipalities/{code}`
- `/v1/psc`
- `/v1/psc/{psc}`
- `/v1/psc/search`
- `/v1/psc/stats`

## Must Fix Before 1.0

Only included candidate endpoints create must-fix blockers:

- Resolve or exclude PortalVS-backed districts, municipalities, and PSC.
- Retain exact source licence and attribution evidence for included Yellow datasets.
- Keep company/IČO docs clearly seed-backed with no national coverage implication.
- Preserve explicit limitations for PSC partial coverage, vehicle historical/reference scope, school aggregate-only scope, and TED_PARTIAL procurement scope.
- Decide whether legacy direct-array responses remain part of the stable contract.
- Verify Render deployment from final `main` and run public smoke tests.
- Require validation, referential integrity, test, compile, and diff checks for the final release PR.

## Not 1.0 Blockers While Excluded

- ŽRSR source acquisition.
- VAT privacy strategy.
- Streets source acquisition.
- Healthcare-facility source acquisition.
- Institution-level school source acquisition.
- ÚVO NATIONAL procurement replacement.
- Scheduled ingestion automation.
- PostgreSQL, Redis, background workers, or provider fallback infrastructure.

## Next Milestone

Recommended 0.22.0: `Source compliance remediation for 1.0`.
