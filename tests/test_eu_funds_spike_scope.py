"""Keep the ITMS21+ EU-funds spike research-only and the API namespace unchanged."""

from pathlib import Path

from fastapi.testclient import TestClient

from main import app


def test_eu_funds_spike_adds_no_eu_funds_routes() -> None:
    client = TestClient(app)
    paths = client.get("/openapi.json").json()["paths"]
    assert not any("eu" in path.lower() and "fund" in path.lower() for path in paths)
    assert not any("itms" in path.lower() for path in paths)
    # 35 pre-0.23.4 operations plus the two exchange-rates production routes.
    assert sum("get" in methods for methods in paths.values()) == 37
    root = client.get("/").json()
    assert root["data"]["apiNamespace"] == "/v1"
    assert root["metadata"]["version"] == "v1"


def test_eu_funds_spike_has_no_production_dataset() -> None:
    data = Path(__file__).resolve().parents[1] / "data"
    assert not list(data.glob("eu_funds*.json"))
    assert not list(data.glob("itms21*.json"))


def test_eu_funds_catalogue_entry_cannot_look_production_ready() -> None:
    response = TestClient(app).get("/v1/sources/euFunds")
    assert response.status_code == 200
    entry = response.json()["data"]
    assert entry["status"] == "research"
    assert entry["coverage"] is None
    assert entry["lastUpdated"] is None
    assert entry["licence"]["status"] == "verified"
    assert entry["licence"]["termsUrl"].startswith("https://data.gov.sk/")
    assert any("no EU funds endpoint" in text for text in entry["limitations"])
    assert any("excluded entirely" in text for text in entry["limitations"])
    assert any("positively reviewed" in text for text in entry["limitations"])
    assert not {"nextAction", "notes", "riskLevel", "redistributionStatus"} & entry.keys()


def test_eu_funds_importer_has_no_production_write_mode() -> None:
    from scripts import import_itms21_projects

    assert not hasattr(import_itms21_projects, "import_production")
    help_text = import_itms21_projects.__doc__ or ""
    assert "NO production-write mode" in help_text
