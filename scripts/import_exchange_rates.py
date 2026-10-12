#!/usr/bin/env python3
"""Offline, dry-run-first ECB eurofxref (euro reference rates) import prototype.

No network access: inputs are explicitly supplied local file paths previously
downloaded from https://www.ecb.europa.eu/stats/eurofxref/ (see
docs/research/exchange-rates-data-schema.md). Strictly validates the
gesmes/ECB Cube XML envelope. Only --write-preview writes, and only into
data/generated/; production promotion is forbidden (research preview only).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GENERATED_DIR = ROOT / "data" / "generated"
DEFAULT_OUTPUT = GENERATED_DIR / "exchange_rates_preview.json"
MAX_INPUT_BYTES = 32 * 1024 * 1024  # eurofxref-hist.xml was 8_196_871 bytes on 2026-10-11
PROFILE = "ecb-eurofxref"

GESMES_NS = "http://www.gesmes.org/xml/2002-08-01"
ECB_NS = "http://www.ecb.int/vocabulary/2002-08-01/eurofxref"
ENVELOPE = f"{{{GESMES_NS}}}Envelope"
SUBJECT = f"{{{GESMES_NS}}}subject"
SENDER_NAME = f"{{{GESMES_NS}}}Sender/{{{GESMES_NS}}}name"
CUBE = f"{{{ECB_NS}}}Cube"

DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
CURRENCY_RE = re.compile(r"[A-Z]{3}")  # ISO 4217 alpha-3, uppercase
RATE_RE = re.compile(r"[0-9]+(?:\.[0-9]+)?")  # unsigned decimal; real feed uses 0..6 places


def read_source_bytes(path: Path) -> bytes:
    """Bound offline inputs; larger inputs are out of spike scope."""
    with path.open("rb") as source:
        raw = source.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError(f"input exceeds {MAX_INPUT_BYTES} byte spike limit: {path.name}")
    if b"<!DOCTYPE" in raw or b"<!ENTITY" in raw:
        raise ValueError(f"DTD/entity declarations are forbidden: {path.name}")
    return raw


def parse_date(value: str) -> str:
    """Strict ISO-8601 calendar date (YYYY-MM-DD), no time component."""
    if not DATE_RE.fullmatch(value):
        raise ValueError(f"invalid ISO date: {value!r}")
    year, month, day = (int(part) for part in value.split("-"))
    try:
        date(year, month, day)
    except ValueError as exc:
        raise ValueError(f"invalid calendar date: {value!r}") from exc
    return value


def parse_currency(value: str) -> str:
    """ISO-4217 alpha-3 uppercase code; EUR is the implied base and must not appear."""
    if not CURRENCY_RE.fullmatch(value):
        raise ValueError(f"invalid ISO 4217 alpha-3 currency code: {value!r}")
    if value == "EUR":
        raise ValueError("EUR must never be listed; it is the implied base currency")
    return value


def parse_rate(value: str) -> str:
    """Strict positive decimal rate; the exact source lexeme is preserved."""
    if not RATE_RE.fullmatch(value):
        raise ValueError(f"invalid rate lexeme: {value!r}")
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"invalid rate lexeme: {value!r}") from exc
    if number <= 0:
        raise ValueError(f"rate must be positive: {value!r}")
    return value


def parse_eurofxref_xml(raw: bytes, label: str) -> dict[str, dict[str, str]]:
    """Parse one eurofxref document strictly; returns {date: {currency: lexeme}}."""
    try:
        root = ET.fromstring(raw)  # noqa: S314 - DTD/entities rejected in read_source_bytes
    except ET.ParseError as exc:
        raise ValueError(f"{label}: not well-formed XML: {exc}") from exc
    if root.tag != ENVELOPE:
        raise ValueError(f"{label}: root must be gesmes:Envelope, got {root.tag!r}")
    subject = root.find(SUBJECT)
    sender = root.find(SENDER_NAME)
    if subject is None or subject.text != "Reference rates":
        raise ValueError(f"{label}: gesmes:subject must be 'Reference rates'")
    if sender is None or sender.text != "European Central Bank":
        raise ValueError(f"{label}: gesmes:Sender name must be 'European Central Bank'")
    outer = root.findall(CUBE)
    if len(outer) != 1 or set(outer[0].keys()) or not len(outer[0]):
        raise ValueError(f"{label}: expected exactly one empty-attribute outer Cube with date children")
    days: dict[str, dict[str, str]] = {}
    for day_cube in outer[0]:
        if day_cube.tag != CUBE or set(day_cube.keys()) != {"time"}:
            raise ValueError(f"{label}: outer Cube children must be date Cubes with only a time attribute")
        day = parse_date(day_cube.get("time", ""))
        if day in days:
            raise ValueError(f"{label}: duplicate date Cube: {day}")
        rates: dict[str, str] = {}
        for rate_cube in day_cube:
            if rate_cube.tag != CUBE or set(rate_cube.keys()) != {"currency", "rate"}:
                raise ValueError(f"{label}: rate Cubes must have only currency/rate attributes")
            currency = parse_currency(rate_cube.get("currency", ""))
            if currency in rates:
                raise ValueError(f"{label}: duplicate currency {currency} on {day}")
            rates[currency] = parse_rate(rate_cube.get("rate", ""))
        if not rates:
            raise ValueError(f"{label}: date Cube {day} has no rate rows")
        days[day] = rates
    if not days:
        raise ValueError(f"{label}: no date Cubes found")
    return days


def serialize_payload(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def validate_preview_path(path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(GENERATED_DIR.resolve()) or resolved.suffix != ".json":
        raise ValueError("preview output must be a JSON file inside data/generated/; production writes are forbidden")
    return resolved


def parse_source_argument(value: str) -> tuple[Path, str]:
    """--source syntax: local-path=canonical-url (both parts required)."""
    local, sep, url = value.partition("=")
    if not sep or not local.strip() or not re.fullmatch(r"https://[^=\s]+", url):
        raise ValueError(f"--source must be path=https-url, got: {value!r}")
    return Path(local.strip()), url


@dataclass
class ImportResult:
    payload: dict[str, Any] = field(default_factory=dict)
    report: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    wrote_files: list[Path] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def import_exchange_rates(sources: list[tuple[Path, str]], *, retrieved_at: str | None = None,
                          dry_run: bool = True, write_preview: bool = False,
                          output: Path = DEFAULT_OUTPUT) -> ImportResult:
    """Validate offline eurofxref inputs and build a deterministic merged preview."""
    result = ImportResult(report={
        "profile": PROFILE, "baseCurrency": "EUR",
        "directionSemantics": "1 EUR = rate units of the foreign currency",
        "inputs": {}, "merged": {"dates": 0, "rows": 0, "skippedDuplicateRows": 0,
                                 "conflictingDuplicateRows": 0},
        "errors": [], "dryRun": True,
    })
    report = result.report
    try:
        destination = validate_preview_path(output)
        if write_preview and dry_run:
            raise ValueError("write-preview and dry-run are mutually exclusive")
        if not sources:
            raise ValueError("at least one --source path=url input is required")
        if retrieved_at is not None and not re.fullmatch(
                r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:Z|[+-][0-9]{2}:[0-9]{2})", retrieved_at):
            raise ValueError(f"--retrieved-at must be an ISO-8601 timestamp, got: {retrieved_at!r}")
        paths = [path for path, _ in sources]
        if len({path.resolve() for path in paths}) != len(paths):
            raise ValueError("duplicate input paths are not allowed")
        merged: dict[str, dict[str, str]] = {}
        for path, url in sources:
            raw = read_source_bytes(path)
            evidence = {"path": str(path), "sourceUrl": url, "bytes": len(raw),
                        "sha256": hashlib.sha256(raw).hexdigest(), "dates": 0, "rows": 0,
                        "earliestDate": None, "latestDate": None, "currencies": []}
            days = parse_eurofxref_xml(raw, path.name)
            currencies = sorted({currency for rates in days.values() for currency in rates})
            evidence.update({
                "dates": len(days), "rows": sum(len(r) for r in days.values()),
                "earliestDate": min(days), "latestDate": max(days), "currencies": currencies,
            })
            report["inputs"][path.name] = evidence
            for day in sorted(days):
                target = merged.setdefault(day, {})
                for currency, lexeme in days[day].items():
                    if currency in target:
                        if Decimal(target[currency]) != Decimal(lexeme):
                            report["merged"]["conflictingDuplicateRows"] += 1
                            raise ValueError(
                                f"conflicting duplicate {day} {currency}: {target[currency]} vs {lexeme}")
                        report["merged"]["skippedDuplicateRows"] += 1
                        continue
                    target[currency] = lexeme
        if not merged:
            raise ValueError("no exchange-rate rows parsed")
        all_currencies = sorted({currency for rates in merged.values() for currency in rates})
        earliest, latest = min(merged), max(merged)
        report["merged"].update({
            "dates": len(merged), "rows": sum(len(r) for r in merged.values()),
            "earliestDate": earliest, "latestDate": latest, "currencies": all_currencies,
        })
        payload = {
            "profile": PROFILE,
            "status": "unapproved-research-preview",
            "baseCurrency": "EUR",
            "directionSemantics": "1 EUR = rate units of the foreign currency",
            "sources": [
                {"file": evidence["path"], "sourceUrl": evidence["sourceUrl"],
                 "sha256": evidence["sha256"], "bytes": evidence["bytes"],
                 **({"retrievedAt": retrieved_at} if retrieved_at else {}),
                 "dates": evidence["dates"], "rows": evidence["rows"],
                 "earliestDate": evidence["earliestDate"], "latestDate": evidence["latestDate"]}
                for evidence in report["inputs"].values()
            ],
            "dates": [
                {"date": day, "base": "EUR",
                 "rates": {currency: merged[day][currency] for currency in sorted(merged[day])}}
                for day in sorted(merged)
            ],
        }
        preview = serialize_payload(payload)
        report["previewBytes"] = len(preview)
        report["previewSha256"] = hashlib.sha256(preview).hexdigest()
        report["inputBytes"] = sum(evidence["bytes"] for evidence in report["inputs"].values())
        result.payload = payload
        if write_preview:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(preview)
            result.wrote_files.append(destination)
            report["dryRun"] = False
        report["wrotePreview"] = bool(result.wrote_files)
    except (ValueError, OSError, UnicodeError) as exc:
        result.errors.append(str(exc))
        report["errors"] = result.errors
        result.payload = {}
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", action="append", type=parse_source_argument, required=True,
                        metavar="PATH=URL", help="offline input file plus its canonical ECB URL; repeatable")
    parser.add_argument("--retrieved-at", help="UTC retrieval timestamp recorded into preview metadata")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="default: validate/report without writing")
    mode.add_argument("--write-preview", action="store_true", help="explicit unapproved generated preview only")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    result = import_exchange_rates(args.source, retrieved_at=args.retrieved_at,
                                   dry_run=not args.write_preview, write_preview=args.write_preview,
                                   output=args.output)
    report = dict(result.report, ok=result.ok)
    # stdout is a machine-readable report, not the preview dataset.
    sys.stdout.buffer.write(serialize_payload(report))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
