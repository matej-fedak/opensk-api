#!/usr/bin/env python3
"""Manual-only successor acquisition. Raw captures MUST remain outside Git.

Technical access is not reuse permission: review PortalVS terms/outreach before
invocation. Never called by FastAPI, CI or a scheduler. No HTML data scraping.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from http.client import HTTPException
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://ciselniky2.portalvs.sk"
OPENAPI_URL = BASE + "/api/docs.json"
URLS = {
    "districts": BASE + "/api/county.json?validity=valid",
    "municipalities": BASE + "/api/town.json?validity=valid",
    "psc": BASE + "/api/postal_code_sk.json",
}
PROFILE = "portalvs-successor-acquisition-v1"
MAX_BYTES = 32 * 1024 * 1024
USER_AGENT = "OpenSK-Offline-Source-Acquisition/0.23.9 (+https://github.com/matej-fedak/opensk-api)"


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def manifest_hash(manifest):
    body = {k: v for k, v in manifest.items() if k != "manifestSha256"}
    return hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch(url):
    if url not in URLS.values():
        raise ValueError("only the three fixed documented official successor URLs are allowed")
    opener = build_opener(NoRedirect())
    for attempt in range(3):
        try:
            with opener.open(Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}), timeout=60) as response:
                if response.status != 200 or "application/json" not in response.headers.get("Content-Type", ""):
                    raise ValueError("expected HTTP 200 JSON")
                raw = response.read(MAX_BYTES + 1)
                if len(raw) > MAX_BYTES:
                    raise ValueError("response exceeds bounded acquisition byte size")
                return raw, {"url": url, "status": response.status,
                             "contentType": response.headers.get("Content-Type"),
                             "etag": response.headers.get("ETag"), "acquiredAt": now()}
        except HTTPError as exc:
            if (exc.code != 429 and not 500 <= exc.code <= 599) or attempt == 2:
                raise ValueError(f"successor HTTP {exc.code}; stopped without raw body logging") from None
            value = exc.headers.get("Retry-After")
            if value:
                try:
                    delay = float(value)
                except ValueError:
                    delay = (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds()
                if delay > 120:
                    raise ValueError("Retry-After exceeds manual retry budget; retry later")
            else:
                delay = 2 ** attempt
            time.sleep(max(0, delay))
        except (URLError, TimeoutError, ConnectionError, HTTPException):
            if attempt == 2:
                raise ValueError("successor network retry budget exhausted") from None
            time.sleep(2 ** attempt)
    raise ValueError("no response")


def acquire(output: Path, *, fetcher=fetch, sleep=time.sleep):
    output = output.resolve()
    if output.is_relative_to(ROOT) or any((parent / ".git").exists() for parent in [output, *output.parents]):
        raise ValueError("raw acquisition directory must be outside any Git repository")
    if output.exists() and any(output.iterdir()):
        raise ValueError("acquisition directory must be new/empty")
    output.mkdir(parents=True, exist_ok=True)
    manifest = {"profile": PROFILE, "startedAt": now(), "openApiUrl": OPENAPI_URL, "sources": {}}
    for dataset, url in URLS.items():
        raw, evidence = fetcher(url)
        rows = json.loads(raw)
        if not isinstance(rows, list) or not rows or not all(isinstance(row, dict) for row in rows):
            raise ValueError("expected a nonempty complete source array of objects")
        filename = dataset + ".json"
        (output / filename).write_bytes(raw)
        manifest["sources"][dataset] = dict(evidence, file=filename, bytes=len(raw),
            sha256=hashlib.sha256(raw).hexdigest(), rows=len(rows), schemaKeys=sorted(set().union(*(row.keys() for row in rows))))
        print(f"Captured {dataset}: {len(rows)} source rows / {len(raw)} bytes", flush=True)
        sleep(1.5)
    manifest["acquiredAt"] = now()
    manifest["manifestSha256"] = manifest_hash(manifest)
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = acquire(args.output_dir)
        print(f"Complete acquisition: {result['acquiredAt']}, manifest {result['manifestSha256']}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"Acquisition failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
