"""Typed public models for the curated source catalogue.

These models define the consumer-facing shape of `GET /v1/sources`. They are
intentionally separate from the internal registry fields in
`data/sources.json`; see `docs/source-catalogue.md` for the public/internal
boundary.
"""

from typing import Literal

from pydantic import BaseModel, Field


PublicSourceStatus = Literal["production", "seed", "historical", "research", "blocked"]
PublicSourceCoverage = Literal["complete", "partial", "seed"]
PublicLicenceStatus = Literal["verified", "identified", "pending", "blocked"]


class SourceIdentity(BaseModel):
    name: str
    url: str


class SourceLicence(BaseModel):
    status: PublicLicenceStatus
    name: str | None = None
    termsUrl: str | None = None


class PublicSourceEntry(BaseModel):
    id: str
    name: str
    status: PublicSourceStatus
    coverage: PublicSourceCoverage | None = None
    source: SourceIdentity
    licence: SourceLicence
    attribution: str | None = None
    lastUpdated: str | None = None
    lastChecked: str | None = None
    updateCadence: str | None = None
    limitations: list[str] = Field(default_factory=list)


class ResponseMetadata(BaseModel):
    source: str
    lastUpdated: str | None = None
    version: str


class SourceListResponse(BaseModel):
    data: list[PublicSourceEntry]
    metadata: ResponseMetadata
    error: None = None


class SourceDetailResponse(BaseModel):
    data: PublicSourceEntry
    metadata: ResponseMetadata
    error: None = None
