from schemas.common import Page, PublicModel


class PlaceOfPerformance(PublicModel):
    city: str | None
    postalCode: str | None
    country: str | None


class ProcurementNotice(PublicModel):
    id: str
    title: str
    noticeType: str
    publicationDate: str
    dispatchDate: str | None
    buyerNames: list[str]
    buyerCountry: str
    placeOfPerformance: PlaceOfPerformance
    tenderDeadline: str | None
    regionCode: str | None
    districtCode: str | None
    municipalityCode: str | None
    sourceUrl: str


class ProcurementSearch(Page[ProcurementNotice]):
    query: str


class ProcurementStats(PublicModel):
    recordCount: int
    coverage: str
    coverageDecision: str
    acquisitionDecision: str
    totalNoticesAtSource: int
    noticeTypes: dict[str, int]
    publicationYears: dict[str, int]
    deadlineCount: int
    regionLinkedCount: int
    districtLinkedCount: int
    municipalityLinkedCount: int
