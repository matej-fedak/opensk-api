# Research Paper Roadmap Coverage Audit

Audit date: 2026-10-07

Paper basis: `Community API Aggregators Research Report`, May 2026, prepared for the SlovakAPI project.

This audit compares the paper's Section 6.1 source assumptions and Section 6.2 endpoint roadmap with the actual OpenSK API repository and verified 2026 source landscape. It does not rewrite the paper and does not add new runtime features.

## Repository Inventory

Current repository state at 0.21.0:

| Metric | Count | Notes |
| --- | ---: | --- |
| Public GET operations | 30 | Root plus 29 `/v1` GET operations from FastAPI OpenAPI. |
| Runtime production JSON files | 11 | Excludes `data/sources.json`; all runtime routes read local files or perform local validation. |
| Source-registry entries | 16 | Includes production, seed-backed, reference, partial, and research-only entries. |
| Research-only source entries | 5 | VAT, ŽRSR, streets, healthcare facilities, and institution-level schools are not production datasets. |
| Seed-backed source entries | 1 | Companies/IČO is intentionally seed-backed. |
| Partial source entries | 3 | PSC, holidays, and procurement notices have explicit partial/limited scope. |
| Historical/reference source entries | 1 | Vehicle registration codes are legacy district abbreviations only. |

Current public route surface:

- Root/service: `/`, `/v1/health`
- Phase 1/reference: `/v1/psc*`, `/v1/holidays/{year}`, `/v1/regions*`, `/v1/districts*`, `/v1/municipalities*`, `/v1/banks*`
- Phase 2/business-finance: `/v1/companies/{ico}`, `/v1/ico/{ico}`, `/v1/iban/validate/{iban}`
- Phase 3/extended: `/v1/phone-areas*`, `/v1/vehicle-registration-codes*`, `/v1/school-facility-counts*`, `/v1/procurement-notices*`

## Phase Coverage Summary

| Phase | Paper items | Production complete | Production partial / limited | Seed-backed | Reference-only | Research-only blocked | Not implemented |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Phase 1 | 6 | 4 | 2 | 0 | 0 | 0 | 0 |
| Phase 2 | 4 | 1 | 0 | 1 | 0 | 2 | 0 |
| Phase 3 | 6 | 1 | 2 | 0 | 1 | 2 | 0 |

Raw classifications are authoritative; the scores do not imply source compliance is already sufficient for `1.0.0`.

## Section 6.2 Roadmap Matrix

