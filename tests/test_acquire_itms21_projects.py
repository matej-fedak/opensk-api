"""Offline acquisition tests; bodies are synthetic, never live personal data."""

import json
from urllib.parse import parse_qs, urlsplit

import pytest

from scripts import acquire_itms21_projects as acquisition


def source_fetch(*, total=3, duplicate=False, inconsistent=False, changed_boundary=False):
    calls = []

    def fetch(url):
        calls.append(url)
        q = parse_qs(urlsplit(url).query)
        offset, limit = int(q["offset"][0]), int(q["limit"][0])
        ids = range(offset + 1, min(total, offset + limit) + 1)
        rows = [{"id": 1 if duplicate else i, "kod": f"TEST{i:06d}"} for i in ids]
        if changed_boundary and len(calls) > 2 and offset == 0:
            rows[0]["id"] = 999
        return json.dumps({"offset": offset, "limit": limit,
                           "size": total + (1 if inconsistent and offset else 0),
                           "results": rows}).encode()

    return fetch, calls


def test_acquisition_records_all_pages_and_boundary_hash(tmp_path):
    fetch, calls = source_fetch()
    manifest = acquisition.acquire(tmp_path / "raw", page_size=2, fetch=fetch, sleep=lambda _: None)
    assert manifest["rowsAcquired"] == manifest["sourceProjectCount"] == 3
    assert [p["offset"] for p in manifest["pages"]] == [0, 2]
    assert len(calls) == 3
    assert manifest["boundaryRecheckSha256"] == manifest["pages"][0]["sha256"]
    assert len(manifest["manifestSha256"]) == 64
    assert not any("TEST" in p["file"] for p in manifest["pages"])


@pytest.mark.parametrize("option", ["duplicate", "inconsistent", "changed_boundary"])
def test_bad_snapshot_never_gets_complete_manifest(tmp_path, option):
    fetch, _ = source_fetch(**{option: True})
    path = tmp_path / "raw"
    with pytest.raises(ValueError):
        acquisition.acquire(path, page_size=2, fetch=fetch, sleep=lambda _: None)
    assert not (path / "manifest.json").exists()


def test_raw_directory_cannot_be_inside_repository():
    with pytest.raises(ValueError, match="outside"):
        acquisition.acquire(acquisition.ROOT / "data" / "raw" / "itms")


def test_nonempty_output_is_not_overwritten(tmp_path):
    (tmp_path / "user-work").write_text("keep", encoding="utf-8")
    with pytest.raises(ValueError, match="empty"):
        acquisition.acquire(tmp_path)
    assert (tmp_path / "user-work").read_text() == "keep"


def test_retry_after_is_honored_or_stops():
    assert acquisition.retry_delay("13", 0) == 13
    with pytest.raises(ValueError, match="budget"):
        acquisition.retry_delay("10000", 0)


def test_fixed_host_and_bounded_limit_are_enforced():
    for url in ("https://example.com/projekt", acquisition.page_url(0, 999),
                acquisition.COLLECTION + "?limit=-1"):
        with pytest.raises(ValueError):
            acquisition.fetch_page(url)


def test_http_retry_after_then_success_without_logging_body(monkeypatch):
    from urllib.error import HTTPError
    from email.message import Message

    headers = Message()
    headers["Retry-After"] = "3"
    attempts, sleeps = [], []

    class Response:
        status = 200
        headers = {"Content-Type": "application/json"}
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self, size): return b'{"synthetic": true}'

    class Opener:
        def open(self, request, timeout):
            attempts.append(timeout)
            if len(attempts) == 1:
                raise HTTPError(request.full_url, 429, "rate limit", headers, None)
            return Response()

    monkeypatch.setattr(acquisition, "build_opener", lambda *a: Opener())
    monkeypatch.setattr(acquisition.time, "sleep", sleeps.append)
    assert acquisition.fetch_page(acquisition.page_url(0, 100)) == b'{"synthetic": true}'
    assert sleeps == [3] and len(attempts) == 2


def test_waf_challenge_is_not_retried(monkeypatch):
    from urllib.error import HTTPError
    attempts = []
    class Opener:
        def open(self, request, timeout):
            attempts.append(1)
            raise HTTPError(request.full_url, 403, "challenge", {}, None)
    monkeypatch.setattr(acquisition, "build_opener", lambda *a: Opener())
    with pytest.raises(ValueError, match="403"):
        acquisition.fetch_page(acquisition.page_url(0, 100))
    assert len(attempts) == 1
