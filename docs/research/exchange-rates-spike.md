# 0.23.3 — Exchange Rates Spike & Source Resilience

Verified 2026-10-11. Candidate domain: **ECB euro foreign exchange reference rates** as a future OpenSK snapshot dataset. This is a research/tooling milestone, not production implementation.

**NO PUBLIC EXCHANGE-RATE ENDPOINT IS ADDED. No production exchange-rate dataset was created. No public elections endpoint was added.**

## 1. Executive summary

**Decision: GO_PRODUCTION_NEXT.** The ECB reference-rate domain passes every production gate the spike was asked to check: authoritative publisher, explicit written reuse permission with attribution, machine-readable feeds that are the publisher's intended consumption mode, a deterministic offline importer with strict validation, zero personal data, a stable 27-year schema, and a measured storage footprint that comfortably fits the materialized-JSON architecture.

Recommended next milestone: **0.23.4 — Exchange Rates Production Surface**.

**PortalVS verdict: SUCCESSOR_COMPATIBLE_WITH_TRANSFORM_CHANGES** (see `docs/research/portalvs-source-resilience.md`): all three current PortalVS-backed datasets can be rebuilt from the successor IS Číselníky API with offline transform changes only — no public contract change forced. Legal permission remains pending (`SENT_AWAITING_REPLY`); technical compatibility does not resolve it.

## 2. Product question

Can OpenSK add a small, useful, trustworthy EUR reference-rate API using official sources without runtime upstream calls? Concretely: date-aware official reference rates for Slovak developers doing historical EUR conversions, accounting/reporting utilities, and rate widgets — with honest "information purposes only" framing.

Explicit non-goals recorded for any future contract: this API is **not** real-time FX, **not** executable/tradable prices, **not** card-network rates, **not** guaranteed bank settlement rates, **not** investment advice, and **not** a replacement for regulated accounting guidance. No reciprocal-conversion engine, crypto, stocks, or generic finance framework.

### Fit with OpenSK positioning

OpenSK is "one consistent developer interface to Slovakia's fragmented public data." ECB reference rates are EU-level, not Slovak-specific — but they match the existing proven pattern of EU sources relevant to Slovakia (Eurostat regions, TED procurement notices). NBS merely republishes the ECB feed (§4), so there is no Slovak official hop to preserve, and Slovak developers working with EUR conversions (CZK/PLN/HUF trade, payroll, historical invoicing) are a plausible audience. Demand evidence is qualitative, not measured — the production milestone should ship the minimal surface first rather than an analytics platform.

## 3. Sources investigated

| Source | Verdict | Evidence |
| --- | --- | --- |
| European Central Bank — eurofxref feeds (daily / 90-day / full history) | **Preferred source; CLEAR rights** | `docs/research/exchange-rates-source-verification.md`, `docs/research/exchange-rates-data-schema.md` |
| ECB Statistical Data Portal — SDMX 2.1 API (dataset EXR) | Viable alternative; heavier client surface | same |
| National Bank of Slovakia | **Republication only — rejected as canonical** | NBS XML retains the ECB gesmes/eurofxref namespace; CSV values match ECB daily exactly; no post-euro NBS rate concept of its own |

No commercial aggregators, card networks, or unofficial mirrors were considered.

## 4. Preferred source

**ECB eurofxref XML feeds.** Reasoning over alternatives: the feeds are single-file, versionless-but-dated snapshots requiring minimal client logic (one HTTPS GET, no content negotiation), while the SDMX API (verified working, dataset `EXR`, e.g. `D.USD.EUR.SP00.A`) requires vendor media types (`text/csv` accepted; standard `application/vnd.sdmx.data+json;version=1.0.0` is rejected with 406 — only `1.0.0-wd`/`1.0.0-cts`) and a much richer parser. The API remains a documented fallback. NBS is excluded as canonical because it adds no data (verbatim mirror) and its no-modification wording would be awkward for transformation anyway.

## 5. Exact provenance

Publisher: **European Central Bank, Frankfurt am Main, Germany** (per its own copyright wording). Human page: `https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html`. Machine feeds (all live-checked 2026-10-11, HTTP 200 `text/xml`):

