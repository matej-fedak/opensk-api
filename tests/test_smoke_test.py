from __future__ import annotations

from scripts import smoke_test


def test_smoke_script_targets_seed_company_and_openapi(monkeypatch) -> None:
    iban = smoke_test._build_valid_slovak_iban("0900", "0000000000000001")
    responses = {
        "/": (200, {"data": {"name": "OpenSK API", "version": "0.12.0", "apiVersion": "v1", "apiNamespace": "/v1"}, "metadata": {"version": "v1"}}),
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
        "/v1/companies/50158635": (200, {"data": {"ico": "50158635"}}),
        "/v1/ico/50158635": (200, {"data": {"ico": "50158635"}}),
        "/docs": (200, "docs"),
        "/openapi.json": (
            200,
            {
                "info": {"version": "0.12.0"},
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
        return responses[path]

    monkeypatch.setattr(smoke_test, "_request_json", fake_request_json)

    assert smoke_test.main(["--base-url", "http://example.com"]) == 0
