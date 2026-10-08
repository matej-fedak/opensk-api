"""Public source catalogue tests.

`/v1/sources` exposes a curated projection of the internal registry. These
tests pin the public schema, the public/internal field boundary, and the
deterministic status/coverage/licence mapping for all registered domains.
"""

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)

EXPECTED_IDS = [
    "regions",
    "districts",
    "municipalities",
    "psc",
    "banks",
    "holidays",
    "companies",
    "vatRegistrations",
    "tradeRegistrations",
    "streets",
    "healthcareFacilities",
    "procurementNotices",
    "schoolsDirectory",
    "phoneAreas",
    "vehicleRegistrationCodes",
    "courtDecisions",
    "schoolFacilityCounts",
]

EXPECTED_STATUS = {
    "regions": "production",
    "districts": "production",
    "municipalities": "production",
    "psc": "production",
    "banks": "production",
    "holidays": "production",
    "companies": "seed",
    "vatRegistrations": "research",
    "tradeRegistrations": "blocked",
    "streets": "blocked",
    "healthcareFacilities": "blocked",
    "procurementNotices": "production",
    "schoolsDirectory": "blocked",
    "phoneAreas": "production",
    "vehicleRegistrationCodes": "historical",
    "courtDecisions": "blocked",
    "schoolFacilityCounts": "production",
}

EXPECTED_COVERAGE = {
    "regions": "complete",
    "districts": "complete",
    "municipalities": "complete",
    "psc": "partial",
    "banks": "complete",
    "holidays": "partial",
    "companies": "seed",
    "vatRegistrations": None,
    "tradeRegistrations": None,
    "streets": None,
    "healthcareFacilities": None,
    "procurementNotices": "partial",
    "schoolsDirectory": None,
    "phoneAreas": "complete",
    "vehicleRegistrationCodes": "complete",
    "courtDecisions": None,
    "schoolFacilityCounts": "complete",
}

EXPECTED_LICENCE_STATUS = {
    "regions": "identified",
    "districts": "pending",
    "municipalities": "pending",
    "psc": "pending",
    "banks": "pending",
    "holidays": "identified",
    "companies": "identified",
    "vatRegistrations": "identified",
    "tradeRegistrations": "blocked",
    "streets": "blocked",
    "healthcareFacilities": "blocked",
    "procurementNotices": "identified",
    "schoolsDirectory": "blocked",
    "phoneAreas": "pending",
    "vehicleRegistrationCodes": "pending",
    "courtDecisions": "blocked",
    "schoolFacilityCounts": "identified",
}

PUBLIC_ENTRY_KEYS = {
    "id",
    "name",
    "status",
    "coverage",
    "source",
    "licence",
    "attribution",
    "lastUpdated",
    "lastChecked",
    "updateCadence",
    "limitations",
}

INTERNAL_ONLY_KEYS = {
    "licenceStatus",
    "redistributionStatus",
    "riskLevel",
    "nextAction",
    "notes",
    "sourceFileUrl",
    "sourceDocumentationUrl",
    "candidateSourceUrls",
    "updateFrequency",
}


def _list_entries(*, params: str = "") -> list[dict[str, object]]:
    response = client.get(f"/v1/sources{params}")
    assert response.status_code == 200
    body = response.json()
    assert body["error"] is None
    assert body["metadata"]["version"] == "v1"
    return body["data"]


def test_sources_list_exposes_all_registered_domains() -> None:
    entries = _list_entries()
    assert [entry["id"] for entry in entries] == EXPECTED_IDS
    assert len(entries) == 17


def test_sources_list_uses_standard_envelope_and_static_cache() -> None:
    response = client.get("/v1/sources")
    assert response.json()["metadata"]["source"] == "OpenSK API curated source catalogue"
    assert response.json()["metadata"]["lastUpdated"] == "2026-10-07"
    assert response.headers["cache-control"] == "public, max-age=86400"


