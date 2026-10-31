#!/usr/bin/env python3
"""Offline evidence for five manually downloaded NRSR2023 aggregate CSVs.

No downloader and no production JSON writer. Reuses the researched CSV parser;
this manifest stage is not a substitute for semantic import/reconciliation.
Default: print a non-content manifest without writing any files.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import import_elections as importer


SOURCE_PAGE = "https://volby.statistics.sk/nrsr/nrsr2023/sk/subory_na_stiahnutie.html"
FILE_BASE = "https://volby.statistics.sk/nrsr/nrsr2023/files/csv/"
LICENCE_URL = "https://creativecommons.org/licenses/by/4.0/"
MANIFEST_PROFILE = "opensk-nrsr2023-manual-acquisition-v1"
COMMITTED_MANIFEST = importer.ROOT / "docs/research/elections-nrsr2023-acquisition.json"

# Exact headers/row counts from elections-data-schema.md (2026-10-11).
# tab03e is intentionally not an input; candidate/person tables are never opened.
TABLES = {
    "tab0c": (importer.TERRITORY_HEADERS, 2927),
    "tab02d": (importer.RESULT_HEADERS, 2927),
    "tab01": (importer.NATIONAL_HEADERS, 1),
    "tab03a": (importer.PARTY_HEADERS[8:] + ("Počet získaných mandátov",), 25),
    "tab0a": (("Číslo politického subjektu", "Názov politického subjektu",
               "Skratka politického subjektu", "Počet kandidátov", "Poznámka"), 25),
}

# Comparison only, not an acceptance allowlist. The research document's full
# tab01 digest is authoritative; the abbreviated digest in the task is not used.
HISTORICAL_HASHES = {
    "tab0c": "479fe57712c4a1500e466ddd2bf7b967e1aeec69fceb34326a2683f29519fa1f",
    "tab02d": "cbabf05cf3d64bd92106670363c538fbaf0b9ea3a547339b917c022c1f484a5e",
    "tab01": "539bce1f2141b9bb789ad1ea627bfa9acc1ce40d9414e3f992b387abc0f4b0fd",
    "tab03a": "53a48342f14008941fd06ad7cf70a3de332336b80971841afc01ce92bc03a289",
    "tab0a": "832f6bbcd6c85a01c77bcbdc4483762c5ae059491e5ad4ce5eccfc55efac9df1",
}


def acquisition_timestamp(value: str) -> str:
    """Use only the supplied, timezone-aware timestamp, never mtime/the clock."""
    if "T" not in value:
        raise ValueError("manually-acquired-at requires an ISO timestamp with timezone")
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid manually-acquired-at timestamp") from exc
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ValueError("manually-acquired-at requires a timezone")
    return stamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def prepare_manifest(source_dir: Path, manually_acquired_at: str, *,
                     attest_manual_download: bool = False,
                     profile: str = MANIFEST_PROFILE,
                     acquisition_time_precision: str = "exact") -> dict:
    if profile != MANIFEST_PROFILE:
        raise ValueError("unsupported election acquisition profile; NRSR2023 only")
    if attest_manual_download is not True:
        raise ValueError("manual official download attestation is required; research bytes are not substitutes")
    stamp = acquisition_timestamp(manually_acquired_at)
    if acquisition_time_precision not in {"exact", "approximate-minute"}:
        raise ValueError("unsupported acquisition time precision")
    directory = source_dir.resolve()
    if directory.is_relative_to(importer.ROOT):
        raise ValueError("raw source directory must be private and outside the repository")
    paths = {key: directory / f"NRSR2023_SK_{key}.csv" for key in TABLES}
    missing = [path.name for path in paths.values() if not path.is_file()]
    if missing:
        raise ValueError("MANUAL_SOURCE_FILES_REQUIRED: " + ", ".join(missing))
    if any(path.resolve().is_relative_to(importer.ROOT) for path in paths.values()):
        raise ValueError("raw source files must remain outside the repository")
    report = {"inputs": {}}
    files = []
    for key, (headers, count) in TABLES.items():
        path = paths[key]
        rows = importer.read_table(path, headers, key, report)
        if len(rows) != count:
            raise ValueError(f"{path.name}: expected {count} data rows, found {len(rows)}; review required")
        evidence = report["inputs"][key]
        files.append({
            "filename": path.name,
            "sourceUrl": FILE_BASE + path.name,
            "manuallyAcquired": True,
            "manuallyAcquiredAt": stamp,
            "sourcePublishedAt": None,  # Per-file publication time is unestablished.
            "bytes": evidence["bytes"],
            "sha256": evidence["sha256"],
            "rowCount": len(rows),
            "headers": list(headers),
            "headerSha256": hashlib.sha256(
                json.dumps(list(headers), ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            ).hexdigest(),
            "headerHashRepresentation": "UTF-8 compact JSON array, ensure_ascii=false, no trailing newline",
            "encoding": "UTF-8",
            "bom": False,
            "delimiter": ",",
            "newline": "LF",
            "historicalResearchSha256": HISTORICAL_HASHES[key],
            "historicalHashComparison": ("MATCH" if evidence["sha256"] == HISTORICAL_HASHES[key]
                                         else "DIFFERENT_REQUIRES_REVIEW"),
        })
    return {
        "profile": MANIFEST_PROFILE,
        "importerProfile": importer.PRODUCTION_PROFILE,
        "electionId": "NRSR2023",
        "sourcePage": SOURCE_PAGE,
        "publisher": "Štatistický úrad Slovenskej republiky",
        "status": "MANIFEST_PREPARED_SEMANTIC_REVIEW_REQUIRED",
        "manuallyAcquired": True,
        "manuallyAcquiredAt": stamp,
        "acquisitionTimePrecision": acquisition_time_precision,
        "acquisitionTimeBasis": ("Maintainer supplied timestamp" if acquisition_time_precision == "exact" else
                                 "Maintainer confirmed manual download just now; session clock recorded to minute, not exact download time"),
        "sourcePublication": {
            "pageStatement": "2023-10-01 14:30",
            "timezone": None,
            "evidence": "docs/research/elections-data-schema.md (2026-10-11 research)",
            "note": "Page-level definitive-results publication statement, not per-file publication or acquisition time.",
        },
        "licence": "CC-BY-4.0",
        "licenceUrl": LICENCE_URL,
        "publisherReplyReceivedOn": "2026-10-30",
        "acquisitionRestriction": "MANUAL_OFFICIAL_DOWNLOAD_ONLY; automated website downloading prohibited",
        "transformations": [
            "Manifest only: rehash raw files, parse reviewed UTF-8 CSV headers and count rows offline.",
            "No source data rows retained here; production normalization/reconciliation still required.",
        ],
        "files": files,
    }


def write_manifest(path: Path, payload: dict) -> None:
    destination = path.resolve()
    if destination.suffix != ".json":
        raise ValueError("manifest output must be JSON")
    if destination.is_relative_to(importer.ROOT) and destination != COMMITTED_MANIFEST.resolve():
        raise ValueError("repository writes allowed only at docs/research/elections-nrsr2023-acquisition.json")
    # No implicit replacement of user work or previous acquisition evidence.
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as stream:
        stream.write(importer.serialize_payload(payload))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--manually-acquired-at", required=True)
    parser.add_argument("--attest-manual-download", action="store_true")
    parser.add_argument("--profile", default=MANIFEST_PROFILE)
    parser.add_argument("--acquisition-time-precision", choices=("exact", "approximate-minute"), default="exact")
    parser.add_argument("--write-manifest", type=Path, help="explicit non-content manifest write; no overwrites")
    args = parser.parse_args(argv)
    try:
        manifest = prepare_manifest(args.source_dir, args.manually_acquired_at,
                                    attest_manual_download=args.attest_manual_download,
                                    profile=args.profile,
                                    acquisition_time_precision=args.acquisition_time_precision)
        if args.write_manifest:
            write_manifest(args.write_manifest, manifest)
    except (ValueError, OSError, UnicodeError, csv.Error) as exc:
        # Keep machine paths out of even failure reports; no invented acquisition.
        message = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
        sys.stdout.buffer.write(importer.serialize_payload({"ok": False, "error": message}))
        return 1
    sys.stdout.buffer.write(importer.serialize_payload(manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
