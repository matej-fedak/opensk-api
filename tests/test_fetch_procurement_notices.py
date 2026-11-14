from __future__ import annotations

import json
import io
import urllib.error
from pathlib import Path


from scripts import fetch_procurement_notices


def test_fetch_procurement_notices_writes_snapshot(monkeypatch, tmp_path: Path) -> None:
    output = tmp_path / "ted-search.json"
    payload = {"notices": [{"publication-number": "123456-2026"}], "totalNoticeCount": 1}

    class FakeResponse:
        def __init__(self):
            self.stream = io.BytesIO(json.dumps(payload).encode("utf-8"))

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self, size):
            assert 0 < size <= 65536
            return self.stream.read(size)

        def geturl(self):
            return fetch_procurement_notices.TED_SEARCH_URL

    def fake_urlopen(request, timeout, **kwargs):
        body = json.loads(request.data.decode("utf-8"))
        assert request.full_url == fetch_procurement_notices.TED_SEARCH_URL
        assert body["query"] == "buyer-country = SVK SORT BY publication-date DESC"
        assert body["limit"] == 5
        assert "contactName" not in body["fields"]
        assert "organisation-email" not in body["fields"]
        return FakeResponse()

    monkeypatch.setattr(fetch_procurement_notices, "open_https", fake_urlopen)

    result = fetch_procurement_notices.run_fetch(output_path=output, limit=5, write=True)

    assert result.ok
    assert result.wrote_file
    assert result.notice_count == 1
    assert result.total_notice_count == 1
    assert json.loads(output.read_text(encoding="utf-8")) == payload


def test_fetch_procurement_notices_reports_network_errors(monkeypatch, tmp_path: Path) -> None:
    def fake_urlopen(request, timeout, **kwargs):
        raise urllib.error.URLError("offline")

    monkeypatch.setattr(fetch_procurement_notices, "open_https", fake_urlopen)

    result = fetch_procurement_notices.run_fetch(output_path=tmp_path / "out.json", limit=5)

    assert not result.ok
    assert not result.wrote_file
    assert "offline" in result.error


def test_fetch_procurement_notices_rejects_bad_limit(tmp_path: Path) -> None:
    result = fetch_procurement_notices.run_fetch(output_path=tmp_path / "out.json", limit=0)

    assert not result.ok
    assert "limit" in result.error
