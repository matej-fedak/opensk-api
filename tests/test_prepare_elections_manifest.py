"""Synthetic/offline acquisition evidence; never download or promote data."""

import csv
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import sys

import pytest

from scripts import prepare_elections_manifest as manifest


STAMP = "2026-10-31T19:00:00+01:00"  # Synthetic test attestation, not real provenance.


@pytest.fixture
def sources(tmp_path, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("Acquisition preparation must never access the network")
    monkeypatch.setattr(socket.socket, "connect", no_network)
    # Tiny fixtures: cardinality enforcement is tested against these explicit counts.
    monkeypatch.setattr(manifest, "TABLES", {key: (headers, 2) for key, (headers, _) in manifest.TABLES.items()})
    for key, (headers, _) in manifest.TABLES.items():
        with (tmp_path / f"NRSR2023_SK_{key}.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(headers)
            writer.writerows([["synthetic, Žilina"] * len(headers)] * 2)
    return tmp_path


def prepare(sources, **kwargs):
    return manifest.prepare_manifest(sources, STAMP, attest_manual_download=True, **kwargs)


def test_manifest_is_non_content_deterministic_offline_and_rehashes(sources):
    first = prepare(sources)
    assert first == prepare(sources)
    assert first["electionId"] == "NRSR2023"
    assert first["manuallyAcquiredAt"] == "2026-10-31T18:00:00Z"
    assert first["status"] == "MANIFEST_PREPARED_SEMANTIC_REVIEW_REQUIRED"
    assert len(first["files"]) == 5
    assert first["sourcePublication"]["timezone"] is None
    assert first["publisherReplyReceivedOn"] == "2026-10-30"
    encoded = json.dumps(first, ensure_ascii=False)
    assert str(sources) not in encoded and "synthetic" not in encoded
    for record in first["files"]:
        raw = (sources / record["filename"]).read_bytes()
        assert record["sha256"] == hashlib.sha256(raw).hexdigest()
        assert record["bytes"] == len(raw)
        assert record["rowCount"] == 2
        assert record["historicalHashComparison"] == "DIFFERENT_REQUIRES_REVIEW"
        assert record["sourcePublishedAt"] is None
        assert record["sourceUrl"].endswith(record["filename"])
        assert len(record["headerSha256"]) == 64
    assert list(sources.glob("*.json")) == []  # dry-run, no writes


def test_headers_and_historical_hashes_match_reviewed_research():
    research = Path("docs/research/elections-data-schema.md").read_text(encoding="utf-8")
    for digest in manifest.HISTORICAL_HASHES.values():
        assert len(digest) == 64 and digest in research
    assert manifest.TABLES["tab03a"][1] == manifest.TABLES["tab0a"][1] == 25
    assert manifest.TABLES["tab0c"][1] == manifest.TABLES["tab02d"][1] == 2927
    assert manifest.TABLES["tab01"][1] == 1


def test_missing_files_never_creates_acquisition(sources):
    (sources / "NRSR2023_SK_tab0a.csv").unlink()
    with pytest.raises(ValueError, match="MANUAL_SOURCE_FILES_REQUIRED.*tab0a"):
        prepare(sources)


def test_manual_attestation_required(sources):
    with pytest.raises(ValueError, match="attestation"):
        manifest.prepare_manifest(sources, STAMP)


@pytest.mark.parametrize("stamp", ["2026-10-31", "2026-10-31T19:00:00", "not-a-date"])
def test_no_invented_timestamp_or_timezone(stamp):
    with pytest.raises(ValueError):
        manifest.acquisition_timestamp(stamp)


def test_wrong_election_profile_rejected(sources):
    with pytest.raises(ValueError, match="NRSR2023 only"):
        prepare(sources, profile="NRSR2020")


@pytest.mark.parametrize("change", ["encoding", "bom", "delimiter", "header", "extra-column", "row-count"])
def test_unreviewed_schema_encoding_or_cardinality_fails(sources, change):
    path = sources / "NRSR2023_SK_tab0c.csv"
    text = path.read_text(encoding="utf-8")
    if change == "encoding":
        path.write_bytes(text.encode("cp1250"))
    elif change == "bom":
        path.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))
    elif change == "delimiter":
        path.write_text(text.replace(",", ";"), encoding="utf-8")
    elif change == "header":
        path.write_bytes(text.replace("Kód kraja", "Wrong header").encode("utf-8"))
    elif change == "extra-column":
        lines = text.splitlines()
        path.write_bytes((lines[0] + ",candidateName\n" + "\n".join(lines[1:]) + "\n").encode("utf-8"))
    else:
        path.write_bytes(("\n".join(text.splitlines()[:-1]) + "\n").encode("utf-8"))
    with pytest.raises((ValueError, UnicodeError)):
        prepare(sources)


def test_excluded_tables_are_not_opened_or_required(sources):
    for key in ("tab03e", "candidate"):
        (sources / f"NRSR2023_SK_{key}.csv").write_bytes(b"invalid UTF-8\xff")
    assert len(prepare(sources)["files"]) == 5


def test_explicit_manifest_write_cannot_touch_production_or_overwrite(sources):
    payload = prepare(sources)
    target = sources / "manifest.json"
    manifest.write_manifest(target, payload)
    assert json.loads(target.read_bytes()) == payload
    with pytest.raises(FileExistsError):
        manifest.write_manifest(target, payload)
    with pytest.raises(ValueError, match="repository writes"):
        manifest.write_manifest(manifest.importer.ROOT / "data/elections_nrsr_2023.json", payload)


def test_repository_raw_inputs_denied():
    with pytest.raises(ValueError, match="outside the repository"):
        prepare(manifest.importer.ROOT)


def test_cli_missing_manual_files_reports_failure_without_writes(tmp_path):
    target = tmp_path / "manifest.json"
    completed = subprocess.run([
        sys.executable, "scripts/prepare_elections_manifest.py", "--source-dir", str(tmp_path),
        "--manually-acquired-at", STAMP, "--attest-manual-download", "--write-manifest", str(target),
    ], capture_output=True, check=False)
    assert completed.returncode == 1
    assert "MANUAL_SOURCE_FILES_REQUIRED" in json.loads(completed.stdout)["error"]
    assert not target.exists()
