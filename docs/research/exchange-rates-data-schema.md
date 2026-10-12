# Exchange-rates data/schema spike: ECB eurofxref feeds and SDMX API

Verified **2026-10-11** (retrieval window 21:27:46–21:28:50 UTC, i.e. 23:27–23:28 CEST), for the OpenSK 0.23.3 spike, agent B (data/schema/import). All values below were re-typed from `measurement-report.txt` and the importer runs against the actual downloaded bytes; nothing was estimated from documentation. Raw downloads live only in `C:\Users\matej\AppData\Local\Temp\opencode\exchange-rates\` (`*.body` + `*.headers`), never in the repo. This is acquisition/schema research plus an offline importer prototype — not a production dataset, endpoint, or licence clearance. ECB/NBS licence wording is owned by agent A.

**Terms quick-check before scripted downloads (agent B check, not clearance):** the ECB "Disclaimer & copyright" page (<https://www.ecb.europa.eu/services/disclaimer/html/index.en.html>, fetched 2026-10-11) states users "may make free use of the information obtained directly from it" subject to source attribution to the ECB, accurate reproduction, explicit marking of modifications, and free-of-charge notice rules for paid redistribution. **No anti-automation/robots clause was found** on that page; downloads therefore proceeded. One **disclaimer finding** worth retaining: the ECB explicitly disclaims all liability for reliance on the published euro foreign exchange reference rates (same page, "Disclaimer" section). Exact reuse wording retention for production remains agent A's task.

## Task 1 — official source bytes

| Artifact | URL | HTTP | Content-Type | Bytes | SHA-256 (hex) |
| --- | --- | --- | --- | --- | --- |
| daily | `https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml` | 200 | `text/xml` | 1,547 | `cf79007a1de55aea7158681ed3731e72ae15f80a92a916d7e0eb32f5640142cd` |
| hist-90d | `https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml` | 200 | `text/xml` | 70,586 | `9be8fea98155a0897b7f933e982d7b5129a35369173fdd580a6d09f3369e6f5f` |
| hist (full) | `https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.xml` | 200 | `text/xml` | 8,196,871 | `7ddf0f32a828b2b4778e4200389a2cd6cdb63e685b9477be256a732e9e771e9d` |
| SDMX data (default) | `https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A?lastNObservations=5` | 200 | `application/vnd.sdmx.genericdata+xml;version=2.1` | 3,353 | `ae724f0f6dfe2a9b9961109aad436be6c7534e769fc411f88a1bdf30159c9c84` |
| SDMX data (CSV via `Accept: text/csv`) | same | 200 | `text/csv` | 1,366 | `00a3346c3729a25457a47ec7c9b6dc64ae73da0b2623567df852f8aba6f7ee39` |
| SDMX data (JSON via `Accept: …data+json;version=1.0.0-wd`) | same | 200 | `application/vnd.sdmx.data+json;version=1.0.0-wd` | 3,644 | `972d07fb91061cd589c2363e40034f19447a3c7cfb44c9e1e49d017ea99b251d` |

SDMX content-negotiation note (measured, not assumed): `Accept: application/vnd.sdmx.data+json;version=1.0.0` returns **HTTP 406** with an `application/problem+json` body listing acceptable versions; only `1.0.0-wd` / `1.0.0-cts` JSON and `text/csv` (plus `application/vnd.ecb.data+csv;version=1.0.0`, untested) are accepted. The CSV contains one row per observation (`OBS_STATUS=A, OBS_CONF=F` for all five sampled days) and matches the XML feed values exactly (e.g. 2026-10-09 USD=1.1206).

### eurofxref XML structure (all three files share it)

- XML declaration `<?xml version="1.0" encoding="UTF-8"?>`; **UTF-8, no BOM**. Single quotes for attributes in `eurofxref-daily.xml`, **double quotes** in the two history files — parsers must not key on quote style.
- Root `gesmes:Envelope` with `xmlns:gesmes="http://www.gesmes.org/xml/2002-08-01"` and default namespace `http://www.ecb.int/vocabulary/2002-08-01/eurofxref`. Children: `gesmes:subject` = `Reference rates`, `gesmes:Sender/gesmes:name` = `European Central Bank`, then exactly one outer `Cube` containing date cubes.
- Date cube: `<Cube time='2026-10-09'>`; rate rows: `<Cube currency='USD' rate='1.1206'/>` (self-closing, exactly two attributes).
- **Decimal representation**: unsigned decimal ASCII, 0–6 decimal places in the full history (histogram over all 221,267 rows: 0 dp: 3,942; 1 dp: 5,858; 2: 32,102; 3: 40,510; 4: 134,972; 5: 3,867; 6: 16). Integer lexemes occur (e.g. `rate="137"`). Max lexeme length 8 characters. **1,281 rows carry a trailing zero** (e.g. `136.80`) whose lexical form would be lost if parsed to float. **Anomaly**: the daily feed pads trailing zeros (`ISK rate='136.80'` on 2026-10-09) while the history feeds do not (`rate="136.8"` for the same date) — same numeric value, different bytes. Cross-feed dedup must compare numerically, not lexically.
- **Dates**: strict `YYYY-MM-DD`. On-disk order in hist/hist-90d is strictly descending (latest first).
- **Currency identifiers**: ISO 4217 alpha-3 uppercase. Per-date order is not alphabetical — it is a stable publishing order starting `USD, JPY, …`; **16 distinct per-date orderings exist** across the 7,111 date cubes (two dominant ones), so deterministic output must sort keys.
- **Duplicates**: none. Zero duplicate date cubes; zero duplicate currency rows within a date (asserted over the full history).
- **Missing-rate semantics**: a currency is simply absent before its debut / after its removal; there are no placeholders, nulls, or empty rows. Per-date currency counts over the full history range 27–35 (distribution: 27: 398 dates, 28: 1,201, 29: 198, 30: 766, 31: 1,005, 32: 1,300, 33: 1,296, 34: 497, 35: 450).
- **Direction semantics**: `1 EUR = rate units of the foreign currency`; **EUR never appears as a listed currency** in any of the 7,111 dates (verified). 29 currencies on the latest date; 41 distinct codes across the full history (legacy codes CYP/EEK/LTL/LVL/MTL/SIT/SKK, redenominations TRL→TRY 2005-01-03 and ROL→RON 2005-07-01, RUB last published 2022-03-01, BGN last published 2025-12-31 — Bulgaria adopted the euro 2026-01-01; BRL/MXN joined 2008-01-02, INR 2009-01-02, ILS 2011-01-03).

