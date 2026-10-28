"""Exact, title-free production schema for the ITMS21+ project subset."""

import re
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from services.eu_funds_policy import (
    APPROVED_LEGAL_FORMS, APPROVED_LEGAL_FORM_LABELS, COLLECTION_URL, LICENCE_NOTICE, NUTS_PATTERN,
    PRIVACY_POLICY, PROJECT_CODE_PATTERN, REVIEWED_NUTS_LABELS, SOURCE_NOTICE, TERMS_URL,
)


class ExactModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class LegalForm(ExactModel):
    code: str
    nameSk: str = Field(min_length=1, max_length=1000)

    @field_validator("code")
    @classmethod
    def approved(cls, value):
        if value not in APPROVED_LEGAL_FORMS:
            raise ValueError("beneficiary legal form is not positively approved")
        return value

    @model_validator(mode="after")
    def source_label(self):
        if APPROVED_LEGAL_FORM_LABELS[self.code] != self.nameSk:
            raise ValueError("legal-form source label changed; review required")
        return self


class Beneficiary(ExactModel):
    name: str = Field(min_length=1, max_length=1500)
    ico: str | None = Field(default=None, pattern=r"^[0-9]{8}$")
    legalForm: LegalForm


class Programme(ExactModel):
    code: str = Field(pattern=r"^[0-9]{6}$")
    nameSk: str = Field(min_length=1, max_length=1500)
    shortName: str | None = Field(default=None, max_length=128)
    cci: str | None = Field(default=None, max_length=128)


class Call(ExactModel):
    code: str = Field(min_length=1, max_length=256)
    nameSk: str = Field(min_length=1, max_length=1500)

    @field_validator("code")
    @classmethod
    def printable_code(cls, value):
        if value != value.strip() or not value.isprintable() or any(c in value for c in "<>"):
            raise ValueError("call code must be a printable source identifier")
        return value


class ProjectStatus(ExactModel):
    label: str | None = Field(default=None, max_length=1000)
    inImplementation: bool
    completed: bool


class Location(ExactModel):
    nuts: str = Field(pattern=f"^{NUTS_PATTERN}$")
    nameSk: str = Field(min_length=1, max_length=1000)

    @model_validator(mode="after")
    def reviewed(self):
        if REVIEWED_NUTS_LABELS.get(self.nuts) != self.nameSk:
            raise ValueError("unreviewed NUTS code/label")
        return self


class Financials(ExactModel):
    contractedTotal: str = Field(
        pattern=r"^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$", max_length=128,
        description="Exact nonnegative total contracted amount (celkovaZazmluvnenaSuma), decimal string; currency not independently established by the integration manual. Not paid/provided funds.",
    )

    @field_validator("contractedTotal")
    @classmethod
    def finite(cls, value):
        if not Decimal(value).is_finite():
            raise ValueError("amount must be finite")
        return value


def valid_instant(value: str) -> str:
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{3})?Z", value):
        raise ValueError("expected UTC ISO-8601 instant")
    datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value


class Project(ExactModel):
    projectCode: str = Field(pattern=f"^{PROJECT_CODE_PATTERN}$")
    sourceId: int = Field(gt=0)
    status: ProjectStatus
    programme: Programme
    call: Call
    beneficiary: Beneficiary
    implementationRegions: list[Location]
    financials: Financials
    sourceUpdatedAt: str
    sourceUrl: str

    _instant = field_validator("sourceUpdatedAt")(valid_instant)

    @model_validator(mode="after")
    def source_identity(self):
        if self.sourceUrl != f"{COLLECTION_URL}/id/{self.sourceId}":
            raise ValueError("source URL must identify this project on the official host")
        codes = [item.nuts for item in self.implementationRegions]
        if codes != sorted(set(codes)):
            raise ValueError("locations must have sorted unique NUTS codes")
        return self


class DatasetMetadata(ExactModel):
    source: Literal[SOURCE_NOTICE]
    sourceUrl: Literal[COLLECTION_URL]
    termsUrl: Literal[TERMS_URL]
    licence: Literal[LICENCE_NOTICE]
    attribution: str
    snapshotDate: str
    retrievedAt: str
    sourceProjectCount: int = Field(gt=0)
    includedProjectCount: int = Field(ge=0)
    privacyExcludedProjectCount: int = Field(ge=0)
    excludedNaturalPersonProjects: int = Field(ge=0)
    excludedUnreviewedBeneficiaryProjects: int = Field(ge=0)
    privacyPolicy: Literal[PRIVACY_POLICY]
    completeAcquisition: Literal[True]
    pageCount: int = Field(gt=0)
    sourceManifestSha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    importerProfile: Literal["itms21-project-references-v1"]

    _retrieved = field_validator("retrievedAt")(valid_instant)

    @field_validator("completeAcquisition", mode="before")
    @classmethod
    def explicitly_complete(cls, value):
        if value is not True:
            raise ValueError("completeAcquisition must be true")
        return value

    @model_validator(mode="after")
    def consistent(self):
        if self.snapshotDate != self.retrievedAt[:10]:
            raise ValueError("snapshot date must match acquisition completion")
        if self.sourceProjectCount != self.includedProjectCount + self.privacyExcludedProjectCount:
            raise ValueError("source/inclusion/exclusion counts disagree")
        if self.privacyExcludedProjectCount != self.excludedNaturalPersonProjects + self.excludedUnreviewedBeneficiaryProjects:
            raise ValueError("privacy exclusion counts disagree")
        return self


class Dataset(ExactModel):
    metadata: DatasetMetadata
    projects: list[Project] = Field(min_length=1)

    @model_validator(mode="after")
    def collection(self):
        if len(self.projects) != self.metadata.includedProjectCount:
            raise ValueError("included count differs from project array")
        codes = [p.projectCode for p in self.projects]
        if codes != sorted(set(codes)):
            raise ValueError("project codes must be sorted and unique")
        if len({p.sourceId for p in self.projects}) != len(self.projects):
            raise ValueError("source IDs must be unique")
        return self


class ResponseMetadata(ExactModel):
    source: str
    lastUpdated: str
    version: Literal["v1"] = "v1"


class ListData(ExactModel):
    items: list[Project]
    count: int
    total: int
    limit: int
    offset: int


class ListResponse(ExactModel):
    model_config = ConfigDict(extra="forbid", strict=True, json_schema_serialization_defaults_required=True)
    data: ListData
    metadata: ResponseMetadata
    error: None = None


class DetailResponse(ExactModel):
    model_config = ConfigDict(extra="forbid", strict=True, json_schema_serialization_defaults_required=True)
    data: Project
    metadata: ResponseMetadata
    error: None = None
