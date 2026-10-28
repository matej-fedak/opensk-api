from pydantic import Field

from schemas.common import PublicModel


class BusinessDayCheck(PublicModel):
    date: str
    weekday: int = Field(description="Monday=0 through Sunday=6.")
    isWeekend: bool
    isHoliday: bool
    holidayName: str | None
    isBusinessDay: bool
    supportedYears: list[int]


class BusinessDayAddition(PublicModel):
    date: str
    days: int
    result: str
    resultIsBusinessDay: bool = Field(description="Historical field is always true, including days=0; use check for the returned date if needed.")
    supportedYears: list[int]


class HolidayHit(PublicModel):
    date: str
    name: str


class BusinessDayInterval(PublicModel):
    from_: str = Field(alias="from")
    to: str
    totalDays: int
    weekendDays: int
    holidayDays: int
    holidays: list[HolidayHit]
    businessDays: int
    supportedYears: list[int]
