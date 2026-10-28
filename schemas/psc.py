from pydantic import Field

from schemas.common import PublicModel
from schemas.geography import Geography


class PSCMatch(PublicModel):
    psc: str
    city: str
    deliveryPost: str
    municipality: str
    municipalityCode: str | None
    district: str | None
    districtCode: str | None
    region: str | None
    regionCode: str | None
    country: str
    validFrom: str | None
    validTo: str | None
    geography: Geography | None = Field(default=None, description="Only present with include=geography and a resolvable local reference.")


class PSCLookup(PSCMatch):
    matchCount: int = Field(description="Number of flat logical matches, equal to len(matches).")
    matches: list[PSCMatch]


class Coverage(PublicModel):
    count: int
    percentage: float


class GeographyCoverage(PublicModel):
    municipalityCode: Coverage
    regionCode: Coverage
    districtCode: Coverage


class PSCSource(PublicModel):
    name: str
    licenceStatus: str


class PSCStats(PublicModel):
    recordCount: int
    uniquePscCount: int
    multiMatchPscCount: int
    geographyCoverage: GeographyCoverage
    source: PSCSource
