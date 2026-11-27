#!/usr/bin/env python3
"""Offline LSUJ research only: manual inputs, default dry-run, never promotion.

The generic official attribute vocabulary is documented, but an exact CSV profile
must be reviewed against manually supplied files. No source schema, relationship
or successful replacement is inferred from a catalogue page or synthetic tests.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.import_utils import normalize_whitespace, read_json, write_json_atomic
from scripts.source_safety import read_bounded


SOURCE_PAGE = "https://zber.statistics.sk/metaudaje/ciselniky"
MANIFEST = ROOT / "docs/research/susr-geography-acquisition.json"
GENERATED = ROOT / "data/generated"
DEFAULT_REPORT = GENERATED / "susr-geography-reconciliation.json"
PROFILE = "susr-geography-csv-v1"
CLASSIFIERS = {
    "0024": ("LSUJ1", "Lokálna štatistická územná jednotka 1 – okres", "districts"),
    "0025": ("LSUJ2", "Lokálna štatistická územná jednotka 2 – obec", "municipalities"),
}
# Generic publisher PDF vocabulary, NOT a claim about the uninspected CSV header.
COLUMNS = frozenset((
    "sortNumber", "code", "officialTitle", "mediumTitle", "shortTitle", "officialTitleEn",
    "mediumTitleEn", "shortTitleEn", "note", "noteEn", "includes", "includesAlso",
    "excludes", "info", "additionalInfo", "infoEn", "unitOfMeasure", "validFrom",
    "validTo", "dateCreated", "dateModified",
))
REGION_NAMESPACE = {"1": "SK010", "2": "SK021", "3": "SK022", "4": "SK023",
                    "5": "SK031", "6": "SK032", "7": "SK041", "8": "SK042"}
# Historical aliases are audited outputs only. The formatter does not read these.
COMPATIBILITY = {
    "510": ("SK031A", "SK03110"), "511": ("SK031B", "SK03111"),
    "610": ("SK032A", "SK03210"), "611": ("SK032B", "SK03211"),
    "612": ("SK032C", "SK03212"), "613": ("SK032D", "SK03213"),
    "710": ("SK041A", "SK04110"), "711": ("SK041B", "SK04111"),
    "712": ("SK041C", "SK04112"), "713": ("SK041D", "SK04113"),
    "810": ("SK042A", "SK04210"), "811": ("SK042B", "SK04211"),
}
SPECIAL_CLASSES = {"FOREIGN_PSEUDO", "TECHNICAL", "INACTIVE", "OUT_OF_SCOPE", "MISSING_FROM_OPEN_SK", "OTHER"}
RIGHTS = "RIGHTS_CONFIRMATION_PENDING"
FILE_FIELDS = frozenset((
    "classifierCode", "acronym", "officialName", "sourcePage", "downloadUrl",
    "manuallyAcquired", "manuallyAcquiredAt", "timePrecision", "bytes", "sha256",
    "encoding", "delimiter", "rowCount", "headers", "headerSha256",
    "sourceVersion", "sourceValidity", "metadataDate", "transformationProfile",
))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def header_hash(headers):
    return sha256(json.dumps(headers, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def official_url(value):
    require(isinstance(value, str), "official evidence URL is required")
    parts = urlsplit(value)
    require(parts.scheme == "https" and (parts.hostname == "statistics.sk" or
            (parts.hostname or "").endswith(".statistics.sk")) and not parts.username
            and not parts.password and parts.port in (None, 443), "evidence must use an official ŠÚ SR HTTPS host")


def iso_date(value):
    require(isinstance(value, str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value), "expected ISO date")
    return date.fromisoformat(value)


def acquisition_day(entry):
    value, precision = entry.get("manuallyAcquiredAt"), entry.get("timePrecision")
    require(isinstance(value, str), "actual manual acquisition time is required")
    if precision == "day":
        result = iso_date(value)
    else:
        pattern = r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}"
        require(precision in {"minute", "second"}, "unreviewed acquisition time precision")
        if precision == "second":
            pattern += r":[0-9]{2}"
        require(re.fullmatch(pattern + r"(?:Z|[+-][0-9]{2}:[0-9]{2})", value), "timestamp precision/zone mismatch")
        result = datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    require(result <= date.today(), "future acquisition date")
    return result


def observe_csv(path, *, encoding="utf-8", delimiter=";"):
    """Strict, non-coercing reader; shared read_csv strips values and fixes comma.

    Return all attributes/rows locally. Observation is not manual-origin proof or
    CSV-profile approval; those require the separately reviewed capture manifest.
    """
    require(encoding in {"utf-8", "utf-8-sig"} and delimiter in {";", ","}, "unreviewed encoding/delimiter")
    path = Path(path).resolve()
    require(not path.is_relative_to(ROOT), "raw classifier files must remain outside the repository")
    with path.open("rb") as source:
        raw = read_bounded(source, 16 * 1024 * 1024, "classifier CSV")
    require(bool(raw), "empty classifier CSV")
    if raw.startswith(b"\xef\xbb\xbf"):
        require(encoding == "utf-8-sig", "UTF-8 BOM must be recorded as utf-8-sig")
    else:
        require(encoding == "utf-8", "utf-8-sig requires an observed UTF-8 BOM")
    text = raw.decode(encoding, errors="strict")
    require("\x00" not in text, "NUL byte in classifier CSV")
    reader = csv.reader(io.StringIO(text, newline=""), delimiter=delimiter, strict=True)
    headers = next(reader, [])
    require(len(headers) == len(set(headers)) and {"code", "officialTitle", "validFrom"} <= set(headers)
            and set(headers) <= COLUMNS, "unexpected CSV schema; manual source profile review required")
    rows, seen = [], set()
    for values in reader:
        require(len(values) == len(headers), "unexpected CSV row width")
        row = dict(zip(headers, values))
        require(re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", row["code"]), "invalid/unreviewed official code")
        require(row["code"] not in seen, "duplicate official code")
        require(bool(row["officialTitle"].strip()), "missing required officialTitle")
        start = iso_date(row["validFrom"])
        if row.get("validTo"):
            require(start <= iso_date(row["validTo"]), "reversed source validity")
        seen.add(row["code"])
        rows.append(row)
        require(len(rows) <= 100_000, "classifier row limit exceeded")
    require(bool(rows), "classifier contains no rows")
    metadata = {"bytes": len(raw), "sha256": sha256(raw), "encoding": encoding,
                "delimiter": delimiter, "rowCount": len(rows), "headers": headers,
                "headerSha256": header_hash(headers)}
    return rows, metadata


def district_public_id(official_code):
    """OpenSK compatibility namespace, not proof of authoritative parentage."""
    require(re.fullmatch(r"[1-8][0-9]{2}", official_code) and int(official_code[1:]) > 0,
            "district code cannot be represented by the reviewed OpenSK namespace")
    return REGION_NAMESPACE[official_code[0]] + str(int(official_code[1:]))


def load_capture(manifest, paths):
    require(manifest.get("profile") == "susr-geography-manual-acquisition-v1", "unreviewed acquisition manifest")
    require(manifest.get("sourceProfileStatus") == "REVIEWED_MANUAL_FILES", "manual source schema review required")
    entries = manifest.get("files")
    require(isinstance(entries, list) and len(entries) == 2, "requires exactly two manually supplied classifiers")
    require({entry.get("classifierCode") for entry in entries} == set(CLASSIFIERS), "wrong/duplicate classifier identity")
    sources, observations = {}, {}
    for entry in entries:
        require(set(entry) == FILE_FIELDS, "unexpected/missing acquisition file metadata")
        code = entry["classifierCode"]
        acronym, name, kind = CLASSIFIERS[code]
        require(entry.get("acronym") == acronym and entry.get("officialName") == name
                and entry.get("sourcePage") == SOURCE_PAGE, "classifier identity evidence mismatch")
        require(entry.get("manuallyAcquired") is True, "source must be manually acquired")
        day = acquisition_day(entry)
        if entry.get("downloadUrl") is not None:
            official_url(entry["downloadUrl"])
        require(all(key in entry for key in ("sourceVersion", "sourceValidity", "metadataDate")), "missing version/validity metadata (use null when unknown)")
        require(paths.get(code) is not None and Path(paths[code]).is_file(), "MANUAL_SOURCE_FILES_REQUIRED")
        rows, observed = observe_csv(paths[code], encoding=entry.get("encoding"), delimiter=entry.get("delimiter"))
        require(all(entry.get(key) == value for key, value in observed.items()), "source bytes/schema differ from acquisition manifest")
        profile = entry.get("transformationProfile", {})
        require(profile.get("id") == PROFILE and profile.get("reviewStatus") == "REVIEWED_MANUAL_SOURCE",
                "unreviewed transformation profile")
        require(profile.get("sourceNameField") in {"officialTitle", "mediumTitle", "shortTitle"}
                and profile["sourceNameField"] in observed["headers"], "source name field is absent/unreviewed")
        require(all(row[profile["sourceNameField"]].strip() for row in rows), "missing required source name")
        for role in ("districtRelationship", "regionRelationship"):
            evidence = profile.get(role)
            if evidence is not None:
                require(evidence.get("verified") is True and evidence.get("basis") == "DIRECT_SOURCE_CODE_FIELD"
                        and evidence.get("field") in observed["headers"] and bool(evidence.get("description")),
                        "coded relationship semantics require verified official field evidence")
                official_url(evidence.get("evidenceUrl"))
        for special_code, decision in profile.get("specialRows", {}).items():
            require(special_code in {row["code"] for row in rows} and decision.get("classification") in SPECIAL_CLASSES
                    and decision.get("reviewed") is True and bool(decision.get("reason")), "unreviewed special-row decision")
            fields = decision.get("evidenceFields", [])
            require(isinstance(fields, list) and bool(fields) and set(fields) <= set(observed["headers"]),
                    "special-row classification requires retained source-field evidence")
        sources[kind] = {"rows": sorted(rows, key=lambda row: row["code"]), "profile": profile, "day": day}
        observations[kind] = dict(entry)
    return sources, observations


def region_relationship(row, profile):
    evidence = profile.get("regionRelationship")
    if evidence is None:
        return None, "PORTALVS_ONLY"
    value = row[evidence["field"]]
    if value in REGION_NAMESPACE.values():
        return value, "DIRECT_SUSR"
    require(value in REGION_NAMESPACE, "unknown official region reference")
    return REGION_NAMESPACE[value], "DETERMINISTIC_DERIVATION_FROM_SUSR"


def active(row, day):
    return iso_date(row["validFrom"]) <= day and (not row.get("validTo") or day <= iso_date(row["validTo"]))


def source_only(row, profile, day):
    decision = profile.get("specialRows", {}).get(row["code"])
    if decision:
        return {"code": row["code"], **decision, "sourceAttributes": row}
    if not active(row, day):
        return {"code": row["code"], "classification": "INACTIVE", "reviewed": True,
                "reason": "source validity excludes the acquisition day", "sourceAttributes": row}
    return {"code": row["code"], "classification": "OTHER", "reviewed": False,
            "reason": "source-only record requires explicit classification; no name-based inference", "sourceAttributes": row}


def reconcile(sources, baseline):
    """Code-based comparison. Baseline values never fill candidate fields."""
    current = {kind: {row["code"]: row for row in baseline[kind]} for kind in ("districts", "municipalities")}
    require(all(len(current[kind]) == len(baseline[kind]) for kind in current), "duplicate production baseline code")
    results = {kind: [] for kind in current}
    extras = {kind: [] for kind in current}
    district_candidates = {}
    for row in sorted(sources["districts"]["rows"], key=lambda item: item["code"]):
        source = sources["districts"]
        try:
            public_code = district_public_id(row["code"])
        except ValueError:
            public_code = None
        if public_code not in current["districts"]:
            extras["districts"].append(source_only(row, source["profile"], source["day"]))
            continue
        require(row["code"] not in source["profile"].get("specialRows", {}), "special-row exclusion overlaps current district")
        source_name = row[source["profile"]["sourceNameField"]]
        name = normalize_whitespace(source_name)
        if source["profile"].get("stripDistrictPrefix"):
            require(name.startswith("Okres "), "unexpected official district title prefix")
            name = name.removeprefix("Okres ")
        region, region_class = region_relationship(row, source["profile"])
        candidate = {"code": public_code, "name": name, "regionCode": region, "country": "SK"}
        item = {"officialCode": row["code"], "SOURCE_NAME": source_name,
                "OPEN_SK_DISPLAY_NAME": current["districts"][public_code]["name"],
                "candidate": candidate, "sourceAttributes": row,
                "active": active(row, source["day"]),
                "fieldCategories": {"code": "OPEN_SK_COMPATIBILITY_VALUE", "name": "DIRECT_SUSR" if name == source_name else "DETERMINISTIC_DERIVATION_FROM_SUSR",
                                    "regionCode": region_class, "country": "OPEN_SK_COMPATIBILITY_VALUE"}}
        district_candidates[row["code"]] = item
        results["districts"].append(item)
    municipal_source = sources["municipalities"]
    represented = [row for row in municipal_source["rows"] if row["code"] in current["municipalities"]]
    names = Counter(normalize_whitespace(row[municipal_source["profile"]["sourceNameField"]]) for row in represented)
    for row in sorted(municipal_source["rows"], key=lambda item: item["code"]):
        if row["code"] not in current["municipalities"]:
            extras["municipalities"].append(source_only(row, municipal_source["profile"], municipal_source["day"]))
            continue
        require(re.fullmatch(r"[0-9]{6}", row["code"]), "municipality identity must be the original six-digit official code")
        require(row["code"] not in municipal_source["profile"].get("specialRows", {}), "special-row exclusion overlaps current municipality")
        source_name = row[municipal_source["profile"]["sourceNameField"]]
        name = normalize_whitespace(source_name)
        parent_evidence = municipal_source["profile"].get("districtRelationship")
        parent = None
        if parent_evidence is not None:
            parent = district_candidates.get(row[parent_evidence["field"]])
            require(parent is not None and parent["active"], "municipality references an absent/inactive official district")
        district = parent["candidate"]["code"] if parent else None
        region, region_class = region_relationship(row, municipal_source["profile"])
        if region is None and parent and parent["candidate"]["regionCode"] is not None:
            region, region_class = parent["candidate"]["regionCode"], "DETERMINISTIC_DERIVATION_FROM_SUSR"
        if region is not None and parent and parent["candidate"]["regionCode"] is not None:
            require(region == parent["candidate"]["regionCode"], "conflicting direct and derived region relationships")
        display = name
        if names[name] > 1:
            display = f"{name} (okres {parent['candidate']['name']})" if parent else None
        candidate = {"code": row["code"], "name": display, "districtCode": district, "regionCode": region, "country": "SK"}
        results["municipalities"].append({"officialCode": row["code"], "SOURCE_NAME": source_name,
            "OPEN_SK_DISPLAY_NAME": current["municipalities"][row["code"]]["name"],
            "candidate": candidate, "sourceAttributes": row, "active": active(row, municipal_source["day"]),
            "fieldCategories": {"code": "DIRECT_SUSR", "name": "OPEN_SK_COMPATIBILITY_VALUE" if display != source_name else "DIRECT_SUSR",
                                "districtCode": "DETERMINISTIC_DERIVATION_FROM_SUSR" if parent else "PORTALVS_ONLY",
                                "regionCode": region_class, "country": "OPEN_SK_COMPATIBILITY_VALUE"}})
    report = {"rightsVerdict": RIGHTS, "productionWrites": False, "datasets": {},
              "provenanceBoundary": "Candidate reproduction only; existing production bytes remain PortalVS-derived."}
    conflicts = dependencies = missing = 0
    for kind, items in results.items():
        for item in items:
            before = current[kind][item["candidate"]["code"]]
            item["differences"] = [key for key, value in item["candidate"].items() if value is not None and value != before[key]]
            item["unreproducedFields"] = [key for key, value in item["candidate"].items() if value is None]
            conflicts += len(item["differences"]) + int(not item["active"])
            dependencies += len(item["unreproducedFields"])
        matched = {item["candidate"]["code"] for item in items}
        unmatched = sorted(current[kind].keys() - matched)
        missing += len(unmatched)
        report["datasets"][kind] = {
            "sourceRows": len(sources[kind]["rows"]), "baselineRows": len(current[kind]), "matched": len(matched),
            "unmatchedProductionCodes": unmatched, "sourceOnlyRows": extras[kind],
            "conflicts": sum(bool(item["differences"]) or not item["active"] for item in items),
            "nameOnlyDifferences": sum(item["SOURCE_NAME"] != item["OPEN_SK_DISPLAY_NAME"] for item in items),
            "displayOnlyOpenSKChanges": sum(item["candidate"]["name"] is not None and item["candidate"]["name"] != item["SOURCE_NAME"]
                                          and not item["differences"] for item in items),
            "relationshipDifferences": sum(key in {"districtCode", "regionCode"} for item in items for key in item["differences"]),
            "idDerivationCategories": dict(sorted(Counter(item["fieldCategories"]["code"] for item in items).items())),
            "records": sorted(items, key=lambda item: item["officialCode"]),
        }
        require(len(items) + len(extras[kind]) == len(sources[kind]["rows"]), "source row was lost")
    report["remainingPortalVSOnlyDependencies"] = dependencies + missing
    special_review_missing = any(not item["reviewed"] for rows in extras.values() for item in rows)
    complete = not (conflicts or dependencies or missing or special_review_missing)
    substantial = all(report["datasets"][kind]["matched"] > 0 for kind in current)
    report["technicalVerdict"] = ("SUSR_TECHNICAL_FULL_REPLACEMENT_READY" if complete else
        "SUSR_TECHNICAL_PARTIAL_REPLACEMENT_READY" if substantial else "NO_GO_SUSR_TECHNICAL_REPLACEMENT")
    report["reconciliationStatus"] = "COMPARED"
    if special_review_missing:
        report["technicalVerdict"] = None
        report["reconciliationStatus"] = "SPECIAL_RECORD_REVIEW_REQUIRED"
    report["compatibilityMappings"] = [{"officialCode": code, "historicalAlias": alias,
        "publicCode": public, "reproducedFromOfficialCode": district_public_id(code) == public,
        "sourceRowPresent": code in district_candidates} for code, (alias, public) in sorted(COMPATIBILITY.items())]
    by_code = {item["officialCode"]: item for item in results["municipalities"]}
    report["reviewedPresentationCodes"] = {code: by_code.get(code) for code in ("504173", "504742")}
    groups = {"Bratislava boroughs": {"SK0101", "SK0102", "SK0103", "SK0104", "SK0105"},
              "Košice boroughs": {"SK0422", "SK0423", "SK0424", "SK0425"}}
    report["specialUnitRetention"] = {label: {"baseline": sum(row["districtCode"] in codes for row in baseline["municipalities"]),
        "sourcePresent": sum(code in by_code for code, row in current["municipalities"].items() if row["districtCode"] in codes)} for label, codes in groups.items()}
    report["specialUnitRetention"]["military units"] = {code: code in by_code for code in ("500267", "518581", "518638") if code in current["municipalities"]}
    return report


def run_reconciliation(manifest_path=MANIFEST, *, districts_file=None, municipalities_file=None):
    manifest = read_json(Path(manifest_path))
    require(manifest.get("profile") == "susr-geography-manual-acquisition-v1", "unreviewed acquisition manifest")
    baseline = {kind: read_json(ROOT / "data" / f"{kind}.json")[kind] for kind in ("districts", "municipalities")}
    require(len(baseline["districts"]) == 79 and len(baseline["municipalities"]) == 2927, "production cardinality changed; STOP")
    before = {p.name: sha256(p.read_bytes()) for p in (ROOT / "data").glob("*.json")}
    protected = manifest.get("baseline", {}).get("productionSha256GitLf")
    require(isinstance(protected, dict) and set(protected) == set(before) - {"sources.json"}, "protected baseline inventory required")
    require(all(sha256((ROOT / "data" / name).read_bytes().replace(b"\r\n", b"\n")) == digest
                for name, digest in protected.items()), "protected production hash changed; STOP")
    if manifest.get("acquisitionStatus") != "MANUAL_FILES_SUPPLIED" or not districts_file or not municipalities_file:
        return {"acquisitionStatus": "MANUAL_SOURCE_FILES_REQUIRED", "technicalVerdict": None,
                "rightsVerdict": RIGHTS, "productionWrites": False, "sourceRows": None,
                "districtsReconciled": None, "municipalitiesReconciled": None,
                "remainingPortalVSOnlyDependencies": None,
                "baselineCounts": {kind: len(rows) for kind, rows in baseline.items()},
                "productionSha256": before}
    sources, observations = load_capture(manifest, {"0024": districts_file, "0025": municipalities_file})
    report = reconcile(sources, baseline)
    report.update(acquisitionStatus="MANUAL_FILES_SUPPLIED", sourceFiles=observations, productionSha256=before)
    require(before == {p.name: sha256(p.read_bytes()) for p in (ROOT / "data").glob("*.json")}, "production changed during reconciliation; STOP")
    return report


def write_diagnostics(path, report):
    path = Path(path).resolve()
    expected = ROOT.resolve() / "data" / "generated"
    require(GENERATED.resolve() == expected and path.is_relative_to(expected) and path.suffix == ".json",
            "diagnostics must stay under data/generated/ with a .json suffix; no symlink escape")
    write_json_atomic(path, report)


def inspect_files(paths, *, delimiter):
    """Non-content observations only; do not invent manual times or approval."""
    report = {"acquisitionStatus": "OBSERVATION_ONLY", "sourceProfileStatus": "MANUAL_FILES_AND_SCHEMA_REVIEW_REQUIRED",
              "technicalVerdict": None, "rightsVerdict": RIGHTS, "productionWrites": False, "files": []}
    for code, (acronym, name, _) in CLASSIFIERS.items():
        require(paths.get(code) is not None, "both local CSV paths are required for inspection")
        path = Path(paths[code])
        with path.open("rb") as source:
            encoding = "utf-8-sig" if source.read(3) == b"\xef\xbb\xbf" else "utf-8"
        _, observed = observe_csv(path, encoding=encoding, delimiter=delimiter)
        report["files"].append({"classifierCode": code, "acronym": acronym, "officialName": name,
            "sourcePage": SOURCE_PAGE, "downloadUrl": None, "manuallyAcquired": None,
            "manuallyAcquiredAt": None, "timePrecision": None, **observed,
            "sourceVersion": None, "sourceValidity": None, "metadataDate": None,
            "transformationProfile": {"id": PROFILE, "reviewStatus": "MANUAL_SOURCE_PROFILE_REQUIRED"}})
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--districts-file", type=Path)
    parser.add_argument("--municipalities-file", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--inspect-files", action="store_true", help="Inspect local CSV metadata only; does not approve origin/schema or infer acquisition dates")
    parser.add_argument("--delimiter", choices=(";", ","), default=";", help="Explicit CSV delimiter for inspection only")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Report only (default)")
    mode.add_argument("--write-diagnostics", action="store_true", help="Write ignored diagnostics only, never production")
    args = parser.parse_args(argv)
    try:
        report = (inspect_files({"0024": args.districts_file, "0025": args.municipalities_file}, delimiter=args.delimiter)
                  if args.inspect_files else run_reconciliation(args.manifest, districts_file=args.districts_file, municipalities_file=args.municipalities_file))
        if args.write_diagnostics:
            write_diagnostics(args.output, report)
        print(json.dumps(report, ensure_ascii=True, sort_keys=True, indent=2))
        return 2 if report["technicalVerdict"] is None else int(report["technicalVerdict"] != "SUSR_TECHNICAL_FULL_REPLACEMENT_READY")
    except (OSError, ValueError, csv.Error, UnicodeError) as exc:
        print(f"Reconciliation blocked: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
