"""Milestone-wide frozen surface and honest missing-evidence guards."""

import hashlib
import json
import re
import socket
from pathlib import Path

from fastapi.testclient import TestClient

from main import app
from schemas.common import DISTRICTS_LAST_UPDATED, MUNICIPALITIES_LAST_UPDATED, PSC_LAST_UPDATED
from scripts import reconcile_susr_geography as tool


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "docs/research"
MANIFEST = json.loads((RESEARCH / "susr-geography-acquisition.json").read_text(encoding="utf-8"))


def test_every_served_dataset_except_intentional_registry_evidence_is_frozen():
    expected = MANIFEST["baseline"]["productionSha256GitLf"]
    actual = {path.name: hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
              for path in (ROOT / "data").glob("*.json") if path.name != "sources.json"}
    assert len(actual) == 14
    assert actual == expected
    assert DISTRICTS_LAST_UPDATED == MUNICIPALITIES_LAST_UPDATED == "2026-10-16"
    assert PSC_LAST_UPDATED == "2026-06-02"


def test_exact_operation_inventory_namespace_and_envelope_unchanged():
    operations = sorted([[method.upper(), path, operation["operationId"]]
                         for path, item in app.openapi()["paths"].items()
                         for method, operation in item.items() if method == "get"])
    expected = json.loads((ROOT / "tests/fixtures/public-operations.json").read_text())
    assert operations == sorted(expected)
    assert len(operations) == 42
    assert hashlib.sha256(json.dumps(operations, separators=(",", ":")).encode()).hexdigest() == MANIFEST["baseline"]["operationInventorySha256"]
    assert all(path == "/" or path.startswith("/v1/") for _, path, _ in operations)
    client = TestClient(app)
    for url in ("/", "/v1/health", "/v1/districts", "/v1/municipalities?limit=1", "/v1/psc?limit=1", "/v1/sources"):
        response = client.get(url)
        assert response.status_code == 200
        assert response.json()["metadata"]["version"] == "v1"


def test_production_special_units_displays_and_compatibility_ids_preserved():
    districts = json.loads((ROOT / "data/districts.json").read_text(encoding="utf-8"))["districts"]
    municipalities = json.loads((ROOT / "data/municipalities.json").read_text(encoding="utf-8"))["municipalities"]
    assert len(districts) == 79 and len(municipalities) == 2927
    assert sum(bool(re.search(r" \(okres [^)]+\)$", row["name"])) for row in municipalities) == 205
    assert {public for _, public in tool.COMPATIBILITY.values()} <= {row["code"] for row in districts}
    assert sum(row["districtCode"] in {"SK0101", "SK0102", "SK0103", "SK0104", "SK0105"} for row in municipalities) == 17
    assert sum(row["districtCode"] in {"SK0422", "SK0423", "SK0424", "SK0425"} for row in municipalities) == 22
    assert {"500267", "518581", "518638", "504173", "504742"} <= {row["code"] for row in municipalities}


def test_manifest_pins_all_protected_datasets_and_exact_operation_inventory():
    baseline = MANIFEST["baseline"]
    protected = baseline["productionSha256GitLf"]
    assert set(protected) == {p.name for p in (ROOT / "data").glob("*.json")} - {"sources.json"}
    for name, digest in protected.items():
        raw = (ROOT / "data" / name).read_bytes().replace(b"\r\n", b"\n")
        assert hashlib.sha256(raw).hexdigest() == digest, name
    operations = sorted([method.upper(), path, entry["operationId"]]
                        for path, item in app.openapi()["paths"].items()
                        for method, entry in item.items() if method == "get")
    assert len(operations) == baseline["getOperations"] == 42
    raw = json.dumps(operations, separators=(",", ":")).encode()
    assert hashlib.sha256(raw).hexdigest() == baseline["operationInventorySha256"]


def test_absent_files_are_not_invented_source_evidence_or_a_final_verdict(monkeypatch):
    def denied(*args, **kwargs):
        raise AssertionError("no network allowed")

    monkeypatch.setattr(socket.socket, "connect", denied)
    assert MANIFEST["files"] == []
    assert MANIFEST["acquisitionStatus"] == "MANUAL_SOURCE_FILES_REQUIRED"
    assert MANIFEST["technicalVerdict"] is None
    report = tool.run_reconciliation()
    assert report["technicalVerdict"] is None
    assert report["sourceRows"] is None
    assert report["districtsReconciled"] is report["municipalitiesReconciled"] is None
    assert report["remainingPortalVSOnlyDependencies"] is None
    assert report["rightsVerdict"] == "RIGHTS_CONFIRMATION_PENDING"


def test_reply_followup_and_rights_have_separate_honest_states():
    evidence = MANIFEST["sourceIdentityEvidence"]
    assert evidence["replyReceivedOn"] == "2026-11-20"
    assert evidence["state"] == "REPLY_RECEIVED_TECHNICAL_SOURCE_CONFIRMED_RIGHTS_ESCALATION_REQUIRED"
    assert evidence["followUp"]["sentOn"] == "2026-11-27"
    assert evidence["followUp"]["state"] == "SENT_AWAITING_REPLY"
    assert evidence["followUp"]["recipientUnit"] is None
    assert evidence["followUp"]["competentUnitRoutingConfirmed"] is False
    assert MANIFEST["classifierSpecificApplicability"] == "CLASSIFIER_SPECIFIC_APPLICABILITY_PENDING"
    assert MANIFEST["rightsVerdict"] == "RIGHTS_CONFIRMATION_PENDING"
    rights = (RESEARCH / "susr-geography-rights.md").read_text(encoding="utf-8")
    for token in ("2026-10-13", "GENERAL_SUSR_TERMS_SUPPORT_CC_BY_4_0", "excessively burdens", "third-party"):
        assert token in rights
    guide = (RESEARCH / "susr-geography-reconciliation.md").read_text(encoding="utf-8")
    assert all(f"| {number} |" in guide for number in range(1, 28))
    assert "Agent sent any email? | **NO**" in guide


def test_acquisition_manifest_does_not_contain_absolute_machine_paths():
    text = (RESEARCH / "susr-geography-acquisition.json").read_text(encoding="utf-8")
    assert not re.search(r"(?<![A-Za-z])[A-Za-z]:[\\/]", text)
    assert "localPath" not in text
