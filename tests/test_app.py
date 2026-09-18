from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def build_valid_slovak_iban(bank_code: str, account_number: str) -> str:
    bban = f"{bank_code}{account_number}"
    provisional = f"SK00{bban}"
    rearranged = f"{bban}SK00"
    numeric = "".join(str(ord(character) - 55) if character.isalpha() else character for character in rearranged)

    remainder = 0
    for digit in numeric:
        remainder = (remainder * 10 + int(digit)) % 97

    check_digits = 98 - remainder
    return f"SK{check_digits:02d}{bban}"


def test_root_returns_project_info() -> None:
    response = client.get("/")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["name"] == "OpenSK API"
    assert body["data"]["version"] == "0.10.0-dev"
    assert body["metadata"]["source"] == "OpenSK API"
    assert body["metadata"]["version"] == "v1"
    assert "lastUpdated" in body["metadata"]
    assert body["error"] is None


def test_docs_or_openapi_is_available() -> None:
    docs_response = client.get("/docs")
    openapi_response = client.get("/openapi.json")

    assert docs_response.status_code == 200
    assert openapi_response.status_code == 200

    schema = openapi_response.json()
    assert schema["info"]["version"] == "0.10.0-dev"
    assert "/v1/banks" in schema["paths"]
    assert "/v1/banks/{code}" in schema["paths"]
    assert "/v1/health" in schema["paths"]
    assert "/v1/holidays/{year}" in schema["paths"]
    assert "/v1/regions" in schema["paths"]
    assert "/v1/regions/{code}" in schema["paths"]
    assert "/v1/districts" in schema["paths"]
    assert "/v1/districts/{code}" in schema["paths"]
    assert "/v1/municipalities" in schema["paths"]
    assert "/v1/municipalities/{code}" in schema["paths"]
    assert "/v1/psc" in schema["paths"]
    assert "/v1/psc/search" in schema["paths"]
    assert "/v1/psc/stats" in schema["paths"]
    assert "/v1/psc/{psc}" in schema["paths"]
    assert "/v1/phone-areas" in schema["paths"]
    assert "/v1/phone-areas/search" in schema["paths"]
    assert "/v1/phone-areas/{code}" in schema["paths"]
    assert "/v1/vehicle-registration-codes" in schema["paths"]
    assert "/v1/vehicle-registration-codes/search" in schema["paths"]
    assert "/v1/vehicle-registration-codes/{code}" in schema["paths"]
    assert "/v1/vehicles/{spz}" not in schema["paths"]
    assert "/v1/school-facility-counts" in schema["paths"]
    assert "/v1/school-facility-counts/stats" in schema["paths"]
    assert "/v1/schools" not in schema["paths"]
    assert "/v1/schools/{code}" not in schema["paths"]
    assert "/v1/companies/{ico}" in schema["paths"]
    assert "/v1/ico/{ico}" in schema["paths"]
    psc_params = schema["paths"]["/v1/psc/{psc}"]["get"]["parameters"]
    assert any(param["name"] == "include" for param in psc_params)


def test_project_version_reset_preserves_v1_route_namespace() -> None:
    schema = client.get("/openapi.json").json()

    assert schema["info"]["version"] == "0.10.0-dev"
    assert "/v1/health" in schema["paths"]
    assert client.get("/v1/health").status_code == 200


def test_health_returns_enveloped_response() -> None:
    response = client.get("/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert "metadata" in body
    assert "error" in body
    assert body["metadata"]["source"] == "OpenSK API"
    assert body["metadata"]["version"] == "v1"
    assert "lastUpdated" in body["metadata"]
    assert body["data"]["status"] == "ok"
    assert "timestamp" in body["data"]


def test_banks_list_returns_enveloped_response() -> None:
    response = client.get("/v1/banks")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["data"], list)
    assert len(body["data"]) == 30
    assert any(bank["code"] == "0900" for bank in body["data"])
    assert body["metadata"]["source"] == "OpenSK API static banks dataset"
    assert body["metadata"]["lastUpdated"] == "2026-05-18"
    assert body["error"] is None


