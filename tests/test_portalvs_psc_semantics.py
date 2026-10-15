"""Synthetic offline research only; no live sources, imports or promotion."""

import copy
import hashlib
import json
import zipfile
from xml.etree import ElementTree as ET

import pytest

from scripts import analyze_portalvs_psc_successor as analysis
from scripts import acquire_portalvs_successor as acquisition


def county(note="101", name="District A"):
    region = analysis.REGIONS[note[0]][0]
    return {"code": region + format(int(note[1:]), "X"), "note": note,
            "officialTitle": "Okres " + name, "mediumTitle": name, "shortTitle": name, "validFrom": "2004-08-01"}


def town(code="100001", name="Synthetic alpha", district="SK0101", **extra):
    return dict({"code": district + code, "note": code, "officialTitle": name, "mediumTitle": name,
                 "shortTitle": name, "validFrom": "2004-08-01"}, **extra)


def postal(name="Synthetic alpha", code="12345", kind="obec", **extra):
    return dict({"psc": code, "obce": name, "typZaznamu": kind, "kodOkresu": "101", "kraj": "BL",
                 "dposta": "Synthetic delivery post", "posta": "Synthetic delivery post", "name_translations": []}, **extra)


def sources(*, towns=None, counties=None, rows=None):
    return {"districts": counties if counties is not None else [county()],
            "municipalities": towns if towns is not None else [town()], "psc": rows if rows is not None else [postal()]}


def run(source, **kwargs):
    return analysis.analyze_sources(source, snapshot_date="2026-10-15", **kwargs)


def test_normalized_title_is_candidate_not_production_mapping():
    result = run(sources(towns=[town(name="Synthetic-Alpha")], rows=[postal(name="SYNTHETIC - Alpha")]))
    assert result["baselineUnresolvedRows"] == 1
    item = result["unresolvedNonStreet"][0]
    assert item["classification"] == "ALTERNATE_OFFICIAL_NAME"
    assert item["normalizedCandidates"] == ["100001"]
    assert item["candidateTownFields"][0]["officialTitle"] == "Synthetic-Alpha"
    assert item["automaticMappingApproved"] is False


def test_district_context_disambiguates_equal_names():
    result = run(sources(counties=[county(), county("102", "District B")],
                         towns=[town(), town("100002", district="SK0102")],
                         rows=[postal(kodOkresu="102")]))
    assert result["baselineUnresolvedRows"] == 0
    assert result["geography"]["disambiguatedNames"] == 2


def test_multiple_candidates_stay_ambiguous():
    result = run(sources(towns=[town(), town("100002")]))
    item = result["unresolvedNonStreet"][0]
    assert item["classification"] == "AMBIGUOUS" and item["normalizedCandidates"] == ["100001", "100002"]
    assert item["exactCandidates"] == ["100001", "100002"]
    assert not item["automaticMappingApproved"]


def test_no_fuzzy_substring_delivery_post_or_district_only_fallback():
    result = run(sources(rows=[postal(name="Synthetic alphx", dposta="Synthetic alpha"),
                               postal(name="Synthetic alpha - sublocality", code="12346")]))
    assert result["baselineUnresolvedRows"] == 2
    assert all(item["classification"] == "UNRESOLVED" for item in result["unresolvedNonStreet"])


def test_types_coverage_and_street_free_summaries():
    street = postal(code="12346", kind="ulica", ulica="SYNTHETIC STREET SECRET", dulica="SYNTHETIC DELIVERY STREET",
                    poznamka="SYNTHETIC HOUSE DETAILS")
    result = run(sources(rows=[postal(), postal(kind="detail_sc"), street]))
    assert result["sourceTypes"] == {"obec": 1, "detail_sc": 1, "ulica": 1}
    assert result["nonStreetPscCount"] == result["ulicaOnlyPscCount"] == 1
    assert result["typeCoexistence"] == {"detail_sc+obec": 1, "ulica": 1}
    assert result["ulicaOnly"][0]["classification"] == "SAFE_TO_COLLAPSE_CANDIDATE"
    assert not result["ulicaOnly"][0]["productionCollapseApproved"]
    raw = analysis.serialized(result)
    assert b"SYNTHETIC STREET SECRET" not in raw and b"SYNTHETIC DELIVERY STREET" not in raw and b"SYNTHETIC HOUSE DETAILS" not in raw


