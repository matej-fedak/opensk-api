#!/usr/bin/env python3
"""Validate static JSON datasets used by OpenSK API."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT_DIR / "data"
DEFAULT_BANKS_PATH = DEFAULT_DATA_DIR / "banks.json"
DEFAULT_HOLIDAYS_PATH = DEFAULT_DATA_DIR / "holidays.json"
DEFAULT_COMPANIES_PATH = DEFAULT_DATA_DIR / "companies.json"
DEFAULT_REGIONS_PATH = DEFAULT_DATA_DIR / "regions.json"
DEFAULT_DISTRICTS_PATH = DEFAULT_DATA_DIR / "districts.json"
DEFAULT_MUNICIPALITIES_PATH = DEFAULT_DATA_DIR / "municipalities.json"
DEFAULT_PSC_PATH = DEFAULT_DATA_DIR / "psc.json"
DEFAULT_SOURCES_PATH = DEFAULT_DATA_DIR / "sources.json"

_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}$")
_POSTAL_CODE_RE = re.compile(r"\d{5}$")
_BANK_CODE_RE = re.compile(r"\d{4}$")
_COMPANY_ICO_RE = re.compile(r"\d{8}$")
_REGION_CODE_RE = re.compile(r"SK\d{3}$")
_DISTRICT_CODE_RE = re.compile(r"SK\d{4}$")
_MUNICIPALITY_CODE_RE = re.compile(r"\d{6}$")
_PSC_CODE_RE = re.compile(r"\d{5}$")
_COMPANY_FORBIDDEN_KEYS = {
    "statutoryBodies",
    "representatives",
    "stakeholders",
    "partners",
    "owners",
    "persons",
    "birthDate",
    "personalNumber",
    "citizenship",
    "residence",
}


@dataclass(frozen=True)
class ValidationIssue:
    level: str
    path: str
    message: str


@dataclass
class ValidationReport:
    dataset: str
    path: Path
    record_count: int = 0
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        return len(self.warnings)

    @property
    def ok(self) -> bool:
        return self.error_count == 0

    def add_error(self, path: str, message: str) -> None:
        self.errors.append(ValidationIssue("error", path, message))

    def add_warning(self, path: str, message: str) -> None:
        self.warnings.append(ValidationIssue("warning", path, message))


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT_DIR))
    except ValueError:
        return str(path)


def _load_json(report: ValidationReport, path: Path) -> Any | None:
    if not path.is_file():
        report.add_error("file", f"File not found: {path}")
        return None

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        report.add_error("json", f"Invalid JSON: {exc.msg} (line {exc.lineno}, column {exc.colno})")
    except OSError as exc:
        report.add_error("file", f"Unable to read file: {exc}")

    return None


def _require_dict(report: ValidationReport, value: Any, path: str, message: str) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        report.add_error(path, message)
        return None
    return value


def _require_list(report: ValidationReport, value: Any, path: str, message: str) -> list[Any] | None:
    if not isinstance(value, list):
        report.add_error(path, message)
        return None
    return value


def _require_string(report: ValidationReport, value: Any, path: str, message: str) -> str | None:
    if not isinstance(value, str) or not value.strip():
        report.add_error(path, message)
        return None
    return value


def _require_ico(report: ValidationReport, value: Any, path: str, message: str) -> str | None:
    text = _require_string(report, value, path, message)
    if text is None:
        return None

    normalized = "".join(text.split())
    if not _COMPANY_ICO_RE.fullmatch(normalized):
        report.add_error(path, f"Expected 8-digit ICO, got {value!r}")
        return None

    return normalized


def _require_nullable_string(report: ValidationReport, value: Any, path: str, message: str) -> str | None:
    if value is None:
        return None
    return _require_string(report, value, path, message)


def _require_iso_date(report: ValidationReport, value: Any, path: str, message: str) -> str | None:
    text = _require_string(report, value, path, message)
    if text is None:
        return None

    if not _DATE_RE.fullmatch(text):
        report.add_error(path, f"Expected YYYY-MM-DD date, got {text!r}")
        return None

    try:
        date.fromisoformat(text)
    except ValueError:
        report.add_error(path, f"Invalid ISO date: {text!r}")
        return None

    return text


def _require_nullable_iso_date(report: ValidationReport, value: Any, path: str, message: str) -> str | None:
    if value is None:
        return None

    if not isinstance(value, str) or not value.strip():
        report.add_error(path, message)
        return None

    if not _DATE_RE.fullmatch(value):
        report.add_error(path, f"Expected YYYY-MM-DD date or null, got {value!r}")
        return None

    try:
        date.fromisoformat(value)
    except ValueError:
        report.add_error(path, f"Invalid ISO date: {value!r}")
        return None

    return value


def _record_forbidden_key_errors(report: ValidationReport, value: Any, path: str) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            item_path = f"{path}.{key}" if path else key
            if key in _COMPANY_FORBIDDEN_KEYS:
                report.add_error(item_path, f"company dataset must not include forbidden field {key!r}")
            _record_forbidden_key_errors(report, item, item_path)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _record_forbidden_key_errors(report, item, f"{path}[{index}]")


def _validate_companies_record(report: ValidationReport, item: dict[str, Any], item_path: str, seen_icos: set[str]) -> None:
    _record_forbidden_key_errors(report, item, item_path)

    ico = _require_ico(report, item.get("ico"), f"{item_path}.ico", "company ico must be an 8-digit string")
    if ico is not None:
        if ico in seen_icos:
            report.add_error(f"{item_path}.ico", f"duplicate IČO {ico!r}")
        seen_icos.add(ico)

    _require_string(report, item.get("name"), f"{item_path}.name", "company name must be a non-empty string")

    for field_name in ("establishedOn", "terminatedOn", "updatedAt"):
        if field_name not in item:
            report.add_error(f"{item_path}.{field_name}", f"company {field_name} must be null or a YYYY-MM-DD date")
            continue
        _require_nullable_iso_date(
            report,
            item.get(field_name),
            f"{item_path}.{field_name}",
            f"company {field_name} must be null or a YYYY-MM-DD date",
        )

    address = _require_dict(report, item.get("address"), f"{item_path}.address", "company address must be an object")
    if address is not None:
        if "postalCode" not in address:
            report.add_error(f"{item_path}.address.postalCode", "company address.postalCode must be null or a 5-digit string")
        else:
            postal_code = address.get("postalCode")
            if postal_code is not None:
                if not isinstance(postal_code, str) or not _POSTAL_CODE_RE.fullmatch(postal_code):
                    report.add_error(f"{item_path}.address.postalCode", f"company address.postalCode must be null or a 5-digit string, got {postal_code!r}")

    source = _require_dict(report, item.get("source"), f"{item_path}.source", "company source must be an object")
    if source is not None:
        _require_string(report, source.get("name"), f"{item_path}.source.name", "company source.name must be a non-empty string")

    established_on = item.get("establishedOn")
    terminated_on = item.get("terminatedOn")
    if isinstance(established_on, str) and isinstance(terminated_on, str) and _DATE_RE.fullmatch(established_on) and _DATE_RE.fullmatch(terminated_on):
        if date.fromisoformat(terminated_on) < date.fromisoformat(established_on):
            report.add_error(f"{item_path}.terminatedOn", "company terminatedOn must be on or after establishedOn")


def validate_companies_payload(payload: Any, path: Path = DEFAULT_COMPANIES_PATH) -> ValidationReport:
    report = ValidationReport("companies", path)
    if isinstance(payload, list):
        companies = _require_list(report, payload, "companies", "companies must be an array")
    elif isinstance(payload, dict):
        companies = _require_list(report, payload.get("companies"), "companies", "companies must be an array")
    else:
        report.add_error("root", "companies dataset must be an object or array")
        return report

    if companies is None:
        return report

    if not companies:
        report.add_error("companies", "companies array must not be empty")

    seen_icos: set[str] = set()
    for index, company in enumerate(companies):
        item_path = f"companies[{index}]"
        item = _require_dict(report, company, item_path, f"{item_path} must be an object")
        if item is None:
            continue
        _validate_companies_record(report, item, item_path, seen_icos)

    data_dir = path.resolve().parent
    registry = _load_registry_payload(report, data_dir / "sources.json")
    _warn_from_source_registry(report, "companies", registry.get("companies") if isinstance(registry, dict) else None)

    report.record_count = len(companies)
    return report


def validate_companies_dataset(path: Path = DEFAULT_COMPANIES_PATH) -> ValidationReport:
    report = ValidationReport("companies", path)
    payload = _load_json(report, path)
    if payload is None:
        return report
    return validate_companies_payload(payload, path)


def _validate_dataset_metadata(report: ValidationReport, payload: dict[str, Any]) -> dict[str, Any] | None:
    metadata = _require_dict(report, payload.get("metadata"), "metadata", "metadata must be an object")
    if metadata is None:
        return None

    _require_string(report, metadata.get("source"), "metadata.source", "metadata.source must be a non-empty string")
    _require_iso_date(
        report,
        metadata.get("lastUpdated"),
        "metadata.lastUpdated",
        "metadata.lastUpdated must be a non-empty ISO date",
    )
    return metadata


def _warn_if_seed(report: ValidationReport, metadata: dict[str, Any] | None) -> None:
    if not isinstance(metadata, dict):
        return

    source = metadata.get("source")
    complete = metadata.get("complete")
    if isinstance(source, str):
        lowered = source.lower()
        if "not exhaustive" in lowered or "incomplete" in lowered or ("seed" in lowered and complete is not True):
            report.add_warning("metadata.source", "Dataset is marked as seed/incomplete data")


def _load_registry_payload(report: ValidationReport, path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None

    payload = _load_json(report, path)
    if not isinstance(payload, dict):
        return None
    return payload


def _warn_from_source_registry(report: ValidationReport, dataset_name: str, entry: Any) -> None:
    if not isinstance(entry, dict):
        return

    coverage = entry.get("coverage")
    licence = entry.get("licence")
    redistribution_status = entry.get("redistributionStatus")
    notes = entry.get("notes")
    source_name = entry.get("sourceName")

    joined = " ".join(
        str(value).lower()
        for value in (coverage, licence, redistribution_status, notes, source_name)
        if isinstance(value, str)
    )

    if any(token in joined for token in ("pending", "partial", "seed", "incomplete", "unknown", "unclear", "not exhaustive")):
        report.add_warning(
            "sourceRegistry",
            f"{dataset_name} source/licence verification is pending or coverage is partial",
        )


def validate_sources_registry(path: Path = DEFAULT_SOURCES_PATH) -> ValidationReport:
    report = ValidationReport("sources", path)
    if not path.is_file():
        report.add_error("file", f"File not found: {path}")
        return report

    payload = _load_registry_payload(report, path)
    if payload is None:
        return report

    required_datasets = {"regions", "districts", "municipalities", "psc", "banks", "holidays", "companies"}
    allowed_coverages = {"complete", "partial", "seed-backed", "unknown"}
    missing = sorted(required_datasets - set(payload))
    if missing:
        report.add_error("root", f"source registry is missing dataset entries: {', '.join(missing)}")

    for dataset_name in sorted(required_datasets):
        entry = payload.get(dataset_name)
        if not isinstance(entry, dict):
            report.add_error(dataset_name, f"{dataset_name} registry entry must be an object")
            continue

        _require_string(report, entry.get("status"), f"{dataset_name}.status", f"{dataset_name} status must be a non-empty string")
        coverage = _require_string(report, entry.get("coverage"), f"{dataset_name}.coverage", f"{dataset_name} coverage must be a non-empty string")
        if coverage is not None and coverage not in allowed_coverages:
            report.add_error(
                f"{dataset_name}.coverage",
                f"{dataset_name} coverage must be one of {sorted(allowed_coverages)}, got {coverage!r}",
            )
        _require_string(report, entry.get("sourceName"), f"{dataset_name}.sourceName", f"{dataset_name} sourceName must be a non-empty string")
        _require_string(report, entry.get("sourceUrl"), f"{dataset_name}.sourceUrl", f"{dataset_name} sourceUrl must be a non-empty string")
        _require_string(report, entry.get("licence"), f"{dataset_name}.licence", f"{dataset_name} licence must be a non-empty string")
        _require_string(
            report,
            entry.get("redistributionStatus"),
            f"{dataset_name}.redistributionStatus",
            f"{dataset_name} redistributionStatus must be a non-empty string",
        )
        _require_iso_date(report, entry.get("lastChecked"), f"{dataset_name}.lastChecked", f"{dataset_name} lastChecked must be a non-empty ISO date")
        _require_string(
            report,
            entry.get("updateCadence"),
            f"{dataset_name}.updateCadence",
            f"{dataset_name} updateCadence must be a non-empty string",
        )
        _require_string(report, entry.get("notes"), f"{dataset_name}.notes", f"{dataset_name} notes must be a non-empty string")

    report.record_count = len(required_datasets)
    return report


def validate_banks_dataset(path: Path = DEFAULT_BANKS_PATH) -> ValidationReport:
    report = ValidationReport("banks", path)
    payload = _load_json(report, path)
    if not isinstance(payload, dict):
        return report

    metadata = _validate_dataset_metadata(report, payload)
    _warn_if_seed(report, metadata)

    banks = _require_list(report, payload.get("banks"), "banks", "banks must be an array")
    if banks is None:
        return report
    if not banks:
        report.add_error("banks", "banks array must not be empty")

    data_dir = path.resolve().parent
    registry = _load_registry_payload(report, data_dir / "sources.json")
    _warn_from_source_registry(report, "banks", registry.get("banks") if isinstance(registry, dict) else None)

    seen_codes: set[str] = set()
    for index, bank in enumerate(banks):
        item_path = f"banks[{index}]"
        item = _require_dict(report, bank, item_path, f"{item_path} must be an object")
        if item is None:
            continue

        code = _require_string(report, item.get("code"), f"{item_path}.code", "bank code must be a non-empty string")
        if code is not None:
            if not _BANK_CODE_RE.fullmatch(code):
                report.add_error(f"{item_path}.code", f"bank code must be 4 digits, got {code!r}")
            if code in seen_codes:
                report.add_error(f"{item_path}.code", f"duplicate bank code {code!r}")
            seen_codes.add(code)

        _require_string(report, item.get("name"), f"{item_path}.name", "bank name must be a non-empty string")
        _require_string(report, item.get("country"), f"{item_path}.country", "bank country must be a non-empty string")

        swift = item.get("swift")
        bic = item.get("bic")
        identifier = swift if swift is not None else bic
        if identifier is not None:
            field_name = "swift" if swift is not None else "bic"
            if not isinstance(identifier, str) or not re.fullmatch(r"[A-Z0-9]{8}([A-Z0-9]{3})?", identifier):
                report.add_error(f"{item_path}.{field_name}", f"bank swift/bic must be uppercase alphanumeric length 8 or 11, got {identifier!r}")

    report.record_count = len(banks)
    return report


def validate_holidays_dataset(path: Path = DEFAULT_HOLIDAYS_PATH) -> ValidationReport:
    report = ValidationReport("holidays", path)
    payload = _load_json(report, path)
    if not isinstance(payload, dict):
        return report

    data_dir = path.resolve().parent
    registry = _load_registry_payload(report, data_dir / "sources.json")
    _warn_from_source_registry(report, "holidays", registry.get("holidays") if isinstance(registry, dict) else None)

    if not payload:
        report.add_error("root", "holidays dataset must not be empty")
        return report

    for year_key, holidays in payload.items():
        if year_key == "metadata":
            continue
        if not re.fullmatch(r"\d{4}", str(year_key)):
            report.add_error(f"{year_key}", f"year key must be 4 digits, got {year_key!r}")
            continue

        year = int(year_key)
        entries = _require_list(report, holidays, str(year_key), f"holidays[{year_key}] must be an array")
        if entries is None:
            continue
        if not entries:
            report.add_error(str(year_key), f"holidays[{year_key}] must not be empty")
            continue

        seen_dates: set[str] = set()
        previous_date: date | None = None
        for index, holiday in enumerate(entries):
            item_path = f"{year_key}[{index}]"
            item = _require_dict(report, holiday, item_path, f"{item_path} must be an object")
            if item is None:
                continue

            date_text = _require_iso_date(report, item.get("date"), f"{item_path}.date", "holiday date must be a non-empty ISO date")
            if date_text is not None:
                holiday_date = date.fromisoformat(date_text)
                if holiday_date.year != year:
                    report.add_error(f"{item_path}.date", f"holiday date {date_text!r} does not match year {year_key}")
                if date_text in seen_dates:
                    report.add_error(f"{item_path}.date", f"duplicate holiday date {date_text!r}")
                seen_dates.add(date_text)
                if previous_date is not None and holiday_date < previous_date:
                    report.add_warning(item_path, "holiday dates are not sorted ascending")
                previous_date = holiday_date

            _require_string(report, item.get("name"), f"{item_path}.name", "holiday name must be a non-empty string")
            _require_string(report, item.get("name_en"), f"{item_path}.name_en", "holiday English name must be a non-empty string")

        report.record_count += len(entries)

    return report


def validate_regions_dataset(path: Path = DEFAULT_REGIONS_PATH) -> ValidationReport:
    report = ValidationReport("regions", path)
    payload = _load_json(report, path)
    if not isinstance(payload, dict):
        return report

    metadata = _validate_dataset_metadata(report, payload)
    complete = metadata.get("complete") if isinstance(metadata, dict) else None
    if complete is not True:
        report.add_error("metadata.complete", "regions dataset must be marked complete")

    regions = _require_list(report, payload.get("regions"), "regions", "regions must be an array")
    if regions is None:
        return report

    if len(regions) != 8:
        report.add_error("regions", f"regions dataset must contain exactly 8 records, found {len(regions)}")

    seen_codes: set[str] = set()
    for index, region in enumerate(regions):
        item_path = f"regions[{index}]"
        item = _require_dict(report, region, item_path, f"{item_path} must be an object")
        if item is None:
            continue

        code = _require_string(report, item.get("code"), f"{item_path}.code", "region code must be a non-empty string")
        if code is not None:
            if not _REGION_CODE_RE.fullmatch(code):
                report.add_error(f"{item_path}.code", f"region code must match SK###, got {code!r}")
            if code in seen_codes:
                report.add_error(f"{item_path}.code", f"duplicate region code {code!r}")
            seen_codes.add(code)

        _require_string(report, item.get("name"), f"{item_path}.name", "region name must be a non-empty string")
        _require_string(report, item.get("nameEn"), f"{item_path}.nameEn", "region English name must be a non-empty string")

        country = _require_string(report, item.get("country"), f"{item_path}.country", "region country must be a non-empty string")
        if country is not None and country != "SK":
            report.add_error(f"{item_path}.country", f"region country must be 'SK', got {country!r}")

    report.record_count = len(regions)
    return report


def _load_index(
    report: ValidationReport,
    path: Path,
    collection_key: str,
    item_key: str,
) -> dict[str, dict[str, Any]]:
    payload = _load_json(report, path)
    if not isinstance(payload, dict):
        return {}

    items = payload.get(collection_key)
    if not isinstance(items, list):
        return {}

    index: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        key = item.get(item_key)
        if isinstance(key, str):
            index[key] = item
    return index


def _load_regions_lookup(data_dir: Path, report: ValidationReport) -> dict[str, dict[str, Any]]:
    return _load_index(report, data_dir / "regions.json", "regions", "code")


def _load_districts_lookup(data_dir: Path, report: ValidationReport) -> dict[str, dict[str, Any]]:
    return _load_index(report, data_dir / "districts.json", "districts", "code")


def validate_districts_dataset(path: Path = DEFAULT_DISTRICTS_PATH) -> ValidationReport:
    report = ValidationReport("districts", path)
    payload = _load_json(report, path)
    if not isinstance(payload, dict):
        return report

    metadata = _validate_dataset_metadata(report, payload)
    _warn_if_seed(report, metadata)

    data_dir = path.resolve().parent
    registry = _load_registry_payload(report, data_dir / "sources.json")
    _warn_from_source_registry(report, "districts", registry.get("districts") if isinstance(registry, dict) else None)

    complete = metadata.get("complete") if isinstance(metadata, dict) else None
    if complete is not False:
        report.add_warning("metadata.complete", "districts dataset is expected to be seed/incomplete data")

    districts = _require_list(report, payload.get("districts"), "districts", "districts must be an array")
    if districts is None:
        return report
    if not districts:
        report.add_error("districts", "districts array must not be empty")

    data_dir = path.resolve().parent
    regions_by_code = _load_regions_lookup(data_dir, report)

    seen_codes: set[str] = set()
    for index, district in enumerate(districts):
        item_path = f"districts[{index}]"
        item = _require_dict(report, district, item_path, f"{item_path} must be an object")
        if item is None:
            continue

        code = _require_string(report, item.get("code"), f"{item_path}.code", "district code must be a non-empty string")
        if code is not None:
            if not _DISTRICT_CODE_RE.fullmatch(code):
                report.add_error(f"{item_path}.code", f"district code must match SK####, got {code!r}")
            if code in seen_codes:
                report.add_error(f"{item_path}.code", f"duplicate district code {code!r}")
            seen_codes.add(code)

        _require_string(report, item.get("name"), f"{item_path}.name", "district name must be a non-empty string")

        region_code = _require_string(report, item.get("regionCode"), f"{item_path}.regionCode", "district regionCode must be a non-empty string")
        if region_code is not None:
            if not _REGION_CODE_RE.fullmatch(region_code):
                report.add_error(f"{item_path}.regionCode", f"district regionCode must match SK###, got {region_code!r}")
            elif region_code not in regions_by_code:
                report.add_error(f"{item_path}.regionCode", f"unknown region code {region_code!r}")

            if code is not None and code[:5] != region_code:
                report.add_error(f"{item_path}.code", f"district code {code!r} does not match region code {region_code!r}")

        country = _require_string(report, item.get("country"), f"{item_path}.country", "district country must be a non-empty string")
        if country is not None and country != "SK":
            report.add_error(f"{item_path}.country", f"district country must be 'SK', got {country!r}")

    report.record_count = len(districts)
    return report


def validate_municipalities_dataset(path: Path = DEFAULT_MUNICIPALITIES_PATH) -> ValidationReport:
    report = ValidationReport("municipalities", path)
    payload = _load_json(report, path)
    if not isinstance(payload, dict):
        return report

    metadata = _validate_dataset_metadata(report, payload)
    _warn_if_seed(report, metadata)

    data_dir = path.resolve().parent
    registry = _load_registry_payload(report, data_dir / "sources.json")
    _warn_from_source_registry(report, "municipalities", registry.get("municipalities") if isinstance(registry, dict) else None)

    complete = metadata.get("complete") if isinstance(metadata, dict) else None
    if complete is not False:
        report.add_warning("metadata.complete", "municipalities dataset is expected to be seed/incomplete data")

    municipalities = _require_list(report, payload.get("municipalities"), "municipalities", "municipalities must be an array")
    if municipalities is None:
        return report
    if not municipalities:
        report.add_error("municipalities", "municipalities array must not be empty")

    data_dir = path.resolve().parent
    regions_by_code = _load_regions_lookup(data_dir, report)
    districts_by_code = _load_districts_lookup(data_dir, report)

    seen_codes: set[str] = set()
    for index, municipality in enumerate(municipalities):
        item_path = f"municipalities[{index}]"
        item = _require_dict(report, municipality, item_path, f"{item_path} must be an object")
        if item is None:
            continue

        code = _require_string(report, item.get("code"), f"{item_path}.code", "municipality code must be a non-empty string")
        if code is not None:
            if not _MUNICIPALITY_CODE_RE.fullmatch(code):
                report.add_error(f"{item_path}.code", f"municipality code must be 6 digits, got {code!r}")
            if code in seen_codes:
                report.add_error(f"{item_path}.code", f"duplicate municipality code {code!r}")
            seen_codes.add(code)

        _require_string(report, item.get("name"), f"{item_path}.name", "municipality name must be a non-empty string")

        region_code = _require_string(report, item.get("regionCode"), f"{item_path}.regionCode", "municipality regionCode must be a non-empty string")
        if region_code is not None:
            if not _REGION_CODE_RE.fullmatch(region_code):
                report.add_error(f"{item_path}.regionCode", f"municipality regionCode must match SK###, got {region_code!r}")
            elif region_code not in regions_by_code:
                report.add_error(f"{item_path}.regionCode", f"unknown region code {region_code!r}")

        district_code = item.get("districtCode")
        if district_code is not None:
            district_code = _require_string(
                report,
                district_code,
                f"{item_path}.districtCode",
                "municipality districtCode must be a non-empty string",
            )
            if district_code is not None:
                if not _DISTRICT_CODE_RE.fullmatch(district_code):
                    report.add_error(f"{item_path}.districtCode", f"municipality districtCode must match SK####, got {district_code!r}")
                elif district_code not in districts_by_code:
                    report.add_error(f"{item_path}.districtCode", f"unknown district code {district_code!r}")
                elif region_code is not None and districts_by_code[district_code].get("regionCode") != region_code:
                    report.add_error(f"{item_path}.districtCode", f"district code {district_code!r} does not belong to region {region_code!r}")

        country = _require_string(report, item.get("country"), f"{item_path}.country", "municipality country must be a non-empty string")
        if country is not None and country != "SK":
            report.add_error(f"{item_path}.country", f"municipality country must be 'SK', got {country!r}")

    report.record_count = len(municipalities)
    return report


def validate_psc_dataset(path: Path = DEFAULT_PSC_PATH) -> ValidationReport:
    report = ValidationReport("psc", path)
    payload = _load_json(report, path)
    if not isinstance(payload, dict):
        return report

    data_dir = path.resolve().parent
    registry = _load_registry_payload(report, data_dir / "sources.json")
    _warn_from_source_registry(report, "psc", registry.get("psc") if isinstance(registry, dict) else None)
    regions_by_code = _load_regions_lookup(data_dir, report)
    districts_by_code = _load_districts_lookup(data_dir, report)
    municipalities_by_code = _load_index(report, data_dir / "municipalities.json", "municipalities", "code")

    if isinstance(payload.get("metadata"), dict):
        metadata = payload["metadata"]
        _validate_dataset_metadata(report, payload)
        _warn_if_seed(report, metadata)

    entries = [(str(psc_code), record) for psc_code, record in payload.items() if psc_code != "metadata"]
    if not entries:
        report.add_error("root", "psc dataset must not be empty")
        return report

    for item_path, record in entries:
        item = _require_dict(report, record, item_path, f"PSC record at {item_path} must be an object")
        if item is None:
            continue

        record_psc = _require_string(report, item.get("psc"), f"{item_path}.psc", "PSC record must include its postal code")
        if record_psc is not None:
            if not _PSC_CODE_RE.fullmatch(record_psc):
                report.add_error(f"{item_path}.psc", f"PSC must be 5 digits, got {record_psc!r}")
            if record_psc != item_path:
                report.add_error(f"{item_path}.psc", f"PSC field {record_psc!r} does not match key {item_path!r}")

        _require_nullable_string(report, item.get("city"), f"{item_path}.city", "PSC city must be a string when provided")
        _require_nullable_string(report, item.get("municipality"), f"{item_path}.municipality", "PSC municipality must be a string when provided")
        _require_nullable_string(report, item.get("district"), f"{item_path}.district", "PSC district must be a string when provided")
        _require_nullable_string(report, item.get("region"), f"{item_path}.region", "PSC region must be a string when provided")

        country = _require_string(report, item.get("country"), f"{item_path}.country", "PSC country must be a non-empty string")
        if country is not None and country != "Slovakia":
            report.add_error(f"{item_path}.country", f"PSC country must be 'Slovakia', got {country!r}")

        valid_from = _require_nullable_iso_date(report, item.get("validFrom"), f"{item_path}.validFrom", "PSC validFrom must be null or a YYYY-MM-DD date")
        valid_to = _require_nullable_iso_date(report, item.get("validTo"), f"{item_path}.validTo", "PSC validTo must be null or a YYYY-MM-DD date")
        if valid_from is not None and valid_to is not None and date.fromisoformat(valid_from) > date.fromisoformat(valid_to):
            report.add_error(f"{item_path}.validFrom", "PSC validFrom must be on or before validTo")

        region_code = item.get("regionCode")
        if region_code is not None:
            if not isinstance(region_code, str) or not _REGION_CODE_RE.fullmatch(region_code):
                report.add_error(f"{item_path}.regionCode", f"PSC regionCode must match SK###, got {region_code!r}")
            elif region_code not in regions_by_code:
                report.add_error(f"{item_path}.regionCode", f"unknown region code {region_code!r}")

        district_code = item.get("districtCode")
        if district_code is not None:
            if not isinstance(district_code, str) or not _DISTRICT_CODE_RE.fullmatch(district_code):
                report.add_error(f"{item_path}.districtCode", f"PSC districtCode must match SK####, got {district_code!r}")
            elif district_code not in districts_by_code:
                report.add_error(f"{item_path}.districtCode", f"unknown district code {district_code!r}")
            elif region_code is not None and districts_by_code[district_code].get("regionCode") != region_code:
                report.add_error(f"{item_path}.districtCode", f"district code {district_code!r} does not belong to region {region_code!r}")

        municipality_code = item.get("municipalityCode")
        if municipality_code is not None:
            if not isinstance(municipality_code, str) or not _MUNICIPALITY_CODE_RE.fullmatch(municipality_code):
                report.add_error(f"{item_path}.municipalityCode", f"PSC municipalityCode must be 6 digits, got {municipality_code!r}")
            elif municipality_code not in municipalities_by_code:
                report.add_error(f"{item_path}.municipalityCode", f"unknown municipality code {municipality_code!r}")

        matches = item.get("matches")
        if matches is None:
            continue

        matches_list = _require_list(report, matches, f"{item_path}.matches", "PSC matches must be a list")
        if matches_list is None:
            continue

        match_count = item.get("matchCount")
        if match_count is not None and (not isinstance(match_count, int) or match_count < 0):
            report.add_error(f"{item_path}.matchCount", "PSC matchCount must be a non-negative integer")
        elif isinstance(match_count, int) and match_count != len(matches_list):
            report.add_error(f"{item_path}.matchCount", f"PSC matchCount must equal len(matches), got {match_count} and {len(matches_list)}")

        seen_matches: set[str] = set()
        for index, match in enumerate(matches_list):
            match_path = f"{item_path}.matches[{index}]"
            match_item = _require_dict(report, match, match_path, "PSC match must be an object")
            if match_item is None:
                continue

            delivery_post = _require_string(report, match_item.get("deliveryPost"), f"{match_path}.deliveryPost", "PSC deliveryPost must be a non-empty string")
            valid_from_match = _require_nullable_iso_date(
                report,
                match_item.get("validFrom"),
                f"{match_path}.validFrom",
                "PSC validFrom must be null or a YYYY-MM-DD date",
            )
            valid_to_match = _require_nullable_iso_date(
                report,
                match_item.get("validTo"),
                f"{match_path}.validTo",
                "PSC validTo must be null or a YYYY-MM-DD date",
            )
            if valid_from_match is not None and valid_to_match is not None and date.fromisoformat(valid_from_match) > date.fromisoformat(valid_to_match):
                report.add_error(f"{match_path}.validFrom", "PSC validFrom must be on or before validTo")

            municipality_code_match = match_item.get("municipalityCode")
            if municipality_code_match is not None and (
                not isinstance(municipality_code_match, str) or not _MUNICIPALITY_CODE_RE.fullmatch(municipality_code_match)
            ):
                report.add_error(f"{match_path}.municipalityCode", f"PSC municipalityCode must be 6 digits, got {municipality_code_match!r}")

            exact_key = json.dumps(match_item, ensure_ascii=False, sort_keys=True)
            if exact_key in seen_matches:
                report.add_error(match_path, "duplicate PSC record")
            seen_matches.add(exact_key)

        matches = item.get("matches")
        if matches is None:
            continue

        matches_list = _require_list(report, matches, f"{item_path}.matches", "PSC matches must be a list")
        if matches_list is None:
            continue

        match_count = item.get("matchCount")
        if match_count is not None and (not isinstance(match_count, int) or match_count < 0):
            report.add_error(f"{item_path}.matchCount", "PSC matchCount must be a non-negative integer")
        elif isinstance(match_count, int) and match_count != len(matches_list):
            report.add_error(f"{item_path}.matchCount", f"PSC matchCount must equal len(matches), got {match_count} and {len(matches_list)}")

            seen_matches: set[str] = set()
            for index, match in enumerate(matches_list):
                match_path = f"{item_path}.matches[{index}]"
                match_item = _require_dict(report, match, match_path, "PSC match must be an object")
                if match_item is None:
                    continue

            delivery_post = _require_string(report, match_item.get("deliveryPost"), f"{match_path}.deliveryPost", "PSC deliveryPost must be a non-empty string")
            valid_from_match = _require_nullable_iso_date(
                report,
                match_item.get("validFrom"),
                f"{match_path}.validFrom",
                "PSC validFrom must be null or a YYYY-MM-DD date",
            )
            valid_to_match = _require_nullable_iso_date(
                report,
                match_item.get("validTo"),
                f"{match_path}.validTo",
                "PSC validTo must be null or a YYYY-MM-DD date",
            )
            if valid_from_match is not None and valid_to_match is not None and date.fromisoformat(valid_from_match) > date.fromisoformat(valid_to_match):
                report.add_error(f"{match_path}.validFrom", "PSC validFrom must be on or before validTo")

            municipality_code_match = match_item.get("municipalityCode")
            if municipality_code_match is not None and (
                not isinstance(municipality_code_match, str) or not _MUNICIPALITY_CODE_RE.fullmatch(municipality_code_match)
            ):
                report.add_error(f"{match_path}.municipalityCode", f"PSC municipalityCode must be 6 digits, got {municipality_code_match!r}")

            exact_key = json.dumps(match_item, ensure_ascii=False, sort_keys=True)
            if exact_key in seen_matches:
                report.add_error(match_path, "duplicate PSC record")
            seen_matches.add(exact_key)

    report.record_count = len(entries)
    return report


def validate_all_datasets(data_dir: Path = DEFAULT_DATA_DIR) -> list[ValidationReport]:
    reports = [
        validate_sources_registry(data_dir / "sources.json"),
        validate_banks_dataset(data_dir / "banks.json"),
        validate_holidays_dataset(data_dir / "holidays.json"),
        validate_regions_dataset(data_dir / "regions.json"),
        validate_districts_dataset(data_dir / "districts.json"),
        validate_municipalities_dataset(data_dir / "municipalities.json"),
        validate_psc_dataset(data_dir / "psc.json"),
    ]

    companies_path = data_dir / "companies.json"
    if companies_path.is_file():
        reports.append(validate_companies_dataset(companies_path))

    return reports


def _print_issue(issue: ValidationIssue, path: Path) -> None:
    print(f"{issue.level.upper():7} {_display_path(path)} {issue.path}: {issue.message}", file=sys.stderr)


def _print_report(report: ValidationReport) -> None:
    status = "OK" if report.ok else "FAIL"
    print(
        f"{report.dataset:14} {status:4} records={report.record_count:3} errors={report.error_count:2} warnings={report.warning_count:2} path={_display_path(report.path)}"
    )
    for issue in report.errors:
        _print_issue(issue, report.path)
    for issue in report.warnings:
        _print_issue(issue, report.path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate OpenSK static JSON datasets.")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR, help="Directory containing the dataset JSON files")
    args = parser.parse_args(argv)

    data_dir = args.data_dir.resolve()
    reports = validate_all_datasets(data_dir)

    print(f"Validated datasets in {_display_path(data_dir)}")
    print(f"{'dataset':14} {'stat':4} {'records':8} {'errors':6} {'warnings':8} path")

    total_records = 0
    total_errors = 0
    total_warnings = 0
    for report in reports:
        _print_report(report)
        total_records += report.record_count
        total_errors += report.error_count
        total_warnings += report.warning_count

    print(
        f"Summary: datasets={len(reports)} records={total_records} errors={total_errors} warnings={total_warnings}"
    )

    return 1 if total_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
