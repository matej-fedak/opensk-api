#!/usr/bin/env python3
"""MANUAL acquisition only. Never imported by FastAPI, CI or a scheduler.

Raw project pages can contain personal data. Output must be outside this
repository. Logs contain page counters only, never source row bodies/names.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = "https://api.itms21.sk/public/v1/projekt"
PROFILE = "itms21-project-list-acquisition-v1"
MAX_RESPONSE_BYTES = 32 * 1024 * 1024
USER_AGENT = "OpenSK-Source-Acquisition/0.23.7 (+https://github.com/matej-fedak/opensk-api)"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def canonical_bytes(obj: dict) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def page_url(offset: int, limit: int) -> str:
    return COLLECTION + "?" + urlencode({"offset": offset, "limit": limit})


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Do not follow requests outside the fixed documented URL.


def retry_delay(value: str | None, attempt: int) -> float:
    if value:
        try:
            delay = float(value)
        except ValueError:
            delay = (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds()
        if delay > 120:
            raise ValueError("Retry-After exceeds manual retry budget; stop and retry later")
        return max(0, delay)
    return 2 ** attempt


def fetch_page(url: str, *, timeout: float = 60, attempts: int = 3) -> bytes:
    opener = build_opener(NoRedirect())
    for attempt in range(attempts):
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
            with opener.open(request, timeout=timeout) as response:
                if response.status != 200 or "application/json" not in response.headers.get("Content-Type", ""):
                    raise ValueError("upstream did not return HTTP 200 JSON")
                raw = response.read(MAX_RESPONSE_BYTES + 1)
                if len(raw) > MAX_RESPONSE_BYTES:
                    raise ValueError("bounded page response exceeds byte limit")
                return raw
        except HTTPError as exc:
            # In particular, never retry/bypass authentication or WAF challenges.
            if exc.code != 429 and not 500 <= exc.code <= 599:
                raise ValueError(f"upstream HTTP {exc.code}; acquisition stopped") from None
            if attempt == attempts - 1:
                raise ValueError("upstream transient HTTP retry budget exhausted") from None
            time.sleep(retry_delay(exc.headers.get("Retry-After"), attempt))
        except (URLError, TimeoutError, ConnectionError):
            if attempt == attempts - 1:
                raise ValueError("upstream network retry budget exhausted") from None
            time.sleep(retry_delay(None, attempt))
    raise ValueError("no upstream response")


def acquire(output: Path, *, page_size: int = 200, pace: float = 1.5, fetch=fetch_page,
            sleep=time.sleep) -> dict:
    output = output.resolve()
    if output.is_relative_to(ROOT.resolve()):
        raise ValueError("raw acquisition output must be outside the repository")
    if not 1 <= page_size <= 250 or pace < 1:
        raise ValueError("page size must be 1..250 and pacing at least one second")
    if output.exists() and any(output.iterdir()):
        raise ValueError("acquisition output must be a new/empty directory")
    output.mkdir(parents=True, exist_ok=True)
    started = utc_now()
    pages, ids, codes = [], set(), set()
    offset, population, first_raw = 0, None, None
    while population is None or offset < population:
        url = page_url(offset, page_size)
        raw = fetch(url)
        retrieved = utc_now()
        try:
            page = json.loads(raw)
            size, rows = page["size"], page["results"]
            if type(size) is not int or not 0 < size <= 100_000 or not isinstance(rows, list):
                raise ValueError
            if page["offset"] != offset or page["limit"] != page_size:
                raise ValueError
        except (ValueError, TypeError, KeyError):
            raise ValueError("invalid project-list page envelope (no body logged)") from None
        if population is None:
            population = size
            first_raw = raw
        if size != population or len(rows) != min(page_size, population - offset):
            raise ValueError("inconsistent source size or incomplete page")
        for row in rows:
            if not isinstance(row, dict) or type(row.get("id")) is not int or not isinstance(row.get("kod"), str) or not row["kod"]:
                raise ValueError("invalid project identity (no body logged)")
            if row["id"] in ids or row["kod"] in codes:
                raise ValueError("duplicate project ID/code; no consistent snapshot")
            ids.add(row["id"])
            codes.add(row["kod"])
        filename = f"page-{len(pages):05d}.json"
        (output / filename).write_bytes(raw)
        pages.append({"file": filename, "url": url, "offset": offset, "limit": page_size,
                      "size": size, "rows": len(rows), "bytes": len(raw),
                      "sha256": hashlib.sha256(raw).hexdigest(), "retrievedAt": retrieved})
        offset += len(rows)
        print(f"Captured page {len(pages)}: {offset}/{population} rows", flush=True)
        sleep(pace)
    # A bounded first-page recheck catches additions/order changes at the head.
    # No upstream transaction token exists; record the acquisition window honestly.
    check = fetch(page_url(0, page_size))
    if check != first_raw:
        raise ValueError("first page changed during acquisition; discard this snapshot")
    manifest = {"profile": PROFILE, "collectionUrl": COLLECTION, "startedAt": started,
                "completedAt": utc_now(), "sourceProjectCount": population, "rowsAcquired": offset,
                "pageSize": page_size, "completeAcquisition": True, "pages": pages,
                "boundaryRecheckSha256": hashlib.sha256(check).hexdigest()}
    manifest["manifestSha256"] = hashlib.sha256(canonical_bytes(manifest)).hexdigest()
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--page-size", type=int, default=200)
    args = parser.parse_args(argv)
    try:
        manifest = acquire(args.output_dir, page_size=args.page_size)
        print(f"Complete: {manifest['rowsAcquired']} rows, {len(manifest['pages'])} pages, manifest {manifest['manifestSha256']}")
        return 0
    except (ValueError, OSError) as exc:
        print(f"Acquisition failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
