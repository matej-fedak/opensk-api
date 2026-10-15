from __future__ import annotations

from scripts import smoke_test
from version import PROJECT_VERSION


def test_smoke_script_targets_seed_company_and_openapi(monkeypatch) -> None:
    iban = smoke_test._build_valid_slovak_iban("0900", "0000000000000001")
    responses = {
        "/": (200, {"data": {"name": "OpenSK API", "version": PROJECT_VERSION, "apiVersion": "v1", "apiNamespace": "/v1"}, "metadata": {"version": "v1"}}),
        "/v1/health": (200, {"data": {"status": "ok"}}),
        "/v1/holidays/2026": (200, {"data": [{}]}),
        "/v1/psc/81101": (200, {"data": {"psc": "81101"}}),
        "/v1/psc": (200, {"data": {"items": []}}),
        "/v1/psc/stats": (200, {"data": {"recordCount": 1, "uniquePscCount": 1}}),
        "/v1/psc/search?q=Bratislava": (200, {"data": {"items": []}}),
        "/v1/banks": (200, {"data": []}),
        "/v1/banks/1100": (200, {"data": {"code": "1100"}}),
        f"/v1/iban/validate/{iban}": (200, {"data": {"normalizedIban": iban}}),
        "/v1/regions": (200, {"data": []}),
        "/v1/regions/SK010": (200, {"data": {"code": "SK010"}}),
        "/v1/districts": (200, {"data": []}),
        "/v1/districts/SK0101": (200, {"data": {"code": "SK0101"}}),
        "/v1/municipalities": (200, {"data": []}),
        "/v1/municipalities/528595": (200, {"data": {"code": "528595"}}),
        "/v1/phone-areas": (200, {"data": {"items": []}}),
        "/v1/phone-areas/02": (200, {"data": {"code": "02", "items": []}}),
        "/v1/phone-areas/search?q=Bratislava": (200, {"data": {"items": []}}),
        "/v1/vehicle-registration-codes": (200, {"data": {"items": []}}),
        "/v1/vehicle-registration-codes/BA": (200, {"data": {"code": "BA"}}),
        "/v1/vehicle-registration-codes/search?q=Trencin": (200, {"data": {"items": []}}),
        "/v1/school-facility-counts": (200, {"data": {"items": []}}),
        "/v1/school-facility-counts/stats": (200, {"data": {"recordCount": 1}}),
        "/v1/procurement-notices": (200, {"data": {"items": []}}),
        "/v1/procurement-notices/search?q=Bratislava": (200, {"data": {"items": []}}),
        "/v1/procurement-notices/stats": (200, {"data": {"recordCount": 100}}),
        "/v1/procurement-notices/670654-2026": (200, {"data": {"id": "670654-2026"}}),
        "/v1/companies/50158635": (200, {"data": {"ico": "50158635"}}),
        "/v1/ico/50158635": (200, {"data": {"ico": "50158635"}}),
        "/v1/sources": (200, {"data": []}),
        "/v1/sources/regions": (200, {"data": {"id": "regions"}}),
        "/v1/business-days/check?date=2026-10-08": (200, {"data": {"isBusinessDay": True}}),
        "/v1/exchange-rates/latest": (200, {"data": {"date": "2026-10-12", "rates": {}}}),
        "/v1/exchange-rates/1999-01-04": (200, {"data": {"date": "1999-01-04", "rates": {}}}),
        "/v1/exchange-rates/latest?currency=usd": (200, {"data": {"rates": {"USD": "1.1574"}}}),
        "/v1/exchange-rates/2026-10-10": (404, {"data": None, "error": {"code": "RATE_DATE_NOT_FOUND"}}),
        "/v1/eu-funds/projects": (200, {"data": {"items": []}}),
        "/v1/eu-funds/projects/TEST000001": (200, {"data": {"projectCode": "TEST000001"}}),
        "/docs": (200, "docs"),
        "/openapi.json": (
            200,
            {
                "info": {"version": PROJECT_VERSION},
                "paths": {
                    "/v1/health": {},
                    "/v1/holidays/{year}": {},
                    "/v1/psc": {},
                    "/v1/psc/search": {},
                    "/v1/psc/stats": {},
                    "/v1/regions": {},
                    "/v1/districts": {},
                    "/v1/municipalities": {},
                    "/v1/banks": {},
                    "/v1/iban/validate/{iban}": {},
                    "/v1/companies/{ico}": {},
                    "/v1/ico/{ico}": {},
                    "/v1/phone-areas": {},
                    "/v1/vehicle-registration-codes": {},
                    "/v1/school-facility-counts": {},
                    "/v1/procurement-notices": {},
                    "/v1/procurement-notices/search": {},
                    "/v1/procurement-notices/stats": {},
                    "/v1/procurement-notices/{id}": {},
                    "/v1/sources": {},
                    "/v1/sources/{source_id}": {},
                    "/v1/business-days/check": {},
                    "/v1/business-days/add": {},
                    "/v1/business-days/between": {},
                    "/v1/exchange-rates/latest": {},
                    "/v1/exchange-rates/{date}": {},
                    "/v1/eu-funds/projects": {},
                    "/v1/eu-funds/projects/{projectCode}": {},
                },
            },
        ),
    }

    def fake_request_json(url: str):
        path = url.split("http://example.com", 1)[-1]
        if path.startswith("/v1/psc/search?"):
            path = "/v1/psc/search?q=Bratislava"
        if path.startswith("/v1/phone-areas/search?"):
            path = "/v1/phone-areas/search?q=Bratislava"
        if path.startswith("/v1/vehicle-registration-codes/search?"):
            path = "/v1/vehicle-registration-codes/search?q=Trencin"
        if path.startswith("/v1/procurement-notices/search?"):
            path = "/v1/procurement-notices/search?q=Bratislava"
        return responses[path]

    def fake_request_headers(url: str):
        assert url.endswith("/v1/banks")
        return 200, {
            "x-ratelimit-limit": "100",
            "x-ratelimit-remaining": "99",
            "x-ratelimit-reset": "1760000060",
        }

    monkeypatch.setattr(smoke_test, "_request_json", fake_request_json)
    monkeypatch.setattr(smoke_test, "_request_headers", fake_request_headers)
    monkeypatch.setattr(smoke_test, "_known_eu_project_code", lambda: "TEST000001")

    assert smoke_test.main(["--base-url", "http://example.com", "--expect-rate-limit"]) == 0


