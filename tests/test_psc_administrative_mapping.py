"""Synthetic evidence and negative controls; no retained archives or network required."""

import hashlib
import io
import json
import socket
import urllib.request
import zipfile
from collections import Counter
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from scripts import analyze_psc_administrative_mapping as mapping
from scripts.acquire_portalvs_successor import PROFILE, URLS, OPENAPI_URL, manifest_hash

TODAY = date(2026, 10, 16)


def xlsx(sheets):
    namespace = mapping.NS["s"]
    relations = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    book = ET.Element("workbook", xmlns=namespace)
    records = ET.SubElement(book, "sheets")
    rels = ET.Element("Relationships", xmlns="http://schemas.openxmlformats.org/package/2006/relationships")
    shared = ET.Element("sst", xmlns=namespace)
    strings = []
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as z:
        for i, (name, rows) in enumerate(sheets.items(), 1):
            ET.SubElement(records, "sheet", name=name, attrib={f"{{{relations}}}id": f"rId{i}"})
            ET.SubElement(rels, "Relationship", Id=f"rId{i}", Target=f"worksheets/sheet{i}.xml")
            worksheet = ET.Element("worksheet", xmlns=namespace)
            data = ET.SubElement(worksheet, "sheetData")
            for number, values in rows:
                r = ET.SubElement(data, "row", r=str(number))
                for column, value in values.items():
                    strings.append(str(value))
                    c = ET.SubElement(r, "c", r=f"{column}{number}", t="s")
                    ET.SubElement(c, "v").text = str(len(strings) - 1)
            z.writestr(f"xl/worksheets/sheet{i}.xml", ET.tostring(worksheet, encoding="utf-8"))
        for value in strings:
            ET.SubElement(ET.SubElement(shared, "si"), "t").text = value
        z.writestr("xl/sharedStrings.xml", ET.tostring(shared, encoding="utf-8"))
        z.writestr("xl/workbook.xml", ET.tostring(book, encoding="utf-8"))
        z.writestr("xl/_rels/workbook.xml.rels", ET.tostring(rels, encoding="utf-8"))
        z.writestr("docProps/core.xml", "SYNTHETIC PRIVATE AUTHOR SECRET")
    return buffer.getvalue()


def relationship(**changes):
    values = ["SK01", "Bratislavský kraj", "SK010", "1", "Bratislavský", "101", "SK0101", "Synthetic district",
              "SK0101100001", "100001", "Alpha", "800001", "Synthetic cadastre", "20001", "Synthetic settlement"]
    return dict(dict(zip("ABCDEFGHIJKLMNO", values)), **changes)


def write_regpj(path, rows, headers=None, extra_member=False):
    headers = headers or dict(zip("ABCDEFGHIJKLMNO", mapping.HEADERS))
    raw = xlsx({"REGPJ": [(1, headers), *[(i, r) for i, r in enumerate(rows, 2)]]})
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("REGPJ2020.xlsx", raw)
        z.writestr("REGPJ2020.ods", b"synthetic unused alternate representation")
        if extra_member:
            z.writestr("unreviewed.txt", "unknown")


def parse(path):
    current = {"100001": {"code": "100001", "name": "Alpha", "districtCode": "SK0101", "regionCode": "SK010"},
               "100002": {"code": "100002", "name": "Beta", "districtCode": "SK0101", "regionCode": "SK010"}}
    return mapping.parse_regpj(path, current, {"101": {"code": "SK0101", "regionCode": "SK010"}}, {"SK010"}, {"101": "SK0101"})


def test_actual_regpj_header_encoding_and_explicit_parent(tmp_path):
    path = tmp_path / "regpj.zip"
    write_regpj(path, [relationship(O="Žilinská lokalita")])
    units, report = parse(path)
    child = next(u for u in units if u["unitType"] == "ZSJ")
    assert child["unitName"] == "Žilinská lokalita" and child["parentCode"] == "100001"
    assert child["unitCode"] == "20001" and child["sourceRows"] == [2]
    assert child["validFrom"] is child["validTo"] is None
    assert report["dataAsOf"] is None and report["validityFields"] == report["streetFields"] == []


