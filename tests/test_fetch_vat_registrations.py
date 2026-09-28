from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, Mock

import scripts.fetch_vat_registrations as fetch_vat_registrations


def test_fetch_vat_registrations_writes_zip_and_metadata(monkeypatch, tmp_path: Path) -> None:
    response = MagicMock()
    response.read.return_value = b"zip-payload"
    response.geturl.return_value = "https://report.financnasprava.sk/ds_dphs.zip"
    response.__enter__.return_value = response
    response.__exit__.return_value = False
    monkeypatch.setattr(fetch_vat_registrations.request, "urlopen", Mock(return_value=response))

    output = tmp_path / "ds_dphs.zip"
    exit_code = fetch_vat_registrations.main(["--output", str(output), "--timeout", "1", "--retries", "0"])

    assert exit_code == 0
    assert output.read_bytes() == b"zip-payload"
    metadata = json.loads(output.with_suffix(".zip.meta.json").read_text(encoding="utf-8"))
    assert metadata["sourceUrl"] == fetch_vat_registrations.DEFAULT_URL
    assert metadata["bytes"] == len(b"zip-payload")
    assert len(metadata["sha256"]) == 64


def test_fetch_vat_registrations_refuses_overwrite(monkeypatch, tmp_path: Path) -> None:
    output = tmp_path / "ds_dphs.zip"
    output.write_bytes(b"existing")
    urlopen = Mock()
    monkeypatch.setattr(fetch_vat_registrations.request, "urlopen", urlopen)

    exit_code = fetch_vat_registrations.main(["--output", str(output)])

    assert exit_code == 1
    urlopen.assert_not_called()
    assert output.read_bytes() == b"existing"
