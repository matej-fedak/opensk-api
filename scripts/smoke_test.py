#!/usr/bin/env python3
"""Smoke-test the public OpenSK API surface.

The script checks stable endpoints and expects the company endpoint to be
backed by the checked-in local seed dataset.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


@dataclass
class SmokeResult:
    name: str
    ok: bool
    status: str
    detail: str = ""


def _normalize_base_url(base_url: str) -> str:
    return base_url.rstrip("/")


def _request_json(url: str) -> tuple[int, object]:
    request = Request(url, headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=15) as response:
            status = response.status
            payload = response.read().decode("utf-8")
    except HTTPError as exc:
        status = exc.code
        payload = exc.read().decode("utf-8")
    except URLError as exc:
        raise RuntimeError(str(exc.reason)) from exc

    try:
        body = json.loads(payload)
    except json.JSONDecodeError:
        body = payload
    return status, body


def _check_ok(name: str, url: str, expected_status: int = 200) -> SmokeResult:
    try:
        status, body = _request_json(url)
    except RuntimeError as exc:
        return SmokeResult(name, False, "FAIL", str(exc))

    if status != expected_status:
        return SmokeResult(name, False, "FAIL", f"expected {expected_status}, got {status}: {body!r}")

    return SmokeResult(name, True, "PASS")


def _check_psc_stats(url: str) -> SmokeResult:
    try:
        status, body = _request_json(url)
    except RuntimeError as exc:
        return SmokeResult("psc-stats", False, "FAIL", str(exc))

    if status != 200:
        return SmokeResult("psc-stats", False, "FAIL", f"expected 200, got {status}: {body!r}")

    try:
        record_count = int(body["data"]["recordCount"])
        unique_psc_count = int(body["data"]["uniquePscCount"])
    except Exception:
        return SmokeResult("psc-stats", False, "FAIL", f"unexpected body: {body!r}")

    if record_count <= 0 or unique_psc_count <= 0:
        return SmokeResult("psc-stats", False, "FAIL", f"non-positive counts: {body!r}")

    return SmokeResult("psc-stats", True, "PASS")


def _check_company_endpoint(name: str, url: str) -> SmokeResult:
    try:
        status, body = _request_json(url)
    except RuntimeError as exc:
        return SmokeResult(name, False, "FAIL", str(exc))

    if status != 200:
        return SmokeResult(name, False, "FAIL", f"expected 200, got {status}: {body!r}")

    try:
        if body["data"]["ico"]:
            return SmokeResult(name, True, "PASS")
    except Exception:
        return SmokeResult(name, False, "FAIL", f"unexpected body: {body!r}")

    return SmokeResult(name, False, "FAIL", f"unexpected body: {body!r}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Smoke test the public OpenSK API surface")
    parser.add_argument("--base-url", required=True, help="Base URL of the deployed API")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    base_url = _normalize_base_url(args.base_url)

    checks = [
        ("root", f"{base_url}/"),
        ("health", f"{base_url}/v1/health"),
        ("psc-search", f"{base_url}/v1/psc/search?q={quote('Bratislava')}", 200),
        ("banks", f"{base_url}/v1/banks"),
        ("regions", f"{base_url}/v1/regions"),
        ("companies", f"{base_url}/v1/companies/50158635", 200),
    ]

    results: list[SmokeResult] = []
    for check in checks:
        if len(check) == 2:
            name, url = check
            if name == "companies":
                result = _check_company_endpoint(name, url)
            elif name == "psc-stats":
                result = _check_psc_stats(url)
            else:
                result = _check_ok(name, url)
        else:
            name, url, expected_status = check
            if name == "companies":
                result = _check_company_endpoint(name, url)
            else:
                result = _check_ok(name, url, expected_status=expected_status)
        results.append(result)

    results.insert(2, _check_psc_stats(f"{base_url}/v1/psc/stats"))

    for result in results:
        line = f"{result.status}: {result.name}"
        if result.detail:
            line += f" - {result.detail}"
        print(line)

    failed = [result for result in results if not result.ok]
    print(f"Summary: {len(results) - len(failed)} passed, {len(failed)} failed")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
