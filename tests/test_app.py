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
    assert "/v1/banks" in schema["paths"]
    assert "/v1/banks/{code}" in schema["paths"]
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


def test_banks_list_returns_enveloped_response() -> None:
    response = client.get("/v1/banks")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["data"], list)
    assert any(bank["code"] == "0900" for bank in body["data"])
    assert body["metadata"]["source"] == "OpenSK API static banks dataset"
    assert body["metadata"]["lastUpdated"] == "2026-05-25"
    assert body["error"] is None


def test_known_bank_code_returns_enveloped_response() -> None:
    response = client.get("/v1/banks/1100")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["code"] == "1100"
    assert body["data"]["name"] == "Tatra banka, a.s."
    assert body["metadata"]["source"] == "OpenSK API static banks dataset"
    assert body["error"] is None


def test_invalid_bank_code_returns_400() -> None:
    response = client.get("/v1/banks/11A0")

    assert response.status_code == 400
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "INVALID_FORMAT"
    assert body["error"]["message"] == "Bank code must be 4 digits"


def test_unknown_bank_code_returns_404() -> None:
    response = client.get("/v1/banks/9999")

    assert response.status_code == 404
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "NOT_FOUND"
    assert body["error"]["message"] == "No bank data available for 9999"


def test_holidays_2026_returns_enveloped_response() -> None:
    response = client.get("/v1/holidays/2026")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "public, max-age=86400"
    body = response.json()
    assert isinstance(body["data"], list)
    assert body["data"]
    first_holiday = body["data"][0]
    assert first_holiday["date"] == "2026-01-01"
    assert first_holiday["name"] == "Deň vzniku Slovenskej republiky"
    assert first_holiday["name_en"] == "Day of the Establishment of the Slovak Republic"
    assert body["metadata"]["source"] == "OpenSK API static dataset"
    assert body["metadata"]["version"] == "v1"
    assert body["metadata"]["lastUpdated"] == "2026-05-25"
    assert body["error"] is None


def test_unsupported_holiday_year_returns_structured_404() -> None:
    response = client.get("/v1/holidays/1900")

    assert response.status_code == 404
    body = response.json()
    assert body["data"] is None
    assert body["metadata"]["source"] == "OpenSK API"
    assert body["error"]["code"] == "NOT_FOUND"
    assert body["error"]["message"] == "No holiday data available for year 1900"
    assert body["error"]["messageSk"] == "Nie sú dostupné sviatky pre rok 1900"


def test_psc_81101_returns_enveloped_response() -> None:
    response = client.get("/v1/psc/81101")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "public, max-age=86400"
    body = response.json()
    assert body["data"]["psc"] == "81101"
    assert body["data"]["city"] == "Bratislava"
    assert body["metadata"]["source"] == "OpenSK API static PSC seed dataset"
    assert body["metadata"]["lastUpdated"] == "2026-05-25"
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
    assert body["data"] is None
    assert body["error"]["code"] == "INVALID_FORMAT"
    assert body["error"]["message"] == "PSC must be a 5-digit Slovak postal code"
    assert body["error"]["messageSk"] == "PSČ musí byť 5-ciferné slovenské poštové číslo"


def test_unknown_valid_psc_returns_404() -> None:
    response = client.get("/v1/psc/99999")

    assert response.status_code == 404
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "NOT_FOUND"
    assert body["error"]["message"] == "No PSC data available for 99999"
    assert body["error"]["messageSk"] == "Pre PSČ 99999 nie sú dostupné údaje"


def test_unknown_route_returns_enveloped_404() -> None:
    response = client.get("/v1/does-not-exist")

    assert response.status_code == 404
    body = response.json()
    assert body["data"] is None
    assert body["metadata"]["source"] == "OpenSK API"
    assert body["error"]["code"] == "NOT_FOUND"


def test_validation_error_returns_enveloped_422() -> None:
    response = client.get("/v1/holidays/not-a-year")

    assert response.status_code == 422
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "VALIDATION_ERROR"
