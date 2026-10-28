from pydantic import Field

from schemas.common import PublicModel


class Holiday(PublicModel):
    date: str
    name: str
    name_en: str
    isStateHoliday: bool = Field(description="State holiday under Act 241/1993 §1, whether working or non-working.")
    isDayOfRest: bool = Field(description="Holiday is a statutory day of rest on this date under applicable §2/§4b; independent of weekday/weekend.")
