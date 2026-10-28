from schemas.common import PublicModel


class CompanyAddress(PublicModel):
    street: str | None
    registrationNumber: str | None
    buildingNumber: str | None
    municipality: str | None
    postalCode: str | None
    country: str | None
    municipalityCode: str | None
    regionCode: str | None
    districtCode: str | None


class CompanySource(PublicModel):
    name: str
    recordId: str


class Company(PublicModel):
    ico: str
    name: str
    legalForm: str | None
    legalStatus: str
    sourceRegister: str | None
    address: CompanyAddress
    establishedOn: str | None
    terminatedOn: str | None
    updatedAt: str
    source: CompanySource
