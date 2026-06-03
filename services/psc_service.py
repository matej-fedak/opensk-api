import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any

from services.geography_service import (
    GeographyInvalidFormatError,
    GeographyNotFoundError,
    get_district,
    get_municipality,
    get_region,
    validate_district_code_format,
    validate_municipality_code_format,
    validate_region_code_format,
)


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "psc.json"
PSC_LIST_DEFAULT_LIMIT = 100
PSC_LIST_MAX_LIMIT = 500
PSC_SEARCH_DEFAULT_LIMIT = 50
PSC_SEARCH_MAX_LIMIT = 200
PSC_SOURCE_NAME = "PortalVS Číselníky classifier 42"
PSC_LICENCE_STATUS = "Source/licence verification pending."


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


def validate_psc_search_query(q: str) -> str:
    normalized = normalize_psc(q)
    if not re.fullmatch(r"\d{2,5}", normalized):
        raise PSCInvalidFormatError(q)
    return normalized


@lru_cache(maxsize=1)
def load_psc_data() -> list[dict[str, object]]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        raw_data = json.load(file)

    if isinstance(raw_data, list):
        records = raw_data
    elif isinstance(raw_data, dict):
        records = [value for key, value in raw_data.items() if key != "metadata"]
    else:
        raise ValueError("PSC dataset must be a list or object of records")

    return [dict(record) for record in records if isinstance(record, dict)]


def _record_sort_key(record: dict[str, object]) -> tuple[str, str, str, str]:
    return (
        normalize_psc(str(record.get("psc") or record.get("code") or "")),
        _normalize_text(record.get("municipalityName") or record.get("municipality")),
        _normalize_text(record.get("deliveryPost") or record.get("city")),
        normalize_psc(str(record.get("municipalityCode") or "")),
    )


def _normalize_flat_record(record: dict[str, object], fallback_psc: str | None = None) -> dict[str, object]:
    normalized = dict(record)
    raw_psc = normalized.get("psc") if normalized.get("psc") is not None else normalized.get("code")
    if raw_psc is None and fallback_psc is not None:
        raw_psc = fallback_psc
    if raw_psc is not None:
        normalized["psc"] = normalize_psc(str(raw_psc))
    return normalized


@lru_cache(maxsize=1)
def load_psc_records() -> list[dict[str, object]]:
    flattened: list[dict[str, object]] = []

    for entry in load_psc_data():
        matches = entry.get("matches")
        entry_psc = str(entry.get("psc") or entry.get("code") or "")

        if isinstance(matches, list) and matches:
            for match in matches:
                if isinstance(match, dict):
                    flattened.append(_normalize_flat_record(match, fallback_psc=entry_psc or None))
        else:
            flattened.append(_normalize_flat_record(entry, fallback_psc=entry_psc or None))

    return sorted(flattened, key=_record_sort_key)


@lru_cache(maxsize=1)
def load_psc_metadata() -> dict[str, object]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        raw_data = json.load(file)

    if isinstance(raw_data, dict):
        metadata = raw_data.get("metadata")
        if isinstance(metadata, dict):
            return dict(metadata)

    return {}


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


def _normalize_text(value: Any) -> str:
    text = "" if value is None else str(value)
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(character for character in decomposed if not unicodedata.combining(character)).casefold()


def _record_has_geography(record: dict[str, object]) -> bool:
    if any(record.get(field) is not None for field in ("regionCode", "districtCode", "municipalityCode")):
        return True

    matches = record.get("matches")
    if isinstance(matches, list):
        for match in matches:
            if isinstance(match, dict) and any(match.get(field) is not None for field in ("regionCode", "districtCode", "municipalityCode")):
                return True

    return False


def _record_search_haystack(record: dict[str, object]) -> str:
    parts: list[str] = []
    for field in ("psc", "municipality", "municipalityName", "deliveryPost", "city"):
        value = record.get(field)
        if value is not None:
            parts.append(str(value))

    matches = record.get("matches")
    if isinstance(matches, list):
        for match in matches:
            if not isinstance(match, dict):
                continue
            for field in ("municipality", "deliveryPost"):
                value = match.get(field)
                if value is not None:
                    parts.append(str(value))

    return _normalize_text(" ".join(parts))


