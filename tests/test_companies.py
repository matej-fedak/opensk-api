from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import app
from scripts.validate_datasets import validate_companies_payload
from services import company_service


client = TestClient(app)


def _write_dataset(tmp_path: Path, payload: dict[str, object]) -> Path:
    data_file = tmp_path / "companies.json"
    data_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data_file


@pytest.fixture()
def company_dataset(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    data_file = _write_dataset(
        tmp_path,
        {
            "metadata": {"source": "local-test-source", "lastUpdated": "2026-06-03"},
            "companies": [
                {
                    "ico": "01234567",
                    "name": "Example, s.r.o.",
                    "legalForm": "s.r.o.",
                    "legalStatus": "active",
                    "sourceRegister": "Obchodný register",
                    "address": {
                        "street": "Example Street 1",
                        "registrationNumber": "1",
                        "buildingNumber": "2",
                        "municipality": "Bratislava",
                        "postalCode": "82101",
                        "country": "SK",
                        "municipalityCode": "528595",
                        "regionCode": "SK010",
                        "districtCode": None,
                    },
                    "establishedOn": "2020-05-01",
                    "terminatedOn": None,
                    "updatedAt": "2026-06-02",
                    "source": {"name": "local-test-source", "recordId": "RPO-01234567"},
                    "statutoryBodies": [{"name": "Hidden Person"}],
                    "stakeholders": [{"name": "Hidden Person"}],
                    "personalData": {"name": "Hidden Person"},
                }
            ],
        },
    )
    monkeypatch.setattr(company_service, "DATA_FILE", data_file)
    company_service.load_company_dataset.cache_clear()
    company_service.load_company_index.cache_clear()
    yield data_file
    company_service.load_company_dataset.cache_clear()
    company_service.load_company_index.cache_clear()


def test_company_lookup_returns_sanitized_enveloped_response(company_dataset: Path) -> None:
    response = client.get("/v1/companies/01234567")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["ico"] == "01234567"
    assert body["data"]["name"] == "Example, s.r.o."
    assert body["data"]["source"] == {"name": "local-test-source", "recordId": "RPO-01234567"}
    assert body["metadata"]["source"] == "OpenSK API local company dataset"
    assert body["metadata"]["lastUpdated"] == "2026-06-03"
    assert body["error"] is None
    assert "stakeholders" not in body["data"]
    assert "statutoryBodies" not in body["data"]
    assert "personalData" not in body["data"]


def test_company_service_normalize_ico_strips_spaces() -> None:
    assert company_service.normalize_ico("01 23 45 67") == "01234567"


def test_company_lookup_normalizes_spaces_in_ico(company_dataset: Path) -> None:
    response = client.get("/v1/companies/01%2023%2045%2067")

    assert response.status_code == 200
    assert response.json()["data"]["ico"] == "01234567"


def test_company_alias_returns_same_company(company_dataset: Path) -> None:
    primary_response = client.get("/v1/companies/01234567")
    alias_response = client.get("/v1/ico/01234567")

    assert primary_response.status_code == 200
    assert alias_response.status_code == 200
    assert primary_response.json()["data"] == alias_response.json()["data"]


def test_invalid_ico_returns_400(company_dataset: Path) -> None:
    response = client.get("/v1/companies/12A4567")

    assert response.status_code == 400
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "INVALID_FORMAT"
    assert body["error"]["message"] == "IČO must be 8 digits"


def test_unknown_valid_ico_returns_404(company_dataset: Path) -> None:
    response = client.get("/v1/companies/99999999")

    assert response.status_code == 404
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "NOT_FOUND"
    assert body["error"]["message"] == "No company data available for 99999999"


def test_missing_dataset_returns_503(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    data_file = tmp_path / "companies.json"
    monkeypatch.setattr(company_service, "DATA_FILE", data_file)
    company_service.load_company_dataset.cache_clear()
    company_service.load_company_index.cache_clear()

    response = client.get("/v1/companies/01234567")

    assert response.status_code == 503
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "DATASET_UNAVAILABLE"
    assert body["error"]["message"] == "Local company dataset is not available"


def test_company_dataset_validation_rejects_duplicate_ico(tmp_path: Path) -> None:
    report = validate_companies_payload(
        {
            "companies": [
                {"ico": "01 23 45 67", "name": "One, s.r.o.", "address": {"postalCode": "82101"}, "source": {"name": "local-test-source"}},
                {"ico": "01234567", "name": "Two, s.r.o.", "address": {"postalCode": "82101"}, "source": {"name": "local-test-source"}},
            ]
        },
        path=tmp_path / "companies.json",
    )

    assert not report.ok
    assert any("duplicate IČO" in issue.message for issue in report.errors)


def test_company_dataset_validation_rejects_missing_name(tmp_path: Path) -> None:
    report = validate_companies_payload(
        {"companies": [{"ico": "01234567", "address": {"postalCode": "82101"}, "source": {"name": "local-test-source"}}]},
        path=tmp_path / "companies.json",
    )

    assert not report.ok
    assert any("company name must be a non-empty string" in issue.message for issue in report.errors)
