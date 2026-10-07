# OpenSK Research & Roadmap — 2026 Q4 Report

Status: research and planning record for milestone `0.23.0`. This report adds no endpoints, datasets, or runtime behavior. It consolidates source-licence verification performed in 2026 Q4, a multi-perspective roadmap council, and the resulting prioritized backlog. It is not legal advice.

Quick links:

- `docs/research/source-licence-outreach.md` — ready-to-send outreach packages (the immediate action).
- `docs/research/roadmap-council-notes.md` — full council verdicts (consensus/majority/contested/rejected).
- `docs/roadmap.md` — the living strategic roadmap (Now/Next/Watch/Later/Completed).
- `docs/1-0-scope.md`, `docs/release-readiness.md` — the candidate 1.0 contract and blockers this report feeds into.

## Executive Summary

1. The dominant risk to the project is upstream rights, not code. PortalVS (districts, municipalities, PSC) is directly verified as carrying a non-commercial copyright restriction and a hard end-of-support date of 2026-10-31 for the legacy system. Every other high-value finding is a clarification opportunity, not a blocker.
2. The next milestone is **Ask & Evidence**: send the prepared outreach messages, retain exact wording for already-adequate licences (Eurostat CC BY 4.0, TED), and align the compliance matrix with retained evidence.
3. Then **Trust Surface**: ETag/Last-Modified caching, curated `/v1/sources` view, rate-limiting contract, deployment/source health hygiene.
4. Then **Elections Spike**: a bounded, aggregate-only elections dataset from official ŠÚ SR open-data CSVs — the highest value-to-risk data addition currently available.
5. The roadmap council produced 13 consensus decisions, 4 majority decisions, 1 contested decision (PortalVS removal order), and 5 explicit rejections (see council notes).

## Part A — Source Licence Verification Findings (2026-10-07)

All findings below were verified directly against official pages during this review unless marked otherwise.

### A.1 PortalVS classifiers 9 / 10 / 42 — CRITICAL, outreach required

- VERIFIED: banner on `ciselniky.portalvs.sk`: "Spustili sme novú verziu číselníkov! Podpora doterajšieho systému končí 31.10.2026." Earlier doubts about the deadline's existence are resolved by direct observation.
- VERIFIED: the successor system `ciselniky2.portalvs.sk` ("IS Číselníky"), operated by MŠVVaM SR, exposes a REST API with JSON/XML/CSV output. Equivalent classifiers: `slovenske-obce` (9/Obce), `slovenske-okresy` (10/Okres), `psc-sk` (42/PSČ). OpenSK's future refresh path is the new system, not the legacy REST endpoints.
- VERIFIED: the portal copyright page reserves rights and allows content use "iba k nekomerčnému použitiu" (non-commercial use only). Whether this restriction reaches the classifier machine-readable exports is exactly the question outreach must answer; until answered, districts/municipalities/PSC stay compliance-Red for 1.0.
- Contacts: `helpdesk@portalvs.sk`, `portalvs@portalvs.sk`. Full Slovak draft in the outreach document.

### A.2 NBS bank-code directory — outreach required (transformation question)

- VERIFIED disclaimer wording (NBS website): "Information published on this website may be stored, reproduced, and further used provided that the source is acknowledged and that neither the content nor other properties of the respective electronic file are modified in any way."
- Open question: whether CSV-to-JSON conversion, field renaming, and an `activeParty` marker constitute "modification". Contact `info@nbs.sk`. Full Slovak draft in the outreach document.

### A.3 NBS holidays — evidence retention, email likely unnecessary

- Same NBS disclaimer applies. Holiday dates are factual dates curated against Act 241/1993 Z. z.; OpenSK does not reproduce an NBS file verbatim. Remaining action: retain the exact disclaimer wording and the legal-act reference in the evidence doc.

### A.4 Telecom regulator phone-area workbook — outreach required

- VERIFIED: the retained workbook (`30.xls`, `List1`) states "údaje určené na ďalšie spracovanie zo strany prijímateľa" — a processing grant that does not by itself settle public redistribution or commercial downstream use.
- Contacts: `marian.jurkovic@teleoff.gov.sk` (data owner), `legal@teleoff.gov.sk`. Full Slovak draft in the outreach document.

