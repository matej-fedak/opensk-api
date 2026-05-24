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

    assert docs_response.status_code == 200 or openapi_response.status_code == 200


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