| Paper item | Paper source expectation | Actual source | API status | Dataset status | Coverage | Licence/reuse | Privacy | 1.0 candidate | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PSC | Slovenska posta / SUSR CSV or unofficial APIs | PortalVS classifier 42 plus local municipality backfill | `PRODUCTION_PARTIAL` | `data/psc.json` | Partial, 1,420 PSC keys and 3,101 source matches | Red: PortalVS redistribution unclear | Low personal-data risk | `INCLUDE_AFTER_COMPLIANCE_FIX` | Shipped with different source and reduced scope. |
| Public holidays | Ministry of Interior / SUSR public info | NBS holidays page and Act 241/1993 curated seed | `PRODUCTION_PARTIAL` | `data/holidays.json` | Checked-in years only | Yellow: exact retained terms needed | Low | Include with documented seed years | Shipped with different source and explicit year limits. |
| Regions | SUSR / data.gov.sk open API | Eurostat LAU 2025 correspondence table | `PRODUCTION_COMPLETE` | `data/regions.json` | 8 regions | Yellow: exact Eurostat evidence needed | Low | Include after attribution evidence | Shipped with different source. |
| Districts | SUSR / open API | PortalVS classifier 10 | `PRODUCTION_COMPLETE` | `data/districts.json` | 79 Slovak districts | Red: PortalVS redistribution unclear | Low | `INCLUDE_AFTER_COMPLIANCE_FIX` | Complete data but source rights block 1.0 commitment. |
| Municipalities | SUSR / data.gov.sk CSV/JSON | PortalVS classifier 9 | `PRODUCTION_COMPLETE` | `data/municipalities.json` | 2,927 current regular municipalities | Red: PortalVS redistribution unclear | Low | `INCLUDE_AFTER_COMPLIANCE_FIX` | Complete runtime data; terms remain unresolved. |
| Banks | NBS HTML/PDF | NBS domestic payment-system identification-code directory | `PRODUCTION_COMPLETE` | `data/banks.json` | 30 domestic rows | Yellow: source terms pending | Low | Include after source evidence | Shipped in intended domain. |
| Company / ORSR / ICO | ORSR scraping / registry lookup | Small verified legal-entity seed plus RPO research | `SEED_BACKED` | `data/companies.json` | 4 seed records | Yellow: seed-specific evidence, RPO not approved | Personal role-holder fields excluded | `INCLUDE_AS_SEED_BACKED` | Stable semantics only; no national RPO/ORSR coverage promise. |
| ŽRSR | HTML/JSON public machine-readable access | ŽRSR human-facing search only verified | `RESEARCH_ONLY_BLOCKED` | No production dataset | None | Blocked: no machine-readable reuse grant | Natural-person entrepreneurs risk | Exclude from 1.0 | Paper claim is incorrect for production use. |
| VAT / DPH | XML / JSON download | Financial Administration ZIP/XML verified | `RESEARCH_ONLY_BLOCKED` | Generated tooling only | Source available, not exposed | Source usable; privacy gate blocks production | No natural/legal subject discriminator | Exclude from 1.0 | Source claim partly confirmed, production blocked by privacy. |
| IBAN | NBS HTML/prefix lookup | Local IBAN checksum plus local bank code data | `PRODUCTION_COMPLETE` | No separate dataset beyond banks | Validation endpoint | Depends on bank-code source evidence | Low | Include | Shipped with local validation, not live lookup. |
| Streets | INSPIRE REST/WMS open access | MV Register adries pages, eID/mailbox workflow, unapproved third-party API | `RESEARCH_ONLY_BLOCKED` | No production dataset | None | Blocked: no approved anonymous reusable street distribution | Address-point privacy risk | Exclude from 1.0 | Paper claim not production-verified. |
| Vehicle registration | Public vehicle registration code lists | Slov-Lex legal text, legacy district abbreviations | `REFERENCE_ONLY` | `data/vehicle_registration_codes.json` | Historical/reference, 93 codes | Yellow: Slov-Lex reuse pending | Low; no vehicle/owner data | Include with limitation after evidence | Scope differs: not `/api/vozidla/{spz}` current plate lookup. |
| Phone area codes | RUSR/TUSR PDF/HTML | Telecom regulator workbook | `PRODUCTION_COMPLETE` | `data/phone_areas.json` | 2,922 rows; 3 unmatched local geography links | Yellow: reuse terms pending | Low | Include after source evidence | Shipped with machine-processable workbook. |
| Healthcare facilities | NCZI REST API open | NCZI NR PZS info, aggregate outputs, e-VUC directory/IdZZ docs | `RESEARCH_ONLY_BLOCKED` | No production dataset | None | Blocked: no approved record-level source | Person/contact fields risk | Exclude from 1.0 | Paper NCZI REST/open assumption not verified. |
| Schools and universities | MŠVVaM/CVTI CSV/REST open | Aggregate MŠVVaM CSV plus blocked RIS/CVTI candidates | `PRODUCTION_PARTIAL` | `data/school_facility_counts.json` | Aggregate school-facility counts only | Yellow for aggregate; institution-level blocked | Aggregate is safe; institution-level needs review | Include aggregate only; exclude institution-level | Superseded by aggregate endpoint scope. |
| Public procurement | ÚVO XML/REST open API | TED Search API Slovak-buyer 100-record snapshot | `PRODUCTION_PARTIAL` | `data/procurement_notices.json` | TED_PARTIAL, not national ÚVO | Yellow: exact TED attribution evidence needed | Personal/contact/winner fields excluded | Include with TED_PARTIAL limitation | Shipped with different source and reduced scope. |

## Section 6.1 Source Claims Not Directly Shipped As Roadmap Endpoints

