from fastapi import APIRouter, HTTPException, Query, Response

from schemas.common import API_SOURCE, PSC_GEOGRAPHY_SOURCE, PSC_LAST_UPDATED, STATIC_CACHE_CONTROL, error_detail, success_response
from services.geography_service import GeographyInvalidFormatError, validate_district_code_format, validate_municipality_code_format, validate_region_code_format
from services.psc_service import PSCInvalidFormatError, PSCNotFoundError, filter_psc_records, get_psc_stats, list_psc_records, lookup_psc, search_psc, search_psc_records, validate_psc_format


router = APIRouter(prefix="/psc", tags=["psc"])


def _invalid_format(message: str, message_sk: str) -> HTTPException:
    return HTTPException(
        status_code=400,
        detail=error_detail(code="INVALID_FORMAT", message=message, message_sk=message_sk),
        headers={"Cache-Control": STATIC_CACHE_CONTROL},
    )


def _parse_optional_psc(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return validate_psc_format(value)
    except PSCInvalidFormatError:
        raise _invalid_format("psc must be a 5-digit postal code", "Parameter psc musí byť 5-ciferné PSČ")


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


def _parse_optional_municipality_code(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return validate_municipality_code_format(value)
    except GeographyInvalidFormatError:
        raise _invalid_format("municipalityCode must be 6 digits", "Parameter municipalityCode musí byť 6-ciferný")


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


def _parse_bool(value: str | None, field_name: str) -> bool | None:
    if value is None:
        return None

    normalized = value.strip().casefold()
    if normalized in {"true", "1", "yes", "on"}:
        return True
    if normalized in {"false", "0", "no", "off"}:
        return False

    raise _invalid_format(f"{field_name} must be true or false", f"Parameter {field_name} musí byť true alebo false")


@router.get(
    "",
    summary="List PSC records",
    description="Returns the static PSC dataset with pagination and filters.",
)
def list_psc_endpoint(
    response: Response,
    psc: str | None = Query(default=None, description="Optional PSC filter."),
    regionCode: str | None = Query(default=None, description="Optional region code filter."),
    districtCode: str | None = Query(default=None, description="Optional district code filter."),
    municipalityCode: str | None = Query(default=None, description="Optional municipality code filter."),
    deliveryPost: str | None = Query(default=None, description="Optional delivery post substring filter."),
    municipalityName: str | None = Query(default=None, description="Optional municipality name substring filter."),
    hasGeography: str | None = Query(default=None, description="Optional geography presence filter."),
    limit: str | None = Query(default=None, description="Optional page size."),
    offset: str | None = Query(default=None, description="Optional result offset."),
) -> dict[str, object]:
    filters: dict[str, object] = {}
    normalized_psc = _parse_optional_psc(psc)
    normalized_region_code = _parse_optional_region_code(regionCode)
    normalized_district_code = _parse_optional_district_code(districtCode)
    normalized_municipality_code = _parse_optional_municipality_code(municipalityCode)
    normalized_has_geography = _parse_bool(hasGeography, "hasGeography")
    parsed_limit = _parse_optional_limit(limit, default=100, maximum=500, field_name="limit")
    parsed_offset = _parse_offset(offset)

    if normalized_psc is not None:
        filters["psc"] = normalized_psc
    if normalized_region_code is not None:
        filters["regionCode"] = normalized_region_code
    if normalized_district_code is not None:
        filters["districtCode"] = normalized_district_code
    if normalized_municipality_code is not None:
        filters["municipalityCode"] = normalized_municipality_code
    if deliveryPost is not None:
        filters["deliveryPost"] = deliveryPost
    if municipalityName is not None:
        filters["municipalityName"] = municipalityName
    if normalized_has_geography is not None:
        filters["hasGeography"] = normalized_has_geography

    filtered = filter_psc_records(filters)
    page = list_psc_records(filters, limit=parsed_limit, offset=parsed_offset)

    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(
        data={
            "items": page,
            "count": len(page),
            "total": len(filtered),
            "limit": parsed_limit,
            "offset": parsed_offset,
        },
        source=f"{API_SOURCE} static PSC dataset",
        last_updated=PSC_LAST_UPDATED,
    )


@router.get(
    "/search",
    summary="Search PSC records",
    description="Searches the static PSC dataset by query string.",
)
def search_psc_endpoint(
    response: Response,
    q: str | None = Query(default=None, description="Search query."),
    limit: str | None = Query(default=None, description="Optional page size."),
    offset: str | None = Query(default=None, description="Optional result offset."),
) -> dict[str, object]:
    if q is None:
        raise _invalid_format("q is required", "Parameter q je povinný")

    normalized_query = q.strip()
    if not normalized_query:
        raise _invalid_format("q is required", "Parameter q je povinný")

    parsed_limit = _parse_optional_limit(limit, default=50, maximum=200, field_name="limit")
    parsed_offset = _parse_offset(offset)

    try:
        all_matches = search_psc_records(normalized_query)
        page = search_psc(normalized_query, limit=parsed_limit, offset=parsed_offset)
    except PSCInvalidFormatError:
        raise _invalid_format("q must be at least 2 characters or a 5-digit PSC", "Parameter q musí mať aspoň 2 znaky alebo byť 5-ciferné PSČ")

    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(
        data={
            "items": page,
            "count": len(page),
            "total": len(all_matches),
            "limit": parsed_limit,
            "offset": parsed_offset,
        },
        source=f"{API_SOURCE} static PSC dataset",
        last_updated=PSC_LAST_UPDATED,
    )


@router.get(
    "/stats",
    summary="PSC dataset stats",
    description="Returns lightweight local statistics for the PSC dataset.",
)
def stats_psc_endpoint(response: Response) -> dict[str, object]:
    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(
        data=get_psc_stats(),
        source=f"{API_SOURCE} static PSC dataset",
        last_updated=PSC_LAST_UPDATED,
    )


@router.get(
    "/{psc}",
    summary="Postal code lookup",
    description="Looks up a Slovak postal code in the expanded static PSC dataset.",
)
def get_psc(
    psc: str,
    response: Response,
    include: str | None = Query(default=None, description="Optional response expansion. Supported value: geography."),
) -> dict[str, object]:
    include_geography = False
    if include is not None:
        if include != "geography":
            raise _invalid_format("include must be omitted or set to geography", "Parameter include musí byť vynechaný alebo nastavený na geography")
        include_geography = True

    try:
        psc_result = lookup_psc(psc, include_geography=include_geography)
    except PSCInvalidFormatError:
        raise _invalid_format(
            "PSC must be a 5-digit Slovak postal code",
            "PSČ musí byť 5-ciferné slovenské poštové číslo",
        )
    except PSCNotFoundError:
        normalized = psc.replace(" ", "")
        raise HTTPException(
            status_code=404,
            detail=error_detail(
                code="NOT_FOUND",
                message=f"No PSC data available for {normalized}",
                message_sk=f"Pre PSČ {normalized} nie sú dostupné údaje",
            ),
            headers={"Cache-Control": STATIC_CACHE_CONTROL},
        )

    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    source = f"{API_SOURCE} static PSC dataset"
    if include_geography:
        source = PSC_GEOGRAPHY_SOURCE
    return success_response(
        data=psc_result,
        source=source,
        last_updated=PSC_LAST_UPDATED,
    )
