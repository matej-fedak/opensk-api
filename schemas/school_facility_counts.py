from schemas.common import PublicModel


class SchoolFacilityCount(PublicModel):
    schoolKindShort: str
    schoolTypeShort: str
    kindLevel1: str
    kindLevel2: str
    regionName: str
    regionCode: str | None
    districtName: str
    districtCode: str | None
    organizationalUnitCount: int
    founderOwnershipType: str
    founderType: str
    country: str


class SchoolFacilityStats(PublicModel):
    recordCount: int
    totalOrganizationalUnitCount: int
    regionLinkedCount: int
    districtLinkedCount: int
    totalsByRegion: dict[str, int]
    totalsByDistrict: dict[str, int]
    totalsBySchoolKind: dict[str, int]
    totalsBySchoolType: dict[str, int]
    totalsByFounderType: dict[str, int]