### A.5 Slov-Lex legal texts (vehicle registration codes) — contact likely unnecessary

- VERIFIED: the current Copyright Act is zákon č. 185/2015 Z. z.; § 5 písm. b) excludes from copyright, inter alia, "text právneho predpisu, úradné rozhodnutie alebo súdne rozhodnutie, technická norma, ako aj spolu s nimi vytvorená prípravná dokumentácia a ich preklad, bez ohľadu na to, či spĺňajú podmienky podľa § 3 ods. 1". Vyhláška MV SR č. 9/2009 Z. z. § 36 ods. 2 (the abbreviation source) is such a text.
- Conservative posture: keep attribution to Slov-Lex and the regulation; retain the statute/section citation in the evidence doc; fallback contact `helpdesk@slov-lex.sk` if doubt resurfaces. No change to the "historical/reference only" presentation.

### A.6 Eurostat (regions) — licence adequate, wording retention remains

- VERIFIED: Eurostat reuse policy confirms CC BY 4.0 for Eurostat data reuse with source acknowledgement. Regions stay Yellow until the exact wording is retained in the evidence doc (paperwork, not uncertainty).

### A.7 TED / Publications Office (procurement snapshot) — licence adequate, wording retention remains

- VERIFIED: TED reuse terms state TED data "can be freely reused, for commercial or non-commercial purposes" and TED metadata are published as CC0, subject to the TED legal notice and source attribution. Retain the exact legal-notice wording; keep `TED_PARTIAL` scope wording everywhere; do not expand procurement automation meanwhile (council majority).

### A.8 MŠVVaM school facility aggregate CSV — adequate, minor ambiguity

- VERIFIED: the source page lists "Creative Commons BY" without a version. Action: resolve the exact version from the dataset's DCAT metadata when convenient; attribution to MŠVVaM SR is already in place. Not a blocker.

### A.9 ŠÚ SR elections open data — verified as the next data spike candidate

Direct verification of `volby.statistics.sk/tree.html` ("Údaje na stiahnutie"):

- Publisher: Štatistický úrad SR (ŠÚ SR), publishing election-statistics datasets under uznesenie vlády SR č. 59 z 11. februára 2015 (Open Government Partnership action plan for Slovakia).
- Verified coverage list: European Parliament elections 2004–2024 (EP), National Council SR elections 1994–2023 (NR SR), self-governing region elections 2001–2022 (OSK), municipal elections 2002+ (OSO); the site nav ("Voľby a referendá") also lists referendums.
- Verified structure: per-election CSV file lists with granularity tiers SR / kraje / územné obvody / okresy / obce / okrsky, including "Územné členenie" tables that carry municipality codes and can join elections data to OpenSK geography datasets.
- Formats: CSV (some companion XLS). Sizes: most files are small; some preferential-vote or okrsok-level files are very large (a preferential-vote CSV around 1.5 GB was observed) — the spike must bound file selection carefully.
- Open questions for the spike: explicit licence wording is not visible on the index page (the OGP resolution is the publication basis; confirm during spike whether ŠÚ SR attaches explicit reuse terms); CSV encoding is reported as Windows-1250/CP1250 — verify on import; whether per-election file links are stable enough for reproducible acquisition documentation.

### A.10 Sources already tracked as blocked/research-only

No change in 2026 Q4: RPO (acquisition gate), VAT/DPH (privacy gate), ŽRSR (acquisition), Register adries (acquisition), NCZI healthcare (acquisition/reuse/privacy), institution-level schools MŠVVaM/RIS/CVTI (multiple gates), Ministry court decisions (reuse/privacy), ÚVO national procurement distribution (not found). See `docs/source-compliance.md` for the live matrix.

## Part B — Council Synthesis

The full record lives in `docs/research/roadmap-council-notes.md`. Applied consequences:

1. Sequencing is compliance-first: outreach now, trust surface next, elections spike after that, elections production only if the spike passes licence/encoding/join checks.
2. The portal-verified PortalVS deadline (2026-10-31) makes a mirrored final snapshot a formal contingency; if the licence answer is negative, removal is planned as one graph-aware change with a staged deprecation window (contested decision, resolved as E-plan with D-window).
3. No promotion of the service while PortalVS redistribution is unresolved; no personal-data endpoints ever; no scraping; no procurement automation before TED wording is retained.

