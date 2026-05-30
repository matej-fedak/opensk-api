from __future__ import annotations

import csv
import json
import socket
import urllib.request
from pathlib import Path

import pytest

from scripts.import_geography import run_import
from scripts.import_utils import (
    build_dataset_payload,
    collect_referential_integrity_errors,
    load_dataset_records,
    write_json,
)


REGIONS = [
    {"code": "SK010", "name": "Bratislavský kraj", "nameEn": "Bratislava Region", "country": "SK"},
    {"code": "SK021", "name": "Trnavský kraj", "nameEn": "Trnava Region", "country": "SK"},
    {"code": "SK022", "name": "Trenčiansky kraj", "nameEn": "Trenčín Region", "country": "SK"},
    {"code": "SK023", "name": "Nitriansky kraj", "nameEn": "Nitra Region", "country": "SK"},
    {"code": "SK031", "name": "Žilinský kraj", "nameEn": "Žilina Region", "country": "SK"},
    {"code": "SK032", "name": "Banskobystrický kraj", "nameEn": "Banská Bystrica Region", "country": "SK"},
    {"code": "SK041", "name": "Prešovský kraj", "nameEn": "Prešov Region", "country": "SK"},
    {"code": "SK042", "name": "Košický kraj", "nameEn": "Košice Region", "country": "SK"},
]

DISTRICTS = [
    {"code": "SK0101", "name": "Bratislava I", "regionCode": "SK010", "country": "SK"},
    {"code": "SK0211", "name": "Trnava", "regionCode": "SK021", "country": "SK"},
]

MUNICIPALITIES = [
    {"code": "528595", "name": "Bratislava - Staré Mesto", "districtCode": "SK0101", "regionCode": "SK010", "country": "SK"},
    {"code": "545321", "name": "Trnava", "districtCode": "SK0211", "regionCode": "SK021", "country": "SK"},
]

PSC_FIXTURE = {
    "81101": {
        "psc": "81101",
        "city": "Bratislava",
        "municipality": "Bratislava - Staré Mesto",
        "municipalityCode": "528595",
        "district": "Bratislava I",
        "districtCode": "SK0101",
        "region": "Bratislavský kraj",
        "regionCode": "SK010",
        "country": "Slovakia",
    }
}


