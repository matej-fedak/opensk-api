# Changelog

## 0.23.5

- Added the application-level rate limiter planned in 0.23.1: **100 requests per 60 seconds per client IP**, fixed window, for `GET /` and `/v1/*`, with `GET /v1/health` fully exempt. Rejected requests return `429` with the standard OpenSK error envelope (`RATE_LIMITED`), `Retry-After`, `Cache-Control: no-store`, and no ETag/Last-Modified; allowed responses (including 304s) carry `X-RateLimit-Limit`/`X-RateLimit-Remaining`/`X-RateLimit-Reset`, exposed to browsers via CORS `Access-Control-Expose-Headers`. No API keys; `docs/rate-limiting-contract.md` is now the authoritative implementation/policy document (was `RATE_LIMIT_CONTRACT_ONLY`).
- Enablement via `OPENSK_RATE_LIMIT_ENABLED` (`auto` default = enabled under Render's official `RENDER=true`, disabled locally; `true`/`false` for explicit override; on Render itself an env change applies via the deploy/restart Render performs, not live). Client identity is a validated IP: on Render the resolver prefers **`CF-Connecting-IP`** (Cloudflare's edge-set visitor IP, not client-controllable), falling back conservatively to the right-most `X-Forwarded-For` entry only, then a shared fail-closed bucket; off-Render, forwarded/vendor headers are ignored and only the connection peer is used. No project-maintained Cloudflare CIDR list.
- Verified current Render facts (2026-10-12) and recorded evidence: Cloudflare fronts all Render inbound traffic (L3/L4 + obvious L7 floods mitigated at the edge), targeted L7/application abuse is the app's responsibility, Render offers no per-client rate limiting for application traffic, and Render sets `RENDER=true`.
- State is in-memory, process-local, ephemeral (reset each window / on restart); documented review trigger: revisit edge/shared-state limiting only if OpenSK moves to multiple serving processes/instances. No Redis, no new datastore, no new dependencies.
- Added scheduled public smoke monitoring: `.github/workflows/public-smoke.yml` runs `scripts/smoke_test.py` against `https://opensk-api.onrender.com/` daily at 06:17 UTC (plus `workflow_dispatch`) with a bounded ~2-minute `/v1/health` warm-up that distinguishes a waking free-tier instance from a real outage; minimal permissions, non-cancellable concurrency group, no secrets, no external monitoring SaaS. Best-effort daily check — not an uptime SLA.
- Smoke script now identifies itself as `OpenSK-Public-Smoke/<version>` (not a limiter bypass) and, with `--expect-rate-limit` (used by the workflow), asserts the deployed limiter advertises its headers — without ever intentionally exhausting the limit. 429 boundary behavior is proven offline only.
- No data-domain changes; 37 GET operations unchanged; `/v1` and `metadata.version == "v1"` unchanged; outreach states unchanged (PortalVS, NBS, telecom, ŠÚ SR all `SENT_AWAITING_REPLY`; no permission inferred). **Operational guardrails are ready; public promotion is still gated by unresolved PortalVS compliance.**

## 0.23.4

