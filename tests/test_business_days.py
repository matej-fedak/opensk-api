"""Slovak business-day utility tests.

Business day = Monday-Friday and not a holiday in the local holidays.json
dataset. Supported years are derived from the dataset (currently 2024-2026);
dates outside that coverage are rejected with UNSUPPORTED_YEAR.
"""

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def _data(response) -> dict[str, object]:  # type: ignore[no-untyped-def]
    assert response.json()["error"] is None
    assert response.json()["metadata"]["version"] == "v1"
    assert response.json()["metadata"]["lastUpdated"] == "2026-05-25"
    return response.json()["data"]


def test_check_weekday_is_business_day() -> None:
    data = _data(client.get("/v1/business-days/check?date=2026-10-08"))
    assert data["isBusinessDay"] is True
    assert data["isWeekend"] is False
    assert data["isHoliday"] is False
    assert data["holidayName"] is None
    assert data["supportedYears"] == [2024, 2025, 2026]


def test_check_saturday_and_sunday_are_not_business_days() -> None:
    for day in ("2026-10-10", "2026-10-11"):
        data = _data(client.get(f"/v1/business-days/check?date={day}"))
        assert data["isWeekend"] is True
        assert data["isBusinessDay"] is False


def test_check_known_weekday_holiday_is_not_business_day() -> None:
    data = _data(client.get("/v1/business-days/check?date=2026-01-01"))
    assert data["isHoliday"] is True
    assert data["holidayName"] is not None
    assert data["isBusinessDay"] is False

    good_friday = _data(client.get("/v1/business-days/check?date=2026-04-03"))
    assert good_friday["isBusinessDay"] is False
    assert good_friday["isHoliday"] is True


def test_add_skips_weekend() -> None:
    data = _data(client.get("/v1/business-days/add?date=2026-10-08&days=5"))
    assert data["result"] == "2026-10-15"
    assert data["resultIsBusinessDay"] is True


def test_add_skips_holidays_and_weekends_across_christmas() -> None:
    # 24.-26.12.2026 are holidays, 27.12. is Sunday.
    data = _data(client.get("/v1/business-days/add?date=2026-12-23&days=1"))
    assert data["result"] == "2026-12-28"


def test_add_negative_days() -> None:
    data = _data(client.get("/v1/business-days/add?date=2026-10-12&days=-1"))
    assert data["result"] == "2026-10-09"

    backwards = _data(client.get("/v1/business-days/add?date=2026-06-15&days=-30"))
    assert backwards["result"] == "2026-04-30"


def test_add_zero_days_returns_same_date() -> None:
    data = _data(client.get("/v1/business-days/add?date=2026-10-08&days=0"))
    assert data["result"] == "2026-10-08"


def test_leap_year_february_29() -> None:
    data = _data(client.get("/v1/business-days/add?date=2024-02-28&days=1"))
    assert data["result"] == "2024-02-29"
    check = _data(client.get("/v1/business-days/check?date=2024-02-29"))
    assert check["isBusinessDay"] is True


def test_unsupported_years_are_rejected_strictly() -> None:
    for url in (
        "/v1/business-days/check?date=2027-01-04",
        "/v1/business-days/check?date=2023-01-02",
        "/v1/business-days/add?date=2026-12-30&days=5",
        "/v1/business-days/between?from=2026-12-01&to=2027-01-10",
    ):
        response = client.get(url)
        assert response.status_code == 400, url
        assert response.json()["error"]["code"] == "UNSUPPORTED_YEAR"


def test_between_counts_business_weekend_and_holiday_days() -> None:
    # 2026-12-24/25 are weekday holidays; 2026-12-26 is a holiday on a Saturday
    # and is classified as a weekend day (weekend classification takes precedence).
    data = _data(client.get("/v1/business-days/between?from=2026-12-22&to=2026-12-28"))
    assert data["totalDays"] == 7
    assert data["weekendDays"] == 2
    assert data["holidayDays"] == 2
    assert data["businessDays"] == 3  # 22, 23 and 28
    assert {hit["date"] for hit in data["holidays"]} == {"2026-12-24", "2026-12-25"}


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