| Feed | URL | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| daily | `…/stats/eurofxref/eurofxref-daily.xml` | 1,547 | `cf79007a1de55aea7158681ed3731e72ae15f80a92a916d7e0eb32f5640142cd` |
| 90-day | `…/stats/eurofxref/eurofxref-hist-90d.xml` | 70,586 | `9be8fea98155a0897b7f933e982d7b5129a35369173fdd580a6d09f3369e6f5f` |
| full history | `…/stats/eurofxref/eurofxref-hist.xml` | 8,196,871 | `7ddf0f32a828b2b4778e4200389a2cd6cdb63e685b9477be256a732e9e771e9d` |

Retrieval 2026-10-11 21:27–21:28 UTC. Latest observation 2026-10-09; earliest 1999-01-04. Raw bytes, headers, and the measurement report live only in the approved temp dir (`C:\Users\matej\AppData\Local\Temp\opencode\exchange-rates\`); no raw upstream file is committed.

## 6. Licence/reuse evidence

Retained verbatim wording: `docs/research/exchange-rates-source-verification.md` §1.2–1.3, from the official **"Disclaimer & copyright"** page (checked 2026-10-11). In summary, ECB grants that "users of this website may make free use of the information obtained directly from it" subject to four conditions:

1. accurate reproduction/distribution with **"the ECB must be cited as the source"**;
2. commercial redistribution must disclose that the information is available free of charge (not applicable to OpenSK's free API);
3. **modifications must be stated explicitly** (our JSON normalization will be);
4. no framing of the ECB site.

Plus the mandatory product notices from the reference-rates page: rates are "published for information purposes only. Using the rates for transaction purposes is strongly discouraged", updated "around 16:00 CET every working day, except on TARGET closing days"; ECB accepts no liability for reliance.

**Verdict: CLEAR** (confidence high). Residual documented ambiguities (not blockers): sui-generis database right not addressed in the wording (low practical risk; optional outreach draft ready, unsent), no published numeric API rate limits, revision policy undocumented, no verified data.europa.eu DCAT entry. Notably absent — unlike the elections source — is any robot/automation prohibition; robots.txt has `Crawl-delay: 5` etiquette only.

## 7. Acquisition workflow

Approved pattern (unchanged architecture): manual or scripted **offline** download of one feed file (single GET), optionally ETag/refresh only inside the maintainer workflow — never at request time. ECB's own "All data services" page describes feeds/SDMX/RSS/MID as structured for automatic processing, so automation is the intended consumption mode. Daily upstream cadence vs OpenSK snapshot cadence is a production decision; a per-day-fetch-then-materialize workflow with source SHA-256 recorded is the importer's model. The importer always takes explicit local paths; no fetcher was written and none is needed for the first production cut (manual download is seconds).

## 8. Source format

Measured (`docs/research/exchange-rates-data-schema.md`): **UTF-8, no BOM**, `gesmes:Envelope` XML (`gesmes:subject` = `Reference rates`, sender `European Central Bank`, ECB `eurofxref` default namespace, nested `Cube` elements with `time`/`currency`/`rate` attributes). Dates `YYYY-MM-DD`, descending file order; ISO-4217 uppercase codes in a non-alphabetical publishing order (16 distinct orderings across history → deterministic output must sort). Rates are unsigned decimals, 0–6 places (integers like `137` occur; 8-char max lexeme; 1,281 trailing-zero lexemes). Daily feed pads trailing zeros (`136.80`) where history feeds use `136.8` — dedup must be numeric. No nulls/placeholders: absent currency = not published for that date. Direction: `1 EUR = rate units of foreign currency`; **EUR never appears** as a listed currency.

## 9. Update cadence

"around 16:00 CET every working day, except on TARGET closing days" (concertation ~14:10 CET). Measured: zero weekend publications in 27 years; 134 missing weekdays in 90 gaps (all TARGET closings; 3–6 per year typical). Freshness can lag real time by up to 4 calendar days (Sunday fetch → Friday rates). Production must treat the dataset as as-of publication dates, never "now".

## 10. Currency coverage

29 currencies on the latest date; 41 distinct codes across full history (legacy euro-area currencies CYP/EEK/LTL/LVL/MTL/SIT/SKK; redenominations TRL→TRY 2005-01-03, ROL→RON 2005-07-01; RUB last published 2022-03-01; BGN last published 2025-12-31 — Bulgaria adopted the euro 2026-01-01; BRL/MXN since 2008, INR 2009, ILS 2011). Sanity-checked USD/GBP/CZK/PLN/HUF/CHF on 2026-10-09 against plausible ranges.

## 11. Historical coverage

Full-history feed covers **1999-01-04 → present**, 7,111 publication dates, 221,267 rate rows at retrieval. latest-only / 90-day / full-history variants are offered by the same publisher and are composable (overlap deduplicates numerically: 1,914 consistent cross-feed duplicate rows, 0 conflicts).

## 12. Publication-day semantics

Rates are **publication-date** rates (concertation ~14:10 CET, publication ~16:00 CET the same TARGET day) — not effective-dated to the following day, not forward-looking. OpenSK must preserve the source date key verbatim. Weekends/holidays simply have no row; no carry-forward is implied by the source, and none is implemented.

## 13. Precision/decimal handling

Importer keeps **exact source lexemes** (`Decimal`-validated, stored as strings in JSON) — no binary floats anywhere. BGN finding: it is **not** a constant 1.9558 across history (105 distinct values since 2000-07-19, converging to the fixed rate), so precision preservation is a general property, not a BGN special case. Rounding policy: none — OpenSK reproduces source values exactly; any conversion math is explicitly client responsibility (documented in the future contract).

## 14. Normalized model

Row-set canonical form: one object per publication date `{"date","base":"EUR","rates":{CCC:"lexeme",…}}`, dates and currency keys sorted, deterministic UTF-8 serialization. Data-file metadata once per file (profile, base, direction semantics, sources with URL/SHA-256/retrieval, coverage range) rather than per-rate repetition. Evaluated and not adopted blindly: the brief's sketch matches the importer output only after adding source-evidence metadata and the `status: "unapproved-research-preview"` marker on previews. Per-date lookup is O(1) after a date→index map in the service layer; runtime cost is trivial at measured sizes.

## 15. Import prototype

`scripts/import_exchange_rates.py` + `tests/test_import_exchange_rates.py` (49 synthetic tests, offline). Properties: explicit `--source PATH=URL` inputs (repeatable), `--retrieved-at` metadata, **dry-run default**, `--write-preview` restricted to gitignored `data/generated/`, no `--dry-run`+`--write-preview` combo, production writes structurally impossible. Validation: 32 MiB input cap, DTD/entity rejection, strict gesmes envelope/sender/subject, single outer Cube, strict ISO dates/currencies, EUR-never-listed rule, positive-decimal rates, intra-file duplicates rejected, cross-feed duplicates must be numerically equal (conflicts fail), deterministic sorted serialization with source SHA-256 recorded. Measured: full-history 8.2 MB parses+validates in ~1.9 s; three-feed merge 7,111 dates / 221,267 rows, 0 errors; preview (indent=2) 6,155,292 bytes, SHA-256 `cbcb84ba36d8b2c2ee68502de44e47127935c87ff7686fcaffd163b1e69b6d47` (lead independently re-ran the dry-run with identical merged counts).

## 16. Size/storage findings

Measured compact-JSON bytes from the actual full history (Decimal-as-string): latest 590 B; 1 year 125,020 B; 5 years 642,828 B; **full 27-year history 3,649,598 B (3.48 MiB)**; 6.15 MB with the repo's `indent=2` preview style. Even full history is comparable to existing datasets (`psc.json` 1.9 MB, `phone_areas.json` 0.66 MB). **JSON_CONTINUE** — no storage review triggered; SQLite explicitly not justified by row count. Production scope choice (full history vs rolling window) is therefore a product decision, not a storage constraint.

## 17. API sketch (contract candidate only — not implemented)

- `GET /v1/exchange-rates/latest` — latest published date envelope (labelled "latest available", never "today").
- `GET /v1/exchange-rates/{date}` — exact publication-date lookup; 404 for non-publication dates (weekend/TARGET closing). A separate `?onOrBefore=` style "latest rate on or before" semantic is a **different operation** and must not be silently folded into the date lookup; decide explicitly at production.
- Optional filter `currency=USD` (trimmed honest extras: no conversion endpoints, no ranges in v1 unless paged).

Standard envelope `{data, metadata{source, lastUpdated, version:"v1"}, error}`; attribution + "information purposes only" notice in route descriptions/metadata; `metadata.lastUpdated` = dataset snapshot date of the newest included publication date; deterministic body ⇒ strong ETag, long-lived cache for historical dates, short/`no-store`-ish treatment only for the `latest` alias. Unsupported currency → 400; unsupported date → 404; before-1999 date → 404.

## 18. Business-day interaction

Publication follows the **TARGET calendar**, not the Slovak holiday calendar, and the existing OpenSK Slovak business-day utilities must **not** be reused to predict ECB publication dates (facts: Slovak-only holidays don't suppress ECB publication; 1 Jan/Good Friday/Easter Monday/1 May/25-26 Dec do; 1999-12-31 also). No fallback ("previous business day") logic is implemented or endorsed inside the data layer; clients get exact dates or an explicit "latest available" alias.

## 19. Risks/limitations

- Sui-generis database right unaddressed by ECB wording (documented, low risk; optional outreach draft in the source-verification doc, **unsent**).
- No published upstream rate limits (single daily pull is far under any sane threshold; `Crawl-delay: 5` applies to the website host).
- Revision/correction policy undocumented; reference rates appear point-in-time published. Production refresh must re-validate hash changes and treat same-date value changes as anomalies requiring review, not silent overwrite.
- Rates are informational only — the API must carry the ECB notice and never imply tradability or endorsement.
- Demand is plausible, not measured; ship the minimal surface first.
- Detector: daily feed's trailing-zero padding vs history feeds required numeric dedup (implemented, tested); BGN is not historically constant (precision preserved by lexemes).
- PortalVS transition is decoupled from this domain: no dependency either way.

## 20. Final decision

**GO_PRODUCTION_NEXT.**

All gates pass with evidence: authoritative source (ECB, high confidence), acceptable reuse rights (explicit written permission, attribution + modification-notice conditions), reproducible approved acquisition (intended machine-readable channels, no anti-automation clause), deterministic transformation (strict importer, 49 tests, reproducible merge), privacy-safe scope (pure public factual rates; no persons, credentials, or tracking data retained; NO personal-data review exceptions needed), stable 27-year schema, useful bounded product surface, and materialized JSON remaining operationally sensible (≤3.5 MiB compact full history).

**Recommended next milestone at spike time: 0.23.4 — Exchange Rates Production Surface**: production dataset wiring, minimal routes, attribution/notices, cache headers and anomaly-guarded refresh. This production work has since shipped. Outreach update: NBS bank clarification resolved 2026-10-14; PortalVS/telecom/ŠÚ SR replies remain outstanding, independent of ECB rates.

> **Production follow-up (2026-10-12, done in 0.23.4):** the recommendation above was implemented. The full-history scope was chosen (no material regression vs the 0.23.3 measurements: 6,006,060 bytes indented JSON, ~74 ms cold parse, ~23 MiB retained heap). `data/exchange_rates.json` materializes 7,112 publication dates (1999-01-04→2026-10-12; one new date since the spike) from the canonical full-history feed with `--write-production`; routes `GET /v1/exchange-rates/latest` and `GET /v1/exchange-rates/{date}` run with exact-date/no-fallback semantics and an optional `?currency=` filter; the snapshotted `latest` alias uses `max-age=3600`, exact dates `max-age=86400`; refresh is a manual offline workflow with a historical-changes/removed-dates guard (`--acknowledge-changes` escape). No outreach reply had arrived by promotion; no compliance status beyond exchangeRates changed.