- Promoted the verified 0.23.3 exchange-rate research to production. New routes: `GET /v1/exchange-rates/latest` (newest ECB publication date in the OpenSK snapshot — not a live rate) and `GET /v1/exchange-rates/{date}` (exact publication date only; 404 `RATE_DATE_NOT_FOUND` for weekends/TARGET holidays/out-of-coverage dates, never a fallback). Optional `?currency=` filter: case-insensitive normalization, 400 `INVALID_FORMAT` for malformed codes, 400 `UNSUPPORTED_CURRENCY` for codes never published, 404 `RATE_NOT_AVAILABLE` for historically known-but-absent-on-that-date series (e.g. SKK, suspended RUB). OpenAPI is now 37 GET operations with the typed `exchange-rates` tag and string-typed `rates`.
- New production dataset `data/exchange_rates.json`: full-history ECB eurofxref snapshot (eurofxref-hist.xml, 8,197,952 source bytes, SHA-256 `420f9e07…c0a6f5` recorded in the dataset itself), 7,112 publication dates 1999-01-04→2026-10-12, 221,296 rate rows, 41 currencies, 6,006,060 bytes. Rates are exact decimal strings (`1 EUR = rate units of the foreign currency`); EUR base only; no floats, no arithmetic. ECB attribution, modification disclosure (XML→JSON normalization only, values verbatim), and the "information purposes only / transaction use strongly discouraged" notice are carried in the dataset metadata, response data, route descriptions, and `/v1/sources/exchangeRates`.
- Importer promoted to production tooling: mutually exclusive `--dry-run` / `--write-preview` / `--write-production` modes; production requires the single canonical full-history source and writes only `data/exchange_rates.json`; deterministic output with no local paths or machine metadata; built-in refresh report (added/removed dates, historical rate changes, currency churn, bytes/SHA-256) that **fails on historical rewrites or removed/truncated dates unless `--acknowledge-changes` is given**. Preview stays confined to ignored `data/generated/`.
- Validation extended (`exchange_rates` dataset: EUR base, ECB HTTPS source URL, SHA-256 format, sorted unique ISO dates, latest/earliest/lastUpdated consistency, sorted currency keys, positive decimal-string rates, no floats, weekend observation warning) — 0 errors, 51 warnings, 7,112 records.
- HTTP caching: `/v1/exchange-rates/*` carries `Last-Modified` from `EXCHANGE_RATES_LAST_UPDATED` (`schemas/common.py`, currently `2026-10-12`); latest alias `public, max-age=3600`, exact-date routes `public, max-age=86400`; strong ETag + 304 on `If-None-Match`/`If-Modified-Since`, including query-filtered variants.
- Source catalogue: `exchangeRates` promoted to `production` / coverage `complete` (relative to the imported ECB full-history feed), licence stays `verified`, `lastUpdated` from the snapshot; limitations now state ECB-reference-only, exact-publication-date, informational, historical-currency-availability and manual-refresh-lag semantics. Runtime measured: ~74 ms cold JSON parse, ~96 ms cold service load on top, ~2.3 µs warm lookups, ~34 MiB peak / ~23 MiB retained Python heap — `JSON_CONTINUE` confirmed, no database justified.
- Fixed the stale `elections.notes` tail in `data/sources.json` (clarification sent manually 2026-10-11, reply pending, no permission inferred).
- Elections remain research-only pending ŠÚ SR evidence; PortalVS, NBS, telecom and ŠÚ SR outreach replies are still pending — no reply received during this milestone and no permission inferred from silence. No runtime upstream calls; no scheduled fetching; no tag/release.

## 0.23.3

- Recorded outreach state change: all four licence-clarification packages (PortalVS, NBS banks, telecom regulator, ŠÚ SR elections) were sent manually by the maintainer on 2026-10-11 and are `SENT_AWAITING_REPLY`; documentation and `data/sources.json` nextActions updated without changing any licence/redistribution status — sending a question is not permission.
- PortalVS source resilience: re-verified both legacy `ciselniky.portalvs.sk` (end-of-support 2026-10-31 banner still present) and successor `ciselniky2.portalvs.sk` live; compact transition manifests with SHA-256 retained locally (not committed); verdict `SUCCESSOR_COMPATIBLE_WITH_TRANSFORM_CHANGES` — all three PortalVS-backed datasets rebuildable from the successor API with offline transforms only, no public contract change required. Licence remains pending.
- Exchange-rates spike concluded **`GO_PRODUCTION_NEXT`**: ECB eurofxref feeds verified (1999-01-04 → present; 7,111 publication dates; 221,267 rate rows; full history only 3.48 MiB compact JSON), NBS confirmed as republication-only, ECB reuse permission explicitly written (attribution + modification notice). Added offline, dry-run-first `scripts/import_exchange_rates.py` with strict gesmes/XML/ISO/Decimal validation, numeric cross-feed dedup and 49 synthetic tests.
- Added the research-only `exchangeRates` source entry and curated public projection (19 domains; coverage unknown, licence verified, no production dataset or endpoint). Public route count unchanged (`NO PUBLIC EXCHANGE-RATE ENDPOINT IS ADDED.`); `JSON_CONTINUE`; no runtime upstream calls.
- Business-day finding: ECB publishes on TARGET working days only (zero weekend publications in 27 years; freshness can lag 4 calendar days) — the Slovak business-day utilities must not be reused for ECB publication semantics. No fallback/"previous business day" logic implemented or endorsed.

## 0.23.2

