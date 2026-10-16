#!/usr/bin/env python3
"""RESEARCH ONLY: offline PSC -> explicit administrative-parent evidence.

No network, fuzzy matching, postcode/delivery-post inference or production writer.
REGPJ paths are snapshot-qualified: absence of validity fields is NOT currentness.
Street names/identifiers and house-number cells never enter output reports.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import unicodedata
import zipfile
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analyze_portalvs_psc_successor import (
    POST_REGIONS, analyze_sources, geography_prototypes, load_capture, read_post_workbook,
)

HEADERS = ["RSUJ2", "NAZRSUJ2", "RSUJ3", "KRJ", "NAZKRJ = NAZRSUJ3", "OKS", "LSUJ1",
           "NAZOKS = NAZLSUJ1", "LSUJ2", "ICZUJ", "NAZZUJ = NAZLSUJ2", "ICUTJ", "NAZUTJ", "ICZSJ", "NAZZSJ"]
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
STATES = ("AUTHORITATIVE_DETERMINISTIC", "AUTHORITATIVE_BUT_AMBIGUOUS", "SEMANTICALLY_INSUFFICIENT", "NO_MATCH", "SOURCE_CONFLICT")
REGPJ_MEMBERS = {"REGPJ2020.xlsx", "REGPJ2020.ods"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def normalize(value):
    """NFC, case/whitespace, reviewed dash variants/spacing ONLY. Keep word boundaries."""
    require(isinstance(value, str), "expected textual label")
    value = unicodedata.normalize("NFC", value).casefold().translate(str.maketrans({"–": "-", "—": "-", "‑": "-"}))
    return re.sub(r"\s*-\s*", "-", " ".join(value.split()))


def serialized(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def archive(raw):
    require(len(raw) <= 32 * 1024 * 1024, "archive exceeds bounded research size")
    z = zipfile.ZipFile(io.BytesIO(raw))
    require(len(z.namelist()) == len(set(z.namelist())), "duplicate archive members")
    require(all(i.file_size <= 32 * 1024 * 1024 for i in z.infolist()), "oversize archive member")
    return z


def workbook(raw, *, allow_cached_formulas=False):
    """Read XML cached scalar cells, never workbook author properties or external links."""
    z = archive(raw)
    require(not any(n.startswith("xl/externalLinks/") for n in z.namelist()), "external workbook links unreviewed")
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        shared = ["".join(si.itertext()) for si in ET.fromstring(z.read("xl/sharedStrings.xml"))]
    rels = {r.attrib["Id"]: r.attrib["Target"] for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    result = {}
    for sheet in ET.fromstring(z.read("xl/workbook.xml")).find("s:sheets", NS):
        rid = sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        target = rels[rid]
        require(".." not in target and not target.startswith(("http:", "https:")), "invalid workbook target")
        target = target.lstrip("/") if target.startswith("/") else "xl/" + target
        rows = []
        for source_row in ET.fromstring(z.read(target)).findall("s:sheetData/s:row", NS):
            cells = {}
            for c in source_row:
                value = c.find("s:v", NS)
                require(c.find("s:f", NS) is None or (allow_cached_formulas and value is not None),
                        "formula cells require reviewed cached values")
                if value is not None:
                    text = shared[int(value.text)] if c.get("t") == "s" else value.text or ""
                elif c.get("t") == "inlineStr":
                    text = "".join(c.find("s:is", NS).itertext())
                else:
                    continue
                column = re.sub(r"[0-9]", "", c.attrib["r"])
                require(column not in cells, "duplicate worksheet cell")
                cells[column] = text
            if cells:
                rows.append((int(source_row.attrib["r"]), cells))
        require(sheet.attrib["name"] not in result, "duplicate sheet name")
        result[sheet.attrib["name"]] = rows
    return result


def parse_regpj(path, municipalities, county_by_note, region_codes, source_district_codes=None):
    raw = Path(path).read_bytes()
    outer = archive(raw)
    require(set(outer.namelist()) == REGPJ_MEMBERS, "unreviewed REGPJ archive members")
    sheets = workbook(outer.read("REGPJ2020.xlsx"))
    require(set(sheets) == {"REGPJ"}, "unreviewed REGPJ sheets")
    rows = sheets["REGPJ"]
    require([rows[0][1].get(chr(65 + i)) for i in range(15)] == HEADERS, "REGPJ header/schema drift")
    columns = [chr(65 + i) for i in range(15)]
    require(set(rows[0][1]) == set(columns), "unreviewed REGPJ header columns/validity profile")
    admins, utj, unit_paths, seen = {}, {}, {}, set()
    duplicate_rows = 0
    zsj_names, zsj_parents, utj_parents = defaultdict(set), defaultdict(set), defaultdict(set)
    for line, cells in rows[1:]:
        require(set(cells) == set(columns) and all(cells[c] for c in columns), "REGPJ row shape drift")
        values = tuple(cells[c] for c in columns)
        # The official file repeats 28 identical relationship rows. Preserve
        # provenance rows but never count them as independent identities.
        duplicate_rows += values in seen
        seen.add(values)
        admin, note, region = cells["J"], cells["F"], cells["C"]
        require(re.fullmatch(r"[0-9]{6}", admin) and admin in municipalities, "unknown REGPJ administrative ID")
        require(note in county_by_note and region in region_codes, "unknown REGPJ district/region reference")
        district = county_by_note[note]
        require(district["regionCode"] == region and municipalities[admin]["districtCode"] == district["code"]
                and municipalities[admin]["regionCode"] == region, "REGPJ/OpenSK administrative relationship conflict")
        # Both are explicitly supplied columns, not a guessed code-prefix parent.
        require(cells["I"] == cells["G"] + admin, "REGPJ composite/ICZUJ conflict")
        if source_district_codes is not None:
            require(cells["G"] == source_district_codes[note], "REGPJ/successor district code conflict")
        identity = (cells["I"], cells["K"], note, region, cells["G"])
        require(admin not in admins or admins[admin] == identity, "conflicting duplicate administrative identity")
        admins[admin] = identity
        require(re.fullmatch(r"[0-9]{6}", cells["L"]), "invalid ICUTJ")
        require(re.fullmatch(r"[0-9]{5}", cells["N"]), "unreviewed ICZSJ representation")
        cadastre = (cells["M"], admin)
        require(cells["L"] not in utj or utj[cells["L"]] == cadastre, "conflicting cadastral parent/identity")
        utj[cells["L"]] = cadastre
        zsj_names[cells["N"]].add(cells["O"])
        zsj_parents[cells["N"]].add(admin)
        utj_parents[cells["L"]].add(admin)
        for kind, code, name in (("LSUJ2", admin, cells["K"]), ("UTJ", cells["L"], cells["M"]), ("ZSJ", cells["N"], cells["O"])):
            key = (kind, code, name, admin, note, region)
            unit_paths.setdefault(key, []).append(line)
    units = [{"unitType": k[0], "unitCode": k[1], "unitName": k[2], "parentCode": k[3],
              "parentName": municipalities[k[3]]["name"],
              "districtStatisticalCode": k[4], "regionCode": k[5], "sourceRows": sorted(lines),
              "validFrom": None, "validTo": None, "temporalStatus": "SNAPSHOT_VALIDITY_UNKNOWN"}
             for k, lines in sorted(unit_paths.items())]
    summary = {"dataRows": len(rows) - 1, "uniqueRelationshipRows": len(seen), "duplicateRelationshipRows": duplicate_rows,
        "sheet": "REGPJ", "headers": HEADERS, "encoding": "UTF-8 XML inside XLSX",
        "administrativeIds": len(admins), "matchedOpenSkIds": len(set(admins) & set(municipalities)),
        "missingOpenSkIds": sorted(set(municipalities) - set(admins)), "extraIds": sorted(set(admins) - set(municipalities)),
        "cadastralIds": len(utj), "zsjIds": len(zsj_parents),
        "zsjIdsWithMultipleAdministrativeParents": sum(len(v) > 1 for v in zsj_parents.values()),
        "zsjIdsWithMultipleNames": {k: sorted(v) for k, v in sorted(zsj_names.items()) if len(v) > 1},
        "cadastralIdsWithMultipleParents": sum(len(v) > 1 for v in utj_parents.values()),
        "validityFields": [], "dataAsOf": None, "streetFields": [],
        "bratislavaBoroughs": sum(v[2] in {"101", "102", "103", "104", "105"} for v in admins.values()),
        "kosiceBoroughs": sum(v[2] in {"802", "803", "804", "805"} for v in admins.values()),
        "militaryUnits": [{"code": k, "name": v[1], "district": v[2]} for k, v in sorted(admins.items()) if "vojenský obvod" in v[1]]}
    return units, summary


def inspect_post_profile(path, district_names):
    """Reviewed columns only; never emit street/house-number or author cells."""
    outer = archive(Path(path).read_bytes())
    require(set(outer.namelist()) == {"OBCE.xlsx", "ULICE.xlsx", "POBoxy.xlsx"}, "unreviewed postal archive members")
    sheets = workbook(outer.read("OBCE.xlsx"), allow_cached_formulas=True)
    require(set(sheets) == {"obce", "detail SČ", "popis", "miestne časti"}, "postal sheet drift")
    require(sheets["obce"][0][1] == dict(zip("ABCDEFGH", ("DOBEC", "OBEC", "OKRES", "PSC", "DPOSTA", "POSTA", "KOD_OKR", "KRAJ"))),
            "postal basic schema drift")
    require(sheets["detail SČ"][1][1] == dict(zip("ABCDEFGH", ("OBEC", "OKRES", "KOD_OKR", "KRAJ", "PSC", "POSTA", "miestne pomenovanie", "Súpisné čísla"))),
            "postal detail schema drift")
    require(sheets["miestne časti"][1][1] == dict(zip("ABCDE", ("kraj", "Okres", "Názov Obce", "Názov Miestnej časti", "Typ"))),
            "postal part schema drift")
    expected = {note: name for name, note in district_names.items()}
    conflicts = []
    for sheet, label_col, name_col, code_col in (("obce", "B", "C", "G"), ("detail SČ", "A", "B", "C")):
        for number, cells in sheets[sheet]:
            code = cells.get(code_col)
            if code in expected and normalize(cells.get(name_col, "")) != expected[code]:
                conflicts.append({"sheet": sheet, "row": number, "postalLocality": cells[label_col],
                                  "districtLabel": cells.get(name_col), "districtCode": code})
    return {"sheets": sorted(sheets), "worksheetRows": {k: len(v) for k, v in sorted(sheets.items())},
            "districtLabelDifferences": conflicts,
            "districtLabelPolicy": "Full-label differences only, not proof of wrong codes; no abbreviation expansion or label override",
            "formulaPolicy": "OBCE cached values read only; workbook never recalculated or rewritten"}


def active(unit, as_of):
    if unit.get("current") is False:
        return False
    return not ((unit.get("validFrom") and date.fromisoformat(unit["validFrom"]) > as_of)
                or (unit.get("validTo") and date.fromisoformat(unit["validTo"]) < as_of))


def index_units(units, as_of):
    index = defaultdict(list)
    for unit in sorted(units, key=lambda u: (u["unitType"], u["unitCode"], u["parentCode"], u["unitName"])):
        require(isinstance(unit.get("parentCode"), str) and re.fullmatch(r"[0-9]{6}", unit["parentCode"]),
                "unit has no explicit administrative parent")
        if active(unit, as_of):
            index[normalize(unit["unitName"])].append(unit)
    return index


def exact_paths(label, row, index, *, admin_only=False):
    region = row.get("kraj")
    require(not region or region in POST_REGIONS, "unreviewed postal region context")
    return [u for u in index.get(normalize(label), [])
            if (not admin_only or u["unitType"] == "LSUJ2")
            and (not row.get("kodOkresu") or row["kodOkresu"] == u["districtStatisticalCode"])
            and (not region or POST_REGIONS[region] == u["regionCode"])]


def map_assignment(row, index, parts, district_names):
    """Return every supported parent; never select first or treat a post as parent."""
    if normalize(row["obce"]) in {"bratislava", "košice"}:
        return {"state": "SEMANTICALLY_INSUFFICIENT", "classification": "AGGREGATE_CITY_REQUIRES_CHILD_CONTEXT",
                "municipalityCodes": [], "evidence": []}
    direct = exact_paths(row["obce"], row, index)
    chained = []
    for part in parts:
        if normalize(part["locality"]) != normalize(row["obce"]):
            continue
        district = district_names.get(normalize(part["districtName"]))
        if district is None or (row.get("kodOkresu") and row["kodOkresu"] != district):
            continue
        context = dict(row, kodOkresu=district)
        for parent in exact_paths(part["municipality"], context, index, admin_only=True):
            chained.append({"publisherPartRow": part["row"], "publisherPart": part["locality"],
                            "publisherParent": part["municipality"], "regpj": parent})
    a, b = {u["parentCode"] for u in direct}, {e["regpj"]["parentCode"] for e in chained}
    codes = sorted(a | b)
    evidence = [{"path": "REGPJ_EXACT_UNIT_PARENT", "regpj": u} for u in direct]
    evidence += [dict(e, path="POST_LOCAL_PART_REGPJ_ADMIN") for e in chained]
    evidence.sort(key=lambda e: json.dumps(e, ensure_ascii=False, sort_keys=True))
    if a and b and a.isdisjoint(b):
        state, classification = "SOURCE_CONFLICT", "EXACT_EVIDENCE_PATHS_DISAGREE"
    elif len(codes) > 1:
        state, classification = "AUTHORITATIVE_BUT_AMBIGUOUS", "MULTIPLE_EXPLICIT_PARENTS"
    elif not codes:
        state, classification = "NO_MATCH", "NO_EXACT_UNIT_WITH_PARENT_IN_CONTEXT"
    else:
        state = "AUTHORITATIVE_DETERMINISTIC"
        kinds = {u["unitType"] for u in direct}
        classification = ("REGPJ_DIRECT_ADMIN" if "LSUJ2" in kinds else "REGPJ_ZSJ_PARENT" if "ZSJ" in kinds
                          else "REGPJ_CADASTRAL_PARENT" if "UTJ" in kinds else "POST_PART_REGPJ_PARENT")
    return {"state": state, "classification": classification, "municipalityCodes": codes, "evidence": evidence}


def coverage(rows, results):
    grouped = defaultdict(list)
    for row, result in zip(rows, results):
        grouped[row["psc"]].append((row, result))
    report = []
    for postal, group in sorted(grouped.items()):
        states = Counter(result["state"] for _, result in group)
        known = {c for _, result in group if result["state"] == "AUTHORITATIVE_DETERMINISTIC" for c in result["municipalityCodes"]}
        mapped = states["AUTHORITATIVE_DETERMINISTIC"]
        status = "COMPLETE" if mapped == len(group) else "PARTIAL" if mapped else "NO_MAPPING"
        report.append({"psc": postal, "sourceRows": len(group), "states": dict(sorted(states.items())),
            "status": status, "mappedRows": mapped, "unresolvedRows": len(group) - mapped,
            "municipalityCodes": sorted(known), "multiMunicipality": len(known) > 1,
            "sourceTypes": dict(sorted(Counter(r["typZaznamu"] for r, _ in group).items())),
            "postalLocalities": sorted({r["obce"] for r, _ in group}),
            "distinctPostalLocalityCount": len({r["obce"] for r, _ in group}),
            "distinctDeliveryPosts": len({r["dposta"] for r, _ in group if r.get("dposta")}),
            "sourceRegions": sorted({r["kraj"] for r, _ in group if r.get("kraj")}),
            "distinctSourceRegionCount": len({r["kraj"] for r, _ in group if r.get("kraj")}),
            "missingRegionRows": sum(not r.get("kraj") for r, _ in group),
            "missingDistrictRows": sum(not r.get("kodOkresu") for r, _ in group),
            "addressScoped": any(r["typZaznamu"] in {"ulica", "detail_sc"} for r, _ in group)})
    return report


def verify_resource(path, entry):
    raw = Path(path).read_bytes()
    require(len(raw) == entry["bytes"] and hashlib.sha256(raw).hexdigest() == entry["sha256"], "evidence resource hash/size mismatch")


def analyze(portalvs_manifest, portalvs_capture, regpj_zip, post_zip, evidence_manifest, data_dir=ROOT / "data"):
    require(Path(portalvs_manifest).resolve().parent == Path(portalvs_capture).resolve(), "manifest must accompany explicit capture directory")
    evidence = json.loads(Path(evidence_manifest).read_bytes())
    require(evidence.get("profile") == "psc-administrative-evidence-v1", "unreviewed evidence manifest")
    verify_resource(regpj_zip, evidence["resources"]["regpj"])
    verify_resource(post_zip, evidence["resources"]["post"])
    manifest, sources = load_capture(portalvs_manifest)
    require(manifest["manifestSha256"] == evidence["portalvsManifestSha256"], "different PortalVS acquisition requires review")
    post = read_post_workbook(post_zip)
    # This intentionally reuses the OLD normalization only to reproduce history,
    # not to approve or enrich mappings in this stricter evidence model.
    baseline = analyze_sources(sources, snapshot_date=manifest["acquiredAt"][:10], post=post)
    baseline_pairs = {(r["sourceLocality"], r["sourceDistrict"]): r for r in baseline["unresolvedNonStreet"]}
    geo = geography_prototypes(sources["districts"], sources["municipalities"], manifest["acquiredAt"][:10])
    current = json.loads((data_dir / "municipalities.json").read_bytes())["municipalities"]
    current = {r["code"]: r for r in current}
    regions = {r["code"] for r in json.loads((data_dir / "regions.json").read_bytes())["regions"]}
    units, regpj = parse_regpj(regpj_zip, current, geo["districtByNote"], regions,
                             {r["note"]: r["code"] for r in sources["districts"] if r["note"]})
    town_titles = {r["note"]: {normalize(r[k]) for k in ("officialTitle", "mediumTitle", "shortTitle")}
                   for r in sources["municipalities"] if r["note"]}
    regpj["administrativeTitleDeviations"] = [{"code": u["parentCode"], "regpjName": u["unitName"],
        "currentName": current[u["parentCode"]]["name"]} for u in units
        if u["unitType"] == "LSUJ2" and normalize(u["unitName"]) not in town_titles[u["parentCode"]]]
    index = index_units(units, date.fromisoformat(manifest["acquiredAt"][:10]))
    district_names = {normalize(r["name"]): note for note, r in geo["districtByNote"].items()}
    post_profile = inspect_post_profile(post_zip, district_names)
    results, blockers, conflicts = [], [], []
    previous_outcomes = defaultdict(Counter)
    for i, row in enumerate(sources["psc"], 1):
        result = map_assignment(row, index, post["parts"], district_names)
        results.append(result)
        previous = baseline_pairs.get((row["obce"], row.get("kodOkresu"))) if row["typZaznamu"] != "ulica" else None
        if previous:
            previous_outcomes[previous["classification"]][result["state"]] += 1
        if result["state"] == "SOURCE_CONFLICT":
            conflicts.append({"psc": row["psc"], "postalLocality": row["obce"], "district": row.get("kodOkresu"), **result})
        if previous and previous["classification"] in {"UNRESOLVED", "AMBIGUOUS"}:
            blockers.append({"sourceRow": i, "psc": row["psc"], "postalType": row["typZaznamu"], "postalLocality": row["obce"],
                "district": row.get("kodOkresu"), "region": row.get("kraj"), "deliveryPost": row.get("dposta"),
                "previousState": previous["classification"], **result})
    all_pscs = coverage(sources["psc"], results)
    old_incomplete = {r["psc"] for r in baseline["ulicaOnly"] if not r["allRowsDeterministicallyMapped"]}
    street_only = {r["psc"] for r in baseline["ulicaOnly"]}
    street_evidence = defaultdict(dict)
    for row, result in zip(sources["psc"], results):
        if row["psc"] in street_only:
            item = {"postalLocality": row["obce"], "sourceRegion": row.get("kraj"),
                    "sourceDistrict": row.get("kodOkresu"), **result}
            street_evidence[row["psc"]][json.dumps(item, ensure_ascii=False, sort_keys=True)] = item
    for item in all_pscs:
        if item["psc"] in street_only:
            item["localityEvidence"] = [v for _, v in sorted(street_evidence[item["psc"]].items())]
    ceiling = Counter(r["status"] for r in all_pscs)
    starting = {k: baseline[k] for k in ("sourceRows", "sourceTypes", "sourcePscCount", "nonStreetPscCount", "ulicaOnlyPscCount",
        "baselineUnresolvedRows", "baselineUnresolvedByType", "baselineUnresolvedPairs", "affectedPscCount", "candidateClassificationRows")}
    starting["remainingNonStreetRows"] = sum(r["rowCount"] for r in baseline["unresolvedNonStreet"] if r["classification"] in {"UNRESOLVED", "AMBIGUOUS"})
    starting["incompleteStreetOnlyPscs"] = len(old_incomplete)
    starting["referenceCountsReproduced"] = (starting["sourceTypes"] == {"obec": 2790, "detail_sc": 173, "ulica": 10737}
        and starting["baselineUnresolvedRows"] == 84 and starting["baselineUnresolvedPairs"] == 82
        and starting["affectedPscCount"] == 69 and starting["remainingNonStreetRows"] == 42
        and starting["sourcePscCount"] == 1415 and starting["nonStreetPscCount"] == 1293
        and starting["ulicaOnlyPscCount"] == 122 and len(old_incomplete) == 63)
    return {"profile": "psc-administrative-mapping-research-v1", "researchOnly": True, "productionApproved": False,
        "normalization": "NFC/casefold/collapsed whitespace/dash variants and spacing only; no word-boundary deletion",
        "temporalQualification": "REGPJ snapshot has no validity/as-of fields; deterministic means within captured evidence, not certified current containment",
        "productionFileSha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(data_dir.glob("*.json"))},
        "baseline": starting, "regpj": regpj, "postProfile": post_profile, "nonStreetBlockers": blockers,
        "priorCandidateOutcomes": {k: dict(sorted(v.items())) for k, v in sorted(previous_outcomes.items())},
        "sourceConflicts": conflicts,
        "nonStreetBlockerStates": dict(sorted(Counter(r["state"] for r in blockers).items())),
        "nonStreetBlockerClasses": dict(sorted(Counter(r["classification"] for r in blockers).items())),
        "streetOnly": [r for r in all_pscs if r["psc"] in street_only],
        "previouslyIncompleteStreetOnly": [r for r in all_pscs if r["psc"] in old_incomplete],
        "pscCoverage": all_pscs, "coverage": {"pscCounts": dict(sorted(ceiling.items())),
            "sourceRowStates": dict(sorted(Counter(r["state"] for r in results).items())),
            "sourceRowStatesByType": {typ: dict(sorted(Counter(r["state"] for source, r in zip(sources["psc"], results)
                                                           if source["typZaznamu"] == typ).items())) for typ in sorted({r["typZaznamu"] for r in sources["psc"]})},
            "multiMunicipalityPscs": sum(r["multiMunicipality"] for r in all_pscs),
            "completeMultiMunicipalityPscs": sum(r["multiMunicipality"] and r["status"] == "COMPLETE" for r in all_pscs),
            "streetScopedPscs": sum("ulica" in r["sourceTypes"] for r in all_pscs),
            "addressScopedPscs": sum(r["addressScoped"] for r in all_pscs),
            "houseNumberScopedPscs": sum("detail_sc" in r["sourceTypes"] for r in all_pscs)},
        "acquisition": {"portalvsAcquiredAt": manifest["acquiredAt"], "portalvsManifestSha256": manifest["manifestSha256"],
            "regpjSha256": evidence["resources"]["regpj"]["sha256"], "postSha256": post["sha256"]}}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--portalvs-manifest", required=True, type=Path)
    p.add_argument("--portalvs-capture", required=True, type=Path)
    p.add_argument("--regpj-zip", required=True, type=Path)
    p.add_argument("--post-zip", required=True, type=Path)
    p.add_argument("--evidence-manifest", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path, help="external or ignored data/generated JSON only")
    a = p.parse_args(argv)
    try:
        output = a.output.resolve()
        require(not output.is_relative_to(ROOT) or output.is_relative_to(ROOT / "data/generated"), "output cannot be a production/tracked repository path")
        require(output not in {path.resolve() for path in (a.portalvs_manifest, a.regpj_zip, a.post_zip, a.evidence_manifest)}, "output would overwrite evidence")
        require(not output.is_relative_to(a.portalvs_capture.resolve()), "output would overwrite a source capture")
        report = analyze(a.portalvs_manifest, a.portalvs_capture, a.regpj_zip, a.post_zip, a.evidence_manifest)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(serialized(report))
        sys.stdout.buffer.write(serialized({k: v for k, v in report.items() if k not in
            {"nonStreetBlockers", "streetOnly", "previouslyIncompleteStreetOnly", "pscCoverage"}}))
        return 0
    except (ValueError, KeyError, TypeError, OSError, zipfile.BadZipFile, ET.ParseError) as exc:
        print(f"Research analysis stopped: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
