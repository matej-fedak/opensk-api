"""Successor geography only; synthetic source inputs, never live/retained raw."""

import copy
import hashlib
import json
import shutil
import socket
from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from scripts import acquire_portalvs_successor as acquisition
from scripts import import_portalvs_geography as importer

ROOT = Path(__file__).resolve().parents[1]
PSC_SHA = "4b7346bbef19a86576fa5ecaa5f7d7c2afa36be5ff711753281b3a042b42bc55"
# Git stores LF; existing Windows core.autocrlf checkout uses CRLF. Both are
# pinned exact bytes, not normalized JSON. Import tests ALSO require byte-for-
# byte equality with their own pre-import snapshot on every platform.
PSC_GIT_SHA = "db9cd5c2d833cec0d199f4a7199f9c13f77346572bbd1507503ce01774b0dc24"
STAMP = "2020-01-02T10:00:00Z"


def row(code, note, name, *, county=False):
    result = dict.fromkeys(importer.SCHEMA, "")
    result.update(code=code, note=note, sortNumber=1, officialTitle=("Okres " if county else "") + name,
                  mediumTitle=name, shortTitle=name, validFrom="2004-08-01")
    return result


def county(note="101", name="Synthetic district"):
    return row(importer.REGIONS[note[0]][0] + format(int(note[1:]), "X"), note, name, county=True)


def town(code="100001", name="Synthetic town", district="SK0101"):
    return row(district + code, code, name)


def transform(counties=None, towns=None):
    return importer.transform(counties if counties is not None else [county()],
                              towns if towns is not None else [town()], date(2026, 10, 16),
                              {v[0] for v in importer.REGIONS.values()})


def test_ordinary_district_and_six_digit_town_output():
    records, report = transform()
    assert records["districts"] == [{"code": "SK0101", "name": "Synthetic district", "regionCode": "SK010", "country": "SK"}]
    assert records["municipalities"][0]["code"] == "100001"
    assert records["municipalities"][0]["districtCode"] == "SK0101"
    assert "SK0101100001" not in json.dumps(records)


@pytest.mark.parametrize("note", ["510", "511", "610", "611", "612", "613", "710", "711", "712", "713", "810", "811"])
def test_all_twelve_reletterings_verify_note_title_and_region(note):
    source = county(note)
    records, report = transform([source], [town(district=source["code"])])
    canonical = importer.REGIONS[note[0]][0] + str(int(note[1:]))
    assert records["districts"][0]["code"] == canonical
    assert records["municipalities"][0]["districtCode"] == canonical
    assert report["reletterings"][0] == {"sourceCode": source["code"], "statisticalCode": note,
                                         "canonicalCode": canonical, "name": "Synthetic district"}


@pytest.mark.parametrize("change", [{"note": "102"}, {"code": "SK9999"}, {"note": "110"},
    {"officialTitle": "Okres Different"}, {"shortTitle": "Different"}, {"validTo": "2010-12-31"},
    {"validFrom": "2099-01-01"}, {"newField": "unreviewed"}, {"mediumTitle": None}])
def test_county_evidence_conflicts_or_schema_drift_fail(change):
    source = dict(county(), **change)
    with pytest.raises(ValueError):
        transform([source])


def test_duplicate_statistical_and_canonical_district_identity_rejected():
    with pytest.raises(ValueError, match="duplicate district"):
        transform([county(), county()])
    with pytest.raises(ValueError):
        transform([county(), dict(county(), code="SK0102")])


def test_pseudo_exclusion_is_explicit_and_verified():
    foreign_county = row("SKZZZZ", "", "Zahraničie")
    foreign_town = row("SKZZZZZZZZZZ", "", "Zahraničie")
    records, report = transform([county(), foreign_county], [town(), foreign_town])
    assert report["excludedPseudo"] == {"districts": 1, "municipalities": 1}
    assert len(records["districts"]) == len(records["municipalities"]) == 1
    for bad in (dict(foreign_county, note="101"), dict(foreign_county, code="SKZZZ")):
        with pytest.raises(ValueError):
            transform([county(), bad])
    with pytest.raises(ValueError, match="duplicate pseudo"):
        transform([county(), foreign_county, foreign_county])
    with pytest.raises(ValueError, match="pseudo town evidence"):
        transform(towns=[town(), dict(foreign_town, officialTitle="Unreviewed")])


