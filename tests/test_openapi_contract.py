"""Bounded, offline public-contract and pre-change compatibility evidence."""

import hashlib
import json
from pathlib import Path
import socket

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from pydantic import TypeAdapter
import pytest

from main import app
from main import (
    banks_router, business_days_router, companies_router, districts_router,
    eu_funds_router, exchange_rates_router, health_router, holidays_router,
    elections_router,
    iban_router, municipalities_router, phone_areas_router,
    procurement_notices_router, psc_router, regions_router,
    school_facility_counts_router, sources_router, vehicle_registration_codes_router,
)
from schemas.common import ErrorResponse
from scripts.audit_openapi_contract import APPLICATION_ERRORS, digest, normalized_body


FIXTURES = Path(__file__).with_name("fixtures")
INVENTORY = json.loads((FIXTURES / "public-operations.json").read_bytes())
BASELINE = json.loads((FIXTURES / "public-contract-baseline.json").read_bytes())
ERROR_CASES = json.loads((FIXTURES / "public-error-cases.json").read_bytes())
ROUTES = {route.path: route for route in app.routes if isinstance(route, APIRoute)}
# Newer FastAPI keeps include_router entries lazy; older releases flatten them
# into app.routes. Inspect the actual declared routers in either case, without
# depending on private _IncludedRouter internals. The exact inventory assertion
# below ensures no mounted operation escapes runtime-model validation.
for router in (
    banks_router, business_days_router, companies_router, districts_router,
    eu_funds_router, exchange_rates_router, health_router, holidays_router,
    elections_router,
    iban_router, municipalities_router, phone_areas_router,
    procurement_notices_router, psc_router, regions_router,
    school_facility_counts_router, sources_router, vehicle_registration_codes_router,
):
    ROUTES.update({"/v1" + route.path: route for route in router.routes if isinstance(route, APIRoute)})


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setenv("OPENSK_RATE_LIMIT_ENABLED", "false")
    def forbidden(*args, **kwargs):
        raise AssertionError("Runtime contract tests must not use network")
    monkeypatch.setattr(socket, "create_connection", forbidden)


def test_complete_reviewed_inventory_and_refs():
    schema = app.openapi()
    tags = {tag["name"]: tag["description"] for tag in schema["tags"]}
    assert tags["districts"] == "Complete Slovak districts dataset materialized from PortalVS / IS Číselníky successor geography data."
    json.dumps(schema, allow_nan=False)
    actual = [[method.upper(), path, op["operationId"]]
              for path, item in schema["paths"].items() for method, op in item.items()]
    assert len(actual) == 42
    assert sorted(actual) == sorted(INVENTORY)
    assert set(ROUTES) == {path for _, path, _ in INVENTORY}
    assert len({op[2] for op in actual}) == 42
    assert all(path == "/" or path.startswith("/v1/") for _, path, _ in actual)
    def resolve(value):
        if isinstance(value, dict):
            if "$ref" in value:
                target = schema
                for part in value["$ref"].removeprefix("#/").split("/"):
                    target = target[part]
            assert value.get("additionalProperties") is not True
            for child in value.values():
                resolve(child)
        elif isinstance(value, list):
            for child in value:
                resolve(child)
    resolve(schema)


@pytest.mark.parametrize("method,path,operation_id", INVENTORY)
def test_each_public_contract(method, path, operation_id):
    op = app.openapi()["paths"][path][method.lower()]
    assert op["operationId"] == operation_id
    assert len(op["summary"]) >= 10
    assert len(op["description"]) >= 40
    assert op["tags"]
    content = op["responses"]["200"]["content"]["application/json"]
    assert "$ref" in content["schema"]
    assert content["examples"]
    model = ROUTES[path].response_model
    for example in content["examples"].values():
        TypeAdapter(model).validate_python(example["value"])
    for parameter in op.get("parameters", []):
        assert len(parameter["description"]) > 20
        assert "example" in parameter
        if parameter["in"] == "path":
            assert parameter["required"]
            assert "{" + parameter["name"] + "}" in path
    expected_errors = set(APPLICATION_ERRORS.get(path, []))
    if path != "/v1/health":
        expected_errors.add(429)
    assert set(op["responses"]) == {"200"} | set(map(str, expected_errors)) | ({"304"} if path != "/v1/health" else set())
    for code in expected_errors:
        error_content = op["responses"][str(code)]["content"]["application/json"]
        assert error_content["schema"]["$ref"] == "#/components/schemas/ErrorResponse"
        ErrorResponse.model_validate(error_content["example"])
    if path != "/v1/health":
        assert set(op["responses"]["429"]["headers"]) == {"Retry-After", "X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"}


