import json
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "school_facility_counts.json"
SCHOOL_FACILITY_COUNT_LIST_DEFAULT_LIMIT = 100
SCHOOL_FACILITY_COUNT_LIST_MAX_LIMIT = 500


def _normalize_text(value: Any) -> str:
    text = "" if value is None else str(value)
    normalized = unicodedata.normalize("NFKD", text.casefold())
    return "".join(char for char in normalized if not unicodedata.combining(char))


@lru_cache(maxsize=1)
def load_school_facility_count_data() -> dict[str, object]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise ValueError("school_facility_counts dataset must be an object")
    return payload


@lru_cache(maxsize=1)
def load_school_facility_count_records() -> list[dict[str, object]]:
    records = load_school_facility_count_data().get("schoolFacilityCounts")
    if not isinstance(records, list):
        raise ValueError("school_facility_counts dataset must contain schoolFacilityCounts array")
    return [dict(record) for record in records if isinstance(record, dict)]


def filter_school_facility_count_records(filters: dict[str, object] | None = None) -> list[dict[str, object]]:
    filters = filters or {}
    records = load_school_facility_count_records()

    exact_fields = {
        "schoolKindShort": filters.get("schoolKind"),
        "schoolTypeShort": filters.get("schoolType"),
        "regionCode": filters.get("regionCode"),
        "districtCode": filters.get("districtCode"),
        "founderOwnershipType": filters.get("founderOwnershipType"),
        "founderType": filters.get("founderType"),
    }
    for field, value in exact_fields.items():
        if isinstance(value, str) and value.strip():
            records = [record for record in records if record.get(field) == value]

    for field in ("regionName", "districtName"):
        value = filters.get(field)
        if isinstance(value, str) and value.strip():
            query = _normalize_text(value)
            records = [record for record in records if query in _normalize_text(record.get(field))]

    return records


def list_school_facility_counts(
    filters: dict[str, object] | None = None,
    *,
    limit: int = SCHOOL_FACILITY_COUNT_LIST_DEFAULT_LIMIT,
    offset: int = 0,
) -> list[dict[str, object]]:
    return filter_school_facility_count_records(filters)[offset : offset + limit]


def _add_total(bucket: dict[str, int], key: object, count: int) -> None:
    if isinstance(key, str) and key:
        bucket[key] = bucket.get(key, 0) + count


def get_school_facility_count_stats() -> dict[str, object]:
    records = load_school_facility_count_records()
    totals_by_region: dict[str, int] = {}
    totals_by_district: dict[str, int] = {}
    totals_by_school_kind: dict[str, int] = {}
    totals_by_school_type: dict[str, int] = {}
    totals_by_founder_type: dict[str, int] = {}
    total_units = 0

    for record in records:
        count = record.get("organizationalUnitCount")
        if not isinstance(count, int):
            continue
        total_units += count
        _add_total(totals_by_region, record.get("regionCode"), count)
        _add_total(totals_by_district, record.get("districtCode"), count)
        _add_total(totals_by_school_kind, record.get("schoolKindShort"), count)
        _add_total(totals_by_school_type, record.get("schoolTypeShort"), count)
        _add_total(totals_by_founder_type, record.get("founderType"), count)

    return {
        "recordCount": len(records),
        "totalOrganizationalUnitCount": total_units,
        "regionLinkedCount": sum(1 for record in records if record.get("regionCode")),
        "districtLinkedCount": sum(1 for record in records if record.get("districtCode")),
        "totalsByRegion": dict(sorted(totals_by_region.items())),
        "totalsByDistrict": dict(sorted(totals_by_district.items())),
        "totalsBySchoolKind": dict(sorted(totals_by_school_kind.items())),
        "totalsBySchoolType": dict(sorted(totals_by_school_type.items())),
        "totalsByFounderType": dict(sorted(totals_by_founder_type.items())),
    }
