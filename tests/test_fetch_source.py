from __future__ import annotations

import json
from pathlib import Path
from urllib import error
from unittest.mock import MagicMock, Mock

import scripts.fetch_source as fetch_source


def _configure_temp_root(monkeypatch, tmp_path: Path) -> Path:
    root_dir = tmp_path
    data_dir = root_dir / "data"
    raw_dir = data_dir / "raw"

    monkeypatch.setattr(fetch_source, "ROOT_DIR", root_dir)
    monkeypatch.setattr(fetch_source, "DATA_DIR", data_dir)
    monkeypatch.setattr(fetch_source, "RAW_DATA_DIR", raw_dir)
    monkeypatch.setattr(fetch_source, "DEFAULT_CONFIG_PATH", raw_dir / "source.json")
    return raw_dir


def test_fetch_source_writes_payload_and_metadata(monkeypatch, tmp_path, capsys) -> None:
    raw_dir = _configure_temp_root(monkeypatch, tmp_path)
    raw_dir.mkdir(parents=True, exist_ok=True)

    config_path = raw_dir / "source.json"
    config_path.write_text(json.dumps({"url": "https://example.com/source.txt", "filename": "download.txt"}), encoding="utf-8")

    response = MagicMock()
    response.read.return_value = b"payload"
    response.geturl.return_value = "https://example.com/source.txt"
    response.__enter__.return_value = response
    response.__exit__.return_value = False

    urlopen = Mock(return_value=response)
    monkeypatch.setattr(fetch_source.request, "urlopen", urlopen)

    exit_code = fetch_source.main(["--config", str(config_path)])

    assert exit_code == 0
    assert (raw_dir / "download.txt").read_bytes() == b"payload"

    metadata = json.loads((raw_dir / "download.txt.meta.json").read_text(encoding="utf-8"))
    assert metadata["sourceUrl"] == "https://example.com/source.txt"
    assert metadata["resolvedUrl"] == "https://example.com/source.txt"
    assert metadata["bytes"] == 7
    assert metadata["fetchedAt"].endswith("Z")

    out = capsys.readouterr().out
    assert "Fetched" in out
    assert "Recorded metadata" in out


def test_fetch_source_refuses_overwrite_without_force(monkeypatch, tmp_path, capsys) -> None:
    raw_dir = _configure_temp_root(monkeypatch, tmp_path)
    raw_dir.mkdir(parents=True, exist_ok=True)

    config_path = raw_dir / "source.json"
    config_path.write_text(json.dumps({"url": "https://example.com/source.txt", "filename": "download.txt"}), encoding="utf-8")

    (raw_dir / "download.txt").write_bytes(b"existing")

    urlopen = Mock()
    monkeypatch.setattr(fetch_source.request, "urlopen", urlopen)

    exit_code = fetch_source.main(["--config", str(config_path)])

    assert exit_code == 1
    urlopen.assert_not_called()
    assert (raw_dir / "download.txt").read_bytes() == b"existing"

    out = capsys.readouterr().out
    assert "Refusing to overwrite" in out
    assert "--force" in out


def test_fetch_source_reports_network_errors(monkeypatch, tmp_path, capsys) -> None:
    raw_dir = _configure_temp_root(monkeypatch, tmp_path)
    raw_dir.mkdir(parents=True, exist_ok=True)

    config_path = raw_dir / "source.json"
    config_path.write_text(json.dumps({"url": "https://example.com/source.txt", "filename": "download.txt"}), encoding="utf-8")

    monkeypatch.setattr(fetch_source.request, "urlopen", Mock(side_effect=error.URLError("offline")))

    exit_code = fetch_source.main(["--config", str(config_path), "--timeout", "1"])

    assert exit_code == 1
    out = capsys.readouterr().out
    assert "Network/offline error while fetching" in out
    assert "offline" in out
