"""HTTP conditional-caching tests.

ETags are strong validators hashed from the exact response body of
deterministic local responses; Last-Modified uses semantic per-dataset
freshness dates. See `docs/http-caching.md`.
"""

from fastapi.testclient import TestClient
import pytest
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from main import app
from services.http_cache import ConditionalCachingMiddleware


client = TestClient(app)


def test_etag_present_and_deterministic_across_requests() -> None:
    first = client.get("/v1/regions")
    second = client.get("/v1/regions")
    assert "etag" in first.headers
    assert first.headers["etag"] == second.headers["etag"]
    assert first.content == second.content


def test_if_none_match_returns_304_without_body() -> None:
    initial = client.get("/v1/regions")
    etag = initial.headers["etag"]
    conditional = client.get("/v1/regions", headers={"If-None-Match": etag})
    assert conditional.status_code == 304
    assert conditional.content == b""
    assert conditional.headers["etag"] == etag


def test_if_none_match_with_mismatched_etag_returns_200() -> None:
    response = client.get("/v1/regions", headers={"If-None-Match": '"bogus-etag"'})
    assert response.status_code == 200


def test_if_none_match_star_matches_any_representation() -> None:
    assert client.get("/v1/regions", headers={"If-None-Match": "*"}).status_code == 304


def test_etag_differs_between_endpoints() -> None:
    assert client.get("/v1/regions").headers["etag"] != client.get("/v1/districts").headers["etag"]


def test_last_modified_uses_semantic_dataset_date() -> None:
    response = client.get("/v1/regions")
    assert response.headers["last-modified"] == "Wed, 27 May 2026 00:00:00 GMT"


def test_if_modified_since_returns_304_when_not_modified() -> None:
    response = client.get("/v1/regions", headers={"If-Modified-Since": "Thu, 01 Oct 2026 00:00:00 GMT"})
    assert response.status_code == 304
    assert response.content == b""


def test_if_modified_since_returns_200_when_dataset_is_newer() -> None:
    response = client.get("/v1/regions", headers={"If-Modified-Since": "Wed, 01 Jan 2020 00:00:00 GMT"})
    assert response.status_code == 200


def test_business_days_use_holiday_dataset_freshness() -> None:
    response = client.get("/v1/business-days/check?date=2026-10-08")
    assert "etag" in response.headers
    assert response.headers["last-modified"].startswith("Wed, 28 Oct 2026")


def test_cache_control_categories() -> None:
    assert client.get("/v1/regions").headers["cache-control"] == "public, max-age=86400"
    assert client.get("/v1/psc/search?q=Bratislava").headers["cache-control"] == "public, max-age=900"
    assert client.get("/v1/phone-areas/search?q=Bratislava").headers["cache-control"] == "public, max-age=900"
    assert client.get("/v1/procurement-notices/search?q=Bratislava").headers["cache-control"] == "public, max-age=900"
    assert client.get("/v1/health").headers["cache-control"] == "no-store"
    assert client.get("/").headers["cache-control"] == "public, max-age=3600"


@pytest.mark.parametrize("iban", ["SK8311000000002918669357", "SK0009000000000000000001", "invalid"])
def test_iban_response_is_not_cacheable(iban: str) -> None:
    response = client.get(f"/v1/iban/validate/{iban}", headers={"If-None-Match": "*", "If-Modified-Since": "Thu, 01 Oct 2099 00:00:00 GMT"})
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert "etag" not in response.headers
    assert "last-modified" not in response.headers


@pytest.mark.parametrize("prefix", ["W/", '"unrelated", W/'])
def test_if_none_match_uses_weak_comparison(prefix: str) -> None:
    initial = client.get("/v1/regions")
    response = client.get("/v1/regions", headers={"If-None-Match": prefix + initial.headers["etag"]})
    assert response.status_code == 304
    assert response.content == b""


@pytest.mark.parametrize("validator", ['"mismatch"', 'W/"mismatch"', ""])
def test_if_none_match_takes_precedence_over_if_modified_since(validator: str) -> None:
    response = client.get("/v1/regions", headers={
        "If-None-Match": validator,
        "If-Modified-Since": "Thu, 01 Oct 2099 00:00:00 GMT",
    })
    assert response.status_code == 200
    assert response.content


@pytest.mark.parametrize("policy", ["no-store", "private, max-age=60", 'private="field", max-age=60', "No-Store, max-age=0"])
def test_private_cache_policies_are_excluded_from_conditional_caching(policy: str) -> None:
    async def endpoint(request):
        return JSONResponse({"private": True}, headers={"Cache-Control": policy})

    private_app = Starlette(routes=[Route("/v1/regions", endpoint)])
    private_app.add_middleware(ConditionalCachingMiddleware)
    response = TestClient(private_app).get("/v1/regions", headers={"If-None-Match": "*"})
    assert response.status_code == 200
    assert response.headers["cache-control"] == policy
    assert "etag" not in response.headers
    assert "last-modified" not in response.headers


def test_health_is_excluded_from_etags() -> None:
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert "etag" not in response.headers


def test_error_responses_do_not_receive_etags() -> None:
    response = client.get("/v1/regions/SK999")
    assert response.status_code == 404
    assert "etag" not in response.headers


def test_root_is_byte_stable_for_etag_semantics() -> None:
    assert client.get("/").content == client.get("/").content


def test_identical_error_responses_are_byte_stable() -> None:
    assert client.get("/v1/regions/SK999").content == client.get("/v1/regions/SK999").content