### Record counts and sanity check

| Feed | Dates | Rate rows | Earliest | Latest | Currencies (latest date) |
| --- | ---: | ---: | --- | --- | ---: |
| daily | 1 | 29 | 2026-10-09 | 2026-10-09 | 29 |
| hist-90d | 65 | 1,885 | 2026-07-13 | 2026-10-09 | 29 |
| hist (full) | 7,111 | 221,267 | **1999-01-04** | **2026-10-09** | 29 |

Sanity ranges on latest date 2026-10-09, all OK: USD=1.1206 ∈ [0.5, 2.0]; GBP=0.84763 ∈ [0.5, 1.5]; CZK=24.369 ∈ [15, 45]; PLN=4.3835 ∈ [2.5, 7]; HUF=365.08 ∈ [250, 600]; CHF=0.9313 ∈ [0.7, 1.3].

**BGN precision finding (important):** the premise "BGN is always the fixed 1.9558" does **not** hold over the full history: 105 distinct BGN rates occur from 2000-07-19 (`1.9469`) onward, converging to `1.9558`; the final 2025-12-31 value is exactly `1.9558`. Precision must therefore be preserved as a general property (keep source lexemes / `Decimal`), not as a BGN-specific constant check.

## Task 2 — size measurement (real bytes, actual full-history file)

