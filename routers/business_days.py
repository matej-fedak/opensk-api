from datetime import date

from fastapi import APIRouter, HTTPException, Query, Response

from schemas.common import API_SOURCE, HOLIDAYS_LAST_UPDATED, STATIC_CACHE_CONTROL, error_detail, success_response
from services.business_days_service import (
    BusinessDayInvalidError,
    BusinessDayUnsupportedYearError,
    MAX_DAYS_DELTA,
    add_business_days,
    business_days_between,
    holiday_names,
    is_business_day,
    parse_iso_date,
    supported_years,
)


router = APIRouter(prefix="/business-days", tags=["business-days"])

_BUSINESS_DAYS_SOURCE = f"{API_SOURCE} static holidays dataset"


def _invalid_format(message: str, message_sk: str) -> HTTPException:
    return HTTPException(
        status_code=400,
        detail=error_detail(code="INVALID_FORMAT", message=message, message_sk=message_sk),
        headers={"Cache-Control": STATIC_CACHE_CONTROL},
    )


def _unsupported_year(exc: BusinessDayUnsupportedYearError) -> HTTPException:
    supported = ", ".join(str(year) for year in exc.supported)
    return HTTPException(
        status_code=400,
        detail=error_detail(
            code="UNSUPPORTED_YEAR",
            message=f"Year {exc.year} is outside verified holiday coverage ({supported})",
            message_sk=f"Rok {exc.year} je mimo overeného pokrytia sviatkov ({supported})",
        ),
        headers={"Cache-Control": STATIC_CACHE_CONTROL},
    )


def _parse_days(value: str | None) -> int:
    if value is None:
        raise _invalid_format("days is required", "Parameter days je povinný")
    normalized = value.strip()
    integer = normalized.startswith("-") and normalized[1:].isdigit() or normalized.isdigit()
    if not integer:
        raise _invalid_format("days must be an integer", "Parameter days musí byť celé číslo")
    parsed = int(normalized)
    if abs(parsed) > MAX_DAYS_DELTA:
        raise _invalid_format(
            f"days must be between -{MAX_DAYS_DELTA} and {MAX_DAYS_DELTA}",
            f"Parameter days musí byť medzi -{MAX_DAYS_DELTA} a {MAX_DAYS_DELTA}",
        )
    return parsed


def _describe(day: date) -> dict[str, object]:
    weekend = day.weekday() >= 5
    holiday_name = holiday_names().get(day)
    return {
        "date": day.isoformat(),
        "weekday": day.weekday(),
        "isWeekend": weekend,
        "isHoliday": holiday_name is not None,
        "holidayName": holiday_name,
        "isBusinessDay": is_business_day(day),
        "supportedYears": supported_years(),
    }


@router.get(
    "/check",
    summary="Check a business day",
    description="Returns whether an ISO date is a Slovak business day (Monday-Friday, not a known public holiday).",
)
def check_business_day(
    response: Response,
    date_: str | None = Query(default=None, alias="date", description="ISO date to check."),
) -> dict[str, object]:
    if date_ is None:
        raise _invalid_format("date is required", "Parameter date je povinný")
    try:
        day = parse_iso_date(date_, "date")
        payload = _describe(day)
    except BusinessDayInvalidError:
        raise _invalid_format("date must be an ISO date (YYYY-MM-DD)", "Parameter date musí byť dátum vo formáte RRRR-MM-DD")
    except BusinessDayUnsupportedYearError as exc:
        raise _unsupported_year(exc)

    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(data=payload, source=_BUSINESS_DAYS_SOURCE, last_updated=HOLIDAYS_LAST_UPDATED)


@router.get(
    "/add",
    summary="Add business days",
    description="Adds (or subtracts) business days from an ISO date using local Slovak holiday data.",
)
def add_business_days_endpoint(
    response: Response,
    date_: str | None = Query(default=None, alias="date", description="ISO start date."),
    days: str | None = Query(default=None, description="Business days to add (negative to subtract)."),
) -> dict[str, object]:
    if date_ is None:
        raise _invalid_format("date is required", "Parameter date je povinný")
    parsed_days = _parse_days(days)
    try:
        start = parse_iso_date(date_, "date")
        result = add_business_days(start, parsed_days)
    except BusinessDayInvalidError:
        raise _invalid_format("date must be an ISO date (YYYY-MM-DD)", "Parameter date musí byť dátum vo formáte RRRR-MM-DD")
    except BusinessDayUnsupportedYearError as exc:
        raise _unsupported_year(exc)

    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(
        data={
            "date": start.isoformat(),
            "days": parsed_days,
            "result": result.isoformat(),
            "resultIsBusinessDay": True,
            "supportedYears": supported_years(),
        },
        source=_BUSINESS_DAYS_SOURCE,
        last_updated=HOLIDAYS_LAST_UPDATED,
    )


@router.get(
    "/between",
    summary="Count business days",
    description="Counts business days in a bounded inclusive ISO date interval using local Slovak holiday data.",
)
def business_days_between_endpoint(
    response: Response,
    from_: str | None = Query(default=None, alias="from", description="ISO start date (inclusive)."),
    to: str | None = Query(default=None, description="ISO end date (inclusive)."),
) -> dict[str, object]:
    if from_ is None:
        raise _invalid_format("from is required", "Parameter from je povinný")
    if to is None:
        raise _invalid_format("to is required", "Parameter to je povinný")
    try:
        start = parse_iso_date(from_, "from")
        end = parse_iso_date(to, "to")
        payload = business_days_between(start, end)
    except BusinessDayInvalidError as exc:
        raise _invalid_format(str(exc), "Parametre from a to musia byť platné ISO dátumy a from nesmie byť po to")
    except BusinessDayUnsupportedYearError as exc:
        raise _unsupported_year(exc)

    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(data=payload, source=_BUSINESS_DAYS_SOURCE, last_updated=HOLIDAYS_LAST_UPDATED)
