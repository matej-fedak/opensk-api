#!/usr/bin/env python3
"""Offline county/town successor importer. Dry-run by default; never reads PSC sources.

Production writes have fixed destinations, prevalidated staged context, a durable
rollback journal and exception rollback. Run offline with API/readers stopped:
two independent file paths cannot offer simultaneous visibility to live readers.
After a process interruption use --recover-production before restarting readers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.acquire_portalvs_successor import GEOGRAPHY_PROFILE, OPENAPI_URL, URLS, manifest_hash
from scripts.import_utils import validate_datasets_before_write

PRODUCTION_DIR = ROOT / "data"
KINDS = ("districts", "municipalities")
TRANSACTION = ".portalvs-geography-transaction"
SOURCE_NAMES = {"districts": "PortalVS / IS Číselníky — Slovenské okresy",
                "municipalities": "PortalVS / IS Číselníky — Slovenské obce"}
LICENSE = "Source/licence verification pending; PortalVS terms may restrict reuse."
REGIONS = {"1": ("SK010", 8), "2": ("SK021", 7), "3": ("SK022", 9), "4": ("SK023", 7),
           "5": ("SK031", 11), "6": ("SK032", 13), "7": ("SK041", 13), "8": ("SK042", 11)}
SCHEMA = {"sortNumber", "code", "officialTitle", "mediumTitle", "shortTitle", "officialTitleEn", "mediumTitleEn",
          "shortTitleEn", "note", "noteEn", "includes", "includesAlso", "excludes", "info", "additionalInfo",
          "infoEn", "unitOfMeasure", "validFrom"}
REVIEWED_NAMES = {"504173": ("Vozokany (okres (Galanta)", "Vozokany (okres Galanta)"),
                  "504742": ("Radošovce (Skalica)", "Radošovce (okres Skalica)")}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value):
    require(isinstance(value, str) and bool(value.strip()), "missing source-backed name")
    return " ".join(unicodedata.normalize("NFC", value).split())


def serialize(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def utc_stamp(value):
    require(isinstance(value, str) and value.endswith("Z"), "acquisition timestamp must be UTC Z")
    stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(stamp.utcoffset().total_seconds() == 0, "non-UTC acquisition timestamp")
    require(stamp <= datetime.now(timezone.utc), "future acquisition timestamp")
    return stamp


def load_sources(manifest_path, capture_dir):
    manifest = json.loads(Path(manifest_path).read_bytes())
    require(manifest.get("profile") == GEOGRAPHY_PROFILE, "requires geography-only acquisition profile")
    require(manifest.get("manifestSha256") == manifest_hash(manifest), "manifest checksum mismatch")
    require(manifest.get("openApiUrl") == OPENAPI_URL and set(manifest.get("sources", {})) == set(KINDS),
            "requires exactly successor county/town sources; no PSC input")
    end = utc_stamp(manifest["acquiredAt"])
    start = utc_stamp(manifest["startedAt"])
    require(start <= end, "reversed acquisition window")
    directory = Path(capture_dir).resolve()
    require(not directory.is_relative_to(ROOT), "raw captures must remain outside repository")
    result = {}
    for kind in KINDS:
        entry = manifest["sources"][kind]
        require(entry["url"] == URLS[kind] and entry["status"] == 200
                and entry["contentType"].split(";")[0].strip() == "application/json", "unexpected source URL/status/type")
        require(start <= utc_stamp(entry["acquiredAt"]) <= end, "source outside acquisition window")
        require(entry["file"] == kind + ".json", "unreviewed source filename")
        path = (directory / entry["file"]).resolve()
        require(path.parent == directory, "source path escapes capture directory")
        require(0 < entry["bytes"] <= 32 * 1024 * 1024 and path.stat().st_size == entry["bytes"], "source size mismatch")
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == entry["sha256"], "source hash mismatch")
        rows = json.loads(raw)
        require(isinstance(rows, list) and rows and len(rows) == entry["rows"], "source row count mismatch")
        require(all(isinstance(r, dict) for r in rows), "source rows must be objects")
        require(sorted(set().union(*(r.keys() for r in rows))) == entry["schemaKeys"], "manifest schema keys mismatch")
        result[kind] = rows
    return manifest, result


def check_row(row, snapshot_date):
    require(SCHEMA <= set(row) <= SCHEMA | {"validTo"}, "source schema drift; review required")
    require(type(row["sortNumber"]) is int and row["sortNumber"] > 0, "invalid source sortNumber")
    require(all(v is None or isinstance(v, str) for k, v in row.items() if k != "sortNumber"), "invalid source field type")
    require(all(isinstance(row[k], str) for k in ("code", "note", "officialTitle", "mediumTitle", "validFrom")),
            "critical source field missing/null")
    require(date.fromisoformat(row["validFrom"]) <= snapshot_date, "future geography row in current-valid source")
    require(not row.get("validTo") or date.fromisoformat(row["validTo"]) >= snapshot_date,
            "retired row in current-valid source; review required")


def transform(counties, towns, snapshot_date, region_codes):
    districts, by_source, notes = {}, {}, set()
    excluded = {k: 0 for k in KINDS}
    mappings = []
    for row in counties:
        check_row(row, snapshot_date)
        if row["code"] == "SKZZZZ":
            require(row["note"] == "" and text(row["officialTitle"]) == "Zahraničie", "pseudo district evidence conflict")
            excluded["districts"] += 1
            require(excluded["districts"] == 1, "duplicate pseudo district")
            continue
        note = row["note"]
        require(re.fullmatch(r"[1-8][0-9]{2}", note), "unknown statistical district code")
        region, maximum = REGIONS[note[0]]
        ordinal = int(note[1:])
        require(region in region_codes and 1 <= ordinal <= maximum, "unknown district/region")
        require(row["code"] == region + format(ordinal, "X"), "district source code/note mismatch")
        code = region + str(ordinal)
        require(note not in notes and code not in districts and row["code"] not in by_source, "duplicate district identity/code")
        name = text(row["mediumTitle"])
        require(text(row["officialTitle"]) == "Okres " + name and text(row["shortTitle"]) == name,
                "district title evidence mismatch")
        record = {"code": code, "name": name, "regionCode": region, "country": "SK"}
        districts[code] = record
        notes.add(note)
        by_source[row["code"]] = record
        if row["code"] != code:
            mappings.append({"sourceCode": row["code"], "statisticalCode": note, "canonicalCode": code, "name": name})
    regular, ids, composites = [], set(), set()
    for row in towns:
        check_row(row, snapshot_date)
        if row["code"] == "SKZZZZZZZZZZ":
            require(row["note"] == "" and text(row["officialTitle"]) == "Zahraničie", "pseudo town evidence conflict")
            excluded["municipalities"] += 1
            require(excluded["municipalities"] == 1, "duplicate pseudo town")
            continue
        code = row["note"]
        require(re.fullmatch(r"[0-9]{6}", code), "municipality note must be a six-digit statistical ID")
        require(len(row["code"]) == 12 and row["code"].endswith(code), "town composite suffix/note mismatch")
        require(row["code"][:-6] in by_source, "unknown source district prefix")
        require(code not in ids and row["code"] not in composites, "duplicate municipality ID/composite")
        ids.add(code)
        composites.add(row["code"])
        regular.append(row)
    counts = Counter(text(row["officialTitle"]) for row in regular)
    municipalities = []
    for row in regular:
        district = by_source[row["code"][:-6]]
        title = text(row["officialTitle"])
        municipalities.append({"code": row["note"],
            "name": title + (f" (okres {district['name']})" if counts[title] > 1 else ""),
            "regionCode": district["regionCode"], "districtCode": district["code"], "country": "SK"})
    records = {"districts": sorted(districts.values(), key=lambda r: (r["regionCode"], int(r["code"][5:]))),
               "municipalities": sorted(municipalities, key=lambda r: (r["regionCode"], r["districtCode"], r["name"], r["code"]))}
    return records, {"sourceCounts": {"districts": len(counties), "municipalities": len(towns)}, "excludedPseudo": excluded,
                     "reletterings": sorted(mappings, key=lambda r: r["statisticalCode"]),
                     "disambiguatedNames": sum(counts[text(r["officialTitle"])] > 1 for r in regular)}


def differences(previous, current, kind):
    before, after = ({r["code"]: r for r in payload[kind]} for payload in (previous, current))
    return {"oldCount": len(before), "newCount": len(after), "addedIds": sorted(after.keys() - before.keys()),
            "removedIds": sorted(before.keys() - after.keys()),
            "recordChanges": [{"code": c, "before": before[c], "after": after[c]}
                              for c in sorted(before.keys() & after.keys()) if before[c] != after[c]],
            "metadataBefore": previous["metadata"], "metadataAfter": current["metadata"]}


def reviewed_diff(report):
    for kind, expected in (("districts", 79), ("municipalities", 2927)):
        diff = report[kind]
        require(diff["oldCount"] == diff["newCount"] == expected, f"{kind}: coverage drift; STOP for review")
        require(not diff["addedIds"] and not diff["removedIds"], f"{kind}: identity drift; STOP for review")
        for change in diff["recordChanges"]:
            before, after = change["before"], change["after"]
            allowed = REVIEWED_NAMES.get(change["code"]) if kind == "municipalities" else None
            require(allowed and (before["name"], after["name"]) == allowed
                    and dict(before, name=after["name"]) == after, f"{kind}: unreviewed record difference; STOP for review")


def all_reference_errors(stage):
    """Cover named geography references in every surrounding JSON, including PSC matches."""
    lookups = {k: {r["code"]: r for r in json.loads((stage / (k + ".json")).read_bytes())[k]}
               for k in ("regions", *KINDS)}
    errors = []
    def visit(value, label):
        if isinstance(value, list):
            for i, child in enumerate(value):
                visit(child, f"{label}[{i}]")
        elif isinstance(value, dict):
            for field, kind in (("regionCode", "regions"), ("districtCode", "districts"), ("municipalityCode", "municipalities")):
                code = value.get(field)
                if code is not None and code not in lookups[kind]:
                    errors.append(f"{label}: unknown {field} {code}")
            town = lookups["municipalities"].get(value.get("municipalityCode"))
            district = lookups["districts"].get(value.get("districtCode"))
            for expected in (town, district):
                if expected:
                    for field in ("regionCode", "districtCode"):
                        if value.get(field) is not None and field in expected and value[field] != expected[field]:
                            errors.append(f"{label}: conflicting {field}")
            for key, child in value.items():
                visit(child, f"{label}.{key}")
    for path in sorted(stage.glob("*.json")):
        visit(json.loads(path.read_bytes()), path.name)
    return errors


def durable_write(path, raw):
    with path.open("wb") as file:
        file.write(raw)
        file.flush()
        os.fsync(file.fileno())


def recover_production():
    """Explicit offline recovery; validate all backups before restoring any path."""
    journal = PRODUCTION_DIR / TRANSACTION
    state_path = journal / "state.json"
    require(state_path.is_file(), "no prepared transaction; inspect any incomplete staging directory manually")
    state = json.loads(state_path.read_bytes())
    require(state["state"] in {"prepared", "committed"}, "unknown transaction state")
    originals = {k: (journal / (k + ".old")).read_bytes() for k in KINDS}
    require(all(hashlib.sha256(originals[k]).hexdigest() == state["before"][k] for k in KINDS), "recovery backup checksum mismatch")
    if state["state"] == "prepared":
        for kind in KINDS:
            destination = journal / (kind + ".restore")
            durable_write(destination, originals[kind])
            os.replace(destination, PRODUCTION_DIR / (kind + ".json"))
    # Exact, tool-owned directory only, never a broad data-directory removal.
    for child in journal.iterdir():
        child.unlink()
    journal.rmdir()


def replace_pair(payloads, baseline):
    journal = PRODUCTION_DIR / TRANSACTION
    journal.mkdir()  # exclusive lock; never overwrite another import/recovery
    state = {"state": "prepared", "before": {k: hashlib.sha256(baseline[k + ".json"]).hexdigest() for k in KINDS}}
    try:
        for kind in KINDS:
            durable_write(journal / (kind + ".old"), baseline[kind + ".json"])
            durable_write(journal / (kind + ".new"), serialize(payloads[kind]))
        require(all(path.read_bytes() == raw for name, raw in baseline.items()
                    for path in [PRODUCTION_DIR / name]), "production context changed during staging")
        durable_write(journal / "state.json", serialize(state))
        for kind in KINDS:
            os.replace(journal / (kind + ".new"), PRODUCTION_DIR / (kind + ".json"))
        state["state"] = "committed"
        durable_write(journal / "state.next", serialize(state))
        os.replace(journal / "state.next", journal / "state.json")
    except BaseException:
        if (journal / "state.json").exists():
            recover_production()
        else:
            for child in journal.iterdir():
                child.unlink()
            journal.rmdir()
        raise
    recover_production()  # committed journal: cleanup only


def run_import(manifest_path, capture_dir, *, write=False):
    require(not (PRODUCTION_DIR / TRANSACTION).exists(), "pending transaction: stop readers and use --recover-production")
    baseline = {p.name: p.read_bytes() for p in PRODUCTION_DIR.glob("*.json")}
    manifest, sources = load_sources(manifest_path, capture_dir)
    region_codes = {r["code"] for r in json.loads(baseline["regions.json"])["regions"]}
    records, report = transform(sources["districts"], sources["municipalities"],
                                date.fromisoformat(manifest["acquiredAt"][:10]), region_codes)
    payloads = {}
    for kind in KINDS:
        entry = manifest["sources"][kind]
        payloads[kind] = {"metadata": {"source": SOURCE_NAMES[kind], "license": LICENSE,
            "sourceUrl": entry["url"], "downloadedAt": manifest["acquiredAt"],
            "sourceBytes": entry["bytes"], "sourceSha256": entry["sha256"],
            "lastUpdated": manifest["acquiredAt"][:10], "complete": True}, kind: records[kind]}
        report[kind] = differences(json.loads(baseline[kind + ".json"]), payloads[kind], kind)
    reviewed_diff(report)
    with tempfile.TemporaryDirectory(prefix="opensk-successor-geography-") as temp:
        stage = Path(temp)
        for name, raw in baseline.items():
            (stage / name).write_bytes(raw)
        for kind in KINDS:
            (stage / (kind + ".json")).write_bytes(serialize(payloads[kind]))
        validate_datasets_before_write(stage)
        errors = all_reference_errors(stage)
        require(not errors, "cross-dataset geography references failed: " + "; ".join(errors))
    psc = json.loads(baseline["psc.json"])
    report["pscStoredMatchLinks"] = sum(len(v["matches"]) for k, v in psc.items() if k != "metadata")
    report["pscSha256Unchanged"] = hashlib.sha256(baseline["psc.json"]).hexdigest()
    report["dryRun"] = not write
    if write:
        replace_pair(payloads, baseline)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--capture-dir", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--write-production", action="store_true")
    mode.add_argument("--recover-production", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.recover_production:
            require(not args.manifest and not args.capture_dir, "recovery does not consume sources")
            recover_production()
            print("Offline geography transaction recovered/cleaned.")
        else:
            require(args.manifest and args.capture_dir, "--manifest and --capture-dir required")
            report = run_import(args.manifest, args.capture_dir, write=args.write_production)
            sys.stdout.buffer.write(serialize(report))
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f"Successor geography import stopped: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
