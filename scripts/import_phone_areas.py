#!/usr/bin/env python3
"""Offline importer for Slovak primary telephone area data."""

from __future__ import annotations

import argparse
import csv
import json
import re
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
DEFAULT_OUTPUT = DEFAULT_DATA_DIR / "generated" / "phone_areas.json"
DEFAULT_SOURCE = "Úrad pre reguláciu elektronických komunikácií a poštových služieb numbering data"
VALID_FORMATS = ("auto", "csv", "json", "xlsx", "xls")

from scripts.import_utils import _xlsx_rows, backup_existing_file, load_dataset_records, normalize_whitespace, write_json
from scripts.validate_datasets import ValidationReport, validate_phone_areas_dataset


@dataclass(frozen=True)
class MunicipalityRecord:
    code: str
    name: str
    district_code: str | None
    region_code: str | None


@dataclass
class ImportResult:
    input_path: Path
    output_path: Path
    input_format: str
    dry_run: bool
    total_records: int = 0
    linked_records: int = 0
    unlinked_records: int = 0
    duplicate_records: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    validation_report: ValidationReport | None = None
    wrote_files: list[Path] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors and (self.validation_report is None or self.validation_report.ok)


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
        text = normalize_whitespace(value)
        if text:
            return text
    return None


def _normalize_text_key(value: Any) -> str:
    text = normalize_whitespace(value).casefold()
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _normalize_phone_code(value: Any) -> str:
    text = normalize_whitespace(value).replace(" ", "")
    text = text.removeprefix("+").removeprefix("421") if text.startswith("+421") else text
    if text.isdigit() and not text.startswith("0") and len(text) in {1, 2}:
        text = f"0{text}"
    if not re.fullmatch(r"0\d{1,2}", text):
        raise ValueError(f"phone area code must match 0# or 0## format, got {value!r}")
    return text


def _load_municipality_index(data_dir: Path = DEFAULT_DATA_DIR) -> tuple[dict[str, MunicipalityRecord], dict[str, list[MunicipalityRecord]]]:
    by_code: dict[str, MunicipalityRecord] = {}
    by_name: dict[str, list[MunicipalityRecord]] = {}
    for record in load_dataset_records("municipalities", data_dir):
        code = normalize_whitespace(record.get("code"))
        name = normalize_whitespace(record.get("name"))
        if not code or not name:
            continue
        item = MunicipalityRecord(
            code=code,
            name=name,
            district_code=normalize_whitespace(record.get("districtCode")) or None,
            region_code=normalize_whitespace(record.get("regionCode")) or None,
        )
        by_code[code] = item
        by_name.setdefault(_normalize_text_key(name), []).append(item)
    return by_code, by_name


def _resolve_input_format(path: Path, input_format: str) -> str:
    if input_format != "auto":
        return input_format
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return "csv"
    if suffix == ".json":
        return "json"
    if suffix == ".xlsx":
        return "xlsx"
    if suffix == ".xls":
        return "xls"
    raise ValueError(f"Unable to detect input format from {path}")


def _read_csv(path: Path) -> list[dict[str, Any]]:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "cp1250"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = raw.decode("utf-8-sig", errors="replace")
    dialect = csv.Sniffer().sniff(text[:2048], delimiters=";,\t,")
    return [dict(row) for row in csv.DictReader(text.splitlines(), dialect=dialect)]


def _read_xlsx(path: Path) -> list[dict[str, Any]]:
    rows = _xlsx_rows(path)
    header_index = -1
    headers: list[str | None] | None = None
    required_aliases = ({"primarnaoblast", "primarnaoblastkod", "kod", "code", "smerovecislo", "ndc"}, {"obec", "obecname", "municipality", "municipalityname", "nazovobce"})
    for index, row in enumerate(rows):
        normalized = {_normalize_key(value) for value in row if value}
        if all(normalized & aliases for aliases in required_aliases):
            header_index = index
            headers = row
            break
    if headers is None:
        raise ValueError(f"Unable to locate a phone-area header row in {path}")

    records: list[dict[str, Any]] = []
    for row in rows[header_index + 1 :]:
        if not any(row):
            continue
        records.append({str(header): row[index] if index < len(row) else None for index, header in enumerate(headers) if header})
    return records


def _load_source_records(path: Path, input_format: str) -> tuple[str, list[dict[str, Any]]]:
    format_name = _resolve_input_format(path, input_format)
    if format_name == "csv":
        return format_name, _read_csv(path)
    if format_name == "xlsx":
        return format_name, _read_xlsx(path)
    if format_name == "xls":
        raise ValueError("Legacy .xls input is not supported directly; convert the workbook's List1 sheet to CSV first.")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        records = payload
    elif isinstance(payload, dict):
        for key in ("phoneAreas", "records", "data", "items"):
            if isinstance(payload.get(key), list):
                records = payload[key]
                break
        else:
            raise ValueError(f"Unable to locate phone area records in {path}")
    else:
        raise ValueError(f"Unsupported JSON input shape in {path}")

    result: list[dict[str, Any]] = []
    for index, item in enumerate(records):
        if not isinstance(item, dict):
            raise ValueError(f"{path}: records[{index}] must be an object")
        result.append(dict(item))
    return format_name, result


