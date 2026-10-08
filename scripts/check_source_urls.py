#!/usr/bin/env python3
"""Report availability of registered upstream source URLs.

Manual/diagnostic source-health tool. It performs HEAD requests (with a GET
fallback) against URLs declared in `data/sources.json` and prints a status
table. This script is intentionally not part of the required CI gates:
upstream availability must never gate releases, and the runtime API never
depends on upstream systems. A future scheduled workflow may run this with
`--strict` for early warning.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_SOURCES_PATH = Path(__file__).resolve().parent.parent / "data" / "sources.json"
URL_FIELDS = ("sourceUrl", "termsUrl", "sourceFileUrl", "sourceDocumentationUrl", "candidateSourceUrls")
USER_AGENT = "OpenSK-API-source-health/0.1 (+https://github.com/matej-fedak/opensk-api)"
DEFAULT_TIMEOUT = 15.0

Opener = Callable[..., Any]


@dataclass
class UrlCheck:
    source_id: str
    field: str
    url: str
    status: int | None
    ok: bool
    detail: str = ""


def collect_urls(payload: dict[str, Any]) -> list[tuple[str, str, str]]:
    """Extract (source_id, field, url) tuples from the registry payload."""

    urls: list[tuple[str, str, str]] = []
    for source_id, entry in payload.items():
        if not isinstance(entry, dict):
            continue
        for field in URL_FIELDS:
            value = entry.get(field)
            if isinstance(value, str) and value.startswith("http"):
                urls.append((source_id, field, value))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and item.startswith("http"):
                        urls.append((source_id, field, item))
    return urls


def check_url(url: str, timeout: float, opener: Opener = urlopen) -> tuple[int | None, bool, str]:
    """HEAD a URL, falling back to GET when HEAD is unsupported."""

    for method in ("HEAD", "GET"):
        request = Request(url, method=method, headers={"User-Agent": USER_AGENT})
        try:
            with opener(request, timeout=timeout) as response:
                status = getattr(response, "status", None) or response.getcode()
                return int(status), 200 <= int(status) < 400, ""
        except HTTPError as exc:
            if method == "HEAD" and exc.code in {405, 501}:
                continue
            return exc.code, 200 <= exc.code < 400, f"HTTPError {exc.code}"
        except (URLError, TimeoutError, OSError) as exc:
            return None, False, str(getattr(exc, "reason", exc))
    return None, False, "unreachable"


def run_checks(payload: dict[str, Any], timeout: float = DEFAULT_TIMEOUT, opener: Opener = urlopen) -> list[UrlCheck]:
    checks: list[UrlCheck] = []
    for source_id, field, url in collect_urls(payload):
        status, ok, detail = check_url(url, timeout, opener)
        checks.append(UrlCheck(source_id=source_id, field=field, url=url, status=status, ok=ok, detail=detail))
    return checks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check availability of registered upstream source URLs")
    parser.add_argument("--sources", default=str(DEFAULT_SOURCES_PATH), help="Path to the source registry JSON")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help="Per-request timeout in seconds")
    parser.add_argument("--strict", action="store_true", help="Exit 1 if any URL check fails")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    sources_path = Path(args.sources)
    with sources_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    checks = run_checks(payload, timeout=args.timeout)
    for check in checks:
        status = str(check.status) if check.status is not None else "---"
        verdict = "OK" if check.ok else "FAIL"
        line = f"{verdict} {status:>3} {check.source_id}.{check.field} {check.url}"
        if check.detail:
            line += f" ({check.detail})"
        print(line)

    failed = [check for check in checks if not check.ok]
    print(f"Summary: {len(checks) - len(failed)} ok, {len(failed)} failed, {len(checks)} total")
    return 1 if args.strict and failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
