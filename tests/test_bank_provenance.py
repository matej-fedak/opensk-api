"""Normal bank/IBAN responses carry NBS provenance without runtime fetching."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import app
from schemas.banks import nbs_attribution
from schemas.common import BANKS_LAST_UPDATED, STATIC_CACHE_CONTROL
from services import bank_service
from scripts.smoke_test import _build_valid_slovak_iban

client = TestClient(app)
DATA = Path(__file__).resolve().parents[1] / "data" / "banks.json"
IBAN_PATH = "/v1/iban/validate/" + _build_valid_slovak_iban("1100", "0000000000000001")


@pytest.mark.parametrize("path", ["/v1/banks", "/v1/banks/1100", IBAN_PATH,
                                 "/v1/iban/validate/SK0009000000000000000001", "/v1/iban/validate/CZ6508000000192000145399"])
def test_normal_responses_expose_local_nbs_provenance(path):
    snapshot = json.loads(DATA.read_text(encoding="utf-8"))
    source = snapshot["metadata"]
    response = client.get(path)
    assert response.status_code == 200
    body = response.json()
    assert body["error"] is None
    metadata = body["metadata"]
    assert "Národná banka Slovenska" in metadata["source"]
    assert metadata["version"] == "v1"
    assert metadata["lastUpdated"] == source["lastUpdated"] == source["sourceEffectiveDate"] == BANKS_LAST_UPDATED
    for key in ("sourceVersion", "sourceEffectiveDate", "sourceUrl", "sourceFileUrl", "sourceSha256", "sourceBytes",
                "termsUrl", "attribution", "transformation"):
        assert metadata[key] == source[key]
    assert metadata["sourceDownloadedAt"] == source["downloadedAt"]
    assert metadata["sourceEffectiveDate"] != metadata["sourceDownloadedAt"][:10]
    if path.startswith("/v1/iban"):
        assert "OpenSK API / ISO 13616 IBAN checksum validation" in metadata["source"]
        assert "Slovak bank-code resolution from Národná banka Slovenska" in metadata["source"]
    else:
        assert "transformed by OpenSK API" in metadata["source"]


def test_refreshed_bank_values_and_iban_resolution():
    banks = client.get("/v1/banks").json()["data"]
    assert isinstance(banks, list) and len(banks) == 30
    by_code = {row["code"]: row for row in banks}
    assert by_code["9956"]["bic"] == by_code["9956"]["swift"] == "PYYUSK22"
    assert by_code["7930"]["name"] == "Bausparkasse Wüstenrot Aktiengesselschaft, pobočka zahraničnej banky"
    result = client.get(IBAN_PATH).json()["data"]
    assert result["checksumValid"] and result["valid"]
    assert result["bankCode"] == "1100" and result["bankName"] == by_code["1100"]["name"]
    assert client.get("/v1/iban/validate/SK0009000000000000000001").json()["data"]["checksumValid"] is False
    assert client.get("/v1/iban/validate/CZ6508000000192000145399").json()["data"]["supportedCountry"] is False


@pytest.mark.parametrize("path", ["/v1/banks", "/v1/banks/1100", IBAN_PATH])
def test_new_effective_date_and_conditional_cache(path):
    response = client.get(path)
    assert response.headers["Cache-Control"] == STATIC_CACHE_CONTROL
    assert response.headers["Last-Modified"] == "Thu, 08 Oct 2026 00:00:00 GMT"
    assert client.get(path, headers={"If-None-Match": response.headers["ETag"]}).status_code == 304
    assert client.get(path, headers={"If-Modified-Since": response.headers["Last-Modified"]}).status_code == 304
    assert client.get(path, headers={"If-Modified-Since": "Mon, 18 May 2026 00:00:00 GMT"}).status_code == 200


def test_provenance_comes_from_dataset_not_router_constants(tmp_path, monkeypatch):
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    metadata = payload["metadata"]
    metadata.update(sourceVersion="999", sourceEffectiveDate="2026-01-01", lastUpdated="2026-01-01",
                    downloadedAt="2026-01-02T01:02:03Z", attribution=nbs_attribution("999", "2026-01-01"))
    path = tmp_path / "synthetic-banks.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    bank_service.load_banks_data.cache_clear()
    monkeypatch.setattr(bank_service, "DATA_FILE", path)
    try:
        for url in ("/v1/banks", "/v1/banks/1100", IBAN_PATH):
            response = client.get(url).json()["metadata"]
            assert response["sourceVersion"] == "999" and response["sourceEffectiveDate"] == "2026-01-01"
            assert response["lastUpdated"] == "2026-01-01" and response["sourceDownloadedAt"] == "2026-01-02T01:02:03Z"
    finally:
        bank_service.load_banks_data.cache_clear()


def test_no_runtime_network_or_new_routes(monkeypatch):
    import socket
    monkeypatch.setattr(socket, "create_connection", lambda *a, **kw: pytest.fail("runtime network"))
    assert client.get("/v1/banks").status_code == 200
    assert client.get(IBAN_PATH).status_code == 200
    schema = app.openapi()
    assert sum("get" in operations for operations in schema["paths"].values()) == 39
    assert "/v1/banks/metadata" not in schema["paths"]
    assert schema["paths"]["/v1/banks"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]["$ref"].endswith("BanksResponse")
