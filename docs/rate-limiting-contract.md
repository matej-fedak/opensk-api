# Future Rate-Limiting Contract

Status: `RATE_LIMIT_CONTRACT_ONLY` for 0.23.1. No request limiting is implemented yet. This document fixes the intended contract so the 0.23.2+ implementation is a mechanical follow-through, not a design debate.

## Purpose

Protect OpenSK server capacity (single hobby-grade Render instance) from bursts and abusive crawlers. It is not a product feature, billing mechanism, or identity system — **no API keys, ever**.

## Probable Model (hypotheses, not policy)

- Per-client-IP fixed-window or token-bucket limit. Working hypothesis: ~100 requests/minute/IP with a small burst (~20), tuned after observing real traffic.
- The limiter applies to `/` and `/v1/*` GET requests.
- Exempt: `/v1/health` (uptime checks must never be throttled).

## 429 Response

Standard OpenSK error envelope:

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

## Headers

- `Retry-After: <seconds>` — required on 429 responses.
- `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` — informative headers on limited API responses (not on health).

## Client Identity And Proxy Considerations

- Render routes traffic through a reverse proxy; client IP must come from `X-Forwarded-For` (right-most entry) only when the immediate peer is trusted. Blindly trusting arbitrary `X-Forwarded-For` lets clients spoof unlimited identities. The implementation must pin trusted proxy behavior explicitly (Render sets the header for external requests).
- Rate-limit state must tolerate Render restarts: in-memory fixed-window counters are acceptable for a single small instance; do not introduce Redis (project constraint).

## Implementation Plan

Target: post-launch milestone (candidate 0.23.2 or the release before public promotion). Evaluate `slowapi` vs. a ~60-line in-house middleware: the project currently has only four dependencies and prefers no new dependency for this. Whichever ships must:

1. emit the 429 envelope and headers above exactly,
2. exempt `/v1/health`,
3. resolve client IP with the trusted-proxy rules above,
4. be fully unit-tested without network access,
5. be documented as enabled/disabled on Render in `docs/api-status.md`.
