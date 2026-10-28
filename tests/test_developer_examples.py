"""Copy-paste examples are requests against real local materialized data."""

from pathlib import Path
import re

from fastapi.testclient import TestClient

from main import app
from schemas.exchange_rates import ExchangeRatesData
from scripts.smoke_test import _build_valid_slovak_iban


def test_all_readme_and_quickstart_curl_targets(monkeypatch):
    monkeypatch.setenv("OPENSK_RATE_LIMIT_ENABLED", "false")
    client = TestClient(app)
    requests = set()
    for file in ("README.md", "docs/quickstart.md"):
        text = Path(file).read_text(encoding="utf-8")
        requests.update(re.findall(r'curl[^\n]*"https://opensk-api\.onrender\.com([^"\s]+)"', text))
    assert len(requests) >= 12
    for url in requests:
        response = client.get(url)
        expected = 400 if "not-a-code" in url else (404 if url == "/v1/psc/99999" else 200)
        assert response.status_code == expected, (url, response.text)
        assert response.json()["metadata"]["version"] == "v1"
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_documented_utility_values_and_conditional_example(monkeypatch):
    monkeypatch.setenv("OPENSK_RATE_LIMIT_ENABLED", "false")
    iban = _build_valid_slovak_iban("0900", "0000000000000001")
    assert iban == "SK5409000000000000000001"
    client = TestClient(app)
    assert client.get("/v1/iban/validate/" + iban).json()["data"]["valid"] is True
    assert client.get("/v1/business-days/check?date=2026-10-08").json()["data"]["isBusinessDay"] is True
    path = "/v1/municipalities/528595"
    response = client.get(path)
    assert "Staré Mesto" in response.json()["data"]["name"]
    assert client.get(path, headers={"If-None-Match": response.headers["etag"]}).status_code == 304
    date_example = ExchangeRatesData.model_fields["date"].examples[0]
    rates_example = ExchangeRatesData.model_fields["rates"].examples[0]
    rates = client.get("/v1/exchange-rates/" + date_example).json()["data"]["rates"]
    assert all(rates[code] == rate for code, rate in rates_example.items())
