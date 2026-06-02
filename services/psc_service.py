import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from services.geography_service import GeographyInvalidFormatError, GeographyNotFoundError, get_district, get_municipality, get_region


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "psc.json"


class PSCInvalidFormatError(ValueError):
    pass


class PSCNotFoundError(KeyError):
    pass


def normalize_psc(psc: str) -> str:
    return psc.replace(" ", "")


def validate_psc_format(psc: str) -> str:
    normalized = normalize_psc(psc)
    if not re.fullmatch(r"\d{5}", normalized):
        raise PSCInvalidFormatError(psc)
    return normalized


@lru_cache(maxsize=1)
def load_psc_data() -> list[dict[str, object]]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        raw_data = json.load(file)

    if isinstance(raw_data, list):
        records = raw_data
    elif isinstance(raw_data, dict):
        records = list(raw_data.values())
    else:
        raise ValueError("PSC dataset must be a list or object of records")

    return [dict(record) for record in records if isinstance(record, dict)]


@lru_cache(maxsize=1)
def index_psc_data() -> dict[str, list[dict[str, object]]]:
    indexed: dict[str, list[dict[str, object]]] = {}

    for record in load_psc_data():
        raw_psc = record.get("psc") if record.get("psc") is not None else record.get("code")
        if raw_psc is None:
            continue

        try:
            normalized_psc = validate_psc_format(str(raw_psc))
        except PSCInvalidFormatError:
            continue

        indexed.setdefault(normalized_psc, []).append(record)

    return indexed


def _record_sort_value(record: dict[str, object], field: str) -> str:
    value: Any | None = record.get(field)
    if value is None and field == "code":
        value = record.get("psc")
    return "" if value is None else str(value)


def _has_local_municipality(record: dict[str, object]) -> bool:
    municipality_code = record.get("municipalityCode")
    if municipality_code is None:
        return False

    try:
        get_municipality(str(municipality_code))
    except (GeographyInvalidFormatError, GeographyNotFoundError):
        return False

    return True


def _primary_match_sort_key(record: dict[str, object]) -> tuple[int, int, str, str, str]:
    return (
        0 if _has_local_municipality(record) else 1,
        0 if record.get("validTo") is None else 1,
        _record_sort_value(record, "deliveryPost"),
        _record_sort_value(record, "name"),
        _record_sort_value(record, "code"),
    )


def _resolve_geography(psc_data: dict[str, object]) -> dict[str, object] | None:
    geography: dict[str, object] = {}

    region_code = psc_data.get("regionCode")
    if region_code is not None:
        try:
            geography["region"] = get_region(str(region_code))
        except (GeographyInvalidFormatError, GeographyNotFoundError):
            pass

    district_code = psc_data.get("districtCode")
    if district_code is not None:
        try:
            geography["district"] = get_district(str(district_code))
        except (GeographyInvalidFormatError, GeographyNotFoundError):
            pass

    municipality_code = psc_data.get("municipalityCode")
    if municipality_code is not None:
        try:
            geography["municipality"] = get_municipality(str(municipality_code))
        except (GeographyInvalidFormatError, GeographyNotFoundError):
            pass

    return geography or None


def _expand_match(record: dict[str, object], include_geography: bool, fallback_psc: str) -> dict[str, object]:
    expanded = dict(record)
    if expanded.get("psc") is not None:
        expanded["psc"] = normalize_psc(str(expanded["psc"]))
    else:
        expanded["psc"] = fallback_psc

    if include_geography:
        geography = _resolve_geography(expanded)
        if geography is not None:
            expanded["geography"] = geography

    return expanded


def lookup_psc(psc: str, include_geography: bool = False) -> dict[str, object]:
    normalized = validate_psc_format(psc)
    matches = index_psc_data().get(normalized, [])

    if not matches:
        raise PSCNotFoundError(normalized)

    ordered_matches = sorted(matches, key=_primary_match_sort_key)
    primary_match = _expand_match(ordered_matches[0], include_geography=include_geography, fallback_psc=normalized)

    result = dict(primary_match)
    result["matchCount"] = len(ordered_matches)
    result["matches"] = [_expand_match(match, include_geography=include_geography, fallback_psc=normalized) for match in ordered_matches]
    if include_geography:
        geography = _resolve_geography(result)
        if geography is not None:
            result["geography"] = geography
    return result
