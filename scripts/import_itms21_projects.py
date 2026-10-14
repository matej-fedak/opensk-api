#!/usr/bin/env python3
"""Offline ITMS21+ EU-funds project-list importer (research prototype).

No network access: inputs are explicitly supplied local JSON captures
previously downloaded from the official ITMS21+ OpenData API
(https://api.itms21.sk/public/v1/, manual "Integračný manuál OPEN DATA
ITMS21+" v1.0, 25.6.2025 - see docs/research/eu-funds-itms21-spike.md).

Modes (exactly one):
  --dry-run        default; validate and report without writing
  --write-preview  write an unapproved research preview, restricted to
                   data/generated/ (gitignored)

There is deliberately NO production-write mode in this milestone
(0.23.6 is a research/source spike; no production EU-funds dataset).

Privacy gate: only explicitly reviewed legal-entity forms may expose a
beneficiary identity. Missing, unreviewed, natural-person or unspecified
forms keep the project facts but redact the beneficiary block and title.
Partner and supplier blocks,
free-text descriptions, addresses, contacts and any natural-person data
are never projected. Money is parsed as Decimal (json parse_float),
serialized as plain decimal strings - never floats.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GENERATED_DIR = ROOT / "data" / "generated"
DEFAULT_OUTPUT = GENERATED_DIR / "itms21_projects_preview.json"
LIST_URL_RE = re.compile(r"https://api\.itms21\.sk/public/v1/projekt(?:\?\S*)?")
DETAIL_URL_RE = re.compile(r"https://api\.itms21\.sk/public/v1/projekt/(?:id|kod)/[^?=]+")
API_BASE = "https://api.itms21.sk/public/v1"
MAX_INPUT_BYTES = 256 * 1024 * 1024  # list capture measured ~2.8 MB / 100 projects
PROFILE = "itms21-projects-research"
LICENCE = (
    "ITMS21+ OpenData API datasets are catalogued by MIRRI SR in the Slovak "
    "national open-data catalogue (data.slovensko.sk) under CC BY "
    "(authors-work, original-database and sui-generis layers), verified "
    "2026-10-14. Attribution: MIRRI SR / ITMS21+; transformed projection, "
    "not an official representation."
)

# Natural-person legal forms from the live /public/v1/pravnaforma catalogue
# (482 entries, captured 2026-10-14): SK/CZ/AT natural persons, sole traders,
# farmers, liberal professions and associations of natural persons without
# legal personality. For these beneficiaries the person block is redacted
# (the project record is kept - dropping it would bias against programmes
# funding individuals). "1009995" is "Nešpecifikovaná právna forma"
# (unspecified legal form) - ambiguous, hence fail-closed redaction.
# Match ONLY on pravnaForma.kod (kodZdroj collides across countries).
NATURAL_PERSON_FORMS = frozenset(
    {
        "100900000",  # Fyzická osoba, občan - nepodnikateľ
        "1009001",  # Samostatne podnikajúca fyzická osoba
        "100901",  # Einzelunternehmen (AT)
        "1009100",  # Fyzická osoba - príležitostne činná
        "1009101",  # Podnikateľ-fyzická osoba-nezapísaný v OR
        "1009102",  # Podnikateľ-fyzická osoba-zapísaný v OR
        "1009103",  # Samostatne hospodáriaci roľník nezapísaný v OR
        "1009104",  # Samostatne hospodáriaci roľník zapísaný v OR
        "1009105",  # Slobodné povolanie-fyzická osoba
        "1009106",  # Slobodné povolanie-fyzická osoba zapísaná v OR
        "1009107",  # Podnikateľ-FO-nezapís. v OR + sam. hosp. roľník
        "1009108",  # Podnikateľ-FO-zapís. v OR + sam. hosp. roľník
        "1009109",  # Podnikateľ-FO-nezapís. v OR + slobodné povolanie
        "1009110",  # Podnikateľ-FO-zapís. v OR + slobodné povolanie
        "1009422",  # Zahraničná fyzická osoba s bydliskom mimo SR
        "1009752",  # Záujmové združenie fyzických osôb bez právnej spôsobilosti
        "1009995",  # Nešpecifikovaná právna forma (fail-closed)
        "1009CZ101", "1009CZ102", "1009CZ104", "1009CZ105",
        "1009CZ106", "1009CZ107", "1009CZ108",  # CZ FO/živnostník/rolník/...
        "1009CZ425",  # Odštěpný závod zahraniční fyzické osoby
    }
)

# Reviewed legal-entity forms actually seen in the 100-project capture.
# This is intentionally not "everything outside the denylist": new/unknown
# forms redact identities until a maintainer reviews the catalogue evidence.
LEGAL_ENTITY_FORMS = frozenset({
    "1009321", "1009921", "1009701", "100910", "1009382", "100906",
    "1009803", "100904", "100909", "1009331", "100913", "1009121",
    "100914", "1009801", "1009751", "1009CZ801", "1009CZ601",
    "1009CZ661", "1009804", "1009CZ325", "1009120", "1009721",
    "1009CZ141", "1009CZ771", "1009CZ331", "1009CZ361", "1009CZ804",
    "1009CZ641",
})

PROJECT_CODE_RE = re.compile(r"[0-9A-Za-z][0-9A-Za-z\-/]{2,40}")
MAX_PAGE = 100_000


def read_source_bytes(path: Path) -> bytes:
    size = path.stat().st_size
    if size > MAX_INPUT_BYTES:
        raise ValueError(f"input exceeds {MAX_INPUT_BYTES} byte spike limit: {path.name}")
    with path.open("rb") as source:
        raw = source.read(size + 1)
    if len(raw) != size:
        raise ValueError(f"input size changed during reading: {path.name}")
    return raw


def reject_nonfinite_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant {value!r}")


def parse_json(raw: bytes, label: str) -> Any:
    try:
        # parse_float=Decimal keeps upstream BigDecimal amounts exact.
        return json.loads(raw.decode("utf-8-sig"), parse_float=Decimal,
                          parse_constant=reject_nonfinite_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label}: not valid UTF-8 JSON: {exc}") from exc


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def require_str(obj: dict, key: str, where: str) -> str:
    value = obj.get(key)
    require(isinstance(value, str) and value.strip(), f"{where}: missing/invalid '{key}'")
    return value


def require_int(obj: dict, key: str, where: str) -> int:
    value = obj.get(key)
    require(isinstance(value, int) and not isinstance(value, bool), f"{where}: missing/invalid '{key}'")
    return value


def require_bool(obj: dict, key: str, where: str) -> bool:
    value = obj.get(key)
    require(isinstance(value, bool), f"{where}: missing/invalid '{key}'")
    return value


def money_string(obj: dict, key: str, where: str, *, mandatory: bool) -> str | None:
    """Project an upstream BigDecimal JSON number as a plain decimal string."""
    value = obj.get(key)
    if value is None:
        if mandatory:
            raise ValueError(f"{where}: missing mandatory money field '{key}'")
        return None
    require(isinstance(value, (int, Decimal)) and not isinstance(value, bool),
            f"{where}: money field '{key}' must be a JSON number")
    amount = value if isinstance(value, Decimal) else Decimal(value)
    require(amount.is_finite() and amount >= 0, f"{where}: invalid amount '{key}'")
    # normalize() applies the ambient Decimal precision and can round. Plain
    # formatting plus lexical zero removal preserves every significant digit.
    text = format(amount, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return "0" if text == "-0" else text


def iso_datetime_from_ms(value: int, where: str, key: str) -> str:
    require(isinstance(value, int) and not isinstance(value, bool),
            f"{where}: invalid timestamp for '{key}'")
    try:
        dt = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(milliseconds=value)
    except (OverflowError, OSError, ValueError) as exc:
        raise ValueError(f"{where}: invalid timestamp for '{key}'") from exc
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + (f".{value % 1000:03d}" if value % 1000 else "") + "Z"


def linked_codelist_name(entry: Any) -> str | None:
    if isinstance(entry, dict) and isinstance(entry.get("nazovSk"), str):
        return entry["nazovSk"]
    return None


def parse_list_page(raw: bytes, label: str) -> tuple[int, list[dict]]:
    page = parse_json(raw, label)
    where = f"{label} (list page)"
    require(isinstance(page, dict), f"{where}: top level must be an object")
    results = page.get("results")
    size = page.get("size")
    require(isinstance(results, list), f"{where}: missing 'results' list")
    require(isinstance(size, int) and not isinstance(size, bool) and 0 <= size <= MAX_PAGE,
            f"{where}: missing/invalid 'size'")
    require(len(results) <= size, f"{where}: results exceed total size")
    offset = require_int(page, "offset", where)
    limit = require_int(page, "limit", where)
    require(offset >= 0 and limit >= -1, f"{where}: invalid pagination metadata")
    require(limit == -1 or len(results) <= limit, f"{where}: results exceed page limit")
    return size, results


def load_detail(raw: bytes, label: str) -> dict:
    detail = parse_json(raw, label)
    where = f"{label} (project detail)"
    require(isinstance(detail, dict) and "results" not in detail, f"{where}: not a detail object")
    require_int(detail, "id", where)
    require_str(detail, "kod", where)
    return detail


def extract_project(row: dict, where: str) -> tuple[dict, dict]:
    """Project one ITMS21+ list-row into the reviewed OpenSK allowlist."""
    require(isinstance(row, dict), f"{where}: row must be an object")
    source_id = require_int(row, "id", where)
    kod = require_str(row, "kod", where)
    require(PROJECT_CODE_RE.fullmatch(kod), f"{where}: invalid project code {kod!r}")
    href = row.get("href")
    require(href == f"/projekt/id/{source_id}", f"{where}: invalid 'href'")
    name = require_str(row, "nazov", where)
    in_implementation = require_bool(row, "vrealizacii", where)
    completed = require_bool(row, "ukonceny", where)
    status_label = row.get("stav")
    require(status_label is None or isinstance(status_label, str), f"{where}: invalid 'stav'")
    updated_at = require_int(row, "updatedAt", where)

    vyzva = row.get("vyzva")
    require(isinstance(vyzva, dict), f"{where}: missing 'vyzva' link")
    call = {"code": require_str(vyzva, "kod", where)}
    if (call_name := linked_codelist_name(vyzva)) is not None:
        call["nameSk"] = call_name
    program = vyzva.get("program")
    require(isinstance(program, dict), f"{where}: missing 'vyzva.program' link")
    programme = {"code": require_str(program, "kod", where)}
    if (programme_name := linked_codelist_name(program)) is not None:
        programme["nameSk"] = programme_name
    if isinstance(program.get("skratka"), str):
        programme["shortName"] = program["skratka"]
    if isinstance(program.get("kodCCI"), str):
        programme["cci"] = program["kodCCI"]

    prijimatel = row.get("prijimatel")
    require(isinstance(prijimatel, dict), f"{where}: missing 'prijimatel'")

    places = row.get("miestoRealizacie")
    require(isinstance(places, list), f"{where}: missing 'miestoRealizacie'")
    regions: list[dict[str, str]] = []
    for entry in places:
        require(isinstance(entry, dict), f"{where}: invalid 'miestoRealizacie' entry")
        code = entry.get("kodZdroj")
        require(isinstance(code, str) and code.strip(), f"{where}: missing NUTS code")
        region: dict[str, str] = {"nuts": code}
        if (region_name := linked_codelist_name(entry)) is not None:
            region["nameSk"] = region_name
        regions.append(region)

    unique = {json.dumps(region, sort_keys=True) for region in regions}
    ordered = sorted((json.loads(region) for region in unique),
                     key=lambda r: (r["nuts"], r.get("nameSk", "")))
    record: dict[str, Any] = {
        "projectCode": kod,
        "sourceId": source_id,
        "name": name,
        "status": {
            "label": status_label,
            "inImplementation": in_implementation,
            "completed": completed,
        },
        "programme": programme,
        "call": call,
        "implementationRegions": ordered,
        "financials": {
            "contractedTotalEur": money_string(row, "celkovaZazmluvnenaSuma", where, mandatory=True),
        },
        "dates": {},
        "sourceUpdatedAt": iso_datetime_from_ms(updated_at, where, "updatedAt"),
        "sourceUrl": f"{API_BASE}{href}",
    }
    if (actual_start := row.get("skutocnaRealizaciaZaciatok")) is not None:
        record["dates"]["actualImplementationStartAt"] = iso_datetime_from_ms(
            actual_start, where, "skutocnaRealizaciaZaciatok")
    if (actual_end := row.get("skutocnaRealizaciaKoniec")) is not None:
        record["dates"]["actualImplementationEndAt"] = iso_datetime_from_ms(
            actual_end, where, "skutocnaRealizaciaKoniec")
    if not record["dates"]:
        del record["dates"]
    return record, prijimatel


def classify_beneficiary(prijimatel: dict, where: str) -> tuple[dict | None, str | None]:
    """Project the beneficiary for legal entities; else redact with reason."""
    pravna_forma = prijimatel.get("pravnaForma")
    if not isinstance(pravna_forma, dict) or not isinstance(pravna_forma.get("kod"), str):
        return None, "unclassifiable-pravnaForma"  # fail-closed: unknown subject type
    form_code = pravna_forma["kod"]
    if form_code in NATURAL_PERSON_FORMS:
        return None, "natural-person-or-unspecified-form"
    if form_code not in LEGAL_ENTITY_FORMS:
        return None, "unreviewed-pravnaForma"
    beneficiary: dict[str, Any] = {"name": require_str(prijimatel, "nazov", where),
                                   "legalForm": {"code": form_code}}
    if (form_name := linked_codelist_name(pravna_forma)) is not None:
        beneficiary["legalForm"]["nameSk"] = form_name
    ico = prijimatel.get("ico")
    if ico is not None:
        require(isinstance(ico, str) and re.fullmatch(r"[0-9]{7,9}", ico) is not None,
                f"{where}: invalid 'ico' {ico!r}")
        beneficiary["ico"] = ico
    return beneficiary, None


def enrich_from_detail(record: dict, detail: dict, where: str) -> None:
    """Add detail-only fields: contracted NFP, provided NFP, planned dates."""
    require(record["sourceId"] == detail["id"], f"{where}: detail/list ID mismatch")
    financials = record["financials"]
    financials["contractedNfpEur"] = money_string(detail, "zazmluvnenaSumaNfp", where, mandatory=True)
    financials["providedNfpEur"] = money_string(detail, "poskytnuteProstriedky", where, mandatory=True)
    dates = record.setdefault("dates", {})
    for key, out_key in (("planovanaRealizaciaZaciatok", "plannedImplementationStartAt"),
                         ("planovanaRealizaciaKoniec", "plannedImplementationEndAt")):
        value = detail.get(key)
        if value is not None:
            dates[out_key] = iso_datetime_from_ms(value, where, key)
    if not dates:
        del record["dates"]


def parse_source_argument(value: str, pattern: re.Pattern, option: str) -> tuple[Path, str]:
    local, sep, url = value.partition("=")
    if not sep or not local.strip() or not pattern.fullmatch(url.strip()):
        raise argparse.ArgumentTypeError(f"{option} must be path={pattern.pattern}, got: {value!r}")
    return Path(local.strip()), url.strip()


def serialize_payload(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def validate_preview_path(path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(GENERATED_DIR.resolve()) or resolved.suffix != ".json":
        raise ValueError("preview output must be a JSON file inside data/generated/")
    return resolved


@dataclass
class ImportResult:
    payload: dict[str, Any] = field(default_factory=dict)
    report: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    wrote_files: list[Path] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def import_itms21_projects(lists: list[tuple[Path, str]], details: list[tuple[Path, str]], *,
                           retrieved_at: str | None = None, dry_run: bool = True,
                           write_preview: bool = False,
                           output: Path = DEFAULT_OUTPUT) -> ImportResult:
    result = ImportResult(report={
        "profile": PROFILE,
        "inputs": {},
        "merged": {"totalRows": 0, "projected": 0, "redactedNaturalPerson": 0,
                   "redactedUnclassified": 0, "redactedRows": []},
        "includedPravnaFormaCodes": {},
        "errors": [], "dryRun": True,
    })
    report = result.report
    try:
        if dry_run == write_preview:
            raise ValueError("exactly one of dry-run / write-preview is required")
        if not lists:
            raise ValueError("at least one --projects list capture is required")
        for path, url in lists:
            require(LIST_URL_RE.fullmatch(url), f"{path.name}: invalid projects source URL")
        for path, url in details:
            require(DETAIL_URL_RE.fullmatch(url), f"{path.name}: invalid detail source URL")
        if retrieved_at is not None and not re.fullmatch(
                r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:Z|[+-][0-9]{2}:[0-9]{2})", retrieved_at):
            raise ValueError(f"--retrieved-at must be an ISO-8601 timestamp, got: {retrieved_at!r}")
        if retrieved_at is not None:
            datetime.fromisoformat(retrieved_at.replace("Z", "+00:00"))

        detail_by_code: dict[str, dict] = {}
        for path, url in details:
            raw = read_source_bytes(path)
            detail = load_detail(raw, path.name)
            kod = detail["kod"]
            require(kod not in detail_by_code, f"duplicate detail for project code {kod!r}")
            detail_by_code[kod] = detail
            require(path.name not in report["inputs"], "duplicate input filename; rename capture for provenance")
            report["inputs"][path.name] = {"role": "detail", "sourceUrl": url, "bytes": len(raw),
                                           "sha256": hashlib.sha256(raw).hexdigest(),
                                           "projectCode": kod}

        rows: dict[str, dict] = {}
        seen_ids: set[int] = set()
        list_sizes: list[int] = []
        for path, url in lists:
            raw = read_source_bytes(path)
            size, page_rows = parse_list_page(raw, path.name)
            list_sizes.append(size)
            require(path.name not in report["inputs"], "duplicate input filename; rename capture for provenance")
            report["inputs"][path.name] = {"role": "list-page", "sourceUrl": url, "bytes": len(raw),
                                           "sha256": hashlib.sha256(raw).hexdigest(),
                                           "rows": len(page_rows), "size": size}
            for row in page_rows:
                where = f"{path.name}"
                record, prijimatel = extract_project(row, where)
                kod = record["projectCode"]
                require(kod not in rows, f"duplicate project code {kod!r} across captures")
                require(record["sourceId"] not in seen_ids, "duplicate project source ID")
                seen_ids.add(record["sourceId"])
                beneficiary, redaction = classify_beneficiary(prijimatel, where)
                if redaction == "natural-person-or-unspecified-form":
                    report["merged"]["redactedNaturalPerson"] += 1
                elif redaction is not None:
                    report["merged"]["redactedUnclassified"] += 1
                if redaction is not None:
                    report["merged"]["redactedRows"].append({"projectCode": kod, "reason": redaction})
                    # A project title can itself contain its applicant's name.
                    # Retain financial/location facts, not that unreviewed text.
                    del record["name"]
                else:
                    form_code = beneficiary["legalForm"]["code"]
                    codes = report["includedPravnaFormaCodes"]
                    codes.setdefault(form_code, 0)
                    codes[form_code] += 1
                    record["beneficiary"] = beneficiary
                if kod in detail_by_code:
                    enrich_from_detail(record, detail_by_code[kod], f"detail {kod}")
                rows[kod] = record
                report["merged"]["projected"] += 1
            report["merged"]["totalRows"] += len(page_rows)

        require(len(set(list_sizes)) <= 1, "list sizes vary between captures; review snapshot consistency")
        require(not set(detail_by_code) - set(rows), "detail has no matching list project")
        require(rows, "no project rows projected")

        payload = {
            "profile": PROFILE,
            "status": "unapproved-research-preview",
            "licence": LICENCE,
            "sources": [
                {"file": str(path), "sourceUrl": url, "role": report["inputs"][path.name]["role"],
                 "sha256": report["inputs"][path.name]["sha256"],
                 "bytes": report["inputs"][path.name]["bytes"],
                 **({"retrievedAt": retrieved_at} if retrieved_at else {})}
                for path, url in sorted([*lists, *details], key=lambda source: (source[1], str(source[0])))
            ],
            "privacy": {
                "naturalPersonBeneficiariesRedacted": True,
                "denylist": sorted(NATURAL_PERSON_FORMS),
                "reviewedLegalEntityForms": sorted(LEGAL_ENTITY_FORMS),
                "redactedNaturalPerson": report["merged"]["redactedNaturalPerson"],
                "redactedUnclassified": report["merged"]["redactedUnclassified"],
                "projection": "beneficiary name/IČO/legal-form only for classifiable legal "
                              "entities; beneficiary block and project title redacted otherwise; no addresses, "
                              "contacts, partners, suppliers, free-text descriptions or "
                              "natural-person data",
            },
            "counts": {
                "inputRows": report["merged"]["totalRows"],
                "projects": report["merged"]["projected"],
                "redactedBeneficiaries": report["merged"]["redactedNaturalPerson"]
                                         + report["merged"]["redactedUnclassified"],
            },
            "projects": [rows[kod] for kod in sorted(rows)],
        }
        preview = serialize_payload(payload)
        report["previewBytes"] = len(preview)
        report["previewSha256"] = hashlib.sha256(preview).hexdigest()
        result.payload = payload
        if write_preview:
            destination = validate_preview_path(output)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(preview)
            result.wrote_files.append(destination)
        if result.wrote_files:
            report["dryRun"] = False
        report["wrotePreview"] = write_preview and bool(result.wrote_files)
    except (ValueError, OSError, UnicodeError) as exc:
        result.errors.append(str(exc))
        report["errors"] = result.errors
        result.payload = {}
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--projects", action="append", required=True, metavar="PATH=URL",
                        type=lambda v: parse_source_argument(v, LIST_URL_RE, "--projects"),
                        help="offline /public/v1/projekt list-page capture plus its canonical URL; repeatable")
    parser.add_argument("--detail", action="append", default=[], metavar="PATH=URL",
                        type=lambda v: parse_source_argument(v, DETAIL_URL_RE, "--detail"),
                        help="optional offline project-detail capture (id/kod URL); repeatable")
    parser.add_argument("--retrieved-at", help="UTC retrieval timestamp recorded into preview metadata")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="default: validate/report without writing")
    mode.add_argument("--write-preview", action="store_true", help="explicit unapproved generated preview only")
    parser.add_argument("--output", type=Path, default=None,
                        help="preview output path (must stay inside data/generated/)")
    args = parser.parse_args(argv)
    result = import_itms21_projects(
        args.projects, args.detail, retrieved_at=args.retrieved_at,
        dry_run=not args.write_preview, write_preview=args.write_preview,
        output=args.output or DEFAULT_OUTPUT)
    report = dict(result.report, ok=result.ok)
    # stdout is a machine-readable report, not the preview dataset.
    sys.stdout.buffer.write(serialize_payload(report))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
