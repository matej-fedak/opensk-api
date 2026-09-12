#!/usr/bin/env python3
"""Offline importer for the Slovak bank identification-code dataset."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
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

DEFAULT_OUTPUT = ROOT / "data" / "generated" / "banks.json"
DEFAULT_SOURCE = "NBS directory of identification codes for the domestic payment system in Slovak Republic"
VALID_FORMATS = ("auto", "csv", "json")
ACTIVE_MARKERS = {"C", "K"}
INACTIVE_MARKERS = {"Ø", "O", "0", ""}

from scripts.import_utils import backup_existing_file, normalize_whitespace, write_json
from scripts.validate_datasets import validate_banks_dataset


@dataclass
class ImportResult:
    input_path: Path
    output_path: Path
    input_format: str
    dry_run: bool
    total_records: int = 0
    active_records: int = 0
    inactive_records: int = 0
    duplicate_bank_codes: list[str] = field(default_factory=list)
    duplicate_bics: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    wrote_files: list[Path] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _read_text(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "cp1250"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8-sig", errors="replace")


def _normalize_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]", "", normalize_whitespace(value).casefold())


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


def _resolve_input_format(path: Path, input_format: str) -> str:
    if input_format != "auto":
        return input_format
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return "csv"
    if suffix == ".json":
        return "json"
    raise ValueError(f"Unable to detect input format from {path}")


def _load_source_records(path: Path, input_format: str) -> list[dict[str, Any]]:
    format_name = _resolve_input_format(path, input_format)
    if format_name == "csv":
        sample = _read_text(path)
        dialect = csv.Sniffer().sniff(sample[:1024], delimiters=";,\t")
        return [dict(row) for row in csv.DictReader(sample.splitlines(), dialect=dialect)]

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        records = payload
    elif isinstance(payload, dict):
        for key in ("banks", "records", "data", "items"):
            if isinstance(payload.get(key), list):
                records = payload[key]
                break
        else:
            raise ValueError(f"Unable to locate bank records in {path}")
    else:
        raise ValueError(f"Unsupported JSON input shape in {path}")

    normalized: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"{path}: records[{index}] must be an object")
        normalized.append(dict(record))
    return normalized


def _normalize_code(value: Any) -> str:
    text = normalize_whitespace(value).replace(" ", "")
    if not text.isdigit() or len(text) > 4:
        raise ValueError(f"bank code must be 1-4 digits before padding, got {value!r}")
    return text.zfill(4)


def _normalize_bic(value: Any) -> str | None:
    text = normalize_whitespace(value).replace(" ", "").upper()
    if not text:
        return None
    if not re.fullmatch(r"[A-Z0-9]{8}([A-Z0-9]{3})?", text):
        raise ValueError(f"bic/swift must be uppercase alphanumeric length 8 or 11, got {value!r}")
    return text


def _normalize_alphabetic_code(value: Any) -> str | None:
    text = normalize_whitespace(value).replace(" ", "").upper()
    if not text:
        return None
    if not re.fullmatch(r"[A-Z0-9]+", text):
        raise ValueError(f"alphabeticCode must be uppercase alphanumeric, got {value!r}")
    return text


def _normalize_active_marker(value: Any) -> tuple[bool, str]:
    text = normalize_whitespace(value).upper()
    if text in {"X", "C", "ÁNO", "ANO", "YES", "TRUE", "1"}:
        return True, "C"
    if text == "K":
        return True, "K"
    if text in INACTIVE_MARKERS or text in {"NIE", "NO", "FALSE"}:
        return False, "Ø"
    raise ValueError(f"unknown active-party marker {value!r}")


def _is_domestic_record(record: dict[str, Any]) -> bool:
    country = (_pick(record, "country", "countryCode") or "SK").upper()
    bic = _normalize_bic(_pick(record, "SWIFT 8", "swift", "bic", "BIC"))
    if bic is not None and len(bic) >= 6 and bic[4:6] != "SK":
        return False
    return country in {"SK", "SVK", "SLOVAKIA"}


def normalize_bank_record(raw_record: dict[str, Any]) -> dict[str, Any] | None:
    if not _is_domestic_record(raw_record):
        return None

    code = _normalize_code(_pick(raw_record, "Payment system code SR", "numeric", "code", "bankCode"))
    name = _pick(raw_record, "Payment service provider", "name", "provider", "NAME Domestic payment service provider")
    if name is None:
        raise ValueError(f"bank {code}: missing name")

    bic = _normalize_bic(_pick(raw_record, "SWIFT 8", "swift", "bic", "BIC"))
    alphabetic_code = _normalize_alphabetic_code(_pick(raw_record, "alphabeticCode", "alphabetic", "Alphabetic"))
    active_party, active_party_marker = _normalize_active_marker(_pick(raw_record, "Payment system SIPS", "activePartyMarker", "activeParty", "Active party"))

    return {
        "code": code,
        "name": name,
        "bic": bic,
        "swift": bic,
        "alphabeticCode": alphabetic_code,
        "activeParty": active_party,
        "activePartyMarker": active_party_marker,
        "country": "SK",
    }


def build_banks_payload(records: list[dict[str, Any]], source: str, last_updated: str) -> tuple[dict[str, Any], ImportResult]:
    result = ImportResult(input_path=Path(), output_path=Path(), input_format="auto", dry_run=True)
    normalized_records: list[dict[str, Any]] = []
    seen_codes: set[str] = set()
    seen_bics: set[str] = set()

    for index, raw_record in enumerate(records):
        try:
            record = normalize_bank_record(raw_record)
        except ValueError as exc:
            result.errors.append(f"row {index + 1}: {exc}")
            continue
        if record is None:
            result.warnings.append(f"row {index + 1}: skipped non-SK BIC record")
            continue

        code = str(record["code"])
        if code in seen_codes:
            result.duplicate_bank_codes.append(code)
            result.errors.append(f"duplicate bank code {code}")
            continue
        seen_codes.add(code)

        bic = record.get("bic")
        if isinstance(bic, str):
            if bic in seen_bics:
                result.duplicate_bics.append(bic)
                result.errors.append(f"duplicate BIC {bic}")
                continue
            seen_bics.add(bic)

        if record["activeParty"] is True:
            result.active_records += 1
        else:
            result.inactive_records += 1
        normalized_records.append(record)

    normalized_records.sort(key=lambda item: item["code"])
    result.total_records = len(normalized_records)

    payload = {
        "metadata": {
            "source": source,
            "license": "Source/licence verification pending.",
            "lastUpdated": last_updated,
            "complete": True,
        },
        "banks": normalized_records,
    }
    return payload, result


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
    records = _load_source_records(input_path, input_format)
    payload, result = build_banks_payload(records, source, last_updated or date.today().isoformat())
    result.input_path = input_path
    result.output_path = output_path
    result.input_format = _resolve_input_format(input_path, input_format)
    result.dry_run = not write

    if result.errors:
        return result

    if write:
        backup_existing_file(output_path)
        write_json(output_path, payload)
        report = validate_banks_dataset(output_path)
        if not report.ok:
            result.errors.extend(f"{issue.path}: {issue.message}" for issue in report.errors)
            return result
        result.wrote_files.append(output_path)
    return result


def _print_result(result: ImportResult) -> None:
    print(f"input={result.input_path} output={result.output_path} format={result.input_format}")
    print(f"total records={result.total_records}")
    print(f"active records={result.active_records}")
    print(f"inactive records={result.inactive_records}")
    print(f"duplicate bank codes={len(result.duplicate_bank_codes)}")
    print(f"duplicate BICs={len(result.duplicate_bics)}")
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
    parser = argparse.ArgumentParser(description="Import Slovak bank identification codes from a local NBS CSV/JSON file.")
    parser.add_argument("--input", required=True, type=Path, help="Local bank source file")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output path, default data/generated/banks.json")
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