def test_known_bank_code_returns_enveloped_response() -> None:
    response = client.get("/v1/banks/1100")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["code"] == "1100"
    assert body["data"]["name"] == "Tatra banka, a.s."
    assert body["data"]["bic"] == "TATRSKBX"
    assert body["data"]["swift"] == "TATRSKBX"
    assert body["data"]["alphabeticCode"] is None
    assert body["data"]["activeParty"] is True
    assert body["data"]["activePartyMarker"] == "C"
    assert body["data"]["country"] == "SK"
    assert body["metadata"]["source"] == "OpenSK API static banks dataset"
    assert body["error"] is None


def test_invalid_bank_code_returns_400() -> None:
    response = client.get("/v1/banks/11A0")

    assert response.status_code == 400
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "INVALID_FORMAT"
    assert body["error"]["message"] == "Bank code must be 4 digits"


def test_unknown_bank_code_returns_404() -> None:
    response = client.get("/v1/banks/9999")

    assert response.status_code == 404
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "NOT_FOUND"
    assert body["error"]["message"] == "No bank data available for 9999"


def test_valid_slovak_iban_returns_enveloped_response() -> None:
    iban = build_valid_slovak_iban("0900", "0000000000000001")
    response = client.get(f"/v1/iban/validate/{iban}")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["normalizedIban"] == iban
    assert body["data"]["countryCode"] == "SK"
    assert body["data"]["supportedCountry"] is True
    assert body["data"]["checksumValid"] is True
    assert body["data"]["valid"] is True
    assert body["data"]["bankCode"] == "0900"
    assert body["data"]["bankName"] == "Slovenská sporiteľňa, a.s."


def test_invalid_checksum_iban_returns_validation_result() -> None:
    iban = "SK0009000000000000000001"
    response = client.get(f"/v1/iban/validate/{iban}")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["normalizedIban"] == iban
    assert body["data"]["supportedCountry"] is True
    assert body["data"]["checksumValid"] is False
    assert body["data"]["valid"] is False


def test_unsupported_country_iban_returns_validation_result() -> None:
    response = client.get("/v1/iban/validate/CZ6508000000192000145399")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["countryCode"] == "CZ"
    assert body["data"]["supportedCountry"] is False
    assert body["data"]["valid"] is False


def test_iban_spaces_are_normalized() -> None:
    iban = build_valid_slovak_iban("1100", "0000000000000002")
    formatted = f"{iban[:4]} {iban[4:8]} {iban[8:12]} {iban[12:16]} {iban[16:20]} {iban[20:]}"
    response = client.get(f"/v1/iban/validate/{formatted.replace(' ', '%20')}")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["normalizedIban"] == iban


def test_holidays_2026_returns_enveloped_response() -> None:
    response = client.get("/v1/holidays/2026")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "public, max-age=86400"
    body = response.json()
    assert isinstance(body["data"], list)
    assert body["data"]
    first_holiday = body["data"][0]
    assert first_holiday["date"] == "2026-01-01"
    assert first_holiday["name"] == "Deň vzniku Slovenskej republiky"
    assert first_holiday["name_en"] == "Day of the Establishment of the Slovak Republic"
    assert body["metadata"]["source"] == "OpenSK API static holidays dataset"
    assert body["metadata"]["version"] == "v1"
    assert body["metadata"]["lastUpdated"] == "2026-05-25"
    assert body["error"] is None


def test_regions_list_returns_enveloped_response() -> None:
    response = client.get("/v1/regions")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "public, max-age=86400"
    body = response.json()
    assert isinstance(body["data"], list)
    assert len(body["data"]) == 8
    assert any(region["code"] == "SK010" for region in body["data"])
    assert body["metadata"]["source"] == "OpenSK API static geography dataset"
    assert body["metadata"]["lastUpdated"] == "2026-05-27"
    assert body["metadata"]["version"] == "v1"
    assert body["error"] is None


def test_known_region_code_returns_one_region() -> None:
    response = client.get("/v1/regions/SK010")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["code"] == "SK010"
    assert body["data"]["name"] == "Bratislavský kraj"
    assert body["error"] is None