def filter_psc_records(filters: dict[str, object] | None = None) -> list[dict[str, object]]:
    records = load_psc_records()
    if not filters:
        return records

    filtered = records

    psc_filter = filters.get("psc")
    if psc_filter is not None:
        normalized_psc = validate_psc_format(str(psc_filter))
        filtered = [record for record in filtered if normalize_psc(str(record.get("psc") or record.get("code") or "")) == normalized_psc]

    region_code_filter = filters.get("regionCode")
    if region_code_filter is not None:
        normalized_region_code = validate_region_code_format(str(region_code_filter))
        filtered = [record for record in filtered if record.get("regionCode") == normalized_region_code]

    district_code_filter = filters.get("districtCode")
    if district_code_filter is not None:
        normalized_district_code = validate_district_code_format(str(district_code_filter))
        filtered = [record for record in filtered if record.get("districtCode") == normalized_district_code]

    municipality_code_filter = filters.get("municipalityCode")
    if municipality_code_filter is not None:
        normalized_municipality_code = validate_municipality_code_format(str(municipality_code_filter))
        filtered = [record for record in filtered if record.get("municipalityCode") == normalized_municipality_code]

    delivery_post_filter = filters.get("deliveryPost")
    if delivery_post_filter is not None:
        normalized_delivery_post = _normalize_text(delivery_post_filter)
        filtered = [
            record
            for record in filtered
            if normalized_delivery_post in _normalize_text(record.get("deliveryPost") or record.get("city"))
        ]

    municipality_name_filter = filters.get("municipalityName")
    if municipality_name_filter is not None:
        normalized_municipality_name = _normalize_text(municipality_name_filter)
        filtered = [record for record in filtered if normalized_municipality_name in _normalize_text(record.get("municipality") or record.get("municipalityName"))]

    has_geography_filter = filters.get("hasGeography")
    if has_geography_filter is not None:
        expected_has_geography = bool(has_geography_filter)
        filtered = [record for record in filtered if _record_has_geography(record) == expected_has_geography]

    return filtered


def list_psc_records(filters: dict[str, object] | None, limit: int, offset: int) -> list[dict[str, object]]:
    if limit < 0:
        raise ValueError("limit must be non-negative")
    if offset < 0:
        raise ValueError("offset must be non-negative")

    filtered = filter_psc_records(filters)
    return filtered[offset : offset + limit]


def search_psc_records(query: str) -> list[dict[str, object]]:
    normalized_query = query.strip()
    if len(normalized_query) < 2:
        raise PSCInvalidFormatError(query)

    normalized_psc_query = normalize_psc(normalized_query)
    is_numeric_query = bool(re.fullmatch(r"\d[\d ]*", normalized_query))

    if is_numeric_query:
        digits = validate_psc_search_query(normalized_query)
        return [record for record in load_psc_records() if normalize_psc(str(record.get("psc") or record.get("code") or "")).startswith(digits)]

    lowered_query = _normalize_text(normalized_query)
    return [record for record in load_psc_records() if lowered_query in _record_search_haystack(record)]


def search_psc(query: str, limit: int, offset: int) -> list[dict[str, object]]:
    if limit < 0:
        raise ValueError("limit must be non-negative")
    if offset < 0:
        raise ValueError("offset must be non-negative")

    matched_records = search_psc_records(query)
    return matched_records[offset : offset + limit]


def get_psc_stats() -> dict[str, object]:
    records = load_psc_records()
    source_entries = load_psc_data()
    indexed = index_psc_data()

    def _coverage(field_name: str) -> dict[str, object]:
        count = sum(1 for record in records if record.get(field_name) is not None)
        percentage = round((count / len(records) * 100) if records else 0.0, 1)
        return {"count": count, "percentage": percentage}

    return {
        "recordCount": len(records),
        "uniquePscCount": len(indexed),
        "multiMatchPscCount": sum(
            1
            for entry in source_entries
            if isinstance(entry, dict)
            and (
                (isinstance(entry.get("matches"), list) and len(entry["matches"]) > 1)
                or (isinstance(entry.get("matchCount"), int) and entry["matchCount"] > 1)
            )
        ),
        "geographyCoverage": {
            "municipalityCode": _coverage("municipalityCode"),
            "regionCode": _coverage("regionCode"),
            "districtCode": _coverage("districtCode"),
        },
        "source": {"name": PSC_SOURCE_NAME, "licenceStatus": PSC_LICENCE_STATUS},
    }
