"""Reply/correspondence projection and no-refresh guards for PR #33."""

import hashlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import app
from schemas.common import BANKS_LAST_UPDATED


def test_bank_catalogue_records_resolved_reply_without_refresh() -> None:
    entry = TestClient(app).get("/v1/sources/banks").json()["data"]
    assert entry["licence"]["status"] == "verified"
    assert entry["licence"]["termsUrl"] == "https://nbs.sk/disclaimer-sk/"
    assert "NBS Terms of Use" in entry["licence"]["name"]
    assert entry["lastUpdated"] == BANKS_LAST_UPDATED == "2026-05-18"
    assert entry["lastChecked"] == "2026-10-14"
    assert "verzia 225" in entry["attribution"]
    assert "OpenSK" in entry["attribution"]
    assert any("not NBS data" in text for text in entry["limitations"])
    assert not {"reply", "correspondence", "nextAction", "notes"} & entry.keys()


def test_bank_snapshot_is_unchanged_v225() -> None:
    # Explicit no-refresh scope guard. A future approved refresh must update it.
    path = Path(__file__).resolve().parents[1] / "data" / "banks.json"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == (
        "8bd46f255f6e06f29a14217a760f19e9cee29d1309fe306e8685c6c640ade514"
    )


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
    for source in ("districts", "municipalities", "psc", "phoneAreas", "elections"):
        assert client.get(f"/v1/sources/{source}").json()["data"]["licence"]["status"] == "pending"