def test_unknown_region_code_returns_404() -> None:
    response = client.get("/v1/regions/SK999")

    assert response.status_code == 404
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "NOT_FOUND"


def test_invalid_region_code_returns_400() -> None:
    response = client.get("/v1/regions/SK10A")

    assert response.status_code == 400
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "INVALID_FORMAT"


def test_invalid_district_region_filter_returns_400() -> None:
    response = client.get("/v1/districts?regionCode=SK01A")

    assert response.status_code == 400
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "INVALID_FORMAT"


def test_districts_list_returns_enveloped_response() -> None:
    response = client.get("/v1/districts")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "public, max-age=86400"
    body = response.json()
    assert isinstance(body["data"], list)
    assert len(body["data"]) == 79
    assert body["metadata"]["source"] == "OpenSK API static geography dataset"
    assert body["metadata"]["version"] == "v1"
    assert body["error"] is None


def test_phone_areas_list_returns_paginated_response() -> None:
    response = client.get("/v1/phone-areas")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "public, max-age=86400"
    body = response.json()
    assert body["data"]["total"] == 2922
    assert body["data"]["count"] == 100
    assert any(item["code"] == "02" for item in body["data"]["items"])
    assert body["metadata"]["source"] == "OpenSK API static phone area dataset"
    assert body["metadata"]["lastUpdated"] == "2026-09-15"
    assert body["error"] is None


def test_phone_area_code_lookup_returns_records() -> None:
    response = client.get("/v1/phone-areas/02")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["code"] == "02"
    assert body["data"]["count"] >= 1
    assert any(item["municipalityCode"] == "528595" for item in body["data"]["items"])
    assert body["error"] is None


def test_phone_area_invalid_code_returns_400() -> None:
    response = client.get("/v1/phone-areas/abc")

    assert response.status_code == 400
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "INVALID_FORMAT"


def test_phone_area_unknown_code_returns_404() -> None:
    response = client.get("/v1/phone-areas/099")

    assert response.status_code == 404
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "NOT_FOUND"


def test_phone_area_filters_work() -> None:
    by_municipality = client.get("/v1/phone-areas?municipalityCode=528595")
    by_region = client.get("/v1/phone-areas?regionCode=SK010")
    by_district = client.get("/v1/phone-areas?districtCode=SK0101")

    assert by_municipality.status_code == 200
    assert by_municipality.json()["data"]["items"][0]["code"] == "02"
    assert by_region.status_code == 200
    assert by_region.json()["data"]["items"][0]["code"] == "02"
    assert by_district.status_code == 200
    assert by_district.json()["data"]["items"][0]["code"] == "02"


def test_phone_area_search_by_municipality_name() -> None:
    response = client.get("/v1/phone-areas/search?q=Bratislava")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["total"] >= 1
    assert any(item["code"] == "02" for item in body["data"]["items"])


def test_vehicle_registration_codes_list_returns_paginated_response() -> None:
    response = client.get("/v1/vehicle-registration-codes")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "public, max-age=86400"
    body = response.json()
    assert body["data"]["total"] == 93
    assert body["data"]["count"] == 93
    assert any(item["code"] == "BA" for item in body["data"]["items"])
    assert body["metadata"]["source"] == "OpenSK API static legacy vehicle registration code dataset"
    assert body["metadata"]["lastUpdated"] == "2026-09-15"
    assert body["error"] is None


def test_vehicle_registration_code_lookup_returns_legacy_reference() -> None:
    response = client.get("/v1/vehicle-registration-codes/ba")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["code"] == "BA"
    assert body["data"]["districtName"] == "Bratislava"
    assert body["data"]["districtCode"] is None
    assert body["data"]["regionCode"] == "SK010"
    assert body["data"]["status"] == "legacy"
    assert "not reliable for current plate lookup" in body["data"]["notes"]
    assert body["error"] is None


def test_vehicle_registration_invalid_code_returns_400() -> None:
    response = client.get("/v1/vehicle-registration-codes/BA123AA")

    assert response.status_code == 400
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "INVALID_FORMAT"


