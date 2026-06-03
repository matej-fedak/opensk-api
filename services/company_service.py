from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "companies.json"


class CompanyInvalidFormatError(ValueError):
    pass


class CompanyDatasetError(ValueError):
    pass


class CompanyNotFoundError(KeyError):
    pass


# Backward-compatible aliases for the earlier module shape.
CompanyInvalidIcoError = CompanyInvalidFormatError
CompanyDatasetUnavailableError = CompanyDatasetError


def _resolve_data_file(data_file: Path | str | None = None) -> Path:
    return DATA_FILE if data_file is None else Path(data_file)


def normalize_ico(ico: str) -> str:
    if not isinstance(ico, str):
        raise CompanyInvalidFormatError(ico)
    return re.sub(r"\s+", "", ico)


def validate_ico(ico: str) -> bool:
    try:
        normalized = normalize_ico(ico)
    except CompanyInvalidFormatError:
        return False
    return bool(re.fullmatch(r"\d{8}", normalized))


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _text_or_none(value: Any) -> str | None:
    if value is None:
        return None

    text = " ".join(str(value).split())
    return text or None


def _normalize_address(address: Any) -> dict[str, Any]:
    raw_address = address if isinstance(address, dict) else {}
    return {
        "street": _text_or_none(raw_address.get("street")),
        "registrationNumber": _text_or_none(raw_address.get("registrationNumber")),
        "buildingNumber": _text_or_none(raw_address.get("buildingNumber")),
        "municipality": _text_or_none(raw_address.get("municipality")),
        "postalCode": _text_or_none(raw_address.get("postalCode")),
        "country": _text_or_none(raw_address.get("country")),
        "municipalityCode": _text_or_none(raw_address.get("municipalityCode")),
        "regionCode": _text_or_none(raw_address.get("regionCode")),
        "districtCode": _text_or_none(raw_address.get("districtCode")),
    }


def _normalize_source(source: Any) -> dict[str, Any]:
    raw_source = source if isinstance(source, dict) else {}
    return {
        "name": _text_or_none(raw_source.get("name")),
        "recordId": _text_or_none(raw_source.get("recordId")),
    }


def _normalize_company_record(record: dict[str, Any], *, index: int) -> dict[str, Any]:
    raw_ico = record.get("ico")
    if raw_ico is None:
        raw_ico = record.get("IČO")

    if not isinstance(raw_ico, str):
        raise CompanyDatasetError(f"companies[{index}].ico must be a string")

    normalized_ico = normalize_ico(raw_ico)
    if not validate_ico(raw_ico):
        raise CompanyDatasetError(f"companies[{index}].ico must be an 8-digit string")

    return {
        "ico": normalized_ico,
        "name": _text_or_none(record.get("name")),
        "legalForm": _text_or_none(record.get("legalForm")),
        "legalStatus": _text_or_none(record.get("legalStatus")),
        "sourceRegister": _text_or_none(record.get("sourceRegister")),
        "address": _normalize_address(record.get("address")),
        "establishedOn": _text_or_none(record.get("establishedOn")),
        "terminatedOn": _text_or_none(record.get("terminatedOn")),
        "updatedAt": _text_or_none(record.get("updatedAt")),
        "source": _normalize_source(record.get("source")),
    }


def _extract_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        raw_records = payload
    elif isinstance(payload, dict):
        raw_records = None
        for key in ("companies", "records", "data", "items"):
            value = payload.get(key)
            if isinstance(value, list):
                raw_records = value
                break
        if raw_records is None:
            raise CompanyDatasetError("company dataset must contain a companies array")
    else:
        raise CompanyDatasetError("company dataset must be a list or object")

    records: list[dict[str, Any]] = []
    for index, record in enumerate(raw_records):
        if not isinstance(record, dict):
            raise CompanyDatasetError(f"companies[{index}] must be an object")
        records.append(dict(record))
    return records


def _load_company_records(data_file: Path | str | None = None, *, missing_ok: bool) -> list[dict[str, Any]]:
    path = _resolve_data_file(data_file)
    if not path.is_file():
        if missing_ok:
            return []
        raise CompanyDatasetUnavailableError(f"Company dataset not found at {path}")

    try:
        payload = _load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        if missing_ok:
            raise CompanyDatasetError("company dataset could not be loaded") from exc
        raise CompanyDatasetUnavailableError("Company dataset is not available") from exc

    records = _extract_records(payload)

    companies: list[dict[str, Any]] = []
    seen: dict[str, int] = {}
    for index, record in enumerate(records):
        try:
            normalized = _normalize_company_record(record, index=index)
        except CompanyInvalidFormatError as exc:
            if missing_ok:
                raise CompanyDatasetError(str(exc)) from exc
            raise CompanyDatasetUnavailableError("Company dataset is not available") from exc

        ico = normalized["ico"]
        if ico in seen:
            previous_index = seen[ico]
            message = f"duplicate company ico {ico!r} at companies[{previous_index}] and companies[{index}]"
            if missing_ok:
                raise CompanyDatasetError(message)
            raise CompanyDatasetUnavailableError(message)
        seen[ico] = index
        companies.append(normalized)

    return companies


def load_companies(data_file: Path | str | None = None) -> list[dict[str, Any]]:
    return _load_company_records(data_file, missing_ok=True)


def get_company_by_ico(ico: str, data_file: Path | str | None = None) -> dict[str, Any]:
    normalized = normalize_ico(ico)
    if not validate_ico(ico):
        raise CompanyInvalidFormatError(ico)

    for company in load_companies(data_file=data_file):
        if company.get("ico") == normalized:
            return company

    raise CompanyNotFoundError(normalized)


@lru_cache(maxsize=None)
def load_company_dataset(data_file: Path | str | None = None) -> dict[str, Any]:
    path = _resolve_data_file(data_file)
    companies = _load_company_records(path, missing_ok=False)
    payload = _load_json(path)
    metadata = payload.get("metadata") if isinstance(payload, dict) else {}
    if not isinstance(metadata, dict):
        metadata = {}
    return {"metadata": dict(metadata), "companies": companies}


@lru_cache(maxsize=None)
def load_company_index(data_file: Path | str | None = None) -> dict[str, dict[str, Any]]:
    return {company["ico"]: company for company in load_company_dataset(data_file=data_file)["companies"]}


def load_company_metadata(data_file: Path | str | None = None) -> dict[str, Any]:
    return dict(load_company_dataset(data_file=data_file)["metadata"])


def lookup_company(ico: str, data_file: Path | str | None = None) -> dict[str, Any]:
    normalized = normalize_ico(ico)
    if not validate_ico(ico):
        raise CompanyInvalidFormatError(ico)

    try:
        return load_company_index(data_file=data_file)[normalized]
    except KeyError as exc:
        raise CompanyNotFoundError(normalized) from exc
