#!/usr/bin/env python3
"""Offline importer for MŠVVaM school facility aggregate counts."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
import tempfile
import unicodedata
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
DEFAULT_OUTPUT = DEFAULT_DATA_DIR / "generated" / "school_facility_counts.json"
DEFAULT_SOURCE = "MŠVVaM SR Register škôl a školských zariadení aggregate CSV"
SOURCE_LICENSE = "Creative Commons BY as listed on the MŠVVaM source page."
EXPECTED_HEADERS = [
    "Druh školy skrátený",
    "Typ školy skrátený",
    "Druh 1",
    "Druh 2",
    "Kraj názov",
    "NUTS3",
    "Okres názov",
    "LAU1",
    "Počet organizačných zložiek",
    "Zriaďovateľ - Forma vlastníctva názov",
    "Zriaďovateľ - Typ názov",
]

from scripts.import_utils import backup_existing_file, load_dataset_records, normalize_whitespace, write_json
from scripts.validate_datasets import ValidationReport, validate_school_facility_counts_dataset


@dataclass(frozen=True)
class DistrictRecord:
    code: str
    name: str
    region_code: str


@dataclass
class ImportResult:
    input_path: Path
    output_path: Path
    dry_run: bool
    total_source_rows: int = 0
    imported_records: int = 0
    skipped_records: int = 0
    duplicate_records: int = 0
    region_links: int = 0
    district_links: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    validation_report: ValidationReport | None = None
    wrote_files: list[Path] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors and (self.validation_report is None or self.validation_report.ok)


def _read_text(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "cp1250"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8-sig", errors="replace")


def _normalize_key(value: Any) -> str:
    text = normalize_whitespace(value).casefold()
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(char for char in normalized if char.isalnum() and not unicodedata.combining(char))


def _normalize_text_key(value: Any) -> str:
    text = normalize_whitespace(value).casefold().replace(" - ", "-")
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _field_map(record: dict[str, Any]) -> dict[str, Any]:
    return {_normalize_key(key): value for key, value in record.items() if key is not None}


def _pick(record: dict[str, Any], name: str) -> str | None:
    text = normalize_whitespace(_field_map(record).get(_normalize_key(name)))
    return text or None


def _load_source_records(path: Path) -> list[dict[str, Any]]:
    text = _read_text(path)
    dialect = csv.Sniffer().sniff(text[:2048], delimiters=";,\t,")
    reader = csv.DictReader(text.splitlines(), dialect=dialect, restkey="__extra__")
    headers = [header for header in (reader.fieldnames or []) if normalize_whitespace(header)]
    if [_normalize_key(header) for header in headers] != [_normalize_key(header) for header in EXPECTED_HEADERS]:
        raise ValueError(f"unexpected CSV headers: {headers}")
    return [dict(row) for row in reader]


def _load_districts(data_dir: Path = DEFAULT_DATA_DIR) -> dict[str, DistrictRecord]:
    districts: dict[str, DistrictRecord] = {}
    for record in load_dataset_records("districts", data_dir):
        code = normalize_whitespace(record.get("code"))
        name = normalize_whitespace(record.get("name"))
        region_code = normalize_whitespace(record.get("regionCode"))
        if code and name and region_code:
            districts[code] = DistrictRecord(code=code, name=name, region_code=region_code)
    return districts


def _district_code_candidates(lau1: str) -> list[str]:
    if not lau1:
        return []
    candidates = [lau1]
    suffix = lau1[-1]
    if suffix.isalpha() and len(lau1) == 6:
        numeric_suffix = 10 + ord(suffix.upper()) - ord("A")
        candidates.append(f"{lau1[:5]}{numeric_suffix}")
    return candidates


def _resolve_district_code(lau1: str | None, district_name: str | None, region_code: str | None, districts: dict[str, DistrictRecord], warnings: list[str], row_number: int) -> str | None:
    if not lau1:
        warnings.append(f"row {row_number}: missing LAU1; leaving districtCode null")
        return None
    for candidate in _district_code_candidates(lau1):
        district = districts.get(candidate)
        if district is None:
            continue
        if region_code and district.region_code != region_code:
            warnings.append(f"row {row_number}: LAU1 {lau1} candidate {candidate} belongs to region {district.region_code}, not {region_code}; leaving districtCode null")
            return None
        if district_name and _normalize_text_key(district.name) != _normalize_text_key(district_name):
            warnings.append(f"row {row_number}: LAU1 {lau1} candidate {candidate} name {district.name!r} does not match source district {district_name!r}; leaving districtCode null")
            return None
        return candidate
    warnings.append(f"row {row_number}: LAU1 {lau1} does not match a local district; leaving districtCode null")
    return None


def _parse_count(value: Any) -> int:
    text = normalize_whitespace(value).replace(" ", "")
    if not text.isdigit():
        raise ValueError(f"organizational unit count must be a non-negative integer, got {value!r}")
    return int(text)


def normalize_school_facility_count_record(raw_record: dict[str, Any], districts: dict[str, DistrictRecord], warnings: list[str], row_number: int) -> dict[str, Any]:
    extras = raw_record.get("__extra__")
    if isinstance(extras, list) and any(normalize_whitespace(extra) for extra in extras):
        warnings.append(f"row {row_number}: ignored extra source columns after expected aggregate fields")

    region_name = _pick(raw_record, "Kraj názov")
    region_code = _pick(raw_record, "NUTS3")
    district_name = _pick(raw_record, "Okres názov")
    district_code = _resolve_district_code(_pick(raw_record, "LAU1"), district_name, region_code, districts, warnings, row_number)
    count = _parse_count(_pick(raw_record, "Počet organizačných zložiek"))

    if not region_name:
        raise ValueError("missing region name")
    if not region_code:
        raise ValueError("missing NUTS3 region code")
    if not district_name:
        raise ValueError("missing district name")

    return {
        "schoolKindShort": _pick(raw_record, "Druh školy skrátený"),
        "schoolTypeShort": _pick(raw_record, "Typ školy skrátený"),
        "kindLevel1": _pick(raw_record, "Druh 1"),
        "kindLevel2": _pick(raw_record, "Druh 2"),
        "regionName": region_name,
        "regionCode": region_code,
        "districtName": district_name,
        "districtCode": district_code,
        "organizationalUnitCount": count,
        "founderOwnershipType": _pick(raw_record, "Zriaďovateľ - Forma vlastníctva názov"),
        "founderType": _pick(raw_record, "Zriaďovateľ - Typ názov"),
        "country": "SK",
    }


def build_school_facility_counts_payload(records: list[dict[str, Any]], source: str, last_updated: str) -> tuple[dict[str, Any], ImportResult]:
    districts = _load_districts()
    result = ImportResult(input_path=Path(), output_path=Path(), dry_run=True)
    result.total_source_rows = len(records)
    normalized_records: list[dict[str, Any]] = []
    seen_exact: set[str] = set()

    for index, raw_record in enumerate(records):
        try:
            record = normalize_school_facility_count_record(raw_record, districts, result.warnings, index + 1)
        except ValueError as exc:
            result.skipped_records += 1
            result.errors.append(f"row {index + 1}: {exc}")
            continue

        exact_key = json.dumps(record, ensure_ascii=False, sort_keys=True)
        if exact_key in seen_exact:
            result.duplicate_records += 1
            result.skipped_records += 1
            result.warnings.append(f"row {index + 1}: skipped duplicate aggregate row")
            continue
        seen_exact.add(exact_key)

        if record.get("regionCode"):
            result.region_links += 1
        if record.get("districtCode"):
            result.district_links += 1
        normalized_records.append(record)

    normalized_records.sort(
        key=lambda item: (
            str(item.get("regionCode") or ""),
            str(item.get("districtCode") or ""),
            str(item.get("schoolKindShort") or ""),
            str(item.get("schoolTypeShort") or ""),
            str(item.get("founderOwnershipType") or ""),
            str(item.get("founderType") or ""),
        )
    )
    result.imported_records = len(normalized_records)

    payload = {
        "metadata": {
            "source": source,
            "license": SOURCE_LICENSE,
            "lastUpdated": last_updated,
            "complete": True,
            "validityDate": "2025-09-15",
            "updatePeriodicity": "semiannual",
            "notes": "Aggregate school facility counts from RIS. This is not an institution-level school directory.",
        },
        "schoolFacilityCounts": normalized_records,
    }
    return payload, result


def _validate_payload(payload: dict[str, Any]) -> ValidationReport:
    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        for name in ("sources.json", "regions.json", "districts.json"):
            shutil.copy2(DEFAULT_DATA_DIR / name, temp_dir / name)
        write_json(temp_dir / "school_facility_counts.json", payload)
        return validate_school_facility_counts_dataset(temp_dir / "school_facility_counts.json")


def run_import(*, input_path: Path, output_path: Path = DEFAULT_OUTPUT, source: str = DEFAULT_SOURCE, last_updated: str | None = None, write: bool = False) -> ImportResult:
    input_path = input_path.resolve()
    output_path = output_path.resolve()
    records = _load_source_records(input_path)
    payload, result = build_school_facility_counts_payload(records, source, last_updated or date.today().isoformat())
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
    print(f"duplicate aggregate rows={result.duplicate_records}")
    print(f"region links={result.region_links}")
    print(f"district links={result.district_links}")
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
    parser = argparse.ArgumentParser(description="Import MŠVVaM school facility aggregate counts from a local CSV file.")
    parser.add_argument("--input", required=True, type=Path, help="Local MŠVVaM aggregate CSV file")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output path, default data/generated/school_facility_counts.json")
    parser.add_argument("--source", default=DEFAULT_SOURCE, help="Source label stored in dataset metadata")
    parser.add_argument("--last-updated", default=None, help="Dataset lastUpdated date, YYYY-MM-DD")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Validate only; do not write files")
    mode.add_argument("--write", action="store_true", help="Write imported JSON if validation passes")
    args = parser.parse_args(argv)

    result = run_import(
        input_path=args.input,
        output_path=args.output,
        source=args.source,
        last_updated=args.last_updated,
        write=bool(args.write),
    )
    _print_result(result)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
