# OpenSK in five minutes

NR SR 2023 aggregate results are available in 0.23.14. See
[election scope and manual-only refresh](elections.md). The hosted deployment
must include this version before the new election calls work.

**Base URL:** `https://opensk-api.onrender.com` · API prefix: `/v1`

[Try requests in Swagger](https://opensk-api.onrender.com/docs) · [OpenAPI JSON](https://opensk-api.onrender.com/openapi.json)

No key or account required. All examples below are checked against the local application and current checked-in data. The hosted deployment may lag an unmerged PR; free-tier cold starts may take a little time.

## 1. Check the service and discover coverage

```bash
curl "https://opensk-api.onrender.com/v1/health"
curl "https://opensk-api.onrender.com/v1/sources"
```

Health is operational liveness, not proof that every dataset is available. It is `no-store` and rate-limit exempt. Sources list provenance, freshness, licence status and limitations, including researched domains that have **no public data endpoint**.

### Historical election example

```bash
curl "https://opensk-api.onrender.com/v1/elections"
curl "https://opensk-api.onrender.com/v1/elections/NRSR2023/results?municipalityCode=528595"
curl "https://opensk-api.onrender.com/v1/elections/NRSR2023/parties"
```

NRSR2023 is the only supported election; 528595 is a real election-native unit
code. Results are a `data.items/count/total/limit/offset` page (default 50/max
100); exact native region/district/unit filters combine with AND. Foreign voting
is unit **599999 / Cudzina**, not a Slovak municipality. Parties are a national
25-item array; numbers are election-scoped strings, percentages exact decimal
strings, blank mandates `null`. Definitive historical results, not live reporting;
no candidate/person, precinct or municipality-party data. Small-area aggregates
may permit contextual inference with external information.

Source: Štatistický úrad SR; **CC BY 4.0**. OpenSK converts selected CSV tables
to JSON; source/licence links, attribution and manual acquisition provenance are
in `/v1/sources/elections`. **OpenSK is not an official ŠÚ SR service.**
Automated source downloading remains prohibited; code MIT is not the data licence.

## 2. Look up a postal code and its administrative matches

```bash
curl "https://opensk-api.onrender.com/v1/psc/01001"
curl "https://opensk-api.onrender.com/v1/psc/01001?include=geography"
curl "https://opensk-api.onrender.com/v1/psc?psc=01001&limit=1"
```

Keep codes as strings to preserve leading zeros. Lookup `data` contains primary fields, `matchCount` and flat `matches`; `01001` has two matches in this snapshot. The filtered collection has `items`, page `count`, matching `total`, `limit` and `offset`. **Do not assume all endpoints use that wrapper:** older lists return arrays directly.

PSC is a **partial historical local lookup**, not an address validator or a guarantee for every address in a municipality. 404 means absent locally, not legally invalid. Since 0.23.12 grouped lookup matches are flat, consistent with list/search; data/source/coverage have not migrated. [Source limitations](https://opensk-api.onrender.com/v1/sources/psc).

## 3. Resolve a municipality or bank; validate a synthetic IBAN

```bash
curl "https://opensk-api.onrender.com/v1/municipalities/528595"
curl "https://opensk-api.onrender.com/v1/banks/1100"
curl "https://opensk-api.onrender.com/v1/iban/validate/SK5409000000000000000001"
```

The municipality is Bratislava–Staré Mesto; city boroughs are administrative records. The IBAN is the repository's **synthetic checksum-valid test value**, not a payment instruction or proof of account existence. Validation returns HTTP 200 even when `data.valid` is false. OpenSK validates checksums; NBS supplies local Slovak bank-code resolution. Bank/IBAN metadata additionally retains NBS version/effective/download provenance and attribution.

## 4. Use a reference rate or business-day utility

```bash
curl "https://opensk-api.onrender.com/v1/exchange-rates/latest?currency=USD"
curl "https://opensk-api.onrender.com/v1/business-days/check?date=2026-10-08"
```

ECB rates are exact decimal **strings**: `1 EUR = rate units of USD`. `latest` means latest in the local snapshot, **not live**; informational use only, not transaction/settlement prices. Exact-date requests do not fall back to a nearby publication date. Business days use Monday–Friday minus statutory days of rest, with verified **2024–2030** coverage only; working statutory holidays stay business days (`isHoliday` can be true while `isBusinessDay` is true), and it is not a bank settlement calendar.

## Read the envelope

Successful JSON has `data`, `metadata`, and `error: null`. `data` is an object, array or page depending on the operation; Swagger documents each shape and nullable field.

- `metadata.source`: source/local dataset label; consult `/v1/sources` for provenance and reuse conditions.
- `metadata.lastUpdated`: snapshot freshness (`YYYY-MM-DD`), not request time or a promise of upstream currentness; null where no dataset applies (root/errors). Health reports today's UTC date.
- `metadata.version`: always **`"v1"`**. This is distinct from project SemVer **0.23.12** in `/` and OpenAPI; it does not change the `/v1` namespace.

## Handle errors and cache politely

```bash
curl -i "https://opensk-api.onrender.com/v1/psc/not-a-code"
curl -i "https://opensk-api.onrender.com/v1/psc/99999"
curl -i "https://opensk-api.onrender.com/v1/municipalities/528595"
```

The first two produce standard **400 `INVALID_FORMAT`** and **404 `NOT_FOUND`** envelopes: `data: null`, `metadata.version: "v1"`, and `error.code`, English `error.message`, Slovak `error.messageSk`. Branch on status/code, not message text. Other codes are operation-specific; Swagger lists them. Existing integer validation on holiday year and procurement year uses **422**, still with the OpenSK envelope. Only company routes document **503 `DATASET_UNAVAILABLE`**.

Responses advertise `ETag`, dataset `Last-Modified` where applicable, and `Cache-Control`. Save the ETag from the third request, then use it literally:

```bash
curl -i -H 'If-None-Match: "PASTE_THE_ETAG_VALUE_HERE"' "https://opensk-api.onrender.com/v1/municipalities/528595"
```

Replace the placeholder with the server's hex value (retain the quotes). A matching validator returns **304 with no body**: reuse your cached JSON instead of parsing the empty response. `If-Modified-Since` also works; ETag takes precedence. No dataset refresh occurs on a request. [Cache details](http-caching.md).

The deployed limit is **100 requests / 60 seconds / client IP**. Read `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`; on **429 `RATE_LIMITED`**, wait `Retry-After` seconds. Conditional 304 requests consume budget too. This is a process-local fixed-window guardrail, not a globally exact quota: NAT users share a bucket and restarts reset counters. Render uses its documented edge-IP resolution; off Render forwarded headers are ignored. [Full policy and enablement caveats](rate-limiting-contract.md).

## Before relying on it

OpenSK is pre-1.0. Companies are a small seed set; procurement is `TED_PARTIAL`, not national ÚVO coverage; schools are aggregate-only; vehicle codes are historical/reference abbreviations. Source reuse/compliance remains unresolved for some datasets, including PortalVS, so availability is **not permission or complete official coverage**. No SDK is promised; use the reviewed OpenAPI as integration input and [share concrete pilot feedback](developer-adoption.md).
