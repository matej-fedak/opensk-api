"""Keep the 0.23.3 exchange-rates spike pre-production."""

from pathlib import Path

from fastapi.testclient import TestClient

from main import app


def test_exchange_rates_spike_adds_no_public_routes() -> None:
    client = TestClient(app)
    paths = client.get("/openapi.json").json()["paths"]
    assert not any(path.startswith("/v1/exchange-rates") for path in paths)
    assert not any("exchange" in path for path in paths)


def test_exchange_rates_spike_has_no_production_dataset() -> None:
    data = Path(__file__).resolve().parents[1] / "data"
    assert not list(data.glob("exchange_rates*.json"))


def test_exchange_rates_preview_output_stays_ignored() -> None:
    repo = Path(__file__).resolve().parents[1]
    import subprocess

    result = subprocess.run(
        ["git", "check-ignore", "-v", "data/generated/exchange_rates_preview.json"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert ".gitignore" in result.stdout
