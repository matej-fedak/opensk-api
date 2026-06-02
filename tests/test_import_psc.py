from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from scripts.import_psc import run_import


FIELDNAMES = (
    "psc",
    "deliveryPost",
    "municipalityCode",
    "city",
    "municipality",
    "district",
    "region",
    "districtCode",
    "regionCode",
    "country",
    "validFrom",
    "validTo",
)


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def _valid_rows() -> list[dict[str, str]]:
    base = {
        "psc": "81 101",
        "municipalityCode": "528595",
        "city": "Bratislava",
        "municipality": "Bratislava - mestská časť Staré Mesto",
        "district": "Bratislava I",
        "region": "Bratislavský kraj",
        "districtCode": "SK0101",
        "regionCode": "SK010",
        "country": "Slovakia",
    }
    return [
        {**base, "deliveryPost": "Bratislava 1", "validFrom": "2026-01-01", "validTo": "2026-06-30"},
        {**base, "deliveryPost": "Bratislava 2", "validFrom": "2026-07-01", "validTo": "2026-12-31"},
    ]


def test_import_valid_sample_csv_writes_normalized_json(tmp_path: Path) -> None:
    input_file = tmp_path / "psc.csv"
    output_dir_one = tmp_path / "out-one"
    output_dir_two = tmp_path / "out-two"
    _write_csv(input_file, _valid_rows())

    result_one = run_import(input_path=input_file, output_path=output_dir_one, write=True)
    result_two = run_import(input_path=input_file, output_path=output_dir_two, write=True)

    assert result_one.ok
    assert result_two.ok

    output_file_one = output_dir_one / "psc.json"
    output_file_two = output_dir_two / "psc.json"
    payload_one = json.loads(output_file_one.read_text(encoding="utf-8"))
    payload_two = json.loads(output_file_two.read_text(encoding="utf-8"))

    assert output_file_one.read_text(encoding="utf-8") == output_file_two.read_text(encoding="utf-8")
    assert set(payload_one) == {"metadata", "81101"}
    assert payload_one == payload_two

    record = payload_one["81101"]
    assert record["psc"] == "81101"
    assert record["matchCount"] == 2
    assert [match["deliveryPost"] for match in record["matches"]] == ["Bratislava 1", "Bratislava 2"]
    assert record["matches"][0]["psc"] == "81101"


def test_dry_run_writes_nothing(tmp_path: Path) -> None:
    input_file = tmp_path / "psc.csv"
    output_dir = tmp_path / "out"
    _write_csv(input_file, _valid_rows())

    result = run_import(input_path=input_file, output_path=output_dir, write=False)

    assert result.dry_run is True
    assert result.wrote_files == []
    assert not (output_dir / "psc.json").exists()


def test_invalid_psc_is_rejected(tmp_path: Path) -> None:
    input_file = tmp_path / "psc.csv"
    _write_csv(
        input_file,
        [{**_valid_rows()[0], "psc": "81A01"}],
    )

    with pytest.raises(ValueError, match="PSC must be exactly 5 digits"):
        run_import(input_path=input_file, output_path=tmp_path / "out", write=False)


def test_exact_duplicate_record_is_rejected(tmp_path: Path) -> None:
    input_file = tmp_path / "psc.csv"
    row = _valid_rows()[0]
    _write_csv(input_file, [row, dict(row)])

    result = run_import(input_path=input_file, output_path=tmp_path / "out", write=False)

    assert not result.ok
    assert any("Duplicate PSC record 81101" in error for error in result.integrity_errors)


def test_unknown_municipality_code_requires_flag(tmp_path: Path) -> None:
    input_file = tmp_path / "psc.csv"
    row = {**_valid_rows()[0], "municipalityCode": "999999"}
    _write_csv(input_file, [row])

    rejected = run_import(input_path=input_file, output_path=tmp_path / "out-rejected", write=False)
    allowed = run_import(
        input_path=input_file,
        output_path=tmp_path / "out-allowed",
        write=True,
        allow_unresolved_geography=True,
    )

    assert not rejected.ok
    assert any("unknown municipalityCode 999999" in error for error in rejected.integrity_errors)

    assert allowed.ok
    output = json.loads((tmp_path / "out-allowed" / "psc.json").read_text(encoding="utf-8"))
    assert output["81101"]["municipalityCode"] is None
