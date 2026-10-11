#!/usr/bin/env python3
"""Offline, dry-run-first NR SR 2023 aggregate import prototype.

No network access, person-level data, or production promotion. Only the
verified 2023 territory/municipality table schemas are accepted.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GENERATED_DIR = ROOT / "data" / "generated"
DEFAULT_OUTPUT = GENERATED_DIR / "elections_nrsr2023_preview.json"
MAX_INPUT_BYTES = 16 * 1024 * 1024


def read_source_bytes(path: Path) -> bytes:
    """Bound offline inputs; giant candidate/preference tables are out of scope."""
    with path.open("rb") as source:
        raw = source.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError(f"input exceeds {MAX_INPUT_BYTES} byte spike limit: {path.name}")
    return raw


def parse_count(value: str) -> int:
    """Parse a nonnegative integer with optional source grouping spaces."""
    text = value.strip()
    if not re.fullmatch(r"(?:[0-9]+|[0-9]{1,3}(?: [0-9]{3})+)", text):
        raise ValueError(f"invalid nonnegative count: {value!r}")
    return int(text.replace(" ", ""))


def parse_percentage(value: str) -> Decimal:
    """The verified 2023 dialect has dot decimals and exactly two places."""
    text = value
    if not re.fullmatch(r"[0-9]+\.[0-9]{2}", text):
        raise ValueError(f"invalid percentage: {value!r}")
    try:
        number = Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"invalid percentage: {value!r}") from exc
    if not 0 <= number <= 100:
        raise ValueError(f"percentage outside 0..100: {value!r}")
    return number


def serialize_payload(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def validate_preview_path(path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(GENERATED_DIR.resolve()) or resolved.suffix != ".json":
        raise ValueError("preview output must be a JSON file inside data/generated/; production writes are forbidden")
    return resolved


def municipality_join_report(records: list[dict[str, Any]], path: Path | None) -> dict[str, Any]:
    """Code-only diagnostic; never enrich output with PortalVS-derived fields.

    Missing current geography does not invalidate election-native records.
    No fuzzy matching or inferred codes are used.
    """
    if path is None or not path.is_file():
        return {"available": False, "sourceRecords": len(records), "reason": "optional reference unavailable"}
    document = json.loads(path.read_text(encoding="utf-8"))
    local: dict[str, dict[str, Any]] = {}
    for record in document["municipalities"]:
        code = record["code"]
        if code in local:
            raise ValueError(f"duplicate municipality reference code: {code}")
        local[code] = record
    matched = 0
    unmatched: list[dict[str, str]] = []
    name_mismatches: list[dict[str, str]] = []
    for record in records:
        code, name = record["municipalityCode"], record["municipalityName"]
        reference = local.get(code)
        if reference is None:
            unmatched.append({"code": code, "name": name})
            continue
        matched += 1
        if " ".join(name.split()) != " ".join(reference["name"].split()):
            name_mismatches.append({"code": code, "sourceName": name, "referenceName": reference["name"]})
    return {
        "available": True,
        "sourceRecords": len(records),
        "matched": matched,
        "unmatched": unmatched,
        "unmatchedCount": len(unmatched),
        "matchRate": round(matched / len(records), 6) if records else None,
        "nameMismatches": name_mismatches,
        "referenceOnlyCodes": sorted(set(local) - {r["municipalityCode"] for r in records}),
    }


@dataclass
class ImportResult:
    payload: dict[str, Any] = field(default_factory=dict)
    report: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    wrote_files: list[Path] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


PROFILE = "nrsr2023-sk-csv"
TERRITORY_HEADERS = (
    "Kód kraja", "Názov kraja", "Kód územného obvodu", "Názov územného obvodu",
    "Kód okresu", "Názov okresu", "Kód obce", "Názov obce", "Počet volebných okrskov",
)
AGGREGATE_HEADERS = (
    "Počet volebných okrskov", "Počet potvrdených okrskových zápisníc",
    "Podiel potvrdených okrskových zápisníc v %", "Počet zapísaných voličov",
    "Počet zúčastnených voličov", "Účasť voličov v %",
    "Počet odovzdaných obálok na hlasovanie", "Podiel odovzdaných obálok v %",
    "Počet platných hlasov spolu", "Podiel platných hlasov spolu v %",
)
RESULT_HEADERS = TERRITORY_HEADERS[:8] + AGGREGATE_HEADERS
PARTY_HEADERS = TERRITORY_HEADERS[:8] + (
    "Číslo politického subjektu", "Názov politického subjektu", "Počet platných hlasov",
    "Podiel platných hlasov v %", "Počet voličov, ktorí využili právo prednostného hlasovania",
    "Podiel voličov, ktorí využili právo prednostného hlasovania v %",
)
NATIONAL_HEADERS = AGGREGATE_HEADERS
NATIVE_FIELDS = (
    "regionCode", "regionName", "territorialCircuitCode", "territorialCircuitName",
    "districtCode", "districtName", "municipalityCode", "municipalityName",
)
AGGREGATE_FIELDS = (
    "precinctCount", "confirmedPrecinctCount", "confirmedPrecinctPercent", "registeredVoters",
    "participatingVoters", "turnoutPercent", "submittedEnvelopes", "submittedEnvelopePercent",
    "validVotes", "validVotePercent",
)
COUNT_FIELDS = tuple(AGGREGATE_FIELDS[i] for i in (0, 1, 3, 4, 6, 8))
MUNICIPALITY_OUTPUT_FIELDS = frozenset(NATIVE_FIELDS + AGGREGATE_FIELDS + ("scope",))
PARTY_OUTPUT_FIELDS = frozenset((
    "municipalityCode", "municipalityName", "scope", "partyNumber", "partyName", "validVotes",
    "partyVotePercent",
))


def read_table(path: Path, headers: tuple[str, ...], label: str,
               report: dict[str, Any]) -> list[list[str]]:
    raw = read_source_bytes(path)
    evidence = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(), "parsedRows": 0}
    report["inputs"][label] = evidence
    if sum(item["bytes"] for item in report["inputs"].values()) > MAX_INPUT_BYTES:
        raise ValueError(f"combined input exceeds {MAX_INPUT_BYTES} byte spike limit")
    if raw.startswith((b"\xef\xbb\xbf", b"\xff\xfe", b"\xfe\xff")):
        raise ValueError(f"{label}: unexpected BOM; only UTF-8 without BOM is accepted")
    text = raw.decode("utf-8", errors="strict")
    if "\r" in text or not text.endswith("\n"):
        raise ValueError(f"{label}: expected LF-terminated records without CR")
    reader = csv.reader(io.StringIO(text, newline=""), delimiter=",", strict=True)
    if tuple(next(reader, [])) != headers:
        raise ValueError(f"{label}: schema/header mismatch for {PROFILE}")
    records = []
    for row in reader:
        if len(row) != len(headers):
            raise ValueError(f"{label}: row {reader.line_num} width {len(row)} != {len(headers)}")
        if any("\n" in cell or "\r" in cell or "\x00" in cell for cell in row):
            raise ValueError(f"{label}: multiline/NUL field at row {reader.line_num}")
        records.append(row)
        evidence["parsedRows"] += 1
    if not records:
        raise ValueError(f"{label}: no data rows")
    return records


def source_count(value: str) -> int:
    # The helper also supports grouping spaces; this explicit profile does not.
    if not re.fullmatch(r"[0-9]+", value):
        raise ValueError(f"invalid ungrouped source count: {value!r}")
    return parse_count(value)


def check_percentage(value: str, numerator: int, denominator: int, field: str) -> None:
    expected = ((Decimal(numerator) * 100 / Decimal(denominator)).quantize(
        Decimal("0.01"), rounding=ROUND_DOWN) if denominator else Decimal("0.00"))
    if parse_percentage(value) != expected:
        raise ValueError(f"{field}: percentage mismatch: {value} != {expected}")


def aggregate_values(values: list[str]) -> dict[str, Any]:
    record = {field: (source_count(value) if field in COUNT_FIELDS else value)
              for field, value in zip(AGGREGATE_FIELDS, values, strict=True)}
    for field in ("confirmedPrecinctPercent", "turnoutPercent", "submittedEnvelopePercent", "validVotePercent"):
        parse_percentage(record[field])
    if not 0 <= record["confirmedPrecinctCount"] <= record["precinctCount"]:
        raise ValueError("confirmed precinct count exceeds configured precinct count")
    if record["precinctCount"] == 0:
        raise ValueError("precinctCount must be positive")
    if not record["validVotes"] <= record["submittedEnvelopes"] <= record["participatingVoters"] <= record["registeredVoters"]:
        raise ValueError("invalid aggregate count relationships")
    for field, numerator, denominator in (
        ("confirmedPrecinctPercent", "confirmedPrecinctCount", "precinctCount"),
        ("turnoutPercent", "participatingVoters", "registeredVoters"),
        ("submittedEnvelopePercent", "submittedEnvelopes", "participatingVoters"),
        ("validVotePercent", "validVotes", "participatingVoters"),
    ):
        check_percentage(record[field], record[numerator], record[denominator], field)
    return record


def native_record(values: list[str]) -> dict[str, str]:
    record = dict(zip(NATIVE_FIELDS, values[:8], strict=True))
    for field, pattern in (("regionCode", r"[1-9]"), ("territorialCircuitCode", r"[0-9]{3}"),
                           ("districtCode", r"[0-9]{3}"), ("municipalityCode", r"[0-9]{6}")):
        if not re.fullmatch(pattern, record[field]):
            raise ValueError(f"invalid native {field}: {record[field]!r}")
    if any(not record[field] or record[field] != record[field].strip()
           for field in NATIVE_FIELDS if field.endswith("Name")):
        raise ValueError("empty or padded native name")
    foreign = record["municipalityCode"] == "599999"
    if foreign:
        if values[:8] != ["9", "Cudzina", "900", "Cudzina", "900", "Cudzina", "599999", "Cudzina"]:
            raise ValueError("foreign 599999 scope must have verified Cudzina parents")
    elif record["regionCode"] == "9" or record["districtCode"] == "900" or record["territorialCircuitCode"] == "900":
        raise ValueError("foreign parent codes require municipality 599999")
    if any(record[field][0] != record["regionCode"] for field in ("districtCode", "territorialCircuitCode")):
        raise ValueError("native parent code region mismatch")
    record["scope"] = "foreign" if foreign else "domestic"
    return record


def totals(records: list[dict[str, Any]]) -> dict[str, int]:
    return {field: sum(record[field] for record in records) for field in COUNT_FIELDS}


def import_elections(territory: Path, results: Path, *, party_results: Path | None = None,
                     national_results: Path | None = None, municipalities: Path | None = None,
                     dry_run: bool = True, write_preview: bool = False,
                     output: Path = DEFAULT_OUTPUT) -> ImportResult:
    """Validate offline election-native inputs; optional references affect report only."""
    result = ImportResult(report={
        "profile": PROFILE, "encoding": "utf-8", "bom": False,
        "delimiter": ",", "newline": "LF", "percentageFormat": "dot decimal, two places, truncated",
        "inputs": {}, "errors": [], "dryRun": True,
    })
    report = result.report
    try:
        destination = validate_preview_path(output)
        if write_preview and dry_run:
            raise ValueError("write-preview and dry-run are mutually exclusive")
        territory_rows = read_table(territory, TERRITORY_HEADERS, "territory", report)
        result_rows = read_table(results, RESULT_HEADERS, "results", report)
        native: dict[str, dict[str, Any]] = {}
        parents: dict[tuple[str, str], tuple[str, ...]] = {}
        for row in territory_rows:
            record = native_record(row)
            record["precinctCount"] = source_count(row[8])
            if not record["precinctCount"]:
                raise ValueError("territory precinctCount must be positive")
            code = record["municipalityCode"]
            if code in native:
                raise ValueError(f"duplicate territory municipality: {code}")
            for level, parent in (("region", (row[1],)), ("territorialCircuit", tuple(row[:4])),
                                  ("district", tuple(row[:6]))):
                key = (level, record[level + "Code"])
                if key in parents and parents[key] != parent:
                    raise ValueError(f"inconsistent native parent names/codes: {key}")
                parents[key] = parent
            native[code] = record
        aggregates: dict[str, dict[str, Any]] = {}
        for row in result_rows:
            record = native_record(row)
            code = record["municipalityCode"]
            if code in aggregates:
                raise ValueError(f"duplicate results municipality: {code}")
            if code not in native:
                raise ValueError(f"orphan results municipality: {code}")
            if any(record[field] != native[code][field] for field in NATIVE_FIELDS):
                raise ValueError(f"native membership/name mismatch for results: {code}")
            record.update(aggregate_values(row[8:]))
            if record["precinctCount"] != native[code]["precinctCount"]:
                raise ValueError(f"territory/result precinct count mismatch: {code}")
            aggregates[code] = record
        if native.keys() != aggregates.keys():
            raise ValueError(f"missing native results memberships: {sorted(native.keys() - aggregates.keys())}")
        ordered = [aggregates[code] for code in sorted(aggregates)]
        full_totals = totals(ordered)
        report["nativeJoins"] = {"territory": len(native), "results": len(aggregates),
                                 "matched": len(aggregates), "missing": 0, "orphan": 0}
        report["totals"] = {"all": full_totals,
                            "domestic": totals([r for r in ordered if r["scope"] == "domestic"]),
                            "foreign": totals([r for r in ordered if r["scope"] == "foreign"])}
        report["unconfirmedMunicipalities"] = [r["municipalityCode"] for r in ordered
                                               if r["confirmedPrecinctCount"] < r["precinctCount"]]
        national = None
        if national_results is not None:
            rows = read_table(national_results, NATIONAL_HEADERS, "nationalResults", report)
            if len(rows) != 1:
                raise ValueError("nationalResults must contain exactly one control row")
            national = aggregate_values(rows[0])
            if any(national[field] != full_totals[field] for field in COUNT_FIELDS):
                raise ValueError("national aggregate control totals mismatch")
        parties = []
        if party_results is not None:
            rows = read_table(party_results, PARTY_HEADERS, "partyResults", report)
            seen: set[tuple[str, str]] = set()
            names: dict[str, str] = {}
            municipal_sums = {code: 0 for code in native}
            party_sums: dict[str, int] = {}
            for row in rows:
                record = native_record(row)
                code = record["municipalityCode"]
                if code not in native:
                    raise ValueError(f"orphan party municipality: {code}")
                if any(record[field] != native[code][field] for field in NATIVE_FIELDS):
                    raise ValueError(f"native membership/name mismatch for party: {code}")
                number, name = row[8:10]
                if not re.fullmatch(r"(?:[1-9]|1[0-9]|2[0-5])", number) or not name or name != name.strip():
                    raise ValueError("invalid 2023 party number/name")
                key = (code, number)
                if key in seen:
                    raise ValueError(f"duplicate party result key: {key}")
                seen.add(key)
                if number in names and names[number] != name:
                    raise ValueError(f"inconsistent party name for number {number}")
                names[number] = name
                votes, preferential = source_count(row[10]), source_count(row[12])
                if not votes or preferential > votes:
                    raise ValueError("party rows must have positive votes and preferential voters <= votes")
                check_percentage(row[11], votes, aggregates[code]["validVotes"], "partyVotePercent")
                check_percentage(row[13], preferential, votes, "preferentialVoterPercent")
                municipal_sums[code] += votes
                party_sums[number] = party_sums.get(number, 0) + votes
                parties.append({"municipalityCode": code, "municipalityName": record["municipalityName"],
                                "scope": record["scope"], "partyNumber": number, "partyName": name,
                                "validVotes": votes, "partyVotePercent": row[11]})
            if any(municipal_sums[code] != aggregates[code]["validVotes"] for code in native):
                raise ValueError("party municipality aggregate totals mismatch")
            parties.sort(key=lambda r: (r["municipalityCode"], int(r["partyNumber"])))
            report["partyResults"] = {"rows": len(parties), "sparsePositiveVotes": True,
                                      "expandedZeros": False, "validVotes": sum(party_sums.values()),
                                      "partyTotals": dict(sorted(party_sums.items(), key=lambda p: int(p[0])))}
        payload = {"profile": PROFILE, "electionId": "NRSR2023", "electionDate": "2023-09-30",
                   "status": "unapproved-research-preview", "inputs": report["inputs"],
                   "municipalities": [r for r in ordered if r["scope"] == "domestic"],
                   "foreignResults": [r for r in ordered if r["scope"] == "foreign"],
                   "partyResults": parties, "nationalControls": national,
                   "totals": full_totals}
        # Privacy boundary: preferences were validated but are never serialized.
        if any(set(r) != MUNICIPALITY_OUTPUT_FIELDS for r in ordered) or any(
                set(r) != PARTY_OUTPUT_FIELDS for r in parties):
            raise ValueError("output field allowlist violation")
        preview = serialize_payload(payload)
        try:
            geography = municipality_join_report(ordered, municipalities)
        except (ValueError, OSError, KeyError, TypeError) as exc:
            # Reference failures are diagnostics, not a dependency of native data.
            geography = {"available": False, "sourceRecords": len(ordered), "error": str(exc)}
        report.update({"previewBytes": len(preview), "previewSha256": hashlib.sha256(preview).hexdigest(),
                       "inputBytes": sum(v["bytes"] for v in report["inputs"].values()),
                       "currentGeography": geography})
        result.payload = payload
        if write_preview:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(preview)
            result.wrote_files.append(destination)
            report["dryRun"] = False
        report["wrotePreview"] = bool(result.wrote_files)
    except (ValueError, OSError, UnicodeError, csv.Error, KeyError, TypeError) as exc:
        result.errors.append(str(exc))
        report["errors"] = result.errors
        result.payload = {}
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--territory", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--party-results", type=Path)
    parser.add_argument("--national-results", type=Path)
    parser.add_argument("--municipalities", type=Path, help="optional current geography diagnostics only")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="default: validate/report without writing")
    mode.add_argument("--write-preview", action="store_true", help="explicit unapproved generated preview only")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    result = import_elections(args.territory, args.results, party_results=args.party_results,
                              national_results=args.national_results, municipalities=args.municipalities,
                              dry_run=not args.write_preview, write_preview=args.write_preview, output=args.output)
    report = dict(result.report, ok=result.ok)
    # stdout is a machine-readable report, not the preview dataset.
    sys.stdout.buffer.write(serialize_payload(report))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
