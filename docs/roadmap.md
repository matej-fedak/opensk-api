# Roadmap

Living strategic roadmap for OpenSK API. This file is the source of truth for direction; update it as milestones complete. Detailed rationale lives in `docs/research/opensk-research-roadmap-2026-q4.md` and `docs/research/roadmap-council-notes.md`; compliance state lives in `docs/source-compliance.md`; candidate stable scope lives in `docs/1-0-scope.md`.

Principles (council consensus): local materialized JSON only, no upstream calls at runtime; compliance evidence before promotion; no personal-data endpoints; no scraping; honest coverage/attribution wording as a feature; no public promotion while PortalVS redistribution is unresolved.

## Now (0.23.x cycle)

Data:

- Milestone 1 "Ask & Evidence": four packages sent manually 2026-10-11. **NBS bank reuse resolved by reply received 2026-10-14** (`REPLY_RECEIVED_RESOLVED`); PortalVS, telecom and ŠÚ SR elections remain `SENT_AWAITING_REPLY`. See `docs/research/source-licence-outreach.md`; no permission inferred for unanswered domains.
- Banks refreshed in **0.23.8** to v226 / effective 2026-10-08, downloaded 2026-10-15T16:23:00Z. All 30 domestic rows/columns reconciled; direct bank/IBAN provenance and attribution delivered. Monitor future versions manually, not another licence outreach. SIPS-derived fields remain distinct from HTML `Akt. úč.`; `docs/research/nbs-bank-reuse-clarification.md`.
- PortalVS geography migrated in **0.23.10**: districts + municipalities are successor-backed from fresh 2026-10-16 county/town data, all IDs preserved, exactly two reviewed display corrections. PSC remains byte-identical, legacy-backed and frozen (`NO_GO_SUCCESSOR_PSC`, 0.23.9). No street/detail import, no runtime upstream dependency; geography refresh no longer needs legacy PortalVS. Rights remain unresolved / `SENT_AWAITING_REPLY`, public promotion gated. Current migration/refresh evidence: `docs/research/portalvs-successor-geography-migration.md`; PSC findings remain in `docs/research/portalvs-psc-successor-semantics.md`.
- **0.23.11 PSC Administrative Mapping Evidence Spike** confirms `MAPPING_PARTIAL`, `CONTRACT_CLARIFICATION_REQUIRED`, `NO_SOURCE_READY`, overall **NO_GO_SUCCESSOR_PSC**. REGPJ reconciles all 2,927 administrative IDs but has no certified as-of/validity or street hierarchy; 127 ZSJ codes have multiple administrative parents. Of 42 target rows: one snapshot-qualified parent, one ambiguous, 40 unmatched; none of 63 incomplete street-only PSCs becomes complete. Postal-part/REGPJ paths conflict for Orechová Potôň-Lúky. **All production JSON remains unchanged. Park PSC**, no promised 0.23.12 migration. `docs/research/psc-administrative-mapping.md`.
- 0.23.5 delivered the public launch guardrails (see Completed): **operational guardrails are ready**, but **public promotion is still gated by unresolved PortalVS compliance** unless a real reply arrives. Priorities consider the three outstanding replies, PortalVS approaching 2026-10-31, production behavior and developer adoption.
- Elections evidence stays parked pending a ŠÚ SR reply: retain election-specific CC BY 4.0 coverage, attribution and an approved acquisition workflow. 0.23.11 observes that current general terms narrow the automation ban to abusive/high-load collection; this does not settle election-specific scope or change the pending outreach state. The NBS bank reply does not clear elections.

Trust & provenance:

- Align `docs/source-compliance.md`, `docs/research/source-verification-evidence.md`, and `data/sources.json` per reply received.

Reliability / ops:

- Delivered in 0.23.5: application rate limiter (`docs/rate-limiting-contract.md`) and the scheduled daily public smoke workflow. Watch the smoke results and rate-limit headers in production; revisit shared-state limiting only on the documented multi-instance trigger.
- Delivered in **0.23.12**: public OpenAPI audited against runtime for all **39 GET operations**, explicit stable IDs, typed success/application-error contracts, verified examples and developer quickstart. PSC grouped lookup/count bug corrected without changing production data/source/freshness; `/v1` and metadata version `v1` unchanged. PSC successor remains parked. `docs/research/openapi-contract-audit.md`.

