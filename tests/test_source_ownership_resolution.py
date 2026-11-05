"""0.23.15 reply, ownership, acquisition-gate and frozen-production guards."""

import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient

from main import app
from schemas.common import PHONE_AREAS_LAST_UPDATED, PSC_LAST_UPDATED


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RESEARCH = ROOT / "docs" / "research"
client = TestClient(app)


def _registry() -> dict[str, object]:
    return json.loads((DATA / "sources.json").read_text(encoding="utf-8"))


def test_telecom_reply_is_scoped_and_publicly_verified() -> None:
    internal = _registry()["phoneAreas"]
    assert internal["licenceStatus"].startswith("verified 2026-11-02")
    assert internal["riskLevel"] == "low"
    assert internal["lastChecked"] == "2026-11-02"
    assert "requested OpenSK use scope" in internal["redistributionStatus"]
    assert "commercial downstream use" in internal["redistributionStatus"]
    assert "no formal licence name" in internal["licence"]

    public = client.get("/v1/sources/phoneAreas").json()["data"]
    assert public["status"] == "production"
    assert public["coverage"] == "complete"
    assert public["licence"] == {
        "status": "verified",
        "name": "Direct institutional reuse clarification (regulator reply, 2026-11-02); no formal licence named",
        "termsUrl": internal["sourceUrl"],
    }
    assert public["lastUpdated"] == PHONE_AREAS_LAST_UPDATED == "2026-09-15"
    assert public["lastChecked"] == "2026-11-02"
    assert "Zdroj: Úrad pre reguláciu" in public["attribution"]
    assert "not mandatory wording" in public["attribution"]
    assert len(public["limitations"]) == 3
    assert not {"notes", "nextAction", "riskLevel", "redistributionStatus"} & public.keys()


def test_telecom_resolution_does_not_refresh_or_rehash_production() -> None:
    payload = json.loads((DATA / "phone_areas.json").read_text(encoding="utf-8"))
    assert len(payload["phoneAreas"]) == 2922
    assert sum(row["municipalityCode"] is not None for row in payload["phoneAreas"]) == 2919
    assert sum(row["municipalityCode"] is None for row in payload["phoneAreas"]) == 3
    assert payload["metadata"]["lastUpdated"] == PHONE_AREAS_LAST_UPDATED == "2026-09-15"
    # The XLS digest is byte-exact. The converted CSV uses Git-style LF
    # normalization so the freeze guard is stable on Windows/Linux checkouts.
    # They identify retained repository bytes, not the historical acquisition
    # event. Neither the workbook nor its converted CSV was changed.
    expected = {
        "teleoff-phone-areas-30.xls": "380025e006ddba17b062538cb347bda88a559137c95c09ec0b4cb528d6b468e2",
        "teleoff-phone-areas-30.csv": "ebd9834bcf3f109b675874240fe20e146f54fd08ea5c4fedbc9a5851cf660639",
    }
    for name, digest in expected.items():
        raw = (DATA / "raw" / name).read_bytes()
        if name.endswith(".csv"):
            raw = raw.replace(b"\r\n", b"\n")
        assert hashlib.sha256(raw).hexdigest() == digest


def test_portalvs_redirect_does_not_upgrade_current_geography_or_psc() -> None:
    registry = _registry()
    for source_id in ("districts", "municipalities"):
        internal = registry[source_id]
        assert internal["licenceStatus"] == "pending verification"
        assert internal["termsUrl"] == "pending"
        assert internal["sourceUrl"].startswith("https://ciselniky2.portalvs.sk/")
        assert "REPLY_RECEIVED_REDIRECTED_TO_SOURCE_OWNER" in internal["notes"]
        assert "NO_GO_SUSR_GEOGRAPHY_REPLACEMENT" in internal["notes"]
        assert "MANUAL_SOURCE_FILES_REQUIRED" in internal["nextAction"]
        public = client.get(f"/v1/sources/{source_id}").json()["data"]
        assert public["licence"]["status"] == "pending"
        assert "does not grant PortalVS redistribution rights" in public["limitations"][0]

    psc = registry["psc"]
    assert psc["licenceStatus"] == "pending verification"
    assert psc["riskLevel"] == "high"
    assert psc["coverage"] == "partial"
    assert "NO_GO_SUCCESSOR_PSC" in psc["nextAction"]
    public_psc = client.get("/v1/sources/psc").json()["data"]
    assert public_psc["licence"]["status"] == "pending"
    assert public_psc["lastUpdated"] == PSC_LAST_UPDATED == "2026-06-02"
    assert "NO_GO_SUCCESSOR_PSC" in public_psc["limitations"][-1]


def test_geography_verdict_is_single_and_acquisition_gate_is_explicit() -> None:
    text = (RESEARCH / "source-ownership-resolution.md").read_text(encoding="utf-8")
    assert "NO_GO_SUSR_GEOGRAPHY_REPLACEMENT" in text
    assert "SUSR_GEOGRAPHY_FULL_REPLACEMENT" not in text
    assert "SUSR_GEOGRAPHY_PARTIAL_REPLACEMENT" not in text
    assert "MANUAL_SOURCE_FILES_REQUIRED" in text
    assert "SUSR_REUSE_VERIFIED" in text
    for identifier in ("CL000024", "CL000025", "0024", "0025"):
        assert identifier in text
    for mapping in ("SK031A", "SK042B", "SK03110", "SK04211"):
        assert mapping in text
    assert "REPLY_RECEIVED_REDIRECTED_TO_SOURCE_OWNER" in text
    assert "PORTALVS_REUSE_APPROVED" in text  # present only in an explicit no-claim sentence
    assert "No `PORTALVS_REUSE_APPROVED` claim is made" in " ".join(text.split())


def test_psc_source_owner_package_is_prepared_but_unsent() -> None:
    text = (RESEARCH / "slovenska-posta-psc-outreach.md").read_text(encoding="utf-8")
    assert "PREPARED_NOT_SENT" in text
    assert "NO_GO_SUCCESSOR_PSC" in text
    assert "zakaznickyservis@slposta.sk" in text
    assert "https://www.posta.sk/psc" in text
    assert "No email or other contact was sent by the agent" in text
    assert "13,700-row" in text
