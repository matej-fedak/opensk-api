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
    assert "/v1/psc/{psc}" in schema["paths"]


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
    assert any(bank["code"] == "0900" for bank in body["data"])
    assert body["metadata"]["source"] == "OpenSK API static banks dataset"
    assert body["metadata"]["lastUpdated"] == "2026-05-25"
    assert body["error"] is None


def test_known_bank_code_returns_enveloped_response() -> None:
    response = client.get("/v1/banks/1100")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["code"] == "1100"
    assert body["data"]["name"] == "Tatra banka, a.s."
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
    assert body["metadata"]["source"] == "OpenSK API static dataset"
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
    assert body["metadata"]["source"] == "OpenSK API static geography dataset"
    assert body["metadata"]["version"] == "v1"
    assert body["error"] is None


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
    assert body["data"]["name"] == "Bratislava - Staré Mesto"


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
    assert body["data"]["city"] == "Bratislava"
    assert body["metadata"]["source"] == "OpenSK API static PSC seed dataset"
    assert body["metadata"]["lastUpdated"] == "2026-05-25"
    assert body["metadata"]["version"] == "v1"
    assert body["error"] is None


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
