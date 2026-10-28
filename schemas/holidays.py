from schemas.common import PublicModel


class Holiday(PublicModel):
    date: str
    name: str
    name_en: str
