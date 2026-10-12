#!/usr/bin/env python3
"""Offline ECB eurofxref (euro reference rates) importer.

No network access: inputs are explicitly supplied local file paths previously
downloaded from https://www.ecb.europa.eu/stats/eurofxref/ (see
docs/research/exchange-rates-data-schema.md). Strictly validates the
gesmes/ECB Cube XML envelope.

Modes (exactly one):
  --dry-run           default; validate and report without writing
  --write-preview     write an unapproved research preview, restricted to
                      data/generated/ (gitignored)
  --write-production  materialize data/exchange_rates.json from the single
                      canonical full-history feed; refuses historical
                      rewrites/removals unless --acknowledge-changes is given

Production output is deterministic, contains no local paths or machine
metadata, and preserves official decimal lexemes as strings. Production
refresh workflow: docs/data-sources.md (Exchange rates).
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
PRODUCTION_OUTPUT = ROOT / "data" / "exchange_rates.json"
PRODUCTION_SOURCE_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.xml"
MAX_INPUT_BYTES = 32 * 1024 * 1024  # eurofxref-hist.xml was 8_197_952 bytes on 2026-10-12
PROFILE = "ecb-eurofxref"
PUBLISHER = "European Central Bank"
RATE_NOTICE = ("ECB reference rates are published for information purposes only; "
               "using them for transaction purposes is strongly discouraged by the ECB.")
DIRECTION_SEMANTICS = "1 EUR = rate units of the foreign currency"

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
        raise ValueError("preview output must be a JSON file inside data/generated/")
    return resolved


def validate_production_path(path: Path) -> Path:
    resolved = path.resolve()
    if resolved != PRODUCTION_OUTPUT.resolve():
        raise ValueError("production output is restricted to data/exchange_rates.json")
    return resolved


def build_production_payload(merged: dict[str, dict[str, str]], *, source_url: str,
                             source_sha256: str) -> dict[str, Any]:
    """Self-describing production artifact; no local paths or machine metadata."""
    earliest, latest = min(merged), max(merged)
    return {
        "metadata": {
            "source": ("European Central Bank — euro foreign exchange reference rates "
                       "(eurofxref full-history feed), materialized offline by OpenSK API; "
                       "XML normalized to JSON, rate values reproduced verbatim"),
            "publisher": PUBLISHER,
            "sourceUrl": source_url,
            "sourceSha256": source_sha256,
            "baseCurrency": "EUR",
            "directionSemantics": DIRECTION_SEMANTICS,
            "notice": RATE_NOTICE,
            "earliestDate": earliest,
            "latestDate": latest,
            "lastUpdated": latest,
            "complete": True,
            "dateCount": len(merged),
            "rateRowCount": sum(len(rates) for rates in merged.values()),
        },
        "dates": [
            {"date": day, "rates": {currency: merged[day][currency] for currency in sorted(merged[day])}}
            for day in sorted(merged)
        ],
    }


def production_refresh_diff(old_payload: dict[str, Any], merged: dict[str, dict[str, str]]) -> dict[str, Any]:
    """Deterministic refresh report; historical corrections are surfaced, not hidden."""
    old_dates = {entry["date"]: entry["rates"] for entry in old_payload.get("dates", [])
                 if isinstance(entry, dict)}
    added = sorted(set(merged) - set(old_dates))
    removed = sorted(set(old_dates) - set(merged))
    changed: list[dict[str, Any]] = []
    for day in sorted(set(merged) & set(old_dates)):
        for currency in sorted(set(merged[day]) | set(old_dates[day])):
            before, after = old_dates[day].get(currency), merged[day].get(currency)
            if before != after:
                changed.append({"date": day, "currency": currency, "from": before, "to": after})
    old_latest = max(old_dates) if old_dates else None
    new_latest = max(merged) if merged else None
    old_currencies = sorted({currency for rates in old_dates.values() for currency in rates})
    new_currencies = sorted({currency for rates in merged.values() for currency in rates})
    return {
        "oldLatestDate": old_latest, "newLatestDate": new_latest,
        "oldDateCount": len(old_dates), "newDateCount": len(merged),
        "addedDates": len(added), "addedDatesSample": added[:10],
        "removedDates": len(removed), "removedDatesSample": removed[:10],
        "historicalChanges": len(changed), "historicalChangesSample": changed[:10],
        "currenciesNewlySeen": sorted(set(new_currencies) - set(old_currencies)),
        "currenciesNoLongerOnLatest": sorted(
            set(old_dates.get(old_latest, {})) - set(merged.get(new_latest, {}))) if old_latest and new_latest else [],
    }


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
                          write_production: bool = False, acknowledge_changes: bool = False,
                          output: Path = DEFAULT_OUTPUT) -> ImportResult:
    """Validate offline eurofxref inputs; preview or production materialization."""
    result = ImportResult(report={
        "profile": PROFILE, "baseCurrency": "EUR",
        "directionSemantics": DIRECTION_SEMANTICS,
        "inputs": {}, "merged": {"dates": 0, "rows": 0, "skippedDuplicateRows": 0,
                                 "conflictingDuplicateRows": 0},
        "errors": [], "dryRun": True,
    })
    report = result.report
    try:
        if sum(bool(mode) for mode in (dry_run, write_preview, write_production)) != 1:
            raise ValueError("exactly one of dry-run / write-preview / write-production is required")
        if not sources:
            raise ValueError("at least one --source path=url input is required")
        if write_production:
            destination = validate_production_path(output)
            if len(sources) != 1 or sources[0][1] != PRODUCTION_SOURCE_URL:
                raise ValueError(
                    f"production mode requires exactly one source with canonical URL {PRODUCTION_SOURCE_URL}")
        else:
            destination = validate_preview_path(output)
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
        report["inputBytes"] = sum(evidence["bytes"] for evidence in report["inputs"].values())
        if write_production:
            source_sha256 = next(iter(report["inputs"].values()))["sha256"]
            payload = build_production_payload(merged, source_url=PRODUCTION_SOURCE_URL,
                                               source_sha256=source_sha256)
            refresh: dict[str, Any] | None = None
            if (existing := PRODUCTION_OUTPUT).is_file():
                try:
                    old_payload = json.loads(existing.read_text(encoding="utf-8"))
                except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                    raise ValueError(f"existing production dataset is unreadable: {exc}") from exc
                refresh = production_refresh_diff(old_payload, merged)
                if (refresh["removedDates"] or refresh["historicalChanges"]) and not acknowledge_changes:
                    raise ValueError(
                        "refresh would rewrite or remove existing history "
                        f"(removedDates={refresh['removedDates']}, "
                        f"historicalChanges={refresh['historicalChanges']}); "
                        "review the report and re-run with --acknowledge-changes to proceed")
            report["refresh"] = refresh
            artifact = serialize_payload(payload)
            report["outputBytes"] = len(artifact)
            report["outputSha256"] = hashlib.sha256(artifact).hexdigest()
            destination.write_bytes(artifact)
            result.wrote_files.append(destination)
            result.payload = payload
        else:
            payload = {
                "profile": PROFILE,
                "status": "unapproved-research-preview",
                "baseCurrency": "EUR",
                "directionSemantics": DIRECTION_SEMANTICS,
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
            result.payload = payload
            if write_preview:
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(preview)
                result.wrote_files.append(destination)
        if result.wrote_files:
            report["dryRun"] = False
        report["wrotePreview"] = write_preview and bool(result.wrote_files)
        report["wroteProduction"] = write_production and bool(result.wrote_files)
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
    mode.add_argument("--write-production", action="store_true",
                      help="materialize data/exchange_rates.json from the canonical full-history feed")
    parser.add_argument("--acknowledge-changes", action="store_true",
                        help="allow production refresh that rewrites/removes existing history (reviewed)")
    parser.add_argument("--output", type=Path, default=None,
                        help="preview output path (must stay inside data/generated/)")
    args = parser.parse_args(argv)
    if args.acknowledge_changes and not args.write_production:
        parser.error("--acknowledge-changes only applies to --write-production")
    if args.write_production and args.output is not None:
        parser.error("--output is not configurable in production mode")
    result = import_exchange_rates(
        args.source, retrieved_at=args.retrieved_at,
        dry_run=not (args.write_preview or args.write_production),
        write_preview=args.write_preview,
        write_production=args.write_production,
        acknowledge_changes=args.acknowledge_changes,
        output=PRODUCTION_OUTPUT if args.write_production else (args.output or DEFAULT_OUTPUT))
    report = dict(result.report, ok=result.ok)
    # stdout is a machine-readable report, not the preview dataset.
    sys.stdout.buffer.write(serialize_payload(report))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
