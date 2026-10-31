"""Resolved reply and 0.23.8 refreshed-snapshot/provenance guards."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import app
from schemas.common import BANKS_LAST_UPDATED


def test_bank_catalogue_records_resolved_reply_and_current_snapshot() -> None:
    entry = TestClient(app).get("/v1/sources/banks").json()["data"]
    assert entry["licence"]["status"] == "verified"
    assert entry["licence"]["termsUrl"] == "https://nbs.sk/disclaimer-sk/"
    assert "NBS Terms of Use" in entry["licence"]["name"]
    assert entry["lastUpdated"] == BANKS_LAST_UPDATED == "2026-10-08"
    assert entry["lastChecked"] == "2026-10-15"
    assert "verzia 226" in entry["attribution"]
    assert "OpenSK" in entry["attribution"]
    assert any("not NBS data" in text for text in entry["limitations"])
    assert not {"reply", "correspondence", "nextAction", "notes"} & entry.keys()


def test_bank_snapshot_is_refreshed_with_audited_source_provenance() -> None:
    import json
    path = Path(__file__).resolve().parents[1] / "data" / "banks.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["metadata"]["sourceVersion"] == "226"
    assert payload["metadata"]["lastUpdated"] == payload["metadata"]["sourceEffectiveDate"] == BANKS_LAST_UPDATED
    assert payload["metadata"]["sourceSha256"] == "b82cd0c34d89ff1a68d710fedd3e8f509065a53ae605282ad4fc29234b74fc64"
    assert len(payload["banks"]) == 30
    assert sum(row["activeParty"] for row in payload["banks"]) == 21
    assert next(row for row in payload["banks"] if row["code"] == "9956")["bic"] == "PYYUSK22"


@pytest.mark.parametrize("sips,expected", [("x", (True, "C")), ("K", (True, "K")),
                                         ("Ø", (False, "Ø"))])
def test_participation_fields_read_sips_not_akt_uc(sips, expected) -> None:
    from scripts.import_banks import normalize_bank_record

    result = normalize_bank_record({
        "Payment system code SR": "123",
        "Payment service provider": "Synthetic test provider",
        "SWIFT 8": "ABCDSKBX",
        "Payment system SIPS": sips,
        "Akt. úč.": "deliberately contradictory source-column value",
    })
    assert result["code"] == "0123"
    assert (result["activeParty"], result["activePartyMarker"]) == expected


def test_bank_reply_does_not_resolve_holidays_or_other_outreach() -> None:
    client = TestClient(app)
    assert client.get("/v1/sources/holidays").json()["data"]["licence"]["status"] == "identified"
    for source in ("districts", "municipalities", "psc", "phoneAreas"):
        assert client.get(f"/v1/sources/{source}").json()["data"]["licence"]["status"] == "pending"
    # Elections were independently cleared by the ŠÚ SR reply, not the bank reply.
    assert client.get("/v1/sources/elections").json()["data"]["licence"]["status"] == "verified"
