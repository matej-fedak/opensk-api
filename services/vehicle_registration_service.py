import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "vehicle_registration_codes.json"
VEHICLE_REGISTRATION_LIST_DEFAULT_LIMIT = 100
VEHICLE_REGISTRATION_LIST_MAX_LIMIT = 500
VEHICLE_REGISTRATION_SEARCH_DEFAULT_LIMIT = 50
VEHICLE_REGISTRATION_SEARCH_MAX_LIMIT = 200


class VehicleRegistrationCodeInvalidFormatError(ValueError):
    pass


class VehicleRegistrationCodeNotFoundError(KeyError):
    pass


def normalize_vehicle_registration_code(code: str) -> str:
    return code.replace(" ", "").upper()


def validate_vehicle_registration_code_format(code: str) -> str:
    normalized = normalize_vehicle_registration_code(code)
    if not re.fullmatch(r"[A-Z]{2}", normalized):
        raise VehicleRegistrationCodeInvalidFormatError(code)
    return normalized


def _normalize_text(value: Any) -> str:
    text = "" if value is None else str(value)
    normalized = unicodedata.normalize("NFKD", text.casefold())
    return "".join(char for char in normalized if not unicodedata.combining(char))


@lru_cache(maxsize=1)
def load_vehicle_registration_code_data() -> dict[str, object]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise ValueError("vehicle_registration_codes dataset must be an object")
    return payload


@lru_cache(maxsize=1)
def load_vehicle_registration_code_records() -> list[dict[str, object]]:
    records = load_vehicle_registration_code_data().get("vehicleRegistrationCodes")
    if not isinstance(records, list):
        raise ValueError("vehicle_registration_codes dataset must contain vehicleRegistrationCodes array")
    return [dict(record) for record in records if isinstance(record, dict)]


def filter_vehicle_registration_code_records(filters: dict[str, object] | None = None) -> list[dict[str, object]]:
    filters = filters or {}
    records = load_vehicle_registration_code_records()

    code = filters.get("code")
    if isinstance(code, str):
        records = [record for record in records if record.get("code") == code]

    for field in ("districtCode", "regionCode", "status"):
        value = filters.get(field)
        if isinstance(value, str):
            records = [record for record in records if record.get(field) == value]

    district_name = filters.get("districtName")
    if isinstance(district_name, str) and district_name.strip():
        query = _normalize_text(district_name)
        records = [record for record in records if query in _normalize_text(record.get("districtName"))]

    return records


def list_vehicle_registration_codes(
    filters: dict[str, object] | None = None,
    *,
    limit: int = VEHICLE_REGISTRATION_LIST_DEFAULT_LIMIT,
    offset: int = 0,
) -> list[dict[str, object]]:
    return filter_vehicle_registration_code_records(filters)[offset : offset + limit]


def get_vehicle_registration_code(code: str) -> dict[str, object]:
    normalized = validate_vehicle_registration_code_format(code)
    records = filter_vehicle_registration_code_records({"code": normalized})
    if not records:
        raise VehicleRegistrationCodeNotFoundError(normalized)
    return records[0]


def search_vehicle_registration_code_records(q: str) -> list[dict[str, object]]:
    query = q.strip()
    if len(query) < 2:
        raise VehicleRegistrationCodeInvalidFormatError(q)
    normalized_query = _normalize_text(query)
    return [
        record
        for record in load_vehicle_registration_code_records()
        if normalized_query in _normalize_text(record.get("code"))
        or normalized_query in _normalize_text(record.get("districtName"))
        or normalized_query in _normalize_text(record.get("districtCode"))
        or normalized_query in _normalize_text(record.get("regionCode"))
    ]


def search_vehicle_registration_codes(
    q: str,
    *,
    limit: int = VEHICLE_REGISTRATION_SEARCH_DEFAULT_LIMIT,
    offset: int = 0,
) -> list[dict[str, object]]:
    return search_vehicle_registration_code_records(q)[offset : offset + limit]


def get_vehicle_registration_code_stats() -> dict[str, int]:
    records = load_vehicle_registration_code_records()
    return {
        "recordCount": len(records),
        "districtLinkedCount": sum(1 for record in records if record.get("districtCode")),
        "regionLinkedCount": sum(1 for record in records if record.get("regionCode")),
    }