- Completed the Slovak elections data spike for official NR SR 2023 aggregate statistics, with three independent source/licence, schema/data and integration/privacy reviews and an evidence-backed decision: `GO_AFTER_LICENCE_EVIDENCE` (including approved acquisition).
- Verified UTF-8 (not CP1250), comma-delimited/dot-decimal 2023 files, 2,927 election-native units, 2,926 current municipality joins and exact national/party reconciliation; retain foreign-voting unit `599999` separately. Sampled NR SR 2020 and referendum 2023 demonstrate dialect/header/semantic drift.
- Added offline, dry-run-first `scripts/import_elections.py` with strict 2023 headers, deterministic aggregate normalization, optional party/national controls, code-only geography diagnostics and synthetic offline tests. Writes are confined to ignored `data/generated/` previews; no fetcher, official raw files or preview datasets are committed.
- Retained general ŠÚ SR CC BY 4.0 wording and its automated-download prohibition; prepared a fourth Slovak clarification draft, `READY_FOR_USER_TO_SEND`, unsent. No production clearance is inferred from OGP publication or downloadability.
- Added the research-only `elections` source entry and curated public projection (18 domains; coverage unknown, licence pending); existing source entries/results behavior remain unchanged.
- **No public elections results endpoint or production election dataset is added.** No SQLite or runtime upstream calls; `JSON_CONTINUE`. Project version is `0.23.2`; `/v1` and envelope `metadata.version == "v1"` remain unchanged.

## 0.23.1

- Added `GET /v1/sources` and `GET /v1/sources/{id}`: a typed (Pydantic) curated public provenance catalogue covering all 17 registered domains with a documented public/internal field boundary and deterministic status/coverage/licence mapping; unresolved licence states stay unresolved.
- Added Slovak business-day utilities `GET /v1/business-days/check`, `GET /v1/business-days/add`, and `GET /v1/business-days/between` over the local holiday dataset, with supported years derived from the dataset (2024-2026) and strict `UNSUPPORTED_YEAR` errors outside coverage.
- Added deterministic HTTP conditional caching: strong body-hash ETags with `If-None-Match`/304, semantic per-dataset `Last-Modified` with `If-Modified-Since`/304, and a documented Cache-Control policy (static 86400, search 900, meta 3600, health no-store; IBAN responses are now publicly cacheable).
- Made root and error envelopes byte-stable by reporting `metadata.lastUpdated: null` when no dataset is involved (previously a daily-changing `date.today()`); dataset freshness values are unchanged.
- Single-sourced the project SemVer into `version.PROJECT_VERSION`; app, root metadata, tests, and smoke expectations now derive from it.
- Merged the duplicated CI workflows into one `CI` workflow, added Dependabot for pip and GitHub Actions, and added the manual/offline `scripts/check_source_urls.py` source-health checker.
- Added docs: source-catalogue boundary, HTTP caching policy, future rate-limit contract (contract-only; `RATE_LIMIT_CONTRACT_ONLY`), dataset-domain contributor gates, and a bounded ECB exchange-rate source research note recommending a post-elections candidate.
- No new datasets; runtime architecture stays materialized-local JSON with no upstream calls.

## 0.23.0

- Completed a 2026 Q4 source-licence verification and multi-perspective roadmap review; added `docs/research/opensk-research-roadmap-2026-q4.md` as the consolidated research report.
- Directly verified the PortalVS end-of-support banner ("Podpora doterajšieho systému končí 31.10.2026."), the MŠVVaM-operated `ciselniky2.portalvs.sk` successor REST API, and the non-commercial-only portal copyright wording; this keeps districts, municipalities, and PSC compliance-Red and adds a final-snapshot contingency before 2026-10-31.
- Verified NBS website disclaimer wording, telecom workbook "ďalšie spracovanie" statement, Slov-Lex Copyright Act 185/2015 Z. z. § 5 písm. b) legal-text exclusion, Eurostat CC BY 4.0 reuse policy, TED free-reuse/CC0-metadata terms, and the unversioned MŠVVaM "Creative Commons BY" notice.
- Directly verified `volby.statistics.sk/tree.html` as the official ŠÚ SR elections open-data source (OGP government resolution 59/2015) covering EP 2004-2024, NR SR 1994-2023, OSK 2001-2022, and OSO 2002+ down to okrsok granularity, and chose elections as the next bounded data spike.
- Added `docs/research/source-licence-outreach.md` with ready-to-send Slovak outreach drafts for PortalVS, NBS banks, and the telecom regulator, plus evidence-retention actions for the remaining Yellow rows; nothing is sent automatically.
- Added `docs/research/roadmap-council-notes.md` recording consensus/majority/contested/rejected verdicts, including the graph-aware PortalVS removal contingency and rejections of VAT-first, CRZ drop-in, personal-data endpoints, and scraping.
- Added `docs/roadmap.md` as the living strategic roadmap (Now/Next/Watch/Later/Completed).
- No new endpoints, datasets, importers, or runtime behavior changes.
- Updated project version metadata to `0.23.0` while keeping `/v1` and response `metadata.version == "v1"` unchanged.

