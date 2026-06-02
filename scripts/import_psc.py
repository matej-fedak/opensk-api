#!/usr/bin/env python3
"""Offline importer for PSC datasets.

Supports local CSV and JSON source files, resolves geography against the
checked-in geography datasets, and writes the canonical `data/psc.json` shape.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
import tempfile
import unicodedata
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

DEFAULT_DATA_DIR = ROOT / "data"
DEFAULT_OUTPUT_DIR = DEFAULT_DATA_DIR / "generated"
DEFAULT_OUTPUT_FILE = DEFAULT_OUTPUT_DIR / "psc.json"

VALID_FORMATS = ("csv", "json", "auto")
VALID_SOURCES = ("portalvs", "data-gov", "custom")

from scripts.import_utils import (
    backup_existing_file,
    copy_existing_file,
    load_dataset_records,
    load_json,
    normalize_whitespace,
    read_csv,
    today_iso,
    write_json,
)
from scripts.validate_datasets import ValidationReport, validate_psc_dataset


@dataclass(frozen=True)
class GeographyRecord:
    code: str
    name: str
    region_code: str | None = None
    district_code: str | None = None


@dataclass
class GeographyIndex:
    regions_by_code: dict[str, GeographyRecord]
    regions_by_name: dict[str, list[GeographyRecord]]
    districts_by_code: dict[str, GeographyRecord]
    districts_by_name: dict[str, list[GeographyRecord]]
    municipalities_by_code: dict[str, GeographyRecord]
    municipalities_by_name: dict[str, list[GeographyRecord]]


@dataclass
class ImportResult:
    input_path: Path
    output_path: Path
    source: str
    input_format: str
    dry_run: bool
    wrote_files: list[Path] = field(default_factory=list)
    validation_report: ValidationReport | None = None
    warnings: list[str] = field(default_factory=list)
    integrity_errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.validation_report is not None and self.validation_report.ok and not self.integrity_errors


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


def _normalize_psc(value: Any) -> str:
    text = normalize_whitespace(value).replace(" ", "")
    if len(text) != 5 or not text.isdigit():
        raise ValueError(f"PSC must be exactly 5 digits, got {value!r}")
    return text


def _resolve_input_file(input_path: Path, input_format: str) -> Path:
    if input_path.is_file():
        if input_format == "auto":
            return input_path
        expected_suffix = f".{input_format}"
        if input_path.suffix.lower() != expected_suffix:
            return input_path
        return input_path

    if not input_path.is_dir():
        raise ValueError(f"Input path does not exist: {input_path}")

    candidates: list[Path] = []
    if input_format in ("auto", "csv"):
        candidates.append(input_path / "psc.csv")
    if input_format in ("auto", "json"):
        candidates.append(input_path / "psc.json")

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    if input_format == "auto":
        matches = [path for path in input_path.iterdir() if path.suffix.lower() in {".csv", ".json"} and path.is_file()]
        if len(matches) == 1:
            return matches[0]

    raise FileNotFoundError(f"Unable to locate PSC input file in {input_path}")


def _load_source_records(path: Path, input_format: str) -> list[dict[str, Any]]:
    if input_format == "auto":
        format_name = path.suffix.lower().lstrip(".")
        if format_name not in {"csv", "json"}:
            raise ValueError(f"Unable to detect input format from {path}")
    else:
        format_name = input_format

    if format_name == "csv":
        return read_csv(path)

    payload = load_json(path)
    if isinstance(payload, list):
        records: list[dict[str, Any]] = []
        for index, item in enumerate(payload):
            if not isinstance(item, dict):
                raise ValueError(f"{path}: item {index} must be an object")
            records.append(dict(item))
        return records

    if isinstance(payload, dict):
        if isinstance(payload.get("records"), list):
            records = []
            for index, item in enumerate(payload["records"]):
                if not isinstance(item, dict):
                    raise ValueError(f"{path}: records[{index}] must be an object")
                records.append(dict(item))
            return records

        if isinstance(payload.get("data"), list):
            records = []
            for index, item in enumerate(payload["data"]):
                if not isinstance(item, dict):
                    raise ValueError(f"{path}: data[{index}] must be an object")
                records.append(dict(item))
            return records

        records = []
        for key, value in payload.items():
            if key == "metadata":
                continue
            if not isinstance(value, dict):
                raise ValueError(f"{path}: PSC record {key!r} must be an object")
            item = dict(value)
            item.setdefault("psc", key)
            records.append(item)
        if records:
            return records

    raise ValueError(f"Unable to locate PSC records in {path}")


def _load_geography_index(data_dir: Path = DEFAULT_DATA_DIR) -> GeographyIndex:
    regions = load_dataset_records("regions", data_dir)
    districts = load_dataset_records("districts", data_dir)
    municipalities = load_dataset_records("municipalities", data_dir)

    def _region(record: dict[str, Any]) -> GeographyRecord:
        return GeographyRecord(code=str(record["code"]), name=str(record["name"]))

    def _district(record: dict[str, Any]) -> GeographyRecord:
        return GeographyRecord(code=str(record["code"]), name=str(record["name"]), region_code=str(record["regionCode"]))

    def _municipality(record: dict[str, Any]) -> GeographyRecord:
        region_code = record.get("regionCode")
        district_code = record.get("districtCode")
        return GeographyRecord(
            code=str(record["code"]),
            name=str(record["name"]),
            region_code=str(region_code) if region_code is not None else None,
            district_code=str(district_code) if district_code is not None else None,
        )

    def _by_name(records: list[GeographyRecord]) -> dict[str, list[GeographyRecord]]:
        mapping: dict[str, list[GeographyRecord]] = {}
        for record in records:
            mapping.setdefault(_normalize_key(record.name), []).append(record)
        return mapping

    region_records = [_region(record) for record in regions]
    district_records = [_district(record) for record in districts]
    municipality_records = [_municipality(record) for record in municipalities]

    return GeographyIndex(
        regions_by_code={record.code: record for record in region_records},
        regions_by_name=_by_name(region_records),
        districts_by_code={record.code: record for record in district_records},
        districts_by_name=_by_name(district_records),
        municipalities_by_code={record.code: record for record in municipality_records},
        municipalities_by_name=_by_name(municipality_records),
    )


def _stage_geography_files(stage_dir: Path, data_dir: Path = DEFAULT_DATA_DIR) -> None:
    for name in ("regions", "districts", "municipalities"):
        source = data_dir / f"{name}.json"
        if not source.is_file():
            raise FileNotFoundError(f"Missing required geography file: {source}")
        copy_existing_file(source, stage_dir / source.name)


def _resolve_record_geography(
    raw_record: dict[str, Any],
    geography: GeographyIndex,
) -> tuple[dict[str, Any], list[str]]:
    municipality_name = _pick(raw_record, "municipalityName", "municipality")
    district_name = _pick(raw_record, "districtName", "district")
    region_name = _pick(raw_record, "regionName", "region")

    municipality_code_raw = _pick(raw_record, "municipalityCode")
    district_code_raw = _pick(raw_record, "districtCode")
    region_code_raw = _pick(raw_record, "regionCode")

    resolved_municipality: GeographyRecord | None = None
    resolved_district: GeographyRecord | None = None
    resolved_region: GeographyRecord | None = None
    issues: list[str] = []

    def _resolve_by_name(
        *,
        label: str,
        name: str,
        candidates: list[GeographyRecord],
        district_context: str | None = None,
        region_context: str | None = None,
    ) -> GeographyRecord | None:
        filtered = candidates
        if district_context is not None:
            filtered = [record for record in filtered if record.district_code == district_context]
        if region_context is not None:
            filtered = [record for record in filtered if record.region_code == region_context]
        if len(filtered) == 1:
            return filtered[0]
        if len(filtered) > 1:
            issues.append(f"ambiguous {label}Name {name!r}")
            return None
        issues.append(f"unknown {label}Name {name!r}")
        return None

    if municipality_code_raw is not None:
        resolved_municipality = geography.municipalities_by_code.get(municipality_code_raw)
        if resolved_municipality is None:
            issues.append(f"unknown municipalityCode {municipality_code_raw}")
    elif municipality_name is not None:
        resolved_municipality = _resolve_by_name(
            label="municipality",
            name=municipality_name,
            candidates=geography.municipalities_by_name.get(_normalize_key(municipality_name), []),
            district_context=district_code_raw,
            region_context=region_code_raw,
        )

    if district_code_raw is not None:
        resolved_district = geography.districts_by_code.get(district_code_raw)
        if resolved_district is None:
            issues.append(f"unknown districtCode {district_code_raw}")
    elif district_name is not None:
        region_context = resolved_municipality.region_code if resolved_municipality is not None else region_code_raw
        resolved_district = _resolve_by_name(
            label="district",
            name=district_name,
            candidates=geography.districts_by_name.get(_normalize_key(district_name), []),
            region_context=region_context,
        )

    if region_code_raw is not None:
        resolved_region = geography.regions_by_code.get(region_code_raw)
        if resolved_region is None:
            issues.append(f"unknown regionCode {region_code_raw}")
    elif region_name is not None:
        region_context = None
        if resolved_municipality is not None:
            region_context = resolved_municipality.region_code
        elif resolved_district is not None:
            region_context = resolved_district.region_code
        resolved_region = _resolve_by_name(
            label="region",
            name=region_name,
            candidates=geography.regions_by_name.get(_normalize_key(region_name), []),
            region_context=region_context,
        )

    if resolved_municipality is not None:
        if resolved_municipality.district_code is not None:
            resolved_district = geography.districts_by_code.get(resolved_municipality.district_code)
        if resolved_municipality.region_code is not None:
            resolved_region = geography.regions_by_code.get(resolved_municipality.region_code)

    if resolved_district is not None and resolved_region is None and resolved_district.region_code is not None:
        resolved_region = geography.regions_by_code.get(resolved_district.region_code)

    if resolved_municipality is not None and municipality_name is not None and _normalize_key(resolved_municipality.name) != _normalize_key(municipality_name):
        issues.append(f"municipalityName {municipality_name!r} does not match municipalityCode {resolved_municipality.code}")
    if resolved_district is not None and district_name is not None and _normalize_key(resolved_district.name) != _normalize_key(district_name):
        issues.append(f"districtName {district_name!r} does not match districtCode {resolved_district.code}")
    if resolved_region is not None and region_name is not None and _normalize_key(resolved_region.name) != _normalize_key(region_name):
        issues.append(f"regionName {region_name!r} does not match regionCode {resolved_region.code}")

    if resolved_municipality is not None and resolved_district is not None and resolved_municipality.district_code is not None and resolved_municipality.district_code != resolved_district.code:
        issues.append(
            f"municipalityCode {resolved_municipality.code} belongs to districtCode {resolved_municipality.district_code}, "
            f"but districtCode {resolved_district.code} was resolved"
        )
    if resolved_municipality is not None and resolved_region is not None and resolved_municipality.region_code is not None and resolved_municipality.region_code != resolved_region.code:
        issues.append(
            f"municipalityCode {resolved_municipality.code} belongs to regionCode {resolved_municipality.region_code}, "
            f"but regionCode {resolved_region.code} was resolved"
        )
    if resolved_district is not None and resolved_region is not None and resolved_district.region_code is not None and resolved_district.region_code != resolved_region.code:
        issues.append(
            f"districtCode {resolved_district.code} belongs to regionCode {resolved_district.region_code}, "
            f"but regionCode {resolved_region.code} was resolved"
        )

    if resolved_municipality is None and municipality_name is not None and municipality_code_raw is None:
        issues.append(f"unresolved municipalityName {municipality_name!r}")
    if resolved_district is None and district_name is not None and district_code_raw is None:
        issues.append(f"unresolved districtName {district_name!r}")
    if resolved_region is None and region_name is not None and region_code_raw is None:
        issues.append(f"unresolved regionName {region_name!r}")

    return {
        "municipalityCode": resolved_municipality.code if resolved_municipality is not None else None,
        "districtCode": resolved_district.code if resolved_district is not None else None,
        "regionCode": resolved_region.code if resolved_region is not None else None,
    }, issues


def _normalize_source_record(raw_record: dict[str, Any], geography: GeographyIndex) -> tuple[dict[str, Any], str | None, str | None]:
    psc = _normalize_psc(_pick(raw_record, "psc", "postalcode", "postal_code", "postalCode"))

    delivery_post = _pick(raw_record, "deliveryPost", "delivery post", "delivery_post", "city", "postOffice")
    valid_from = _pick(raw_record, "validFrom", "valid from", "validity_from")
    valid_to = _pick(raw_record, "validTo", "valid to", "validity_to")
    municipality_name = _pick(raw_record, "municipalityName", "municipality", "municipality_name", "obec")
    district_name = _pick(raw_record, "districtName", "district", "district_name", "okres")
    region_name = _pick(raw_record, "regionName", "region", "region_name", "kraj")
    country = _pick(raw_record, "country", "countryName", "stat") or "Slovakia"

    geography_codes, geography_issues = _resolve_record_geography(raw_record, geography)

    resolved_municipality = geography.municipalities_by_code.get(geography_codes["municipalityCode"]) if geography_codes["municipalityCode"] else None
    resolved_district = geography.districts_by_code.get(geography_codes["districtCode"]) if geography_codes["districtCode"] else None
    resolved_region = geography.regions_by_code.get(geography_codes["regionCode"]) if geography_codes["regionCode"] else None

    municipality_text = municipality_name or (resolved_municipality.name if resolved_municipality is not None else None) or delivery_post
    district_text = district_name or (resolved_district.name if resolved_district is not None else None)
    region_text = region_name or (resolved_region.name if resolved_region is not None else None)
    city_text = delivery_post or municipality_text or (resolved_municipality.name if resolved_municipality is not None else None)

    record = {
        "psc": psc,
        "city": city_text,
        "deliveryPost": delivery_post,
        "municipality": municipality_text,
        "municipalityCode": geography_codes["municipalityCode"],
        "district": district_text,
        "districtCode": geography_codes["districtCode"],
        "region": region_text,
        "regionCode": geography_codes["regionCode"],
        "country": country,
        "validFrom": valid_from,
        "validTo": valid_to,
    }

    sort_municipality_name = normalize_whitespace(municipality_name or municipality_text)
    sort_delivery_post = normalize_whitespace(delivery_post or city_text)
    sort_municipality_code = normalize_whitespace(record["municipalityCode"])
    sort_valid_from = normalize_whitespace(valid_from)
    sort_valid_to = normalize_whitespace(valid_to)
    sort_key = (psc, sort_municipality_name, sort_delivery_post, sort_municipality_code, sort_valid_from, sort_valid_to)
    geography_issue = "; ".join(geography_issues) if geography_issues else None
    return record, geography_issue, sort_key


def _load_input_records(input_path: Path, input_format: str) -> list[dict[str, Any]]:
    resolved_input = _resolve_input_file(input_path, input_format)
    return _load_source_records(resolved_input, input_format if input_path.is_file() else resolved_input.suffix.lstrip(".").lower())


def _build_payload(records: list[dict[str, Any]], source: str, geography: GeographyIndex, allow_unresolved_geography: bool) -> tuple[dict[str, Any], list[str], list[str]]:
    grouped_records: dict[str, list[tuple[tuple[str, str, str, str, str, str], dict[str, Any]]]] = {}
    warnings: list[str] = []
    integrity_errors: list[str] = []
    seen_exact_records: set[str] = set()

    for raw_record in records:
        record, geography_issue, sort_key = _normalize_source_record(raw_record, geography)
        psc = record["psc"]

        if source in {"portalvs", "data-gov"} and record.get("municipalityCode") is None:
            warnings.append(f"PSC {psc}: filtered non-Slovak record")
            continue

        record_signature = json.dumps(record, ensure_ascii=False, sort_keys=True)
        if record_signature in seen_exact_records:
            integrity_errors.append(f"Duplicate PSC record {psc}")
            continue
        seen_exact_records.add(record_signature)

        if geography_issue is not None:
            if allow_unresolved_geography:
                warnings.append(f"PSC {psc}: {geography_issue}; nulled municipalityCode, districtCode, regionCode")
                record["municipalityCode"] = None
                record["districtCode"] = None
                record["regionCode"] = None
            else:
                integrity_errors.append(f"PSC {psc}: {geography_issue}")

        grouped_records.setdefault(psc, []).append((sort_key, record))

    for psc_records in grouped_records.values():
        psc_records.sort(key=lambda item: item[0])

    payload: dict[str, Any] = {
        "metadata": {
            "source": source,
            "lastUpdated": today_iso(),
        }
    }
    for psc in sorted(grouped_records):
        matches = [dict(record) for _, record in grouped_records[psc]]
        primary = dict(matches[0])
        primary["matchCount"] = len(matches)
        primary["matches"] = matches
        payload[psc] = primary

    return payload, warnings, integrity_errors


def run_import(
    *,
    input_path: Path,
    output_path: Path,
    input_format: str = "auto",
    source: str = "custom",
    write: bool = False,
    allow_unresolved_geography: bool = False,
) -> ImportResult:
    if input_format not in VALID_FORMATS:
        raise ValueError(f"Unsupported input format: {input_format}")
    if source not in VALID_SOURCES:
        raise ValueError(f"Unsupported source: {source}")

    input_path = input_path.resolve()
    output_path = output_path.resolve()

    geography = _load_geography_index(DEFAULT_DATA_DIR)
    records = _load_input_records(input_path, input_format)
    payload, warnings, integrity_errors = _build_payload(records, source, geography, allow_unresolved_geography)

    with tempfile.TemporaryDirectory(prefix="opensk-psc-") as temp_dir_name:
        stage_dir = Path(temp_dir_name)
        _stage_geography_files(stage_dir, DEFAULT_DATA_DIR)
        stage_path = stage_dir / "psc.json"
        write_json(stage_path, payload)
        validation_report = validate_psc_dataset(stage_path)

        if not validation_report.ok or integrity_errors:
            return ImportResult(
                input_path=input_path,
                output_path=output_path,
                source=source,
                input_format=input_format,
                dry_run=not write,
                validation_report=validation_report,
                warnings=warnings + [f"validation: {issue.path}: {issue.message}" for issue in validation_report.warnings],
                integrity_errors=integrity_errors + [f"validation: {issue.path}: {issue.message}" for issue in validation_report.errors],
            )

        wrote_files: list[Path] = []
        if write:
            destination = output_path if output_path.suffix.lower() == ".json" else output_path / "psc.json"
            backup_existing_file(destination)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(stage_path, destination)
            wrote_files.append(destination)

        return ImportResult(
            input_path=input_path,
            output_path=output_path,
            source=source,
            input_format=input_format,
            dry_run=not write,
            wrote_files=wrote_files,
            validation_report=validation_report,
            warnings=warnings + [f"validation: {issue.path}: {issue.message}" for issue in validation_report.warnings],
        )


def _print_result(result: ImportResult) -> None:
    print(f"source={result.source} format={result.input_format} input={result.input_path} output={result.output_path}")
    if result.validation_report is not None:
        report = result.validation_report
        status = "OK" if report.ok else "FAIL"
        print(f"psc: {status} records={report.record_count} errors={report.error_count} warnings={report.warning_count}")
        for issue in report.errors:
            print(f"- validation: {issue.path}: {issue.message}")
        for issue in report.warnings:
            print(f"- warning: {issue.path}: {issue.message}")

    for warning in result.warnings:
        print(f"- warning: {warning}")

    if result.integrity_errors:
        print("Referential integrity issues:")
        for error in result.integrity_errors:
            print(f"- {error}")

    if result.wrote_files:
        print("Wrote:")
        for path in result.wrote_files:
            print(f"- {path}")
    elif result.dry_run:
        print("Dry run only; no files written.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import PSC data from local CSV or JSON files.")
    parser.add_argument("--input", required=True, type=Path, help="Input file or directory")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_FILE, help="Output file or directory")
    parser.add_argument("--format", choices=VALID_FORMATS, default="auto", help="Input format: csv, json, or auto")
    parser.add_argument("--source", choices=VALID_SOURCES, default="custom", help="Source label stored in dataset metadata")
    parser.add_argument("--dry-run", action="store_true", help="Validate only; do not write files")
    parser.add_argument("--write", action="store_true", help="Write the imported PSC dataset when validation passes")
    parser.add_argument(
        "--allow-unresolved-geography",
        action="store_true",
        help="Allow PSC records with unresolved geography by nulling their geography codes",
    )
    args = parser.parse_args(argv)

    try:
        result = run_import(
            input_path=args.input,
            output_path=args.output,
            input_format=args.format,
            source=args.source,
            write=bool(args.write),
            allow_unresolved_geography=args.allow_unresolved_geography,
        )
    except (OSError, ValueError, FileNotFoundError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    _print_result(result)

    if result.validation_report is None or not result.validation_report.ok or result.integrity_errors:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