def test_rate_limit_header_check_negative_paths(monkeypatch) -> None:
    monkeypatch.setattr(smoke_test, "_request_headers", lambda url: (200, {"x-ratelimit-limit": "100"}))
    result = smoke_test._check_rate_limit_headers("http://example.com/v1/banks")
    assert not result.ok and "missing headers" in result.detail

    monkeypatch.setattr(smoke_test, "_request_headers", lambda url: (429, {}))
    result = smoke_test._check_rate_limit_headers("http://example.com/v1/banks")
    assert not result.ok and "expected 200, got 429" in result.detail


def test_request_headers_case_normalization(monkeypatch) -> None:
    """Mixed-case response headers must satisfy the lowercased check."""
    from email.message import Message

    real_headers = Message()
    real_headers["X-RateLimit-Limit"] = "100"
    real_headers["X-RATELIMIT-REMAINING"] = "99"
    real_headers["X-RateLimit-Reset"] = "1"

    class _Response:
        status = 200
        headers = real_headers

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    monkeypatch.setattr(smoke_test, "urlopen", lambda request, timeout: _Response())
    status, headers = smoke_test._request_headers("http://example.com/v1/banks")
    assert status == 200
    assert headers == {"x-ratelimit-limit": "100", "x-ratelimit-remaining": "99", "x-ratelimit-reset": "1"}

    monkeypatch.setattr(smoke_test, "_request_headers", lambda url: (status, headers))
    assert smoke_test._check_rate_limit_headers("http://example.com/v1/banks").ok


def test_rate_limit_check_skipped_without_flag(monkeypatch) -> None:
    monkeypatch.setattr(smoke_test, "_known_eu_project_code", lambda: "TEST000001")
    def fail_if_called(url: str):
        raise AssertionError("_request_headers must not be called without --expect-rate-limit")

    monkeypatch.setattr(smoke_test, "_request_headers", fail_if_called)
    monkeypatch.setattr(smoke_test, "_request_json", lambda url: (_ for _ in ()).throw(AssertionError()))
    for check_name in ("_check_root", "_check_ok", "_check_psc_stats", "_check_company_endpoint", "_check_company_alias", "_check_openapi"):
        monkeypatch.setattr(
            smoke_test,
            check_name,
            (lambda name: (lambda *args, **kwargs: smoke_test.SmokeResult(name, True, "PASS")))(check_name),
        )

    assert smoke_test.main(["--base-url", "http://example.com"]) == 0


def test_smoke_client_identifies_itself(monkeypatch) -> None:
    seen_headers: dict[str, str] = {}

    def fake_urlopen(request, timeout):
        seen_headers.update({key.lower(): value for key, value in request.headers.items()})

        class _Response:
            status = 200
            headers: dict[str, str] = {}

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return b"{}"

        return _Response()

    monkeypatch.setattr(smoke_test, "urlopen", fake_urlopen)

    smoke_test._request_json("http://example.com/v1/health")
    assert seen_headers["user-agent"] == f"OpenSK-Public-Smoke/{PROJECT_VERSION}"

    smoke_test._request_headers("http://example.com/v1/banks")
    assert seen_headers["user-agent"] == f"OpenSK-Public-Smoke/{PROJECT_VERSION}"
