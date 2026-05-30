from scripts.check_referential_integrity import collect_errors
from scripts.validate_datasets import (
    validate_all_datasets,
    validate_banks_dataset,
    validate_districts_dataset,
    validate_holidays_dataset,
    validate_municipalities_dataset,
    validate_psc_dataset,
    validate_regions_dataset,
)


def test_dataset_files_parse_as_valid_json() -> None:
    reports = validate_all_datasets()

    assert len(reports) == 6
    assert all(report.record_count > 0 for report in reports)
    assert all(report.ok for report in reports)


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
    assert report.record_count > 0


def test_municipality_references_are_valid() -> None:
    report = validate_municipalities_dataset()

    assert report.ok
    assert report.record_count > 0


def test_psc_records_have_unique_codes_and_valid_geography_references() -> None:
    report = validate_psc_dataset()

    assert report.ok
    assert report.record_count > 0


def test_referential_integrity_script_reports_no_errors() -> None:
    assert collect_errors() == []
