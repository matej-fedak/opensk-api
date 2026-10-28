"""Grouped storage must never leak as a logical lookup match."""

import hashlib
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from main import app
from services.psc_service import (
    _primary_match_sort_key,
    index_psc_data,
    load_psc_records,
    lookup_psc,
)


@pytest.mark.parametrize("include", [False, True])
def test_real_grouped_lookup_parity_and_primary(include):
    client = TestClient(app)
    suffix = "?include=geography" if include else ""
    response = client.get("/v1/psc/01001" + suffix)
    assert response.status_code == 200
    lookup = response.json()["data"]
    listed = client.get("/v1/psc?psc=01001").json()["data"]["items"]
    searched = client.get("/v1/psc/search?q=01001").json()["data"]["items"]
    assert lookup["matchCount"] == len(lookup["matches"]) == 2
    assert {r["municipalityCode"] for r in lookup["matches"]} == {"517402", "517801"}
    flat = [{k: v for k, v in match.items() if k != "geography"} for match in lookup["matches"]]
    assert flat == sorted(listed, key=_primary_match_sort_key)
    assert sorted(flat, key=lambda r: r["municipalityCode"]) == sorted(searched, key=lambda r: r["municipalityCode"])
    assert all("matches" not in m and "matchCount" not in m for m in flat)
    assert {k: v for k, v in lookup.items() if k not in {"matches", "matchCount"}} == lookup["matches"][0]
    assert lookup == client.get("/v1/psc/01001" + suffix).json()["data"]
    if include:
        for match in lookup["matches"]:
            for kind in ("municipality", "district", "region"):
                assert match["geography"][kind]["code"] == match[kind + "Code"]
        assert lookup["geography"] == lookup["matches"][0]["geography"]


def test_all_indexed_matches_flat_and_single_match_preserved():
    assert sum(map(len, index_psc_data().values())) == len(load_psc_records()) == 3101
    for code, records in index_psc_data().items():
        assert all("matches" not in record for record in records)
        if len(records) == 1:
            result = lookup_psc(code)
            assert result["matchCount"] == 1
            assert result["matches"] == records


@pytest.mark.parametrize("url,status,code", [
    ("/v1/psc/99A99", 400, "INVALID_FORMAT"),
    ("/v1/psc/01001?include=bad", 400, "INVALID_FORMAT"),
    ("/v1/psc/99999", 404, "NOT_FOUND"),
])
def test_lookup_errors_unchanged(url, status, code):
    response = TestClient(app).get(url)
    assert response.status_code == status
    assert response.json()["error"]["code"] == code


def test_frozen_psc_and_corrected_body_cache():
    # Canonical Git bytes make this strict check independent of CRLF checkout.
    canonical = Path("data/psc.json").read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha256(canonical).hexdigest() == "db9cd5c2d833cec0d199f4a7199f9c13f77346572bbd1507503ce01774b0dc24"
    client = TestClient(app)
    response = client.get("/v1/psc/01001")
    etag = '"' + hashlib.sha256(response.content).hexdigest()[:32] + '"'
    assert response.headers["etag"] == etag
    assert response.headers["last-modified"] == "Tue, 02 Jun 2026 00:00:00 GMT"
    assert response.headers["cache-control"] == "public, max-age=86400"
    conditional = client.get("/v1/psc/01001", headers={"If-None-Match": etag})
    assert conditional.status_code == 304
    assert conditional.content == b""