## 0.22.0

- Researched official Slovak court-decision sources for a future Phase 3 court-decisions API.
- Verified the Ministry RESS/ISU OpenAPI discovery chain, including Swagger config and the OpenAPI document for anonymous-looking `GET /v1/rozhodnutie`, `GET /v1/rozhodnutie/{id}`, and `GET /v1/rozhodnutie/autocomplete` endpoints.
- Documented decision metadata and ECLI fields, while recording privacy-risk fields such as judge/person names, participants, addresses/contact data, snippets/highlights, and document/text fields.
- Chose `Acquisition decision: RESEARCH_AND_TOOLING_ONLY` and `Text decision: NO_PRODUCTION_DATA` because Ministry/court-source reuse, local caching, transformation, redistribution, commercial-use, metadata-only privacy projection, and full-text exclusion are not verified.
- Added a research-only `courtDecisions` source-registry entry; did not add `/v1/court-decisions`, `data/court_decisions.json`, fetch tooling, import tooling, or full-text storage.
- Updated project version metadata to `0.22.0` while keeping `/v1` and response `metadata.version == "v1"` unchanged.

## 0.21.0

- Audited the May 2026 research-paper source assumptions and Phase 1-3 endpoint roadmap against the actual repository and verified source landscape.
- Added `docs/research/paper-roadmap-coverage.md` with paper-vs-repo classifications, data.gov.sk findings, architecture recommendations, best-practices audit, and coverage scores.
- Added `docs/1-0-scope.md` to define the candidate `1.0.0` scope, excluded domains, and actual must-fix blockers.
- Decided that company/IČO lookup is included as `INCLUDE_AS_SEED_BACKED`, while districts, municipalities, and PSC are `INCLUDE_AFTER_COMPLIANCE_FIX` because PortalVS rights remain unresolved.
- Updated release/readiness docs to distinguish included 1.0 blockers from excluded research-only roadmap domains.
- Updated project version metadata to `0.21.0` while keeping `/v1` and response `metadata.version == "v1"` unchanged.

## 0.20.0

- Researched institution-level Slovak school and school-facility directory sources for the Phase 3 schools roadmap item.
- Documented that the confirmed MŠVVaM open-data CSV remains aggregate-only and must stay separate from any future school-directory endpoint.
- Identified official MŠVVaM/CVTI PDF and XLS candidates plus RIS/CRINFO public screens, but blocked production import because licence/reuse, stable documented acquisition, identifier semantics, coverage, and privacy gates are incomplete.
- Added `schoolsDirectory` source-registry metadata as research-only/acquisition-blocked.
- Did not add `/v1/schools`, `/v1/education-institutions`, an importer, or a production dataset.
- Updated project version metadata to `0.20.0` while keeping `/v1` and response `metadata.version == "v1"` unchanged.

## 0.19.0

- Researched Slovak public procurement notice sources for the Phase 3 public-procurement roadmap item.
- Verified no current anonymous machine-readable ÚVO national notice distribution with production-ready terms was found, while TED Search API provides an official anonymous notice subset for `buyer-country = SVK`.
- Added offline TED fetch and import tooling for a bounded latest-notice snapshot with privacy-scoped fields only.
- Added `data/procurement_notices.json` with 100 normalized Slovak-buyer TED notices and explicit `PRODUCTION_IMPORT_APPROVED` / `TED_PARTIAL` metadata.
- Added `procurementNotices` source-registry metadata and local validation for IDs, dates, buyer country, source URLs, duplicates, partial coverage flags, geography links, and privacy-forbidden fields.
- Added `GET /v1/procurement-notices`, `GET /v1/procurement-notices/{id}`, `GET /v1/procurement-notices/search`, and `GET /v1/procurement-notices/stats` backed only by the checked-in static snapshot.
- Updated project version metadata to `0.19.0` while keeping `/v1` and response `metadata.version == "v1"` unchanged.

