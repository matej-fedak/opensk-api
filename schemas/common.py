from datetime import date
from typing import Any, TypedDict


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
            "lastUpdated": last_updated or date.today().isoformat(),
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
            "lastUpdated": last_updated or date.today().isoformat(),
            "version": version,
        },
        "error": error,
    }
