"""Keep the elections spike pre-production and the API namespace unchanged."""

from pathlib import Path

from fastapi.testclient import TestClient

from main import app


def test_elections_spike_adds_no_results_routes() -> None:
    client = TestClient(app)
    paths = client.get("/openapi.json").json()["paths"]
    assert not any(path.startswith("/v1/elections") for path in paths)
    assert sum("get" in methods for methods in paths.values()) == 35
    root = client.get("/").json()
    assert root["data"]["apiNamespace"] == "/v1"
    assert root["metadata"]["version"] == "v1"


def test_elections_spike_has_no_production_dataset() -> None:
    data = Path(__file__).resolve().parents[1] / "data"
    assert not list(data.glob("elections*.json"))


def test_elections_catalogue_entry_cannot_look_production_ready() -> None:
    response = TestClient(app).get("/v1/sources/elections")
    assert response.status_code == 200
    entry = response.json()["data"]
    assert entry["status"] == "research"
    assert entry["coverage"] is None
    assert entry["lastUpdated"] is None
    assert entry["licence"]["status"] == "pending"
    assert entry["licence"]["termsUrl"].startswith("https://slovak.statistics.sk/")
    assert any("no election results endpoint" in text for text in entry["limitations"])
    assert not {"nextAction", "notes", "riskLevel", "redistributionStatus"} & entry.keys()
