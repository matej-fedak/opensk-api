#!/usr/bin/env python3
"""Offline importer for TED Slovak public procurement notice snapshots."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

DEFAULT_DATA_DIR = ROOT / "data"
DEFAULT_INPUT = DEFAULT_DATA_DIR / "raw" / "procurement-notices-ted-search.json"
DEFAULT_OUTPUT = DEFAULT_DATA_DIR / "generated" / "procurement_notices.json"
DEFAULT_SOURCE = "TED Search API Slovak-buyer procurement notice snapshot"
SOURCE_LICENSE = "TED / Publications Office reuse terms; preserve attribution. See https://ted.europa.eu/en/legal-notice."
SOURCE_TERMS_URL = "https://ted.europa.eu/en/legal-notice"
SOURCE_API_URL = "https://api.ted.europa.eu/v3/notices/search"
ACQUISITION_DECISION = "PRODUCTION_IMPORT_APPROVED"
COVERAGE_DECISION = "TED_PARTIAL"

_PUBLICATION_NUMBER_RE = re.compile(r"^[0-9]{6}-[0-9]{4}$")

_PROCUREMENT_FORBIDDEN_KEYS = {
    "contact",
    "contactPoint",
    "contactPerson",
    "contactName",
    "email",
    "phone",
    "telephone",
    "fax",
    "street",
    "address",
    "addressLine1",
    "addressLine2",
    "winner",
    "winnerName",
    "tenderer",
    "tendererName",
    "subcontractor",
    "subcontractorName",
    "person",
    "personName",
    "beneficialOwner",
    "ubo",
    "organisationEmail",
    "organisationTel",
    "organisationFax",
    "buyerEmail",
    "buyerPhone",
}

from scripts.import_utils import backup_existing_file, normalize_whitespace, write_json
from scripts.validate_datasets import ValidationReport, validate_procurement_notices_dataset


@dataclass
class ImportResult:
    input_path: Path
    output_path: Path
    dry_run: bool
    total_source_rows: int = 0
    imported_records: int = 0
    skipped_records: int = 0
    malformed_records: int = 0
    duplicate_records: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    validation_report: ValidationReport | None = None
    wrote_files: list[Path] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors and (self.validation_report is None or self.validation_report.ok)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("TED search snapshot must be a JSON object")
    return payload


def _load_source_records(path: Path) -> tuple[list[dict[str, Any]], int]:
    payload = _load_json(path)
    notices = payload.get("notices")
    if not isinstance(notices, list):
        raise ValueError("TED search snapshot must contain a notices array")
    records = [dict(item) for item in notices if isinstance(item, dict)]
    total = payload.get("totalNoticeCount", len(records))
    return records, total if isinstance(total, int) else len(records)


def _localized_values(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return []
    preferred_langs = ("slk", "eng")
    values: list[str] = []
    for language in preferred_langs:
        item = value.get(language)
        if isinstance(item, list):
            values.extend(normalize_whitespace(item_value) for item_value in item if normalize_whitespace(item_value))
        else:
            text = normalize_whitespace(item)
            if text:
                values.append(text)
    for key in sorted(value):
        if key in preferred_langs:
            continue
        item = value[key]
        if isinstance(item, list):
            values.extend(normalize_whitespace(item_value) for item_value in item if normalize_whitespace(item_value))
        else:
            text = normalize_whitespace(item)
            if text:
                values.append(text)
    return values


def _first_localized_value(value: Any, *, field_name: str) -> str:
    values = _localized_values(value)
    if not values:
        raise ValueError(f"missing {field_name}")
    return values[0]


def _localized_list(value: Any) -> list[str]:
    return _localized_values(value)


def _first_string(value: Any) -> str | None:
    if isinstance(value, list):
        for item in value:
            text = normalize_whitespace(item)
            if text:
                return text
        return None
    text = normalize_whitespace(value)
    return text or None


def _normalize_date(value: Any, *, field_name: str, required: bool = False) -> str | None:
    text = _first_string(value)
    if text is None:
        if required:
            raise ValueError(f"missing {field_name}")
        return None
    date_part = text.split("+", 1)[0].split("T", 1)[0]
    try:
        return date.fromisoformat(date_part).isoformat()
    except ValueError:
        raise ValueError(f"invalid {field_name}: {text!r}")


def _normalize_country(value: Any, *, field_name: str, required: bool = False) -> str | None:
    text = _first_string(value)
    if text is None:
        if required:
            raise ValueError(f"missing {field_name}")
        return None
    if text == "SVK":
        return "SK"
    if text == "SK":
        return "SK"
    return text


def _normalize_postal_code(value: Any) -> str | None:
    text = _first_string(value)
    if text is None:
        return None
    compact = text.replace(" ", "")
    return compact or None


def _publication_number(value: Any) -> str:
    text = _first_string(value)
    if text is None or not _PUBLICATION_NUMBER_RE.fullmatch(text):
        raise ValueError(f"publication-number must match 123456-YYYY, got {text!r}")
    return text


def _scan_forbidden_keys(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            item_path = f"{path}.{key}" if path else key
            if key in _PROCUREMENT_FORBIDDEN_KEYS:
                errors.append(f"forbidden procurement source field at {item_path}")
            _scan_forbidden_keys(item, item_path, errors)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _scan_forbidden_keys(item, f"{path}[{index}]", errors)


def normalize_procurement_notice_record(raw_record: dict[str, Any], *, row_number: int) -> dict[str, Any]:
    source_url = raw_record.get("links", {}).get("xml", {}).get("MUL")
    if not isinstance(source_url, str) or not source_url.startswith("https://ted.europa.eu/"):
        raise ValueError("missing TED XML source link")

    publication_number = _publication_number(raw_record.get("publication-number"))
    title = _first_localized_value(raw_record.get("notice-title"), field_name="notice-title")
    buyer_names = _localized_list(raw_record.get("buyer-name"))
    if not buyer_names:
        raise ValueError("missing buyer-name")
    buyer_country = _normalize_country(raw_record.get("buyer-country"), field_name="buyer-country", required=True)
    if buyer_country != "SK":
        raise ValueError(f"buyer country must normalize to SK, got {buyer_country!r}")

    record = {
        "id": publication_number,
        "title": title,
        "noticeType": _first_string(raw_record.get("notice-type")),
        "publicationDate": _normalize_date(raw_record.get("publication-date"), field_name="publication-date", required=True),
        "dispatchDate": _normalize_date(raw_record.get("dispatch-date"), field_name="dispatch-date"),
        "buyerNames": buyer_names,
        "buyerCountry": buyer_country,
        "placeOfPerformance": {
            "city": _first_string(raw_record.get("place-of-performance-city-proc")),
            "postalCode": _normalize_postal_code(raw_record.get("place-of-performance-post-code-proc")),
            "country": _normalize_country(raw_record.get("place-of-performance-country-proc"), field_name="place-of-performance-country-proc"),
        },
        "tenderDeadline": _normalize_date(raw_record.get("deadline-date-lot"), field_name="deadline-date-lot"),
        "regionCode": None,
        "districtCode": None,
        "municipalityCode": None,
        "sourceUrl": source_url,
    }
    if not record["noticeType"]:
        raise ValueError("missing notice-type")
    return record


def build_procurement_notices_payload(
    records: list[dict[str, Any]],
    *,
    total_notice_count: int,
    source: str = DEFAULT_SOURCE,
    last_updated: str | None = None,
) -> tuple[dict[str, Any], ImportResult]:
    result = ImportResult(input_path=Path(), output_path=Path(), dry_run=True)
    result.total_source_rows = len(records)
    normalized_records: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    forbidden_errors: list[str] = []

    for index, raw_record in enumerate(records, 1):
        _scan_forbidden_keys(raw_record, f"notices[{index}]", forbidden_errors)
        try:
            record = normalize_procurement_notice_record(raw_record, row_number=index)
        except ValueError as exc:
            result.malformed_records += 1
            result.skipped_records += 1
            result.errors.append(f"row {index}: {exc}")
            continue
        record_id = str(record["id"])
        if record_id in seen_ids:
            result.duplicate_records += 1
            result.skipped_records += 1
            result.warnings.append(f"row {index}: skipped duplicate publication number {record_id}")
            continue
        seen_ids.add(record_id)
        normalized_records.append(record)

    if forbidden_errors:
        result.errors.extend(forbidden_errors)

    normalized_records.sort(key=lambda item: (str(item.get("publicationDate") or ""), str(item.get("dispatchDate") or ""), str(item["id"])), reverse=True)
    result.imported_records = len(normalized_records)

    publication_dates = [str(item["publicationDate"]) for item in normalized_records if item.get("publicationDate")]
    snapshot_date = max(publication_dates) if publication_dates else (last_updated or date.today().isoformat())
    payload = {
        "metadata": {
            "source": source,
            "sourceUrl": SOURCE_API_URL,
            "license": SOURCE_LICENSE,
            "termsUrl": SOURCE_TERMS_URL,
            "lastUpdated": last_updated or snapshot_date,
            "complete": False,
            "coverage": "partial",
            "coverageDecision": COVERAGE_DECISION,
            "acquisitionDecision": ACQUISITION_DECISION,
            "snapshotLimit": len(normalized_records),
            "totalNoticesAtSource": total_notice_count,
            "notes": "Partial normalized TED Search API snapshot for notices with buyer-country SVK. This is not the national ÚVO procurement register and does not claim national coverage.",
        },
        "procurementNotices": normalized_records,
    }
    return payload, result


def _validate_payload(payload: dict[str, Any]) -> ValidationReport:
    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        for name in ("sources.json", "regions.json", "districts.json", "municipalities.json"):
            shutil.copy2(DEFAULT_DATA_DIR / name, temp_dir / name)
        write_json(temp_dir / "procurement_notices.json", payload)
        return validate_procurement_notices_dataset(temp_dir / "procurement_notices.json")


def run_import(*, input_path: Path = DEFAULT_INPUT, output_path: Path = DEFAULT_OUTPUT, source: str = DEFAULT_SOURCE, last_updated: str | None = None, write: bool = False) -> ImportResult:
    input_path = input_path.resolve()
    output_path = output_path.resolve()
    records, total_notice_count = _load_source_records(input_path)
    payload, result = build_procurement_notices_payload(records, total_notice_count=total_notice_count, source=source, last_updated=last_updated)
    result.input_path = input_path
    result.output_path = output_path
    result.dry_run = not write
    result.validation_report = _validate_payload(payload)
    if not result.validation_report.ok:
        result.errors.extend(f"{issue.path}: {issue.message}" for issue in result.validation_report.errors)
    if result.errors:
        return result
    if write:
        backup_existing_file(output_path)
        write_json(output_path, payload)
        result.wrote_files.append(output_path)
    return result


def _print_result(result: ImportResult) -> None:
    print(f"input={result.input_path} output={result.output_path}")
    print(f"total source rows={result.total_source_rows}")
    print(f"imported records={result.imported_records}")
    print(f"skipped records={result.skipped_records}")
    print(f"malformed records={result.malformed_records}")
    print(f"duplicate records={result.duplicate_records}")
    print(f"warnings={len(result.warnings)}")
    print(f"errors={len(result.errors)}")
    for warning in result.warnings:
        print(f"- warning: {warning}")
    for error in result.errors:
        print(f"- error: {error}")
    if result.wrote_files:
        for path in result.wrote_files:
            print(f"Wrote: {path}")
    elif result.dry_run:
        print("Dry run only; no files written.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import a checked TED Search API snapshot into normalized procurement-notice JSON.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Local TED Search API response JSON")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output path, default data/generated/procurement_notices.json")
    parser.add_argument("--source", default=DEFAULT_SOURCE, help="Source label stored in dataset metadata")
    parser.add_argument("--last-updated", default=None, help="Dataset lastUpdated date, YYYY-MM-DD")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Validate only; do not write files")
    mode.add_argument("--write", action="store_true", help="Write the normalized dataset")
    args = parser.parse_args(argv)

    try:
        result = run_import(input_path=args.input, output_path=args.output, source=args.source, last_updated=args.last_updated, write=args.write)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    _print_result(result)
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