| Paper source | Paper claim | 2026 verification result | Status | Recommendation |
| --- | --- | --- | --- | --- |
| `data.gov.sk` | CKAN-based portal with REST API and broad datasets | Repeated project attempts often returned JavaScript shell or no verified usable distribution in this environment | `PARTIALLY_CONFIRMED` | Continue checking first, but verify publisher and working distribution URL before approval. |
| Statistical Office API / national statistics | JSON-stat/CSV/XML/XLSX, updated twice daily | Not implemented as a runtime source; RPO/API docs were useful for research but not production-approved for company expansion | `UNVERIFIED` for current runtime | Treat as future discovery candidate, not current 1.0 scope. |
| Court decisions | XML, partially open | Not researched/implemented in this repository | `NOT_IMPLEMENTED` | Exclude from 1.0; future domain only after source/licence/privacy review. |
| Apitalks / commercial proxy | Free-to-use Slovak/EU open-data proxy | Not approved as production source | `UNVERIFIED` | Prefer official publisher or retained source-owner terms. |
| LOD Slovakia | Earlier linked-data precedent | Not used by runtime | `UNVERIFIED` | Historical precedent only unless refreshed and licensed. |

## Paper Assumption Accuracy Audit

| Assumption | Category | Project evidence | Effect on recommendation |
| --- | --- | --- | --- |
| Zero-auth, CORS-enabled, JSON-first API is useful | `CONFIRMED` | Current FastAPI API is zero-auth, CORS-enabled, JSON envelope based | Preserve. |
| `data.gov.sk` is a straightforward CKAN/API acquisition route | `PARTIALLY_CONFIRMED` | Portal exists, but project attempts often returned JS shell or no verified distribution | Check it, but do not rely on it without publisher/distribution verification. |
| Financial Administration VAT bulk download exists | `CONFIRMED` | ZIP/XML source verified in 0.15.0 | Keep tooling; production waits for privacy strategy. |
| NCZI REST/open healthcare facility data is available | `INCORRECT_FOR_PRODUCTION_USE` | No approved public record-level bulk/API/export with reuse rights verified | Healthcare excluded from 1.0. |
| MŠVVaM/CVTI schools CSV/REST is open for institution directory | `INCORRECT_FOR_PRODUCTION_USE` | Aggregate CSV verified; institution-level RIS/CVTI candidates lack reuse/acquisition gates | Only aggregate school counts remain in scope. |
| ŽRSR machine-readable public access is available | `INCORRECT_FOR_PRODUCTION_USE` | Human-facing search only verified | Exclude ŽRSR from 1.0. |
| Register adries / INSPIRE street access is open for API redistribution | `INCORRECT_FOR_PRODUCTION_USE` | MV services exist, but no anonymous reusable street snapshot verified | Exclude streets from 1.0. |
| ÚVO XML/REST open API can support procurement endpoint | `OUTDATED` / `UNVERIFIED` | ÚVO national source not verified; TED works for partial scope | Keep TED_PARTIAL only unless ÚVO is verified. |
| ORSR scraping is viable | `INCORRECT_FOR_PRODUCTION_USE` | Project policy rejects scraping unstable HTML for runtime data | Keep company seed/RPO research path, not scraping. |
| Statistical Office API is available | `UNVERIFIED` for runtime | Not used by current production datasets | Future source-discovery candidate only. |

## National Open Data Catalogue Audit

The paper correctly treats the Slovak national open-data catalogue as important infrastructure. OpenSK project evidence shows it is not sufficient by itself for production acquisition.

Project milestones that attempted catalogue use include VAT, ŽRSR, streets, healthcare, schools, and procurement. In several checks, `data.gov.sk` or `data.slovensko.sk` returned a JavaScript application shell or did not expose a verified working distribution in the research environment. Publisher-direct sources were more useful for VAT, school aggregates, procurement via TED, phone areas, banks, and legal/reference data.

OpenSK should continue checking the catalogue for every future dataset, but only as a discovery layer.

Future source-discovery policy:

1. Check `data.gov.sk` / the national catalogue.
2. Verify the publisher and responsible authority.
3. Follow the distribution URL, not just catalogue metadata.
4. Verify that the distribution works anonymously and reproducibly.
5. Verify licence, attribution, transformation, caching, redistribution, and commercial downstream rights.
6. Prefer a publisher-direct machine-readable distribution when equivalent and clearer.
7. Document catalogue failure, stale metadata, or missing distributions when applicable.

Do not create an OpenSK API endpoint for the catalogue itself in the 1.0 scope.

## Source Compliance Classification For Production Datasets

