"""Tiny invented classifier examples: not official captures or rights evidence."""

import copy
import csv
import hashlib
import io
import json
import socket
import subprocess
from datetime import date
from pathlib import Path

import pytest

from scripts import reconcile_susr_geography as tool


HEADERS = ["code", "officialTitle", "mediumTitle", "validFrom", "validTo", "info", "additionalInfo"]


def row(code, name, *, district="", region="", valid_to=""):
    return {"code": code, "officialTitle": name, "mediumTitle": name,
            "validFrom": "2020-01-01", "validTo": valid_to,
            "info": district, "additionalInfo": region}


def relationship(field):
    return {"field": field, "verified": True, "basis": "DIRECT_SOURCE_CODE_FIELD",
            "evidenceUrl": tool.SOURCE_PAGE,
            "description": "SYNTHETIC TEST ONLY: this invented field has coded parent semantics"}


def profile(kind):
    return {"id": tool.PROFILE, "reviewStatus": "REVIEWED_MANUAL_SOURCE",
            "districtIdDerivation": {"id": "opensk-district-namespace-v1", "verified": True,
                "evidenceUrl": tool.SOURCE_PAGE, "description": "SYNTHETIC TEST ONLY: invented reviewed code namespace"},
            "sourceNameField": "officialTitle",
            "regionRelationship": relationship("additionalInfo") if kind == "districts" else None,
            "districtRelationship": relationship("info") if kind == "municipalities" else None,
            "specialRows": {}}


def synthetic():
    sources = {
        "districts": {"rows": [row("101", "Alpha", region="1"), row("510", "Beta", region="5")],
                      "profile": profile("districts"), "day": date(2026, 11, 26)},
        "municipalities": {"rows": [row("500001", "Same", district="101"), row("500002", "Same", district="510")],
                           "profile": profile("municipalities"), "day": date(2026, 11, 26)},
    }
    baseline = {"districts": [
        {"code": "SK0101", "name": "Alpha", "regionCode": "SK010", "country": "SK"},
        {"code": "SK03110", "name": "Beta", "regionCode": "SK031", "country": "SK"}],
        "municipalities": [
            {"code": "500001", "name": "Same (okres Alpha)", "districtCode": "SK0101", "regionCode": "SK010", "country": "SK"},
            {"code": "500002", "name": "Same (okres Beta)", "districtCode": "SK03110", "regionCode": "SK031", "country": "SK"}],
    }
    return sources, baseline


def write_csv(path, rows, *, delimiter=";", encoding="utf-8", headers=HEADERS):
    text = io.StringIO(newline="")
    writer = csv.DictWriter(text, fieldnames=headers, delimiter=delimiter)
    writer.writeheader()
    writer.writerows({key: item.get(key, "") for key in headers} for item in rows)
    path.write_bytes(text.getvalue().encode(encoding))
    return path


def capture(tmp_path):
    sources, _ = synthetic()
    entries, paths = [], {}
    for code, (acronym, name, kind) in tool.CLASSIFIERS.items():
        path = write_csv(tmp_path / f"synthetic-{code}.csv", sources[kind]["rows"])
        _, observed = tool.observe_csv(path)
        entry = {"classifierCode": code, "acronym": acronym, "officialName": name,
                 "sourcePage": tool.SOURCE_PAGE, "downloadUrl": None, "manuallyAcquired": True,
                 "manuallyAcquiredAt": "2026-11-26", "timePrecision": "day", **observed,
                 "sourceVersion": None, "sourceValidity": None, "metadataDate": None,
                 "transformationProfile": sources[kind]["profile"]}
        entries.append(entry)
        paths[code] = path
    return {"profile": "susr-geography-manual-acquisition-v1", "sourceProfileStatus": "REVIEWED_MANUAL_FILES", "files": entries}, paths


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError("reconciliation must not perform network I/O")
    monkeypatch.setattr(socket, "create_connection", denied)
    monkeypatch.setattr(socket.socket, "connect", denied)