def test_vehicle_registration_unknown_valid_code_returns_404() -> None:
    response = client.get("/v1/vehicle-registration-codes/AA")

    assert response.status_code == 404
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "NOT_FOUND"


def test_vehicle_registration_code_search_by_district_name() -> None:
    response = client.get("/v1/vehicle-registration-codes/search?q=Trencin")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["total"] == 3
    assert {item["code"] for item in body["data"]["items"]} == {"TN", "TC", "TE"}


def test_vehicle_registration_code_filters_work() -> None:
    by_region = client.get("/v1/vehicle-registration-codes?regionCode=SK010")
    by_district = client.get("/v1/vehicle-registration-codes?districtCode=SK0229")

    assert by_region.status_code == 200
    assert {item["code"] for item in by_region.json()["data"]["items"]} >= {"BA", "BD", "BE", "BI", "BL", "BT", "MA", "PK", "SC"}
    assert by_district.status_code == 200
    assert {item["code"] for item in by_district.json()["data"]["items"]} == {"TN", "TC", "TE"}


def test_full_vehicle_plate_lookup_route_is_not_exposed() -> None:
    response = client.get("/v1/vehicles/BA123AA")

    assert response.status_code == 404


def test_school_facility_counts_list_returns_paginated_response() -> None:
    response = client.get("/v1/school-facility-counts")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "public, max-age=86400"
    body = response.json()
    assert body["data"]["total"] == 1227
    assert body["data"]["count"] == 100
    assert body["metadata"]["source"] == "OpenSK API static school facility aggregate count dataset"
    assert body["metadata"]["lastUpdated"] == "2025-09-15"
    assert body["error"] is None


def test_school_facility_counts_filters_work() -> None:
    response = client.get("/v1/school-facility-counts?regionCode=SK022&districtCode=SK0229&schoolKind=GYM")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["total"] == 3
    assert all(item["regionCode"] == "SK022" for item in body["data"]["items"])
    assert all(item["districtCode"] == "SK0229" for item in body["data"]["items"])
    assert all(item["schoolKindShort"] == "GYM" for item in body["data"]["items"])


def test_school_facility_counts_name_filters_are_accent_insensitive() -> None:
    response = client.get("/v1/school-facility-counts?districtName=Trencin&schoolType=GYM")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["total"] == 3
    assert all(item["districtName"] == "Trenčín" for item in body["data"]["items"])


def test_school_facility_counts_invalid_limit_returns_400() -> None:
    response = client.get("/v1/school-facility-counts?limit=abc")

    assert response.status_code == 400
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "INVALID_FORMAT"


def test_school_facility_counts_invalid_region_returns_400() -> None:
    response = client.get("/v1/school-facility-counts?regionCode=SK01A")

    assert response.status_code == 400
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "INVALID_FORMAT"


def test_school_facility_counts_empty_filter_returns_200() -> None:
    response = client.get("/v1/school-facility-counts?founderType=missing")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["total"] == 0
    assert body["data"]["items"] == []


def test_school_facility_counts_stats_returns_totals() -> None:
    response = client.get("/v1/school-facility-counts/stats")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["recordCount"] == 1227
    assert body["data"]["totalOrganizationalUnitCount"] == 7026
    assert body["data"]["regionLinkedCount"] == 1227
    assert body["data"]["districtLinkedCount"] == 1227
    assert body["data"]["totalsByRegion"]["SK010"] == 774
    assert body["data"]["totalsBySchoolKind"]["MŠ"] == 3221


def test_schools_route_is_not_exposed() -> None:
    response = client.get("/v1/schools")

    assert response.status_code == 404


def test_districts_region_filter_returns_subset() -> None:
    response = client.get("/v1/districts?regionCode=SK010")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]
    assert all(district["regionCode"] == "SK010" for district in body["data"])


def test_known_district_code_returns_one_district() -> None:
    response = client.get("/v1/districts/SK0101")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["code"] == "SK0101"
    assert body["data"]["name"] == "Bratislava I"


