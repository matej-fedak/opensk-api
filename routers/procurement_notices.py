from fastapi import APIRouter, HTTPException, Query, Response

from schemas.common import API_SOURCE, PROCUREMENT_NOTICES_LAST_UPDATED, SEARCH_CACHE_CONTROL, STATIC_CACHE_CONTROL, error_detail, success_response
from services.procurement_notice_service import (
    PROCUREMENT_NOTICE_LIST_DEFAULT_LIMIT,
    PROCUREMENT_NOTICE_LIST_MAX_LIMIT,
    PROCUREMENT_NOTICE_SEARCH_DEFAULT_LIMIT,
    PROCUREMENT_NOTICE_SEARCH_MAX_LIMIT,
    filter_procurement_notice_records,
    get_procurement_notice_by_id,
    get_procurement_notice_stats,
    list_procurement_notices,
    search_procurement_notices,
)


router = APIRouter(prefix="/procurement-notices", tags=["procurement-notices"])
_PROCUREMENT_NOTICE_SOURCE = f"{API_SOURCE} static TED_PARTIAL procurement notice snapshot"


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


@router.get(
    "",
    summary="List public procurement notices",
    description="Returns a checked-in partial TED Search API snapshot of Slovak-buyer public procurement notices. This is not the complete national ÚVO procurement register.",
)
def list_procurement_notices_endpoint(
    response: Response,
    noticeType: str | None = Query(default=None, description="Optional TED notice-type filter."),
    year: int | None = Query(default=None, ge=2000, le=2100, description="Optional publication-year filter."),
    limit: str | None = Query(default=None, description="Optional page size."),
    offset: str | None = Query(default=None, description="Optional result offset."),
) -> dict[str, object]:
    filters: dict[str, object] = {}
    if noticeType is not None:
        filters["noticeType"] = noticeType
    if year is not None:
        filters["year"] = year

    parsed_limit = _parse_optional_limit(limit, default=PROCUREMENT_NOTICE_LIST_DEFAULT_LIMIT, maximum=PROCUREMENT_NOTICE_LIST_MAX_LIMIT, field_name="limit")
    parsed_offset = _parse_offset(offset)
    filtered = filter_procurement_notice_records(filters)
    page = list_procurement_notices(filters, limit=parsed_limit, offset=parsed_offset)
    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(
        data={"items": page, "count": len(page), "total": len(filtered), "limit": parsed_limit, "offset": parsed_offset},
        source=_PROCUREMENT_NOTICE_SOURCE,
        last_updated=PROCUREMENT_NOTICES_LAST_UPDATED,
    )


@router.get(
    "/search",
    summary="Search public procurement notices",
    description="Searches the checked-in partial TED snapshot by publication number, notice title, buyer name, or place city. The endpoint does not call upstream TED or ÚVO services.",
)
def search_procurement_notices_endpoint(
    response: Response,
    q: str | None = Query(default=None, description="Search text for id, title, buyer names, or place city."),
    noticeType: str | None = Query(default=None, description="Optional TED notice-type filter."),
    year: int | None = Query(default=None, ge=2000, le=2100, description="Optional publication-year filter."),
    limit: str | None = Query(default=None, description="Optional page size."),
    offset: str | None = Query(default=None, description="Optional result offset."),
) -> dict[str, object]:
    if q is None or not q.strip():
        raise _invalid_format("q must be a non-empty search string", "Parameter q nesmie byť prázdny")

    filters: dict[str, object] = {}
    if noticeType is not None:
        filters["noticeType"] = noticeType
    if year is not None:
        filters["year"] = year

    parsed_limit = _parse_optional_limit(limit, default=PROCUREMENT_NOTICE_SEARCH_DEFAULT_LIMIT, maximum=PROCUREMENT_NOTICE_SEARCH_MAX_LIMIT, field_name="limit")
    parsed_offset = _parse_offset(offset)
    page, total = search_procurement_notices(q, filters=filters, limit=parsed_limit, offset=parsed_offset)
    response.headers["Cache-Control"] = SEARCH_CACHE_CONTROL
    return success_response(
        data={"items": page, "count": len(page), "total": total, "limit": parsed_limit, "offset": parsed_offset, "query": q.strip()},
        source=_PROCUREMENT_NOTICE_SOURCE,
        last_updated=PROCUREMENT_NOTICES_LAST_UPDATED,
    )


@router.get(
    "/stats",
    summary="Public procurement notice snapshot stats",
    description="Returns totals for the checked-in TED_PARTIAL public procurement notice snapshot, explicitly including partial-coverage flags.",
)
def get_procurement_notice_stats_endpoint(response: Response) -> dict[str, object]:
    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(
        data=get_procurement_notice_stats(),
        source=_PROCUREMENT_NOTICE_SOURCE,
        last_updated=PROCUREMENT_NOTICES_LAST_UPDATED,
    )


@router.get(
    "/{id}",
    summary="Public procurement notice by TED publication number",
    description="Returns one record from the checked-in partial TED snapshot. The source URL links back to TED XML, but the API does not fetch or serve raw XML/PDF/HTML.",
)
def get_procurement_notice_endpoint(id: str, response: Response) -> dict[str, object]:
    record = get_procurement_notice_by_id(id)
    if record is None:
        raise HTTPException(
            status_code=404,
            detail=error_detail(code="NOT_FOUND", message="Procurement notice not found in the local TED_PARTIAL snapshot", message_sk="Oznámenie verejného obstarávania sa nenašlo v lokálnej TED_PARTIAL databáze"),
            headers={"Cache-Control": STATIC_CACHE_CONTROL},
        )
    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(
        data=record,
        source=_PROCUREMENT_NOTICE_SOURCE,
        last_updated=PROCUREMENT_NOTICES_LAST_UPDATED,
    )
