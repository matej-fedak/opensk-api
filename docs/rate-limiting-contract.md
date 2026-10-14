# Rate-Limiting Contract

Status: **implemented since 0.23.5**. This document is the authoritative policy for the application-level rate limiter in `services/rate_limit.py`.

## Purpose

Protect the OpenSK deployment itself (a single hobby-grade Render instance) from accidental client loops, simple abusive clients, and resource exhaustion while keeping a zero-auth developer experience. It is not a product feature, billing mechanism, or identity system — **no API keys, ever**.

Rate limiting protects OpenSK only. It has nothing to do with protecting ECB, PortalVS, or any other upstream provider, because runtime requests never contact upstream sources (everything is materialized local JSON).

## Verified Platform Facts (re-checked 2026-10-12)

- Render routes **all inbound web-service traffic through Cloudflare's global network**; Layer 3/4 and obviously flooded Layer 7 attacks are mitigated at the edge automatically, for free ([Render: How Render handles DDoS attacks](https://render.com/articles/how-render-handles-ddos-attacks), [Render: DDoS protection](https://render.com/docs/ddos-protection)).
- Targeted Layer 7 traffic that looks like real requests ("API abuse, slow requests") is **explicitly the application's responsibility** — Render recommends application-level rate limiting. Render offers **no configurable per-client rate limiting** for normal inbound application traffic on web services. (Render's own API rate limits apply only to the Render *management* API at api.render.com — unrelated.)
- Render always sets `RENDER=true` in the runtime environment ([Render: Default environment variables](https://render.com/docs/environment-variables)), which OpenSK uses as its Render detection signal. Render also sets `FORWARDED_ALLOW_IPS=*` for Python runtimes by default.
- Cloudflare's request headers ([Cloudflare: HTTP headers](https://developers.cloudflare.com/fundamentals/reference/http-headers/)): `CF-Connecting-IP` is the client's IP address as seen by Cloudflare's edge, sent to the origin on every request and controlled by the edge — a client-supplied inbound value does not survive, which is why Cloudflare recommends it (or Enterprise `True-Client-IP`) for restoring the original visitor IP. Separately, if the client sent an `X-Forwarded-For` header, Cloudflare **appends** the connecting peer: client-supplied values survive as **left-most** (spoofable) entries, and the right-most entry is the real connecting peer.
- Consequences: the *left-most* X-Forwarded-For entry is attacker-controlled and must not be an identity; uvicorn's `ProxyHeadersMiddleware` (with Render's default `FORWARDED_ALLOW_IPS=*`) resolves `request.client` to the **left-most** entry, so OpenSK must **not** use `request.client.host` as a rate-limit identity on Render. OpenSK implements its own Render-specific resolver: prefer the edge-owned `CF-Connecting-IP`; fall back conservatively to the right-most X-Forwarded-For entry only.

## Policy

- **100 requests per 60 seconds per client IP**, fixed window.
- Fixed-window boundary behavior is an accepted simplification for this deployment: a client may send up to 2× the limit inside a narrow window straddling a boundary. This is documented rather than eliminated with a more complex algorithm.
- Scope: `GET` requests to `/` and `/v1/*`.
- Exempt: `GET /v1/health` (uptime/monitoring must never be throttled; health responses also carry no rate-limit headers).
- Out of scope (unchanged): `/docs`, `/redoc`, `/openapi.json` (framework paths outside `/v1`), and CORS `OPTIONS` preflights (handled by the outer CORS middleware, never reaching the limiter).

## Client Identity Resolution

Bucket identity is a validated IP address (IPv4 or IPv6, parsed with Python `ipaddress`):

- **Render detection** uses the official `RENDER=true` environment variable; proxy headers are trusted only in that verified environment.
- **On Render, primary signal**: `CF-Connecting-IP` — Cloudflare's original visitor IP header. Render routes all inbound traffic through Cloudflare, and Cloudflare's edge sets this header itself (a client-supplied value is not preserved across the edge — see [Cloudflare HTTP headers](https://developers.cloudflare.com/fundamentals/reference/http-headers/)). A forged `X-Forwarded-For` or a fake client-sent `CF-Connecting-IP` therefore cannot mint a fresh identity: the edge-owned value always wins. This avoids any project-maintained Cloudflare CIDR list and any proxy-topology assumptions.
- **On Render, conservative fallback** (only when `CF-Connecting-IP` is missing or malformed): `X-Forwarded-For`, right-most parseable entry only. Cloudflare appends the real connecting peer at the right end, so client-supplied left-most entries are never considered. If nothing parseable remains, identity is the shared fail-closed `"unknown"` bucket — never a bypass. (Cloudflare-Workers-mediated clients resolve through the same edge-set header, so they no longer manipulate identity; the old right-to-left + CIDR-skip walk, the hardcoded Cloudflare network table, and the Workers-egress caveat are gone.)
- **Off Render**: use the immediate peer (`request.scope["client"]`) only; `CF-Connecting-IP` and `X-Forwarded-For` are ignored entirely — there is no trusted-proxy configuration for local/test runs.
- Malformed/missing identity never bypasses limiting; it maps to the shared `"unknown"` bucket.
- No raw client IP is written to disk or emitted in application logs from the middleware; bucket keys are ephemeral in-memory only.

## Enablement Model

Environment variable `OPENSK_RATE_LIMIT_ENABLED`:

- `auto` (default): enabled when `RENDER=true`, disabled elsewhere.
- `true`: always enabled (emergency/manual force-on, local testing).
- `false`: always disabled (emergency kill switch).

Unknown values fall back to `auto`. No configuration library is used. Values are evaluated lazily inside the running process on each request (useful for tests and local servers), **but** on Render a Dashboard environment-variable change only reaches the process when Render applies the configuration through a new deploy/restart — this is an emergency override mechanism, not a live request-by-request remote switch. The limit/window (100 / 60 s) stays a code constant.

## State And Limits Of The Design

- State is **in-memory, process-local, best-effort**: a map `identity -> count` plus the current window identifier, protected by a lock; when the window rolls over the map is discarded, so no per-IP state accumulates across windows.
- Restarts/deploys wipe counters — acceptable; the limiter is a guardrail, not a quota product.
- It does **not** provide a globally exact quota if OpenSK later runs multiple workers/instances. **Review trigger:** if OpenSK moves to multiple serving processes/instances, or rate-limit accuracy becomes a product requirement, revisit edge/shared-state limiting (then out of current scope; no Redis today).
- Buckets are per client **IP**, so everyone behind one NAT (office, school, carrier-grade NAT) shares a bucket; 100/minute is generous for a cached read-only data API, but a noisy-neighbor 429 heals within ≤60 s with `Retry-After`. Similarly, forcing `OPENSK_RATE_LIMIT_ENABLED=true` on a self-hosted deployment behind an untracked reverse proxy yields a single shared bucket (peer = proxy IP) unless the proxy topology matches the Render trust model.

## Response Contract

Limited responses (any status, including 304) carry:

- `X-RateLimit-Limit`: 100
- `X-RateLimit-Remaining`: requests left in the current window after this one (never negative)
- `X-RateLimit-Reset`: UTC Unix epoch second when the current window resets

429 responses:

- status `429` with the standard OpenSK error envelope:

```json
{
  "data": null,
  "metadata": { "source": "OpenSK API", "lastUpdated": null, "version": "v1" },
  "error": {
    "code": "RATE_LIMITED",
    "message": "Rate limit exceeded. Retry after the number of seconds in Retry-After.",
    "messageSk": "Prekročený limit požiadaviek. Skúste znova po počte sekúnd v Retry-After."
  }
}
```

- `Retry-After: <integer seconds until the current window resets>`
- `Cache-Control: no-store`
- no `ETag`, no `Last-Modified` (429s are generated by the limiter before the conditional-caching middleware, and no clock values appear in the JSON body)

## Middleware Order

`CORS → rate limiter → conditional caching (ETag) → application`

- CORS is outermost, so browser clients see `Access-Control-Allow-Origin` even on 429s, and `Access-Control-Expose-Headers` includes `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, and `Retry-After`.
- Rejected requests stop at the limiter and never reach routing/serialization/ETag hashing.
- Conditional requests that return 304 still consume quota and still carry the rate-limit headers.

## Scheduled Public Smoke Monitoring

A separate GitHub Actions workflow (`.github/workflows/public-smoke.yml`) runs the smoke suite daily against `https://opensk-api.onrender.com` (06:17 UTC, `workflow_dispatch` also available), warm-starting the free-tier instance through `/v1/health` first (~2 minutes of retries, worst case ~7 minutes including request timeouts). It behaves like a normal external developer — no rate-limit bypass — and its 40 requests sit comfortably below the 100/minute limit. A green run requires production to be deployed from the same ref, so a manual dispatch from a pre-merge branch legitimately fails the version and (pre-deploy) rate-limit checks. GitHub disables scheduled workflows after 60 days of repository inactivity; wake it by any commit/re-enable. See `docs/release-readiness.md` for what this monitoring is and is not (best-effort daily check, not an uptime SLA).
