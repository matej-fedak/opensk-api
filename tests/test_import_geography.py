from __future__ import annotations

import csv
import json
from pathlib import Path

from scripts.import_geography import run_import
from scripts.import_utils import load_dataset_records


def _regions_payload() -> list[dict[str, str]]:
    return [
        {"code": "SK010", "name": "Bratislavský kraj", "nameEn": "Bratislava Region", "country": "SK"},
        {"code": "SK020", "name": "Trnavský kraj", "nameEn": "Trnava Region", "country": "SK"},
        {"code": "SK031", "name": "Trenčiansky kraj", "nameEn": "Trenčín Region", "country": "SK"},
        {"code": "SK032", "name": "Nitriansky kraj", "nameEn": "Nitra Region", "country": "SK"},
        {"code": "SK041", "name": "Žilinský kraj", "nameEn": "Žilina Region", "country": "SK"},
        {"code": "SK042", "name": "Banskobystrický kraj", "nameEn": "Banská Bystrica Region", "country": "SK"},
        {"code": "SK051", "name": "Prešovský kraj", "nameEn": "Prešov Region", "country": "SK"},
        {"code": "SK052", "name": "Košický kraj", "nameEn": "Košice Region", "country": "SK"},
    ]


def test_json_import_validates_without_writing(tmp_path: Path) -> None:
    input_file = tmp_path / "regions.json"
    input_file.write_text(json.dumps(_regions_payload(), ensure_ascii=False), encoding="utf-8")

    output_dir = tmp_path / "output"
    result = run_import(
        dataset="regions",
        source="unit-test",
        input_path=input_file,
        output_path=output_dir,
        write=False,
        allow_incomplete=True,
    )

    assert result.validation_reports[0].ok
    assert result.wrote_files == []
    assert result.integrity_errors
    assert not (output_dir / "regions.json").exists()


def test_csv_import_writes_single_dataset(tmp_path: Path) -> None:
    input_file = tmp_path / "regions.csv"
    with input_file.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["code", "name", "nameEn", "country"])
        writer.writeheader()
        for record in _regions_payload():
            writer.writerow(record)

    records = load_dataset_records("regions", input_file)
    assert len(records) == 8

    output_dir = tmp_path / "output"
    result = run_import(
        dataset="regions",
        source="unit-test",
        input_path=input_file,
        output_path=output_dir,
        write=True,
        allow_incomplete=True,
    )

    output_file = output_dir / "regions.json"
    assert output_file.exists()
    assert result.wrote_files == [output_file]

    payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert payload["metadata"]["source"] == "unit-test"
    assert payload["regions"] == _regions_payload()
