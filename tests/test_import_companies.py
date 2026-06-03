from __future__ import annotations

import json
from pathlib import Path

from scripts.import_companies import run_import


def _sample_payload() -> dict[str, object]:
    return {
        "metadata": {"source": "unit-test", "lastUpdated": "2026-06-03"},
        "records": [
            {
                "IČO": "87654321",
                "name": "Beta, a.s.",
                "legalForm": "a.s.",
                "legalStatus": "active",
                "sourceRegister": "Obchodný register",
                "recordId": "RPO-87654321",
                "establishedOn": "2020-05-01",
                "updatedAt": "2026-06-02",
                "sidlo": {
                    "street": "Beta 1",
                    "registrationNumber": "1",
                    "buildingNumber": "2",
                    "postalCode": "82101",
                    "municipality": "Bratislava",
                    "municipalityCode": "528595",
                    "regionCode": "SK010",
                    "country": "Slovakia",
                },
            },
            {
                "ico": "01234567",
                "name": "Example, s.r.o.",
                "legalForm": "s.r.o.",
                "legalStatus": "active",
                "sidlo": "Example Street 1, Bratislava",
            },
        ],
    }


def test_dry_run_does_not_write_output(tmp_path: Path) -> None:
    input_file = tmp_path / "companies.json"
    input_file.write_text(json.dumps(_sample_payload(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    output_dir = tmp_path / "output"
    result = run_import(input_path=input_file, output_path=output_dir, write=False)

    assert result.ok
    assert result.dry_run is True
    assert result.wrote_files == []
    assert not (output_dir / "companies.json").exists()


def test_write_normalizes_and_sorts_companies(tmp_path: Path) -> None:
    input_file = tmp_path / "companies.json"
    input_file.write_text(json.dumps(_sample_payload(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    output_one = tmp_path / "output-one"
    output_two = tmp_path / "output-two"

    result_one = run_import(input_path=input_file, output_path=output_one, source="unit-test", write=True)
    result_two = run_import(input_path=input_file, output_path=output_two, source="unit-test", write=True)

    assert result_one.ok
    assert result_two.ok

    file_one = output_one / "companies.json"
    file_two = output_two / "companies.json"
    payload_one = json.loads(file_one.read_text(encoding="utf-8"))
    payload_two = json.loads(file_two.read_text(encoding="utf-8"))

    assert file_one.read_text(encoding="utf-8") == file_two.read_text(encoding="utf-8")
    assert payload_one == payload_two
    assert payload_one["metadata"]["source"] == "unit-test"
    assert payload_one["metadata"]["lastUpdated"] == "2026-06-03"
    assert [record["ico"] for record in payload_one["companies"]] == ["01234567", "87654321"]

    first, second = payload_one["companies"]
    assert first["source"]["name"] == "unit-test"
    assert first["source"]["recordId"] == "01234567"
    assert second["legalStatus"] == "active"
    assert second["sourceRegister"] == "Obchodný register"
    assert second["address"] == {
        "street": "Beta 1",
        "registrationNumber": "1",
        "buildingNumber": "2",
        "municipality": "Bratislava",
        "postalCode": "82101",
        "country": "SK",
        "municipalityCode": "528595",
        "regionCode": "SK010",
        "districtCode": None,
    }
    assert second["establishedOn"] == "2020-05-01"
    assert second["updatedAt"] == "2026-06-02"
    assert second["source"] == {"name": "unit-test", "recordId": "RPO-87654321"}


def test_invalid_ico_is_rejected(tmp_path: Path) -> None:
    input_file = tmp_path / "companies.json"
    input_file.write_text(
        json.dumps({"records": [{"ico": "1234", "name": "Broken, s.r.o."}]}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    result = run_import(input_path=input_file, output_path=tmp_path / "output", write=False)

    assert not result.ok
    assert any("8 digits" in error for error in result.errors)
    assert result.wrote_files == []


def test_missing_name_is_rejected(tmp_path: Path) -> None:
    input_file = tmp_path / "companies.json"
    input_file.write_text(
        json.dumps({"records": [{"ico": "12345678"}]}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    result = run_import(input_path=input_file, output_path=tmp_path / "output", write=False)

    assert not result.ok
    assert any("missing company name" in error for error in result.errors)
    assert result.wrote_files == []


def test_duplicate_icos_are_rejected(tmp_path: Path) -> None:
    input_file = tmp_path / "companies.json"
    input_file.write_text(
        json.dumps(
            {
                "records": [
                    {"ico": "12345678", "name": "Alpha, s.r.o.", "sidlo": {"postalCode": "82101"}, "updatedAt": "2026-06-03"},
                    {"ico": "12345678", "name": "Beta, s.r.o.", "sidlo": {"postalCode": "82101"}, "updatedAt": "2026-06-03"},
                ]
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_import(input_path=input_file, output_path=tmp_path / "output", write=False)

    assert not result.ok
    assert any("duplicate IČO" in error for error in result.errors)
