from pydantic import Field

from schemas.common import PublicModel


class BusinessDayCheck(PublicModel):
    date: str
    weekday: int = Field(description="Monday=0 through Sunday=6.")
    isWeekend: bool
    isHoliday: bool = Field(description="Date exists in the statutory holiday calendar, including working holidays.")
    isDayOfRest: bool = Field(description="Holiday-related statutory day-of-rest status; may be false when isHoliday is true.")
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
    holidayDays: int = Field(description="Weekday days excluded because isDayOfRest=true; weekend holidays count only as weekendDays.")
    holidays: list[HolidayHit] = Field(description="Only non-weekend statutory days of rest relevant to business-day counting, not all holiday dates.")
    businessDays: int
    supportedYears: list[int]