| Colour | Datasets | Meaning |
| --- | --- | --- |
| Green | None yet | No production dataset currently has retained evidence strong enough to remove all 1.0 source caveats. |
| Yellow | regions, banks, holidays, companies seed, phone areas, vehicle registration codes, school facility counts, procurement notices | Production or limited data exists, but exact attribution/reuse evidence needs tightening before stable release. |
| Red | districts, municipalities, PSC | Production data exists, but PortalVS redistribution uncertainty is high enough that these must be resolved before inclusion in 1.0 or excluded. |

Research-only datasets are not 1.0 blockers when explicitly excluded from the stable scope.

## Architecture Recommendation Audit

| Paper recommendation | Current project | Classification | Rationale |
| --- | --- | --- | --- |
| Next.js or Hono | FastAPI | `INTENTIONALLY_DIFFERENT` | Python/FastAPI fits current local-data scripts and OpenAPI generation. |
| Vercel or Cloudflare Workers | Render | `INTENTIONALLY_DIFFERENT` | Render is simpler for FastAPI; public smoke tests verify deployment. |
| PostgreSQL + Redis | Static JSON files | `INTENTIONALLY_DIFFERENT` | Current scale and static datasets do not justify database/cache infrastructure. |
| GitHub Actions ingestion | Offline scripts, manual promotion | `PARTIAL` / `FUTURE` | Safer before source rights are settled. |
| Swagger UI | FastAPI `/docs` | `ADOPTED` | Interactive docs are available. |
| Rate limiting | Not implemented | `FUTURE` | Needed before high-traffic stable/public launch, not for current static MVP. |
| Monitoring | Render health plus smoke script | `PARTIAL` | No public status page yet. |
| MIT licence | MIT app licence | `ADOPTED` | Data licences remain source-specific. |
| Provider fallback | Not used | `NOT_NEEDED_YET` | Most routes use local static snapshots, not live upstream providers. |

## Best-Practices Audit

| Best practice | Status | Evidence / gap |
| --- | --- | --- |
| Zero-auth core API | `DONE` | No API key required. |
| CORS | `DONE` | FastAPI middleware allows browser GETs. |
| OpenAPI / Swagger | `DONE` | `/docs` and `/openapi.json`. |
| GitHub-first workflow | `DONE` | PR-based workflow and issue-ready docs. |
| Semantic versioning | `PARTIAL` | Pre-1.0 project SemVer with `/v1` namespace documented. |
| Consistent response envelope | `PARTIAL` | Envelope is consistent for most routes; some legacy list responses use arrays. |
| Source metadata | `DONE` | `data/sources.json` and metadata in datasets. |
| `lastUpdated` | `DONE` | Runtime metadata includes update dates where applicable. |
| Bilingual structured errors | `DONE` | Error envelopes include English and Slovak messages. |
| Changelog | `DONE` | `CHANGELOG.md`. |
| Health endpoint | `DONE` | `/v1/health`. |
| Caching headers | `NOT_IMPLEMENTED` | Future performance hardening. |
| Rate limiting | `NOT_IMPLEMENTED` | Future abuse protection. |
| Live upstream monitoring/tests | `DEFERRED` | Runtime does not call upstream; source refresh monitoring can come later. |
| Provider fallback | `NOT_APPLICABLE` | Static local runtime removes live upstream fallback need for current scope. |

## Coverage Score

- Phase 1: 4/6 production complete; 2/6 partial or compliance-blocked.
- Phase 2: 1/4 production complete; 1/4 seed-backed; 2/4 research-only blocked.
- Phase 3: 1/6 production complete; 2/6 production partial; 1/6 reference-only; 2/6 research-only blocked.

Production-complete domains: regions, districts, municipalities, banks, IBAN, phone area codes.

Partial/limited domains: PSC, holidays, school facility aggregates, public procurement notices.

Blocked domains: ŽRSR, VAT production exposure, streets, healthcare facilities, institution-level schools.

Research-only domains: VAT, ŽRSR, streets, healthcare facilities, institution-level school directory.

Reference-only domains: legacy vehicle registration district codes.

## Recommended Next Milestone

Recommended 0.22.0: `Source compliance remediation for 1.0`.

Focus on actual 1.0 blockers rather than new domains:

- Resolve PortalVS classifier 9, 10, and 42 redistribution/commercial-use/caching/transformation/attribution terms.
- Retain exact attribution/reuse evidence for Eurostat, NBS, telecom regulator, Slov-Lex, MŠVVaM, and TED.
- Decide whether any unresolved red source must be excluded before final 1.0 freeze.
