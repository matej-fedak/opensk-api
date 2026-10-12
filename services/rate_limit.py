"""Application-level rate limiting for the public OpenSK deployment.

A small, in-memory, process-local fixed-window limiter (100 requests / 60
seconds / client IP) protecting the single-instance Render deployment from
accidental client loops and simple abusive traffic.

Client identity is a validated IP address. On Render (`RENDER=true`), all
inbound traffic passes through Cloudflare, which *appends* the real peer IP
to `X-Forwarded-For`; the resolver therefore walks the header right-to-left,
skipping malformed entries and published Cloudflare egress ranges. Client-
supplied (left-most) entries are never trusted, so fake headers cannot mint
fresh identities. Off Render, `X-Forwarded-For` is ignored entirely and the
immediate peer is used. Unresolvable identity maps to a shared fail-closed
bucket. No client IP is written to disk or logged.

See `docs/rate-limiting-contract.md` for the full policy and evidence.
"""

import ipaddress
import os
import threading
import time
from collections.abc import Callable

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from schemas.common import API_SOURCE, error_detail, error_response

WINDOW_SECONDS = 60
REQUEST_LIMIT = 100
RATE_LIMIT_HEADERS_PREFIX = "X-RateLimit"
_UNKNOWN_IDENTITY = "unknown"

# Published Cloudflare egress ranges (https://www.cloudflare.com/ips-v4/,
# https://www.cloudflare.com/ips-v6/), captured 2026-10-12. Used only to skip
# proxy hops while walking X-Forwarded-For right-to-left on Render; membership
# changes at worst coarsen a bucket (fail-closed), never enable spoofing.
_CLOUDFLARE_NETWORKS = tuple(
    ipaddress.ip_network(cidr)
    for cidr in (
        "173.245.48.0/20",
        "103.21.244.0/22",
        "103.22.200.0/22",
        "103.31.4.0/22",
        "141.101.64.0/18",
        "108.162.192.0/18",
        "190.93.240.0/20",
        "188.114.96.0/20",
        "197.234.240.0/22",
        "198.41.128.0/17",
        "162.158.0.0/15",
        "104.16.0.0/13",
        "104.24.0.0/14",
        "172.64.0.0/13",
        "131.0.72.0/22",
        "2400:cb00::/32",
        "2606:4700::/32",
        "2803:f800::/32",
        "2405:b500::/32",
        "2405:8100::/32",
        "2a06:98c0::/29",
        "2c0f:f248::/32",
    )
)


def rate_limit_enabled(env: Callable[[str], str | None] = os.environ.get) -> bool:
    """Resolve OPENSK_RATE_LIMIT_ENABLED: auto (default) | true | false.

    `auto` enables the limiter only on Render (`RENDER=true`). Unknown values
    behave as `auto`. Read lazily per call so dashboard env changes apply
    without a restart.
    """
    setting = (env("OPENSK_RATE_LIMIT_ENABLED") or "auto").strip().lower()
    if setting == "true":
        return True
    if setting == "false":
        return False
    return (env("RENDER") or "").strip().lower() == "true"


def _render_context(env: Callable[[str], str | None] = os.environ.get) -> bool:
    return (env("RENDER") or "").strip().lower() == "true"


