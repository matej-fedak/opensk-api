import csv
import json
from pathlib import Path

from scripts.import_phone_areas import run_import


def _write_phone_area_csv(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("code", "name", "municipalityName"))
        writer.writeheader()
        writer.writerow({"code": "033", "name": "Trnava", "municipalityName": "Trnava"})
        writer.writerow({"code": "099", "name": "Unknown", "municipalityName": "Unknown municipality"})


def test_phone_area_import_dry_run_does_not_write(tmp_path: Path) -> None:
    source = tmp_path / "phone_areas.csv"
    output = tmp_path / "phone_areas.json"
    _write_phone_area_csv(source)

    result = run_import(input_path=source, output_path=output, last_updated="2026-09-12", write=False)

    assert result.ok
    assert result.dry_run is True
    assert result.total_records == 2
    assert result.linked_records == 1
    assert result.unlinked_records == 1
    assert result.warnings == ["row 2: municipality name 'Unknown municipality' not found in local municipalities"]
    assert not output.exists()


def test_phone_area_import_write_outputs_normalized_payload(tmp_path: Path) -> None:
    source = tmp_path / "phone_areas.csv"
    output = tmp_path / "phone_areas.json"
    _write_phone_area_csv(source)

    result = run_import(input_path=source, output_path=output, source="unit-test", last_updated="2026-09-12", write=True)

    assert result.ok
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["metadata"] == {
        "source": "unit-test",
        "license": "Source/licence verification pending.",
        "lastUpdated": "2026-09-12",
        "complete": True,
    }
    assert payload["phoneAreas"][0] == {
        "code": "033",
        "name": "Trnava",
        "municipalityCode": "506745",
        "municipalityName": "Trnava",
        "districtCode": "SK0217",
        "regionCode": "SK021",
        "country": "SK",
    }
    assert payload["phoneAreas"][1]["municipalityCode"] is None
    assert payload["phoneAreas"][1]["districtCode"] is None
    assert payload["phoneAreas"][1]["regionCode"] is None


def test_phone_area_import_duplicate_records_are_skipped(tmp_path: Path) -> None:
    source = tmp_path / "phone_areas.csv"
    source.parent.mkdir(parents=True, exist_ok=True)
    with source.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("code", "name", "municipalityName"))
        writer.writeheader()
        writer.writerow({"code": "033", "name": "Trnava", "municipalityName": "Trnava"})
        writer.writerow({"code": "033", "name": "Trnava", "municipalityName": "Trnava"})

    result = run_import(input_path=source, output_path=tmp_path / "phone_areas.json", last_updated="2026-09-12", write=False)

    assert result.ok
    assert result.duplicate_records == 1
    assert any("skipped duplicate phone area record" in warning for warning in result.warnings)


def test_phone_area_import_xls_requires_manual_csv_conversion(tmp_path: Path) -> None:
    source = tmp_path / "phone_areas.xls"
    source.write_bytes(b"legacy xls placeholder")

    try:
        run_import(input_path=source, output_path=tmp_path / "phone_areas.json", write=False)
    except ValueError as exc:
        assert "convert the workbook's List1 sheet to CSV first" in str(exc)
    else:
        raise AssertionError("expected legacy .xls input to require manual CSV conversion")
