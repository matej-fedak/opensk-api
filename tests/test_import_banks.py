"""Synthetic local NBS importer/provenance/column-audit regressions."""

import copy
import hashlib

import pytest

from schemas.banks import NBS_LICENSE, NBS_SOURCE_URL, NBS_TERMS_URL
from scripts.import_banks import compare_bank_snapshots, run_import
from scripts.validate_datasets import validate_banks_payload

OPTIONS = {"source_version": "226", "effective_date": "2026-10-08",
           "downloaded_at": "2026-10-15T16:00:00Z",
           "source_file_url": "https://nbs.sk/dokument/synthetic-bank-source.csv?force=true"}
EN_HEADER = "Payment system code SR;Payment service provider;SWIFT 8;Payment system SIPS;Akt. úč.\n"
SK_HEADER = "Kód platobného styku;Poskytovateľ platobných služieb;SWIFT kód 8;Systém SIPS;Akt. úč.\n"


def source(tmp_path, rows="123;Synthetic bank;TESTSKBX;x;Ø\n", *, slovak=False):
    path = tmp_path / "source.csv"
    header = "Prevodník identifikačných kódov SR;;;\n" + SK_HEADER if slovak else EN_HEADER
    path.write_text(header + rows, encoding="utf-8-sig")
    return path


