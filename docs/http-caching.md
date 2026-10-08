# HTTP Caching

OpenSK responses are computed from checked-in deterministic JSON datasets, so HTTP conditional caching is safe and cheap. This document records the policy implemented in 0.23.1.

## ETag Strategy

- Dataset and meta GET responses carry a strong validator: `ETag: "<sha256(body)[:32]>"`.
- The hash is computed over the exact response body bytes. Because bodies are derived only from checked-in deterministic JSON, identical requests produce byte-identical bodies, so ETags are stable across process restarts without any clock, random value, or upstream call.
- `If-None-Match: <etag>` (or `*`) returns `304 Not Modified` with an empty body and the same validator headers.
- Error responses (4xx/5xx) intentionally do not carry ETags. `/v1/health` is excluded because its timestamp legitimately changes per request.

## Last-Modified Strategy

- `Last-Modified` uses the semantic per-dataset freshness date (the `*_LAST_UPDATED` constants), rendered as midnight UTC of that date — never the deployment time and never "now".
- Routes without a semantic dataset date (root, `/v1/companies*`, `/v1/ico*`) get no `Last-Modified` header at all rather than a fabricated one.
- `If-Modified-Since` returns `304` when the dataset date is not newer than the supplied date.

## Cache-Control Policy

| Category | Routes | Policy | Rationale |
| --- | --- | --- | --- |
| Static lists/details/stats/utilities | all dataset list, detail, stats, lookup, IBAN, business-days, and sources routes | `public, max-age=86400` | Content changes only on dataset releases (days to months). |
| Search | `/v1/psc/search`, `/v1/phone-areas/search`, `/v1/vehicle-registration-codes/search`, `/v1/procurement-notices/search` | `public, max-age=900` | Query-shaped traffic; shorter lifetime limits stale-search windows. |
| Meta | `/` | `public, max-age=3600` | Stable metadata; cheap to revalidate anyway via ETag. |
| Health | `/v1/health` | `no-store` | Live check must never be served from cache. |

Error responses keep the route-level `Cache-Control` they already carried; the middleware does not modify them.

## Implementation Notes

- Implemented as `ConditionalCachingMiddleware` (`services/http_cache.py`) so dataset routers needed no per-route rewrites; routers continue to own their `Cache-Control`.
- Byte-stability precondition: root and error envelopes no longer embed `date.today()` in `metadata.lastUpdated` (it is `null` when no dataset is involved). `docs/api-contract-v1.md` documents the nullable field.
- No Redis, no cache storage, no database: HTTP semantics only.
