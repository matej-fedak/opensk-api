# Roadmap

Living strategic roadmap for OpenSK API. This file is the source of truth for direction; update it as milestones complete. Detailed rationale lives in `docs/research/opensk-research-roadmap-2026-q4.md` and `docs/research/roadmap-council-notes.md`; compliance state lives in `docs/source-compliance.md`; candidate stable scope lives in `docs/1-0-scope.md`.

Principles (council consensus): local materialized JSON only, no upstream calls at runtime; compliance evidence before promotion; no personal-data endpoints; no scraping; honest coverage/attribution wording as a feature; no public promotion while PortalVS redistribution is unresolved.

## Now (0.23.x cycle)

Data:

- Milestone 1 "Ask & Evidence": PortalVS, NBS, telecom and ŠÚ SR elections outreach packages were sent manually by the maintainer on 2026-10-11; all are `SENT_AWAITING_REPLY` and no permission is inferred (states in `docs/research/source-licence-outreach.md`). Retain exact Eurostat/TED/NBS/Slov-Lex/MŠVVaM wording in evidence docs.
- PortalVS transition: 0.23.3 verified both systems live and concluded `SUCCESSOR_COMPATIBLE_WITH_TRANSFORM_CHANGES` — temp-dir manifests/snapshots retained locally (not committed), successor rebuild is offline transforms only. Keep watching the 2026-10-31 legacy end-of-support date and the outreach reply (`docs/research/portalvs-source-resilience.md`).
- Recommended next: **0.23.4 — Exchange Rates Production Surface**. 0.23.3 concluded `GO_PRODUCTION_NEXT`: ECB reuse permission is explicit, acquisition is the intended machine channel, the offline importer is prototype-tested, and full-history JSON is ~3.5 MiB. If an outreach reply arrives first, evaluate whether a small evidence-driven compliance/promotion milestone supersedes it.
- Elections evidence stays parked pending a ŠÚ SR reply: retain election-specific CC BY 4.0 coverage, attribution and an approved acquisition workflow. The general policy's automated-download prohibition is a real gate, not an inferred exception. No reply is assumed from any of the four packages.

Trust & provenance:

- Align `docs/source-compliance.md`, `docs/research/source-verification-evidence.md`, and `data/sources.json` per reply received.

Reliability / ops:

- Scheduled daily public smoke test (still open); rate-limit implementation per `docs/rate-limiting-contract.md` before public promotion.

Delivered in 0.23.1: curated `/v1/sources` public provenance catalogue, Slovak business-day utilities (strict 2024-2026 coverage), ETag/Last-Modified conditional caching with documented Cache-Control policy, version single-sourcing (`version.py`), unified CI + Dependabot, manual source-health checker (`scripts/check_source_urls.py`), dataset-domain contributor gates (`docs/adding-a-dataset.md`), and the rate-limit contract document.

## Next (queued)

Data:

- Elections production stays **pending evidence**, not scheduled: 0.23.2 concluded `GO_AFTER_LICENCE_EVIDENCE` (also acquisition permission). NR SR 2023 is UTF-8/comma/dot decimal, not the previously suspected CP1250; 2,926/2,927 current municipality matches and complete election-native joins. The official foreign-voting unit must remain independent of PortalVS. After rights/acquisition clearance, scope one aggregate historical election, not candidate/precinct services or a generic all-election framework.

Trust & provenance:

- Milestone 2 "Trust Surface": `/v1/sources` curated view; rate-limit contract doc + implementation; ETag/Last-Modified with byte-stable dataset responses.

Developer adoption:

- Typed OpenAPI models; version single-sourcing; dataset-domain contributor guide.

## Watch (sources identified, gates unresolved — no scheduled work)

Data:

- ITMS EU funds (licence capture needed).
- ŠÚKL medicines (licence unstated).
- ECB euro reference rates: promoted out of Watch by 0.23.3 (`GO_PRODUCTION_NEXT`; synthesis in `docs/research/exchange-rates-spike.md`). Business-day utility itself is delivered in 0.23.1.
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

- 0.23.3: exchange-rates spike (`GO_PRODUCTION_NEXT`, `JSON_CONTINUE`) + PortalVS source resilience (`SUCCESSOR_COMPATIBLE_WITH_TRANSFORM_CHANGES`) + outreach state alignment (all four packages `SENT_AWAITING_REPLY` since 2026-10-11). ECB eurofxref feeds measured (1999-01-04→present, 7,111 dates, 221,267 rows), offline importer prototype with strict validation; research-only `exchangeRates` source entry; **no public exchange-rate or elections endpoint, no production dataset**. Evidence: `docs/research/exchange-rates-spike.md`, `docs/research/portalvs-source-resilience.md`.
- 0.23.2: NR SR 2023 source/licence/schema/privacy spike and offline import prototype; `GO_AFTER_LICENCE_EVIDENCE`, `JSON_CONTINUE`. No public elections results endpoint or production data. NR SR 2020/referendum 2023 samples establish dialect and semantic drift; ŠÚ SR outreach sent manually 2026-10-11, awaiting reply. Evidence: `docs/research/elections-spike.md`.
- 0.23.1: trust and utility surface — `/v1/sources` curated provenance catalogue, business-day check/add/between utilities, ETag/Last-Modified caching + cache policy, version single-sourcing, CI merge + Dependabot + source-health checker, rate-limit contract (implementation deferred).
- 0.23.0: licence-outreach packages + council notes + living roadmap; PortalVS deadline (2026-10-31) and non-commercial wording verified; elections chosen as next data spike.
- 0.22.0: court-decision source research (Ministry OpenAPI verified; research-only; no endpoint/dataset).
- 0.21.0: paper-roadmap coverage audit; candidate `docs/1-0-scope.md` frozen.
- 0.20.0–0.19.0: school-directory research (aggregate counts stay the only school surface); TED_PARTIAL procurement snapshot.
- 0.13.0–0.14.0: CI gates + 1.0 readiness audit + v1 contract doc; company seed hardened, RPO gated.