@pytest.mark.parametrize("change", [dict(J="999999"), dict(I="SK0101999999"), dict(F="999"), dict(C="SK099"),
                                    dict(G="SK0102", I="SK0102100001"), dict(L="invalid"), dict(N="000001")])
def test_unknown_ids_or_invalid_parent_context_fail(tmp_path, change):
    path = tmp_path / "regpj.zip"
    write_regpj(path, [relationship(**change)])
    with pytest.raises(ValueError):
        parse(path)


def test_unknown_archive_member_and_schema_not_silently_parsed(tmp_path):
    path = tmp_path / "regpj.zip"
    write_regpj(path, [relationship()], extra_member=True)
    with pytest.raises(ValueError, match="archive members"):
        parse(path)
    headers = dict(zip("ABCDEFGHIJKLMNO", mapping.HEADERS))
    headers["P"] = "validTo"
    write_regpj(path, [relationship()], headers=headers)
    with pytest.raises(ValueError, match="header columns"):
        parse(path)


def test_identical_rows_deduplicate_but_conflicting_admin_identity_fails(tmp_path):
    path = tmp_path / "regpj.zip"
    write_regpj(path, [relationship(), relationship()])
    units, report = parse(path)
    assert report["duplicateRelationshipRows"] == 1 and report["uniqueRelationshipRows"] == 1
    assert len(units) == 3
    write_regpj(path, [relationship(), relationship(K="Different admin name")])
    with pytest.raises(ValueError, match="conflicting duplicate administrative"):
        parse(path)


def test_zsj_many_to_many_is_preserved_not_first_parent_selected(tmp_path):
    path = tmp_path / "regpj.zip"
    write_regpj(path, [relationship(), relationship(J="100002", I="SK0101100002", K="Beta", L="800002")])
    units, report = parse(path)
    assert report["zsjIdsWithMultipleAdministrativeParents"] == 1
    candidates = [u for u in units if u["unitType"] == "ZSJ"]
    assert {u["parentCode"] for u in candidates} == {"100001", "100002"}


def test_conflicting_cadastral_parent_is_rejected(tmp_path):
    path = tmp_path / "regpj.zip"
    write_regpj(path, [relationship(), relationship(J="100002", I="SK0101100002", K="Beta", N="20002")])
    with pytest.raises(ValueError, match="cadastral parent"):
        parse(path)


def unit(name="Locality", parent="100001", kind="ZSJ", **changes):
    return dict({"unitName": name, "unitCode": "20001" if kind != "LSUJ2" else parent,
        "unitType": kind, "parentCode": parent, "districtStatisticalCode": "101", "regionCode": "SK010",
        "sourceRows": [2], "temporalStatus": "SNAPSHOT_VALIDITY_UNKNOWN", "validFrom": None, "validTo": None}, **changes)


def postal(name="Locality", **changes):
    return dict({"psc": "12345", "obce": name, "typZaznamu": "obec", "kodOkresu": "101", "kraj": "BL", "dposta": "Delivery post"}, **changes)


def match(row=None, units=None, parts=None):
    return mapping.map_assignment(row or postal(), mapping.index_units(units if units is not None else [unit()], TODAY),
                                  parts or [], {"synthetic district": "101"})


@pytest.mark.parametrize("kind,classification", [("LSUJ2", "REGPJ_DIRECT_ADMIN"), ("ZSJ", "REGPJ_ZSJ_PARENT"), ("UTJ", "REGPJ_CADASTRAL_PARENT")])
def test_exact_unit_with_explicit_parent(kind, classification):
    result = match(units=[unit(kind=kind)])
    assert result["state"] == "AUTHORITATIVE_DETERMINISTIC"
    assert result["classification"] == classification and result["municipalityCodes"] == ["100001"]


