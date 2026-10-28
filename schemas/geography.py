from schemas.common import PublicModel


class Region(PublicModel):
    code: str
    name: str
    nameEn: str
    country: str


class District(PublicModel):
    code: str
    name: str
    regionCode: str
    country: str


class Municipality(PublicModel):
    code: str
    name: str
    regionCode: str
    districtCode: str
    country: str


class Geography(PublicModel):
    # Missing references are omitted by the existing resolver, not emitted null.
    region: Region | None = None
    district: District | None = None
    municipality: Municipality | None = None