## 0.18.0

- Researched Slovak healthcare-facility/provider sources for the Phase 3 medical-facilities roadmap item.
- Documented NCZI NR PZS as the authoritative national register, but no approved public record-level bulk/API/export source was verified.
- Documented e-VUC / Register zdravotnictva and IdZZ; IdZZ is suitable as a future canonical facility ID if exposed by an approved source.
- Added `healthcareFacilities` source-registry metadata as research-only/acquisition-blocked.
- Did not add an importer, production dataset, runtime service, or public endpoint.
- Updated project version metadata to `0.18.0` while keeping `/v1` and response `metadata.version == "v1"` unchanged.

## 0.17.0

- Researched Register adries / Slovak street and address data sources for the Phase 3 streets roadmap item.
- Documented that MV reference-data services and an eID/mailbox XML dataset workflow exist, but no approved anonymous reproducible open-data/bulk source was verified for OpenSK production use.
- Documented `registeradries.sk` as a separate third-party/API-key source candidate, not an approved official production source.
- Added `streets` source-registry metadata as research-only/acquisition-blocked.
- Did not add an importer, production dataset, runtime service, or public endpoint.
- Updated project version metadata to `0.17.0` while keeping `/v1` and response `metadata.version == "v1"` unchanged.

## 0.16.0

- Researched official ŽRSR / Slovak Trade Register machine-readable acquisition options.
- Documented that only a human-facing ŽRSR search interface was verified; no official bulk export, open-data distribution, documented API, WSDL, CSV, XML, JSON, or downloadable archive was approved.
- Classified ŽRSR production import as research-only because source access, reuse, privacy, and reproducible acquisition gates are blocked.
- Added `tradeRegistrations` source-registry metadata as research-only/no production dataset.
- Did not add an importer, production dataset, runtime service, or public endpoint.
- Updated project version metadata to `0.16.0` while keeping `/v1` and response `metadata.version == "v1"` unchanged.

## 0.15.0

- Verified the official Finančná správa `Zoznam daňových subjektov registrovaných pre DPH` ZIP/XML source and retained licence evidence.
- Added offline VAT registration fetch/import tooling for generated research output.
- Blocked production VAT promotion because the XML includes natural persons and addresses but has no reliable natural/legal subject marker.
- Added VAT registration validation helpers and tests for privacy-field rejection and deterministic normalization.
- Added `vatRegistrations` source-registry metadata and VAT source research documentation.
- Did not add `GET /v1/vat/{ico}` or `GET /v1/dph/{ico}` in this milestone.
- Updated project version metadata to `0.15.0` while keeping `/v1` and response `metadata.version == "v1"` unchanged.

## 0.14.0

- Verified the current RPO acquisition gate and chose `RESEARCH_AND_TOOLING_ONLY`; the production company dataset remains seed-backed.
- Documented current RPO portal/API/mirror findings, CC BY 4.0 evidence from API documentation, privacy constraints, and production import blockers.
- Hardened the company importer for future local RPO-style files with natural-person exclusion, recursive forbidden-field stripping, duplicate reporting, and richer import statistics.
- Strengthened company privacy validation denylists for statutory/person-role fields.
- Retained both existing lookup endpoints, including `/v1/ico/{ico}` as the compatibility alias.
- Updated project version metadata to `0.14.0` while keeping `/v1` and response `metadata.version == "v1"` unchanged.

## 0.13.0

- Added a concrete `1.0.0` readiness audit covering public endpoints, datasets, source/licence posture, breaking-change candidates, privacy, operations, and release blockers.
- Added a candidate `v1` API contract document for eventual `1.0.0` without changing the `/v1` namespace or response `metadata.version` semantics.
- Added release-readiness and privacy-review documentation.
- Added minimal GitHub Actions CI gates for dataset validation, referential integrity, tests, compileall, and whitespace checks.
- Updated project version metadata to `0.13.0` while keeping the API namespace at `/v1`.

