"""Public contract for GET /v1/exchange-rates/latest and /v1/exchange-rates/{date}."""

from email.utils import format_datetime, parsedate_to_datetime

import pytest
from fastapi.testclient import TestClient

from main import app
from schemas.common import EXCHANGE_RATES_LAST_UPDATED

client = TestClient(app)

LATEST = "/v1/exchange-rates/latest"
HISTORICAL = "/v1/exchange-rates/1999-01-04"
SOURCE = "European Central Bank — euro foreign exchange reference rates (materialized by OpenSK API)"


def _body(response) -> dict:  # noqa: ANN001 - tiny test helper
    assert response.headers["content-type"].startswith("application/json")
    return response.json()


# --- envelope and payload semantics -------------------------------------------------


def test_latest_returns_snapshot_latest_with_standard_envelope() -> None:
    response = client.get(LATEST)
    assert response.status_code == 200
    body = _body(response)
    assert set(body) == {"data", "metadata", "error"}
    assert body["error"] is None
    data = body["data"]
    assert data["date"] == EXCHANGE_RATES_LAST_UPDATED
    assert data["base"] == "EUR"
    assert data["directionSemantics"] == "1 EUR = rate units of the foreign currency"
    assert "information purposes only" in data["notice"]
    assert isinstance(data["rates"], dict) and len(data["rates"]) > 1
    assert all(isinstance(rate, str) for rate in data["rates"].values())
    metadata = body["metadata"]
    assert metadata["source"] == SOURCE
    assert metadata["lastUpdated"] == EXCHANGE_RATES_LAST_UPDATED
    assert metadata["version"] == "v1"


def test_exact_date_returns_that_date_not_a_neighbor() -> None:
    response = client.get(HISTORICAL)
    assert response.status_code == 200
    data = _body(response)["data"]
    assert data["date"] == "1999-01-04"
    assert data["rates"]["USD"] == "1.1789"
    assert data["rates"]["SKK"] == "42.991"


def test_historical_response_shows_dataset_freshness_not_observation_date() -> None:
    body = _body(client.get(HISTORICAL))
    assert body["data"]["date"] == "1999-01-04"
    assert body["metadata"]["lastUpdated"] == EXCHANGE_RATES_LAST_UPDATED


def test_weekend_exact_date_is_404_not_a_fallback() -> None:
    response = client.get("/v1/exchange-rates/2026-10-10")  # Saturday
    assert response.status_code == 404
    body = _body(response)
    assert body["data"] is None
    assert body["error"]["code"] == "RATE_DATE_NOT_FOUND"
    assert "messageSk" in body["error"]
    assert body["metadata"]["version"] == "v1"


@pytest.mark.parametrize("day", ["1998-12-31", "2099-01-01"])
def test_out_of_coverage_dates_are_404(day: str) -> None:
    response = client.get(f"/v1/exchange-rates/{day}")
    assert response.status_code == 404
    assert _body(response)["error"]["code"] == "RATE_DATE_NOT_FOUND"


@pytest.mark.parametrize("day", ["2026-1-4", "20260104", "2026-13-04T00:00", "latest2"])
def test_malformed_dates_are_400_invalid_format(day: str) -> None:
    response = client.get(f"/v1/exchange-rates/{day}")
    assert response.status_code == 400
    assert _body(response)["error"]["code"] == "INVALID_FORMAT"


@pytest.mark.parametrize("day", ["2026-02-30", "2026-13-40", "2025-02-29"])
def test_impossible_calendar_dates_are_400_not_404(day: str) -> None:
    # Shape-valid but nonexistent calendar dates are malformed input, not "no publication".
    response = client.get(f"/v1/exchange-rates/{day}")
    assert response.status_code == 400
    assert _body(response)["error"]["code"] == "INVALID_FORMAT"


def test_latest_is_not_swallowed_by_dynamic_date_route() -> None:
    response = client.get(LATEST)
    assert response.status_code == 200
    assert _body(response)["data"]["date"] == EXCHANGE_RATES_LAST_UPDATED


# --- currency filter -----------------------------------------------------------------


def test_currency_filter_returns_single_key_same_shape() -> None:
    response = client.get(LATEST, params={"currency": "USD"})
    assert response.status_code == 200
    data = _body(response)["data"]
    assert set(data["rates"]) == {"USD"}
    assert isinstance(data["rates"]["USD"], str)
    assert data["base"] == "EUR"  # shape must not become a scalar/other object


def test_currency_filter_is_case_insensitive_and_trimmed() -> None:
    lowercase = _body(client.get(LATEST, params={"currency": " usd "}))["data"]["rates"]
    uppercase = _body(client.get(LATEST, params={"currency": "USD"}))["data"]["rates"]
    assert lowercase == uppercase


@pytest.mark.parametrize("value", ["US", "USD2", "EU R", "💶"])
def test_malformed_currency_is_400_invalid_format(value: str) -> None:
    response = client.get(LATEST, params={"currency": value})
    assert response.status_code == 400
    assert _body(response)["error"]["code"] == "INVALID_FORMAT"


def test_never_present_currency_is_400_unsupported() -> None:
    response = client.get(LATEST, params={"currency": "XXX"})
    assert response.status_code == 400
    body = _body(response)
    assert body["error"]["code"] == "UNSUPPORTED_CURRENCY"
    assert "USD" in body["error"]["message"]  # lists what's actually supported


def test_historically_retired_currency_is_404_on_latest_but_200_on_its_date() -> None:
    missing = client.get(LATEST, params={"currency": "SKK"})
    assert missing.status_code == 404
    assert _body(missing)["error"]["code"] == "RATE_NOT_AVAILABLE"

    historical = client.get("/v1/exchange-rates/2008-12-31", params={"currency": "SKK"})
    assert historical.status_code == 200
    assert _body(historical)["data"]["rates"] == {"SKK": "30.126"}