## Part C — Next Three Milestones

### Milestone 1: Ask & Evidence (recommended next)

Scope:

- Send the three outreach messages in `docs/research/source-licence-outreach.md` (PortalVS, NBS banks, telecom). Human-sent, from the maintainer's address.
- Retain exact wording for Eurostat CC BY 4.0, TED legal notice, NBS disclaimer, Slov-Lex § 5 písm. b) citation, MŠVVaM CC BY (resolve version via DCAT), in `docs/research/source-verification-evidence.md`.
- Align `docs/source-compliance.md` and `data/sources.json` with retained evidence in the same commit per reply.
- Download and archive a final PortalVS snapshot (classifiers 9, 10, 42 and their `ciselniky2` equivalents) before 2026-10-31 as contingency; record acquisition provenance in `docs/import-pipeline.md` terms.

Exit criteria: three messages sent; evidence doc has exact retained wording for every non-PortalVS Yellow row; contingency snapshot archived with provenance; compliance matrix reflects replies where received.

### Milestone 2: Trust Surface

Scope:

- ETag/Last-Modified caching headers for static dataset endpoints (if-modified-since round trips), with tests.
- Curated `/v1/sources` view (hand-maintained projection of `data/sources.json` compliance fields; not a raw internal dump).
- Rate-limiting contract documented in `docs/api-contract-v1.md`-style terms, then implemented (by-IP token bucket or host platform limits documented honestly).
- Ops hygiene: deduplicate CI workflow jobs, add Dependabot, add a scheduled daily public smoke test against Render, add a monthly source-health check action (link checks on source URLs and licence pages).

Exit criteria: conditional-request tests pass; `/v1/sources` documented with curated-field disclaimer; rate-limit behavior documented and tested; CI/Dependabot/scheduled smoke running.

### Milestone 3: Elections Spike

Scope (bounded; spike, not production):

- Choose one election with modest file sizes (recommended: NR SR 2023, obce-level results plus "Územné členenie" table).
- Verify on import: encoding (expected CP1250/Windows-1250), delimiter/format stability, municipality-code join rate against `data/municipalities.json`, aggregate sanity (turnout sums at SR tier vs tiers below).
- Verify licence: locate explicit ŠÚ SR reuse terms for the datasets (publication basis is the OGP resolution; confirm wording) or add ŠÚ SR to the outreach set.
- Produce a go/no-go decision record for a production `/v1/elections/*` surface; spike output is analysis plus import prototype, no public endpoint in the spike milestone.

Exit criteria: documented spike findings (encoding, join rate, sizes, licence wording), import prototype in `scripts/` (offline, dry-run-first), decision record for production promotion.

## Part D — Data Backlog (ranked)

Scores: Value (1–5 developer/consumer value), Licence (confirmed/adequate/pending/blocked), Privacy (risk none/low/high), Effort (S/M/L), Verdict. Verdicts: NEXT / AFTER-M1..M3 / GATED / WATCH / BLOCKED / REJECTED.

