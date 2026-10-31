"""Local-only public contracts, native filters, reconciliation and cache checks."""

import json
from pathlib import Path
import socket

from fastapi.testclient import TestClient
import pytest

from main import app
from schemas.common import Page, SuccessResponse
from schemas.elections import ElectionCatalogueEntry, ElectionParty, ElectionUnit
from services import elections_service as service


client = TestClient(app)
RESULTS = "/v1/elections/NRSR2023/results"
PARTIES = "/v1/elections/NRSR2023/parties"


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    connect = socket.socket.connect
    def local_only(sock, address):
        # Windows asyncio builds its internal socketpair over loopback.
        if not isinstance(address, tuple) or address[0] not in {"127.0.0.1", "::1"}:
            raise AssertionError("Election runtime must never access source websites")
        return connect(sock, address)
    monkeypatch.setattr(socket.socket, "connect", local_only)
    monkeypatch.setenv("OPENSK_RATE_LIMIT_ENABLED", "false")


def body(url):
    response = client.get(url)
    assert response.status_code == 200, response.text
    value = response.json()
    assert value["error"] is None and value["metadata"]["version"] == "v1"
    assert value["metadata"]["lastUpdated"] == "2026-10-31"
    assert "Štatistický úrad" in value["metadata"]["source"] and "CC BY 4.0" in value["metadata"]["source"]
    return value


def test_catalogue_and_national_controls():
    value = body("/v1/elections")
    SuccessResponse[list[ElectionCatalogueEntry]].model_validate(value)
    assert [e["id"] for e in value["data"]] == ["NRSR2023"]
    national = value["data"][0]["national"]
    assert national["validVotes"] == 2967896
    assert (national["precinctCount"], national["confirmedPrecinctCount"]) == (6014, 6013)


def test_results_default_and_pagination():
    value = body(RESULTS)
    SuccessResponse[Page[ElectionUnit]].model_validate(value)
    data = value["data"]
    assert (data["count"], data["total"], data["limit"], data["offset"]) == (50, 2927, 50, 0)
    second = body(RESULTS + "?limit=10&offset=10")["data"]
    assert second["items"] == data["items"][10:20]
    assert body(RESULTS + "?offset=2927")["data"]["items"] == []
    units = service.load_dataset().units
    assert data["items"] == [u.model_dump() for u in units[:50]]


@pytest.mark.parametrize("query,field,value", [
    ("regionCode=1", "regionCode", "1"), ("districtCode=101", "districtCode", "101"),
    ("municipalityCode=528595", "municipalityCode", "528595"),
])
def test_exact_native_filters(query, field, value):
    data = body(RESULTS + "?" + query + "&limit=100")["data"]
    expected = [u for u in service.load_dataset().units if getattr(u, field) == value]
    assert data["total"] == len(expected) > 0
    assert all(u[field] == value for u in data["items"])


def test_and_filters_empty_results_and_foreign_scope():
    domestic = body(RESULTS + "?regionCode=1&districtCode=101&municipalityCode=528595")["data"]
    assert domestic["total"] == 1 and domestic["items"][0]["unitType"] == "domestic"
    for query in ("regionCode=2&municipalityCode=528595", "municipalityCode=518638", "municipalityCode=000000", "districtCode=000"):
        assert body(RESULTS + "?" + query)["data"]["items"] == []
    foreign = body(RESULTS + "?regionCode=9&districtCode=900&municipalityCode=599999")["data"]
    assert foreign["total"] == 1
    row = foreign["items"][0]
    assert row["municipalityName"] == "Cudzina" and row["unitType"] == "foreign"
    assert row["validVotes"] == 57856
    assert row["territorialCircuitCode"] == "900"
    assert not any(key.startswith("openSk") or key == "partyVotes" for key in row)


@pytest.mark.parametrize("query", ["regionCode=SK010", "regionCode=0", "regionCode=", "districtCode=SK0101",
                                   "districtCode=10", "municipalityCode=123", "municipalityCode=",
                                   "limit=0", "limit=101", "limit=-1", "limit=bad", "limit=99999999999999999999",
                                   "offset=-1", "offset=2147483648", "offset=1.0"])
def test_invalid_filters_and_pagination(query):
    response = client.get(RESULTS + "?" + query)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_FORMAT"


@pytest.mark.parametrize("election_id", ["NRSR2020", "REF2023", "nrsr2023", "UNKNOWN"])
@pytest.mark.parametrize("endpoint", ["results", "parties"])
def test_unknown_election_404(election_id, endpoint):
    response = client.get(f"/v1/elections/{election_id}/{endpoint}")
    assert response.status_code == 404 and response.json()["error"]["code"] == "NOT_FOUND"


def test_parties_national_only_ordered_decimal_strings_nullable_seats():
    value = body(PARTIES)
    SuccessResponse[list[ElectionParty]].model_validate(value)
    data = value["data"]
    assert len(data) == 25 and [p["partyNumber"] for p in data] == [str(n) for n in range(1, 26)]
    assert sum(p["validVotes"] for p in data) == 2967896
    assert sum(p["seats"] or 0 for p in data) == 150
    assert sum(p["seats"] is None for p in data) == 18
    assert all(type(p["votePercent"]) is str for p in data)


@pytest.mark.parametrize("url", ["/v1/elections", RESULTS, PARTIES])
def test_static_cache_validators(url):
    first = client.get(url)
    assert first.headers["cache-control"] == "public, max-age=86400"
    assert first.headers["last-modified"] == "Sat, 31 Oct 2026 00:00:00 GMT"
    assert client.get(url).content == first.content
    assert client.get(url, headers={"If-None-Match": first.headers["etag"]}).status_code == 304
    assert client.get(url, headers={"If-Modified-Since": first.headers["last-modified"]}).status_code == 304


def test_existing_39_operation_ids_exactly_retained():
    baseline = json.loads(Path("tests/fixtures/public-operations-0.23.13.json").read_bytes())
    actual = {(m.upper(), p, op["operationId"]) for p, item in app.openapi()["paths"].items() for m, op in item.items()}
    old = {tuple(row) for row in baseline}
    assert len(old) == 39 and old <= actual
    assert actual - old == {
        ("GET", "/v1/elections", "list_elections"),
        ("GET", "/v1/elections/{electionId}/results", "list_election_results"),
        ("GET", "/v1/elections/{electionId}/parties", "list_election_parties"),
    }


def test_portalvs_absence_cannot_affect_election_bytes(monkeypatch):
    service.load_dataset.cache_clear()
    original = Path.read_bytes
    def read_only_election(path):
        if path.name != "elections_nrsr_2023.json":
            raise AssertionError("No other dataset may be read for election loading")
        return original(path)
    monkeypatch.setattr(Path, "read_bytes", read_only_election)
    assert body(RESULTS + "?municipalityCode=599999")["data"]["items"][0]["validVotes"] == 57856