Delivered in 0.23.1: curated `/v1/sources` public provenance catalogue, Slovak business-day utilities (strict 2024-2026 coverage), ETag/Last-Modified conditional caching with documented Cache-Control policy, version single-sourcing (`version.py`), unified CI + Dependabot, manual source-health checker (`scripts/check_source_urls.py`), dataset-domain contributor gates (`docs/adding-a-dataset.md`), and the rate-limit contract document.

## Next (queued)

Data:

- Elections production stays **pending evidence**, not scheduled: 0.23.2 concluded `GO_AFTER_LICENCE_EVIDENCE` (also acquisition permission). NR SR 2023 is UTF-8/comma/dot decimal, not the previously suspected CP1250; 2,926/2,927 current municipality matches and complete election-native joins. The official foreign-voting unit must remain independent of PortalVS. After rights/acquisition clearance, scope one aggregate historical election, not candidate/precinct services or a generic all-election framework.
- **PSC is parked after 0.23.11**, not queued for another automatic evidence loop or production migration. Reopen only on a specific authoritative distinguishing crosswalk, dated street/admin hierarchy or source-owner clarification; exact mappings, temporal scope, truthful occurrence semantics and reuse must all be established. Preserve the current historical snapshot. No unrelated dataset is automatically next.

Trust & provenance:

- Align `docs/source-compliance.md`, `docs/research/source-verification-evidence.md`, and `data/sources.json` per reply received (repeated from Now; the Trust Surface backlog — sources catalogue, rate limiter, conditional caching — is delivered, see Completed).

Developer adoption:

- **Real external-developer feedback is next**, not another automatic dataset milestone: a maintainer-run, appropriately scoped **5–10 developer pilot**, starting with quickstart/Swagger, one lookup, filtered collection, utility and `/v1/sources`. Collect concrete integration friction and prioritize observed failures. No outreach has happened as part of 0.23.12; public-promotion/source-compliance gates remain. `docs/developer-adoption.md`.
- Do not generate/publish an SDK until outside developers have tested the OpenAPI and identified a concrete need. Continue source-owner reply monitoring separately; **no 1.0 promise**, no automatic PSC evidence loop or successor migration.

## Watch (sources identified, gates unresolved — no scheduled work)

Data:

- ITMS2014+ historical EU-funds extension (live, but distinct schema/licence evidence); defer rather than mix into the primary ITMS21+ slice.
- ŠÚKL medicines (licence unstated).
- ECB euro reference rates: promoted to production in 0.23.4 (see Completed); business-day utility delivered in 0.23.1.
- Slov-Lex legislation metadata catalogue (after elections; § 5 písm. b) exclusion verified).
- NCZI healthcare facilities; CVTI/RIS institution-level schools; ÚVO national procurement; Ministry court-decision metadata — all gated, see `docs/source-compliance.md`.

Architecture:

- Storage review triggers; SQLite spike only if triggers fire. Materialized JSON stays the architecture meanwhile.

## Later (explicitly deferred)

- SDK/client libraries (OpenAPI correctness first).
- Custom domain before public launch/promotion (nice-to-have, not a blocker).
- Automated scheduled dataset refreshes (after licence clarity + trigger design).
- `/v2` uniform response-shape cleanup (only if a uniform contract is chosen; `docs/api-contract-v1.md` decision).
- CRZ contracts, VAT/DPH: gated on privacy, not scheduled.
- RPO company expansion: gated on acquisition + privacy, not scheduled.

## Rejected (council record)

- VAT/DPH build-first; CRZ as procurement drop-in; procurement automation before TED wording retention; personal-data endpoints; scraping any human-facing portal. Details: `docs/research/roadmap-council-notes.md`.

## Completed (recent milestones)

