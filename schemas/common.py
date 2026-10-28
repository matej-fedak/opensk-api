from typing import Any, Generic, Literal, TypeVar, TypedDict

from pydantic import BaseModel, ConfigDict, Field


API_SOURCE = "OpenSK API"
BANKS_LAST_UPDATED = "2026-10-08"
# Authoritative calendar-law/source verification date, not future occurrence or NBS publication date.
HOLIDAYS_LAST_UPDATED = "2026-10-28"
PSC_LAST_UPDATED = "2026-06-02"
PHONE_AREAS_LAST_UPDATED = "2026-09-15"
VEHICLE_REGISTRATION_CODES_LAST_UPDATED = "2026-09-15"
SCHOOL_FACILITY_COUNTS_LAST_UPDATED = "2025-09-15"
PROCUREMENT_NOTICES_LAST_UPDATED = "2026-09-29"
EXCHANGE_RATES_LAST_UPDATED = "2026-10-12"
EU_FUNDS_LAST_UPDATED = "2026-10-15"
REGIONS_LAST_UPDATED = "2026-05-27"
# Successor geography freshness is the UTC OpenSK acquisition date, not validFrom.
DISTRICTS_LAST_UPDATED = "2026-10-16"
MUNICIPALITIES_LAST_UPDATED = "2026-10-16"
SOURCES_LAST_UPDATED = "2026-10-16"
PSC_LIST_SOURCE = "OpenSK API static PSC dataset"
PSC_SEARCH_SOURCE = "OpenSK API static PSC dataset"
PSC_STATS_SOURCE = "OpenSK API static PSC dataset"
PSC_GEOGRAPHY_SOURCE = "OpenSK API static PSC dataset + static geography seed datasets"
STATIC_CACHE_CONTROL = "public, max-age=86400"
SEARCH_CACHE_CONTROL = "public, max-age=900"
META_CACHE_CONTROL = "public, max-age=3600"
NO_STORE_CACHE_CONTROL = "no-store"
GEOGRAPHY_SOURCE = "OpenSK API static geography dataset"
GEOGRAPHY_SEED_SOURCE = "OpenSK API static geography seed dataset"


class Metadata(TypedDict):
    source: str
    lastUpdated: str | None
    version: str


class Envelope(TypedDict, total=False):
    data: Any
    metadata: Metadata
    error: Any | None


class PublicModel(BaseModel):
    """Closed public shapes: fail on unmodelled fields rather than filter them."""

    model_config = ConfigDict(extra="forbid")


class ResponseMetadata(PublicModel):
    source: str
    lastUpdated: str | None = Field(description="Local snapshot freshness; not a live-source guarantee.")
    version: Literal["v1"]


DataT = TypeVar("DataT")


class SuccessResponse(PublicModel, Generic[DataT]):
    data: DataT
    metadata: ResponseMetadata
    error: None


class Page(PublicModel, Generic[DataT]):
    items: list[DataT]
    count: int = Field(description="Items in this page, not the total matching count.")
    total: int
    limit: int
    offset: int


class ApplicationError(PublicModel):
    code: str
    message: str
    messageSk: str


class ErrorResponse(PublicModel):
    data: None
    metadata: ResponseMetadata
    error: ApplicationError


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
