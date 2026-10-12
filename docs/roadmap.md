# Roadmap

Living strategic roadmap for OpenSK API. This file is the source of truth for direction; update it as milestones complete. Detailed rationale lives in `docs/research/opensk-research-roadmap-2026-q4.md` and `docs/research/roadmap-council-notes.md`; compliance state lives in `docs/source-compliance.md`; candidate stable scope lives in `docs/1-0-scope.md`.

Principles (council consensus): local materialized JSON only, no upstream calls at runtime; compliance evidence before promotion; no personal-data endpoints; no scraping; honest coverage/attribution wording as a feature; no public promotion while PortalVS redistribution is unresolved.

## Now (0.23.x cycle)

Data:

- Milestone 1 "Ask & Evidence": PortalVS, NBS, telecom and ŠÚ SR elections outreach packages were sent manually by the maintainer on 2026-10-11; all are `SENT_AWAITING_REPLY` and no permission is inferred (states in `docs/research/source-licence-outreach.md`). Retain exact Eurostat/TED/NBS/Slov-Lex/MŠVVaM wording in evidence docs.
- PortalVS transition: 0.23.3 verified both systems live and concluded `SUCCESSOR_COMPATIBLE_WITH_TRANSFORM_CHANGES` — temp-dir manifests/snapshots retained locally (not committed), successor rebuild is offline transforms only. Keep watching the 2026-10-31 legacy end-of-support date and the outreach reply (`docs/research/portalvs-source-resilience.md`).
- 0.23.5 delivered the public launch guardrails (see Completed): **operational guardrails are ready**, but **public promotion is still gated by unresolved PortalVS compliance** unless a real reply arrives. Next milestone is reassessed from: (1) any of the four outreach replies, (2) PortalVS approaching 2026-10-31, (3) production behavior of exchange rates and the new limiter/smoke runs, (4) developer adoption priorities.
- Elections evidence stays parked pending a ŠÚ SR reply: retain election-specific CC BY 4.0 coverage, attribution and an approved acquisition workflow. The general policy's automated-download prohibition is a real gate, not an inferred exception. No reply is assumed from any of the four packages.

Trust & provenance:

- Align `docs/source-compliance.md`, `docs/research/source-verification-evidence.md`, and `data/sources.json` per reply received.

Reliability / ops:

- Delivered in 0.23.5: application rate limiter (`docs/rate-limiting-contract.md`) and the scheduled daily public smoke workflow. Watch the smoke results and rate-limit headers in production; revisit shared-state limiting only on the documented multi-instance trigger.

Delivered in 0.23.1: curated `/v1/sources` public provenance catalogue, Slovak business-day utilities (strict 2024-2026 coverage), ETag/Last-Modified conditional caching with documented Cache-Control policy, version single-sourcing (`version.py`), unified CI + Dependabot, manual source-health checker (`scripts/check_source_urls.py`), dataset-domain contributor gates (`docs/adding-a-dataset.md`), and the rate-limit contract document.

## Next (queued)

Data:

- Elections production stays **pending evidence**, not scheduled: 0.23.2 concluded `GO_AFTER_LICENCE_EVIDENCE` (also acquisition permission). NR SR 2023 is UTF-8/comma/dot decimal, not the previously suspected CP1250; 2,926/2,927 current municipality matches and complete election-native joins. The official foreign-voting unit must remain independent of PortalVS. After rights/acquisition clearance, scope one aggregate historical election, not candidate/precinct services or a generic all-election framework.

Trust & provenance:

- Align `docs/source-compliance.md`, `docs/research/source-verification-evidence.md`, and `data/sources.json` per reply received (repeated from Now; the Trust Surface backlog — sources catalogue, rate limiter, conditional caching — is delivered, see Completed).

Developer adoption:

- Typed OpenAPI models; version single-sourcing; dataset-domain contributor guide.

## Watch (sources identified, gates unresolved — no scheduled work)

Data:

- ITMS EU funds (licence capture needed).
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

- 0.23.5: public launch guardrails — 100 requests/60 s/client-IP fixed-window application limiter (`429 RATE_LIMITED` + `Retry-After` + `X-RateLimit-*` headers, `/v1/health` exempt, Render auto-enablement via verified `RENDER=true`, spoof-resistant `X-Forwarded-For` right-to-left identity, process-local in-memory state, no Redis/keys/new deps) and daily 06:17 UTC scheduled public smoke workflow with bounded cold-start warm-up (`--expect-rate-limit` proves deployed limiter headers; never exhausts the limit). Operational guardrails ready; public promotion still gated by unresolved PortalVS compliance.
- 0.23.4: ECB exchange-rate production surface — `GET /v1/exchange-rates/latest` + `GET /v1/exchange-rates/{date}` (37 GET operations total), full-history `data/exchange_rates.json` snapshot (1999-01-04→2026-10-12, 7,112 dates, 221,296 rows, 6,006,060 bytes), decimal-string rates, exact-date/no-fallback semantics, optional `?currency=` filter, production `exchangeRates` catalogue entry (licence verified), ETag/Last-Modified + per-route Cache-Control, production importer with historical-change refresh guard, manual offline refresh policy. No runtime upstream calls; no database (`JSON_CONTINUE`; ~74 ms cold parse, ~23 MiB retained heap measured). Elections stay research-only; the four outreach replies remain pending.
- 0.23.3: exchange-rates spike (`GO_PRODUCTION_NEXT`, `JSON_CONTINUE`) + PortalVS source resilience (`SUCCESSOR_COMPATIBLE_WITH_TRANSFORM_CHANGES`) + outreach state alignment (all four packages `SENT_AWAITING_REPLY` since 2026-10-11). ECB eurofxref feeds measured (1999-01-04→present, 7,111 dates, 221,267 rows), offline importer prototype with strict validation; research-only `exchangeRates` source entry; **no public exchange-rate or elections endpoint, no production dataset**. Evidence: `docs/research/exchange-rates-spike.md`, `docs/research/portalvs-source-resilience.md`.
- 0.23.2: NR SR 2023 source/licence/schema/privacy spike and offline import prototype; `GO_AFTER_LICENCE_EVIDENCE`, `JSON_CONTINUE`. No public elections results endpoint or production data. NR SR 2020/referendum 2023 samples establish dialect and semantic drift; ŠÚ SR outreach sent manually 2026-10-11, awaiting reply. Evidence: `docs/research/elections-spike.md`.
- 0.23.1: trust and utility surface — `/v1/sources` curated provenance catalogue, business-day check/add/between utilities, ETag/Last-Modified caching + cache policy, version single-sourcing, CI merge + Dependabot + source-health checker, rate-limit contract (implementation deferred).
- 0.23.0: licence-outreach packages + council notes + living roadmap; PortalVS deadline (2026-10-31) and non-commercial wording verified; elections chosen as next data spike.
- 0.22.0: court-decision source research (Ministry OpenAPI verified; research-only; no endpoint/dataset).
- 0.21.0: paper-roadmap coverage audit; candidate `docs/1-0-scope.md` frozen.
- 0.20.0–0.19.0: school-directory research (aggregate counts stay the only school surface); TED_PARTIAL procurement snapshot.
- 0.13.0–0.14.0: CI gates + 1.0 readiness audit + v1 contract doc; company seed hardened, RPO gated.
