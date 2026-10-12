# Rate-Limiting Contract

Status: **implemented since 0.23.5**. This document is the authoritative policy for the application-level rate limiter in `services/rate_limit.py`.

## Purpose

Protect the OpenSK deployment itself (a single hobby-grade Render instance) from accidental client loops, simple abusive clients, and resource exhaustion while keeping a zero-auth developer experience. It is not a product feature, billing mechanism, or identity system — **no API keys, ever**.

Rate limiting protects OpenSK only. It has nothing to do with protecting ECB, PortalVS, or any other upstream provider, because runtime requests never contact upstream sources (everything is materialized local JSON).

## Verified Platform Facts (re-checked 2026-10-12)

- Render routes **all inbound web-service traffic through Cloudflare's global network**; Layer 3/4 and obviously flooded Layer 7 attacks are mitigated at the edge automatically, for free ([Render: How Render handles DDoS attacks](https://render.com/articles/how-render-handles-ddos-attacks), [Render: DDoS protection](https://render.com/docs/ddos-protection)).
- Targeted Layer 7 traffic that looks like real requests ("API abuse, slow requests") is **explicitly the application's responsibility** — Render recommends application-level rate limiting. Render offers **no configurable per-client rate limiting** for normal inbound application traffic on web services. (Render's own API rate limits apply only to the Render *management* API at api.render.com — unrelated.)
- Render always sets `RENDER=true` in the runtime environment ([Render: Default environment variables](https://render.com/docs/environment-variables)), which OpenSK uses as its Render detection signal. Render also sets `FORWARDED_ALLOW_IPS=*` for Python runtimes by default.
- Cloudflare's `X-Forwarded-For` handling ([Cloudflare: HTTP headers](https://developers.cloudflare.com/fundamentals/reference/http-headers/)): if the client already sent an `X-Forwarded-For` header, Cloudflare **appends** the IP of the peer that connected to Cloudflare. A client-supplied value therefore survives as the **left-most** entries, and the **right-most** entry is the real connecting peer — meaning the left-most entry is **spoofable** and must not be used as a rate-limit identity. Cloudflare explicitly recommends `CF-Connecting-IP` over `X-Forwarded-For` for restoring the original visitor IP for the same reason.
- Consequence for the old 0.23.1 hypothesis ("take the right-most entry"): the *left-most* entry is attacker-controlled; the right-most entry closest to the client is the last trustworthy hop appended by Cloudflare. uvicorn's `ProxyHeadersMiddleware` (`--proxy-headers`, with Render's default `FORWARDED_ALLOW_IPS=*`) resolves `request.client` to the **left-most** entry, so OpenSK must **not** use `request.client.host` as a rate-limit identity on Render. OpenSK implements its own Render-specific resolver instead.

## Policy

- **100 requests per 60 seconds per client IP**, fixed window.
- Fixed-window boundary behavior is an accepted simplification for this deployment: a client may send up to 2× the limit inside a narrow window straddling a boundary. This is documented rather than eliminated with a more complex algorithm.
- Scope: `GET` requests to `/` and `/v1/*`.
- Exempt: `GET /v1/health` (uptime/monitoring must never be throttled; health responses also carry no rate-limit headers).
- Out of scope (unchanged): `/docs`, `/redoc`, `/openapi.json` (framework paths outside `/v1`), and CORS `OPTIONS` preflights (handled by the outer CORS middleware, never reaching the limiter).

## Client Identity Resolution

Bucket identity is a validated IP address:

- **On Render** (`RENDER=true`): read `X-Forwarded-For` (all header instances), walk entries **right-to-left**, skip entries that are not parseable IP addresses, are not globally routable (private/reserved/loopback/link-local), or fall inside **published Cloudflare IP ranges** (<https://www.cloudflare.com/ips-v4/>, `ips-v6/`, captured 2026-10-12); take the first remaining entry. Cloudflare always appends the real connecting peer on the right, so walking right-to-left past proxy hops (including a hop Render's load balancer may append) yields the real client whenever the client connects from a normal ISP address. Entries a client forged sit to the *left* of the appended real IP and are never reached, so **fake headers cannot mint fresh identities**. If no global, non-Cloudflare entry survives, fall back to the rightmost valid entry — fail-closed into a coarse shared-ish bucket, never a bypass.
- Known residual caveat: a client connecting **through Cloudflare itself** (e.g. a Cloudflare Worker fetch) presents a Cloudflare egress IP as the real peer, which the walk skips in favor of entries further left; such a client can shift identity within its own forged left-hand entries. This is accepted for the stated threat model (accidental loops, simple abuse) and shared by any X-Forwarded-For-based design behind Cloudflare; `CF-Ray` in Render logs remains the audit signal if abuse emerges.
- **Off Render**: use the immediate peer (`request.scope["client"]`). Arbitrary `X-Forwarded-For` is ignored entirely — there is no trusted-proxy configuration for local/test runs.
- Malformed/missing identity never bypasses limiting; it maps to the shared `"unknown"` bucket.
- IPv4 and IPv6 are both supported (Python `ipaddress`).
- `CF-Connecting-IP` is deliberately **not** used: OpenSK trusts only the platform-verified `X-Forwarded-For` append semantics, not vendor-specific headers.
- No raw client IP is written to disk or emitted in application logs from the middleware; bucket keys are ephemeral in-memory only.

## Enablement Model

Environment variable `OPENSK_RATE_LIMIT_ENABLED`:

- `auto` (default): enabled when `RENDER=true`, disabled elsewhere.
- `true`: always enabled (emergency/manual force-on, local testing).
- `false`: always disabled (emergency kill switch without a redeploy of code).

Unknown values fall back to `auto`. No configuration library is used; `os.environ` is read lazily per request so a dashboard env change takes effect on the next request. The limit/window (100 / 60 s) stays a code constant.

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
