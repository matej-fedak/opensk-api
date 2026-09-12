from fastapi import APIRouter, HTTPException, Query, Response

from schemas.common import API_SOURCE, PHONE_AREAS_LAST_UPDATED, STATIC_CACHE_CONTROL, error_detail, success_response
from services.geography_service import GeographyInvalidFormatError, validate_district_code_format, validate_municipality_code_format, validate_region_code_format
from services.phone_area_service import (
    PHONE_AREA_LIST_DEFAULT_LIMIT,
    PHONE_AREA_LIST_MAX_LIMIT,
    PHONE_AREA_SEARCH_DEFAULT_LIMIT,
    PHONE_AREA_SEARCH_MAX_LIMIT,
    PhoneAreaInvalidFormatError,
    PhoneAreaNotFoundError,
    filter_phone_area_records,
    get_phone_area_by_code,
    list_phone_areas,
    search_phone_area_records,
    search_phone_areas,
    validate_phone_area_code_format,
)


router = APIRouter(prefix="/phone-areas", tags=["phone-areas"])


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


def _parse_optional_code(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return validate_phone_area_code_format(value)
    except PhoneAreaInvalidFormatError:
        raise _invalid_format("code must match 0# or 0## format", "Parameter code musí mať formát 0# alebo 0##")


def _parse_optional_municipality_code(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return validate_municipality_code_format(value)
    except GeographyInvalidFormatError:
        raise _invalid_format("municipalityCode must be 6 digits", "Parameter municipalityCode musí byť 6-ciferný")


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
    summary="List phone area records",
    description="Returns the static Slovak primary telephone area dataset with pagination and filters.",
)
def list_phone_areas_endpoint(
    response: Response,
    code: str | None = Query(default=None, description="Optional phone area code filter."),
    municipalityCode: str | None = Query(default=None, description="Optional municipality code filter."),
    municipalityName: str | None = Query(default=None, description="Optional municipality name substring filter."),
    regionCode: str | None = Query(default=None, description="Optional region code filter."),
    districtCode: str | None = Query(default=None, description="Optional district code filter."),
    limit: str | None = Query(default=None, description="Optional page size."),
    offset: str | None = Query(default=None, description="Optional result offset."),
) -> dict[str, object]:
    filters: dict[str, object] = {}
    normalized_code = _parse_optional_code(code)
    normalized_municipality_code = _parse_optional_municipality_code(municipalityCode)
    normalized_region_code = _parse_optional_region_code(regionCode)
    normalized_district_code = _parse_optional_district_code(districtCode)
    parsed_limit = _parse_optional_limit(limit, default=PHONE_AREA_LIST_DEFAULT_LIMIT, maximum=PHONE_AREA_LIST_MAX_LIMIT, field_name="limit")
    parsed_offset = _parse_offset(offset)

    if normalized_code is not None:
        filters["code"] = normalized_code
    if normalized_municipality_code is not None:
        filters["municipalityCode"] = normalized_municipality_code
    if normalized_region_code is not None:
        filters["regionCode"] = normalized_region_code
    if normalized_district_code is not None:
        filters["districtCode"] = normalized_district_code
    if municipalityName is not None:
        filters["municipalityName"] = municipalityName

    filtered = filter_phone_area_records(filters)
    page = list_phone_areas(filters, limit=parsed_limit, offset=parsed_offset)
    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(
        data={"items": page, "count": len(page), "total": len(filtered), "limit": parsed_limit, "offset": parsed_offset},
        source=f"{API_SOURCE} static phone area dataset",
        last_updated=PHONE_AREAS_LAST_UPDATED,
    )


@router.get(
    "/search",
    summary="Search phone area records",
    description="Searches the static Slovak primary telephone area dataset by query string.",
)
def search_phone_areas_endpoint(
    response: Response,
    q: str | None = Query(default=None, description="Search query."),
    limit: str | None = Query(default=None, description="Optional page size."),
    offset: str | None = Query(default=None, description="Optional result offset."),
) -> dict[str, object]:
    if q is None or not q.strip():
        raise _invalid_format("q is required", "Parameter q je povinný")
    parsed_limit = _parse_optional_limit(limit, default=PHONE_AREA_SEARCH_DEFAULT_LIMIT, maximum=PHONE_AREA_SEARCH_MAX_LIMIT, field_name="limit")
    parsed_offset = _parse_offset(offset)
    try:
        all_matches = search_phone_area_records(q)
        page = search_phone_areas(q, limit=parsed_limit, offset=parsed_offset)
    except PhoneAreaInvalidFormatError:
        raise _invalid_format("q must be at least 2 characters", "Parameter q musí mať aspoň 2 znaky")
    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(
        data={"items": page, "count": len(page), "total": len(all_matches), "limit": parsed_limit, "offset": parsed_offset},
        source=f"{API_SOURCE} static phone area dataset",
        last_updated=PHONE_AREAS_LAST_UPDATED,
    )


@router.get(
    "/{code}",
    summary="Phone area lookup by code",
    description="Returns all static phone area records for one Slovak primary telephone area code.",
)
def get_phone_area(code: str, response: Response) -> dict[str, object]:
    try:
        records = get_phone_area_by_code(code)
    except PhoneAreaInvalidFormatError:
        raise _invalid_format("code must match 0# or 0## format", "Kód primárnej oblasti musí mať formát 0# alebo 0##")
    except PhoneAreaNotFoundError:
        normalized = code.replace(" ", "")
        raise HTTPException(
            status_code=404,
            detail=error_detail(
                code="NOT_FOUND",
                message=f"No phone area data available for {normalized}",
                message_sk=f"Pre telefónnu primárnu oblasť {normalized} nie sú dostupné údaje",
            ),
            headers={"Cache-Control": STATIC_CACHE_CONTROL},
        )
    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(
        data={"code": records[0]["code"], "items": records, "count": len(records)},
        source=f"{API_SOURCE} static phone area dataset",
        last_updated=PHONE_AREAS_LAST_UPDATED,
    )
