from fastapi import APIRouter, HTTPException, Query, Response

from schemas.common import API_SOURCE, STATIC_CACHE_CONTROL, VEHICLE_REGISTRATION_CODES_LAST_UPDATED, error_detail, success_response
from services.geography_service import GeographyInvalidFormatError, validate_district_code_format, validate_region_code_format
from services.vehicle_registration_service import (
    VEHICLE_REGISTRATION_LIST_DEFAULT_LIMIT,
    VEHICLE_REGISTRATION_LIST_MAX_LIMIT,
    VEHICLE_REGISTRATION_SEARCH_DEFAULT_LIMIT,
    VEHICLE_REGISTRATION_SEARCH_MAX_LIMIT,
    VehicleRegistrationCodeInvalidFormatError,
    VehicleRegistrationCodeNotFoundError,
    filter_vehicle_registration_code_records,
    get_vehicle_registration_code,
    list_vehicle_registration_codes,
    search_vehicle_registration_code_records,
    search_vehicle_registration_codes,
    validate_vehicle_registration_code_format,
)


router = APIRouter(prefix="/vehicle-registration-codes", tags=["vehicle-registration-codes"])


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
        return validate_vehicle_registration_code_format(value)
    except VehicleRegistrationCodeInvalidFormatError:
        raise _invalid_format("code must be two letters", "Parameter code musí obsahovať dve písmená")


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
    summary="List legacy vehicle registration district codes",
    description="Returns static historical Slovak vehicle registration district abbreviations. This does not decode full plates and is not reliable for current plate lookup.",
)
def list_vehicle_registration_codes_endpoint(
    response: Response,
    code: str | None = Query(default=None, description="Optional two-letter legacy district abbreviation filter."),
    districtName: str | None = Query(default=None, description="Optional district name substring filter."),
    regionCode: str | None = Query(default=None, description="Optional region code filter."),
    districtCode: str | None = Query(default=None, description="Optional district code filter."),
    limit: str | None = Query(default=None, description="Optional page size."),
    offset: str | None = Query(default=None, description="Optional result offset."),
) -> dict[str, object]:
    filters: dict[str, object] = {}
    normalized_code = _parse_optional_code(code)
    normalized_region_code = _parse_optional_region_code(regionCode)
    normalized_district_code = _parse_optional_district_code(districtCode)
    parsed_limit = _parse_optional_limit(limit, default=VEHICLE_REGISTRATION_LIST_DEFAULT_LIMIT, maximum=VEHICLE_REGISTRATION_LIST_MAX_LIMIT, field_name="limit")
    parsed_offset = _parse_offset(offset)

    if normalized_code is not None:
        filters["code"] = normalized_code
    if normalized_region_code is not None:
        filters["regionCode"] = normalized_region_code
    if normalized_district_code is not None:
        filters["districtCode"] = normalized_district_code
    if districtName is not None:
        filters["districtName"] = districtName

    filtered = filter_vehicle_registration_code_records(filters)
    page = list_vehicle_registration_codes(filters, limit=parsed_limit, offset=parsed_offset)
    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(
        data={"items": page, "count": len(page), "total": len(filtered), "limit": parsed_limit, "offset": parsed_offset},
        source=f"{API_SOURCE} static legacy vehicle registration code dataset",
        last_updated=VEHICLE_REGISTRATION_CODES_LAST_UPDATED,
    )


@router.get(
    "/search",
    summary="Search legacy vehicle registration district codes",
    description="Searches static historical district abbreviations by code, district name, or local geography code. It does not decode full vehicle plates.",
)
def search_vehicle_registration_codes_endpoint(
    response: Response,
    q: str | None = Query(default=None, description="Search query."),
    limit: str | None = Query(default=None, description="Optional page size."),
    offset: str | None = Query(default=None, description="Optional result offset."),
) -> dict[str, object]:
    if q is None or not q.strip():
        raise _invalid_format("q is required", "Parameter q je povinný")
    parsed_limit = _parse_optional_limit(limit, default=VEHICLE_REGISTRATION_SEARCH_DEFAULT_LIMIT, maximum=VEHICLE_REGISTRATION_SEARCH_MAX_LIMIT, field_name="limit")
    parsed_offset = _parse_offset(offset)
    try:
        all_matches = search_vehicle_registration_code_records(q)
        page = search_vehicle_registration_codes(q, limit=parsed_limit, offset=parsed_offset)
    except VehicleRegistrationCodeInvalidFormatError:
        raise _invalid_format("q must be at least 2 characters", "Parameter q musí mať aspoň 2 znaky")
    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(
        data={"items": page, "count": len(page), "total": len(all_matches), "limit": parsed_limit, "offset": parsed_offset},
        source=f"{API_SOURCE} static legacy vehicle registration code dataset",
        last_updated=VEHICLE_REGISTRATION_CODES_LAST_UPDATED,
    )


@router.get(
    "/{code}",
    summary="Legacy vehicle registration district code lookup",
    description="Returns one static historical Slovak vehicle registration district abbreviation. This is not a current plate lookup.",
)
def get_vehicle_registration_code_endpoint(code: str, response: Response) -> dict[str, object]:
    try:
        record = get_vehicle_registration_code(code)
    except VehicleRegistrationCodeInvalidFormatError:
        raise _invalid_format("code must be two letters", "Kód musí obsahovať dve písmená")
    except VehicleRegistrationCodeNotFoundError:
        normalized = code.replace(" ", "").upper()
        raise HTTPException(
            status_code=404,
            detail=error_detail(
                code="NOT_FOUND",
                message=f"No legacy vehicle registration code data available for {normalized}",
                message_sk=f"Pre historický evidenčný kód {normalized} nie sú dostupné údaje",
            ),
            headers={"Cache-Control": STATIC_CACHE_CONTROL},
        )
    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(
        data=record,
        source=f"{API_SOURCE} static legacy vehicle registration code dataset",
        last_updated=VEHICLE_REGISTRATION_CODES_LAST_UPDATED,
    )