def test_suspended_series_is_404_on_latest() -> None:
    response = client.get(LATEST, params={"currency": "RUB"})  # suspended since 2022-03-01
    assert response.status_code == 404
    assert _body(response)["error"]["code"] == "RATE_NOT_AVAILABLE"


def test_filter_on_missing_date_still_reports_date_error() -> None:
    response = client.get("/v1/exchange-rates/2026-10-10", params={"currency": "USD"})
    assert response.status_code == 404
    assert _body(response)["error"]["code"] == "RATE_DATE_NOT_FOUND"


def test_eur_is_never_an_acceptable_currency_filter() -> None:
    response = client.get(LATEST, params={"currency": "EUR"})
    assert response.status_code == 400
    error = _body(response)["error"]
    assert error["code"] == "UNSUPPORTED_CURRENCY"
    assert "base currency" in error["message"]


# --- HTTP caching ---------------------------------------------------------------------


def test_latest_cache_policy_is_short_and_conditional() -> None:
    response = client.get(LATEST)
    assert response.headers["cache-control"] == "public, max-age=3600"
    assert "etag" in response.headers
    assert "last-modified" in response.headers
    assert parsedate_to_datetime(response.headers["last-modified"]).date().isoformat() == \
        EXCHANGE_RATES_LAST_UPDATED


def test_exact_date_cache_policy_is_daily_stable() -> None:
    response = client.get(HISTORICAL)
    assert response.headers["cache-control"] == "public, max-age=86400"
    assert "etag" in response.headers and "last-modified" in response.headers


def test_if_none_match_returns_304_on_both_routes() -> None:
    for path in (LATEST, HISTORICAL, f"{LATEST}?currency=USD"):
        etag = client.get(path).headers["etag"]
        again = client.get(path, headers={"If-None-Match": etag})
        assert again.status_code == 304
        assert again.headers["etag"] == etag


def test_if_modified_since_returns_304() -> None:
    last_modified = client.get(HISTORICAL).headers["last-modified"]
    again = client.get(HISTORICAL, headers={"If-Modified-Since": last_modified})
    assert again.status_code == 304


def test_currency_filter_changes_etag_and_cache_policy_stays_route_bound() -> None:
    full = client.get(LATEST)
    filtered = client.get(LATEST, params={"currency": "USD"})
    assert full.headers["etag"] != filtered.headers["etag"]
    assert filtered.headers["cache-control"] == "public, max-age=3600"
    exact_filtered = client.get(HISTORICAL, params={"currency": "USD"})
    assert exact_filtered.headers["cache-control"] == "public, max-age=86400"


def test_last_modified_matches_snapshot_freshness_constant() -> None:
    for path in (LATEST, HISTORICAL):
        stamp = parsedate_to_datetime(client.get(path).headers["last-modified"])
        assert stamp == parsedate_to_datetime(
            format_datetime(__import__("datetime").datetime.combine(
                __import__("datetime").date.fromisoformat(EXCHANGE_RATES_LAST_UPDATED),
                __import__("datetime").time.min,
                tzinfo=__import__("datetime").UTC,
            ), usegmt=True))


# --- OpenAPI surface ------------------------------------------------------------------


def test_openapi_exposes_typed_exchange_rate_contract() -> None:
    openapi = client.get("/openapi.json").json()
    assert "/v1/exchange-rates/latest" in openapi["paths"]
    assert "/v1/exchange-rates/{date}" in openapi["paths"]
    assert sum("get" in methods for methods in openapi["paths"].values()) == 42
    tags = {tag["name"] for tag in openapi["tags"]}
    assert "exchange-rates" in tags
    route = openapi["paths"]["/v1/exchange-rates/latest"]["get"]
    assert route["tags"] == ["exchange-rates"]
    description = route["description"].lower()
    assert "information purposes only" in description
    assert "1 eur" in description
    assert "not a live" in description or "not live" in description


def test_openapi_models_keep_rates_as_strings() -> None:
    openapi = client.get("/openapi.json").json()
    data_schema = openapi["components"]["schemas"]["ExchangeRatesData"]
    rates_schema = data_schema["properties"]["rates"]
    assert rates_schema["additionalProperties"]["type"] == "string"
    base_schema = data_schema["properties"]["base"]
    assert base_schema["type"] == "string" and base_schema["const"] == "EUR"
    date_schema = openapi["components"]["schemas"]["ExchangeRatesResponseMetadata"]
    assert "lastUpdated" in date_schema["properties"]


# --- source catalogue promotion ------------------------------------------------------


def test_source_catalogue_entry_is_production_backed() -> None:
    response = client.get("/v1/sources/exchangeRates")
    assert response.status_code == 200
    entry = _body(response)["data"]
    assert entry["status"] == "production"
    assert entry["coverage"] == "complete"
    assert entry["licence"]["status"] == "verified"
    assert entry["lastUpdated"] == EXCHANGE_RATES_LAST_UPDATED
    assert "European Central Bank" in entry["source"]["name"]
    assert entry["attribution"]
    limitations = " ".join(entry["limitations"]).lower()
    assert "informational" in limitations
    assert "not live" in limitations or "tradable" in limitations
    assert "offline" in limitations and ("manual" in limitations or "manually" in limitations)
    assert "no exchange-rate endpoint" not in limitations
    assert "research spike" not in limitations
    assert "target working days" in entry["updateCadence"].lower() or \
        "offline" in entry["updateCadence"].lower()