@pytest.mark.parametrize("path,baseline", BASELINE.items())
def test_runtime_validates_and_matches_before(path, baseline):
    response = TestClient(app).get(baseline["url"])
    assert response.status_code == 200
    body = response.json()
    model = ROUTES[path].response_model
    parsed = TypeAdapter(model).validate_python(body)
    # No dropped fields, injected defaults, alias changes, null changes or coercion.
    assert parsed.model_dump(mode="json", by_alias=True, exclude_unset=True) == body
    assert set(body) == {"data", "metadata", "error"}
    assert body["metadata"]["version"] == "v1"
    assert body["error"] is None
    if path != "/v1/psc/{psc}":
        assert digest(normalized_body(path, body)) == baseline["bodySha256"]
    assert response.headers.get("cache-control") == baseline["cacheControl"]
    assert response.headers.get("last-modified") == baseline["lastModified"]
    if path != "/v1/health":
        assert response.headers["etag"] == '"' + hashlib.sha256(response.content).hexdigest()[:32] + '"'
        cached = TestClient(app).get(baseline["url"], headers={"If-None-Match": response.headers["etag"]})
        assert cached.status_code == 304 and cached.content == b""


@pytest.mark.parametrize("path,url,status,code", ERROR_CASES)
def test_application_error_runtime_contract(path, url, status, code):
    response = TestClient(app).get(url)
    assert response.status_code == status
    body = ErrorResponse.model_validate(response.json())
    assert body.error.code == code
    assert body.metadata.lastUpdated is None
    assert body.metadata.version == "v1"
    documented = app.openapi()["paths"][path]["get"]["responses"][str(status)]
    assert response.json() == documented["content"]["application/json"]["example"]


def test_required_wire_parameters_do_not_change_manual_400_behavior():
    for path in ("/v1/psc/search", "/v1/phone-areas/search", "/v1/business-days/check"):
        assert app.openapi()["paths"][path]["get"]["parameters"][0]["required"]
        assert TestClient(app).get(path).status_code == 400
    district_parameter = app.openapi()["paths"]["/v1/psc"]["get"]["parameters"][2]
    assert "five" in district_parameter["description"]
    assert TestClient(app).get("/v1/psc?districtCode=SK03111").status_code == 200


def test_optional_geography_not_injected_and_bank_provenance_retained():
    client = TestClient(app)
    plain = client.get("/v1/psc/01001").json()["data"]
    assert "geography" not in plain
    assert all("geography" not in match for match in plain["matches"])
    for url in ("/v1/banks/1100", "/v1/iban/validate/SK3109000000000000000001"):
        metadata = client.get(url).json()["metadata"]
        assert {"sourceVersion", "sourceEffectiveDate", "sourceDownloadedAt", "sourceSha256", "attribution", "transformation"} <= set(metadata)


def test_all_production_data_frozen():
    expected = json.loads((FIXTURES / "production-data-sha256.json").read_bytes())
    actual = {p.name: hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
              for p in Path("data").glob("*.json")}
    assert actual == expected


@pytest.mark.parametrize("path,baseline", BASELINE.items())
def test_response_example_values_still_match_local_data(path, baseline):
    url = "/v1/iban/validate/SK5409000000000000000001" if path == "/v1/iban/validate/{iban}" else baseline["url"]
    actual = TestClient(app).get(url).json()
    example = app.openapi()["paths"][path]["get"]["responses"]["200"]["content"]["application/json"]["examples"]["snapshot"]["value"]
    actual = normalized_body(path, actual)
    example = normalized_body(path, example)
    if isinstance(actual["data"], list):
        actual["data"] = actual["data"][:1]
    if path == "/v1/phone-areas/{code}":
        actual["data"]["items"] = actual["data"]["items"][:1]
    assert example == actual


def test_503_documentation_matches_existing_company_error(monkeypatch):
    import routers.companies as companies
    def unavailable(ico):
        raise companies.CompanyDatasetUnavailableError()
    monkeypatch.setattr(companies, "lookup_company", unavailable)
    for path, url in (("/v1/companies/{ico}", "/v1/companies/50158635"), ("/v1/ico/{ico}", "/v1/ico/50158635")):
        response = TestClient(app).get(url)
        assert response.status_code == 503
        expected = app.openapi()["paths"][path]["get"]["responses"]["503"]["content"]["application/json"]["example"]
        assert response.json() == expected


def test_rate_limit_example_and_health_exemption(monkeypatch):
    from services.rate_limit import rate_limiter
    monkeypatch.setenv("OPENSK_RATE_LIMIT_ENABLED", "true")
    monkeypatch.setattr(rate_limiter, "_clock", lambda: 60.0)
    rate_limiter.reset()
    try:
        client = TestClient(app)
        for _ in range(100):
            assert client.get("/").status_code == 200
        response = client.get("/")
        assert response.status_code == 429
        documented = app.openapi()["paths"]["/"]["get"]["responses"]["429"]["content"]["application/json"]["example"]
        assert response.json() == documented
        assert response.headers["x-ratelimit-limit"] == "100"
        assert response.headers["x-ratelimit-remaining"] == "0"
        assert 1 <= int(response.headers["retry-after"]) <= 60
        assert "etag" not in response.headers
        health = client.get("/v1/health")
        assert health.status_code == 200 and health.headers["cache-control"] == "no-store"
        assert "etag" not in health.headers and "x-ratelimit-limit" not in health.headers
    finally:
        rate_limiter.reset()