| # | Domain | Value | Licence | Privacy | Effort | Verdict | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Elections results (ŠÚ SR) | 5 | pending-explicit (OGP publication basis verified) | none (aggregates) | M | NEXT | Milestone 3 spike, then production if spike passes. |
| 2 | Companies/RPO improvement | 5 | CC BY 4.0 identified for API docs, acquisition gate failed | high (natural persons in register) | L | GATED | Seed-backed lookup stays; expansion needs acquisition+privacy passes. |
| 3 | CRZ contracts (central register) | 4 | unverified | high (contract content, personal data) | L | GATED | Rejected as procurement drop-in; revisit only with privacy gate resolution. |
| 4 | ITMS EU funds | 3 | needs capture | low | M | WATCH | Candidate after Milestones 1–3 if licence evidence is clean. |
| 5 | ŠÚKL medicines | 3 | unstated | low | M | WATCH | Licence wording not found; capture before any spike. |
| 6 | NBS/ECB rates + business-days calculator | 3 | NBS disclaimer applies (A.2/A.3) | none | S | AFTER-M2 | Natural extension once NBS wording is retained; rates change daily → materialized snapshot design needed. |
| 7 | Slov-Lex legislation metadata | 3 | § 5 písm. b) exclusion (A.5) | none | M | AFTER-M3 | Metadata-only catalogue (act numbers, titles, effective dates); retention rule: attribution to Slov-Lex. |
| 8 | Court-decision metadata | 4 | reuse unverified (0.22.0 research) | high until metadata-only projection approved | L | GATED | Stays research-only; see `docs/research/court-decisions-source.md`. |
| 9 | Healthcare facilities (NCZI NR PZS) | 4 | blocked | high | L | BLOCKED | No record-level non-scraping source with reuse rights verified. |
| 10 | Institution-level schools (MŠVVaM/RIS/CVTI) | 4 | blocked | medium | L | BLOCKED | Aggregate counts remain the only school surface (`/v1/school-facility-counts`). |

Rejected this cycle: VAT/DPH endpoint (privacy gate), CRZ as procurement replacement (privacy), personal-data endpoints (unconditional), scraping-derived datasets (unconditional).

## Part E — Operations & Quality Backlog (ranked)

| # | Item | Category | Priority | Note |
| --- | --- | --- | --- | --- |
| 1 | Licence outreach + evidence retention | compliance | P0 | Milestone 1; unblocks Red rows, tightens Yellow rows. |
| 2 | `/v1/sources` curated view | trust/API | P1 | After evidence round; curated fields only. |
| 3 | ETag/Last-Modified caching + fix any dynamic-date metadata so conditional requests are meaningful | reliability | P1 | Part of Trust Surface; responses should be byte-stable per dataset version. |
| 4 | CI job deduplication + Dependabot | CI | P1 | Cheap, immediate. |
| 5 | Scheduled daily public smoke test (against Render) | CI/ops | P1 | Catch deploy drift; smoke script already supports the checks. |
| 6 | Monthly source-health action (source/licence URL checks) | ops | P2 | Detects upstream page moves (e.g., PortalVS migration) early. |
| 7 | Rate limiting: contract doc, then implementation | API/ops | P1 | Consensus: required before any public launch/promotion. |
| 8 | Typed OpenAPI response models | DX | P2 | Improves generated docs and future SDKs (SDK itself deferred). |
| 9 | Version single-sourcing | DX/ops | P2 | One authoritative place for the project version (currently repeated in app/tests/smoke). |
| 10 | Contributor guide for adding a dataset domain | DX | P2 | Encoding the existing gates (licence, privacy, offline import, validation, referential integrity, tests). |
| 11 | Storage review triggers document; SQLite spike only when triggers fire | architecture | P3 | Keep materialized-JSON architecture until documented triggers (dataset size, write-amplification, query load) are met. |

## Part F — Effect On This Repository (0.23.0)

- New docs: this report, the council notes, the outreach package, `docs/roadmap.md`.
- Updated docs: README/CHANGELOG/versioning/release-readiness/privacy-review/1-0-readiness-audit milestone references; compliance, limitations, data-sources, 1-0-scope, verification-backlog notes reflecting A.1–A.9.
- No new endpoints, datasets, importers, or runtime changes.
- Project version `0.22.0` -> `0.23.0`; `/v1` namespace and response `metadata.version == "v1"` unchanged.

## Appendix — Directly Verified URLs

- `https://ciselniky.portalvs.sk/` — legacy classifier portal with 31.10.2026 end-of-support banner.
- `https://ciselniky2.portalvs.sk/` — IS Číselníky successor REST API (JSON/XML/CSV).
- `https://volby.statistics.sk/tree.html` — ŠÚ SR elections download index ("Údaje na stiahnutie").
- NBS website legal disclaimer (wording retained in A.2); NBS holidays page; telecom regulator numbering page; Slov-Lex static text of Vyhláška 9/2009 Z. z.; Eurostat reuse policy; TED legal notice; MŠVVaM dataset page. Exact URLs and wording land in `docs/research/source-verification-evidence.md` during Milestone 1.
