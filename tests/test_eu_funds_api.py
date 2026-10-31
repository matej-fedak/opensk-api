"""Synthetic service/router/cache tests, independent of upstream availability."""

import copy

import pytest
from fastapi.testclient import TestClient

from main import app
from schemas.common import STATIC_CACHE_CONTROL
from schemas.eu_funds import Dataset
from scripts.itms21_production import materialize
from services import eu_funds_service as service
from test_itms21_production import capture, source_row


@pytest.fixture
def client(tmp_path, monkeypatch):
    rows = [source_row(), source_row("TEST000002", 2), source_row("UNSAFE0001", 3, "1009101")]
    rows[1]["vyzva"]["program"]["kod"] = "402000"
    rows[1]["vyzva"]["kod"] = "CALL-2"
    rows[1]["prijimatel"]["ico"] = "87654321"
    rows[1].update(vrealizacii=False, ukonceny=True)
    # No production file is read during this test; all records are synthetic.
    monkeypatch.setattr("scripts.itms21_production.PRODUCTION_OUTPUT", tmp_path / "absent.json")
    result = materialize(capture(tmp_path / "capture", rows))
    assert result.ok, result.errors
    dataset = Dataset.model_validate(result.payload)
    service.clear_cache()
    monkeypatch.setattr(service, "load_dataset", lambda: dataset)
    yield TestClient(app)
    service.project_index.cache_clear()


def test_default_page_and_envelope(client):
    response = client.get("/v1/eu-funds/projects")
    assert response.status_code == 200
    body = response.json()
    assert body["error"] is None
    assert body["data"]["count"] == body["data"]["total"] == 2
    assert body["data"]["limit"] == 50 and body["data"]["offset"] == 0
    assert body["metadata"]["version"] == "v1"
    assert body["metadata"]["lastUpdated"] == "2026-10-15"
    assert "MIRRI" in body["metadata"]["source"] and "ITMS21+" in body["metadata"]["source"]
    assert response.headers["Cache-Control"] == STATIC_CACHE_CONTROL


@pytest.mark.parametrize("query,code", [
    ("programmeCode=401000", "TEST000001"), ("callCode=CALL-2", "TEST000002"),
    ("beneficiaryIco=12345678", "TEST000001"), ("inImplementation=true", "TEST000001"),
    ("completed=true", "TEST000002"),
    ("programmeCode=%20401000%20&inImplementation=%20TRUE%20", "TEST000001"),
])
def test_exact_filters(client, query, code):
    data = client.get(f"/v1/eu-funds/projects?{query}").json()["data"]
    assert data["total"] == data["count"] == 1
    assert data["items"][0]["projectCode"] == code


def test_and_paging_and_empty(client):
    data = client.get("/v1/eu-funds/projects?limit=1&offset=1").json()["data"]
    assert data["total"] == 2 and data["count"] == 1
    assert data["items"][0]["projectCode"] == "TEST000002"
    assert client.get("/v1/eu-funds/projects?offset=20").json()["data"]["items"] == []
    assert client.get("/v1/eu-funds/projects?programmeCode=401000&completed=true").json()["data"]["total"] == 0
    assert client.get("/v1/eu-funds/projects?nuts=SK010").json()["data"]["total"] == 2
    assert client.get("/v1/eu-funds/projects?nuts=SK042").json()["data"]["total"] == 0


@pytest.mark.parametrize("query", ["limit=0", "limit=201", "limit=x", "limit=1.5", "offset=-1",
                                  "offset=x", "programmeCode=x", "programmeCode=", "callCode=",
                                  "callCode=%00", "beneficiaryIco=123", "completed=1", "inImplementation=yes",
                                  "nuts=bad", "nuts=SK0100000"])
def test_invalid_query_is_standard_400(client, query):
    response = client.get(f"/v1/eu-funds/projects?{query}")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_FORMAT"
    assert response.json()["metadata"]["source"] == "OpenSK API"


def test_lookup_and_no_privacy_existence_leak(client):
    good = client.get("/v1/eu-funds/projects/TEST000001")
    assert good.status_code == 200 and good.json()["data"]["projectCode"] == "TEST000001"
    assert "name" not in good.json()["data"] and "dates" not in good.json()["data"]
    excluded = client.get("/v1/eu-funds/projects/UNSAFE0001")
    absent = client.get("/v1/eu-funds/projects/UNKNOWN001")
    assert excluded.status_code == absent.status_code == 404
    assert excluded.json() == absent.json()
    assert excluded.json()["error"]["code"] == "NOT_FOUND"
    assert client.get("/v1/eu-funds/projects/not-a-code").status_code == 400


def test_conditional_cache_and_query_etags(client):
    path = "/v1/eu-funds/projects"
    for url in (path, path+"/TEST000001"):
        response = client.get(url)
        assert "etag" in response.headers
        assert client.get(url, headers={"If-None-Match": response.headers["etag"]}).status_code == 304
        # Last-Modified is tested after the normal prefix registration below.
        assert "last-modified" in response.headers
        assert client.get(url, headers={"If-Modified-Since": response.headers["last-modified"]}).status_code == 304
    assert client.get(path).headers["etag"] != client.get(path+"?limit=1").headers["etag"]


def test_typed_openapi_and_exactly_two_routes(client):
    schema = client.get("/openapi.json").json()
    paths = {p for p in schema["paths"] if p.startswith("/v1/eu-funds")}
    assert paths == {"/v1/eu-funds/projects", "/v1/eu-funds/projects/{projectCode}"}
    assert sum("get" in value for value in schema["paths"].values()) == 42
    response = schema["paths"]["/v1/eu-funds/projects"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    assert response["$ref"].endswith("ListResponse")
    model = schema["components"]["schemas"]["Project"]
    assert model["additionalProperties"] is False and "name" not in model["properties"]


def test_runtime_can_serve_with_network_disabled(client, monkeypatch):
    import socket
    monkeypatch.setattr(socket, "create_connection", lambda *a, **kw: pytest.fail("runtime network"))
    assert client.get("/v1/eu-funds/projects").status_code == 200
