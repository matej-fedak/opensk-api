from typing import Any, TypedDict


API_SOURCE = "OpenSK API"
BANKS_LAST_UPDATED = "2026-05-25"
HOLIDAYS_LAST_UPDATED = "2026-05-25"
PSC_LAST_UPDATED = "2026-05-27"
REGIONS_LAST_UPDATED = "2026-05-27"
DISTRICTS_LAST_UPDATED = "2026-05-27"
MUNICIPALITIES_LAST_UPDATED = "2026-05-27"
PSC_GEOGRAPHY_SOURCE = "OpenSK API static PSC seed dataset + static geography seed datasets"
STATIC_CACHE_CONTROL = "public, max-age=86400"
GEOGRAPHY_SOURCE = "OpenSK API static geography dataset"
GEOGRAPHY_SEED_SOURCE = "OpenSK API static geography seed dataset"


class Metadata(TypedDict):
    source: str
    lastUpdated: str
    version: str


class Envelope(TypedDict, total=False):
    data: Any
    metadata: Metadata
    error: Any | None


def success_response(
    data: object,
    source: str,
    last_updated: str | None,
    version: str = "v1",
) -> dict[str, object]:
    return {
        "data": data,
        "metadata": {
            "source": source,
            "lastUpdated": last_updated,
            "version": version,
        },
        "error": None,
    }


def error_response(
    error: object,
    source: str,
    last_updated: str | None,
    version: str = "v1",
) -> dict[str, object]:
    return {
        "data": None,
        "metadata": {
            "source": source,
            "lastUpdated": last_updated,
            "version": version,
        },
        "error": error,
    }


def error_detail(code: str, message: str, message_sk: str) -> dict[str, str]:
    return {
        "code": code,
        "message": message,
        "messageSk": message_sk,
    }