def normalize_phone_area_record(
    raw_record: dict[str, Any],
    municipalities_by_code: dict[str, MunicipalityRecord],
    municipalities_by_name: dict[str, list[MunicipalityRecord]],
    warnings: list[str],
    row_number: int,
) -> dict[str, Any]:
    code = _normalize_phone_code(_pick(raw_record, "code", "areaCode", "phoneAreaCode", "primaryAreaCode", "primárna oblasť", "primarna oblast", "smerové číslo", "smerove cislo", "NDC"))
    name = _pick(raw_record, "name", "areaName", "primaryAreaName", "názov primárnej oblasti", "nazov primarnej oblasti", "primaryArea", "PO") or code
    municipality_name = _pick(raw_record, "municipalityName", "municipality", "obec", "názov obce", "nazov obce")
    municipality_code = _pick(raw_record, "municipalityCode", "codeObce", "kod obce", "kód obce", "obecCode", "číselný kód obce", "ciselny kod obce")

    municipality: MunicipalityRecord | None = None
    if municipality_code:
        municipality = municipalities_by_code.get(municipality_code)
        if municipality is None:
            warnings.append(f"row {row_number}: municipalityCode {municipality_code} not found in local municipalities")
    elif municipality_name:
        matches = municipalities_by_name.get(_normalize_text_key(municipality_name), [])
        if len(matches) == 1:
            municipality = matches[0]
        elif len(matches) > 1:
            warnings.append(f"row {row_number}: municipality name {municipality_name!r} is ambiguous; leaving geography unlinked")
        else:
            warnings.append(f"row {row_number}: municipality name {municipality_name!r} not found in local municipalities")

    return {
        "code": code,
        "name": name,
        "municipalityCode": municipality.code if municipality is not None else None,
        "municipalityName": municipality.name if municipality is not None else (municipality_name or None),
        "districtCode": municipality.district_code if municipality is not None else None,
        "regionCode": municipality.region_code if municipality is not None else None,
        "country": "SK",
    }


def build_phone_areas_payload(records: list[dict[str, Any]], source: str, last_updated: str) -> tuple[dict[str, Any], ImportResult]:
    municipalities_by_code, municipalities_by_name = _load_municipality_index()
    result = ImportResult(input_path=Path(), output_path=Path(), input_format="auto", dry_run=True)
    normalized_records: list[dict[str, Any]] = []
    seen_exact: set[str] = set()

    for index, raw_record in enumerate(records):
        try:
            record = normalize_phone_area_record(raw_record, municipalities_by_code, municipalities_by_name, result.warnings, index + 1)
        except ValueError as exc:
            result.errors.append(f"row {index + 1}: {exc}")
            continue
        exact_key = json.dumps(record, ensure_ascii=False, sort_keys=True)
        if exact_key in seen_exact:
            result.duplicate_records += 1
            result.warnings.append(f"row {index + 1}: skipped duplicate phone area record")
            continue
        seen_exact.add(exact_key)
        if record.get("municipalityCode") and record.get("districtCode") and record.get("regionCode"):
            result.linked_records += 1
        else:
            result.unlinked_records += 1
        normalized_records.append(record)

    normalized_records.sort(key=lambda item: (str(item.get("code") or ""), str(item.get("municipalityName") or ""), str(item.get("municipalityCode") or "")))
    result.total_records = len(normalized_records)
    payload = {
        "metadata": {
            "source": source,
            "license": "Source/licence verification pending.",
            "lastUpdated": last_updated,
            "complete": True,
        },
        "phoneAreas": normalized_records,
    }
    return payload, result


def _validate_payload(payload: dict[str, Any]) -> ValidationReport:
    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        for name in ("sources.json", "regions.json", "districts.json", "municipalities.json"):
            shutil.copy2(DEFAULT_DATA_DIR / name, temp_dir / name)
        write_json(temp_dir / "phone_areas.json", payload)
        return validate_phone_areas_dataset(temp_dir / "phone_areas.json")


def run_import(
    *,
    input_path: Path,
    output_path: Path = DEFAULT_OUTPUT,
    input_format: str = "auto",
    source: str = DEFAULT_SOURCE,
    last_updated: str | None = None,
    write: bool = False,
) -> ImportResult:
    if input_format not in VALID_FORMATS:
        raise ValueError(f"Unsupported format {input_format!r}")
    input_path = input_path.resolve()
    output_path = output_path.resolve()
    format_name, records = _load_source_records(input_path, input_format)
    payload, result = build_phone_areas_payload(records, source, last_updated or date.today().isoformat())
    result.input_path = input_path
    result.output_path = output_path
    result.input_format = format_name
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
    print(f"input={result.input_path} output={result.output_path} format={result.input_format}")
    print(f"total records={result.total_records}")
    print(f"linked records={result.linked_records}")
    print(f"unlinked records={result.unlinked_records}")
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
    parser = argparse.ArgumentParser(description="Import Slovak primary telephone area data from a local CSV/JSON/XLSX file.")
    parser.add_argument("--input", required=True, type=Path, help="Local phone area source file")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output path, default data/generated/phone_areas.json")
    parser.add_argument("--format", choices=VALID_FORMATS, default="auto", help="Input format")
    parser.add_argument("--source", default=DEFAULT_SOURCE, help="Source label stored in dataset metadata")
    parser.add_argument("--last-updated", default=None, help="Dataset lastUpdated date, YYYY-MM-DD")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Validate only; do not write files")
    mode.add_argument("--write", action="store_true", help="Write imported JSON if validation passes")
    args = parser.parse_args(argv)

    result = run_import(
        input_path=args.input,
        output_path=args.output,
        input_format=args.format,
        source=args.source,
        last_updated=args.last_updated,
        write=bool(args.write),
    )
    _print_result(result)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
