import json
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "procurement_notices.json"
PROCUREMENT_NOTICE_LIST_DEFAULT_LIMIT = 100
PROCUREMENT_NOTICE_LIST_MAX_LIMIT = 500
PROCUREMENT_NOTICE_SEARCH_DEFAULT_LIMIT = 50
PROCUREMENT_NOTICE_SEARCH_MAX_LIMIT = 200


def _normalize_text(value: Any) -> str:
    text = "" if value is None else str(value)
    normalized = unicodedata.normalize("NFKD", text.casefold())
    return "".join(char for char in normalized if not unicodedata.combining(char))


@lru_cache(maxsize=1)
def load_procurement_notice_data() -> dict[str, Any]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise ValueError("procurement notices dataset must be an object")
    return payload


@lru_cache(maxsize=1)
def load_procurement_notice_records() -> list[dict[str, Any]]:
    records = load_procurement_notice_data().get("procurementNotices")
    if not isinstance(records, list):
        raise ValueError("procurement notices dataset must contain procurementNotices array")
    return [dict(record) for record in records if isinstance(record, dict)]


def filter_procurement_notice_records(filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    filters = filters or {}
    records = load_procurement_notice_records()

    notice_type = filters.get("noticeType")
    if isinstance(notice_type, str) and notice_type.strip():
        normalized_notice_type = notice_type.strip().casefold()
        records = [record for record in records if str(record.get("noticeType", "")).casefold() == normalized_notice_type]

    year = filters.get("year")
    if isinstance(year, int):
        prefix = f"{year}-"
        records = [record for record in records if str(record.get("publicationDate", "")).startswith(prefix)]

    return records


def list_procurement_notices(
    filters: dict[str, Any] | None = None,
    *,
    limit: int = PROCUREMENT_NOTICE_LIST_DEFAULT_LIMIT,
    offset: int = 0,
) -> list[dict[str, Any]]:
    return filter_procurement_notice_records(filters)[offset : offset + limit]


def get_procurement_notice_by_id(notice_id: str) -> dict[str, Any] | None:
    for record in load_procurement_notice_records():
        if record.get("id") == notice_id:
            return record
    return None


def search_procurement_notices(
    query: str,
    *,
    filters: dict[str, Any] | None = None,
    limit: int = PROCUREMENT_NOTICE_SEARCH_DEFAULT_LIMIT,
    offset: int = 0,
) -> tuple[list[dict[str, Any]], int]:
    normalized_query = _normalize_text(query).strip()
    records = filter_procurement_notice_records(filters)
    if normalized_query:
        records = [
            record
            for record in records
            if normalized_query in _normalize_text(record.get("id"))
            or normalized_query in _normalize_text(record.get("title"))
            or any(normalized_query in _normalize_text(name) for name in record.get("buyerNames", []))
            or normalized_query in _normalize_text((record.get("placeOfPerformance") or {}).get("city"))
        ]
    return records[offset : offset + limit], len(records)


def get_procurement_notice_stats() -> dict[str, Any]:
    records = load_procurement_notice_records()
    metadata = load_procurement_notice_data().get("metadata", {})
    notice_types: dict[str, int] = {}
    years: dict[str, int] = {}
    linked_region_count = 0
    linked_district_count = 0
    linked_municipality_count = 0
    deadline_count = 0

    for record in records:
        notice_type = record.get("noticeType")
        if isinstance(notice_type, str) and notice_type:
            notice_types[notice_type] = notice_types.get(notice_type, 0) + 1
        publication_date = record.get("publicationDate")
        if isinstance(publication_date, str) and len(publication_date) >= 4:
            year = publication_date[:4]
            years[year] = years.get(year, 0) + 1
        if record.get("regionCode"):
            linked_region_count += 1
        if record.get("districtCode"):
            linked_district_count += 1
        if record.get("municipalityCode"):
            linked_municipality_count += 1
        if record.get("tenderDeadline"):
            deadline_count += 1

    return {
        "recordCount": len(records),
        "coverage": "partial",
        "coverageDecision": "TED_PARTIAL",
        "acquisitionDecision": "PRODUCTION_IMPORT_APPROVED",
        "totalNoticesAtSource": metadata.get("totalNoticesAtSource"),
        "noticeTypes": dict(sorted(notice_types.items())),
        "publicationYears": dict(sorted(years.items())),
        "deadlineCount": deadline_count,
        "regionLinkedCount": linked_region_count,
        "districtLinkedCount": linked_district_count,
        "municipalityLinkedCount": linked_municipality_count,
    }