def test_exact_post_part_to_regpj_admin_chain():
    parts = [{"locality": "Locality", "municipality": "Alpha", "districtName": "Synthetic district", "row": 42}]
    result = match(units=[unit("Alpha", kind="LSUJ2")], parts=parts)
    assert result["classification"] == "POST_PART_REGPJ_PARENT"
    assert result["evidence"][0]["publisherPartRow"] == 42


def test_part_parent_must_itself_be_exact_admin_not_another_settlement():
    parts = [{"locality": "Locality", "municipality": "Alpha", "districtName": "Synthetic district", "row": 42}]
    assert match(units=[unit("Alpha", kind="ZSJ")], parts=parts)["state"] == "NO_MATCH"


def test_conflicting_post_and_regpj_paths_never_vote():
    parts = [{"locality": "Locality", "municipality": "Alpha", "districtName": "Synthetic district", "row": 42}]
    result = match(units=[unit("Locality", "100002"), unit("Alpha", kind="LSUJ2")], parts=parts)
    assert result["state"] == "SOURCE_CONFLICT" and result["municipalityCodes"] == ["100001", "100002"]


def test_same_settlement_or_zsj_name_with_two_parents_stays_ambiguous():
    result = match(units=[unit(), unit(parent="100002")])
    assert result["state"] == "AUTHORITATIVE_BUT_AMBIGUOUS" and len(result["municipalityCodes"]) == 2


def test_same_name_across_districts_requires_explicit_context():
    units = [unit(), unit(parent="100002", districtStatisticalCode="102")]
    assert match(units=units)["municipalityCodes"] == ["100001"]
    assert match(postal(kodOkresu=None), units=units)["state"] == "AUTHORITATIVE_BUT_AMBIGUOUS"


def test_missing_region_cannot_be_borrowed_from_another_row_or_delivery_post():
    units = [unit(), unit(parent="100002", districtStatisticalCode="501", regionCode="SK031")]
    row = postal(kodOkresu=None, kraj=None)
    assert match(row, units)["state"] == "AUTHORITATIVE_BUT_AMBIGUOUS"
    rows = [postal(kodOkresu=None), row]
    results = [match(r, units) for r in rows]
    report = mapping.coverage(rows, results)[0]
    assert report["sourceRegions"] == ["BL"] and report["missingRegionRows"] == 1
    assert report["status"] == "PARTIAL" and report["missingDistrictRows"] == 2


@pytest.mark.parametrize("name", ["Bratislava", "Košice", " KOŠICE "])
def test_aggregate_city_label_cannot_choose_a_borough_even_if_name_matches(name):
    result = match(postal(name), [unit(name, kind="LSUJ2")])
    assert result["state"] == "SEMANTICALLY_INSUFFICIENT" and result["municipalityCodes"] == []


def test_delivery_post_proximity_and_first_result_do_not_establish_identity():
    assert match(postal("Unmatched", dposta="Alpha"), [unit("Alpha", kind="LSUJ2")])["state"] == "NO_MATCH"
    assert match(postal("Locality-suffix"), [unit()])["state"] == "NO_MATCH"
    assert match(postal("Locallty"), [unit()])["state"] == "NO_MATCH"
    with pytest.raises(ValueError, match="explicit administrative parent"):
        match(units=[unit(parent=None)])


@pytest.mark.parametrize("changes", [{"current": False}, {"validTo": "2000-01-01"}, {"validFrom": "2099-01-01"}])
def test_historic_or_future_units_do_not_enter_mapping(changes):
    assert match(units=[unit(**changes)])["state"] == "NO_MATCH"


def test_kolonia_negative_control():
    row = postal("Kolónia", kodOkresu="811", kraj="KI")
    units = [unit("Kolónia", parent, districtStatisticalCode="811", regionCode="SK042") for parent in ("528188", "543896")]
    assert match(row, units)["state"] == "AUTHORITATIVE_BUT_AMBIGUOUS"


