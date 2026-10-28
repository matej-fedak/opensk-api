from schemas.common import PublicModel


class PhoneArea(PublicModel):
    code: str
    name: str
    municipalityCode: str | None
    municipalityName: str
    districtCode: str | None
    regionCode: str | None
    country: str


class PhoneAreaLookup(PublicModel):
    code: str
    items: list[PhoneArea]
    count: int