@pytest.mark.parametrize("classifier", ["0024", "0025"])
@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig"])
@pytest.mark.parametrize("delimiter", [";", ","])
def test_strict_csv_observation_preserves_codes_headers_and_unicode(tmp_path, classifier, encoding, delimiter):
    code = "101" if classifier == "0024" else "000123"
    path = write_csv(tmp_path / "synthetic.csv", [row(code, "Žltá obec")], delimiter=delimiter, encoding=encoding)
    rows, observed = tool.observe_csv(path, encoding=encoding, delimiter=delimiter)
    assert rows[0]["code"] == code
    assert rows[0]["officialTitle"] == "Žltá obec"
    assert observed["headers"] == HEADERS
    assert observed["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert observed["headerSha256"] == tool.header_hash(HEADERS)
    assert observed["rowCount"] == 1


def test_complete_manifest_selects_exact_classifiers_not_internal_cl_ids(tmp_path):
    manifest, paths = capture(tmp_path)
    sources, observations = tool.load_capture(manifest, paths)
    assert len(sources["districts"]["rows"]) == len(sources["municipalities"]["rows"]) == 2
    assert observations["districts"]["classifierCode"] == "0024"
    assert "CL000024" not in json.dumps(observations)


@pytest.mark.parametrize("mutation", ["duplicate", "missing", "unexpected", "bad_width", "code_whitespace", "empty_name", "bad_date"])
def test_bad_source_rows_or_schema_fail_closed(tmp_path, mutation):
    rows = [row("101", "Alpha")]
    headers = list(HEADERS)
    if mutation == "duplicate":
        rows.append(row("101", "Different name"))
    elif mutation == "missing":
        headers.remove("code")
    elif mutation == "unexpected":
        headers.append("guessedParent")
    elif mutation == "code_whitespace":
        rows[0]["code"] = " 101"
    elif mutation == "empty_name":
        rows[0]["officialTitle"] = ""
    elif mutation == "bad_date":
        rows[0]["validFrom"] = "2026-02-30"
    path = write_csv(tmp_path / "bad.csv", rows, headers=headers)
    if mutation == "bad_width":
        path.write_bytes(path.read_bytes() + b"too;few\n")
    with pytest.raises(ValueError):
        tool.observe_csv(path)


def test_wrong_delimiter_encoding_and_unrecorded_bom_fail(tmp_path):
    path = write_csv(tmp_path / "source.csv", [row("101", "Žltá")], encoding="utf-8-sig")
    with pytest.raises(ValueError, match="BOM"):
        tool.observe_csv(path)
    with pytest.raises(ValueError, match="schema"):
        tool.observe_csv(path, encoding="utf-8-sig", delimiter=",")
    with pytest.raises(ValueError, match="encoding/delimiter"):
        tool.observe_csv(path, encoding="cp1250")


@pytest.mark.parametrize("mutation", ["hash", "header", "manual", "identity", "profile", "relationship", "time", "path"])
def test_capture_metadata_or_unreviewed_semantics_cannot_bypass_gates(tmp_path, mutation):
    manifest, paths = capture(tmp_path)
    entry = manifest["files"][0]
    if mutation == "hash":
        entry["sha256"] = "0" * 64
    elif mutation == "header":
        entry["headers"].append("unobserved")
    elif mutation == "manual":
        entry["manuallyAcquired"] = False
    elif mutation == "identity":
        entry["classifierCode"] = "CL000024"
    elif mutation == "profile":
        manifest["sourceProfileStatus"] = "UNVERIFIED"
    elif mutation == "relationship":
        entry["transformationProfile"]["regionRelationship"]["verified"] = False
    elif mutation == "time":
        entry["manuallyAcquiredAt"] = "2099-01-01"
    elif mutation == "path":
        entry["localPath"] = str(paths["0024"])
    with pytest.raises(ValueError):
        tool.load_capture(manifest, paths)


def test_capture_requires_review_of_compatibility_derivation_not_just_matching_names(tmp_path):
    manifest, paths = capture(tmp_path)
    manifest["files"][0]["transformationProfile"].pop("districtIdDerivation")
    with pytest.raises(ValueError, match="derivation requires independent source review"):
        tool.load_capture(manifest, paths)


def test_unknown_profile_transform_cannot_be_silently_ignored(tmp_path):
    manifest, paths = capture(tmp_path)
    manifest["files"][0]["transformationProfile"]["nameOverride"] = "not supported"
    with pytest.raises(ValueError, match="unexpected transformation"):
        tool.load_capture(manifest, paths)


def test_no_name_join_duplicate_names_and_distinct_display_names():
    sources, baseline = synthetic()
    report = tool.reconcile(sources, baseline)
    assert report["technicalVerdict"] == "SUSR_TECHNICAL_FULL_REPLACEMENT_READY"
    assert report["rightsVerdict"] == "RIGHTS_CONFIRMATION_PENDING"
    assert report["remainingPortalVSOnlyDependencies"] == 0
    assert report["datasets"]["municipalities"]["nameOnlyDifferences"] == 2
    assert report["datasets"]["municipalities"]["displayOnlyOpenSKChanges"] == 2
    first, second = report["datasets"]["municipalities"]["records"]
    assert first["SOURCE_NAME"] == second["SOURCE_NAME"] == "Same"
    assert first["candidate"]["districtCode"] != second["candidate"]["districtCode"]
    assert first["fieldCategories"]["regionCode"] == "DETERMINISTIC_DERIVATION_FROM_SUSR"

    sources["municipalities"]["rows"][0]["code"] = "500099"
    report = tool.reconcile(sources, baseline)
    assert "500001" in report["datasets"]["municipalities"]["unmatchedProductionCodes"]
    assert report["technicalVerdict"] is None  # source-only row must be classified first
    assert report["datasets"]["municipalities"]["matched"] == 1


def test_absent_relationship_evidence_never_falls_back_to_production():
    sources, baseline = synthetic()
    sources["municipalities"]["profile"]["districtRelationship"] = None
    report = tool.reconcile(sources, baseline)
    assert report["technicalVerdict"] == "SUSR_TECHNICAL_PARTIAL_REPLACEMENT_READY"
    assert report["remainingPortalVSOnlyDependencies"] > 0
    assert all(item["candidate"]["districtCode"] is None for item in report["datasets"]["municipalities"]["records"])
    assert all(item["candidate"]["name"] is None for item in report["datasets"]["municipalities"]["records"])


@pytest.mark.parametrize("region", ["7", "SK041"])
def test_relationship_conflicts_are_not_repaired_from_names_or_baseline(region):
    sources, baseline = synthetic()
    sources["municipalities"]["profile"]["regionRelationship"] = relationship("additionalInfo")
    sources["municipalities"]["rows"][0]["additionalInfo"] = region
    with pytest.raises(ValueError, match="conflicting"):
        tool.reconcile(sources, baseline)


def test_all_source_only_special_rows_retained_with_attributes():
    sources, baseline = synthetic()
    sources["municipalities"]["rows"].extend([
        row("999999", "Synthetic foreign", district="101"),
        row("TECH", "Synthetic technical", district="101"),
        row("500003", "Synthetic retired", district="101", valid_to="2020-12-31"),
    ])
    for code, category in [("999999", "FOREIGN_PSEUDO"), ("TECH", "TECHNICAL")]:
        sources["municipalities"]["profile"]["specialRows"][code] = {
            "classification": category, "reviewed": True, "reason": "invented fixture decision",
            "evidenceFields": ["code", "officialTitle"],
        }
    report = tool.reconcile(sources, baseline)
    rows = report["datasets"]["municipalities"]["sourceOnlyRows"]
    assert {item["classification"] for item in rows} == {"FOREIGN_PSEUDO", "TECHNICAL", "INACTIVE"}
    assert all(item["sourceAttributes"]["officialTitle"] for item in rows)
    assert report["datasets"]["municipalities"]["sourceRows"] == 5
    assert report["technicalVerdict"] == "SUSR_TECHNICAL_FULL_REPLACEMENT_READY"


def test_special_row_rule_cannot_discard_a_current_identity():
    sources, baseline = synthetic()
    sources["municipalities"]["profile"]["specialRows"]["500001"] = {"classification": "OUT_OF_SCOPE", "reviewed": True}
    with pytest.raises(ValueError, match="overlaps"):
        tool.reconcile(sources, baseline)


def test_compatibility_formatter_is_code_only_for_all_twelve_aliases():
    for official, (_, expected) in tool.COMPATIBILITY.items():
        assert tool.district_public_id(official) == expected
    assert len(tool.COMPATIBILITY) == 12
    with pytest.raises(ValueError):
        tool.district_public_id("SK031A")


def test_deterministic_comparison_does_not_mutate_inputs():
    sources, baseline = synthetic()
    before = copy.deepcopy((sources, baseline))
    first = tool.reconcile(sources, baseline)
    second = tool.reconcile(sources, baseline)
    assert first == second
    assert (sources, baseline) == before
    for source in sources.values():
        source["rows"].reverse()
    assert tool.reconcile(sources, baseline) == first


def test_observation_does_not_claim_manual_origin_or_guessed_times(tmp_path):
    _, paths = capture(tmp_path)
    report = tool.inspect_files(paths, delimiter=";")
    assert report["acquisitionStatus"] == "OBSERVATION_ONLY"
    assert report["technicalVerdict"] is None
    for entry in report["files"]:
        assert entry["manuallyAcquired"] is None
        assert entry["manuallyAcquiredAt"] is None
        assert entry["timePrecision"] is None
        assert not any(str(tmp_path) in value for value in entry.values() if isinstance(value, str))


def test_special_units_and_both_reviewed_presentation_codes_are_not_dropped():
    sources, baseline = synthetic()
    for old, new in [("500001", "504173"), ("500002", "504742")]:
        for item in sources["municipalities"]["rows"] + baseline["municipalities"]:
            if item["code"] == old:
                item["code"] = new
    for code, name in [("528595", "Synthetic city part B"), ("599891", "Synthetic city part K"),
                       ("518638", "Synthetic military unit")]:
        sources["municipalities"]["rows"].append(row(code, name, district="101"))
        baseline["municipalities"].append({"code": code, "name": name, "districtCode": "SK0101",
                                           "regionCode": "SK010", "country": "SK"})
    report = tool.reconcile(sources, baseline)
    assert report["datasets"]["municipalities"]["matched"] == 5
    assert report["specialUnitRetention"]["military units"]["518638"] is True
    assert all(report["reviewedPresentationCodes"][code] is not None for code in ("504173", "504742"))
    assert report["technicalVerdict"] == "SUSR_TECHNICAL_FULL_REPLACEMENT_READY"


def test_default_dry_run_blocks_without_real_sources_and_does_not_write(tmp_path, capsys):
    output = tmp_path / "must-not-exist.json"
    assert tool.main(["--output", str(output)]) == 2
    report = json.loads(capsys.readouterr().out)
    assert report["acquisitionStatus"] == "MANUAL_SOURCE_FILES_REQUIRED"
    assert report["technicalVerdict"] is None
    assert report["remainingPortalVSOnlyDependencies"] is None
    assert report["baselineCounts"] == {"districts": 79, "municipalities": 2927}
    assert not output.exists()


def test_diagnostics_cannot_write_production_or_escape_generated(tmp_path, monkeypatch):
    monkeypatch.setattr(tool, "ROOT", tmp_path)
    generated = tmp_path / "data/generated"
    generated.mkdir(parents=True)
    monkeypatch.setattr(tool, "GENERATED", generated)
    for path in (tmp_path / "data/districts.json", generated / "../municipalities.json", generated / "data.csv"):
        with pytest.raises(ValueError, match="diagnostics"):
            tool.write_diagnostics(path, {})
    output = generated / "report.json"
    tool.write_diagnostics(output, {"productionWrites": False})
    assert json.loads(output.read_text()) == {"productionWrites": False}


def test_cli_has_no_production_mode():
    with pytest.raises(SystemExit):
        tool.main(["--write-production"])
    with pytest.raises(SystemExit):
        tool.main(["--dry-run", "--write-diagnostics"])


def test_raw_classifier_files_are_not_tracked():
    tracked = subprocess.check_output(["git", "ls-files"], cwd=tool.ROOT, text=True).splitlines()
    assert not [name for name in tracked if Path(name).suffix.lower() in {".csv", ".xml", ".zip"}
                and any(token in name.lower() for token in ("lsuj", "susr-geography", "0024", "0025"))]