def test_nfc_whitespace_and_dash_only_not_arbitrary_punctuation():
    assert mapping.normalize("  Be\u0301la  –  Dulice ") == mapping.normalize("Béla-Dulice")
    assert mapping.normalize("A B") != mapping.normalize("AB")
    assert mapping.normalize("A. B") != mapping.normalize("A B")
    assert mapping.normalize("n/Trnavou") != mapping.normalize("nad Trnavou")
    result = match(postal("Locality – Part"), [unit("Locality-Part"), unit("Locality - Part", "100002")])
    assert result["state"] == "AUTHORITATIVE_BUT_AMBIGUOUS"


def test_partial_row_coverage_cannot_be_reported_complete_and_multiple_parents_preserved():
    rows = [postal(), postal("Unknown")]
    results = [match(r) for r in rows]
    report = mapping.coverage(rows, results)[0]
    assert report["status"] == "PARTIAL" and report["mappedRows"] == report["unresolvedRows"] == 1
    rows[1] = postal("Other")
    results[1] = match(rows[1], [unit("Other", "100002")])
    report = mapping.coverage(rows, results)[0]
    assert report["status"] == "COMPLETE" and report["municipalityCodes"] == ["100001", "100002"]


def test_street_and_house_fields_never_leak_to_summary():
    row = postal(typZaznamu="ulica", ulica="SECRET STREET", dulica="SECRET STREET ID", poznamka="SECRET HOUSE RANGE")
    raw = mapping.serialized(mapping.coverage([row], [match(row)]))
    assert b"SECRET" not in raw and b'"ulica": 1' in raw


def synthetic_capture(tmp_path):
    capture, data = tmp_path / "capture", tmp_path / "data"
    capture.mkdir()
    data.mkdir()
    county = {"code": "SK0101", "note": "101", "officialTitle": "Okres Synthetic district", "mediumTitle": "Synthetic district",
              "shortTitle": "Synthetic district", "validFrom": "2004-08-01"}
    town = {"code": "SK0101100001", "note": "100001", "officialTitle": "Alpha", "mediumTitle": "Alpha", "shortTitle": "Alpha", "validFrom": "2004-08-01"}
    sources = {"districts": [county], "municipalities": [town], "psc": [postal("Alpha"), postal("Alpha", psc="12346", typZaznamu="ulica")]}
    manifest = {"profile": PROFILE, "startedAt": "2026-10-15T10:00:00Z", "acquiredAt": "2026-10-15T10:01:00Z", "openApiUrl": OPENAPI_URL, "sources": {}}
    for kind, rows in sources.items():
        raw = mapping.serialized(rows)
        (capture / (kind + ".json")).write_bytes(raw)
        manifest["sources"][kind] = {"url": URLS[kind], "status": 200, "contentType": "application/json", "file": kind + ".json",
            "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(), "rows": len(rows), "etag": None}
    manifest["manifestSha256"] = manifest_hash(manifest)
    (capture / "manifest.json").write_bytes(mapping.serialized(manifest))
    (data / "regions.json").write_bytes(mapping.serialized({"regions": [{"code": "SK010"}]}))
    (data / "municipalities.json").write_bytes(mapping.serialized({"municipalities": [{"code": "100001", "name": "Alpha", "districtCode": "SK0101", "regionCode": "SK010"}]}))
    regpj = tmp_path / "regpj.zip"
    write_regpj(regpj, [relationship()])
    basic_header = dict(zip("ABCDEFGH", ("DOBEC", "OBEC", "OKRES", "PSC", "DPOSTA", "POSTA", "KOD_OKR", "KRAJ")))
    detail_header = dict(zip("ABCDEFGH", ("OBEC", "OKRES", "KOD_OKR", "KRAJ", "PSC", "POSTA", "miestne pomenovanie", "Súpisné čísla")))
    part_header = dict(zip("ABCDE", ("kraj", "Okres", "Názov Obce", "Názov Miestnej časti", "Typ")))
    obce = xlsx({"obce": [(1, basic_header), (2, dict(zip("ABCDEFGH", ("Alpha", "Alpha", "Synthetic district", "12345", "Post", "Post", "101", "BL"))))],
        "detail SČ": [(1, {"A": "Title"}), (3, detail_header)], "miestne časti": [(1, {"A": "Title"}), (2, part_header)],
        "popis": [(1, {"A": "Synthetic description"})]})
    post = tmp_path / "post.zip"
    with zipfile.ZipFile(post, "w") as z:
        z.writestr("OBCE.xlsx", obce)
        z.writestr("ULICE.xlsx", xlsx({"ulice": []}))
        z.writestr("POBoxy.xlsx", b"synthetic unused P.O.BOX representation")
    evidence = tmp_path / "evidence.json"
    payload = {"profile": "psc-administrative-evidence-v1", "portalvsManifestSha256": manifest["manifestSha256"], "resources": {}}
    for kind, path in (("regpj", regpj), ("post", post)):
        raw = path.read_bytes()
        payload["resources"][kind] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    evidence.write_bytes(mapping.serialized(payload))
    return capture, data, regpj, post, evidence


def test_full_offline_analysis_deterministic_and_production_untouched(tmp_path, monkeypatch):
    capture, data, regpj, post, evidence = synthetic_capture(tmp_path)
    before = {p.name: p.read_bytes() for p in (mapping.ROOT / "data").glob("*.json")}
    def forbidden(*args, **kwargs):
        pytest.fail("network access attempted")
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)
    args = (capture / "manifest.json", capture, regpj, post, evidence)
    a = mapping.analyze(*args, data_dir=data)
    b = mapping.analyze(*args, data_dir=data)
    assert mapping.serialized(a) == mapping.serialized(b)
    assert a["coverage"]["pscCounts"] == {"COMPLETE": 2}
    assert a["researchOnly"] and not a["productionApproved"]
    assert before == {p.name: p.read_bytes() for p in (mapping.ROOT / "data").glob("*.json")}
    assert b"SYNTHETIC PRIVATE AUTHOR SECRET" not in mapping.serialized(a)
    with pytest.raises(ValueError, match="hash/size"):
        mapping.verify_resource(regpj, {"bytes": 1, "sha256": "0" * 64})


