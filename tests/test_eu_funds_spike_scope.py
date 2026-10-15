"""Production scope guards replacing the retired 0.23.6 research-only guards."""

from pathlib import Path

from fastapi.testclient import TestClient

from main import app


def test_eu_funds_has_only_the_two_approved_routes() -> None:
    client = TestClient(app)
    paths = client.get("/openapi.json").json()["paths"]
    assert {p for p in paths if p.startswith("/v1/eu-funds")} == {
        "/v1/eu-funds/projects", "/v1/eu-funds/projects/{projectCode}"}
    assert not any("itms" in path.lower() for path in paths)
    # 35 original operations plus two exchange-rate and two EU-funds routes.
    assert sum("get" in methods for methods in paths.values()) == 39
    root = client.get("/").json()
    assert root["data"]["apiNamespace"] == "/v1"
    assert root["metadata"]["version"] == "v1"


def test_eu_funds_has_one_normalized_project_dataset_no_raw_capture() -> None:
    data = Path(__file__).resolve().parents[1] / "data"
    assert list(data.glob("eu_funds*.json")) == [data / "eu_funds_projects.json"]
    assert not list(data.glob("itms21*.json"))


def test_eu_funds_catalogue_is_honest_partial_production() -> None:
    response = TestClient(app).get("/v1/sources/euFunds")
    assert response.status_code == 200
    entry = response.json()["data"]
    assert entry["status"] == "production"
    assert entry["coverage"] == "partial"
    assert entry["lastUpdated"] == "2026-10-15"
    assert entry["licence"]["status"] == "verified"
    assert entry["licence"]["termsUrl"].startswith("https://data.gov.sk/")
    assert any("not all EU funds" in text for text in entry["limitations"])
    assert any("excluded entirely" in text for text in entry["limitations"])
    assert any("positively reviewed" in text for text in entry["limitations"])
    assert not {"nextAction", "notes", "riskLevel", "redistributionStatus"} & entry.keys()


def test_production_write_is_manifest_only() -> None:
    from scripts import import_itms21_projects

    help_text = import_itms21_projects.__doc__ or ""
    assert "--manifest" in help_text and "cannot write production" in help_text