@pytest.mark.parametrize("change", [{"note": "12345"}, {"note": "999999"}, {"code": "SK0102100001"},
    {"code": "SK9999100001"}, {"code": "SK010100100001"}, {"newField": "unreviewed"}])
def test_town_unknown_identity_suffix_or_district_fails(change):
    with pytest.raises(ValueError):
        transform(towns=[dict(town(), **change)])


def test_duplicate_town_id_fails():
    with pytest.raises(ValueError, match="duplicate municipality"):
        transform(towns=[town(), town()])


def test_duplicate_names_are_suffixed_but_unique_names_stay_plain():
    records, report = transform([county(), county("102", "Synthetic B")],
        [town(), town("100002", district="SK0102"), town("100003", "Unique")])
    names = {r["code"]: r["name"] for r in records["municipalities"]}
    assert names == {"100001": "Synthetic town (okres Synthetic district)",
                     "100002": "Synthetic town (okres Synthetic B)", "100003": "Unique"}
    assert report["disambiguatedNames"] == 2


def test_deterministic_serialization_independent_of_source_order():
    c, t = [county(), county("102", "Synthetic B")], [town(), town("100002", district="SK0102")]
    assert importer.serialize(transform(c, t)) == importer.serialize(transform(c[::-1], t[::-1]))


@pytest.fixture
def prepared(tmp_path, monkeypatch):
    """Reconstruct SYNTHETIC county/town rows from public output, not source dumps."""
    data, raw = tmp_path / "data", tmp_path / "raw"
    data.mkdir()
    raw.mkdir()
    for path in (ROOT / "data").glob("*.json"):
        shutil.copyfile(path, data / path.name)
    monkeypatch.setattr(importer, "PRODUCTION_DIR", data)
    districts = json.loads((data / "districts.json").read_bytes())["districts"]
    municipalities = json.loads((data / "municipalities.json").read_bytes())["municipalities"]
    inverse = {v[0]: k for k, v in importer.REGIONS.items()}
    counties = [county(inverse[r["regionCode"]] + f"{int(r['code'][5:]):02d}", r["name"]) for r in districts]
    source_by_public = {r["code"]: source["code"] for r, source in zip(districts, counties)}
    towns = []
    for r in municipalities:
        name = r["name"].split(" (okres ")[0]
        if r["code"] == "504742":
            name = "Radošovce"
        towns.append(town(r["code"], name, source_by_public[r["districtCode"]]))
    source = {"districts": counties + [row("SKZZZZ", "", "Zahraničie")],
              "municipalities": towns + [row("SKZZZZZZZZZZ", "", "Zahraničie")]}
    # Always exercise the migration from the two old display labels.
    payload = json.loads((data / "municipalities.json").read_bytes())
    for r in payload["municipalities"]:
        if r["code"] in importer.REVIEWED_NAMES:
            r["name"] = importer.REVIEWED_NAMES[r["code"]][0]
    (data / "municipalities.json").write_bytes(importer.serialize(payload))
    manifest = {"profile": acquisition.GEOGRAPHY_PROFILE, "startedAt": STAMP, "acquiredAt": STAMP,
                "openApiUrl": acquisition.OPENAPI_URL, "sources": {}}
    def save():
        for kind, rows in source.items():
            content = importer.serialize(rows)
            (raw / (kind + ".json")).write_bytes(content)
            manifest["sources"][kind] = {"url": acquisition.URLS[kind], "status": 200,
                "contentType": "application/json; charset=utf-8", "etag": '"synthetic"', "file": kind + ".json",
                "acquiredAt": STAMP, "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest(),
                "rows": len(rows), "schemaKeys": sorted(set().union(*(r.keys() for r in rows)))}
        manifest["manifestSha256"] = acquisition.manifest_hash(manifest)
        (raw / "manifest.json").write_bytes(importer.serialize(manifest))
    save()
    return data, raw, source, save


