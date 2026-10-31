#!/usr/bin/env python3
"""Bounded, build-time-only acquisition of the official TED Search API.

Raw pages and token-bearing responses must stay outside Git. A completed manifest
is written only after an empty terminal page AND exact stable-total agreement.
"""

import argparse
from datetime import date, datetime, UTC
import hashlib
import json
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.fetch_procurement_notices import TED_FIELDS, TED_SEARCH_URL

PROFILE = "opensk-ted-reference-v1"
PRIVACY_PROFILE = "opensk-ted-buyer-privacy-v1"
# Explicit research-only projection. Reuse names/cardinality/title from the
# already retained first capture; never reacquire names, titles or contacts.
PRIVACY_FIELDS = [
    "publication-number", "publication-date", "buyer-country", "buyer-person",
    "buyer-legal-type", "buyer-identifier", "customization-id", "notice-subtype",
]
PROFILE_FIELDS = {PROFILE: TED_FIELDS, PRIVACY_PROFILE: PRIVACY_FIELDS}
DOCS_URL = "https://docs.ted.europa.eu/api/latest/search.html"
OPENAPI_URL = "https://api.ted.europa.eu/api-v3.yaml"
LEGAL_URL = "https://ted.europa.eu/en/legal-notice"


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def sha(value):
    return hashlib.sha256(value).hexdigest()


def instant():
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def query_for(cutoff, start=None):
    date.fromisoformat(cutoff)
    query = f"buyer-country = SVK AND publication-date <= {cutoff.replace('-', '')}"
    if start:
        if date.fromisoformat(start) > date.fromisoformat(cutoff):
            raise ValueError("start date is after cutoff")
        query += f" AND publication-date >= {start.replace('-', '')}"
    return query


def request_payload(cutoff, limit=250, token=None, start=None, *, profile=PROFILE):
    if not 1 <= limit <= 250:
        raise ValueError("TED limit must be 1..250")
    if profile not in PROFILE_FIELDS:
        raise ValueError("unknown acquisition profile")
    payload = {"query": query_for(cutoff, start), "fields": list(PROFILE_FIELDS[profile]),
               "limit": limit, "paginationMode": "ITERATION", "onlyLatestVersions": True}
    if token:
        payload["iterationNextToken"] = token
    return payload


def source_date(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}(?:Z|[+-][0-9]{2}:[0-9]{2})?", value):
        raise ValueError("invalid TED publication date")
    return date.fromisoformat(value[:10])


def validate_scope(row, cutoff, start=None):
    if not isinstance(row, dict):
        raise ValueError("notice must be an object")
    record_id = row.get("publication-number")
    if not isinstance(record_id, str) or not re.fullmatch(r"[0-9]{1,6}-[0-9]{4}", record_id) or int(record_id.split("-")[0]) == 0:
        raise ValueError("invalid publication number")
    published = source_date(row.get("publication-date"))
    if published.year != int(record_id[-4:]):
        raise ValueError("publication ID/date year mismatch")
    if published > date.fromisoformat(cutoff) or (start and published < date.fromisoformat(start)):
        raise ValueError("notice outside fixed publication-date scope")
    countries = row.get("buyer-country")
    if not isinstance(countries, list) or not all(isinstance(c, str) for c in countries) or "SVK" not in countries:
        raise ValueError("notice has no Slovak buyer-country scope")
    # The reviewed API exposes latest-only as a server query option, not a row
    # assertion. Reject a contrary marker if an API adds one; never invent one.
    if row.get("isLatestVersion") is False or row.get("latestVersion") is False:
        raise ValueError("obsolete version returned by latest-only request")
    # Historic TED numbers are unpadded (e.g. 150-2017). Numeric zero-padding
    # is an exact identity normalization, not fuzzy deduplication/new identity.
    number, year = record_id.split("-")
    return f"{int(number):06d}-{year}"