## 0.12.0

- Hardened public API consistency docs and regression coverage against the actual OpenAPI route surface.
- Updated root metadata to expose project SemVer separately from API namespace/version fields.
- Expanded smoke tests to cover representative list, detail, search, stats, company alias, docs, and OpenAPI routes.
- Added route-shadowing, error-envelope, OpenAPI tag/summary, and `/v1` namespace regression tests.
- Preserved existing `/v1` route namespace and response `metadata.version == "v1"` semantics.

## 0.11.0

- Added MŠVVaM `Register škôl a školských zariadení` as aggregate school facility count data, not an institution-level school directory.
- Added offline `scripts/import_school_facility_counts.py` for the confirmed local CSV and retained the 2025-09-15 source CSV under `data/raw/`.
- Added `data/school_facility_counts.json` with 1,227 aggregate rows and 7,026 total organizational units; all rows link to local region and district codes.
- Added `GET /v1/school-facility-counts` and `GET /v1/school-facility-counts/stats` endpoints.
- Intentionally did not add `/v1/schools` or per-school lookup routes because the confirmed source CSV contains aggregate rows only.
- Kept privacy guardrails: no school names, addresses, staff, directors, pupils, personal emails, or phone numbers are exposed.

## Unreleased / pre-1.0 stabilization

- Reset project-facing versioning to `0.10.0-dev` so future `1.0.0` can represent the first stable public API contract.
- Documented that earlier `v1.x` labels were internal development milestone labels, not formal stable releases.
- Kept all existing API functionality, endpoint paths, and response shapes unchanged.
- Reserved future `1.0.0` for a stabilization pass that includes source/compliance review and an intentional release process.

## v1.9.0

- Added MŠVVaM `Register škôl a školských zariadení` as aggregate school facility count data, not an institution-level school directory.
- Added offline `scripts/import_school_facility_counts.py` for the confirmed local CSV and retained the 2025-09-15 source CSV under `data/raw/`.
- Added `data/school_facility_counts.json` with 1,227 aggregate rows and 7,026 total organizational units; all rows link to local region and district codes.
- Added `GET /v1/school-facility-counts` and `GET /v1/school-facility-counts/stats` endpoints.
- Intentionally did not add `/v1/schools` or per-school lookup routes because the confirmed source CSV contains aggregate rows only.
- Kept privacy guardrails: no school names, addresses, staff, directors, pupils, personal emails, or phone numbers are exposed.

## v1.8.0

- Added `data/vehicle_registration_codes.json` with 93 legacy two-letter district abbreviations from Slov-Lex legal text for vehicle registration numbers.
- Added `GET /v1/vehicle-registration-codes`, `GET /v1/vehicle-registration-codes/{code}`, and `GET /v1/vehicle-registration-codes/search` endpoints.
- Linked 84 records to local district codes and all 93 records to local region codes; aggregate Bratislava and Košice abbreviations intentionally keep `districtCode: null`.
- Added validation, referential integrity checks, API tests, dataset tests, and smoke-test coverage.
- Kept wording conservative: this is historical/reference data only, not a full plate lookup, current vehicle lookup, owner lookup, or proof of current plate-to-district accuracy.

## v1.7.1

- Located and retained the official telecom regulator phone-area workbook source (`30.xls`) and converted its `List1` sheet to CSV for reproducible offline imports.
- Replaced the 5-row phone-area seed with 2,922 imported municipality-to-primary-area records.
- Linked 2,919 imported phone-area rows to local municipality, district, and region codes; retained 3 unmatched source rows with null local geography links.
- Updated phone-area source metadata, docs, validation expectations, and tests while keeping licence wording conservative.
- Kept runtime API behavior local/static with no upstream route calls and no new endpoint domains.

## v1.7.0

- Added seed-backed `data/phone_areas.json` with local municipality, district, and region links for initial phone-area lookup coverage.
- Added offline `scripts/import_phone_areas.py` support for local CSV/JSON/XLSX source files.
- Added `GET /v1/phone-areas`, `GET /v1/phone-areas/{code}`, and `GET /v1/phone-areas/search` endpoints.
- Added phone-area dataset validation, referential integrity checks, smoke tests, and API/import tests.
- Kept licence and source wording conservative pending retained telecom regulator workbook evidence.

