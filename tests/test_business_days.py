"""Slovak business-day utility tests.

Business day = Monday-Friday minus statutory Slovak days of rest. Statutory
holiday dates that are legally working days (Act 241/1993 §2(3), §4b) stay in
the calendar with isDayOfRest=false and remain business days. Supported years
are derived from the dataset (2024-2030); dates outside coverage are rejected
with UNSUPPORTED_YEAR. See docs/research/holiday-calendar-correctness.md.
"""

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)

SUPPORTED_YEARS = [2024, 2025, 2026, 2027, 2028, 2029, 2030]

# Weekday statutory holidays that are legally working days (pre-change bugs).
WORKING_HOLIDAYS = [
    "2025-09-01", "2025-10-28", "2025-11-17",
    "2026-05-08", "2026-09-01", "2026-09-15", "2026-10-28", "2026-11-17",
]


def _data(response) -> dict[str, object]:  # type: ignore[no-untyped-def]
    assert response.json()["error"] is None
    assert response.json()["metadata"]["version"] == "v1"
    assert response.json()["metadata"]["lastUpdated"] == "2026-10-28"
    return response.json()["data"]


def _check(day: str) -> dict[str, object]:
    return _data(client.get(f"/v1/business-days/check?date={day}"))


def test_check_weekday_is_business_day() -> None:
    data = _check("2026-10-08")
    assert data["isBusinessDay"] is True
    assert data["isWeekend"] is False
    assert data["isHoliday"] is False
    assert data["isDayOfRest"] is False
    assert data["holidayName"] is None
    assert data["supportedYears"] == SUPPORTED_YEARS


def test_check_saturday_and_sunday_are_not_business_days() -> None:
    for day in ("2026-10-10", "2026-10-11"):
        data = _check(day)
        assert data["isWeekend"] is True
        assert data["isBusinessDay"] is False


def test_check_known_weekday_day_of_rest_is_not_business_day() -> None:
    data = _check("2026-01-01")
    assert data["isHoliday"] is True
    assert data["isDayOfRest"] is True
    assert data["holidayName"] is not None
    assert data["isBusinessDay"] is False

    good_friday = _check("2026-04-03")
    assert good_friday["isHoliday"] is True
    assert good_friday["isDayOfRest"] is True
    assert good_friday["isBusinessDay"] is False


def test_working_statutory_holidays_are_business_days() -> None:
    """Regression: holiday membership previously made these weekdays non-business."""
    for day in WORKING_HOLIDAYS:
        data = _check(day)
        assert data["isWeekend"] is False, day
        assert data["isHoliday"] is True, day
        assert data["isDayOfRest"] is False, day
        assert data["holidayName"] is not None, day
        assert data["isBusinessDay"] is True, day


def test_2024_working_holidays_on_weekend_keep_weekend_precedence() -> None:
    # 2024-09-01 was a Sunday: isDayOfRest=false, but the weekend still wins.
    sept = _check("2024-09-01")
    assert (sept["isWeekend"], sept["isHoliday"], sept["isDayOfRest"], sept["isBusinessDay"]) == (True, True, False, False)
    # 2024-11-17 was a Sunday and still a day of rest before the 2025-11-01 amendment.
    nov = _check("2024-11-17")
    assert (nov["isWeekend"], nov["isHoliday"], nov["isDayOfRest"], nov["isBusinessDay"]) == (True, True, True, False)


def test_2027_restores_may_8_and_september_15_day_of_rest() -> None:
    # 2027-05-08 is a Saturday: day of rest again, non-business via both rules.
    may = _check("2027-05-08")
    assert (may["isWeekend"], may["isHoliday"], may["isDayOfRest"], may["isBusinessDay"]) == (True, True, True, False)
    # 2027-09-15 is a Wednesday: non-business because day of rest returned.
    sept = _check("2027-09-15")
    assert (sept["isWeekend"], sept["isHoliday"], sept["isDayOfRest"], sept["isBusinessDay"]) == (False, True, True, False)


def test_supported_year_boundaries() -> None:
    first = _check("2024-01-02")
    assert first["isBusinessDay"] is True
    last_holiday = _check("2030-04-22")  # Easter Monday 2030, independently verified
    assert (last_holiday["isHoliday"], last_holiday["isDayOfRest"], last_holiday["isBusinessDay"]) == (True, True, False)


def test_add_skips_weekend() -> None:
    data = _data(client.get("/v1/business-days/add?date=2026-10-08&days=5"))
    assert data["result"] == "2026-10-15"
    assert data["resultIsBusinessDay"] is True


def test_add_traverses_working_holidays() -> None:
    """Regression: add must skip weekends/days of rest, not working holidays."""
    for start, result in (
        ("2026-05-07", "2026-05-08"),
        ("2026-09-14", "2026-09-15"),
        ("2026-08-31", "2026-09-01"),
        ("2026-10-27", "2026-10-28"),
        ("2026-11-16", "2026-11-17"),
        ("2025-10-27", "2025-10-28"),
        ("2025-11-14", "2025-11-17"),
    ):
        assert _data(client.get(f"/v1/business-days/add?date={start}&days=1"))["result"] == result, start


