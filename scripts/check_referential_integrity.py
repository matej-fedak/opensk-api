#!/usr/bin/env python3
"""Check PSC and geography referential integrity."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.import_utils import collect_referential_integrity_errors


def collect_errors(data_dir: Path | None = None) -> list[str]:
    return collect_referential_integrity_errors(data_dir or ROOT / "data")


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