def test_shared_street_psc_is_multi_municipality():
    result = run(sources(towns=[town(), town("100002", "Synthetic beta")],
        rows=[postal(kind="ulica", kodOkresu=None), postal(name="Synthetic beta", kind="ulica", kodOkresu=None)]))
    item = result["ulicaOnly"][0]
    assert item["classification"] == "MULTI_MUNICIPALITY" and item["allRowsDeterministicallyMapped"]
    assert len(item["candidateMunicipalities"]) == 2
    assert item["sourceDistrictCount"] == 0 and item["candidateDistricts"] == ["SK0101"]


def test_ulica_unknown_and_ambiguous_context_not_guessed():
    result = run(sources(towns=[town(), town("100002")], rows=[postal(kind="ulica", kodOkresu=None),
                     postal(name="Synthetic missing", kind="ulica", code="12346", kodOkresu=None)]))
    assert result["ulicaOnlyClassifications"] == {"AMBIGUOUS": 1, "INSUFFICIENT_EVIDENCE": 1}


@pytest.mark.parametrize("row", [postal(kind="future-type"), postal(kodOkresu="999"), postal(kraj="BC")])
def test_unknown_type_or_conflicting_context_fails_closed(row):
    with pytest.raises(ValueError):
        run(sources(rows=[row]))


def post_stub(*, basic=None, parts=None):
    return {"url": analysis.POST_ZIP_URL, "bytes": 123, "sha256": "a"*64,
            "basic": basic or [], "parts": parts or [], "detail": []}


def test_publisher_paired_label_is_evidence_not_handwritten_alias():
    post = post_stub(basic=[{"postalLocality": "Synthetic abbr.", "deliveryLocality": "Synthetic alpha", "district": "101",
                            "psc": "12345", "row": 4, "deliveryPost": "Synthetic post"}])
    result = run(sources(rows=[postal(name="Synthetic abbr.")]), post=post)
    item = result["unresolvedNonStreet"][0]
    assert item["normalizedCandidates"] == [] and item["publisherCandidates"] == ["100001"]
    assert item["classification"] == "DELIVERY_LOCALITY"
    assert item["evidence"][0]["kind"] == "PAIRED_POSTAL_LABEL"
    assert not item["automaticMappingApproved"]


def test_publisher_locality_part_relation_is_explicit():
    post = post_stub(parts=[{"municipality": "Synthetic alpha", "locality": "Synthetic part", "districtName": "District A", "row": 3}])
    result = run(sources(rows=[postal(name="Synthetic part")]), post=post)
    item = result["unresolvedNonStreet"][0]
    assert item["classification"] == "MUNICIPALITY_PART" and item["publisherCandidates"] == ["100001"]
    assert item["evidence"][0]["sheet"] == "miestne časti"


def test_ambiguous_publisher_parts_not_resolved_by_delivery_post():
    post = post_stub(parts=[{"municipality": "Synthetic alpha", "locality": "Synthetic part", "districtName": "District A", "row": 3},
                            {"municipality": "Synthetic beta", "locality": "Synthetic part", "districtName": "District A", "row": 4}])
    result = run(sources(towns=[town(), town("100002", "Synthetic beta")],
                         rows=[postal(name="Synthetic part", dposta="Synthetic alpha")]), post=post)
    assert result["unresolvedNonStreet"][0]["classification"] == "AMBIGUOUS"


def test_dropping_rows_causes_visible_undercoverage():
    result = run(sources(rows=[postal(), postal(name="Synthetic missing"), postal(name="Synthetic missing", code="12346")]))
    assert result["affectedPscCount"] == 2
    coverage = result["coverageDiagnosticsNotApprovedForProduction"]
    assert coverage["affectedPscsWithSomeExactRows"] == coverage["affectedPscsLostByExactOnly"] == 1
    assert coverage["baselineExactPscs"] == 1 and coverage["nonStreetAllRowsIdeal"] == 2