def test_unknown_district_code_returns_404() -> None:
    response = client.get("/v1/districts/SK9999")

    assert response.status_code == 404
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "NOT_FOUND"


def test_municipalities_list_returns_enveloped_response() -> None:
    response = client.get("/v1/municipalities")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "public, max-age=86400"
    body = response.json()
    assert isinstance(body["data"], list)
    assert body["metadata"]["source"] == "OpenSK API static geography seed dataset"
    assert body["metadata"]["version"] == "v1"
    assert body["error"] is None


def test_municipalities_region_filter_returns_subset() -> None:
    response = client.get("/v1/municipalities?regionCode=SK010")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]
    assert all(municipality["regionCode"] == "SK010" for municipality in body["data"])


def test_municipalities_district_filter_returns_subset() -> None:
    response = client.get("/v1/municipalities?districtCode=SK0101")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]
    assert all(municipality["districtCode"] == "SK0101" for municipality in body["data"])


def test_invalid_municipality_region_filter_returns_400() -> None:
    response = client.get("/v1/municipalities?regionCode=SK01A")

    assert response.status_code == 400
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "INVALID_FORMAT"


def test_known_municipality_code_returns_one_municipality() -> None:
    response = client.get("/v1/municipalities/528595")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["code"] == "528595"
    assert body["data"]["name"] == "Bratislava - mestská časť Staré Mesto"
    assert body["data"]["districtCode"] == "SK0101"


def test_unknown_municipality_district_filter_returns_404() -> None:
    response = client.get("/v1/municipalities?districtCode=SK9999")

    assert response.status_code == 404
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "NOT_FOUND"


def test_unknown_municipality_code_returns_404() -> None:
    response = client.get("/v1/municipalities/999999")

    assert response.status_code == 404
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "NOT_FOUND"


def test_unsupported_holiday_year_returns_structured_404() -> None:
    response = client.get("/v1/holidays/1900")

    assert response.status_code == 404
    body = response.json()
    assert body["data"] is None
    assert body["metadata"]["source"] == "OpenSK API"
    assert body["error"]["code"] == "NOT_FOUND"
    assert body["error"]["message"] == "No holiday data available for year 1900"
    assert body["error"]["messageSk"] == "Nie sú dostupné sviatky pre rok 1900"


def test_psc_81101_returns_enveloped_response() -> None:
    response = client.get("/v1/psc/81101")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "public, max-age=86400"
    body = response.json()
    assert body["data"]["psc"] == "81101"
    assert body["data"]["matchCount"] == len(body["data"]["matches"])
    assert body["data"]["matches"]
    assert body["data"]["city"] == "Bratislava 1"
    assert body["data"]["municipalityCode"] == "528595"
    assert body["data"]["districtCode"] == "SK0101"
    assert body["data"]["regionCode"] == "SK010"
    assert body["data"]["municipality"] == "Bratislava - mestská časť Staré Mesto"
    assert body["data"]["district"] is None
    assert body["data"]["region"] == "Bratislavský kraj"
    assert body["data"]["country"] == "Slovakia"
    assert body["metadata"]["source"] == "OpenSK API static PSC dataset"
    assert body["metadata"]["lastUpdated"] == "2026-06-02"
    assert body["metadata"]["version"] == "v1"
    assert body["error"] is None


def test_psc_stats_reports_nonzero_counts() -> None:
    response = client.get("/v1/psc/stats")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["recordCount"] > 0
    assert body["data"]["uniquePscCount"] > 0
    assert body["metadata"]["source"] == "OpenSK API static PSC dataset"
    assert body["error"] is None


def test_psc_list_returns_paged_enveloped_response() -> None:
    response = client.get("/v1/psc")

    assert response.status_code == 200
    body = response.json()
    assert set(body["data"]) == {"items", "count", "total", "limit", "offset"}
    assert body["data"]["count"] == 100
    assert body["data"]["limit"] == 100
    assert body["data"]["offset"] == 0
    assert body["data"]["items"][0]["psc"] == "01001"
    assert body["metadata"]["source"] == "OpenSK API static PSC dataset"
    assert body["error"] is None


