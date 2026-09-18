#!/usr/bin/env python3
"""Smoke-test the public OpenSK API surface.

The script checks the documented public surface and expects the company
endpoint to be backed by the checked-in local seed dataset.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
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
    last_error: BaseException | None = None
    for attempt in range(2):
        try:
            with urlopen(request, timeout=15) as response:
                status = response.status
                payload = response.read().decode("utf-8")
                break
        except HTTPError as exc:
            status = exc.code
            payload = exc.read().decode("utf-8")
            break
        except (TimeoutError, URLError) as exc:
            last_error = exc
            if attempt == 0:
                time.sleep(5)
                continue
            reason = getattr(exc, "reason", exc)
            raise RuntimeError(str(reason)) from exc
    else:
        raise RuntimeError(str(last_error))

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


def _check_root(url: str) -> SmokeResult:
    try:
        status, body = _request_json(url)
    except RuntimeError as exc:
        return SmokeResult("root", False, "FAIL", str(exc))

    if status != 200:
        return SmokeResult("root", False, "FAIL", f"expected 200, got {status}: {body!r}")

    try:
        data = body["data"]
        metadata = body["metadata"]
        if data["version"] == "0.13.0" and data["apiVersion"] == metadata["version"] == "v1" and data["apiNamespace"] == "/v1":
            return SmokeResult("root", True, "PASS")
    except Exception:
        return SmokeResult("root", False, "FAIL", f"unexpected body: {body!r}")

    return SmokeResult("root", False, "FAIL", f"unexpected body: {body!r}")


def _check_openapi(url: str) -> SmokeResult:
    try:
        status, body = _request_json(url)
    except RuntimeError as exc:
        return SmokeResult("openapi", False, "FAIL", str(exc))

    if status != 200:
        return SmokeResult("openapi", False, "FAIL", f"expected 200, got {status}: {body!r}")

    required_paths = {
        "/v1/health",
        "/v1/holidays/{year}",
        "/v1/psc",
        "/v1/psc/search",
        "/v1/psc/stats",
        "/v1/regions",
        "/v1/districts",
        "/v1/municipalities",
        "/v1/banks",
        "/v1/iban/validate/{iban}",
        "/v1/companies/{ico}",
        "/v1/ico/{ico}",
        "/v1/phone-areas",
        "/v1/vehicle-registration-codes",
        "/v1/school-facility-counts",
    }
    try:
        paths = set(body["paths"])
        version = body["info"]["version"]
    except Exception:
        return SmokeResult("openapi", False, "FAIL", f"unexpected body: {body!r}")

    missing = sorted(required_paths - paths)
    if missing:
        return SmokeResult("openapi", False, "FAIL", f"missing paths: {missing}")
    if version != "0.13.0":
        return SmokeResult("openapi", False, "FAIL", f"expected version 0.13.0, got {version!r}")

    return SmokeResult("openapi", True, "PASS")


def _build_valid_slovak_iban(bank_code: str, account_number: str) -> str:
    bban = f"{bank_code}{account_number}"
    rearranged = f"{bban}SK00"
    numeric = "".join(str(ord(character) - 55) if character.isalpha() else character for character in rearranged)

    remainder = 0
    for digit in numeric:
        remainder = (remainder * 10 + int(digit)) % 97

    check_digits = 98 - remainder
    return f"SK{check_digits:02d}{bban}"


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


def _check_company_alias(url: str, expected_ico: str) -> SmokeResult:
    try:
        status, body = _request_json(url)
    except RuntimeError as exc:
        return SmokeResult("companies-alias", False, "FAIL", str(exc))

    if status != 200:
        return SmokeResult("companies-alias", False, "FAIL", f"expected 200, got {status}: {body!r}")

    try:
        if body["data"]["ico"] == expected_ico:
            return SmokeResult("companies-alias", True, "PASS")
    except Exception:
        return SmokeResult("companies-alias", False, "FAIL", f"unexpected body: {body!r}")

    return SmokeResult("companies-alias", False, "FAIL", f"unexpected body: {body!r}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Smoke test the public OpenSK API surface")
    parser.add_argument("--base-url", required=True, help="Base URL of the deployed API")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    base_url = _normalize_base_url(args.base_url)

    checks = [
        ("health", f"{base_url}/v1/health"),
        ("holidays", f"{base_url}/v1/holidays/2026"),
        ("psc-item", f"{base_url}/v1/psc/81101"),
        ("psc-list", f"{base_url}/v1/psc"),
        ("psc-search", f"{base_url}/v1/psc/search?q={quote('Bratislava')}", 200),
        ("psc-stats", f"{base_url}/v1/psc/stats"),
        ("banks", f"{base_url}/v1/banks"),
        ("bank-item", f"{base_url}/v1/banks/1100"),
        ("iban", f"{base_url}/v1/iban/validate/{_build_valid_slovak_iban('0900', '0000000000000001')}"),
        ("regions", f"{base_url}/v1/regions"),
        ("region-item", f"{base_url}/v1/regions/SK010"),
        ("districts", f"{base_url}/v1/districts"),
        ("district-item", f"{base_url}/v1/districts/SK0101"),
        ("municipalities", f"{base_url}/v1/municipalities"),
        ("municipality-item", f"{base_url}/v1/municipalities/528595"),
        ("phone-areas", f"{base_url}/v1/phone-areas"),
        ("phone-area-item", f"{base_url}/v1/phone-areas/02"),
        ("phone-area-search", f"{base_url}/v1/phone-areas/search?q={quote('Bratislava')}", 200),
        ("vehicle-registration-codes", f"{base_url}/v1/vehicle-registration-codes"),
        ("vehicle-registration-code", f"{base_url}/v1/vehicle-registration-codes/BA"),
        ("vehicle-registration-code-search", f"{base_url}/v1/vehicle-registration-codes/search?q={quote('Trencin')}", 200),
        ("school-facility-counts", f"{base_url}/v1/school-facility-counts"),
        ("school-facility-count-stats", f"{base_url}/v1/school-facility-counts/stats"),
        ("companies", f"{base_url}/v1/companies/50158635", 200),
    ]

    results: list[SmokeResult] = [_check_root(f"{base_url}/")]
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

    results.append(_check_company_alias(f"{base_url}/v1/ico/50158635", "50158635"))
    results.append(_check_ok("docs", f"{base_url}/docs"))
    results.append(_check_openapi(f"{base_url}/openapi.json"))

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