def test_deterministic_reports_and_no_network(monkeypatch):
    import socket
    import urllib.request
    monkeypatch.setattr(socket, "create_connection", lambda *a, **kw: pytest.fail("network used"))
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **kw: pytest.fail("network used"))
    s = sources(towns=[town(), town("100002", "Synthetic beta")], rows=[postal(), postal(name="Synthetic beta", code="12346")])
    before = copy.deepcopy(s)
    a = analysis.serialized(run(s))
    for rows in s.values():
        rows.reverse()
    assert analysis.serialized(run(s)) == a
    for rows in s.values():
        rows.reverse()
    assert s == before


@pytest.mark.parametrize("note,expected", [("510", "SK03110"), ("511", "SK03111"), ("610", "SK03210"),
    ("611", "SK03211"), ("612", "SK03212"), ("613", "SK03213"), ("710", "SK04110"), ("711", "SK04111"),
    ("712", "SK04112"), ("713", "SK04113"), ("810", "SK04210"), ("811", "SK04211")])
def test_all_twelve_district_reletterings_are_prototypes_only(note, expected):
    result = analysis.geography_prototypes([county(note)], [], "2026-10-15")
    assert list(result["districts"]) == [expected]
    assert result["relettered"][0]["publicCode"] == expected


def test_pseudo_and_retired_exclusions_keep_statistical_town_ids():
    pseudo_county = dict(county(), code="SKZZZZ", note="")
    pseudo_town = dict(town(), code="SKZZZZZZZZZZ", note="")
    retired = town("523551", "Synthetic retired", validTo="2010-12-31")
    result = analysis.geography_prototypes([county(), pseudo_county], [town(), pseudo_town, retired], "2026-10-15")
    assert list(result["municipalities"]) == ["100001"]
    assert result["districtsExcludedPseudo"] == result["townsExcludedPseudo"] == result["townsExcludedRetired"] == 1


@pytest.mark.parametrize("kind", ["duplicate-county", "county-conflict", "duplicate-town", "town-conflict"])
def test_prototypes_reject_unknown_or_duplicate_identities(kind):
    c, t = [county()], [town()]
    if kind == "duplicate-county":
        c.append(county())
    if kind == "county-conflict":
        c[0]["code"] = "SK031A"
    if kind == "duplicate-town":
        t.append(town())
    if kind == "town-conflict":
        t[0]["code"] = "SK9999100001"
    with pytest.raises(ValueError):
        analysis.geography_prototypes(c, t, "2026-10-15")