Per-date map `{"date", "base": "EUR", "rates": {...}}` with Decimal-as-string values, UTF-8, sorted keys, compact separators, serialized from the actual parsed history:

| Scope | Dates | Rows | Compact UTF-8 bytes | KiB/MiB |
| --- | ---: | ---: | ---: | --- |
| latest-only | 1 | 29 | 590 | 0.6 KiB |
| 1 year | 256 | 7,482 | 125,020 | 122.1 KiB |
| 5 years | 1,281 | 38,651 | 642,828 | 627.8 KiB |
| full history (1999-01-04 → 2026-10-09) | 7,111 | 221,267 | 3,649,598 | 3.48 MiB |

**Conclusion: JSON_CONTINUE.** Even the full 27-year history materializes to ~3.5 MiB compact JSON (≈6.15 MB with the repository's `indent=2` preview style, as confirmed by the prototype run below) — comfortably within the house materialized-JSON pattern. **SQLite is not justified by row count.**

## Task 3 — importer prototype

`scripts/import_exchange_rates.py` (offline; explicit `--source PATH=URL` inputs; dry-run default; `--write-preview` writes only into `data/generated/`, which is already `.gitignore`d) and `tests/test_import_exchange_rates.py` (49 tests, all passing; full suite 378 passed). Strict validation: gesmes envelope/subject/sender, single outer Cube, strict ISO calendar dates, ISO-4217 uppercase codes, EUR never listed, unsigned-decimal positive rates, DTD/entity declarations rejected, input size bound, numeric cross-feed duplicate check (conflicting duplicates fail; value-equal duplicates are counted as skipped), deterministic sorted serialization, source SHA-256 + URL + `--retrieved-at` recorded into preview metadata.

Importer run against the real downloads (three feeds, retrieved 2026-10-11):

- Dry-run (full history only): **ok=true in ~1.9 s** (Python 3.14.5, includes parsing 8.2 MB XML); merged 7,111 dates, 221,267 rows, 0 skipped duplicates, preview 6,154,376 bytes (indent=2), preview SHA-256 `b06aa749554f6a64dceda1eece62846dae620af201060c2828c2b20cf70d7314`.
- `--write-preview` (hist + 90d + daily): **ok=true in ~1.9 s**; 1,914 consistent cross-feed duplicate rows skipped (1,885 + 29), **0 conflicts** — including the `136.80` vs `136.8` trailing-zero case, which passes as value-equal. Preview written only to `data/generated/exchange_rates_preview.json` (gitignored): **6,155,292 bytes, SHA-256 `cbcb84ba36d8b2c2ee68502de44e47127935c87ff7686fcaffd163b1e69b6d47`** (matches the on-disk hash exactly).

## Task 4 — business-day interaction (factual note, no fallback implemented)

Measured over the full history (7,111 published dates, 1999-01-04 → 2026-10-09):

- **Zero weekend publication dates.** ECB never publishes on Sat/Sun in this dataset.
- **134 weekday dates are missing, in 90 gaps**, each 1–2 weekdays long (histogram: 46 single-day, 44 two-day events). Missing-date weekday histogram: Monday 44, Friday 42, Tue/Wed/Thu 16 each. 3–6 missing dates per year (range 1–7).
- Every recent gap matches a **TARGET closing day**: 1 Jan, Good Friday + Easter Monday (e.g. 2026-04-03 and 2026-04-06), 1 May (2026-05-01), 25–26 Dec. The single extra 1999-12-31 gap is the millennium closing day.
- Consequently the latest publication date can lag "today" by up to 4 calendar days (e.g. retrieval on Sun 2026-10-11 → latest date Fri 2026-10-09). Any "latest rates" endpoint must expect as-of dates, not "today". Fallback semantics (weekend/holiday carry-forward) are **not** implemented anywhere in this spike.