## v1.6.0

- Added explicit source-compliance metadata to `data/sources.json`, including licence status, redistribution status, terms URL, attribution, risk level, and next action.
- Added `docs/source-compliance.md` with a dataset-by-dataset compliance matrix.
- Added retained-evidence and source-owner question docs under `docs/research/`.
- Updated validation to warn, not fail, for pending or high-risk source-compliance entries.
- Kept runtime behavior unchanged: no new endpoints, no new datasets, and no upstream calls from API routes.

## v1.5.0

- Expanded `data/banks.json` from the NBS domestic payment-system identification-code directory snapshot effective `2026-05-18`.
- Added the offline `scripts/import_banks.py` importer with dry-run/write modes, CSV/JSON support, and active-party marker normalization.
- Hardened bank dataset validation for BIC/SWIFT, active-party fields, country codes, and duplicate identifiers.
- Kept IBAN validation and bank-code resolution fully local with no runtime upstream calls.
- Kept source/licence wording conservative: `Source/licence verification pending.`

## v1.4.0

- Backfilled PSC `districtCode` from `municipalityCode` using verified local municipality district mappings.
- Verified PSC `districtCode` coverage is 100% for the current local PSC records, with 0 unresolved municipality codes and 0 region conflicts.
- Kept PSC source as PortalVS classifier 42 and did not infer districtCode values from names or PSC patterns.
- Kept PortalVS licence/reuse wording conservative and added no new endpoints.

## v1.3.0

- Populated municipality district mappings from PortalVS classifier 9 (`Obce`) for the checked-in runtime dataset.
- Kept municipality codes stable and validated municipality region alignment against the local districts dataset.
- Kept PSC `districtCode` coverage unchanged for the v1.4.0 backfill milestone.
- No new endpoints or response-envelope changes were introduced.

## v1.2.0

- Expanded the district dataset to the verified 79 Slovak districts imported from PortalVS classifier 10.
- Updated district source, coverage, and validation metadata to reflect the complete district dataset.
- Kept PSC districtCode coverage unchanged.
- No API behavior changes were introduced.

## v1.1.0

- Improved the dataset source registry and aligned it with current coverage and verification status.
- Added and updated source verification documentation for PSC, company, bank, district, holiday, and geography datasets.
- Clarified licence and redistribution statuses without changing API behavior.
- Added a verification backlog for unresolved source tasks.
- No API behavior changes were introduced.

## v1.0.1

- Fixed post-release version and status references in the app metadata and docs.
- Aligned the README and API status docs with the shipped v1.0.0 stable seed-backed release.
- Verified the public smoke-test expectations against the deployed surface.
- No API behavior changes were introduced.
- No new endpoints were added.

## v1.0.0-rc.6

- Finalized release verification and aligned endpoint status documentation with the shipped local data model.
- Expanded smoke-test coverage for the documented public surface and confirmed the seed-backed company lookup.
- Kept the release feature set unchanged and added no new public endpoints.
- Bumped the application version to `v1.0.0-rc.6`.

## v1.0.0-rc.5

- Added a small checked-in company seed dataset and activated local company lookups for known IČOs.
- Updated the smoke test and dataset/docs to reflect seed-backed company coverage.
- Bumped the application version to `v1.0.0-rc.5`.

## v1.0.0-rc.4

- Added `docs/api-status.md`, `docs/known-limitations.md`, and the RPO verification follow-up notes.
- Added the public smoke-test script and the data source verification issue template.
- Tightened the README into stable vs experimental endpoint sections and refreshed public-readiness guidance.
- Bumped the application version to `v1.0.0-rc.4`.
- No new public endpoints were added.

## v1.0.0-rc.3

- Added an RPO licence verification note and kept the company dataset withheld because official redistribution terms remain unverified.
- Hardened company dataset validation against forbidden personal/stakeholder fields.
- Kept the company lookup endpoint fail-closed with `503 DATASET_UNAVAILABLE` until a local dataset is approved.
- Bumped the application version to `v1.0.0-rc.3`.

## v1.0.0-rc.2

