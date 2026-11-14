"""User-controlled numeric inputs must never escape as conversion errors."""

import pytest
from fastapi.testclient import TestClient

from main import app
from services.iban_service import iban_checksum_valid, validate_iban
from services.numeric_parser import parse_ascii_integer


client = TestClient(app)
PAGINATED_PATHS = [
    "/v1/psc", "/v1/psc/search?q=Bratislava",
    "/v1/phone-areas", "/v1/phone-areas/search?q=Bratislava",
    "/v1/vehicle-registration-codes", "/v1/vehicle-registration-codes/search?q=Bratislava",
    "/v1/school-facility-counts", "/v1/procurement-notices",
    "/v1/procurement-notices/search?q=Bratislava",
    "/v1/eu-funds/projects", "/v1/elections/NRSR2023/results",
]


@pytest.mark.parametrize("path", PAGINATED_PATHS)
@pytest.mark.parametrize("parameter", ["limit", "offset"])
@pytest.mark.parametrize("value", ["²", "٢", "9" * 4301, "0" * 4301])
def test_pagination_rejects_non_ascii_and_oversized_numbers(path, parameter, value):
    params = {parameter: value}
    if "/search" in path:
        params["q"] = "Bratislava"
    response = client.get(path, params=params)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_FORMAT"


@pytest.mark.parametrize("value", ["²", "٢", "9" * 4301, "-" + "9" * 4301, "0" * 4301])
def test_business_day_delta_rejects_unsafe_numbers(value):
    response = client.get("/v1/business-days/add", params={"date": "2026-10-08", "days": value})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_FORMAT"


@pytest.mark.parametrize("path", ["/v1/holidays/", "/v1/procurement-notices?year="])
@pytest.mark.parametrize("value", ["²", "9" * 4301])
def test_framework_numeric_fields_keep_documented_422(path, value):
    response = client.get(path + value)
    assert response.status_code == 422


@pytest.mark.parametrize("path", [
    "/v1/banks/١١٠٠", "/v1/psc/٠١٠٠١", "/v1/regions/SK٠١٠",
    "/v1/districts/SK٠١٠١", "/v1/municipalities/٥١٧٤٠٢",
    "/v1/companies/١٢٣٤٥٦٧٨", "/v1/ico/١٢٣٤٥٦٧٨", "/v1/phone-areas/0٢",
    "/v1/psc/search?q=²²", "/v1/psc/search?q=٠١",
])
def test_numeric_identifiers_require_ascii_digits(path):
    response = client.get(path)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_FORMAT"


def test_ascii_integer_bounds_and_existing_syntax():
    assert parse_ascii_integer("0005", maximum=500) == 5
    assert parse_ascii_integer("1000000000", maximum=10**9) == 10**9
    assert parse_ascii_integer("-5", minimum=-500, maximum=500, signed=True) == -5
    for value in ("", "+1", " 1", "-1", "501", "0" * 11):
        with pytest.raises(ValueError):
            parse_ascii_integer(value, maximum=500)


def _checksummed_iban(bban: str) -> str:
    numeric = "".join(str(ord(char) - 55) if char.isalpha() else char for char in bban + "SK00")
    return f"SK{98 - int(numeric) % 97:02d}" + bban


@pytest.mark.parametrize("bban", ["1100" + "0" * 15, "1100" + "0" * 17, "1100" + "A" + "0" * 15])
def test_checksum_alone_does_not_make_a_slovak_iban_valid(bban):
    iban = _checksummed_iban(bban)
    assert iban_checksum_valid(iban) is True
    result = validate_iban(iban)
    assert result["valid"] is False
    assert result["bankCode"] is None


@pytest.mark.parametrize("iban", [
    "SK83²1000000002918669357", "SK83١1000000002918669357",
    "ſK8311000000002918669357", "SK83é1000000002918669357", "SK" + "9" * 4301,
])
def test_unicode_and_oversized_iban_return_false_without_crashing(iban):
    assert iban_checksum_valid(iban) is False
    response = client.get("/v1/iban/validate/" + iban)
    assert response.status_code == 200
    assert response.json()["data"]["checksumValid"] is False
    assert response.json()["data"]["valid"] is False
    assert response.headers["cache-control"] == "no-store"


def test_lowercase_spaced_slovak_iban_remains_supported():
    result = validate_iban("sk29 1100 0000 0029 1866 9357")
    assert result["valid"] is True
    assert result["bankCode"] == "1100"
