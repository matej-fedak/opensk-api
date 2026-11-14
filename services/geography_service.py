import json
import re
from functools import lru_cache
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REGIONS_FILE = DATA_DIR / "regions.json"
DISTRICTS_FILE = DATA_DIR / "districts.json"
MUNICIPALITIES_FILE = DATA_DIR / "municipalities.json"


class GeographyInvalidFormatError(ValueError):
    pass


class GeographyNotFoundError(KeyError):
    pass


def normalize_code(code: str) -> str:
    return code.replace(" ", "")


def validate_region_code_format(code: str) -> str:
    normalized = normalize_code(code)
    if not re.fullmatch(r"SK[0-9]{3}", normalized):
        raise GeographyInvalidFormatError(code)
    return normalized


def validate_district_code_format(code: str) -> str:
    normalized = normalize_code(code)
    if not re.fullmatch(r"SK[0-9]{4,5}", normalized):
        raise GeographyInvalidFormatError(code)
    return normalized


def validate_municipality_code_format(code: str) -> str:
    normalized = normalize_code(code)
    if not re.fullmatch(r"[0-9]{6}", normalized):
        raise GeographyInvalidFormatError(code)
    return normalized


@lru_cache(maxsize=1)
def load_regions_data() -> dict[str, object]:
    with REGIONS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


@lru_cache(maxsize=1)
def load_districts_data() -> dict[str, object]:
    with DISTRICTS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


@lru_cache(maxsize=1)
def load_municipalities_data() -> dict[str, object]:
    with MUNICIPALITIES_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_regions() -> list[dict[str, str]]:
    return list(load_regions_data().get("regions", []))


def load_districts() -> list[dict[str, str]]:
    return list(load_districts_data().get("districts", []))


def load_municipalities() -> list[dict[str, str]]:
    return list(load_municipalities_data().get("municipalities", []))


def _code_index(records: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for record in records:
        # Keep the first match, as the original ordered lookup did.
        indexed.setdefault(record["code"], record)
    return indexed


@lru_cache(maxsize=1)
def index_regions() -> dict[str, dict[str, str]]:
    return _code_index(load_regions())


@lru_cache(maxsize=1)
def index_districts() -> dict[str, dict[str, str]]:
    return _code_index(load_districts())


@lru_cache(maxsize=1)
def index_municipalities() -> dict[str, dict[str, str]]:
    return _code_index(load_municipalities())


def get_region(code: str) -> dict[str, str]:
    normalized = validate_region_code_format(code)

    region = index_regions().get(normalized)
    if region is not None:
        return region

    raise GeographyNotFoundError(normalized)


def get_district(code: str) -> dict[str, str]:
    normalized = validate_district_code_format(code)

    district = index_districts().get(normalized)
    if district is not None:
        return district

    raise GeographyNotFoundError(normalized)


def get_municipality(code: str) -> dict[str, str]:
    normalized = validate_municipality_code_format(code)

    municipality = index_municipalities().get(normalized)
    if municipality is not None:
        return municipality

    raise GeographyNotFoundError(normalized)


def list_districts(region_code: str | None = None) -> list[dict[str, str]]:
    districts = load_districts()

    if region_code is None:
        return districts

    normalized_region_code = validate_region_code_format(region_code)
    get_region(normalized_region_code)
    return [district for district in districts if district.get("regionCode") == normalized_region_code]


def list_municipalities(
    region_code: str | None = None,
    district_code: str | None = None,
) -> list[dict[str, str]]:
    municipalities = load_municipalities()

    normalized_region_code = None
    normalized_district_code = None

    if region_code is not None:
        normalized_region_code = validate_region_code_format(region_code)
        get_region(normalized_region_code)

    if district_code is not None:
        normalized_district_code = validate_district_code_format(district_code)
        get_district(normalized_district_code)

    filtered = municipalities
    if normalized_region_code is not None:
        filtered = [municipality for municipality in filtered if municipality.get("regionCode") == normalized_region_code]
    if normalized_district_code is not None:
        filtered = [municipality for municipality in filtered if municipality.get("districtCode") == normalized_district_code]

    return filtered
