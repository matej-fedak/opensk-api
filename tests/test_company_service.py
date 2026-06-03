from __future__ import annotations

import json
from pathlib import Path

import pytest

from services.company_service import (
    CompanyDatasetError,
    CompanyInvalidFormatError,
    CompanyNotFoundError,
    get_company_by_ico,
    load_companies,
    normalize_ico,
    validate_ico,
)


def _write_companies(path: Path, companies: list[dict[str, object]]) -> None:
    payload = {"metadata": {"source": "unit-test", "lastUpdated": "2026-06-03"}, "companies": companies}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_normalize_ico_strips_whitespace() -> None:
    assert normalize_ico(" 01 23\t45\n67 ") == "01234567"


def test_validate_ico_accepts_exactly_eight_digits() -> None:
    assert validate_ico(" 0123 4567 ") is True


@pytest.mark.parametrize("value", ["1234", "1234567A", "1234-5678"])
def test_validate_ico_rejects_non_digits(value: str) -> None:
    assert validate_ico(value) is False


def test_load_companies_uses_configurable_path(tmp_path: Path) -> None:
    path = tmp_path / "companies.json"
    _write_companies(
        path,
        [
            {"ico": "87654321", "name": "Beta, a.s."},
            {"ico": "01234567", "name": "Example, s.r.o."},
        ],
    )

    companies = load_companies(data_file=path)

    assert [company["ico"] for company in companies] == ["87654321", "01234567"]
    assert companies[0]["name"] == "Beta, a.s."


def test_load_companies_returns_empty_list_when_file_is_missing(tmp_path: Path) -> None:
    assert load_companies(data_file=tmp_path / "companies.json") == []


def test_duplicate_ico_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "companies.json"
    _write_companies(
        path,
        [
            {"ico": "01234567", "name": "Alpha"},
            {"ico": "0123 4567", "name": "Duplicate"},
        ],
    )

    with pytest.raises(CompanyDatasetError):
        load_companies(data_file=path)


def test_get_company_by_ico_returns_matching_company(tmp_path: Path) -> None:
    path = tmp_path / "companies.json"
    _write_companies(path, [{"ico": "01234567", "name": "Example, s.r.o."}])

    company = get_company_by_ico(" 0123 4567 ", data_file=path)

    assert company["ico"] == "01234567"
    assert company["name"] == "Example, s.r.o."


def test_get_company_by_ico_raises_not_found_for_unknown_valid_ico(tmp_path: Path) -> None:
    path = tmp_path / "companies.json"
    _write_companies(path, [{"ico": "01234567", "name": "Example, s.r.o."}])

    with pytest.raises(CompanyNotFoundError) as exc:
        get_company_by_ico("87654321", data_file=path)

    assert exc.value.args[0] == "87654321"
