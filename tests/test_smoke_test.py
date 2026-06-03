from __future__ import annotations

from scripts import smoke_test


def test_smoke_script_targets_seed_company_and_openapi(monkeypatch) -> None:
    iban = smoke_test._build_valid_slovak_iban("0900", "0000000000000001")
    responses = {
        "/": (200, {"data": {"name": "OpenSK API"}}),
        "/v1/health": (200, {"data": {"status": "ok"}}),
        "/v1/holidays/2026": (200, {"data": [{}]}),
        "/v1/psc/81101": (200, {"data": {"psc": "81101"}}),
        "/v1/psc": (200, {"data": {"items": []}}),
        "/v1/psc/stats": (200, {"data": {"recordCount": 1, "uniquePscCount": 1}}),
        "/v1/psc/search?q=Bratislava": (200, {"data": {"items": []}}),
        "/v1/banks": (200, {"data": []}),
        f"/v1/iban/validate/{iban}": (200, {"data": {"normalizedIban": iban}}),
        "/v1/regions": (200, {"data": []}),
        "/v1/districts": (200, {"data": []}),
        "/v1/municipalities": (200, {"data": []}),
        "/v1/companies/50158635": (200, {"data": {"ico": "50158635"}}),
        "/v1/ico/50158635": (200, {"data": {"ico": "50158635"}}),
        "/docs": (200, "docs"),
        "/openapi.json": (200, {"paths": {}}),
    }

    def fake_request_json(url: str):
        path = url.split("http://example.com", 1)[-1]
        if path.startswith("/v1/psc/search?"):
            path = "/v1/psc/search?q=Bratislava"
        return responses[path]

    monkeypatch.setattr(smoke_test, "_request_json", fake_request_json)

    assert smoke_test.main(["--base-url", "http://example.com"]) == 0