- Added a local company lookup service with canonical `/v1/companies/{ico}` and alias `/v1/ico/{ico}` routes.
- Added IČO normalization/validation and offline company dataset validation helpers.
- Kept company data local/offline only with `503 DATASET_UNAVAILABLE` when the dataset is absent.
- Kept personal, stakeholder, and statutory-body fields out of the public response shape.
- Updated the docs to keep the runtime scope offline-only and honest about partial PSC coverage.
- Clarified that source/licence verification is still pending for datasets that need it.
- Bumped the application version to `v1.0.0-rc.2`.

## v1.0.0-rc.1

- Added IČO/company research notes under `docs/research/ico-sources.md`.
- Documented the proposed normalized company schema and offline prototype import flow.
- Added a research-only company source entry to `data/sources.json`.
- Updated the README and source inventory to keep company work prototype-only.
- Bumped the application version to `v1.0.0-rc.1`.
- No public company endpoint was added.

## v0.9.0

- Documented the PSC collection surface, including list, search, and stats endpoints.
- Documented PSC pagination with `limit` and `offset`.
- Clarified that imported PSC data currently has `districtCode: null` and that source/licence verification is still pending.
- Bumped the application version to `v0.9.0`.

## v0.8.0

- Expanded the checked-in PSC dataset beyond the original tiny seed-only sample.
- Documented the current PSC coverage, importer workflow, and source/licence verification status.
- Updated the PSC documentation to explain repeated source codes and the `matchCount` / `matches` preview shape.
- Bumped the application version to `v0.8.0`.

## v0.7.0

- Expanded `data/municipalities.json` from the Eurostat LAU 2025 workbook.
- Updated `data/regions.json` to the current Eurostat NUTS 2024 code mapping.
- Kept district provenance explicitly unverified and documented the offline-only import/runtime flow.
- Bumped the application version to `v0.7.0`.
- No runtime upstream calls were added.

## v0.6.0

- Added `data/sources.json` as the source registry.
- Added `data/raw/` and `data/generated/` storage conventions for import work.
- Added `scripts/import_geography.py`, `scripts/import_utils.py`, and `scripts/fetch_source.py` for offline import and optional source fetching.
- Added `docs/import-pipeline.md` to document the offline raw-to-generated-to-runtime flow.
- Added importer tests for dry-run, write, validation, and referential checks.
- No new public endpoints were added.

## v0.5.0

- Added `docs/data-sources.md` with the current dataset inventory, coverage notes, and provenance placeholders.
- Added `docs/dataset-format.md` with the local JSON file shapes and shared metadata conventions.
- Updated the README with dataset tooling guidance.
- No new public endpoints were added in this release.

## v0.2.0

- Added `GET /v1/banks` and `GET /v1/banks/{code}` from a static Slovak bank seed dataset.
- Added `GET /v1/iban/validate/{iban}` for local Slovak IBAN validation and bank resolution.
- Documented the new endpoints and dataset limitations.

## v0.4.0

- Added PSC geography code fields and optional geography expansion.
- Added `GET /v1/psc/{psc}?include=geography` for nested local geography objects.
- Linked PSC seed records to the local regions, districts, and municipalities datasets where available.
- Updated tests and docs for PSC geography integration.

## v0.3.0

- Added `GET /v1/regions` and `GET /v1/regions/{code}`.
- Added `GET /v1/districts` and `GET /v1/districts/{code}`, including `regionCode` filtering.
- Added `GET /v1/municipalities` and `GET /v1/municipalities/{code}`, including `regionCode` and `districtCode` filtering.
- Added static geography datasets with honest seed/full coverage notes.

## v0.2.0

- Added `GET /v1/banks` and `GET /v1/banks/{code}` from a static Slovak bank seed dataset.
- Added `GET /v1/iban/validate/{iban}` for local Slovak IBAN validation and bank resolution.
- Documented the new endpoints and dataset limitations.

## v0.1.1

- Fixed README deployment URLs and markdown formatting.
- Added consistent enveloped API error responses.
- Added stable dataset freshness metadata for holidays and PSC.
- Added `Cache-Control` headers for static dataset endpoints.

## v0.1.0

- Added `GET /v1/health` for basic service checks.
- Added `GET /v1/holidays/2026` from a static holiday dataset.
- Added `GET /v1/psc/81101` and a small static PSC seed dataset.
- Added Swagger docs at `/docs` and OpenAPI at `/openapi.json`.
- Enabled global CORS for browser clients.
- Added tests and CI for local and GitHub Actions verification.
