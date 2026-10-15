#!/usr/bin/env python3
"""Offline importer for the Slovak bank identification-code dataset."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from dataclasses import dataclass, field
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
from schemas.banks import (BankDatasetMetadata, NBS_SOURCE, NBS_SOURCE_URL, NBS_TERMS_URL,
                           NBS_LICENSE, NBS_TRANSFORMATION, nbs_attribution)

DEFAULT_SOURCE = NBS_SOURCE
PRODUCTION_PATH = ROOT / "data" / "banks.json"
CSV_PROFILES = (
    {"Payment system code SR", "Payment service provider", "SWIFT 8", "Payment system SIPS"},
    {"Kód platobného styku", "Poskytovateľ platobných služieb", "SWIFT kód 8", "Systém SIPS"},
)
VALID_FORMATS = ("auto", "csv", "json")
ACTIVE_MARKERS = {"C", "K"}
INACTIVE_MARKERS = {"Ø", "O", "0", ""}

from scripts.import_utils import backup_existing_file, normalize_whitespace, write_json
from scripts.validate_datasets import validate_banks_payload


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
    payload: dict[str, Any] = field(default_factory=dict)
    refresh: dict[str, Any] | None = None

    @property
    def ok(self) -> bool:
        return not self.errors


def _read_text(raw: bytes) -> str:
    for encoding in ("utf-8-sig", "cp1250"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("source is neither valid UTF-8 nor CP1250; no replacement decoding allowed")


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


def _load_source_records(path: Path, input_format: str, raw: bytes) -> list[dict[str, Any]]:
    format_name = _resolve_input_format(path, input_format)
    if format_name == "csv":
        text = _read_text(raw)
        # The reviewed Slovak file has a title row before its four-column
        # header. Do not guess column positions or fall back to Akt. úč.
        lines = [line for line in text.splitlines() if line.strip()]
        if lines and lines[0].rstrip("; ") == "Prevodník identifikačných kódov SR":
            lines = lines[1:]
        if not lines:
            raise ValueError("empty bank CSV")
        dialect = csv.Sniffer().sniff(lines[0], delimiters=";,\t")
        reader = csv.DictReader(io.StringIO("\n".join(lines)), dialect=dialect)
        headings = reader.fieldnames or []
        fields = set(headings)
        if len(fields) != len(headings) or not any(
            profile <= fields and fields - profile <= {"Akt. úč."} for profile in CSV_PROFILES
        ):
            raise ValueError("unreviewed bank CSV columns; source-column review required")
        records = [dict(row) for row in reader]
        if any(None in row or any(value is None for value in row.values()) for row in records):
            raise ValueError("bank CSV row width differs from reviewed header")
        return records

    payload = json.loads(raw.decode("utf-8-sig"))
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
    bic = _normalize_bic(_pick(record, "SWIFT 8", "SWIFT kód 8", "swift", "bic", "BIC"))
    if bic is not None and len(bic) >= 6 and bic[4:6] != "SK":
        return False
    return country in {"SK", "SVK", "SLOVAKIA"}


def normalize_bank_record(raw_record: dict[str, Any]) -> dict[str, Any] | None:
    if not _is_domestic_record(raw_record):
        return None

    code = _normalize_code(_pick(raw_record, "Payment system code SR", "Kód platobného styku", "numeric", "code", "bankCode"))
    name = _pick(raw_record, "Payment service provider", "Poskytovateľ platobných služieb", "name", "provider", "NAME Domestic payment service provider")
    if name is None:
        raise ValueError(f"bank {code}: missing name")

    bic = _normalize_bic(_pick(raw_record, "SWIFT 8", "SWIFT kód 8", "swift", "bic", "BIC"))
    alphabetic_code = _normalize_alphabetic_code(_pick(raw_record, "alphabeticCode", "alphabetic", "Alphabetic"))
    marker_fields = ("Payment system SIPS", "Systém SIPS", "activePartyMarker", "activeParty", "Active party")
    mapping = _field_map(raw_record)
    # Preserve a present blank SIPS marker over any conflicting convenience
    # alias. Akt. úč. is deliberately absent from this input selection.
    marker_key = next((_normalize_key(k) for k in marker_fields if _normalize_key(k) in mapping), None)
    if marker_key is None:
        raise ValueError("missing SIPS projection input; Akt. úč. is not a substitute")
    active_party, active_party_marker = _normalize_active_marker(mapping[marker_key])

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


def build_banks_payload(records: list[dict[str, Any]], metadata: dict[str, Any]) -> tuple[dict[str, Any], ImportResult]:
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
        "metadata": metadata,
        "banks": normalized_records,
    }
    return payload, result


def compare_bank_snapshots(previous: dict, current: dict, *, previous_source_version: str | None = None) -> dict:
    """Deterministic review report; no silent stale-row/history retention."""
    before = {row["code"]: row for row in previous["banks"]}
    after = {row["code"]: row for row in current["banks"]}
    common = sorted(before.keys() & after.keys())
    def changed(fields):
        return [{"code": code, "before": {k: before[code].get(k) for k in fields},
                 "after": {k: after[code].get(k) for k in fields}}
                for code in common if any(before[code].get(k) != after[code].get(k) for k in fields)]
    return {
        "previousSourceVersion": previous["metadata"].get("sourceVersion") or previous_source_version,
        "newSourceVersion": current["metadata"]["sourceVersion"],
        "previousEffectiveDate": previous["metadata"]["lastUpdated"],
        "newEffectiveDate": current["metadata"]["sourceEffectiveDate"],
        "previousRecordCount": len(before), "newRecordCount": len(after),
        "addedCodes": sorted(after.keys() - before.keys()), "removedCodes": sorted(before.keys() - after.keys()),
        "changedCodes": [code for code in common if before[code] != after[code]],
        "bicChanges": changed(("bic", "swift")), "providerNameChanges": changed(("name",)),
        "sipsProjectionChanges": changed(("activeParty", "activePartyMarker")),
        "activeProjectionCount": sum(row["activeParty"] for row in after.values()),
        "inactiveProjectionCount": sum(not row["activeParty"] for row in after.values()),
    }


def run_import(
    *,
    input_path: Path,
    output_path: Path = DEFAULT_OUTPUT,
    input_format: str = "auto",
    source: str = DEFAULT_SOURCE,
    source_version: str | None = None,
    effective_date: str | None = None,
    downloaded_at: str | None = None,
    source_file_url: str | None = None,
    compare_with: Path = PRODUCTION_PATH,
    previous_source_version: str | None = None,
    write: bool = False,
) -> ImportResult:
    if input_format not in VALID_FORMATS:
        raise ValueError(f"Unsupported format {input_format!r}")
    input_path = input_path.resolve()
    output_path = output_path.resolve()
    for label, value in (("source version", source_version), ("effective date", effective_date),
                         ("download timestamp", downloaded_at), ("source file URL", source_file_url)):
        if not value:
            raise ValueError(f"explicit {label} is required")
    raw = input_path.read_bytes()
    metadata = BankDatasetMetadata.model_validate({
        "source": source, "sourceUrl": NBS_SOURCE_URL, "sourceFileUrl": source_file_url,
        "termsUrl": NBS_TERMS_URL, "sourceVersion": source_version,
        "sourceEffectiveDate": effective_date, "downloadedAt": downloaded_at,
        "sourceBytes": len(raw), "sourceSha256": hashlib.sha256(raw).hexdigest(),
        "license": NBS_LICENSE, "attribution": nbs_attribution(source_version, effective_date),
        "transformation": NBS_TRANSFORMATION, "lastUpdated": effective_date, "complete": True,
    }).model_dump()
    records = _load_source_records(input_path, input_format, raw)
    payload, result = build_banks_payload(records, metadata)
    result.input_path = input_path
    result.output_path = output_path
    result.input_format = _resolve_input_format(input_path, input_format)
    result.dry_run = not write

    if result.errors:
        return result

    report = validate_banks_payload(payload, output_path)
    if not report.ok:
        result.errors.extend(f"{issue.path}: {issue.message}" for issue in report.errors)
        return result
    result.payload = payload
    if compare_with.exists():
        previous = json.loads(compare_with.read_text(encoding="utf-8"))
        result.refresh = compare_bank_snapshots(previous, payload, previous_source_version=previous_source_version)

    if write:
        backup_existing_file(output_path)
        write_json(output_path, payload)
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
    if result.refresh is not None:
        print(json.dumps(result.refresh, ensure_ascii=False, indent=2))
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
    parser.add_argument("--source-version", required=True, help="Version verified on official NBS converter page")
    parser.add_argument("--effective-date", "--last-updated", dest="effective_date", required=True, help="Verified source effective date, YYYY-MM-DD; never download/today's date")
    parser.add_argument("--downloaded-at", required=True, help="Actual source acquisition timestamp with timezone")
    parser.add_argument("--source-file-url", required=True, help="Exact official URL of the acquired file")
    parser.add_argument("--compare-with", type=Path, default=PRODUCTION_PATH, help="Previous local snapshot for deterministic review report")
    parser.add_argument("--previous-source-version", help="Evidence-backed previous version if legacy snapshot metadata lacks it")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Validate only; do not write files")
    mode.add_argument("--write", action="store_true", help="Write imported JSON if validation passes")
    args = parser.parse_args(argv)

    result = run_import(
        input_path=args.input,
        output_path=args.output,
        input_format=args.format,
        source=args.source,
        source_version=args.source_version,
        effective_date=args.effective_date,
        downloaded_at=args.downloaded_at,
        source_file_url=args.source_file_url,
        compare_with=args.compare_with,
        previous_source_version=args.previous_source_version,
        write=bool(args.write),
    )
    _print_result(result)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
