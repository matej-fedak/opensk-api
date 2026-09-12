import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "phone_areas.json"
PHONE_AREA_LIST_DEFAULT_LIMIT = 100
PHONE_AREA_LIST_MAX_LIMIT = 500
PHONE_AREA_SEARCH_DEFAULT_LIMIT = 50
PHONE_AREA_SEARCH_MAX_LIMIT = 200


class PhoneAreaInvalidFormatError(ValueError):
    pass


class PhoneAreaNotFoundError(KeyError):
    pass


def normalize_phone_area_code(code: str) -> str:
    return code.replace(" ", "")


def validate_phone_area_code_format(code: str) -> str:
    normalized = normalize_phone_area_code(code)
    if not re.fullmatch(r"0\d{1,2}", normalized):
        raise PhoneAreaInvalidFormatError(code)
    return normalized


def _normalize_text(value: Any) -> str:
    text = "" if value is None else str(value)
    normalized = unicodedata.normalize("NFKD", text.casefold())
    return "".join(char for char in normalized if not unicodedata.combining(char))


@lru_cache(maxsize=1)
def load_phone_area_data() -> dict[str, object]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise ValueError("phone_areas dataset must be an object")
    return payload


@lru_cache(maxsize=1)
def load_phone_area_records() -> list[dict[str, object]]:
    records = load_phone_area_data().get("phoneAreas")
    if not isinstance(records, list):
        raise ValueError("phone_areas dataset must contain phoneAreas array")
    return [dict(record) for record in records if isinstance(record, dict)]


def filter_phone_area_records(filters: dict[str, object] | None = None) -> list[dict[str, object]]:
    filters = filters or {}
    records = load_phone_area_records()

    code = filters.get("code")
    if isinstance(code, str):
        records = [record for record in records if record.get("code") == code]

    for field in ("municipalityCode", "regionCode", "districtCode"):
        value = filters.get(field)
        if isinstance(value, str):
            records = [record for record in records if record.get(field) == value]

    municipality_name = filters.get("municipalityName")
    if isinstance(municipality_name, str) and municipality_name.strip():
        query = _normalize_text(municipality_name)
        records = [record for record in records if query in _normalize_text(record.get("municipalityName"))]

    return records


def list_phone_areas(filters: dict[str, object] | None = None, *, limit: int = PHONE_AREA_LIST_DEFAULT_LIMIT, offset: int = 0) -> list[dict[str, object]]:
    return filter_phone_area_records(filters)[offset : offset + limit]


def get_phone_area_by_code(code: str) -> list[dict[str, object]]:
    normalized = validate_phone_area_code_format(code)
    records = filter_phone_area_records({"code": normalized})
    if not records:
        raise PhoneAreaNotFoundError(normalized)
    return records


def search_phone_areas(q: str, *, limit: int = PHONE_AREA_SEARCH_DEFAULT_LIMIT, offset: int = 0) -> list[dict[str, object]]:
    query = q.strip()
    if len(query) < 2:
        raise PhoneAreaInvalidFormatError(q)
    normalized_query = _normalize_text(query)
    matches = [
        record
        for record in load_phone_area_records()
        if normalized_query in _normalize_text(record.get("code"))
        or normalized_query in _normalize_text(record.get("name"))
        or normalized_query in _normalize_text(record.get("municipalityName"))
        or normalized_query in _normalize_text(record.get("municipalityCode"))
    ]
    return matches[offset : offset + limit]


def search_phone_area_records(q: str) -> list[dict[str, object]]:
    query = q.strip()
    if len(query) < 2:
        raise PhoneAreaInvalidFormatError(q)
    normalized_query = _normalize_text(query)
    return [
        record
        for record in load_phone_area_records()
        if normalized_query in _normalize_text(record.get("code"))
        or normalized_query in _normalize_text(record.get("name"))
        or normalized_query in _normalize_text(record.get("municipalityName"))
        or normalized_query in _normalize_text(record.get("municipalityCode"))
    ]


def get_phone_area_stats() -> dict[str, int]:
    records = load_phone_area_records()
    linked = [record for record in records if record.get("municipalityCode") and record.get("districtCode") and record.get("regionCode")]
    return {
        "recordCount": len(records),
        "uniqueCodeCount": len({str(record.get("code")) for record in records}),
        "municipalityLinkedCount": len(linked),
    }
