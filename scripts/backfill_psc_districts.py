#!/usr/bin/env python3
"""Backfill PSC districtCode values from municipality mappings."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_INPUT = ROOT / "data" / "psc.json"
DEFAULT_OUTPUT = ROOT / "data" / "generated" / "psc.with-districts.json"
DEFAULT_DATA_DIR = ROOT / "data"


@dataclass
class BackfillStats:
    total_records: int = 0
    records_with_municipality_code: int = 0
    successfully_backfilled: int = 0
    unresolved_municipality_codes: set[str] = field(default_factory=set)
    region_conflicts: list[str] = field(default_factory=list)
    invalid_district_codes: list[str] = field(default_factory=list)
    district_code_coverage_before: int = 0
    district_code_coverage_after: int = 0

    @property
    def unresolved_municipality_code_count(self) -> int:
        return len(self.unresolved_municipality_codes)

    @property
    def region_conflict_count(self) -> int:
        return len(self.region_conflicts)

    @property
    def ok(self) -> bool:
        return not self.region_conflicts and not self.invalid_district_codes


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _load_index(path: Path, collection_key: str) -> dict[str, dict[str, Any]]:
    payload = _read_json(path)
    if not isinstance(payload, dict) or not isinstance(payload.get(collection_key), list):
        raise ValueError(f"{path} must contain a {collection_key} array")

    index: dict[str, dict[str, Any]] = {}
    for record in payload[collection_key]:
        if isinstance(record, dict) and isinstance(record.get("code"), str):
            index[record["code"]] = record
    return index


def _canonical_psc_records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for psc_code, record in payload.items():
        if psc_code == "metadata" or not isinstance(record, dict):
            continue
        matches = record.get("matches")
        if isinstance(matches, list) and matches:
            records.extend(match for match in matches if isinstance(match, dict))
        else:
            records.append(record)
    return records


def _psc_entries(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [record for psc_code, record in payload.items() if psc_code != "metadata" and isinstance(record, dict)]


def _backfill_record(
    record: dict[str, Any],
    *,
    municipalities: dict[str, dict[str, Any]],
    districts: dict[str, dict[str, Any]],
    stats: BackfillStats,
    counted: bool,
) -> None:
    municipality_code = record.get("municipalityCode")
    if counted:
        stats.total_records += 1
        if record.get("districtCode") is not None:
            stats.district_code_coverage_before += 1

    if not isinstance(municipality_code, str) or not municipality_code:
        record["districtCode"] = None
        return

    if counted:
        stats.records_with_municipality_code += 1

    municipality = municipalities.get(municipality_code)
    if municipality is None:
        record["districtCode"] = None
        if counted:
            stats.unresolved_municipality_codes.add(municipality_code)
        return

    municipality_region_code = municipality.get("regionCode")
    psc_region_code = record.get("regionCode")
    if isinstance(psc_region_code, str) and municipality_region_code != psc_region_code:
        record["districtCode"] = None
        if counted:
            psc = record.get("psc") or "unknown"
            stats.region_conflicts.append(f"PSC {psc}: municipalityCode {municipality_code} regionCode {municipality_region_code} != PSC regionCode {psc_region_code}")
        return

    district_code = municipality.get("districtCode")
    if not isinstance(district_code, str) or district_code not in districts:
        record["districtCode"] = None
        if counted:
            psc = record.get("psc") or "unknown"
            stats.invalid_district_codes.append(f"PSC {psc}: municipalityCode {municipality_code} has invalid districtCode {district_code!r}")
        return

    record["districtCode"] = district_code
    if counted:
        stats.successfully_backfilled += 1
        stats.district_code_coverage_after += 1


def backfill_psc_districts(input_path: Path, data_dir: Path = DEFAULT_DATA_DIR) -> tuple[dict[str, Any], BackfillStats]:
    payload = _read_json(input_path)
    if not isinstance(payload, dict):
        raise ValueError("PSC input must be a JSON object")

    municipalities = _load_index(data_dir / "municipalities.json", "municipalities")
    districts = _load_index(data_dir / "districts.json", "districts")
    _load_index(data_dir / "regions.json", "regions")

    stats = BackfillStats()
    canonical_records = _canonical_psc_records(payload)
    for record in canonical_records:
        _backfill_record(record, municipalities=municipalities, districts=districts, stats=stats, counted=True)

    counted_ids = {id(record) for record in canonical_records}
    for record in _psc_entries(payload):
        if id(record) not in counted_ids:
            _backfill_record(record, municipalities=municipalities, districts=districts, stats=stats, counted=False)

    return payload, stats


def _coverage_text(count: int, total: int) -> str:
    percentage = round((count / total * 100) if total else 0.0, 1)
    return f"{count}/{total} ({percentage:.1f}%)"


def _print_stats(stats: BackfillStats, *, dry_run: bool, output_path: Path) -> None:
    print(f"total PSC records: {stats.total_records}")
    print(f"records with municipalityCode: {stats.records_with_municipality_code}")
    print(f"records successfully backfilled: {stats.successfully_backfilled}")
    print(f"unresolved municipalityCode count: {stats.unresolved_municipality_code_count}")
    print(f"region conflict count: {stats.region_conflict_count}")
    print(f"districtCode coverage before: {_coverage_text(stats.district_code_coverage_before, stats.total_records)}")
    print(f"districtCode coverage after: {_coverage_text(stats.district_code_coverage_after, stats.total_records)}")
    if dry_run:
        print("Dry run only; no files written.")
    else:
        print(f"Wrote: {output_path}")

    for municipality_code in sorted(stats.unresolved_municipality_codes):
        print(f"WARNING unresolved municipalityCode: {municipality_code}")
    for conflict in stats.region_conflicts:
        print(f"ERROR {conflict}")
    for invalid in stats.invalid_district_codes:
        print(f"ERROR {invalid}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Backfill PSC districtCode values from municipality mappings.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="PSC input JSON path")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output JSON path")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Validate and report only; do not write files")
    mode.add_argument("--write", action="store_true", help="Write the generated PSC JSON")
    parser.add_argument("--promote", action="store_true", help="Write directly to data/psc.json after validation")
    args = parser.parse_args(argv)

    output_path = ROOT / "data" / "psc.json" if args.promote else args.output
    payload, stats = backfill_psc_districts(args.input)
    dry_run = not args.write and not args.promote

    if not dry_run:
        _write_json(output_path, payload)

    _print_stats(stats, dry_run=dry_run, output_path=output_path)
    return 0 if stats.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