def test_public_projection_contains_only_public_keys() -> None:
    for entry in _list_entries():
        assert set(entry) == PUBLIC_ENTRY_KEYS
        intersection = set(entry) & INTERNAL_ONLY_KEYS
        assert not intersection, f"internal field leaked: {intersection}"
        assert isinstance(entry["limitations"], list)


def test_status_mapping_is_deterministic_for_all_domains() -> None:
    entries = {entry["id"]: entry for entry in _list_entries()}
    for source_id, expected in EXPECTED_STATUS.items():
        assert entries[source_id]["status"] == expected, source_id


def test_coverage_mapping_is_deterministic_for_all_domains() -> None:
    entries = {entry["id"]: entry for entry in _list_entries()}
    for source_id, expected in EXPECTED_COVERAGE.items():
        assert entries[source_id]["coverage"] == expected, source_id


def test_licence_status_mapping_is_deterministic_for_all_domains() -> None:
    entries = {entry["id"]: entry for entry in _list_entries()}
    for source_id, expected in EXPECTED_LICENCE_STATUS.items():
        assert entries[source_id]["licence"]["status"] == expected, source_id


def test_unresolved_licences_stay_unresolved_in_public_projection() -> None:
    entries = {entry["id"]: entry for entry in _list_entries()}
    for source_id in ("districts", "municipalities", "psc"):
        assert entries[source_id]["licence"]["status"] == "pending"
        assert entries[source_id]["licence"]["termsUrl"] is None


def test_source_detail_returns_single_entry() -> None:
    response = client.get("/v1/sources/procurementNotices")
    assert response.status_code == 200
    entry = response.json()["data"]
    assert entry["id"] == "procurementNotices"
    assert entry["status"] == "production"
    assert entry["coverage"] == "partial"
    assert "TED" in entry["source"]["name"]
    assert entry["licence"]["termsUrl"].startswith("https://")
    assert len(entry["limitations"]) == 2


def test_source_detail_for_blocked_domain_does_not_look_available() -> None:
    response = client.get("/v1/sources/courtDecisions")
    assert response.status_code == 200
    entry = response.json()["data"]
    assert entry["status"] == "blocked"
    assert entry["coverage"] is None
    assert entry["licence"]["status"] == "blocked"
    assert entry["lastUpdated"] is None


def test_unknown_source_returns_standard_404_envelope() -> None:
    response = client.get("/v1/sources/unknownSource")
    assert response.status_code == 404
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "NOT_FOUND"
    assert "messageSk" in body["error"]


def test_malformed_source_id_returns_400_without_filesystem_effects() -> None:
    response = client.get("/v1/sources/1bad%20id")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_FORMAT"


def test_status_filter() -> None:
    blocked = _list_entries(params="?status=blocked")
    assert {entry["id"] for entry in blocked} == {
        "tradeRegistrations",
        "streets",
        "healthcareFacilities",
        "schoolsDirectory",
        "courtDecisions",
    }


def test_coverage_filter() -> None:
    partial = _list_entries(params="?coverage=partial")
    assert {entry["id"] for entry in partial} == {"psc", "holidays", "procurementNotices"}


def test_query_filter_matches_name_source_or_id() -> None:
    results = _list_entries(params="?q=ted")
    assert {entry["id"] for entry in results} == {"procurementNotices"}


def test_invalid_filter_values_return_400() -> None:
    assert client.get("/v1/sources?status=nope").status_code == 400
    assert client.get("/v1/sources?coverage=nope").status_code == 400
    assert client.get("/v1/sources?q=%20").status_code == 400


def test_openapi_contains_typed_source_models() -> None:
    schema = client.get("/openapi.json").json()
    assert "PublicSourceEntry" in schema["components"]["schemas"]
    assert "SourceListResponse" in schema["components"]["schemas"]
    assert "SourceDetailResponse" in schema["components"]["schemas"]
    list_op = schema["paths"]["/v1/sources"]["get"]
    assert list_op["tags"] == ["sources"]
