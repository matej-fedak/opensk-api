# Exchange-Rate Source Research (Optional Task 23)

Status: research note only. No endpoint, importer, or dataset is added in 0.23.1.

## Question

Is there a clean, official, machine-readable exchange/reference-rate source useful to Slovak developers, suitable for a future OpenSK snapshot domain?

## Findings (verified 2026-10-08)

- ECB publishes the **euro foreign exchange reference rates** on its official site: ~30 currencies quoted against EUR, updated at around 16:00 CET every working day except TARGET closing days. The page states the rates are published "for information purposes only" and using them for transactions is discouraged.
- The same ECB statistics section offers machine-readable distributions (XML reference-rate feed and the ECB Data Portal / SDMX API), suitable for offline snapshot acquisition without scraping.
- Stable identifiers: ISO 4217 currency codes with EUR base. Deterministic snapshot: one daily file per publication date; a bounded monthly or quarterly snapshot cadence is feasible.
- NBS's own website points readers to ECB reference rates for general EUR conversion purposes; the NBS website disclaimer wording (verified in 0.23.0) applies to NBS own pages. Using the ECB feed directly avoids duplicating a second central-bank hop.
- Reuse terms: ECB statistics are reusable with source attribution under the ECB legal terms; exact wording was not retained during this bounded task and **must** be captured in the evidence doc before any production work, the same way TED wording is being retained.

## Fit assessment

| Gate | State | Note |
| --- | --- | --- |
| Authoritative source | pass | European Central Bank, official statistics. |
| Machine-readable acquisition | pass | XML/SDMX feeds, no scraping required. |
| Stable identifiers | pass | ISO 4217; EUR base documented. |
| Privacy | pass | Rates are public factual data; no personal data. |
| Reuse/licence wording | pending | Retain exact ECB reuse wording before implementation. |
| Cadence design | design needed | Daily upstream vs OpenSK snapshot model; monthly/quarterly snapshot or on-release refresh must be chosen consciously. |
| Architecture fit | pass | Matches materialized-local-data pipeline; no runtime upstream calls. |

## Recommendation

Candidate: `0.23.2 — Elections Spike` is already queued; make exchange rates a candidate **after** elections spike, in a future `0.24.x` or later utility milestone, as a small bounded snapshot endpoint such as `GET /v1/exchange-rates` with explicit informational-only wording. Do not implement in 0.23.1. Before implementation: retain exact ECB reuse wording, decide snapshot cadence, and mirror the rate-limit/caching lessons from 0.23.1.
