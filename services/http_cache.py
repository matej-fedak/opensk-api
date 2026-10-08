"""HTTP conditional caching for locally materialized datasets.

ETags are strong validators derived from the exact response body bytes
(SHA-256, truncated). Because runtime responses are computed only from
checked-in deterministic JSON, identical requests produce byte-identical
bodies, so ETags are stable across processes without any upstream calls or
clocks. `Last-Modified` uses per-dataset semantic `LAST_UPDATED` dates, never
the deployment or request time.

See `docs/http-caching.md` for the full policy.
"""

import hashlib
from datetime import UTC, date, datetime, time
from email.utils import format_datetime, parsedate_to_datetime

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from schemas.common import (
    BANKS_LAST_UPDATED,
    DISTRICTS_LAST_UPDATED,
    HOLIDAYS_LAST_UPDATED,
    MUNICIPALITIES_LAST_UPDATED,
    PHONE_AREAS_LAST_UPDATED,
    PROCUREMENT_NOTICES_LAST_UPDATED,
    PSC_LAST_UPDATED,
    REGIONS_LAST_UPDATED,
    SCHOOL_FACILITY_COUNTS_LAST_UPDATED,
    SOURCES_LAST_UPDATED,
    VEHICLE_REGISTRATION_CODES_LAST_UPDATED,
)


_ETAG_EXCLUDED_PATHS = frozenset({"/v1/health"})

# Semantic dataset freshness per path prefix. Paths missing here (companies,
# /v1/ico alias, and root) intentionally get no Last-Modified header.
_LAST_MODIFIED_BY_PREFIX: dict[str, str] = {
    "/v1/holidays": HOLIDAYS_LAST_UPDATED,
    "/v1/business-days": HOLIDAYS_LAST_UPDATED,
    "/v1/banks": BANKS_LAST_UPDATED,
    "/v1/iban": BANKS_LAST_UPDATED,
    "/v1/psc": PSC_LAST_UPDATED,
    "/v1/regions": REGIONS_LAST_UPDATED,
    "/v1/districts": DISTRICTS_LAST_UPDATED,
    "/v1/municipalities": MUNICIPALITIES_LAST_UPDATED,
    "/v1/phone-areas": PHONE_AREAS_LAST_UPDATED,
    "/v1/vehicle-registration-codes": VEHICLE_REGISTRATION_CODES_LAST_UPDATED,
    "/v1/school-facility-counts": SCHOOL_FACILITY_COUNTS_LAST_UPDATED,
    "/v1/procurement-notices": PROCUREMENT_NOTICES_LAST_UPDATED,
    "/v1/sources": SOURCES_LAST_UPDATED,
}


def make_etag(body: bytes) -> str:
    return '"' + hashlib.sha256(body).hexdigest()[:32] + '"'


def _parse_http_date(value: str) -> datetime | None:
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


def _last_modified_for(path: str) -> datetime | None:
    for prefix, iso_date in _LAST_MODIFIED_BY_PREFIX.items():
        if path == prefix or path.startswith(prefix + "/"):
            return datetime.combine(date.fromisoformat(iso_date), time.min, tzinfo=UTC)
    return None


def _matches_etag(if_none_match: str, etag: str) -> bool:
    tokens = [token.strip() for token in if_none_match.split(",")]
    return "*" in tokens or etag in tokens


class ConditionalCachingMiddleware(BaseHTTPMiddleware):
    """Attach ETag/Last-Modified and honor If-None-Match/If-Modified-Since.

    Applies to GET requests on `/` and `/v1/*` with status 200. Error
    responses, `/v1/health`, and framework-owned paths are passed through
    unchanged.
    """

    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def]
        path = request.url.path
        if request.method != "GET":
            return await call_next(request)
        if path != "/" and not path.startswith("/v1/"):
            return await call_next(request)
        if path in _ETAG_EXCLUDED_PATHS:
            return await call_next(request)

        response = await call_next(request)
        if response.status_code != 200:
            return response

        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        etag = make_etag(body)
        last_modified = _last_modified_for(path)

        headers = dict(response.headers)
        headers["etag"] = etag
        if last_modified is not None:
            headers["last-modified"] = format_datetime(last_modified, usegmt=True)

        if_none_match = request.headers.get("if-none-match")
        if if_none_match and _matches_etag(if_none_match, etag):
            return Response(status_code=304, headers=headers)

        if last_modified is not None:
            if_modified_since = request.headers.get("if-modified-since")
            if if_modified_since:
                parsed = _parse_http_date(if_modified_since)
                if parsed is not None and last_modified <= parsed:
                    return Response(status_code=304, headers=headers)

        return Response(content=body, status_code=200, headers=headers, media_type="application/json")
