#!/usr/bin/env python3
"""RESEARCH ONLY: offline successor diagnostics, never a production importer.

No fuzzy matching, legacy fallback, network, source promotion or dataset writes.
Street/house-number cells and personal workbook metadata are never emitted.
Optional Slovenska posta ZIP evidence enriches CANDIDATES, not production links.
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
from datetime import date, datetime
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.acquire_portalvs_successor import PROFILE, URLS, manifest_hash

POST_ZIP_URL = "https://www.posta.sk/files/6811e10125b182cd7cd9e3a9/postove-smerovacie-cisla-na-stiahnutie.zip"
TITLE_FIELDS = ("officialTitle", "mediumTitle", "shortTitle")
REGIONS = {"1": ("SK010", 8), "2": ("SK021", 7), "3": ("SK022", 9), "4": ("SK023", 7),
           "5": ("SK031", 11), "6": ("SK032", 13), "7": ("SK041", 13), "8": ("SK042", 11)}
POST_REGIONS = dict(zip(("BL", "TA", "TC", "NI", "ZI", "BC", "PV", "KI"), (v[0] for v in REGIONS.values())))
GEO_KEYS = {"sortNumber", "code", *TITLE_FIELDS, "officialTitleEn", "mediumTitleEn", "shortTitleEn",
            "note", "noteEn", "includes", "includesAlso", "excludes", "info", "additionalInfo", "infoEn",
            "unitOfMeasure", "validFrom", "validTo"}
PSC_KEYS = {"dulica", "ulica", "psc", "dposta", "posta", "obce", "typZaznamu", "kodOkresu", "kraj",
            "name_translations", "poznamka"}
TYPES = {"obec", "detail_sc", "ulica"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def exact_text(value):
    require(isinstance(value, str), "expected source string")
    return " ".join(unicodedata.normalize("NFC", value).split())


def normalized_text(value):
    """Comparison only: preserve letters/diacritics; no expansion/typo repair."""
    return "".join(c for c in exact_text(value).casefold()
                   if not c.isspace() and not unicodedata.category(c).startswith("P"))


def load_capture(manifest_path):
    path = Path(manifest_path).resolve()
    require(not path.is_relative_to(ROOT), "raw capture must remain outside repository")
    manifest = json.loads(path.read_bytes())
    require(manifest.get("profile") == PROFILE and manifest.get("manifestSha256") == manifest_hash(manifest),
            "acquisition manifest profile/hash mismatch")
    require(set(manifest.get("sources", {})) == set(URLS), "all three coherent captures required")
    stamp = datetime.fromisoformat(manifest["acquiredAt"].replace("Z", "+00:00"))
    require(stamp.utcoffset() is not None, "acquisition timestamp needs timezone")
    sources = {}
    for key, url in URLS.items():
        entry = manifest["sources"][key]
        require(entry["url"] == url and entry["status"] == 200 and "application/json" in entry["contentType"],
                "unexpected acquisition URL/status/type")
        require(entry["file"] == key + ".json", "unexpected raw filename")
        raw_path = (path.parent / entry["file"]).resolve()
        require(raw_path.parent == path.parent, "raw page escapes capture directory")
        raw = raw_path.read_bytes()
        require(len(raw) == entry["bytes"] and hashlib.sha256(raw).hexdigest() == entry["sha256"], "raw source hash/size mismatch")
        rows = json.loads(raw)
        require(isinstance(rows, list) and len(rows) == entry["rows"] and all(isinstance(r, dict) for r in rows),
                "raw source rows differ from manifest")
        sources[key] = rows
    return manifest, sources


def check_schema(sources):
    for kind, rows in sources.items():
        allowed = PSC_KEYS if kind == "psc" else GEO_KEYS
        for row in rows:
            require(not set(row) - allowed, "unreviewed source schema key")
            for key, value in row.items():
                if key == "sortNumber":
                    require(type(value) is int, "invalid source sort number")
                elif key == "name_translations":
                    require(isinstance(value, list), "invalid translations shape")
                else:
                    require(value is None or isinstance(value, str), "invalid source field type")
            if kind == "psc":
                require(row.get("typZaznamu") in TYPES, "unknown PSC source type")
                require(re.fullmatch(r"[0-9]{5}", row.get("psc", "")), "malformed source PSC")
                require(bool(exact_text(row.get("obce", ""))), "missing postal locality")
            else:
                require(all(isinstance(row.get(k), str) for k in ("code", "note", *TITLE_FIELDS, "validFrom")),
                        "missing critical geography field")


def geography_prototypes(counties, towns, snapshot_date):
    """In-memory only; published identifiers from statistical note + source code."""
    districts, by_source, by_note, relettered = {}, {}, {}, []
    excluded_counties = 0
    for row in counties:
        if row["code"] in {"SKZZZZ", "SKZZZ"}:
            excluded_counties += 1
            continue
        note = row["note"]
        require(re.fullmatch(r"[1-8][0-9]{2}", note), "malformed statistical district code")
        region, maximum = REGIONS[note[0]]
        ordinal = int(note[1:])
        require(1 <= ordinal <= maximum, "unreviewed district ordinal")
        require(row["code"] == region + format(ordinal, "X"), "district statistical/source code conflict")
        code = region + str(ordinal)
        require(note not in by_note and code not in districts and row["code"] not in by_source, "duplicate district identity")
        require(not row.get("validTo") or date.fromisoformat(row["validTo"]) >= date.fromisoformat(snapshot_date),
                "unexpected retired district in valid capture")
        out = {"code": code, "name": exact_text(row["mediumTitle"]), "regionCode": region, "country": "SK"}
        require(out["name"], "empty district title")
        districts[code] = out
        by_source[row["code"]] = out
        by_note[note] = out
        if row["code"] != code:
            relettered.append({"successorCode": row["code"], "publicCode": code, "statisticalCode": note})
    regular, pseudo, retired = [], 0, 0
    for row in towns:
        if row["code"] in {"SKZZZZZZZZZZ", "SKZZZZ"}:
            pseudo += 1
            continue
        if row.get("validTo") and date.fromisoformat(row["validTo"]) < date.fromisoformat(snapshot_date):
            retired += 1
            continue
        note = row["note"]
        require(re.fullmatch(r"[0-9]{6}", note), "malformed six-digit municipality note")
        require(row["code"].endswith(note) and row["code"][:-6] in by_source, "unknown/conflicting town district")
        regular.append(row)
    frequencies = Counter(exact_text(t["officialTitle"]) for t in regular)
    municipalities = {}
    for row in regular:
        code = row["note"]
        require(code not in municipalities, "duplicate municipality identity")
        district = by_source[row["code"][:-6]]
        title = exact_text(row["officialTitle"])
        require(title, "empty municipality title")
        name = title + (f" (okres {district['name']})" if frequencies[title] > 1 else "")
        municipalities[code] = {"code": code, "name": name, "districtCode": district["code"],
                                "regionCode": district["regionCode"], "country": "SK"}
    return {"districts": districts, "municipalities": municipalities, "townRows": regular,
            "districtByNote": by_note, "districtBySource": by_source,
            "districtsExcludedPseudo": excluded_counties, "townsExcludedPseudo": pseudo,
            "townsExcludedRetired": retired, "relettered": sorted(relettered, key=lambda r: r["publicCode"]),
            "disambiguatedNames": sum(frequencies[exact_text(t["officialTitle"])] > 1 for t in regular)}


def title_index(geo, normalizer):
    index = defaultdict(dict)
    for row in geo["townRows"]:
        district = geo["districtBySource"][row["code"][:-6]]
        for field in TITLE_FIELDS:
            title = normalizer(row[field])
            if title:
                index[(title, district["code"])].setdefault(row["note"], set()).add(field)
    return index


def candidates(row, geo, index, normalizer, *, allow_missing_district=False):
    name = normalizer(row["obce"])
    district_note, region = row.get("kodOkresu"), row.get("kraj")
    if district_note:
        require(district_note in geo["districtByNote"], "unknown postal district context")
        district = geo["districtByNote"][district_note]
        if region:
            require(POST_REGIONS.get(region) == district["regionCode"], "postal district/region conflict")
        return sorted(index.get((name, district["code"]), {}))
    if not allow_missing_district:
        raise ValueError("non-street row lacks required district context")
    if region:
        require(region in POST_REGIONS, "unknown postal region context")
    result = set()
    for (title, district_code), options in index.items():
        if title == name and (not region or geo["districts"][district_code]["regionCode"] == POST_REGIONS[region]):
            result.update(options)
    return sorted(result)


def read_post_workbook(archive_path):
    """Read public postal workbooks with stdlib only; no author properties.

    Retain locality/administrative evidence, not house-number cells. Street
    equality signatures are transient and never emitted in summary reports.
    """
    ns = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    raw = Path(archive_path).read_bytes()
    outer = zipfile.ZipFile(io.BytesIO(raw))
    require(outer.getinfo("OBCE.xlsx").file_size < 8 * 1024 * 1024, "oversize research workbook")
    book_bytes = outer.read("OBCE.xlsx")
    require(len(book_bytes) < 8 * 1024 * 1024, "oversize research workbook")
    book = zipfile.ZipFile(io.BytesIO(book_bytes))
    require(all(item.file_size < 32 * 1024 * 1024 for item in book.infolist()), "oversize workbook member")
    shared = ["".join(si.itertext()) for si in ET.fromstring(book.read("xl/sharedStrings.xml"))]
    workbook = ET.fromstring(book.read("xl/workbook.xml"))
    rels = {r.attrib["Id"]: r.attrib["Target"].lstrip("/") for r in ET.fromstring(book.read("xl/_rels/workbook.xml.rels"))}
    sheets = {}
    for sheet in workbook.find("s:sheets", ns):
        rel = sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        target = rels[rel]
        path = target if target.startswith("xl/") else "xl/" + target
        values = []
        for source_row in ET.fromstring(book.read(path)).findall("s:sheetData/s:row", ns):
            cells = {}
            for cell in source_row:
                value = cell.find("s:v", ns)
                if value is None:
                    continue
                text = value.text or ""
                if cell.get("t") == "s":
                    text = shared[int(text)]
                column = re.sub(r"[0-9]", "", cell.attrib["r"])
                cells[column] = text
            values.append((int(source_row.attrib["r"]), cells))
        sheets[sheet.attrib["name"]] = values
    basic, parts = [], []
    for number, row in sheets["obce"]:
        if number == 1 or not row.get("A") or not row.get("B") or not re.fullmatch(r"[0-9]{3}", row.get("G", "")):
            continue
        postal = re.sub(r"\s", "", row.get("D", ""))
        basic.append({"deliveryLocality": row["A"], "postalLocality": row["B"], "district": row["G"],
                      "psc": postal if re.fullmatch(r"[0-9]{5}", postal) else None,
                      "deliveryPost": row.get("E"), "post": row.get("F"), "row": number})
    for number, row in sheets["miestne časti"]:
        if number <= 2 or not row.get("C") or not row.get("D") or not row.get("B"):
            continue
        if normalized_text(row["C"]) == normalized_text(row["D"]):
            continue  # The municipality's own row is not part-alias evidence.
        parts.append({"municipality": row["C"], "locality": row["D"], "districtName": row["B"], "row": number})
    description = "\n".join(row.get("A", "") for _, row in sheets["popis"])
    detail = [{"municipality": row["A"], "district": row["C"], "psc": re.sub(r"\s", "", row.get("E", "")),
               "post": row.get("F"), "row": n}
              for n, row in sheets["detail SČ"] if n > 3 and row.get("A") and re.fullmatch(r"[0-9]{3}", row.get("C", ""))]
    street_signatures, street_rows = set(), 0
    if "ULICE.xlsx" in outer.namelist():
        require(outer.getinfo("ULICE.xlsx").file_size < 8 * 1024 * 1024, "oversize street workbook")
        street_bytes = outer.read("ULICE.xlsx")
        require(len(street_bytes) < 8 * 1024 * 1024, "oversize street workbook")
        street_book = zipfile.ZipFile(io.BytesIO(street_bytes))
        require(all(item.file_size < 32 * 1024 * 1024 for item in street_book.infolist()), "oversize street workbook member")
        street_shared = ["".join(si.itertext()) for si in ET.fromstring(street_book.read("xl/sharedStrings.xml"))]
        for source_row in ET.fromstring(street_book.read("xl/worksheets/sheet1.xml")).findall("s:sheetData/s:row", ns):
            cells = {}
            for cell in source_row:
                column = re.sub(r"[0-9]", "", cell.attrib["r"])
                if column not in {"B", "C", "D", "G"}:
                    continue
                value = cell.find("s:v", ns)
                if value is not None:
                    cells[column] = street_shared[int(value.text)] if cell.get("t") == "s" else value.text
            postal = re.sub(r"\s", "", cells.get("C", ""))
            if re.fullmatch(r"[0-9]{5}", postal):
                street_rows += 1
                street_signatures.add(street_signature(cells.get("G", ""), cells.get("B", ""), postal, cells.get("D", "")))
    return {"url": POST_ZIP_URL, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
            "basic": basic, "parts": parts, "detail": detail, "description": description,
            "streetSignatureHashes": sorted(street_signatures), "streetRows": street_rows}


def street_signature(locality, street, postal, delivery_post):
    """Transient equality proof only; hashes never included in public reports."""
    return hashlib.sha256(json.dumps([exact_text(v) for v in (locality, street, postal, delivery_post)],
                                    ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def post_evidence(row, geo, normalized_index, post):
    """Only publisher-provided paired values/part relations, never substrings."""
    if post is None:
        return [], []
    district = geo["districtByNote"][row["kodOkresu"]]
    names = {normalized_text(row["obce"])}
    codes, proofs = set(), []
    for item in post["basic"]:
        if item["district"] != row["kodOkresu"] or item["psc"] != row["psc"]:
            continue
        if normalized_text(item["postalLocality"]) != normalized_text(row["obce"]):
            continue
        names.add(normalized_text(item["deliveryLocality"]))
        possible = sorted(normalized_index.get((normalized_text(item["deliveryLocality"]), district["code"]), {}))
        if possible:
            codes.update(possible)
            proofs.append({"kind": "PAIRED_POSTAL_LABEL", "sheet": "obce", "row": item["row"],
                           "publisherDeliveryLocality": item["deliveryLocality"], "candidates": possible})
    for item in post["parts"]:
        if normalized_text(item["districtName"]) != normalized_text(district["name"]):
            continue
        if normalized_text(item["locality"]) not in names:
            continue
        possible = sorted(normalized_index.get((normalized_text(item["municipality"]), district["code"]), {}))
        if possible:
            codes.update(possible)
            proofs.append({"kind": "PUBLISHER_LOCALITY_PART", "sheet": "miestne časti", "row": item["row"],
                           "publisherLocality": item["locality"], "publisherMunicipality": item["municipality"],
                           "candidates": possible})
    return sorted(codes), sorted(proofs, key=lambda p: (p["sheet"], p["row"]))


def classify_unresolved(rows, geo, normal_index, post):
    exact_index = title_index(geo, exact_text)
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["obce"], row["kodOkresu"])].append(row)
    result = []
    for (name, context), group in sorted(grouped.items()):
        norm = candidates(group[0], geo, normal_index, normalized_text)
        publisher_codes, proofs = set(), []
        for row in group:
            codes, evidence = post_evidence(row, geo, normal_index, post)
            publisher_codes.update(codes)
            proofs.extend(evidence)
        all_codes = set(norm) | publisher_codes
        if len(all_codes) > 1:
            classification = "AMBIGUOUS"
        elif norm:
            classification = "ALTERNATE_OFFICIAL_NAME"
        elif publisher_codes:
            classification = ("MUNICIPALITY_PART" if any(e["kind"] == "PUBLISHER_LOCALITY_PART" for e in proofs)
                              else "DELIVERY_LOCALITY")
        else:
            classification = "UNRESOLVED"
        district = geo["districtByNote"][context]
        proof_unique = {json.dumps(e, ensure_ascii=False, sort_keys=True): e for e in proofs}
        result.append({"sourceLocality": name, "sourceDistrict": context, "publicDistrict": district["code"],
            "sourceRegions": sorted({r["kraj"] for r in group if r.get("kraj")}),
            "types": sorted({r["typZaznamu"] for r in group}), "pscs": sorted({r["psc"] for r in group}),
            "rowCount": len(group), "exactCandidates": candidates(group[0], geo, exact_index, exact_text),
            "normalizedCandidates": norm,
            "publisherCandidates": sorted(publisher_codes), "classification": classification,
            "candidateMunicipalities": [{"code": c, "name": geo["municipalities"][c]["name"]} for c in sorted(all_codes)],
            "candidateTownFields": [{field: town.get(field) for field in
                (*TITLE_FIELDS, "includes", "includesAlso", "excludes", "note", "additionalInfo", "info")}
                for town in sorted(geo["townRows"], key=lambda r: r["note"]) if town["note"] in all_codes],
            "evidence": [proof_unique[k] for k in sorted(proof_unique)],
            "evidenceLimit": ("No unique identity established; exact titles, normalized titles and publisher relations checked."
                              if classification in {"UNRESOLVED", "AMBIGUOUS"} else
                              "Research candidate only; postal label pairing is not an administrative identity guarantee."),
            "automaticMappingApproved": False})
    return result


def ulica_summary(rows, geo, index):
    ids, no_candidate, ambiguous = set(), 0, 0
    for row in rows:
        options = candidates(row, geo, index, normalized_text, allow_missing_district=True)
        if not options:
            no_candidate += 1
        elif len(options) > 1:
            ambiguous += 1
        else:
            ids.update(options)
    classification = ("MULTI_MUNICIPALITY" if len(ids) > 1 else "AMBIGUOUS" if ambiguous else
                      "INSUFFICIENT_EVIDENCE" if no_candidate else "SAFE_TO_COLLAPSE_CANDIDATE")
    return {"psc": rows[0]["psc"], "ulicaRows": len(rows),
            "sourceLocalities": sorted({r["obce"] for r in rows}),
            "distinctSourceLocalities": len({r["obce"] for r in rows}),
            "sourceDistricts": sorted({r["kodOkresu"] for r in rows if r.get("kodOkresu")}),
            "sourceDistrictCount": len({r["kodOkresu"] for r in rows if r.get("kodOkresu")}),
            "distinctDeliveryPosts": len({r["dposta"] for r in rows if r.get("dposta")}),
            "sourceRegionContexts": sorted({r["kraj"] for r in rows if r.get("kraj")}),
            "candidateMunicipalities": [{"code": c, "name": geo["municipalities"][c]["name"]} for c in sorted(ids)],
            "candidateDistricts": sorted({geo["municipalities"][c]["districtCode"] for c in ids}),
            "rowsWithoutCandidate": no_candidate, "rowsWithAmbiguousCandidates": ambiguous,
            "allRowsDeterministicallyMapped": not no_candidate and not ambiguous,
            "allRowsMapToOneMunicipality": not no_candidate and not ambiguous and len(ids) == 1,
            "classification": classification, "productionCollapseApproved": False}


def geographic_diff(before, after):
    return {"oldCount": len(before), "newCount": len(after), "addedCodes": sorted(after.keys() - before.keys()),
            "removedCodes": sorted(before.keys() - after.keys()),
            "changedRecords": [{"code": c, "before": before[c], "after": after[c]}
                               for c in sorted(before.keys() & after.keys()) if before[c] != after[c]]}


def analyze_sources(sources, *, snapshot_date, previous=None, post=None):
    check_schema(sources)
    geo = geography_prototypes(sources["districts"], sources["municipalities"], snapshot_date)
    exact_index, normal_index = title_index(geo, exact_text), title_index(geo, normalized_text)
    nonstreet, streets = [], []
    for row in sources["psc"]:
        (streets if row["typZaznamu"] == "ulica" else nonstreet).append(row)
    unresolved, resolved, normalized_resolved, enriched = [], [], [], []
    for row in nonstreet:
        exact = candidates(row, geo, exact_index, exact_text)
        normalized = candidates(row, geo, normal_index, normalized_text)
        if len(exact) != 1:
            unresolved.append(row)
        else:
            resolved.append(row)
        if len(normalized) == 1:
            normalized_resolved.append(row)
        codes, _ = post_evidence(row, geo, normal_index, post) if len(exact) != 1 else (exact, [])
        if len(set(normalized) | set(codes)) == 1:
            enriched.append(row)
    unresolved_table = classify_unresolved(unresolved, geo, normal_index, post)
    all_codes = {r["psc"] for r in sources["psc"]}
    nonstreet_codes = {r["psc"] for r in nonstreet}
    street_only = sorted(all_codes - nonstreet_codes)
    street_groups = defaultdict(list)
    for row in streets:
        if row["psc"] in street_only:
            street_groups[row["psc"]].append(row)
    ulica = [ulica_summary(street_groups[code], geo, normal_index) for code in street_only]
    affected = []
    pair_candidates = {(r["sourceLocality"], r["sourceDistrict"]):
                       set(r["normalizedCandidates"]) | set(r["publisherCandidates"]) for r in unresolved_table}
    for code in sorted({r["psc"] for r in unresolved}):
        known = [r for r in resolved if r["psc"] == code]
        unknown = [r for r in unresolved if r["psc"] == code]
        known_ids = {c for r in known for c in candidates(r, geo, exact_index, exact_text)}
        proposed_ids = set()
        still_unassigned = 0
        for row in unknown:
            options = pair_candidates[(row["obce"], row["kodOkresu"])]
            if len(options) == 1:
                proposed_ids.update(options)
            else:
                still_unassigned += 1
        affected.append({"psc": code, "exactRows": len(known), "unresolvedRows": len(unknown),
                         "hasExactRows": bool(known), "disappearsIfDropped": not known,
                         "exactMunicipalityCodes": sorted(known_ids),
                         "candidateAdditionalMunicipalityCodes": sorted(proposed_ids - known_ids),
                         "candidateAlreadyCoveredMunicipalityCodes": sorted(proposed_ids & known_ids),
                         "stillUnassignedRows": still_unassigned,
                         "extraMunicipalityCoverageKnown": False})
    report = {
        "profile": "portalvs-psc-semantics-research-v1", "researchOnly": True,
        "sourceRows": {k: len(v) for k, v in sources.items()},
        "sourceTypes": dict(sorted(Counter(r["typZaznamu"] for r in sources["psc"]).items())),
        "typeCoexistence": dict(sorted(Counter("+".join(sorted({r["typZaznamu"] for r in sources["psc"] if r["psc"] == code}))
                                            for code in all_codes).items())),
        "sourcePscCount": len(all_codes), "nonStreetRows": len(nonstreet), "nonStreetPscCount": len(nonstreet_codes),
        "ulicaOnlyPscCount": len(street_only), "baselineUnresolvedRows": len(unresolved),
        "baselineUnresolvedByType": dict(sorted(Counter(r["typZaznamu"] for r in unresolved).items())),
        "baselineUnresolvedPairs": len(unresolved_table), "affectedPscCount": len(affected),
        "baselineUnresolvedNormalizedTitleRows": sum(len(candidates(r, geo, normal_index, normalized_text)) == 1 for r in unresolved),
        "automaticMunicipalityMappingsApproved": 0,
        "candidateClassificationRows": dict(sorted(Counter({label: sum(v["rowCount"] for v in unresolved_table if v["classification"] == label)
            for label in {v["classification"] for v in unresolved_table}}).items())),
        "candidateClassificationPairs": dict(sorted(Counter(v["classification"] for v in unresolved_table).items())),
        "unresolvedNonStreet": unresolved_table, "ulicaOnly": ulica, "affectedNonStreetPscs": affected,
        "ulicaOnlyClassifications": dict(sorted(Counter(v["classification"] for v in ulica).items())),
        "coverageDiagnosticsNotApprovedForProduction": {
            "allSourcePscs": len(all_codes), "nonStreetAllRowsIdeal": len(nonstreet_codes),
            "baselineExactRows": len(resolved), "baselineExactPscs": len({r["psc"] for r in resolved}),
            "normalizedTitleRows": len(normalized_resolved), "normalizedTitlePscs": len({r["psc"] for r in normalized_resolved}),
            "publisherEnrichedCandidateRows": len(enriched), "publisherEnrichedCandidatePscs": len({r["psc"] for r in enriched}),
            "affectedPscsWithSomeExactRows": sum(r["hasExactRows"] for r in affected),
            "affectedPscsLostByExactOnly": sum(r["disappearsIfDropped"] for r in affected),
        },
        "townAuxiliaryFieldNonemptyCounts": {k: sum(bool(t.get(k)) for t in geo["townRows"])
            for k in ("includes", "includesAlso", "excludes", "note", "info", "additionalInfo", "noteEn")},
        "geography": {k: geo[k] for k in ("districtsExcludedPseudo", "townsExcludedPseudo", "townsExcludedRetired", "relettered", "disambiguatedNames")},
    }
    if previous is not None:
        for kind in ("districts", "municipalities"):
            report["geography"][kind] = geographic_diff({r["code"]: r for r in previous[kind][kind]}, geo[kind])
        old = previous["psc"]
        codes = set(old) - {"metadata"}
        report["productionComparison"] = {"oldPscKeys": len(codes), "oldMatches": sum(len(old[c]["matches"]) for c in codes),
            "sourceAddedPscs": sorted(all_codes - codes), "sourceAbsentPscs": sorted(codes - all_codes)}
        link_failures = 0
        for code in codes:
            for row in old[code]["matches"]:
                town = geo["municipalities"].get(row.get("municipalityCode"))
                if not town or town["districtCode"] != row.get("districtCode") or town["regionCode"] != row.get("regionCode"):
                    link_failures += 1
        report["geography"]["existingPscLinkFailures"] = link_failures
    if post is not None:
        report["postEvidence"] = {k: post[k] for k in ("url", "bytes", "sha256")}
        report["postEvidence"].update(basicRows=len(post["basic"]), detailRows=len(post["detail"]), partRows=len(post["parts"]))
        basic_signatures = {(r["psc"], exact_text(r["postalLocality"]), exact_text(r["deliveryLocality"]),
                             exact_text(r["deliveryPost"] or "")) for r in post["basic"] if r["psc"]}
        detail_signatures = {(r["psc"], exact_text(r["municipality"]), r["district"], exact_text(r["post"] or "")) for r in post["detail"]}
        report["postEvidence"]["obecSignatureMatches"] = sum(
            (r["psc"], exact_text(r["obce"]), exact_text(r.get("dulica") or ""), exact_text(r.get("dposta") or "")) in basic_signatures
            for r in nonstreet if r["typZaznamu"] == "obec")
        report["postEvidence"]["detailScSignatureMatches"] = sum(
            (r["psc"], exact_text(r["obce"]), r["kodOkresu"], exact_text(r.get("posta") or "")) in detail_signatures
            for r in nonstreet if r["typZaznamu"] == "detail_sc")
        if post.get("streetRows"):
            hashes = set(post["streetSignatureHashes"])
            report["postEvidence"]["streetRows"] = post["streetRows"]
            report["postEvidence"]["ulicaSignatureMatches"] = sum(
                street_signature(r["obce"], r.get("ulica") or "", r["psc"], r.get("dposta") or "") in hashes for r in streets)
    return report


def analyze(manifest_path, *, post_zip=None, data_dir=ROOT / "data"):
    manifest, sources = load_capture(manifest_path)
    previous = {key: json.loads((data_dir / (key + ".json")).read_bytes()) for key in URLS}
    report = analyze_sources(sources, snapshot_date=manifest["acquiredAt"][:10], previous=previous,
                             post=read_post_workbook(post_zip) if post_zip else None)
    report["acquisition"] = {"acquiredAt": manifest["acquiredAt"], "manifestSha256": manifest["manifestSha256"],
        "sources": {k: {field: v[field] for field in ("url", "status", "contentType", "bytes", "sha256", "etag", "rows")}
                    for k, v in manifest["sources"].items()}}
    report["productionFileSha256"] = {key: hashlib.sha256((data_dir / (key + ".json")).read_bytes()).hexdigest() for key in URLS}
    return report


def serialized(report):
    return (json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--post-zip", type=Path, help="optional official published ZIP; research candidates only")
    parser.add_argument("--output", type=Path, help="research JSON; outside repository or ignored data/generated only")
    args = parser.parse_args(argv)
    try:
        if args.output:
            destination = args.output.resolve()
            require(not destination.is_relative_to(ROOT) or destination.is_relative_to(ROOT / "data" / "generated"),
                    "research output cannot overwrite production or tracked repository files")
        report = analyze(args.manifest, post_zip=args.post_zip)
        if args.output:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(serialized(report))
        summary = {k: v for k, v in report.items() if k not in {"unresolvedNonStreet", "ulicaOnly", "affectedNonStreetPscs"}}
        sys.stdout.buffer.write(serialized(summary))
        return 0
    except (ValueError, KeyError, OSError, zipfile.BadZipFile) as exc:
        print(f"Research analysis failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