def content(data):
    return {p.name: p.read_bytes() for p in data.glob("*.json")}


def test_default_dry_run_stages_all_validates_and_never_uses_network(prepared, monkeypatch):
    data, raw, source, save = prepared
    before = content(data)
    monkeypatch.setattr(socket, "create_connection", lambda *a, **kw: pytest.fail("network attempted"))
    report = importer.run_import(raw / "manifest.json", raw)
    assert report["dryRun"] and report["pscStoredMatchLinks"] == 3101
    assert report["districts"]["oldCount"] == report["districts"]["newCount"] == 79
    assert report["municipalities"]["newCount"] == 2927
    assert {v["code"] for v in report["municipalities"]["recordChanges"]} == {"504173", "504742"}
    assert report["disambiguatedNames"] == 205
    assert content(data) == before


def test_success_replaces_both_only_and_is_repeatable(prepared):
    data, raw, source, save = prepared
    before = content(data)
    importer.run_import(raw / "manifest.json", raw, write=True)
    after = content(data)
    assert {k for k in before if before[k] != after[k]} == {"districts.json", "municipalities.json"}
    assert after["psc.json"] == before["psc.json"]
    assert hashlib.sha256(after["psc.json"]).hexdigest() in {PSC_SHA, PSC_GIT_SHA}
    for kind in importer.KINDS:
        metadata = json.loads(after[kind + ".json"])["metadata"]
        assert metadata["lastUpdated"] == "2020-01-02" and metadata["downloadedAt"] == STAMP
        assert metadata["sourceUrl"] == acquisition.URLS[kind]
    names = {r["code"]: r["name"] for r in json.loads(after["municipalities.json"])["municipalities"]}
    assert names["504173"] == "Vozokany (okres Galanta)"
    assert names["504742"] == "Radošovce (okres Skalica)"
    importer.run_import(raw / "manifest.json", raw, write=True)
    assert content(data) == after and not (data / importer.TRANSACTION).exists()


@pytest.mark.parametrize("kind", importer.KINDS)
def test_invalid_candidate_never_partially_writes(prepared, kind):
    data, raw, source, save = prepared
    before = content(data)
    source[kind][0]["note"] = "999999"
    save()
    with pytest.raises(ValueError):
        importer.run_import(raw / "manifest.json", raw, write=True)
    assert content(data) == before


@pytest.mark.parametrize("kind", importer.KINDS)
def test_unreviewed_name_diff_stops_before_write(prepared, kind):
    data, raw, source, save = prepared
    before = content(data)
    source[kind][0]["officialTitle"] = "Okres Unreviewed" if kind == "districts" else "Unreviewed"
    source[kind][0]["mediumTitle"] = source[kind][0]["shortTitle"] = "Unreviewed"
    save()
    with pytest.raises(ValueError, match="STOP for review"):
        importer.run_import(raw / "manifest.json", raw, write=True)
    assert content(data) == before


def test_second_replace_failure_rolls_back_first(prepared, monkeypatch):
    data, raw, source, save = prepared
    before = content(data)
    replace = importer.os.replace
    def failure(src, dest):
        if Path(src).name == "municipalities.new":
            raise OSError("synthetic second replacement failure")
        return replace(src, dest)
    monkeypatch.setattr(importer.os, "replace", failure)
    with pytest.raises(OSError):
        importer.run_import(raw / "manifest.json", raw, write=True)
    assert content(data) == before and not (data / importer.TRANSACTION).exists()


def test_staged_validation_failure_leaves_production_unchanged(prepared, monkeypatch):
    data, raw, source, save = prepared
    before = content(data)
    def invalid(stage):
        raise ValueError("synthetic failed staged validation")
    monkeypatch.setattr(importer, "validate_datasets_before_write", invalid)
    with pytest.raises(ValueError, match="staged validation"):
        importer.run_import(raw / "manifest.json", raw, write=True)
    assert content(data) == before


