from fastapi import APIRouter, HTTPException, Query, Response

from schemas.common import API_SOURCE, SCHOOL_FACILITY_COUNTS_LAST_UPDATED, STATIC_CACHE_CONTROL, error_detail, success_response
from services.geography_service import GeographyInvalidFormatError, validate_district_code_format, validate_region_code_format
from services.school_facility_count_service import (
    SCHOOL_FACILITY_COUNT_LIST_DEFAULT_LIMIT,
    SCHOOL_FACILITY_COUNT_LIST_MAX_LIMIT,
    filter_school_facility_count_records,
    get_school_facility_count_stats,
    list_school_facility_counts,
)


router = APIRouter(prefix="/school-facility-counts", tags=["school-facility-counts"])


def _invalid_format(message: str, message_sk: str) -> HTTPException:
    return HTTPException(
        status_code=400,
        detail=error_detail(code="INVALID_FORMAT", message=message, message_sk=message_sk),
        headers={"Cache-Control": STATIC_CACHE_CONTROL},
    )


def _parse_optional_limit(value: str | None, *, default: int, maximum: int, field_name: str) -> int:
    if value is None:
        return default
    if not value.isdigit():
        raise _invalid_format(f"{field_name} must be a non-negative integer up to {maximum}", f"Parameter {field_name} musí byť nezáporné celé číslo do {maximum}")
    parsed = int(value)
    if parsed > maximum:
        raise _invalid_format(f"{field_name} must be a non-negative integer up to {maximum}", f"Parameter {field_name} musí byť nezáporné celé číslo do {maximum}")
    return parsed


def _parse_offset(value: str | None) -> int:
    return _parse_optional_limit(value, default=0, maximum=10**9, field_name="offset")


def _parse_optional_region_code(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return validate_region_code_format(value)
    except GeographyInvalidFormatError:
        raise _invalid_format("regionCode must match the SK### format", "Parameter regionCode musí mať formát SK###")


def _parse_optional_district_code(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return validate_district_code_format(value)
    except GeographyInvalidFormatError:
        raise _invalid_format("districtCode must match the SK#### format", "Parameter districtCode musí mať formát SK####")


@router.get(
    "",
    summary="List school facility aggregate counts",
    description="Returns static aggregate school facility count rows from the MŠVVaM register dataset. This is not an institution-level school directory.",
)
def list_school_facility_counts_endpoint(
    response: Response,
    schoolKind: str | None = Query(default=None, description="Optional source school-kind abbreviation filter."),
    schoolType: str | None = Query(default=None, description="Optional source school-type abbreviation filter."),
    regionName: str | None = Query(default=None, description="Optional region name substring filter."),
    regionCode: str | None = Query(default=None, description="Optional region code filter."),
    districtName: str | None = Query(default=None, description="Optional district name substring filter."),
    districtCode: str | None = Query(default=None, description="Optional district code filter."),
    founderOwnershipType: str | None = Query(default=None, description="Optional founder ownership type filter."),
    founderType: str | None = Query(default=None, description="Optional founder type filter."),
    limit: str | None = Query(default=None, description="Optional page size."),
    offset: str | None = Query(default=None, description="Optional result offset."),
) -> dict[str, object]:
    filters: dict[str, object] = {}
    parsed_region_code = _parse_optional_region_code(regionCode)
    parsed_district_code = _parse_optional_district_code(districtCode)
    parsed_limit = _parse_optional_limit(limit, default=SCHOOL_FACILITY_COUNT_LIST_DEFAULT_LIMIT, maximum=SCHOOL_FACILITY_COUNT_LIST_MAX_LIMIT, field_name="limit")
    parsed_offset = _parse_offset(offset)

    for key, value in {
        "schoolKind": schoolKind,
        "schoolType": schoolType,
        "regionName": regionName,
        "districtName": districtName,
        "founderOwnershipType": founderOwnershipType,
        "founderType": founderType,
    }.items():
        if value is not None:
            filters[key] = value
    if parsed_region_code is not None:
        filters["regionCode"] = parsed_region_code
    if parsed_district_code is not None:
        filters["districtCode"] = parsed_district_code

    filtered = filter_school_facility_count_records(filters)
    page = list_school_facility_counts(filters, limit=parsed_limit, offset=parsed_offset)
    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(
        data={"items": page, "count": len(page), "total": len(filtered), "limit": parsed_limit, "offset": parsed_offset},
        source=f"{API_SOURCE} static school facility aggregate count dataset",
        last_updated=SCHOOL_FACILITY_COUNTS_LAST_UPDATED,
    )


@router.get(
    "/stats",
    summary="School facility aggregate count stats",
    description="Returns local totals for the aggregate school facility count dataset. It does not expose per-school, staff, or pupil data.",
)
def get_school_facility_count_stats_endpoint(response: Response) -> dict[str, object]:
    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(
        data=get_school_facility_count_stats(),
        source=f"{API_SOURCE} static school facility aggregate count dataset",
        last_updated=SCHOOL_FACILITY_COUNTS_LAST_UPDATED,
    )