def capture(tmp_path):
    directory = tmp_path / "capture"
    directory.mkdir()
    manifest = {"profile": acquisition.PROFILE, "startedAt": "2026-10-15T10:00:00Z", "acquiredAt": "2026-10-15T10:01:00Z",
                "openApiUrl": acquisition.OPENAPI_URL, "sources": {}}
    for kind, rows in sources().items():
        raw = json.dumps(rows).encode()
        (directory / (kind + ".json")).write_bytes(raw)
        manifest["sources"][kind] = {"url": acquisition.URLS[kind], "status": 200, "contentType": "application/json",
            "file": kind + ".json", "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(), "rows": len(rows), "etag": None}
    manifest["manifestSha256"] = acquisition.manifest_hash(manifest)
    path = directory / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


def test_capture_hashes_are_checked(tmp_path):
    path = capture(tmp_path)
    manifest, data = analysis.load_capture(path)
    assert data == sources()
    (path.parent / "psc.json").write_bytes(b"changed synthetic data")
    with pytest.raises(ValueError, match="hash/size"):
        analysis.load_capture(path)


def test_cli_cannot_write_production(tmp_path):
    path = capture(tmp_path)
    target = analysis.ROOT / "data" / "psc.json"
    before = target.read_bytes()
    assert analysis.main(["--manifest", str(path), "--output", str(target)]) == 1
    assert target.read_bytes() == before
    with pytest.raises(SystemExit):
        analysis.main(["--manifest", str(path), "--write-production"])


def test_acquisition_is_offline_in_tests_and_rejects_repository_output(tmp_path):
    calls = []
    def fake_fetch(url):
        calls.append(url)
        return b'[{"synthetic":true}]', {"url": url, "status": 200, "contentType": "application/json", "etag": '"test"', "acquiredAt": "2026-10-15T10:00:00Z"}
    manifest = acquisition.acquire(tmp_path / "raw", fetcher=fake_fetch, sleep=lambda _: None)
    assert calls == list(acquisition.URLS.values()) and len(manifest["sources"]) == 3
    assert manifest["manifestSha256"] == acquisition.manifest_hash(manifest)
    with pytest.raises(ValueError, match="outside"):
        acquisition.acquire(acquisition.ROOT / "data" / "raw" / "successor")
    with pytest.raises(ValueError, match="fixed"):
        acquisition.fetch("https://example.com/town.json")


def test_xlsx_reader_drops_house_and_author_cells(tmp_path):
    # Minimal XLSX/ZIP source, all synthetic, no openpyxl/runtime dependency.
    ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    relns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    strings = []
    def sheet(rows):
        root = ET.Element("worksheet", xmlns=ns)
        data = ET.SubElement(root, "sheetData")
        for number, values in rows:
            r = ET.SubElement(data, "row", r=str(number))
            for col, value in values.items():
                strings.append(value)
                c = ET.SubElement(r, "c", r=f"{col}{number}", t="s")
                ET.SubElement(c, "v").text = str(len(strings)-1)
        return ET.tostring(root)
    sheets = {
        "obce": sheet([(2, {"A": "Synthetic alpha", "B": "Synthetic abbr.", "G": "101", "D": "123 45", "E": "Synthetic post"})]),
        "detail SČ": sheet([(4, {"A": "Synthetic alpha", "C": "101", "E": "123 45", "H": "SYNTHETIC HOUSE SECRET"})]),
        "popis": sheet([(1, {"A": "Synthetic publisher description"})]),
        "miestne časti": sheet([(3, {"B": "District A", "C": "Synthetic alpha", "D": "Synthetic part"})]),
    }
    street_sheet = sheet([(2, {"G": "Synthetic alpha", "B": "SYNTHETIC STREET SECRET", "C": "123 45",
                              "D": "Synthetic delivery post", "F": "SYNTHETIC STREET HOUSE SECRET"})])
    shared = ET.Element("sst", xmlns=ns)
    for value in strings:
        ET.SubElement(ET.SubElement(shared, "si"), "t").text = value
    book = ET.Element("workbook", xmlns=ns)
    records = ET.SubElement(book, "sheets")
    rels = ET.Element("Relationships", xmlns="http://schemas.openxmlformats.org/package/2006/relationships")
    import io
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as z:
        for i, (name, raw) in enumerate(sheets.items(), 1):
            ET.SubElement(records, "sheet", name=name, attrib={f"{{{relns}}}id": f"rId{i}"})
            ET.SubElement(rels, "Relationship", Id=f"rId{i}", Target=f"worksheets/sheet{i}.xml")
            z.writestr(f"xl/worksheets/sheet{i}.xml", raw)
        z.writestr("xl/workbook.xml", ET.tostring(book))
        z.writestr("xl/_rels/workbook.xml.rels", ET.tostring(rels))
        z.writestr("xl/sharedStrings.xml", ET.tostring(shared))
        z.writestr("docProps/core.xml", "SYNTHETIC PRIVATE AUTHOR SECRET")
    path = tmp_path / "post.zip"
    street_buffer = io.BytesIO()
    with zipfile.ZipFile(street_buffer, "w") as z:
        z.writestr("xl/worksheets/sheet1.xml", street_sheet)
        z.writestr("xl/sharedStrings.xml", ET.tostring(shared))
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("OBCE.xlsx", buffer.getvalue())
        z.writestr("ULICE.xlsx", street_buffer.getvalue())
    result = analysis.read_post_workbook(path)
    text = json.dumps(result)
    assert "SYNTHETIC HOUSE SECRET" not in text and "SYNTHETIC PRIVATE AUTHOR SECRET" not in text
    assert result["basic"][0]["psc"] == "12345" and result["parts"][0]["locality"] == "Synthetic part"
    assert "SYNTHETIC STREET SECRET" not in text and "SYNTHETIC STREET HOUSE SECRET" not in text
    report = run(sources(rows=[postal(kind="ulica", ulica="SYNTHETIC STREET SECRET")]), post=result)
    assert report["postEvidence"]["ulicaSignatureMatches"] == report["postEvidence"]["streetRows"] == 1
    assert b"SYNTHETIC STREET SECRET" not in analysis.serialized(report)
    assert result["streetSignatureHashes"][0].encode() not in analysis.serialized(report)


def test_curated_historical_tables_are_complete_and_consistent():
    text = (analysis.ROOT / "docs/research/portalvs-psc-successor-diagnostics.md").read_text(encoding="utf-8")
    sections = text.split("## ")[1:]
    tables = [[line.strip("| ").split(" | ") for line in section.splitlines() if line.startswith("| ")][2:]
              for section in sections]
    a, b, c = tables
    assert len(a) == 82 and sum(int(row[4]) for row in a) == 84
    assert sum(int(row[4]) for row in a if row[2] == "obec") == 65
    assert sum(int(row[4]) for row in a if row[2] == "detail_sc") == 19
    assert len(b) == 122 and sum(int(row[1]) for row in b) == 5770
    assert all(int(row[2]) == len(row[5].split("; ")) for row in b)
    assert all(row[3] == "0" and row[4] == "1" for row in b)
    assert len(c) == 69 and sum(int(row[2]) for row in c) == 84
    assert sum(row[3] == "yes" for row in c) == 16


@pytest.mark.parametrize("fault", ["url", "path", "manifest-hash", "row-count"])
def test_manifest_tampering_is_rejected(tmp_path, fault):
    path = capture(tmp_path)
    manifest = json.loads(path.read_bytes())
    if fault == "url":
        manifest["sources"]["psc"]["url"] = "https://example.com/data.json"
    if fault == "path":
        manifest["sources"]["psc"]["file"] = "../psc.json"
    if fault == "manifest-hash":
        manifest["manifestSha256"] = "0" * 64
    if fault == "row-count":
        manifest["sources"]["psc"]["rows"] = 999
    if fault != "manifest-hash":
        manifest["manifestSha256"] = acquisition.manifest_hash(manifest)
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError):
        analysis.load_capture(path)