def test_surrounding_reference_failure_is_not_ignored(prepared):
    data, raw, source, save = prepared
    payload = json.loads((data / "procurement_notices.json").read_bytes())
    payload["syntheticReference"] = {"municipalityCode": "999999"}
    (data / "procurement_notices.json").write_bytes(importer.serialize(payload))
    before = content(data)
    with pytest.raises(ValueError, match="cross-dataset"):
        importer.run_import(raw / "manifest.json", raw, write=True)
    assert content(data) == before


def test_interrupted_prepared_transaction_requires_explicit_recovery(prepared):
    data, raw, source, save = prepared
    before = content(data)
    journal = data / importer.TRANSACTION
    journal.mkdir()
    state = {"state": "prepared", "before": {}}
    for kind in importer.KINDS:
        original = before[kind + ".json"]
        (journal / (kind + ".old")).write_bytes(original)
        state["before"][kind] = hashlib.sha256(original).hexdigest()
    (journal / "state.json").write_bytes(importer.serialize(state))
    (data / "districts.json").write_bytes(b"synthetic interrupted replacement")
    with pytest.raises(ValueError, match="pending transaction"):
        importer.run_import(raw / "manifest.json", raw)
    importer.recover_production()
    assert content(data) == before and not journal.exists()


def test_interrupted_committed_cleanup_does_not_require_deleted_backups(prepared):
    data, raw, source, save = prepared
    before = content(data)
    journal = data / importer.TRANSACTION
    journal.mkdir()
    state = {"state": "committed", "after": {k: hashlib.sha256(before[k + ".json"]).hexdigest() for k in importer.KINDS}}
    (journal / "state.json").write_bytes(importer.serialize(state))
    importer.recover_production()
    assert content(data) == before and not journal.exists()


@pytest.mark.parametrize("fault", ["url", "hash", "count", "schema", "psc", "path"])
def test_manifest_and_source_verification(prepared, fault):
    data, raw, source, save = prepared
    manifest = json.loads((raw / "manifest.json").read_bytes())
    entry = manifest["sources"]["districts"]
    if fault == "url":
        entry["url"] = acquisition.URLS["psc"]
    elif fault == "hash":
        entry["sha256"] = "0" * 64
    elif fault == "count":
        entry["rows"] += 1
    elif fault == "schema":
        entry["schemaKeys"] = []
    elif fault == "psc":
        manifest["sources"]["psc"] = copy.deepcopy(entry)
    elif fault == "path":
        entry["file"] = "../districts.json"
    manifest["manifestSha256"] = acquisition.manifest_hash(manifest)
    (raw / "manifest.json").write_bytes(importer.serialize(manifest))
    before = content(data)
    with pytest.raises(ValueError):
        importer.run_import(raw / "manifest.json", raw, write=True)
    assert content(data) == before


def test_geography_acquisition_never_requests_psc(tmp_path):
    called = []
    def fetch(url):
        called.append(url)
        return b'[{"synthetic":true}]', {"url": url, "status": 200, "contentType": "application/json", "acquiredAt": STAMP}
    manifest = acquisition.acquire(tmp_path / "raw", geography_only=True, fetcher=fetch, sleep=lambda _: None)
    assert called == [acquisition.URLS[k] for k in importer.KINDS]
    assert manifest["profile"] == acquisition.GEOGRAPHY_PROFILE
    assert set(manifest["sources"]) == set(importer.KINDS)


