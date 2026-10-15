"""NBS bank provenance and additive metadata on existing v1 responses."""

import re
from datetime import date, datetime
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

NBS_SOURCE = "Národná banka Slovenska — Prevodník identifikačných kódov pre tuzemský platobný styk pre Slovenskú republiku"
NBS_SOURCE_URL = "https://nbs.sk/platby/vseobecne-informacie/ciselniky-a-registre/prevodnik-sk/"
NBS_TERMS_URL = "https://nbs.sk/disclaimer-sk/"
NBS_LICENSE = "NBS Terms of Use + institutional clarification received 2026-10-14; attribution required. MIT applies to OpenSK code, not NBS data."
NBS_TRANSFORMATION = (
    "NBS CSV converted to OpenSK JSON with field renaming, whitespace normalization, "
    "four-digit code padding and BIC normalization; not the original NBS file. "
    "activePartyMarker and activeParty are OpenSK-derived from Payment system SIPS "
    "(CSV: Systém SIPS), not a direct copy of Akt. úč. or a guarantee of bank operating status. "
    "country is an OpenSK-derived domestic scope label; alphabeticCode is a null schema "
    "placeholder when the source supplies no corresponding field. Derived fields are not NBS data."
)


def nbs_attribution(version: str, effective: str) -> str:
    return (
        "Zdroj: Národná banka Slovenska, Prevodník identifikačných kódov pre tuzemský "
        f"platobný styk pre Slovenskú republiku, verzia {version}, platnosť od {effective}, "
        f"{NBS_SOURCE_URL}. Údaje previedol do formátu JSON projekt OpenSK; "
        "odvodené polia nie sú údajmi NBS."
    )


def official_nbs_url(value: str) -> str:
    parts = urlsplit(value)
    if parts.scheme != "https" or parts.netloc not in {"nbs.sk", "www.nbs.sk"} or parts.fragment:
        raise ValueError("source file URL must use the official NBS HTTPS host")
    return value


class BankDatasetMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    source: Literal[NBS_SOURCE]
    sourceUrl: Literal[NBS_SOURCE_URL]
    sourceFileUrl: str
    termsUrl: Literal[NBS_TERMS_URL]
    sourceVersion: str = Field(pattern=r"^[0-9]+$", max_length=20)
    sourceEffectiveDate: str
    downloadedAt: str
    sourceBytes: int = Field(gt=0)
    sourceSha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    license: Literal[NBS_LICENSE]
    attribution: str
    transformation: Literal[NBS_TRANSFORMATION]
    lastUpdated: str
    complete: Literal[True]

    _file_url = field_validator("sourceFileUrl")(official_nbs_url)

    @field_validator("sourceEffectiveDate", "lastUpdated")
    @classmethod
    def iso_date(cls, value):
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
            raise ValueError("expected ISO date YYYY-MM-DD")
        date.fromisoformat(value)
        return value

    @field_validator("downloadedAt")
    @classmethod
    def download_instant(cls, value):
        if "T" not in value or datetime.fromisoformat(value.replace("Z", "+00:00")).utcoffset() is None:
            raise ValueError("downloadedAt must be an ISO datetime with timezone")
        return value

    @field_validator("complete", mode="before")
    @classmethod
    def complete_boolean(cls, value):
        if value is not True:
            raise ValueError("complete must be true")
        return value

    @model_validator(mode="after")
    def consistent(self):
        if self.lastUpdated != self.sourceEffectiveDate:
            raise ValueError("lastUpdated must equal sourceEffectiveDate, not download date")
        if self.attribution != nbs_attribution(self.sourceVersion, self.sourceEffectiveDate):
            raise ValueError("attribution must describe the actual served version/effective date")
        return self


class BankRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    code: str
    name: str
    bic: str | None
    swift: str | None
    alphabeticCode: str | None
    activeParty: bool
    activePartyMarker: Literal["C", "K", "Ø"]
    country: Literal["SK"]


class BankResponseMetadata(BaseModel):
    source: str
    lastUpdated: str
    version: Literal["v1"]
    sourceVersion: str
    sourceEffectiveDate: str
    sourceDownloadedAt: str
    sourceUrl: str
    sourceFileUrl: str
    sourceSha256: str
    sourceBytes: int
    termsUrl: str
    attribution: str
    transformation: str


class BanksResponse(BaseModel):
    data: list[BankRecord]
    metadata: BankResponseMetadata
    error: None = None


class BankResponse(BaseModel):
    data: BankRecord
    metadata: BankResponseMetadata
    error: None = None


class IbanValidationData(BaseModel):
    inputIban: str
    normalizedIban: str
    countryCode: str | None
    supportedCountry: bool
    checksumValid: bool
    bankCode: str | None
    bankName: str | None
    valid: bool


class IbanValidationResponse(BaseModel):
    data: IbanValidationData
    metadata: BankResponseMetadata
    error: None = None
