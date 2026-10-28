import copy
import json

import pytest

from scripts.acquire_procurement_notices import acquire, encoded, request_payload, validate_scope


def row(number=1):
    return {"publication-number": f"{number:06}-2026", "publication-date": "2026-10-28Z", "buyer-country": ["SVK"]}


def page(rows, token="next", total=2):
    return {"notices": rows, "iterationNextToken": token, "totalNoticeCount": total, "timedOut": False}


def source(pages, requests):
    pages = iter(pages)
    def fetch(payload, statuses):
        requests.append(payload)
        statuses["200"] = statuses.get("200", 0) + 1
        body = next(pages)
        return encoded(body), body, "application/json"
    return fetch


def test_iteration_complete_manifest_and_exact_request(tmp_path):
    requests = []
    pages = [page([row()], "a"), page([row(2)], "b"), page([], "b")]
    manifest = acquire(tmp_path / "raw", "2026-10-28", limit=2, fetcher=source(pages, requests), delay=0)
    assert manifest["acquiredTotal"] == manifest["reportedTotal"] == 2
    assert manifest["pageCount"] == 3 and manifest["pages"][-1]["rows"] == 0
    assert requests[0] == request_payload("2026-10-28", 2)
    assert "iterationNextToken" not in requests[0]
    assert requests[1]["iterationNextToken"] == "a"
    assert all(r["onlyLatestVersions"] is True and r["paginationMode"] == "ITERATION" for r in requests)
    assert "publication-date <= 20261028" in requests[0]["query"]
    assert json.loads((tmp_path / "raw/manifest.json").read_bytes())["complete"] is True


@pytest.mark.parametrize("pages", [
    [page([row()], None)],
    [page([row()], "a"), page([row(2)], "a")],
    [page([row()], "a"), page([row()], "b")],
    [page([row()], "a"), page([], "a")],
    [page([row()], "a"), page([row(2)], "b", total=3)],
    [page([row(), row(2), row(3)], "a")],
    [page([row()], "a", total=-1)],
])
def test_broken_iteration_fails_closed_without_complete_manifest(tmp_path, pages):
    with pytest.raises(ValueError):
        acquire(tmp_path / "raw", "2026-10-28", limit=2, max_pages=3, fetcher=source(pages, []), delay=0)
    assert not (tmp_path / "raw/manifest.json").exists()


def test_page_bound_cannot_silently_truncate(tmp_path):
    with pytest.raises(ValueError, match="max-pages"):
        acquire(tmp_path / "raw", "2026-10-28", max_pages=1, fetcher=source([page([row()])], []), delay=0)
    assert not (tmp_path / "raw/manifest.json").exists()


@pytest.mark.parametrize("field,value", [
    ("publication-number", "123x-2026"), ("publication-number", "000001-2025"),
    ("publication-date", "2026-10-29Z"), ("publication-date", "2026-02-30Z"),
    ("buyer-country", ["CZE"]), ("buyer-country", "SVK"), ("isLatestVersion", False),
])
def test_scope_and_obsolete_negative_controls(field, value):
    item = copy.deepcopy(row())
    item[field] = value
    with pytest.raises(ValueError):
        validate_scope(item, "2026-10-28")


def test_output_cannot_use_repository():
    from scripts.acquire_procurement_notices import ROOT
    with pytest.raises(ValueError, match="outside"):
        acquire(ROOT / "data/raw/test", "2026-10-28")
