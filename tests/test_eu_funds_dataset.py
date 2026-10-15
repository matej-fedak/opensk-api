"""Validate the actual checked-in public dataset without any raw source input."""

import json
from pathlib import Path

from schemas.common import EU_FUNDS_LAST_UPDATED
from schemas.eu_funds import Dataset
from scripts.itms21_production import manifest_digest
from scripts.validate_datasets import validate_eu_funds_projects_dataset
from services.eu_funds_policy import APPROVED_LEGAL_FORMS

ROOT = Path(__file__).resolve().parents[1]


def test_production_dataset_counts_policy_and_schema():
    path = ROOT / "data" / "eu_funds_projects.json"
    report = validate_eu_funds_projects_dataset(path)
    assert report.ok, report.errors
    dataset = Dataset.model_validate(json.loads(path.read_text(encoding="utf-8")))
    assert dataset.projects
    meta = dataset.metadata
    assert meta.snapshotDate == EU_FUNDS_LAST_UPDATED
    assert meta.sourceProjectCount == meta.includedProjectCount + meta.privacyExcludedProjectCount
    assert meta.includedProjectCount == len(dataset.projects)
    assert all(row.beneficiary.legalForm.code in APPROVED_LEGAL_FORMS for row in dataset.projects)
    assert not any("name" in row.model_dump() or "dates" in row.model_dump() for row in dataset.projects)
    assert all(isinstance(row.financials.contractedTotal, str) for row in dataset.projects)


def test_nonpersonal_public_acquisition_manifest_matches_dataset():
    manifest_path = ROOT / "docs" / "research" / "eu-funds-acquisition-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    dataset = json.loads((ROOT / "data" / "eu_funds_projects.json").read_text(encoding="utf-8"))
    assert manifest_digest(manifest) == manifest["manifestSha256"] == dataset["metadata"]["sourceManifestSha256"]
    assert sum(page["rows"] for page in manifest["pages"]) == dataset["metadata"]["sourceProjectCount"]
    assert len(manifest["pages"]) == dataset["metadata"]["pageCount"]
    assert "/projekt/id/" not in manifest_path.read_text(encoding="utf-8")
    assert all(set(page) == {"file", "url", "offset", "limit", "size", "rows", "bytes", "sha256", "retrievedAt"}
               for page in manifest["pages"])


def test_foreign_or_unreviewed_legal_forms_do_not_bypass_positive_gate():
    # CZ325 was present in the research seed, but not established as an
    # independent legal person in the full production review.
    assert "1009CZ325" not in APPROVED_LEGAL_FORMS
    assert "1009101" not in APPROVED_LEGAL_FORMS
    assert "1009995" not in APPROVED_LEGAL_FORMS