- 0.23.12: **Developer Adoption & OpenAPI Contract Correctness**. Actual OpenAPI/TestClient before-audit of all 39 GET operations; typed success schemas **9→39**, explicit stable IDs **0→39**, operation response examples **0→39**, applicable typed errors **0→38** (health exempt, no application errors). Focused domain schemas preserve historical arrays/objects/pages, casing/nulls and bank provenance; manual 400 parsing and genuine integer 422 paths retained. PSC lookup indexes the same flat logical records as list/search, fixes matchCount and geography expansion; **all 14 production JSON files byte-identical**, no source/licence/outreach/freshness changes. README/quickstart and manual pilot handoff; no new route/dataset/SDK or `/v2`. **PSC successor remains PARKED / NO_GO_SUCCESSOR_PSC**. `docs/research/openapi-contract-audit.md`.
- 0.23.11: **PSC Administrative Mapping Evidence Spike — RESEARCH ONLY**. Fresh 13,700-row successor capture and official postal ZIP; manually supplied official REGPJ ZIP, real schema/parent cardinalities, 2,927/2,927 administrative IDs reconciled, offline deterministic evidence analyzer/negative controls and 42-row/63-PSC curated diagnostics. Strict snapshot-qualified model: 1,228 complete / 105 partial / 82 no-map PSCs, 10,432/13,700 uniquely parented source rows; **not current certified coverage or import approval**. `MAPPING_PARTIAL`, `CONTRACT_CLARIFICATION_REQUIRED`, `NO_SOURCE_READY`, **NO_GO_SUCCESSOR_PSC**. Source-specific reuse pending/unknown; no licence inference, automatic outreach, raw street dump, runtime/API/source registry or production dataset changes; **39 GET operations**. Developer adoption next. `docs/research/psc-administrative-mapping.md`.
- 0.23.10: **PortalVS Successor Geography Migration**, districts + municipalities only. Fresh 2026-10-16T08:04:45Z county/town acquisition (80 / 2,928 source rows), one foreign pseudo row excluded per source, **79 districts / 2,927 municipalities**, all IDs/relationships preserved; all 12 re-letterings evidence-verified. 205 disambiguated names; exactly two reviewed display corrections (`504173`, `504742`). Offline manifest-checked, staged/validated paired importer with rollback/recovery, current geography registry/catalogue provenance and acquisition-date freshness. **PSC bytes/source/freshness unchanged and legacy-backed**; no street/detail/REGPJ work, no runtime upstream dependency. Rights/outreach unchanged; **39 GET operations**. `docs/research/portalvs-successor-geography-migration.md`.
- 0.23.9: PortalVS PSC semantics/successor mapping **research spike, not production migration**. Complete retained successor capture reproduced (80 county / 2,928 town / 13,700 PSC rows); official postal ZIP evidence, offline deterministic analyzer and synthetic tests; curated 82-pair / 122-street-only-PSC / 69-affected-PSC diagnostics without streets/raw dumps. `NO_GO_SUCCESSOR_PSC`; districts/municipalities technically `GO_PRODUCTION_NEXT`. No production JSON/registry/source/outreach/route changes; 39 GET operations. `docs/research/portalvs-psc-successor-semantics.md`.
- 0.23.8: NBS bank v226 / effective 2026-10-08 refresh (download 2026-10-15T16:23:00Z; URL/bytes/hash retained), 30 domestic rows, two names/one BIC changed, no code/SIPS changes. Current CSV/HTML field audit, deterministic refresh report, explicit importer provenance and validation. Existing bank/IBAN responses carry NBS source/version/effective/download/attribution/transformation metadata; checksum logic remains OpenSK/ISO. 39 GET operations; no runtime upstream, DB/dependencies/symbols or unrelated dataset/outreach changes. `docs/research/nbs-bank-reuse-clarification.md`.
- 0.23.7: ITMS21+ title-free project-reference production API, exactly list and project-code lookup (**39 GET operations**). Complete bounded 2026-10-15 list acquisition: 4,574 source / 4,561 included / 13 privacy-excluded; 46 forms reviewed, 40 positively approved. Manifest-backed offline importer, refresh/removal guard, exact money strings without unsupported EUR claim, typed schema/static caching, MIRRI/generic catalogue CC BY attribution; public coverage partial. **JSON_CONTINUE**, ~5.33 MB / ~320 ms service cold load. No raw personal captures, runtime upstream, ITMS2014+, payment/procurement/irregularity expansion, DB or bank refresh. `docs/eu-funds.md`.
- 0.23.6: ITMS21+ EU-funds source/licence/schema/privacy spike; `GO_PRODUCTION_NEXT`, `JSON_CONTINUE`. Official JSON and project-specific rights verified; 4,571 source projects observed, 100 eligible sample rows, eight NUTS3 codes matched. Offline generated-only importer with exact decimals and positive reviewed legal-form gate **excluding entire unsafe/unreviewed projects and identifiers/URLs**; research-only catalogue entry. NBS bank reuse clarification received/resolved; v225 unchanged. No EU-funds production route/data, DB, runtime acquisition or procurement fusion; PortalVS/telecom/elections states unchanged.
- 0.23.5: public launch guardrails — 100 requests/60 s/client-IP fixed-window application limiter (`429 RATE_LIMITED` + `Retry-After` + `X-RateLimit-*` headers, `/v1/health` exempt, Render auto-enablement via verified `RENDER=true`, spoof-resistant identity via Cloudflare's edge-set `CF-Connecting-IP` visitor header with a conservative right-most-XFF fallback, process-local in-memory state, no Redis/keys/new deps) and daily 06:17 UTC scheduled public smoke workflow with bounded cold-start warm-up (`--expect-rate-limit` proves deployed limiter headers; never exhausts the limit). Operational guardrails ready; public promotion still gated by unresolved PortalVS compliance.
- 0.23.4: ECB exchange-rate production surface — `GET /v1/exchange-rates/latest` + `GET /v1/exchange-rates/{date}` (37 GET operations total), full-history `data/exchange_rates.json` snapshot (1999-01-04→2026-10-12, 7,112 dates, 221,296 rows, 6,006,060 bytes), decimal-string rates, exact-date/no-fallback semantics, optional `?currency=` filter, production `exchangeRates` catalogue entry (licence verified), ETag/Last-Modified + per-route Cache-Control, production importer with historical-change refresh guard, manual offline refresh policy. No runtime upstream calls; no database (`JSON_CONTINUE`; ~74 ms cold parse, ~23 MiB retained heap measured). Elections stay research-only. Current outreach states are recorded under Now (NBS bank reply resolved 2026-10-14).
- 0.23.3: exchange-rates spike (`GO_PRODUCTION_NEXT`, `JSON_CONTINUE`) + PortalVS source resilience (`SUCCESSOR_COMPATIBLE_WITH_TRANSFORM_CHANGES`) + manual dispatch of four packages on 2026-10-11 (current states under Now; NBS bank reply resolved 2026-10-14). ECB eurofxref feeds measured (1999-01-04→present, 7,111 dates, 221,267 rows), offline importer prototype with strict validation; research-only `exchangeRates` source entry; **no public exchange-rate or elections endpoint, no production dataset**. Evidence: `docs/research/exchange-rates-spike.md`, `docs/research/portalvs-source-resilience.md`.
- 0.23.2: NR SR 2023 source/licence/schema/privacy spike and offline import prototype; `GO_AFTER_LICENCE_EVIDENCE`, `JSON_CONTINUE`. No public elections results endpoint or production data. NR SR 2020/referendum 2023 samples establish dialect and semantic drift; ŠÚ SR outreach sent manually 2026-10-11, awaiting reply. Evidence: `docs/research/elections-spike.md`.
- 0.23.1: trust and utility surface — `/v1/sources` curated provenance catalogue, business-day check/add/between utilities, ETag/Last-Modified caching + cache policy, version single-sourcing, CI merge + Dependabot + source-health checker, rate-limit contract (implementation deferred).
- 0.23.0: licence-outreach packages + council notes + living roadmap; PortalVS deadline (2026-10-31) and non-commercial wording verified; elections chosen as next data spike.
- 0.22.0: court-decision source research (Ministry OpenAPI verified; research-only; no endpoint/dataset).
- 0.21.0: paper-roadmap coverage audit; candidate `docs/1-0-scope.md` frozen.
- 0.20.0–0.19.0: school-directory research (aggregate counts stay the only school surface); TED_PARTIAL procurement snapshot.
- 0.13.0–0.14.0: CI gates + 1.0 readiness audit + v1 contract doc; company seed hardened, RPO gated.
