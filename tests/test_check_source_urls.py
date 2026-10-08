"""Unit tests for the manual source-health URL checker.

No network access: the HTTP opener is replaced with a fake in every test.
"""

from __future__ import annotations

from urllib.error import HTTPError, URLError

from scripts.check_source_urls import collect_urls, run_checks


REGISTRY_SAMPLE = {
    "alpha": {
        "sourceUrl": "https://example.com/alpha",
        "termsUrl": "pending",
        "candidateSourceUrls": ["https://example.com/a1", "not-a-url", "https://example.com/a2"],
    },
    "beta": {
        "sourceUrl": "https://example.com/beta",
        "sourceFileUrl": "https://example.com/beta.zip",
        "sourceDocumentationUrl": "https://example.com/beta-docs",
    },
}


class FakeResponse:
    def __init__(self, status: int) -> None:
        self.status = status

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def getcode(self) -> int:
        return self.status


def _fake_opener_factory(statuses: dict[str, object]):
    calls: list[tuple[str, str]] = []

    def opener(request, timeout):  # type: ignore[no-untyped-def]
        url = request.full_url
        calls.append((request.get_method(), url))
        outcome = statuses.get(url, 200)
        if isinstance(outcome, list):
            outcome = outcome.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        if isinstance(outcome, FakeResponse):
            return outcome
        return FakeResponse(int(outcome))

    return opener, calls


def test_collect_urls_extracts_http_fields_and_skips_non_urls() -> None:
    urls = collect_urls(REGISTRY_SAMPLE)
    assert urls == [
        ("alpha", "sourceUrl", "https://example.com/alpha"),
        ("alpha", "candidateSourceUrls", "https://example.com/a1"),
        ("alpha", "candidateSourceUrls", "https://example.com/a2"),
        ("beta", "sourceUrl", "https://example.com/beta"),
        ("beta", "sourceFileUrl", "https://example.com/beta.zip"),
        ("beta", "sourceDocumentationUrl", "https://example.com/beta-docs"),
    ]


def test_run_checks_reports_ok_for_successful_urls() -> None:
    opener, calls = _fake_opener_factory({"https://example.com/alpha": 200})
    checks = run_checks({"alpha": {"sourceUrl": "https://example.com/alpha"}}, opener=opener)
    assert len(checks) == 1
    assert checks[0].ok is True
    assert checks[0].status == 200
    assert calls == [("HEAD", "https://example.com/alpha")]


def test_run_checks_falls_back_to_get_when_head_is_not_allowed() -> None:
    opener, calls = _fake_opener_factory(
        {"https://example.com/alpha": [HTTPError("https://example.com/alpha", 405, "Method Not Allowed", {}, None), FakeResponse(200)]}
    )
    checks = run_checks({"alpha": {"sourceUrl": "https://example.com/alpha"}}, opener=opener)
    assert checks[0].ok is True
    assert calls[0][0] == "HEAD"
    assert calls[1][0] == "GET"


def test_run_checks_marks_server_errors_and_network_failures_as_failed() -> None:
    opener, _ = _fake_opener_factory(
        {
            "https://example.com/down": HTTPError("https://example.com/down", 500, "Server Error", {}, None),
            "https://example.com/timeout": URLError("timed out"),
        }
    )
    checks = run_checks(
        {"a": {"sourceUrl": "https://example.com/down"}, "b": {"sourceUrl": "https://example.com/timeout"}},
        opener=opener,
    )
    assert checks[0].ok is False
    assert checks[0].status == 500
    assert checks[1].ok is False
    assert checks[1].status is None
