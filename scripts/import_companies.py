#!/usr/bin/env python3
"""Offline importer for research company/IČO samples.

The importer normalizes local JSON samples into the proposed `companies` shape,
validates that `ico` is exactly 8 digits, and defaults to previewing output
under `data/generated/companies.json`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone
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
DEFAULT_OUTPUT_DIR = DEFAULT_DATA_DIR / "generated"
DEFAULT_OUTPUT_FILE = DEFAULT_OUTPUT_DIR / "companies.json"
DEFAULT_SOURCE = "RPO research prototype"
PRODUCTION_OUTPUT_FILE = DEFAULT_DATA_DIR / "companies.json"

from scripts.import_utils import backup_existing_file, load_json, normalize_ico, normalize_whitespace, write_json


@dataclass
class ImportResult:
    input_path: Path
    output_path: Path
    source: str
    dry_run: bool
    record_count: int = 0
    wrote_files: list[Path] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _normalize_key(value: Any) -> str:
    text = normalize_whitespace(value).casefold()
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(char for char in normalized if char.isalnum() and not unicodedata.combining(char))


def _field_map(record: dict[str, Any]) -> dict[str, Any]:
    return {_normalize_key(key): value for key, value in record.items() if key is not None}


def _pick(record: dict[str, Any], *names: str) -> str | None:
    mapping = _field_map(record)
    for name in names:
        value = mapping.get(_normalize_key(name))
        if value is None:
            continue
        text = normalize_whitespace(value)
        if text:
            return text
    return None


def _normalize_country(value: Any, *, default: str = "SK") -> str:
    text = normalize_whitespace(value)
    if not text:
        return default

    normalized = text.casefold()
    if normalized in {"sk", "svk", "slovakia"}:
        return "SK"
    return text


def _normalize_iso_date(value: Any, *, field_name: str) -> str | None:
    text = normalize_whitespace(value)
    if not text:
        return None

    match = re.match(r"^(\d{4}-\d{2}-\d{2})", text)
    if not match:
        raise ValueError(f"{field_name} must be an ISO date, got {value!r}")

    return match.group(1)


def _load_source_records(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    payload = load_json(path)
    return _source_records_from_payload(path, payload)


def _source_records_from_payload(path: Path, payload: Any) -> list[dict[str, Any]]:
    records: list[Any]

    if isinstance(payload, list):
        records = list(payload)
    elif isinstance(payload, dict):
        for key in ("records", "companies", "data", "items"):
            if isinstance(payload.get(key), list):
                records = list(payload[key])
                break
        else:
            records = []
            for key, value in payload.items():
                if key == "metadata":
                    continue
                if not isinstance(value, dict):
                    continue
                item = dict(value)
                item.setdefault("ico", key)
                records.append(item)
    else:
        raise ValueError(f"Unsupported JSON input shape in {path}")

    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(records):
        if not isinstance(item, dict):
            raise ValueError(f"{path}: records[{index}] must be an object")
        normalized.append(dict(item))

    return normalized


def _source_date(path: Path, payload: Any) -> str:
    if isinstance(payload, dict):
        metadata = payload.get("metadata")
        if isinstance(metadata, dict):
            last_updated = metadata.get("lastUpdated") or metadata.get("lastChecked")
            if isinstance(last_updated, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", last_updated):
                return last_updated

    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).date().isoformat()


def _source_record_id(raw_record: dict[str, Any], ico: str, index: int) -> str:
    for key in ("recordId", "sourceRecordId", "sourceId", "entityId", "id", "rpoId", "registerId", "uuid"):
        value = _pick(raw_record, key)
        if value is not None:
            return value
    return ico or f"row-{index + 1}"


def _build_address(raw_record: dict[str, Any]) -> dict[str, Any]:
    raw_address = None
    for key in ("address", "sidlo", "registeredOffice", "registered_office", "seat", "seatAddress"):
        raw_address = raw_record.get(key)
        if raw_address is not None:
            break

    if raw_address is None:
        raw_address = {}

    if isinstance(raw_address, str):
        text = normalize_whitespace(raw_address)
        raw_address = {"street": text} if text else {}

    if not isinstance(raw_address, dict):
        raw_address = {}

    street = _pick(raw_address, "street", "ulica", "streetName", "addressLine1")
    registration_number = _pick(
        raw_address,
        "registrationNumber",
        "registration_number",
        "supisneCislo",
        "conscriptionNumber",
        "houseNumber",
    )
    building_number = _pick(
        raw_address,
        "buildingNumber",
        "building_number",
        "orientacneCislo",
        "orientationNumber",
        "addressLine2",
    )
    municipality = _pick(raw_address, "municipality", "obec", "city", "mesto")
    postal_code = _pick(raw_address, "postalCode", "zip", "psc")
    municipality_code = _pick(raw_address, "municipalityCode")
    district_code = _pick(raw_address, "districtCode")
    region_code = _pick(raw_address, "regionCode")
    country = _pick(raw_address, "country", "countryCode", "stat")

    return {
        "street": street,
        "registrationNumber": registration_number,
        "buildingNumber": building_number,
        "municipality": municipality,
        "postalCode": postal_code,
        "country": _normalize_country(country),
        "municipalityCode": municipality_code,
        "regionCode": region_code,
        "districtCode": district_code,
    }


def _normalize_company_record(raw_record: dict[str, Any], *, source: str, source_date: str, index: int) -> dict[str, Any]:
    ico_raw = _pick(raw_record, "ico", "IČO", "icO", "companyId", "company_id")
    if ico_raw is None:
        raise ValueError("missing ico")

    name = _pick(raw_record, "name", "obchodneMeno", "obchodnéMeno", "businessName", "companyName")
    if name is None:
        raise ValueError(f"IČO {ico_raw!r}: missing company name")

    ico = normalize_ico(ico_raw)
    record: dict[str, Any] = {
        "ico": ico,
        "name": name,
        "legalForm": _pick(raw_record, "legalForm", "pravnaForma", "legal_form", "form"),
        "legalStatus": _pick(raw_record, "legalStatus", "status", "stav", "state"),
        "sourceRegister": _pick(raw_record, "sourceRegister", "registerName", "register", "registry", "source_registry"),
        "address": _build_address(raw_record),
        "establishedOn": _normalize_iso_date(
            _pick(raw_record, "establishedOn", "registeredAt", "foundedOn", "dateRegistered", "vznik", "createdAt"),
            field_name=f"IČO {ico}: establishedOn",
        ),
        "terminatedOn": _normalize_iso_date(
            _pick(raw_record, "terminatedOn", "dissolvedOn", "cancelledOn", "deletedOn", "zrusenOn", "zanikOn", "closedOn"),
            field_name=f"IČO {ico}: terminatedOn",
        ),
        "updatedAt": _normalize_iso_date(
            _pick(raw_record, "updatedAt", "lastUpdated", "modifiedAt", "last_modified", "dbModificationDate") or source_date,
            field_name=f"IČO {ico}: updatedAt",
        ),
        "source": {
            "name": source,
            "recordId": _source_record_id(raw_record, ico, index),
        },
    }

    return record


def _sort_key(record: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        normalize_whitespace(record.get("ico")),
        normalize_whitespace(record.get("name")).casefold(),
        normalize_whitespace((record.get("source") or {}).get("recordId")).casefold(),
        json.dumps(record.get("address"), ensure_ascii=False, sort_keys=True),
    )


def _build_payload(records: list[dict[str, Any]], source: str, source_date: str) -> dict[str, Any]:
    ordered_records = sorted(records, key=_sort_key)
    return {
        "metadata": {
            "source": source,
            "lastUpdated": source_date,
            "complete": False,
        },
        "companies": ordered_records,
    }


def _resolve_output_path(output_path: Path) -> Path:
    if output_path.suffix.lower() == ".json":
        return output_path
    return output_path / "companies.json"


def run_import(
    *,
    input_path: Path,
    output_path: Path = DEFAULT_OUTPUT_FILE,
    source: str = DEFAULT_SOURCE,
    write: bool = False,
) -> ImportResult:
    input_path = input_path.resolve()
    output_path = output_path.resolve()

    payload = load_json(input_path)
    source_date = _source_date(input_path, payload)
    raw_records = _source_records_from_payload(input_path, payload)
    if not raw_records:
        raise ValueError(f"No company records found in {input_path}")

    records: list[dict[str, Any]] = []
    errors: list[str] = []
    for index, raw_record in enumerate(raw_records):
        try:
            records.append(_normalize_company_record(raw_record, source=source, source_date=source_date, index=index))
        except ValueError as exc:
            errors.append(f"records[{index}]: {exc}")

    result = ImportResult(
        input_path=input_path,
        output_path=output_path,
        source=source,
        dry_run=not write,
        record_count=len(records),
        errors=errors,
    )

    if errors:
        return result

    payload = _build_payload(records, source, source_date)
    destination = _resolve_output_path(output_path)

    if write:
        if destination == PRODUCTION_OUTPUT_FILE.resolve():
            result.errors.append("Refusing to write data/companies.json in this milestone; use data/generated/companies.json")
            return result

        backup_existing_file(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        write_json(destination, payload)
        result.wrote_files.append(destination)

    return result


def _print_result(result: ImportResult) -> None:
    print(f"input={result.input_path} output={result.output_path} source={result.source}")
    status = "OK" if result.ok else "FAIL"
    print(f"companies: {status} records={result.record_count} errors={len(result.errors)}")

    for warning in result.warnings:
        print(f"- warning: {warning}")
    for error in result.errors:
        print(f"- error: {error}")

    if result.wrote_files:
        print("Wrote:")
        for path in result.wrote_files:
            print(f"- {path}")
    elif result.dry_run:
        print("Dry run only; no files written.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Import company/IČO data from local JSON files.")
    parser.add_argument("--input", required=True, type=Path, help="Input local JSON file")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_FILE, help="Output file or directory")
    parser.add_argument("--source", default=DEFAULT_SOURCE, help="Source label stored in metadata and records")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Validate only; do not write files")
    mode.add_argument("--write", action="store_true", help="Write the normalized companies JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = run_import(
            input_path=args.input,
            output_path=args.output,
            source=args.source,
            write=bool(args.write),
        )
    except (OSError, ValueError, FileNotFoundError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    _print_result(result)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
