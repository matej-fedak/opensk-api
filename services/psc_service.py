import json
import re
from functools import lru_cache
from pathlib import Path

from services.geography_service import get_district, get_municipality, get_region


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "psc.json"


class PSCInvalidFormatError(ValueError):
    pass


class PSCNotFoundError(KeyError):
    pass


class PSCGeographyDataError(ValueError):
    pass


def normalize_psc(psc: str) -> str:
    return psc.replace(" ", "")


def validate_psc_format(psc: str) -> str:
    normalized = normalize_psc(psc)
    if not re.fullmatch(r"\d{5}", normalized):
        raise PSCInvalidFormatError(psc)
    return normalized


@lru_cache(maxsize=1)
def load_psc_data() -> dict[str, dict[str, object]]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def _resolve_geography(psc_data: dict[str, object]) -> dict[str, object] | None:
    region_code = psc_data.get("regionCode")
    district_code = psc_data.get("districtCode")
    municipality_code = psc_data.get("municipalityCode")

    if region_code is None and district_code is None and municipality_code is None:
        return None

    geography: dict[str, object] = {}

    if region_code is not None:
        region = get_region(str(region_code))
        geography["region"] = region

    if district_code is not None:
        district = get_district(str(district_code))
        geography["district"] = district
        if region_code is not None and district.get("regionCode") != region_code:
            raise PSCGeographyDataError(f"District {district_code} does not match PSC region {region_code}")

    if municipality_code is not None:
        municipality = get_municipality(str(municipality_code))
        geography["municipality"] = municipality
        if district_code is not None and municipality.get("districtCode") != district_code:
            raise PSCGeographyDataError(f"Municipality {municipality_code} does not match PSC district {district_code}")
        if region_code is not None and municipality.get("regionCode") != region_code:
            raise PSCGeographyDataError(f"Municipality {municipality_code} does not match PSC region {region_code}")

    return geography


def lookup_psc(psc: str, include_geography: bool = False) -> dict[str, object]:
    normalized = validate_psc_format(psc)
    psc_data = load_psc_data()

    if normalized not in psc_data:
        raise PSCNotFoundError(normalized)

    result = dict(psc_data[normalized])
    if include_geography:
        geography = _resolve_geography(result)
        if geography is not None:
            result["geography"] = geography
    return result