def test_current_production_snapshot_and_psc_freeze():
    sources = json.loads((ROOT / "data/sources.json").read_bytes())
    assert hashlib.sha256((ROOT / "data/psc.json").read_bytes()).hexdigest() in {PSC_SHA, PSC_GIT_SHA}
    psc = json.loads((ROOT / "data/psc.json").read_bytes())
    assert {"83006", "83155", "91931", "93539", "97651"} <= set(psc)
    assert sources["psc"]["sourceUrl"] == "https://ciselniky.portalvs.sk/classifier/show/42/"
    assert sources["psc"]["sourceName"] == "PortalVS classifier 42 (PSČ obcí SR a ČR)"
    assert hashlib.sha256(json.dumps(sources["psc"], ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest() == "9a72cd6fa891ad312612b9caab22234916761dd030e4c1e9e45fcc8c4e5e0462"
    from schemas.common import PSC_LAST_UPDATED
    assert PSC_LAST_UPDATED == "2026-06-02"
    assert len(json.loads((ROOT / "data/districts.json").read_bytes())["districts"]) == 79
    assert len(json.loads((ROOT / "data/municipalities.json").read_bytes())["municipalities"]) == 2927


@pytest.mark.parametrize("url", ["/v1/districts", "/v1/districts/SK03110", "/v1/municipalities", "/v1/municipalities/504173"])
def test_geography_caching_after_migration(url):
    from main import app
    from schemas.common import STATIC_CACHE_CONTROL
    client = TestClient(app)
    response = client.get(url)
    assert response.status_code == 200 and response.json()["metadata"]["version"] == "v1"
    assert response.headers["cache-control"] == STATIC_CACHE_CONTROL
    assert response.headers["last-modified"] == "Fri, 16 Oct 2026 00:00:00 GMT"
    assert client.get(url, headers={"If-None-Match": response.headers["etag"]}).status_code == 304
    assert client.get(url, headers={"If-Modified-Since": response.headers["last-modified"]}).status_code == 304
    assert client.get(url, headers={"If-Modified-Since": "Thu, 15 Oct 2026 00:00:00 GMT"}).status_code == 200
    from services.http_cache import make_etag
    from starlette.responses import JSONResponse
    old = response.json()
    old["metadata"]["lastUpdated"] = "2026-05-27"
    assert response.headers["etag"] != make_etag(JSONResponse(old).body)


def test_public_source_catalogue_is_intentionally_mixed():
    from main import app
    client = TestClient(app)
    for kind in importer.KINDS:
        entry = client.get("/v1/sources/" + kind).json()["data"]
        assert entry["source"] == {"name": importer.SOURCE_NAMES[kind], "url": acquisition.URLS[kind]}
        assert entry["lastUpdated"] == "2026-10-16" and entry["licence"]["status"] == "pending"
    psc = client.get("/v1/sources/psc").json()["data"]
    assert psc["source"]["url"] == "https://ciselniky.portalvs.sk/classifier/show/42/"
    assert psc["lastUpdated"] == "2026-06-02" and psc["licence"]["status"] == "pending"


def test_psc_caching_and_body_remain_historical():
    from main import app
    from services.psc_service import load_psc_records
    client = TestClient(app)
    for url in ("/v1/psc/01001", "/v1/psc?psc=01001", "/v1/psc/stats"):
        response = client.get(url)
        assert response.status_code == 200 and response.json()["metadata"]["lastUpdated"] == "2026-06-02"
        assert response.headers["last-modified"] == "Tue, 02 Jun 2026 00:00:00 GMT"
        assert client.get(url, headers={"If-None-Match": response.headers["etag"]}).status_code == 304
    # Historical embedded labels are intentionally not rewritten.
    assert any(r["municipality"] == "Vozokany (okres (Galanta)" for r in load_psc_records())


def test_preserve_external_changes_detected_before_commit(prepared, monkeypatch):
    data, raw, source, save = prepared
    validate = importer.validate_datasets_before_write
    modified = b"synthetic concurrent maintainer edit"
    def external_edit(stage):
        validate(stage)
        (data / "districts.json").write_bytes(modified)
    monkeypatch.setattr(importer, "validate_datasets_before_write", external_edit)
    original_towns = (data / "municipalities.json").read_bytes()
    with pytest.raises(ValueError, match="context changed"):
        importer.run_import(raw / "manifest.json", raw, write=True)
    assert (data / "districts.json").read_bytes() == modified
    assert (data / "municipalities.json").read_bytes() == original_towns
