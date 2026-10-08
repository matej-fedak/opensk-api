"""HTTP conditional-caching tests.

ETags are strong validators hashed from the exact response body of
deterministic local responses; Last-Modified uses semantic per-dataset
freshness dates. See `docs/http-caching.md`.
"""

from fastapi.testclient import TestClient

from main import app


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
    assert response.headers["last-modified"].startswith("Mon, 25 May 2026")


def test_cache_control_categories() -> None:
    assert client.get("/v1/regions").headers["cache-control"] == "public, max-age=86400"
    assert client.get("/v1/psc/search?q=Bratislava").headers["cache-control"] == "public, max-age=900"
    assert client.get("/v1/phone-areas/search?q=Bratislava").headers["cache-control"] == "public, max-age=900"
    assert client.get("/v1/procurement-notices/search?q=Bratislava").headers["cache-control"] == "public, max-age=900"
    assert client.get("/v1/health").headers["cache-control"] == "no-store"
    assert client.get("/").headers["cache-control"] == "public, max-age=3600"


def test_iban_response_is_now_publicly_cacheable() -> None:
    response = client.get("/v1/iban/validate/SK8311000000002918669357")
    assert response.status_code == 200
    assert response.headers["cache-control"] == "public, max-age=86400"


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
