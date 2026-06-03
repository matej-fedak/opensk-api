import json
import shutil
from pathlib import Path

import pytest

from scripts.check_referential_integrity import collect_errors
from scripts.import_utils import validate_datasets_before_write
from scripts.import_utils import load_dataset_records
from scripts.validate_datasets import (
    validate_all_datasets,
    validate_companies_dataset,
    validate_banks_dataset,
    validate_districts_dataset,
    validate_holidays_dataset,
    validate_municipalities_dataset,
    validate_psc_dataset,
    validate_regions_dataset,
)


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def _copy_dataset_dir(target_dir: Path) -> None:
    for source in DATA_DIR.glob("*.json"):
        shutil.copy2(source, target_dir / source.name)


def _copy_dataset_dir_without_companies(target_dir: Path) -> None:
    for source in DATA_DIR.glob("*.json"):
        if source.name == "companies.json":
            continue
        shutil.copy2(source, target_dir / source.name)


def _write_psc_dataset(target_dir: Path, payload: dict[str, object]) -> None:
    (target_dir / "psc.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_companies_dataset(target_dir: Path, payload: dict[str, object]) -> None:
    (target_dir / "companies.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_dataset_files_parse_as_valid_json() -> None:
    reports = validate_all_datasets()

    assert len(reports) == 7
    assert all(report.record_count > 0 for report in reports)
    assert all(report.ok for report in reports)


def test_validate_all_datasets_skips_missing_companies_dataset(tmp_path: Path) -> None:
    _copy_dataset_dir_without_companies(tmp_path)

    reports = validate_all_datasets(tmp_path)

    assert all(report.dataset != "companies" for report in reports)


def test_regions_complete_dataset_has_eight_regions() -> None:
    report = validate_regions_dataset()

    assert report.ok
    assert report.record_count == 8


def test_bank_codes_are_unique_and_valid() -> None:
    report = validate_banks_dataset()

    assert report.ok
    assert report.record_count > 0


def test_holidays_dataset_is_valid() -> None:
    report = validate_holidays_dataset()

    assert report.ok
    assert report.record_count > 0


def test_district_region_codes_reference_existing_regions() -> None:
    report = validate_districts_dataset()

    assert report.ok
    assert report.record_count == 9


def test_municipality_references_are_valid() -> None:
    report = validate_municipalities_dataset()

    assert report.ok
    assert report.record_count > 2000


def test_municipalities_were_expanded_from_eurostat_lau() -> None:
    regions = {region["code"] for region in load_dataset_records("regions", DATA_DIR / "regions.json")}
    districts = {district["code"]: district for district in load_dataset_records("districts", DATA_DIR / "districts.json")}
    municipalities = load_dataset_records("municipalities", DATA_DIR / "municipalities.json")

    municipality_codes = [municipality["code"] for municipality in municipalities]

    assert len(municipalities) > 2000
    assert {"503681", "507814", "528595"}.issubset(municipality_codes)
    assert len(municipality_codes) == len(set(municipality_codes))
    assert all(municipality["regionCode"] in regions for municipality in municipalities)
    assert all(municipality.get("districtCode") is None or municipality["districtCode"] in districts for municipality in municipalities)


def test_psc_records_have_unique_codes_and_valid_geography_references() -> None:
    report = validate_psc_dataset()

    assert report.ok
    assert report.record_count > 0


def test_companies_dataset_is_optional_but_validated_when_present(tmp_path: Path) -> None:
    _copy_dataset_dir(tmp_path)
    _write_companies_dataset(
        tmp_path,
        {
            "metadata": {"source": "unit-test", "lastUpdated": "2026-06-03"},
            "companies": [
                {
                    "ico": "12345678",
                    "name": "Example, s.r.o.",
                    "establishedOn": "2020-01-01",
                    "terminatedOn": None,
                    "updatedAt": "2026-06-03",
                    "address": {"postalCode": "82101"},
                    "source": {"name": "unit-test"},
                }
            ],
        },
    )

    report = validate_companies_dataset(tmp_path / "companies.json")
    all_reports = validate_all_datasets(tmp_path)

    assert report.ok
    assert report.record_count == 1
    assert any(item.dataset == "companies" for item in all_reports)


def test_companies_dataset_rejects_duplicate_icos_and_bad_date_order(tmp_path: Path) -> None:
    _write_companies_dataset(
        tmp_path,
        {
            "companies": [
                {
                    "ico": "12345678",
                    "name": "Alpha, s.r.o.",
                    "establishedOn": "2021-01-01",
                    "terminatedOn": "2020-12-31",
                    "updatedAt": "2026-06-03",
                    "address": {"postalCode": "82101"},
                    "source": {"name": "unit-test"},
                },
                {
                    "ico": "12345678",
                    "name": "Beta, s.r.o.",
                    "establishedOn": None,
                    "terminatedOn": None,
                    "updatedAt": None,
                    "address": {"postalCode": None},
                    "source": {"name": "unit-test"},
                },
            ]
        },
    )

    report = validate_companies_dataset(tmp_path / "companies.json")

    assert not report.ok
    assert any("duplicate IČO" in issue.message for issue in report.errors)
    assert any("terminatedOn must be on or after establishedOn" in issue.message for issue in report.errors)


def test_companies_dataset_rejects_forbidden_personal_fields(tmp_path: Path) -> None:
    _write_companies_dataset(
        tmp_path,
        {
            "companies": [
                {
                    "ico": "12345678",
                    "name": "Example, s.r.o.",
                    "establishedOn": "2020-01-01",
                    "terminatedOn": None,
                    "updatedAt": "2026-06-03",
                    "address": {"postalCode": "82101"},
                    "source": {"name": "unit-test"},
                    "owners": [{"name": "Hidden Person"}],
                    "residence": "Hidden Street 1",
                }
            ]
        },
    )

    report = validate_companies_dataset(tmp_path / "companies.json")

    assert not report.ok
    assert any("forbidden field 'owners'" in issue.message for issue in report.errors)
    assert any("forbidden field 'residence'" in issue.message for issue in report.errors)


def test_psc_dataset_accepts_expanded_model_and_multiple_matches(tmp_path: Path) -> None:
    _copy_dataset_dir(tmp_path)
    _write_psc_dataset(
        tmp_path,
        {
            "81101": {
                "psc": "81101",
                "city": "Bratislava",
                "municipality": "Bratislava - mestská časť Staré Mesto",
                "municipalityCode": "528595",
                "district": "Bratislava I",
                "districtCode": None,
                "region": "Bratislavský kraj",
                "regionCode": "SK010",
                "country": "Slovakia",
                "matchCount": 2,
                "matches": [
                    {
                        "psc": "81101",
                        "city": "Bratislava",
                        "municipality": "Bratislava - mestská časť Staré Mesto",
                        "municipalityCode": "528595",
                        "district": "Bratislava I",
                        "districtCode": None,
                        "region": "Bratislavský kraj",
                        "regionCode": "SK010",
                        "country": "Slovakia",
                        "deliveryPost": "Bratislava 1",
                        "validFrom": "2026-01-01",
                        "validTo": "2026-06-30",
                    },
                    {
                        "psc": "81101",
                        "city": "Bratislava",
                        "municipality": "Bratislava - mestská časť Staré Mesto",
                        "municipalityCode": "528595",
                        "district": "Bratislava I",
                        "districtCode": None,
                        "region": "Bratislavský kraj",
                        "regionCode": "SK010",
                        "country": "Slovakia",
                        "deliveryPost": "Bratislava 2",
                        "validFrom": "2026-07-01",
                        "validTo": "2026-12-31",
                    },
                ],
            }
        },
    )

    report = validate_psc_dataset(tmp_path / "psc.json")

    assert report.ok
    assert report.record_count == 1


def test_psc_dataset_rejects_exact_duplicates(tmp_path: Path) -> None:
    _copy_dataset_dir(tmp_path)
    _write_psc_dataset(
        tmp_path,
        {
            "81101": {
                "psc": "81101",
                "city": "Bratislava",
                "municipality": "Bratislava - mestská časť Staré Mesto",
                "municipalityCode": "528595",
                "district": "Bratislava I",
                "districtCode": None,
                "region": "Bratislavský kraj",
                "regionCode": "SK010",
                "country": "Slovakia",
                "matchCount": 2,
                "matches": [
                    {
                        "psc": "81101",
                        "city": "Bratislava",
                        "municipality": "Bratislava - mestská časť Staré Mesto",
                        "municipalityCode": "528595",
                        "district": "Bratislava I",
                        "districtCode": None,
                        "region": "Bratislavský kraj",
                        "regionCode": "SK010",
                        "country": "Slovakia",
                        "deliveryPost": "Bratislava 1",
                        "validFrom": "2026-01-01",
                        "validTo": "2026-06-30",
                    },
                    {
                        "psc": "81101",
                        "city": "Bratislava",
                        "municipality": "Bratislava - mestská časť Staré Mesto",
                        "municipalityCode": "528595",
                        "district": "Bratislava I",
                        "districtCode": None,
                        "region": "Bratislavský kraj",
                        "regionCode": "SK010",
                        "country": "Slovakia",
                        "deliveryPost": "Bratislava 1",
                        "validFrom": "2026-01-01",
                        "validTo": "2026-06-30",
                    },
                ],
            }
        },
    )

    report = validate_psc_dataset(tmp_path / "psc.json")

    assert not report.ok
    assert any("duplicate PSC record" in issue.message for issue in report.errors)


def test_psc_dataset_checks_valid_from_and_valid_to(tmp_path: Path) -> None:
    _copy_dataset_dir(tmp_path)
    _write_psc_dataset(
        tmp_path,
        {
            "81101": {
                "psc": "81101",
                "city": "Bratislava",
                "municipality": "Bratislava - mestská časť Staré Mesto",
                "municipalityCode": "528595",
                "district": "Bratislava I",
                "districtCode": None,
                "region": "Bratislavský kraj",
                "regionCode": "SK010",
                "country": "Slovakia",
                "matchCount": 1,
                "matches": [
                    {
                        "psc": "81101",
                        "city": "Bratislava",
                        "municipality": "Bratislava - mestská časť Staré Mesto",
                        "municipalityCode": "528595",
                        "district": "Bratislava I",
                        "districtCode": None,
                        "region": "Bratislavský kraj",
                        "regionCode": "SK010",
                        "country": "Slovakia",
                        "deliveryPost": "Bratislava 1",
                        "validFrom": "2026-06-30",
                        "validTo": "2026-01-01",
                    }
                ],
            }
        },
    )

    report = validate_psc_dataset(tmp_path / "psc.json")

    assert not report.ok
    assert any("validFrom must be on or before validTo" in issue.message for issue in report.errors)


def test_referential_integrity_script_reports_no_errors() -> None:
    assert collect_errors() == []


def test_dataset_preflight_refuses_bad_output(tmp_path: Path) -> None:
    _copy_dataset_dir(tmp_path)

    districts_path = tmp_path / "districts.json"
    payload = json.loads(districts_path.read_text(encoding="utf-8"))
    payload["districts"][0]["regionCode"] = "SK999"
    districts_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    assert collect_errors(tmp_path)

    with pytest.raises(ValueError, match="before write"):
        validate_datasets_before_write(tmp_path)
