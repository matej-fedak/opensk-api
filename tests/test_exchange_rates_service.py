"""Service-layer behavior for the materialized ECB reference-rate snapshot."""

import pytest

from schemas.common import EXCHANGE_RATES_LAST_UPDATED
from services.exchange_rates_service import (
    DATA_PATH,
    RateDateNotFoundError,
    RateNotAvailableError,
    UnsupportedCurrencyError,
    earliest_date,
    get_for_date,
    get_latest,
    latest_date,
    metadata,
    reset_cache,
    supported_currencies,
)


@pytest.fixture(autouse=True)
def _fresh_service_cache():
    reset_cache()
    yield
    reset_cache()


def test_dataset_loads_and_matches_central_freshness_constant() -> None:
    meta = metadata()
    assert meta["baseCurrency"] == "EUR"
    assert meta["publisher"] == "European Central Bank"
    assert meta["sourceUrl"].endswith("eurofxref-hist.xml")
    assert meta["dateCount"] == len(meta_dates())
    assert earliest_date() == "1999-01-04"
    assert latest_date() == meta["latestDate"] == meta["lastUpdated"] == EXCHANGE_RATES_LAST_UPDATED


def meta_dates() -> list[str]:
    import json

    return [entry["date"] for entry in json.loads(DATA_PATH.read_text(encoding="utf-8"))["dates"]]


def test_latest_resolves_newest_publication_date() -> None:
    record = get_latest()
    assert record["date"] == latest_date()
    assert record["base"] == "EUR"
    assert record["directionSemantics"] == "1 EUR = rate units of the foreign currency"
    assert "information purposes only" in record["notice"]
    assert record["rates"] and all(isinstance(rate, str) for rate in record["rates"].values())


def test_exact_historical_date_resolves_verbatim_lexemes() -> None:
    record = get_for_date("1999-01-04")
    assert record["date"] == "1999-01-04"
    assert record["rates"]["USD"] == "1.1789"
    assert record["rates"]["SKK"] == "42.991"


def test_lookup_is_deterministic_across_calls() -> None:
    assert get_for_date("2005-01-03") == get_for_date("2005-01-03")
    assert get_latest() == get_latest()


def test_no_weekend_or_neighbor_fallback() -> None:
    # 2026-10-10 is a Saturday; ECB published nothing and nothing must fall back.
    with pytest.raises(RateDateNotFoundError):
        get_for_date("2026-10-10")


def test_before_coverage_and_far_future_are_not_found() -> None:
    for day in ("1998-12-31", "2099-01-01"):
        with pytest.raises(RateDateNotFoundError):
            get_for_date(day)


def test_supported_currencies_cover_historical_series() -> None:
    currencies = supported_currencies()
    assert {"USD", "SKK", "TRL", "RUB", "TRY"} <= set(currencies)
    assert "EUR" not in currencies
    assert currencies == sorted(currencies)


def test_currency_filter_is_normalized_and_verbatim() -> None:
    assert get_latest(" usd ")["rates"] == {"USD": get_latest("USD")["rates"]["USD"]}
    record = get_for_date("2008-12-31", "skk")
    assert record["rates"] == {"SKK": "30.126"}  # fixed conversion-rate lexeme preserved


def test_unknown_currency_is_unsupported_not_not_found() -> None:
    with pytest.raises(UnsupportedCurrencyError):
        get_latest("XXX")


def test_historically_retired_currency_has_no_rate_on_latest() -> None:
    with pytest.raises(RateNotAvailableError):
        get_latest("SKK")
    with pytest.raises(RateNotAvailableError):
        get_for_date(latest_date(), "RUB")  # suspended since 2022-03-01


def test_eur_quote_is_never_served() -> None:
    with pytest.raises(UnsupportedCurrencyError):
        get_latest("EUR")