def test_explicit_provenance_and_technical_conversion(tmp_path):
    path = source(tmp_path, slovak=True)
    result = run_import(input_path=path, output_path=tmp_path / "banks.json", **OPTIONS, write=True)
    assert result.ok, result.errors
    metadata = result.payload["metadata"]
    assert metadata["sourceVersion"] == "226"
    assert metadata["sourceEffectiveDate"] == metadata["lastUpdated"] == "2026-10-08"
    assert metadata["downloadedAt"] == OPTIONS["downloaded_at"]
    assert metadata["sourceFileUrl"] == OPTIONS["source_file_url"]
    assert metadata["sourceUrl"] == NBS_SOURCE_URL and metadata["termsUrl"] == NBS_TERMS_URL
    assert metadata["sourceSha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert metadata["sourceBytes"] == len(path.read_bytes())
    assert metadata["license"] == NBS_LICENSE and "pending" not in metadata["license"].lower()
    assert "verzia 226" in metadata["attribution"] and "2026-10-08" in metadata["attribution"]
    assert "not the original NBS file" in metadata["transformation"]
    assert result.payload["banks"][0] == {"code": "0123", "name": "Synthetic bank", "bic": "TESTSKBX",
        "swift": "TESTSKBX", "activeParty": True, "activePartyMarker": "C", "alphabeticCode": None, "country": "SK"}


@pytest.mark.parametrize("field", ["source_version", "effective_date", "downloaded_at", "source_file_url"])
def test_explicit_source_metadata_required(tmp_path, field):
    path = source(tmp_path)
    kwargs = dict(OPTIONS)
    kwargs.pop(field)
    with pytest.raises(ValueError, match="required"):
        run_import(input_path=path, **kwargs)


@pytest.mark.parametrize("field,value", [("source_version", ""), ("source_version", "not-a-version"),
    ("effective_date", "2026-02-30"), ("downloaded_at", "2026-10-15"),
    ("downloaded_at", "2026-10-15T16:00:00"), ("source_file_url", "https://example.com/banks.csv")])
def test_invalid_provenance_rejected(tmp_path, field, value):
    with pytest.raises(ValueError):
        run_import(input_path=source(tmp_path), **dict(OPTIONS, **{field: value}))


@pytest.mark.parametrize("slovak", [False, True])
@pytest.mark.parametrize("marker,active,normalized,akt", [("x", True, "C", "Ø"), ("", False, "Ø", "C"),
    ("K", True, "K", "Ø"), ("Ø", False, "Ø", "C")])
def test_sips_is_used_not_contradictory_akt_uc(tmp_path, slovak, marker, active, normalized, akt):
    result = run_import(input_path=source(tmp_path, f"0012;Synthetic bank;TESTSKBX;{marker};{akt}\n", slovak=slovak), **OPTIONS)
    assert result.ok, result.errors
    row = result.payload["banks"][0]
    assert row["code"] == "0012"
    assert (row["activeParty"], row["activePartyMarker"]) == (active, normalized)


@pytest.mark.parametrize("rows,error", [
    ("123;Synthetic bank;TESTSKBX;?;C\n", "unknown active-party"),
    ("123;Synthetic bank;bad;C;C\n", "bic/swift"),
    ("123;Synthetic bank;TESTSKBX;x;C\n123;Synthetic duplicate;OTERSKBX;x;C\n", "duplicate bank code"),
    ("123;Synthetic bank;TESTSKBX;x;C\n124;Synthetic duplicate;TESTSKBX;x;C\n", "duplicate BIC"),
])
def test_invalid_source_never_overwrites_output(tmp_path, rows, error):
    target = tmp_path / "banks.json"
    target.write_bytes(b"existing maintainer snapshot")
    result = run_import(input_path=source(tmp_path, rows), output_path=target, **OPTIONS, write=True)
    assert not result.ok and any(error in message for message in result.errors)
    assert target.read_bytes() == b"existing maintainer snapshot"


def test_unknown_source_columns_fail_closed(tmp_path):
    path = source(tmp_path)
    path.write_text(path.read_text(encoding="utf-8-sig").replace("Payment system SIPS", "Unknown field"), encoding="utf-8")
    with pytest.raises(ValueError, match="source-column review"):
        run_import(input_path=path, **OPTIONS)


def test_cp1250_source_values_are_preserved(tmp_path):
    path = source(tmp_path, "123;Syntetická banka;TESTSKBX;x;0\n", slovak=True)
    path.write_bytes(path.read_text(encoding="utf-8-sig").encode("cp1250"))
    result = run_import(input_path=path, **OPTIONS)
    assert result.ok, result.errors
    assert result.payload["banks"][0]["name"] == "Syntetická banka"
    assert result.payload["metadata"]["sourceSha256"] == hashlib.sha256(path.read_bytes()).hexdigest()


def test_deterministic_order_and_no_network(tmp_path, monkeypatch):
    import socket
    monkeypatch.setattr(socket, "create_connection", lambda *a, **k: pytest.fail("network used"))
    path = source(tmp_path, "124;Synthetic B;BBBBSKBX;x;Ø\n123;Synthetic A;AAAASKBX;;C\n")
    target = tmp_path / "banks.json"
    first = run_import(input_path=path, output_path=target, **OPTIONS, write=True)
    raw = target.read_bytes()
    second = run_import(input_path=path, output_path=target, **OPTIONS, write=True)
    assert first.ok and second.ok and target.read_bytes() == raw
    assert [row["code"] for row in first.payload["banks"]] == ["0123", "0124"]


def test_refresh_comparison_exposes_all_source_changes(tmp_path):
    current = run_import(input_path=source(tmp_path, "123;Synthetic new;NEWBSKBX;x;Ø\n125;Synthetic added;ADDDSKBX;x;Ø\n"), **OPTIONS).payload
    previous = copy.deepcopy(current)
    previous["metadata"].update(sourceVersion="225", lastUpdated="2026-05-18")
    previous["banks"][0].update(name="Synthetic old", bic="OLDBSKBX", swift="OLDBSKBX", activeParty=False, activePartyMarker="Ø")
    previous["banks"][1]["code"] = "0124"
    report = compare_bank_snapshots(previous, current)
    assert report["previousSourceVersion"] == "225" and report["newSourceVersion"] == "226"
    assert report["previousRecordCount"] == report["newRecordCount"] == 2
    assert report["addedCodes"] == ["0125"] and report["removedCodes"] == ["0124"]
    assert report["changedCodes"] == ["0123"]
    for field in ("bicChanges", "providerNameChanges", "sipsProjectionChanges"):
        assert [row["code"] for row in report[field]] == ["0123"]
    assert report["activeProjectionCount"] == 2 and report["inactiveProjectionCount"] == 0


@pytest.mark.parametrize("field,value", [("source", ""), ("sourceUrl", "https://example.com"),
    ("termsUrl", "https://nbs.sk/other/"), ("sourceVersion", ""), ("sourceEffectiveDate", "invalid"),
    ("downloadedAt", "2026-10-15"), ("sourceSha256", "A"*64), ("license", "Source/licence verification pending."),
    ("attribution", ""), ("transformation", ""), ("lastUpdated", "2026-10-15"), ("complete", False), ("complete", 1)])
def test_validator_rejects_missing_or_invalid_production_metadata(tmp_path, field, value):
    payload = run_import(input_path=source(tmp_path), **OPTIONS).payload
    for mutation in ("invalid", "missing"):
        candidate = copy.deepcopy(payload)
        if mutation == "invalid":
            candidate["metadata"][field] = value
        else:
            candidate["metadata"].pop(field)
        assert not validate_banks_payload(candidate, tmp_path / "banks.json").ok
