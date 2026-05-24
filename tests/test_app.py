from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_root_returns_project_info() -> None:
    response = client.get("/")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["name"] == "OpenSK API"
    assert body["metadata"]["source"] == "OpenSK API"
    assert body["metadata"]["version"] == "v1"
    assert "lastUpdated" in body["metadata"]
    assert body["error"] is None


def test_docs_or_openapi_is_available() -> None:
    docs_response = client.get("/docs")
    openapi_response = client.get("/openapi.json")

    assert docs_response.status_code == 200
    assert openapi_response.status_code == 200

    schema = openapi_response.json()
    assert "/v1/health" in schema["paths"]
    assert "/v1/holidays/{year}" in schema["paths"]
    assert "/v1/psc/{psc}" in schema["paths"]


def test_health_returns_enveloped_response() -> None:
    response = client.get("/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert "metadata" in body
    assert "error" in body
    assert body["metadata"]["source"] == "OpenSK API"
    assert body["metadata"]["version"] == "v1"
    assert "lastUpdated" in body["metadata"]
    assert body["data"]["status"] == "ok"
    assert "timestamp" in body["data"]


def test_holidays_2026_returns_enveloped_response() -> None:
    response = client.get("/v1/holidays/2026")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["data"], list)
    assert body["data"]
    first_holiday = body["data"][0]
    assert first_holiday["date"] == "2026-01-01"
    assert first_holiday["name"] == "Deň vzniku Slovenskej republiky"
    assert first_holiday["name_en"] == "Day of the Establishment of the Slovak Republic"
    assert body["metadata"]["source"] == "OpenSK API static dataset"
    assert body["metadata"]["version"] == "v1"
    assert "lastUpdated" in body["metadata"]
    assert body["error"] is None


def test_unsupported_holiday_year_returns_structured_404() -> None:
    response = client.get("/v1/holidays/1900")

    assert response.status_code == 404
    body = response.json()
    assert body["detail"]["code"] == "NOT_FOUND"
    assert body["detail"]["message"] == "No holiday data available for year 1900"
    assert body["detail"]["messageSk"] == "Nie sú dostupné sviatky pre rok 1900"


def test_psc_81101_returns_enveloped_response() -> None:
    response = client.get("/v1/psc/81101")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["psc"] == "81101"
    assert body["data"]["city"] == "Bratislava"
    assert body["metadata"]["source"] == "OpenSK API static PSC seed dataset"
    assert "lastUpdated" in body["metadata"]
    assert body["metadata"]["version"] == "v1"
    assert body["error"] is None


def test_psc_with_space_is_normalized() -> None:
    response = client.get("/v1/psc/811%2001")

    assert response.status_code == 200
    assert response.json()["data"]["psc"] == "81101"


def test_invalid_psc_returns_400() -> None:
    response = client.get("/v1/psc/81A01")

    assert response.status_code == 400
    body = response.json()
    assert body["detail"]["code"] == "INVALID_FORMAT"
    assert body["detail"]["message"] == "PSC must be a 5-digit Slovak postal code"
    assert body["detail"]["messageSk"] == "PSČ musí byť 5-ciferné slovenské poštové číslo"


def test_unknown_valid_psc_returns_404() -> None:
    response = client.get("/v1/psc/99999")

    assert response.status_code == 404
    body = response.json()
    assert body["detail"]["code"] == "NOT_FOUND"
    assert body["detail"]["message"] == "No PSC data available for 99999"
    assert body["detail"]["messageSk"] == "Pre PSČ 99999 nie sú dostupné údaje"
