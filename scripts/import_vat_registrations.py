#!/usr/bin/env python3
"""Offline importer for Finančná správa VAT registration XML exports.

The current source has no reliable natural/legal subject marker. This importer
therefore supports generated research output but refuses direct production
promotion until the privacy gate is approved in a future milestone.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "generated" / "vat_registrations.json"
PRODUCTION_OUTPUT = ROOT / "data" / "vat_registrations.json"
SOURCE_NAME = "Finančná správa SR - Zoznam daňových subjektov registrovaných pre DPH"
SOURCE_FILE_URL = "https://report.financnasprava.sk/ds_dphs.zip"

_ICO_RE = re.compile(r"\d{8}$")
_VAT_ID_RE = re.compile(r"SK[0-9A-Z]{8,12}$")
_DATE_DMY_RE = re.compile(r"(\d{2})\.(\d{2})\.(\d{4})$")

FORBIDDEN_SOURCE_KEYS = {
    "NAZOV_DS",
    "OBEC",
    "PSC",
    "ULICA_CISLO",
    "STAT",
    "firstName",
    "lastName",
    "fullName",
    "personName",
    "residence",
    "privateAddress",
    "street",
    "houseNumber",
    "birthDate",
    "birthNumber",
    "personalNumber",
    "personalEmail",
    "personalPhone",
}


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


@dataclass
class ImportResult:
    input_path: Path
    output_path: Path
    dry_run: bool
    source_record_count: int = 0
    records_inspected: int = 0
    production_eligible_records: int = 0
    natural_persons_excluded: int = 0
    records_without_ico: int = 0
    invalid_icos: int = 0
    invalid_vat_ids: int = 0
    duplicate_icos: int = 0
    duplicate_vat_ids: int = 0
    multiple_registrations_per_ico: int = 0
    malformed_dates: int = 0
    record_count: int = 0
    source_date: str | None = None
    xml_filename: str | None = None
    xml_size_bytes: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    wrote_files: list[Path] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _text(element: ET.Element | None) -> str:
    return " ".join((element.text or "").split()) if element is not None else ""


def _normalize_date(value: str, *, result: ImportResult) -> str | None:
    value = " ".join(value.split())
    if not value:
        return None
    match = _DATE_DMY_RE.fullmatch(value)
    if not match:
        result.malformed_dates += 1
        return None
    day, month, year = match.groups()
    try:
        return date(int(year), int(month), int(day)).isoformat()
    except ValueError:
        result.malformed_dates += 1
        return None


def _source_date(value: str) -> str | None:
    if not re.fullmatch(r"\d{8}", value):
        return None
    day, month, year = value[:2], value[2:4], value[4:]
    try:
        return date(int(year), int(month), int(day)).isoformat()
    except ValueError:
        return None


def _xml_from_input(path: Path) -> tuple[bytes, str]:
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            xml_names = [name for name in archive.namelist() if name.lower().endswith(".xml")]
            if len(xml_names) != 1:
                raise ValueError(f"expected exactly one XML file in ZIP, found {xml_names}")
            name = xml_names[0]
            return archive.read(name), name
    return path.read_bytes(), path.name


def _registration_from_item(item: ET.Element, *, result: ImportResult) -> tuple[str | None, dict[str, Any] | None]:
    ico = _text(item.find("ICO"))
    vat_id = _text(item.find("IC_DPH"))
    registration_type = _text(item.find("DRUH_REG_DPH"))

    if not ico:
        result.records_without_ico += 1
        return None, None
    if not _ICO_RE.fullmatch(ico):
        result.invalid_icos += 1
        return None, None
    if not _VAT_ID_RE.fullmatch(vat_id):
        result.invalid_vat_ids += 1
        return None, None
    if not registration_type:
        result.errors.append(f"record for IČO {ico} has empty registration type")
        return None, None

    return ico, {
        "vatId": vat_id,
        "registrationType": registration_type,
        "registeredOn": _normalize_date(_text(item.find("DATUM_REG")), result=result),
        "vatPayerFrom": _normalize_date(_text(item.find("PLAT_DPH_OD")), result=result),
        "registrationTypeChangedOn": _normalize_date(_text(item.find("DATUM_ZMENY_DRUHU_REG")), result=result),
    }


def normalize_vat_registrations(path: Path, *, output_path: Path = DEFAULT_OUTPUT, write: bool = False) -> tuple[dict[str, Any], ImportResult]:
    result = ImportResult(input_path=path, output_path=output_path, dry_run=not write)
    xml_payload, xml_filename = _xml_from_input(path)
    result.xml_filename = xml_filename
    result.xml_size_bytes = len(xml_payload)

    root = ET.fromstring(xml_payload)
    if root.tag != "ZoznamSubjektovRegistrovanychkDPH":
        raise ValueError(f"unexpected VAT XML root element {root.tag!r}")
    result.source_date = _source_date(_text(root.find("DatumAktualizacieZoznamu")))

    by_ico: dict[str, list[dict[str, Any]]] = defaultdict(list)
    vat_ids: Counter[str] = Counter()
    exact_records: set[str] = set()

    for item in root.findall("./DS_DPHS/ITEM"):
        result.source_record_count += 1
        result.records_inspected += 1
        ico, registration = _registration_from_item(item, result=result)
        if ico is None or registration is None:
            continue
        exact_key = json.dumps({"ico": ico, **registration}, ensure_ascii=False, sort_keys=True)
        if exact_key in exact_records:
            result.warnings.append(f"duplicate exact registration skipped for IČO {ico}")
            continue
        exact_records.add(exact_key)
        by_ico[ico].append(registration)
        vat_ids[registration["vatId"]] += 1

    result.duplicate_icos = sum(1 for registrations in by_ico.values() if len(registrations) > 1)
    result.multiple_registrations_per_ico = result.duplicate_icos
    result.duplicate_vat_ids = sum(1 for count in vat_ids.values() if count > 1)
    result.production_eligible_records = 0
    result.natural_persons_excluded = 0
    result.warnings.append("privacy gate blocked: XML has no reliable natural/legal subject marker, so no records are production-eligible")
    result.record_count = len(by_ico)

    records = [
        {"ico": ico, "registrations": sorted(registrations, key=lambda item: (item["vatId"], item["registrationType"], item["registeredOn"] or ""))}
        for ico, registrations in sorted(by_ico.items())
    ]
    payload = {
        "metadata": {
            "source": SOURCE_NAME,
            "sourceFileUrl": SOURCE_FILE_URL,
            "lastUpdated": result.source_date,
            "coverage": "research-generated; privacy gate blocked production promotion",
            "privacyGate": "PRIVACY_IMPORT_BLOCKED",
        },
        "vatRegistrations": records,
    }

    return payload, result


def run_import(input_path: Path, *, output_path: Path = DEFAULT_OUTPUT, write: bool = False) -> ImportResult:
    result = ImportResult(input_path=input_path, output_path=output_path, dry_run=not write)
    try:
        payload, result = normalize_vat_registrations(input_path, output_path=output_path, write=write)
    except (OSError, ET.ParseError, ValueError, zipfile.BadZipFile) as exc:
        result.errors.append(str(exc))
        return result

    if output_path.resolve() == PRODUCTION_OUTPUT.resolve():
        result.errors.append(
            "Refusing to write data/vat_registrations.json because the VAT privacy gate is blocked; use data/generated/vat_registrations.json"
        )
        return result

    if write:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result.wrote_files.append(output_path)

    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Normalize the official VAT registration XML ZIP into generated JSON.")
    parser.add_argument("source", type=Path, help="Local ds_dphs.zip or ds_dphs.xml path")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Generated JSON output path")
    parser.add_argument("--write", action="store_true", help="Write output; default is dry-run")
    args = parser.parse_args(argv)

    result = run_import(args.source, output_path=args.output, write=args.write)
    print(f"source records: {result.source_record_count}")
    print(f"records inspected: {result.records_inspected}")
    print(f"production eligible records: {result.production_eligible_records}")
    print(f"natural persons excluded: {result.natural_persons_excluded}")
    print(f"records without IČO: {result.records_without_ico}")
    print(f"invalid IČOs: {result.invalid_icos}")
    print(f"invalid VAT IDs: {result.invalid_vat_ids}")
    print(f"duplicate IČOs: {result.duplicate_icos}")
    print(f"duplicate VAT IDs: {result.duplicate_vat_ids}")
    print(f"multiple registrations per IČO: {result.multiple_registrations_per_ico}")
    print(f"malformed dates: {result.malformed_dates}")
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    for error_message in result.errors:
        print(f"ERROR: {error_message}", file=sys.stderr)
    if result.wrote_files:
        print(f"wrote: {', '.join(str(path) for path in result.wrote_files)}")
    elif result.ok:
        print("dry-run only; pass --write to write generated JSON")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
