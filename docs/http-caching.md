# HTTP Caching

OpenSK's cacheable responses are computed from checked-in deterministic JSON datasets. Conditional caching reduces response transfer, not endpoint computation: the middleware receives the computed/serialized response before evaluating validators. This page records the current policy, introduced in 0.23.1.

## ETag Strategy

- Cacheable successful dataset and meta GET responses carry a strong validator: `ETag: "<sha256(body)[:32]>"`.
- The hash is computed over the exact response body bytes. Because bodies are derived only from checked-in deterministic JSON, identical requests produce byte-identical bodies, so ETags are stable across process restarts without any clock, random value, or upstream call.
- `If-None-Match: <etag>` (or `*`) returns `304 Not Modified` with an empty body and the same validator headers. GET revalidation uses weak comparison: `W/"<matching-hash>"` also matches the emitted strong ETag; a list matches if any validator matches.
- The **presence** of `If-None-Match` suppresses `If-Modified-Since` evaluation, including when the ETag does not match. A nonmatching ETag plus a future modification date returns the normal 200 response, not 304.
- Error responses (4xx/5xx) intentionally do not carry ETags. `/v1/health` and `/v1/iban/validate/{iban}` are excluded from validators and conditional 304s; both use `no-store`.

## Last-Modified Strategy

- `Last-Modified` uses the semantic per-dataset freshness date (the `*_LAST_UPDATED` constants), rendered as midnight UTC of that date — never the deployment time and never "now".
- Routes without a semantic dataset date (root, `/v1/companies*`, `/v1/ico*`) get no `Last-Modified` header at all rather than a fabricated one. Health and IBAN validation also carry no `Last-Modified`.
- `If-Modified-Since` returns `304` when the dataset date is not newer than the supplied date.

## Cache-Control Policy

| Category | Routes | Policy | Rationale |
| --- | --- | --- | --- |
| Static lists/details/stats/utilities | dataset list, detail, stats, lookup, business-days, and sources routes (except categories below) | `public, max-age=86400` | Content changes only on dataset releases (days to months). |
| Search | `/v1/psc/search`, `/v1/phone-areas/search`, `/v1/vehicle-registration-codes/search`, `/v1/procurement-notices/search` | `public, max-age=900` | Query-shaped traffic; shorter lifetime limits stale-search windows. |
| Meta | `/` | `public, max-age=3600` | Stable metadata; cheap to revalidate anyway via ETag. |
| Exchange-rate latest | `/v1/exchange-rates/latest` | `public, max-age=3600` | Snapshot-latest alias changes whenever the local ECB snapshot is refreshed. |
| Health | `/v1/health` | `no-store` | Live check must never be served from cache. |
| IBAN validation | `/v1/iban/validate/{iban}` | `no-store` | Account identifiers may be sensitive; no ETag, Last-Modified or conditional 304. |

Historical exact-date exchange-rate responses (`/v1/exchange-rates/{date}`, including
filtered variants) use the static 86400 policy: they are stable within a checked-in
snapshot. Both exchange-rate routes carry `Last-Modified` from
`EXCHANGE_RATES_LAST_UPDATED` (the newest ECB publication date in the snapshot).

Error responses keep the route-level `Cache-Control` they already carried; the middleware does not modify them.

## Implementation Notes

- Implemented as `ConditionalCachingMiddleware` (`services/http_cache.py`) so dataset routers needed no per-route rewrites; routers continue to own their `Cache-Control`.
- Byte-stability precondition: root and error envelopes no longer embed `date.today()` in `metadata.lastUpdated` (it is `null` when no dataset is involved). `docs/api-contract-v1.md` documents the nullable field.
- No Redis, no cache storage, no database: HTTP semantics only.
- Revalidation still performs local endpoint work, serialization and body hashing, and consumes rate-limit budget. It is not a response cache or a claim that conditional requests avoid repeated dataset scans.
- IBAN `no-store` does not prevent URLs appearing in client/proxy logs. Use synthetic values, not real account numbers, in examples and tests.
