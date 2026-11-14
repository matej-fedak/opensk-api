"""Ensure collection routes reuse the matches already needed for total counts."""

from importlib import import_module

import pytest
from fastapi.testclient import TestClient

from main import app
from services import geography_service, psc_service


@pytest.mark.parametrize("module,service,function,path", [
    ("psc", "psc_service", "filter_psc_records", "/v1/psc"),
    ("phone_areas", "phone_area_service", "filter_phone_area_records", "/v1/phone-areas"),
    ("vehicle_registration_codes", "vehicle_registration_service", "filter_vehicle_registration_code_records", "/v1/vehicle-registration-codes"),
    ("school_facility_counts", "school_facility_count_service", "filter_school_facility_count_records", "/v1/school-facility-counts"),
    ("procurement_notices", "procurement_notice_service", "filter_procurement_notice_records", "/v1/procurement-notices"),
    ("psc", "psc_service", "search_psc_records", "/v1/psc/search?q=Bratislava"),
    ("phone_areas", "phone_area_service", "search_phone_area_records", "/v1/phone-areas/search?q=Bratislava"),
    ("vehicle_registration_codes", "vehicle_registration_service", "search_vehicle_registration_code_records", "/v1/vehicle-registration-codes/search?q=Bratislava"),
])
def test_collection_scans_once_and_preserves_page(monkeypatch, module, service, function, path):
    router = import_module("routers." + module)
    service_module = import_module("services." + service)
    original = getattr(service_module, function)
    calls = []

    def tracked(*args, **kwargs):
        records = original(*args, **kwargs)
        calls.append(records)
        return records

    monkeypatch.setattr(router, function, tracked)
    monkeypatch.setattr(service_module, function, tracked)
    params = {"limit": 2, "offset": 1}
    if "/search" in path:
        params["q"] = "Bratislava"
    response = TestClient(app).get(path, params=params)
    assert response.status_code == 200
    assert len(calls) == 1
    data = response.json()["data"]
    assert data["total"] == len(calls[0])
    assert data["count"] == len(data["items"])
    # Response models may add nullable fields, so compare the original fields.
    assert len(data["items"]) == len(calls[0][1:3])
    for actual, expected in zip(data["items"], calls[0][1:3]):
        assert {key: actual[key] for key in expected} == expected


@pytest.mark.parametrize("kind,code", [("regions", "SK010"), ("districts", "SK0101"), ("municipalities", "517402")])
def test_geography_code_index_is_built_once_and_keeps_first_match(monkeypatch, kind, code):
    index = getattr(geography_service, "index_" + kind)
    getter = getattr(geography_service, "get_" + {"regions": "region", "districts": "district", "municipalities": "municipality"}[kind])
    first = {"code": code, "name": "first"}
    calls = []

    def records():
        calls.append(True)
        return [first, {"code": code, "name": "second"}]

    index.cache_clear()
    monkeypatch.setattr(geography_service, "load_" + kind, records)
    try:
        assert getter(code) is first
        assert getter(code) is first
        assert len(calls) == 1
    finally:
        index.cache_clear()


def test_psc_resolves_geography_once_per_logical_match(monkeypatch):
    original = psc_service._resolve_geography
    calls = []

    def tracked(record):
        calls.append(record)
        return original(record)

    monkeypatch.setattr(psc_service, "_resolve_geography", tracked)
    result = psc_service.lookup_psc("01001", include_geography=True)
    assert len(calls) == result["matchCount"] == 2
    assert result["geography"] == result["matches"][0]["geography"]