def _write_csv(path: Path, fieldnames: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_bundle(source_dir: Path, *, as_json: bool = False, duplicate_region: bool = False) -> None:
    regions = [dict(record) for record in REGIONS]
    districts = [dict(record) for record in DISTRICTS]
    municipalities = [dict(record) for record in MUNICIPALITIES]

    if duplicate_region:
        regions[1]["code"] = regions[0]["code"]

    if as_json:
        write_json(source_dir / "regions.json", regions)
        write_json(source_dir / "districts.json", districts)
        write_json(source_dir / "municipalities.json", municipalities)
        return

    _write_csv(source_dir / "regions.csv", ("code", "name", "nameEn", "country"), regions)
    _write_csv(source_dir / "districts.csv", ("code", "name", "regionCode", "country"), districts)
    _write_csv(
        source_dir / "municipalities.csv",
        ("code", "name", "districtCode", "regionCode", "country"),
        municipalities,
    )


def _write_seed_psc(data_dir: Path) -> None:
    write_json(data_dir / "psc.json", PSC_FIXTURE)


def _expected_payload(dataset: str, records: list[dict[str, str]]) -> str:
    payload = build_dataset_payload(dataset, records, "unit-test", complete=(dataset == "regions"))
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def test_dry_run_does_not_write_output(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    output_dir = tmp_path / "output"
    _write_bundle(source_dir)
    _write_seed_psc(output_dir)

    result = run_import(
        dataset="all",
        source="unit-test",
        input_path=source_dir,
        output_path=output_dir,
        write=False,
        allow_incomplete=False,
    )

    assert result.dry_run is True
    assert result.wrote_files == []
    assert not (output_dir / "regions.json").exists()
    assert not (output_dir / "districts.json").exists()
    assert not (output_dir / "municipalities.json").exists()


def test_write_writes_normalized_json(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    output_dir = tmp_path / "output"
    _write_bundle(source_dir)
    _write_seed_psc(output_dir)

    result = run_import(
        dataset="all",
        source="unit-test",
        input_path=source_dir,
        output_path=output_dir,
        write=True,
        allow_incomplete=False,
    )

    assert result.ok
    assert result.wrote_files == [output_dir / "regions.json", output_dir / "districts.json", output_dir / "municipalities.json"]
    assert (output_dir / "regions.json").read_text(encoding="utf-8") == _expected_payload("regions", REGIONS)
    assert (output_dir / "districts.json").read_text(encoding="utf-8") == _expected_payload("districts", DISTRICTS)
    assert (output_dir / "municipalities.json").read_text(encoding="utf-8") == _expected_payload("municipalities", MUNICIPALITIES)


def test_invalid_source_data_fails_validation(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    output_dir = tmp_path / "output"
    source_dir.mkdir()
    _write_seed_psc(output_dir)
    _write_csv(
        source_dir / "regions.csv",
        ("code", "name", "nameEn"),
        [{"code": REGIONS[0]["code"], "name": REGIONS[0]["name"], "nameEn": REGIONS[0]["nameEn"]}],
    )

    with pytest.raises(ValueError, match="missing required columns"):
        run_import(
            dataset="regions",
            source="unit-test",
            input_path=source_dir / "regions.csv",
            output_path=output_dir,
            write=False,
            allow_incomplete=False,
        )


def test_duplicate_codes_fail_validation(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    output_dir = tmp_path / "output"
    _write_bundle(source_dir, duplicate_region=True)
    _write_seed_psc(output_dir)

    result = run_import(
        dataset="all",
        source="unit-test",
        input_path=source_dir,
        output_path=output_dir,
        write=False,
        allow_incomplete=False,
    )

    assert not result.validation_reports[0].ok
    assert any("duplicate region code" in issue.message for issue in result.validation_reports[0].errors)


def test_municipality_with_unknown_district_fails_referential_integrity(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    output_dir = tmp_path / "output"
    _write_bundle(source_dir)
    _write_seed_psc(output_dir)

    result = run_import(
        dataset="all",
        source="unit-test",
        input_path=source_dir,
        output_path=output_dir,
        write=True,
        allow_incomplete=False,
    )
    assert result.ok

    broken = json.loads((output_dir / "municipalities.json").read_text(encoding="utf-8"))
    broken["municipalities"][1]["districtCode"] = "SK9999"
    write_json(output_dir / "municipalities.json", broken)

    errors = collect_referential_integrity_errors(output_dir)

    assert any("unknown districtCode SK9999" in error for error in errors)


def test_output_is_stable_and_no_network_is_required(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    csv_source = tmp_path / "csv-source"
    json_source = tmp_path / "json-source"
    csv_output = tmp_path / "csv-output"
    json_output = tmp_path / "json-output"
    _write_bundle(csv_source)
    _write_bundle(json_source, as_json=True)
    _write_seed_psc(csv_output)
    _write_seed_psc(json_output)

    monkeypatch.setattr(socket, "create_connection", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("network not allowed")))
    monkeypatch.setattr(urllib.request, "urlopen", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("network not allowed")))

    assert load_dataset_records("regions", csv_source) == load_dataset_records("regions", json_source)

    csv_result = run_import(
        dataset="all",
        source="unit-test",
        input_path=csv_source,
        output_path=csv_output,
        write=True,
        allow_incomplete=False,
    )
    json_result = run_import(
        dataset="all",
        source="unit-test",
        input_path=json_source,
        output_path=json_output,
        write=True,
        allow_incomplete=False,
    )

    assert csv_result.ok
    assert json_result.ok
    assert (csv_output / "regions.json").read_text(encoding="utf-8") == (json_output / "regions.json").read_text(encoding="utf-8")
    assert (csv_output / "districts.json").read_text(encoding="utf-8") == (json_output / "districts.json").read_text(encoding="utf-8")
    assert (csv_output / "municipalities.json").read_text(encoding="utf-8") == (json_output / "municipalities.json").read_text(encoding="utf-8")
