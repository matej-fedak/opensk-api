import re
from datetime import date as calendar_date

from fastapi import APIRouter, HTTPException, Query, Response

from schemas.common import (
    EXCHANGE_RATES_LAST_UPDATED,
    META_CACHE_CONTROL,
    STATIC_CACHE_CONTROL,
    error_detail,
)
from schemas.exchange_rates import ExchangeRateDayResponse, ExchangeRatesData, ExchangeRatesResponseMetadata
from services.exchange_rates_service import (
    RateDateNotFoundError,
    RateNotAvailableError,
    UnsupportedCurrencyError,
    get_for_date,
    get_latest,
    supported_currencies,
)

router = APIRouter(prefix="/exchange-rates", tags=["exchange-rates"])

_SOURCE = "European Central Bank — euro foreign exchange reference rates (materialized by OpenSK API)"

_DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
_CURRENCY_QUERY_RE = re.compile(r"[A-Za-z]{3}")

_COMMON_DESCRIPTION = (
    "Source: European Central Bank euro foreign exchange reference rates, transformed "
    "by OpenSK from the official ECB eurofxref XML feed into normalized JSON (rate values "
    "reproduced verbatim as decimal strings; no rounding, inversion or arithmetic). "
    "Direction: `1 EUR = rate units of the foreign currency` (USD = \"1.16\" means "
    "1 EUR = 1.16 USD). Rates are published by the ECB for information purposes only; "
    "the ECB strongly discourages using them for transaction or settlement purposes, and "
    "they are not live market prices. Currency availability changes historically (legacy "
    "euro-area and suspended series are included)."
)


def _http_error(status_code: int, code: str, message: str, message_sk: str,
                cache_control: str = STATIC_CACHE_CONTROL) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail=error_detail(code=code, message=message, message_sk=message_sk),
        headers={"Cache-Control": cache_control},
    )


def _normalize_currency(currency: str | None) -> str | None:
    if currency is None:
        return None
    candidate = currency.strip()
    if not _CURRENCY_QUERY_RE.fullmatch(candidate):
        raise _http_error(
            400, "INVALID_FORMAT",
            f"currency must be a three-letter ISO 4217 code, got: {currency!r}",
            f"Parameter currency musí byť trojpísmenový kód ISO 4217, zadané: {currency!r}",
        )
    return candidate.upper()


def _envelope(data: ExchangeRatesData, cache_control: str,
              response: Response) -> ExchangeRateDayResponse:
    response.headers["Cache-Control"] = cache_control
    return ExchangeRateDayResponse(
        data=data,
        metadata=ExchangeRatesResponseMetadata(
            source=_SOURCE, lastUpdated=EXCHANGE_RATES_LAST_UPDATED, version="v1"),
        error=None,
    )


def _respond(day: str | None, currency: str | None, cache_control: str,
             response: Response) -> ExchangeRateDayResponse:
    normalized = _normalize_currency(currency)
    try:
        record = get_latest(normalized) if day is None else get_for_date(day, normalized)
    except UnsupportedCurrencyError as exc:
        if normalized == "EUR":
            raise _http_error(
                400, "UNSUPPORTED_CURRENCY",
                "EUR is the fixed base currency and is never quoted against itself "
                "(every rate already means 1 EUR = rate units of the foreign currency)",
                "EUR je pevná základná mena a nikdy nie je kotované samo proti sebe",
            )
        raise _http_error(
            400, "UNSUPPORTED_CURRENCY",
            f"Currency {exc.currency} has no rate anywhere in the ECB reference-rate "
            f"snapshot; supported: {', '.join(supported_currencies())}",
            f"Mena {exc.currency} sa v snímke referenčných kurzov ECB nenachádza",
        )
    except RateDateNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=error_detail(
                code="RATE_DATE_NOT_FOUND",
                message=f"No ECB reference-rate publication exists for the exact date {exc.day}. "
                        "ECB publishes on TARGET working days only; OpenSK returns no "
                        "fallback or nearest date.",
                message_sk=f"Pre presný dátum {exc.day} neexistuje publikácia referenčných kurzov ECB",
            ),
            headers={"Cache-Control": cache_control},
        )
    except RateNotAvailableError as exc:
        raise HTTPException(
            status_code=404,
            detail=error_detail(
                code="RATE_NOT_AVAILABLE",
                message=f"Currency {exc.currency} exists in the snapshot's history but has "
                        f"no ECB reference rate on {exc.day}.",
                message_sk=f"Mena {exc.currency} nemá pre dátum {exc.day} referenčný kurz ECB",
            ),
            headers={"Cache-Control": cache_control},
        )
    return _envelope(ExchangeRatesData(**record), cache_control, response)


@router.get(
    "/latest",
    summary="Latest ECB EUR reference rates in the OpenSK snapshot",
    description=(
        "Returns the newest ECB publication date available in the current materialized "
        "OpenSK snapshot — not a live or today's market rate; the snapshot may lag the "
        "latest ECB publication until refreshed offline. " + _COMMON_DESCRIPTION
    ),
    response_model=ExchangeRateDayResponse,
)
def get_latest_rates(
    response: Response,
    currency: str | None = Query(
        default=None,
        description="Optional ISO 4217 alpha-3 currency filter (case-insensitive)."),
) -> ExchangeRateDayResponse:
    return _respond(None, currency, META_CACHE_CONTROL, response)


@router.get(
    "/{date}",
    summary="ECB EUR reference rates for an exact publication date",
    description=(
        "Returns the ECB rate set published on exactly `{date}` (ISO YYYY-MM-DD). "
        "If the ECB published nothing on that date (weekend, TARGET holiday, or a date "
        "outside snapshot coverage), the response is 404 — never a neighbouring, "
        "previous or nearest date. " + _COMMON_DESCRIPTION
    ),
    response_model=ExchangeRateDayResponse,
)
def get_rates_for_date(
    date: str,
    response: Response,
    currency: str | None = Query(
        default=None,
        description="Optional ISO 4217 alpha-3 currency filter (case-insensitive)."),
) -> ExchangeRateDayResponse:
    if not _DATE_RE.fullmatch(date):
        raise _http_error(
            400, "INVALID_FORMAT",
            f"date must be an ISO YYYY-MM-DD calendar date, got: {date!r}",
            f"Dátum musí byť kalendárny dátum vo formáte RRRR-MM-DD, zadané: {date!r}",
        )
    try:
        calendar_date.fromisoformat(date)
    except ValueError:
        raise _http_error(
            400, "INVALID_FORMAT",
            f"date must be an existing calendar date, got: {date!r}",
            f"Dátum musí byť existujúci kalendárny dátum, zadané: {date!r}",
        )
    return _respond(date, currency, STATIC_CACHE_CONTROL, response)