def test_cli_cannot_write_production_or_enable_production_mode(tmp_path):
    capture, data, regpj, post, evidence = synthetic_capture(tmp_path)
    args = ["--portalvs-manifest", str(capture / "manifest.json"), "--portalvs-capture", str(capture),
            "--regpj-zip", str(regpj), "--post-zip", str(post), "--evidence-manifest", str(evidence)]
    target = mapping.ROOT / "data/psc.json"
    before = target.read_bytes()
    assert mapping.main([*args, "--output", str(target)]) == 1
    assert target.read_bytes() == before
    assert mapping.main([*args, "--output", str(capture / "psc.json")]) == 1
    with pytest.raises(SystemExit):
        mapping.main([*args, "--output", str(tmp_path / "report.json"), "--write-production"])


def test_curated_blocker_tables_preserve_all_rows_and_missing_context():
    text = (mapping.ROOT / "docs/research/psc-administrative-mapping-diagnostics.md").read_text(encoding="utf-8")
    def rows(section):
        return [line.strip("| ").split(" | ") for line in section.splitlines() if line.startswith("| ")][2:]
    a = rows(text.split("## A.")[1].split("## B.")[0])
    b = rows(text.split("## B.")[1].split("## C.")[0])
    assert len(a) == 42 and len(b) == 63
    assert Counter(row[5] for row in a) == {"NO_MATCH": 40, "AMBIGUOUS": 1, "ZSJ_PARENT": 1}
    assert sum(int(row[1]) for row in b) == 3141
    assert sum(int(row[5]) for row in b) == 188
    assert sum(int(row[6]) for row in b) == 12
    assert sum(int(row[7]) for row in b) == 2941
    assert all(int(row[1]) == sum(int(row[i]) for i in (5, 6, 7)) for row in b)
    assert [row[4] for row in b if row[0] in {"96001", "96221"}] == ["BC + null(2)", "BC + null(10)"]
