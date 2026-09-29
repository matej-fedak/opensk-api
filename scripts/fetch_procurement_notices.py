#!/usr/bin/env python3
"""Fetch a small TED Search API snapshot for Slovak public procurement notices."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT / "data"
DEFAULT_OUTPUT = DEFAULT_DATA_DIR / "raw" / "procurement-notices-ted-search.json"
TED_SEARCH_URL = "https://api.ted.europa.eu/v3/notices/search"
TED_QUERY = "buyer-country = SVK SORT BY publication-date DESC"
TED_FIELDS = [
    "publication-number",
    "publication-date",
    "dispatch-date",
    "notice-type",
    "notice-title",
    "buyer-name",
    "buyer-country",
    "place-of-performance-city-proc",
    "place-of-performance-post-code-proc",
    "place-of-performance-country-proc",
    "deadline-date-lot",
]
FORBIDDEN_TIMED_REQUEST_LIMIT = 250


@dataclass(frozen=True)
class FetchResult:
    output_path: Path
    wrote_file: bool
    notice_count: int = 0
    total_notice_count: int = 0
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None


def build_search_payload(limit: int) -> dict[str, Any]:
    return {
        "query": TED_QUERY,
        "fields": TED_FIELDS,
        "page": 1,
        "limit": limit,
    }


def fetch_search_response(limit: int, timeout: int = 60) -> dict[str, Any]:
    if not 1 <= limit <= FORBIDDEN_TIMED_REQUEST_LIMIT:
        raise ValueError(f"limit must be between 1 and {FORBIDDEN_TIMED_REQUEST_LIMIT}")
    body = json.dumps(build_search_payload(limit)).encode("utf-8")
    request = urllib.request.Request(
        TED_SEARCH_URL,
        data=body,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.load(response)
    if not isinstance(payload, dict):
        raise ValueError("TED Search API response must be a JSON object")
    notices = payload.get("notices")
    if not isinstance(notices, list):
        raise ValueError("TED Search API response must contain a notices array")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_fetch(*, output_path: Path = DEFAULT_OUTPUT, limit: int = 100, write: bool = False, timeout: int = 60) -> FetchResult:
    output_path = output_path.resolve()
    try:
        payload = fetch_search_response(limit=limit, timeout=timeout)
    except (OSError, ValueError, urllib.error.URLError) as exc:
        return FetchResult(output_path=output_path, wrote_file=False, error=str(exc))

    notice_count = len(payload.get("notices", []))
    total_notice_count = payload.get("totalNoticeCount", 0)
    if not isinstance(total_notice_count, int):
        total_notice_count = 0
    if write:
        write_json(output_path, payload)
        return FetchResult(output_path=output_path, wrote_file=True, notice_count=notice_count, total_notice_count=total_notice_count)
    return FetchResult(output_path=output_path, wrote_file=False, notice_count=notice_count, total_notice_count=total_notice_count)


def _print_result(result: FetchResult, *, write: bool) -> None:
    print(f"output={result.output_path}")
    if result.error is not None:
        print(f"error={result.error}")
        return
    print(f"notices={result.notice_count}")
    print(f"totalNoticeCount={result.total_notice_count}")
    if result.wrote_file:
        print(f"Wrote: {result.output_path}")
    elif not write:
        print("Dry run only; no files written.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch a small TED Search API snapshot for Slovak-buyer procurement notices.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output JSON path, default data/raw/procurement-notices-ted-search.json")
    parser.add_argument("--limit", type=int, default=100, help=f"Number of latest notices to request, 1-{FORBIDDEN_TIMED_REQUEST_LIMIT}")
    parser.add_argument("--timeout", type=int, default=60, help="HTTP timeout in seconds")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Fetch and report only; do not write files")
    mode.add_argument("--write", action="store_true", help="Write the fetched Search API JSON")
    args = parser.parse_args(argv)

    result = run_fetch(output_path=args.output, limit=args.limit, write=args.write, timeout=args.timeout)
    _print_result(result, write=args.write)
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
