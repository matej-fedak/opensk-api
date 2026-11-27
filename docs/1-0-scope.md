# Candidate 1.0 Scope

Scope alignment: project **0.23.15**, including all **42 GET operations** in the current candidate contract. This is an inclusion decision, not evidence that release gates are closed.

This document freezes the intended first stable `1.0.0` scope candidate. It does not release `1.0.0`; it defines what must be stabilized or excluded before that release.

## Included In 1.0

These domains are intended to receive a stable compatibility commitment if the listed source evidence is retained before release:

| Domain | Routes | Scope decision | Required pre-1.0 work |
| --- | --- | --- | --- |
| Project metadata and health | `/`, `/v1/health` | Include | Final deployment verification. |
| Source catalogue | `/v1/sources`, `/v1/sources/{id}` | Include | Curated public projection only; catalogue presence is not a data endpoint or reuse grant. Preserve unresolved rights and snapshot freshness. |
| IBAN validation | `/v1/iban/validate/{iban}` | Include | Local format/checksum and Slovak structure validation, not account existence; `no-store`, no validators. Never use real accounts as documentation examples. |
| Business days | `/v1/business-days/check`, `/v1/business-days/add`, `/v1/business-days/between` | Include with bounded calendar | Monday–Friday minus statutory days of rest, verified 2024–2030 only; working state holidays remain business days; not a bank settlement calendar. |
| Exchange rates | `/v1/exchange-rates/latest`, `/v1/exchange-rates/{date}` | Include with ECB conditions | Local full-history EUR reference snapshot, exact decimal strings, informational use only. `latest` is snapshot-latest; exact dates have no fallback; retain attribution/modification notices. |
| Regions | `/v1/regions`, `/v1/regions/{code}` | Include after evidence | Retain exact Eurostat reuse/attribution evidence. |
| Banks | `/v1/banks`, `/v1/banks/{code}` | Include with NBS conditions | Reuse resolved; v226 / effective 2026-10-08 refreshed/audited in 0.23.8. Direct bank/IBAN attribution/version/effective/download metadata; retain NBS conditions and OpenSK-derived-field disclosure. |
| Phone areas | `/v1/phone-areas`, `/v1/phone-areas/{code}`, `/v1/phone-areas/search` | Include with limitations | Telecom regulator reply received 2026-11-02 resolves the requested storage, JSON transformation, API/commercial redistribution and derived-join scope; retain factual attribution/transformation disclosure and the 3 unmatched-row warning. |

## Included With Documented Limitations

These domains may be stable if limitations remain explicit and source rights are acceptable:

| Domain | Routes | Scope decision | Limitation |
| --- | --- | --- | --- |
| Districts | `/v1/districts`, `/v1/districts/{code}` | `INCLUDE_AFTER_COMPLIANCE_FIX` | Complete data, but PortalVS redistribution terms must be resolved. |
| Municipalities | `/v1/municipalities`, `/v1/municipalities/{code}` | `INCLUDE_AFTER_COMPLIANCE_FIX` | Complete runtime dataset, but PortalVS redistribution terms must be resolved. |
| PSC | `/v1/psc`, `/v1/psc/{psc}`, `/v1/psc/search`, `/v1/psc/stats` | `INCLUDE_AFTER_COMPLIANCE_FIX` | Partial coverage and PortalVS classifier 42 rights must be resolved. |
| Public holidays | `/v1/holidays/{year}` | Include as bounded statutory calendar | 112 dates generated offline from Act 241/1993, verified 2024–2030 only; preserve `isStateHoliday`/`isDayOfRest` and date-exact exceptions. NBS corroborates, not the permission basis; future law can change the calendar. |
| Company/IČO | `/v1/companies/{ico}`, `/v1/ico/{ico}` | `INCLUDE_AS_SEED_BACKED` | Compatibility applies to endpoint semantics only, not national RPO completeness. |
| Vehicle registration codes | `/v1/vehicle-registration-codes`, `/v1/vehicle-registration-codes/{code}`, `/v1/vehicle-registration-codes/search` | Include as reference-only after evidence | Historical district abbreviations only; no current plate, vehicle, or owner lookup. |
| School facility counts | `/v1/school-facility-counts`, `/v1/school-facility-counts/stats` | Include as aggregate-only after evidence | Aggregate counts only; no institution-level school directory. |
| Public procurement notices | `/v1/procurement-notices`, `/v1/procurement-notices/{id}`, `/v1/procurement-notices/search`, `/v1/procurement-notices/stats` | Include as TED_PARTIAL after evidence | 100-record TED Slovak-buyer snapshot, not national ÚVO coverage. |
| EU-funds project references | `/v1/eu-funds/projects`, `/v1/eu-funds/projects/{projectCode}` | Include as partial ITMS21+ references | Title-free, positively reviewed legal-entity projects only; 4,561 of 4,574 acquired, whole-project privacy exclusion. Generic catalogue CC BY, no invented version/currency; manual snapshot, no payments/ITMS2014+/rich domains. [Contract](eu-funds.md). |
| Election aggregates | `/v1/elections`, `/v1/elections/{electionId}/results`, `/v1/elections/{electionId}/parties` | Include as selected NRSR2023 historical aggregates | 2,927 native units including foreign Cudzina and 25 national parties; no precinct, municipality-party or person records. Publisher-confirmed CC BY 4.0 with attribution/modification/non-endorsement; manual official downloads only, contextual-inference caveat, no automatic second election. [Contract](elections.md). |

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
| Court decisions | Ministry OpenAPI was researched in 0.22.0, but reuse/redistribution, privacy, published-decision scope, and full-text gates remain unresolved; no endpoint or dataset is added. |
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
- PortalVS's 2026-11-02 redirect is not permission. The [0.23.16 geography reconciliation](research/susr-geography-reconciliation.md) established technical readiness; classifier-specific reuse remains `RIGHTS_CONFIRMATION_PENDING` and the 2026-11-27 escalation awaits a reply. The separate Slovenská pošta PSC request sent 2026-11-05 also awaits a reply. Production provenance remains PortalVS-derived.
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
- Court-decision source/reuse/privacy approval.
- ÚVO NATIONAL procurement replacement.
- Scheduled ingestion automation.
- PostgreSQL, Redis, background workers, or provider fallback infrastructure.

## Next Milestone

The trust surface, ECB rates, ITMS21+ references and selected NRSR2023 production surface are delivered. Next is an appropriately scoped, maintainer-run 5–10 external-developer pilot, not an automatic new dataset or PSC migration. Public promotion and stable release remain gated by source compliance and deployment verification. See [roadmap](roadmap.md), [source compliance](source-compliance.md) and [release readiness](release-readiness.md).
