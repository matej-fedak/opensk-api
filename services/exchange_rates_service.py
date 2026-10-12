"""Offline access to the materialized ECB euro reference-rate snapshot.

The production dataset `data/exchange_rates.json` is built by
`scripts/import_exchange_rates.py` from the official ECB eurofxref
full-history feed and checked in. This service only reads that local file:
no network access, no database, no upstream dependency at runtime.

Rates are reproduced as exact decimal strings (`1 EUR = <rate> units of the
foreign currency`). Publication dates are exact ECB dates only — no weekend,
TARGET-closure or business-day fallback exists here.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "exchange_rates.json"


class ExchangeRatesError(Exception):
    """Base class for exchange-rate lookup failures."""


class RateDateNotFoundError(ExchangeRatesError):
    """No ECB publication exists for the exact requested date."""

    def __init__(self, day: str) -> None:
        super().__init__(day)
        self.day = day


class UnsupportedCurrencyError(ExchangeRatesError):
    """Well-formed currency code that never appears in the dataset."""

    def __init__(self, currency: str) -> None:
        super().__init__(currency)
        self.currency = currency


class RateNotAvailableError(ExchangeRatesError):
    """Currency exists in dataset history but not on the requested date."""

    def __init__(self, currency: str, day: str) -> None:
        super().__init__(currency)
        self.currency = currency
        self.day = day


@lru_cache(maxsize=1)
def _payload() -> dict[str, Any]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _index() -> dict[str, dict[str, str]]:
    return {entry["date"]: entry["rates"] for entry in _payload()["dates"]}


@lru_cache(maxsize=1)
def _currencies() -> frozenset[str]:
    return frozenset(currency for rates in _index().values() for currency in rates)


def reset_cache() -> None:
    """Test hook: drop process-local caches."""
    _payload.cache_clear()
    _index.cache_clear()
    _currencies.cache_clear()


def metadata() -> dict[str, Any]:
    return dict(_payload()["metadata"])


def earliest_date() -> str:
    return _payload()["metadata"]["earliestDate"]


def latest_date() -> str:
    return _payload()["metadata"]["latestDate"]


def supported_currencies() -> list[str]:
    """All currencies present anywhere in the snapshot (historical ones included)."""
    return sorted(_currencies())


def _resolve_currency(currency: str) -> str:
    normalized = currency.strip().upper()
    if normalized not in _currencies():
        raise UnsupportedCurrencyError(normalized)
    return normalized


def _pick_rates(day: str, currency: str | None) -> dict[str, str]:
    rates = _index().get(day)
    if rates is None:
        raise RateDateNotFoundError(day)
    if currency is None:
        return dict(rates)
    normalized = _resolve_currency(currency)
    if normalized not in rates:
        raise RateNotAvailableError(normalized, day)
    return {normalized: rates[normalized]}


def get_latest(currency: str | None = None) -> dict[str, Any]:
    return get_for_date(latest_date(), currency)


def get_for_date(day: str, currency: str | None = None) -> dict[str, Any]:
    """Exact publication date only; never a neighbouring/fallback date."""
    rates = _pick_rates(day, currency)
    meta = metadata()
    return {
        "date": day,
        "base": meta["baseCurrency"],
        "directionSemantics": meta["directionSemantics"],
        "rates": rates,
        "notice": meta["notice"],
    }