def fetch(payload, *, attempts=3, timeout=60, sleep=time.sleep, http=None, statuses=None):
    http = http or urllib.request.urlopen
    statuses = statuses if statuses is not None else {}
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(TED_SEARCH_URL, data=encoded(payload), method="POST",
                headers={"Content-Type": "application/json", "Accept": "application/json",
                         "User-Agent": "OpenSK-Offline-TED/0.23.13 (https://github.com/matej-fedak/opensk-api)"})
            with http(request, timeout=timeout) as response:
                statuses[str(response.status)] = statuses.get(str(response.status), 0) + 1
                content_type = response.headers.get("Content-Type", "")
                if response.status != 200 or content_type.split(";", 1)[0].lower() != "application/json":
                    raise ValueError("TED must return HTTP 200 application/json")
                raw = response.read(32 * 1024 * 1024 + 1)
                if len(raw) > 32 * 1024 * 1024:
                    raise ValueError("TED page exceeds bounded response size")
            body = json.loads(raw)
            if body.get("timedOut") is not False:
                raise TimeoutError("TED search timed out")
            return raw, body, content_type
        except urllib.error.HTTPError as exc:
            statuses[str(exc.code)] = statuses.get(str(exc.code), 0) + 1
            if exc.code not in {429, 500, 502, 503, 504} or attempt == attempts - 1:
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == attempts - 1:
                raise
        sleep(2 ** attempt)
    raise AssertionError("unreachable retry exhaustion")


def acquire(output, cutoff, *, start=None, limit=250, max_pages=1000, fetcher=fetch, delay=0.1, profile=PROFILE):
    if profile not in PROFILE_FIELDS:
        raise ValueError("unknown acquisition profile")
    output = Path(output).resolve()
    if output.is_relative_to(ROOT):
        raise ValueError("Raw acquisition must be outside the repository")
    if date.fromisoformat(cutoff) > datetime.now(UTC).date():
        raise ValueError("cutoff cannot be in the future")
    if max_pages < 1 or max_pages > 2000:
        raise ValueError("max-pages must be 1..2000")
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("Use a new empty acquisition directory; never mix runs")
    manifest = {"profile": profile, "startedAt": instant(), "apiUrl": TED_SEARCH_URL,
                "documentationUrl": DOCS_URL, "openapiUrl": OPENAPI_URL, "apiVersion": "3.0.0",
                "legalUrl": LEGAL_URL, "query": query_for(cutoff, start), "cutoff": cutoff,
                "startDate": start, "fields": list(PROFILE_FIELDS[profile]), "paginationMode": "ITERATION",
                "onlyLatestVersions": True, "limit": limit, "maxPages": max_pages,
                "pages": [], "httpStatuses": {}, "duplicates": 0, "malformed": 0}
    token = None
    tokens = set()
    ids = set()
    total = None
    for number in range(1, max_pages + 1):
        payload = request_payload(cutoff, limit, token, start, profile=profile)
        raw, body, content_type = fetcher(payload, statuses=manifest["httpStatuses"])
        count = body.get("totalNoticeCount")
        if type(count) is not int or count < 0 or (total is not None and count != total):
            raise ValueError("invalid or moving TED total")
        total = count
        rows = body.get("notices")
        if not isinstance(rows, list) or len(rows) > limit:
            raise ValueError("invalid notices page")
        for row in rows:
            record_id = validate_scope(row, cutoff, start)
            if record_id in ids:
                raise ValueError("duplicate publication number; fail closed")
            ids.add(record_id)
        next_token = body.get("iterationNextToken")
        if rows and (not isinstance(next_token, str) or not next_token or next_token in tokens):
            raise ValueError("missing or repeated iteration token before completion")
        if len(ids) > total:
            raise ValueError("acquired rows exceed reported total")
        name = f"page-{number:04d}.json"
        (output / name).write_bytes(raw)
        manifest["pages"].append({"file": name, "bytes": len(raw), "sha256": sha(raw),
             "rows": len(rows), "contentType": content_type, "requestSha256": sha(encoded(payload))})
        if not rows:
            if len(ids) != total:
                raise ValueError("empty terminal page before reported total; truncated acquisition")
            manifest.update({"finishedAt": instant(), "reportedTotal": total, "acquiredTotal": len(ids),
                             "pageCount": number, "rawBytes": sum(p["bytes"] for p in manifest["pages"]),
                             "complete": True})
            manifest["pagesSha256"] = sha(encoded(manifest["pages"]))
            (output / "manifest.json").write_bytes(encoded(manifest))
            return manifest
        tokens.add(next_token)
        token = next_token
        if delay:
            time.sleep(delay)
    raise ValueError("max-pages exhausted; acquisition is incomplete")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cutoff", required=True)
    parser.add_argument("--start-date")
    parser.add_argument("--limit", type=int, default=250)
    parser.add_argument("--max-pages", type=int, default=1000)
    parser.add_argument("--profile", choices=PROFILE_FIELDS, default=PROFILE)
    args = parser.parse_args()
    manifest = acquire(args.output, args.cutoff, start=args.start_date, limit=args.limit, max_pages=args.max_pages, profile=args.profile)
    print(json.dumps({k: v for k, v in manifest.items() if k != "pages"}, indent=2))


if __name__ == "__main__":
    main()
