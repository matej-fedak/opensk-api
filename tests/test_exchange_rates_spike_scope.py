"""Keep the 0.23.3 spike residue clean now that 0.23.4 promoted exchange rates.

The spike-era guards (no routes, no production dataset) were retired when the
production surface landed; these guards keep the leftover research-only
artifacts from leaking back in.
"""

import subprocess
from pathlib import Path


def test_exchange_rates_preview_output_stays_ignored() -> None:
    repo = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        ["git", "check-ignore", "-v", "data/generated/exchange_rates_preview.json"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert ".gitignore" in result.stdout


def test_exchange_rates_production_dataset_is_not_gitignored() -> None:
    repo = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        ["git", "check-ignore", "data/exchange_rates.json"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0  # must be tracked, never ignored