@pytest.mark.parametrize("status", [301, 302, 403, 404])
def test_acquisition_rejects_redirects_and_permanent_errors(monkeypatch, status):
    from urllib.error import HTTPError
    class Opener:
        def open(self, *args, **kwargs):
            raise HTTPError(acquisition.URLS["psc"], status, "synthetic", {}, None)
    monkeypatch.setattr(acquisition, "build_opener", lambda *args: Opener())
    monkeypatch.setattr(acquisition.time, "sleep", lambda _: pytest.fail("unexpected retry"))
    with pytest.raises(ValueError, match=f"HTTP {status}"):
        acquisition.fetch(acquisition.URLS["psc"])
    assert acquisition.NoRedirect().redirect_request(None, None, status, "", {}, "https://example.com") is None


def test_acquisition_network_retries_are_bounded(monkeypatch):
    calls, delays = [], []
    class Opener:
        def open(self, *args, **kwargs):
            calls.append(1)
            raise TimeoutError("synthetic")
    monkeypatch.setattr(acquisition, "build_opener", lambda *args: Opener())
    monkeypatch.setattr(acquisition.time, "sleep", delays.append)
    with pytest.raises(ValueError, match="budget exhausted"):
        acquisition.fetch(acquisition.URLS["psc"])
    assert len(calls) == 3 and delays == [1, 2]
