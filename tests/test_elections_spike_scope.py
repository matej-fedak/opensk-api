"""Lock the transition from the historical research spike to one narrow election."""

from pathlib import Path

from fastapi.testclient import TestClient

from main import app


def test_elections_adds_exactly_three_reviewed_routes() -> None:
    client = TestClient(app)
    paths = client.get("/openapi.json").json()["paths"]
    assert {path: methods["get"]["operationId"] for path, methods in paths.items() if path.startswith("/v1/elections")} == {
        "/v1/elections": "list_elections",
        "/v1/elections/{electionId}/results": "list_election_results",
        "/v1/elections/{electionId}/parties": "list_election_parties",
    }
    assert sum("get" in methods for methods in paths.values()) == 42
    root = client.get("/").json()
    assert root["data"]["apiNamespace"] == "/v1"
    assert root["metadata"]["version"] == "v1"


def test_only_nrsr2023_production_dataset() -> None:
    data = Path(__file__).resolve().parents[1] / "data"
    assert [p.name for p in data.glob("elections*.json")] == ["elections_nrsr_2023.json"]


def test_elections_catalogue_evidence_and_narrow_production_scope() -> None:
    response = TestClient(app).get("/v1/sources/elections")
    assert response.status_code == 200
    entry = response.json()["data"]
    assert entry["status"] == "production"
    assert entry["coverage"] == "complete"
    assert entry["lastUpdated"] == "2026-10-31"
    assert entry["licence"]["status"] == "verified"
    assert entry["licence"]["termsUrl"] == "https://creativecommons.org/licenses/by/4.0/"
    assert "2026-10-30" in entry["licence"]["name"]
    assert any("not complete Slovak elections" in text for text in entry["limitations"])
    assert any("MANUAL_OFFICIAL_DOWNLOAD_ONLY" in text for text in entry["limitations"])
    assert any("contextual inference" in text for text in entry["limitations"])
    assert "nie je oficiálnou službou" in entry["attribution"]
    assert not {"nextAction", "notes", "riskLevel", "redistributionStatus"} & entry.keys()
