from schemas.common import PublicModel


class VehicleRegistrationCode(PublicModel):
    code: str
    districtName: str
    districtCode: str | None
    regionCode: str | None
    validFrom: str | None
    validTo: str | None
    status: str
    notes: str
