#!/usr/bin/env python3
"""Offline fetcher for the official Finančná správa VAT registration ZIP."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib import error, parse


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.source_safety import open_https, read_bounded, validate_https_url, validate_timeout

MAX_DOWNLOAD_BYTES = 128 * 1024 * 1024
DEFAULT_URL = "https://report.financnasprava.sk/ds_dphs.zip"
DEFAULT_OUTPUT = ROOT / "data" / "raw" / "ds_dphs.zip"


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def fetch(url: str, *, timeout: float, retries: int) -> tuple[bytes, str]:
    validate_timeout(timeout)
    validate_https_url(url)
    if not 0 <= retries <= 5:
        raise ValueError("retries must be between 0 and 5")
    allowed_hosts = {parse.urlsplit(url).hostname.lower()}
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            with open_https(url, timeout=timeout, allowed_hosts=allowed_hosts) as response:
                resolved_url = response.geturl()
                validate_https_url(resolved_url, allowed_hosts)
                return read_bounded(response, MAX_DOWNLOAD_BYTES, "VAT download"), resolved_url
        except (error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(min(2**attempt, 5))
    raise RuntimeError(f"failed to fetch VAT ZIP from {url}: {last_error}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch the official VAT registration ZIP for offline import.")
    parser.add_argument("--url", default=DEFAULT_URL, help="Official VAT registration ZIP URL")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output ZIP path")
    parser.add_argument("--timeout", type=float, default=60.0, help="Request timeout in seconds")
    parser.add_argument("--retries", type=int, default=2, help="Retry count after the first attempt")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing output file")
    args = parser.parse_args(argv)

    output = args.output
    if output.exists() and not args.force:
        print(f"Refusing to overwrite {output}; pass --force to replace it")
        return 1

    try:
        payload, resolved_url = fetch(args.url, timeout=args.timeout, retries=args.retries)
    except (RuntimeError, ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(payload)

    metadata = {
        "sourceUrl": args.url,
        "resolvedUrl": resolved_url,
        "bytes": len(payload),
        "sha256": _sha256(payload),
        "fetchedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    metadata_path = output.with_suffix(output.suffix + ".meta.json")
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Fetched {len(payload)} bytes to {output}")
    print(f"SHA256 {metadata['sha256']}")
    print(f"Recorded metadata in {metadata_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
