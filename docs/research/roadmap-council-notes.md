# Roadmap Council Notes

This document records the multi-perspective roadmap review held during the 0.23.0 milestone. Reviewers covered data licensing, privacy, API product, operations/CI, developer experience, architecture, and sceptical risk review. Verdicts are grouped by strength. This is a decision record, not legal advice.

Companion documents:

- `docs/research/opensk-research-roadmap-2026-q4.md` — the full research report this council reviewed.
- `docs/roadmap.md` — the living roadmap where verdicts are applied.
- `docs/research/source-licence-outreach.md` — the outreach packages that implement the top consensus verdict.

## Consensus (all reviewers aligned)

1. Licence outreach with evidence retention is the next action, and messages are dispatched by the human maintainer, never automatically. This unblocks the Red compliance rows (PortalVS) and tightens the Yellow rows.
2. Elections data is the next data spike: official ŠÚ SR CSV exports exist at `volby.statistics.sk`, published under the OGP open-data initiative (government resolution 59/2015), covering EP 2004–2024, NR SR 1994–2023, OSK 2001–2022, OSO 2002+, with granularity down to okrsok and municipality code tables for joining. A bounded spike (one election, one granularity) is appropriate and privacy-safe (aggregate counts, no personal data).
3. Materialized-layer architecture stays: runtime routes read checked-in local JSON only; no upstream calls from API routes; imports remain offline and reviewed.
4. Stay on JSON (no CSV/NDJSON sibling formats now). Keep one response envelope.
5. Rate limiting is required before any public launch/promotion, written down as contract first, implemented second.
6. ETag/Last-Modified caching posture is the correct HTTP-cache direction for static dataset endpoints.
7. Ops hygiene bundle: deduplicate CI jobs, add Dependabot (or equivalent) for dependency updates, add a scheduled daily public smoke test against Render.
8. `docs/roadmap.md` becomes the strategic source of truth for direction; `docs/api-status.md` remains the endpoint-status surface; `docs/1-0-scope.md` remains the candidate 1.0 scope.
9. Versioning stays on 0.X.Y milestones until an intentional 1.0. No renumbering.
10. Positioning: the project is a public, honest, source-verified reference API, not an official government endpoint; trust wording (provenance, partial coverage flags, licence status) is a feature.
11. SDK/client libraries are deferred; OpenAPI correctness and docs come first.
12. A custom domain is desirable before public launch but is not a current blocker; keep `onrender.com` deployment honest in docs.
13. No promotion/advertising while the PortalVS redistribution question is unresolved.

## Majority (supported, with recorded dissent or conditions)

1. `/v1/sources` endpoint: build a curated, hand-maintained view of source/licence status (from `data/sources.json` plus compliance docs) after the outreach evidence round strengthens the underlying data. Dissent/conditions: do not auto-expose raw compliance internals as an API guarantee; the endpoint is a curated snapshot, versioned with the same care as datasets.
2. Companies/IČO: demote-but-keep the seed-backed lookup (explicit `SEED` wording everywhere), rather than deleting it or pretending RPO coverage. Production RPO expansion stays gated behind the acquisition gate.
3. Procurement: freeze the surface at the 100-record TED_PARTIAL snapshot. Do not expand procurement automation (scheduled refreshes, larger snapshots, ÚVO replacement) before exact TED attribution wording is retained and the ÚVO national distribution question is answered. Lower marginal value than licence/trust work.
4. NCZI (healthcare) and CVTI/RIS (institution-level schools) stay in WATCH: sources are identified but blocked on acquisition/reuse/privacy gates; no new probing work is scheduled for them this quarter.

## Contested (recorded disagreement, decision taken with dissent preserved)

1. PortalVS removal order if the licence answer is negative or never arrives.
   - Position D (staged): keep the datasets and routes live with stronger warnings while awaiting a reply; remove only after a documented cutoff date; migrate to a mirrored final PortalVS snapshot taken before the 31.10.2026 end-of-support date if the old API disappears first.
   - Position E (all-or-nothing, graph-aware): districts, municipalities, and PSC form one referential graph (PSC -> municipality -> district -> region; phone areas and school facility counts join into the same codes), so removing one tier breaks referential integrity for several other datasets; removal should be planned as one coordinated change across routes, datasets, tests, and docs.
   - Decision recorded for 0.23.0: proceed with outreach first (consensus item 1). If the answer is negative, plan removal as a single coordinated graph-aware change (position E) with a staged public deprecation window (position D) before deletion. The healthy scepticism raised during review about whether a hard PortalVS deadline existed was resolved by direct verification of the banner ("Podpora doterajšieho systému končí 31.10.2026."); the deadline is real, so the contingency plan must include a mirrored final snapshot.

## Rejected (considered and explicitly declined)

1. Building the VAT/DPH endpoint first: rejected because the privacy gate (no deterministic natural/legal person discriminator in the source XML) is unresolved; licence clarity does not fix privacy.
2. CRZ (central register of contracts) as a drop-in replacement or major expansion of procurement: rejected pending the privacy gate on contract content and because it does not answer the ÚVO national-notice question.
3. Expanding or automating procurement fetches before exact TED attribution wording is retained: rejected as compliance-first sequencing.
4. Personal-data endpoints (names, statutory organs, individuals): rejected unconditionally.
5. Scraping any human-facing portal (ORSR, ŽRSR, NCZI search screens, RIS screens) for runtime data: rejected; matches long-standing repo rule "do not scrape".