def test_psc_list_supports_max_limit_and_offset() -> None:
    response = client.get("/v1/psc?limit=500&offset=20")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["count"] == 500
    assert body["data"]["limit"] == 500
    assert body["data"]["offset"] == 20
    assert body["data"]["items"]


def test_psc_list_rejects_limit_over_max() -> None:
    response = client.get("/v1/psc?limit=501")

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_FORMAT"


def test_psc_list_filters_and_empty_results() -> None:
    region_response = client.get("/v1/psc?regionCode=SK010")
    district_response = client.get("/v1/psc?districtCode=SK0101")
    municipality_response = client.get("/v1/psc?municipalityCode=528595")
    delivery_response = client.get("/v1/psc?deliveryPost=Bratislava%201")
    empty_response = client.get("/v1/psc?deliveryPost=NoSuchDeliveryPost")

    assert region_response.status_code == 200
    assert district_response.status_code == 200
    assert municipality_response.status_code == 200
    assert delivery_response.status_code == 200
    assert empty_response.status_code == 200


    region_body = region_response.json()
    district_body = district_response.json()
    municipality_body = municipality_response.json()
    delivery_body = delivery_response.json()
    empty_body = empty_response.json()

    assert all(item["regionCode"] == "SK010" for item in region_body["data"]["items"])
    assert district_body["data"]["items"]
    assert all(item["districtCode"] == "SK0101" for item in district_body["data"]["items"])
    assert municipality_body["data"]["count"] == 9
    assert all(item["municipalityCode"] == "528595" for item in municipality_body["data"]["items"])
    assert all("Bratislava 1" in item["deliveryPost"] for item in delivery_body["data"]["items"])
    assert empty_body["data"]["items"] == []
    assert empty_body["data"]["total"] == 0


def test_psc_list_supports_exact_filters() -> None:
    response = client.get("/v1/psc?psc=81101&limit=1&offset=0")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["count"] == 1
    assert body["data"]["total"] == 1
    assert body["data"]["items"][0]["psc"] == "81101"


def test_psc_list_rejects_invalid_filters() -> None:
    invalid_psc = client.get("/v1/psc?psc=81A01")
    invalid_limit = client.get("/v1/psc?limit=abc")
    invalid_offset = client.get("/v1/psc?offset=-1")

    assert invalid_psc.status_code == 400
    assert invalid_psc.json()["error"]["code"] == "INVALID_FORMAT"
    assert invalid_limit.status_code == 400
    assert invalid_limit.json()["error"]["code"] == "INVALID_FORMAT"
    assert invalid_offset.status_code == 400
    assert invalid_offset.json()["error"]["code"] == "INVALID_FORMAT"


def test_psc_search_returns_results_and_validates_query() -> None:
    bratislava_response = client.get("/v1/psc/search?q=Bratislava")
    prefix_response = client.get("/v1/psc/search?q=811")
    missing_response = client.get("/v1/psc/search")
    short_response = client.get("/v1/psc/search?q=8")

    assert bratislava_response.status_code == 200
    assert prefix_response.status_code == 200
    assert missing_response.status_code == 400
    assert short_response.status_code == 400

    bratislava_body = bratislava_response.json()
    prefix_body = prefix_response.json()

    assert bratislava_body["data"]["items"]
    assert any("Bratislava" in item["city"] or "Bratislava" in item["municipality"] for item in bratislava_body["data"]["items"])
    assert prefix_body["data"]["items"]
    assert all(item["psc"].startswith("811") for item in prefix_body["data"]["items"])


def test_psc_stats_returns_summary() -> None:
    response = client.get("/v1/psc/stats")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["recordCount"] == 3101
    assert body["data"]["uniquePscCount"] == 1420
    assert body["data"]["multiMatchPscCount"] == 759
    assert body["data"]["geographyCoverage"]["municipalityCode"] == {"count": 3101, "percentage": 100.0}
    assert body["data"]["geographyCoverage"]["regionCode"] == {"count": 3101, "percentage": 100.0}
    assert body["data"]["geographyCoverage"]["districtCode"] == {"count": 3101, "percentage": 100.0}
    assert body["data"]["source"]["name"] == "PortalVS Číselníky classifier 42"
    assert body["data"]["source"]["licenceStatus"] == "Source/licence verification pending."
    assert body["metadata"]["source"] == "OpenSK API static PSC dataset"
    assert body["error"] is None