def _parse_ip(token: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    token = token.strip()
    if not token:
        return None
    # Tolerate bracketed IPv6 / host:port forms defensively.
    if token.startswith("[") and "]" in token:
        token = token[1 : token.index("]")]
    try:
        return ipaddress.ip_address(token)
    except ValueError:
        pass
    # Last resort: IPv4 with a trailing :port.
    if token.count(":") == 1 and "." in token:
        try:
            return ipaddress.ip_address(token.rsplit(":", 1)[0])
        except ValueError:
            return None
    return None


def resolve_identity(request: Request, render_context: bool) -> str:
    """Return the validated client-IP bucket identity for the request.

    Render: walk X-Forwarded-For right-to-left (all header instances),
    skipping malformed entries, non-global addresses, and published
    Cloudflare egress hops; the first remaining entry is the real client,
    which Cloudflare appends to the right end before the request reaches
    Render. If nothing global/non-Cloudflare survives, fall back to the
    rightmost valid entry (fail-closed shared-ish bucket, never a bypass).
    Off Render: use the immediate peer from the connection only.
    """
    if render_context:
        headers = request.headers.getlist("x-forwarded-for")
        valid = [
            parsed
            for header in headers
            for parsed in (_parse_ip(part) for part in header.split(","))
            if parsed is not None
        ]
        if valid:
            for entry in reversed(valid):
                if entry.is_global and not any(entry in network for network in _CLOUDFLARE_NETWORKS):
                    return str(entry)
            return str(valid[-1])
        return _UNKNOWN_IDENTITY

    client = request.scope.get("client")
    if client:
        parsed = _parse_ip(str(client[0]))
        if parsed is not None:
            return str(parsed)
        return str(client[0])
    return _UNKNOWN_IDENTITY


class FixedWindowRateLimiter:
    """Fixed-window counter: identity -> count, reset map per window."""

    def __init__(self, clock: Callable[[], float] = time.time, limit: int = REQUEST_LIMIT, window_seconds: int = WINDOW_SECONDS) -> None:
        self._clock = clock
        self._limit = limit
        self._window_seconds = window_seconds
        self._window_id: int | None = None
        self._counts: dict[str, int] = {}
        self._lock = threading.Lock()

    def hit(self, identity: str) -> tuple[bool, int, int, int]:
        """Consume one unit for identity.

        Returns (allowed, remaining_after_this_request, window_reset_epoch,
        clock_second). The clock is read inside the lock so the window can
        never regress and Retry-After/Reset stay mutually consistent.
        """
        with self._lock:
            now = int(self._clock())
            window_id = now // self._window_seconds
            if window_id != self._window_id:
                self._counts = {}
                self._window_id = window_id
            count = self._counts.get(identity, 0) + 1
            self._counts[identity] = count
        reset_epoch = (window_id + 1) * self._window_seconds
        remaining = max(0, self._limit - count)
        return count <= self._limit, remaining, reset_epoch, now

    def reset(self) -> None:
        with self._lock:
            self._counts = {}
            self._window_id = None


rate_limiter = FixedWindowRateLimiter()


def _is_limited_path(request: Request) -> bool:
    if request.method != "GET":
        return False
    path = request.url.path
    if path == "/v1/health":
        return False
    return path == "/" or path.startswith("/v1/")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Enforce the fixed-window limit; emit X-RateLimit headers and 429s.

    Must sit inside CORSMiddleware and outside the conditional-caching
    middleware: CORS wraps 429s for browsers, and rejected requests never
    reach routing or ETag hashing.
    """

    def __init__(self, app, limiter: FixedWindowRateLimiter = rate_limiter) -> None:  # type: ignore[no-untyped-def]
        super().__init__(app)
        self._limiter = limiter

    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def]
        if not _is_limited_path(request) or not rate_limit_enabled():
            return await call_next(request)

        identity = resolve_identity(request, render_context=_render_context())
        allowed, remaining, reset_epoch, now = self._limiter.hit(identity)

        if not allowed:
            retry_after = max(1, reset_epoch - now)
            payload = error_response(
                error=error_detail(
                    "RATE_LIMITED",
                    "Rate limit exceeded. Retry after the number of seconds in Retry-After.",
                    "Prekročený limit požiadaviek. Skúste znova po počte sekúnd v Retry-After.",
                ),
                source=API_SOURCE,
                last_updated=None,
            )
            return JSONResponse(
                status_code=429,
                content=payload,
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self._limiter._limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_epoch),
                    "Cache-Control": "no-store",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self._limiter._limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_epoch)
        return response
