#!/usr/bin/env python3
"""Check geography references and independent election-native consistency."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.import_utils import collect_referential_integrity_errors


def collect_errors(data_dir: Path | None = None) -> list[str]:
    data_dir = data_dir or ROOT / "data"
    errors = collect_referential_integrity_errors(data_dir)
    # Election relationships are internal to the historical election dictionary.
    # No FK to current municipalities (especially not Cudzina / 599999).
    if (data_dir / "elections_nrsr_2023.json").is_file():
        from scripts.validate_datasets import validate_elections_dataset
        report = validate_elections_dataset(data_dir / "elections_nrsr_2023.json")
        errors.extend(f"elections: {issue.path}: {issue.message}" for issue in report.errors)
    return errors


def main() -> int:
    errors = collect_errors()

    if errors:
        print("Referential integrity check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Referential integrity check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