def test_add_skips_days_of_rest_and_weekends_across_christmas() -> None:
    # 24.-26.12.2026 are days of rest, 27.12. is Sunday.
    data = _data(client.get("/v1/business-days/add?date=2026-12-23&days=1"))
    assert data["result"] == "2026-12-28"


def test_add_negative_days_counts_working_holidays() -> None:
    data = _data(client.get("/v1/business-days/add?date=2026-10-12&days=-1"))
    assert data["result"] == "2026-10-09"

    # 2026-05-08 is now traversable, shifting the pre-fix result by one day.
    backwards = _data(client.get("/v1/business-days/add?date=2026-06-15&days=-30"))
    assert backwards["result"] == "2026-05-04"


def test_add_zero_days_returns_same_date() -> None:
    data = _data(client.get("/v1/business-days/add?date=2026-10-08&days=0"))
    assert data["result"] == "2026-10-08"


def test_leap_year_february_29() -> None:
    data = _data(client.get("/v1/business-days/add?date=2024-02-28&days=1"))
    assert data["result"] == "2024-02-29"
    assert _check("2024-02-29")["isBusinessDay"] is True


def test_add_across_year_boundary_within_coverage() -> None:
    # 2027-01-01 is a Friday day of rest, so +1 from 2026-12-31 lands 2027-01-04.
    data = _data(client.get("/v1/business-days/add?date=2026-12-31&days=1"))
    assert data["result"] == "2027-01-04"


def test_unsupported_years_are_rejected_strictly() -> None:
    for url in (
        "/v1/business-days/check?date=2031-01-04",
        "/v1/business-days/check?date=2023-01-02",
        "/v1/business-days/add?date=2030-12-30&days=5",
        "/v1/business-days/add?date=2030-12-31&days=1",
        "/v1/business-days/between?from=2030-12-01&to=2031-01-10",
        "/v1/business-days/between?from=2023-12-01&to=2024-01-10",
    ):
        response = client.get(url)
        assert response.status_code == 400, url
        assert response.json()["error"]["code"] == "UNSUPPORTED_YEAR"


def test_between_counts_business_weekend_and_day_of_rest_days() -> None:
    # 2026-12-24/25 are weekday days of rest; 2026-12-26 is a day of rest on a
    # Saturday and is classified as a weekend day (weekend precedence).
    data = _data(client.get("/v1/business-days/between?from=2026-12-22&to=2026-12-28"))
    assert data["totalDays"] == 7
    assert data["weekendDays"] == 2
    assert data["holidayDays"] == 2
    assert data["businessDays"] == 3  # 22, 23 and 28
    assert {hit["date"] for hit in data["holidays"]} == {"2026-12-24", "2026-12-25"}


def test_between_working_holidays_are_business_not_holiday_days() -> None:
    """2026-09-01 (Tuesday) is a working state holiday: eligible, not holidayDays."""
    data = _data(client.get("/v1/business-days/between?from=2026-08-31&to=2026-09-02"))
    assert data["totalDays"] == 3
    assert data["weekendDays"] == 0
    assert data["holidayDays"] == 0
    assert data["businessDays"] == 3
    assert data["holidays"] == []


def test_between_2027_easter_window_counts_restored_days_of_rest() -> None:
    data = _data(client.get("/v1/business-days/between?from=2027-03-25&to=2027-03-29"))
    assert data["totalDays"] == 5
    assert data["weekendDays"] == 2
    assert data["holidayDays"] == 2
    assert data["businessDays"] == 1
    assert {hit["date"] for hit in data["holidays"]} == {"2027-03-26", "2027-03-29"}


def test_between_plain_working_week() -> None:
    data = _data(client.get("/v1/business-days/between?from=2026-10-05&to=2026-10-11"))
    assert data["totalDays"] == 7
    assert data["weekendDays"] == 2
    assert data["holidayDays"] == 0
    assert data["businessDays"] == 5


def test_between_rejects_reversed_interval() -> None:
    response = client.get("/v1/business-days/between?from=2026-10-11&to=2026-10-05")
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_FORMAT"


def test_invalid_dates_and_bounds_are_rejected() -> None:
    assert client.get("/v1/business-days/check?date=08.10.2026").json()["error"]["code"] == "INVALID_FORMAT"
    assert client.get("/v1/business-days/check").json()["error"]["code"] == "INVALID_FORMAT"
    assert client.get("/v1/business-days/add?date=2026-10-08").json()["error"]["code"] == "INVALID_FORMAT"
    assert client.get("/v1/business-days/add?date=2026-10-08&days=abc").json()["error"]["code"] == "INVALID_FORMAT"
    assert client.get("/v1/business-days/add?date=2026-10-08&days=367").json()["error"]["code"] == "INVALID_FORMAT"


def test_business_day_responses_are_deterministic() -> None:
    first = client.get("/v1/business-days/check?date=2026-10-08")
    second = client.get("/v1/business-days/check?date=2026-10-08")
    assert first.content == second.content
