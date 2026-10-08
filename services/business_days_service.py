"""Slovak business-day checks and arithmetic over the local holiday dataset.

Business day definition for this milestone: a day that is Monday-Friday and is
not a holiday present in the checked-in `data/holidays.json` dataset. This is
not a bank settlement calendar, a company-specific working calendar, or any
authority-specific schedule. Supported years are derived from the dataset keys
so new holiday years become supported without code changes.
"""

import json
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
HOLIDAYS_FILE = DATA_DIR / "holidays.json"

MAX_DAYS_DELTA = 366


class BusinessDayInvalidError(ValueError):
    pass


class BusinessDayUnsupportedYearError(ValueError):
    def __init__(self, year: int, supported: list[int]) -> None:
        self.year = year
        self.supported = supported
        super().__init__(f"year {year} is outside supported holiday coverage {supported}")


@lru_cache(maxsize=1)
def load_holidays_data() -> dict[str, list[dict[str, str]]]:
    with HOLIDAYS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def supported_years() -> list[int]:
    return sorted(int(year) for year in load_holidays_data())


@lru_cache(maxsize=1)
def holiday_dates() -> frozenset[date]:
    days: set[date] = set()
    for entries in load_holidays_data().values():
        for entry in entries:
            days.add(date.fromisoformat(entry["date"]))
    return frozenset(days)


@lru_cache(maxsize=1)
def holiday_names() -> dict[date, str]:
    names: dict[date, str] = {}
    for entries in load_holidays_data().values():
        for entry in entries:
            names[date.fromisoformat(entry["date"])] = entry["name"]
    return names


def parse_iso_date(value: str, field_name: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise BusinessDayInvalidError(f"{field_name} must be an ISO date (YYYY-MM-DD)") from exc


def require_supported(day: date) -> date:
    if day.year not in supported_years():
        raise BusinessDayUnsupportedYearError(day.year, supported_years())
    return day


def is_business_day(day: date) -> bool:
    require_supported(day)
    if day.weekday() >= 5:
        return False
    return day not in holiday_dates()


def add_business_days(day: date, days: int) -> date:
    require_supported(day)
    if days == 0:
        require_supported(day)
        return day

    step = 1 if days > 0 else -1
    remaining = abs(days)
    current = day
    while remaining > 0:
        current += timedelta(days=step)
        require_supported(current)
        if is_business_day(current):
            remaining -= 1
    return current


def business_days_between(start: date, end: date) -> dict[str, object]:
    require_supported(start)
    require_supported(end)

    if end < start:
        raise BusinessDayInvalidError("from must be on or before to")

    span_days = (end - start).days
    if span_days > MAX_DAYS_DELTA:
        raise BusinessDayInvalidError(f"the interval must be at most {MAX_DAYS_DELTA} days")

    business = 0
    weekends = 0
    holiday_hits: list[dict[str, str]] = []
    current = start
    names = holiday_names()
    while current <= end:
        if current.weekday() >= 5:
            weekends += 1
        elif current in holiday_dates():
            holiday_hits.append({"date": current.isoformat(), "name": names.get(current, "")})
        else:
            business += 1
        current += timedelta(days=1)

    return {
        "from": start.isoformat(),
        "to": end.isoformat(),
        "totalDays": span_days + 1,
        "weekendDays": weekends,
        "holidayDays": len(holiday_hits),
        "holidays": holiday_hits,
        "businessDays": business,
        "supportedYears": supported_years(),
    }