def test_psc_81101_with_geography_includes_nested_objects() -> None:
    response = client.get("/v1/psc/81101?include=geography")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["matchCount"] == len(body["data"]["matches"])
    assert body["data"]["municipalityCode"] == "528595"
    assert body["data"]["districtCode"] == "SK0101"
    assert body["data"]["regionCode"] == "SK010"
    assert body["data"]["geography"]["district"]["code"] == body["data"]["districtCode"]
    assert body["data"]["geography"]["region"]["code"] == body["data"]["regionCode"]
    assert body["data"]["geography"]["municipality"]["code"] == body["data"]["municipalityCode"]
    assert body["data"]["geography"]["municipality"]["regionCode"] == body["data"]["regionCode"]
    assert body["metadata"]["source"] == "OpenSK API static PSC dataset + static geography seed datasets"
    assert body["metadata"]["lastUpdated"] == "2026-06-02"
    assert body["metadata"]["version"] == "v1"
    assert body["error"] is None


def test_invalid_psc_include_returns_400() -> None:
    response = client.get("/v1/psc/81101?include=bogus")

    assert response.status_code == 400
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "INVALID_FORMAT"
    assert body["error"]["message"] == "include must be omitted or set to geography"


def test_psc_with_space_is_normalized() -> None:
    response = client.get("/v1/psc/811%2001")

    assert response.status_code == 200
    assert response.json()["data"]["psc"] == "81101"


def test_invalid_psc_returns_400() -> None:
    response = client.get("/v1/psc/81A01")

    assert response.status_code == 400
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "INVALID_FORMAT"
    assert body["error"]["message"] == "PSC must be a 5-digit Slovak postal code"
    assert body["error"]["messageSk"] == "PSČ musí byť 5-ciferné slovenské poštové číslo"


def test_unknown_valid_psc_returns_404() -> None:
    response = client.get("/v1/psc/99999")

    assert response.status_code == 404
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "NOT_FOUND"
    assert body["error"]["message"] == "No PSC data available for 99999"
    assert body["error"]["messageSk"] == "Pre PSČ 99999 nie sú dostupné údaje"


def test_psc_seed_records_reference_existing_geography() -> None:
    from services.geography_service import load_districts, load_municipalities, load_regions
    from services.psc_service import index_psc_data

    regions = {region["code"]: region for region in load_regions()}
    districts = {district["code"]: district for district in load_districts()}
    municipalities = {municipality["code"]: municipality for municipality in load_municipalities()}

    for psc_code, records in index_psc_data().items():
        for record in records:
            region_code = record.get("regionCode")
            district_code = record.get("districtCode")
            municipality_code = record.get("municipalityCode")

            if region_code is not None:
                assert region_code in regions, psc_code

            if district_code is not None:
                assert district_code in districts, psc_code
                if region_code is not None:
                    assert districts[district_code]["regionCode"] == region_code, psc_code

            if municipality_code is not None:
                assert municipality_code in municipalities, psc_code
                if district_code is not None:
                    assert municipalities[municipality_code]["districtCode"] == district_code, psc_code
                if region_code is not None:
                    assert municipalities[municipality_code]["regionCode"] == region_code, psc_code


def test_unknown_route_returns_enveloped_404() -> None:
    response = client.get("/v1/does-not-exist")

    assert response.status_code == 404
    body = response.json()
    assert body["data"] is None
    assert body["metadata"]["source"] == "OpenSK API"
    assert body["error"]["code"] == "NOT_FOUND"


def test_validation_error_returns_enveloped_422() -> None:
    response = client.get("/v1/holidays/not-a-year")

    assert response.status_code == 422
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "VALIDATION_ERROR"
