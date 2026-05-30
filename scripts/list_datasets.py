#!/usr/bin/env python3
"""List repository dataset files with record counts and coverage notes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def count_records(payload: Any) -> int | None:
    if isinstance(payload, list):
        return len(payload)

    if isinstance(payload, dict):
        if "metadata" in payload:
            data_keys = [key for key in payload.keys() if key != "metadata"]
            if len(data_keys) == 1 and isinstance(payload[data_keys[0]], list):
                return len(payload[data_keys[0]])

        if payload and all(isinstance(value, list) for value in payload.values()):
            return sum(len(value) for value in payload.values())

        return len(payload)

    return None


def coverage_status(payload: Any, dataset_name: str) -> str:
    if isinstance(payload, dict):
        metadata = payload.get("metadata")
        if isinstance(metadata, dict):
            if "complete" in metadata:
                return "complete" if metadata["complete"] else "seed/incomplete"

            source = metadata.get("source")
            if isinstance(source, str):
                lowered = source.lower()
                if "not exhaustive" in lowered or "incomplete" in lowered:
                    return "incomplete"
                if "seed" in lowered:
                    return "seed"

    documented = {
        "banks": "seed/incomplete",
        "districts": "seed/incomplete",
        "holidays": "static",
        "municipalities": "seed/incomplete",
        "psc": "seed/partial",
        "regions": "complete",
    }
    return documented.get(dataset_name, "not documented")


def main() -> None:
    if not DATA_DIR.is_dir():
        raise SystemExit(f"data directory not found: {DATA_DIR}")

    dataset_files = sorted(DATA_DIR.glob("*.json"))
    if not dataset_files:
        print("No dataset files found.")
        return

    rows: list[tuple[str, str, str]] = []
    total_records = 0

    for path in dataset_files:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            rows.append((path.name, "n/a", "unreadable"))
            continue

        records = count_records(payload)
        coverage = coverage_status(payload, path.stem)
        count_text = "n/a" if records is None else str(records)
        if records is not None:
            total_records += records
        rows.append((path.name, count_text, coverage))

    name_width = max(len(name) for name, _, _ in rows)
    count_width = max(len(count) for _, count, _ in rows)

    print(f"Datasets in {DATA_DIR.relative_to(ROOT)}")
    for name, count, coverage in rows:
        print(f"{name.ljust(name_width)}  {count.rjust(count_width)} records  coverage: {coverage}")
    print(f"Total: {len(rows)} files, {total_records} records")


if __name__ == "__main__":
    main()
