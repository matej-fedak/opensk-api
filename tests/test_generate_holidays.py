from datetime import date
import json

import pytest

from scripts.generate_holidays import easter_sunday, generate, generate_year, serialize, write_candidate, ROOT


# Independent known Gregorian Easter Sundays, including century/exception years;
# Census Bureau Easter table (1600-2099), plus NBS 2026/2027 corroboration:
# https://www.census.gov/data/software/x13as/genhol/easter-dates.html
@pytest.mark.parametrize("year,expected", [
    (1900, "1900-04-15"), (1954, "1954-04-18"), (2000, "2000-04-23"),
    (2024, "2024-03-31"), (2025, "2025-04-20"), (2026, "2026-04-05"),
    (2027, "2027-03-28"), (2028, "2028-04-16"), (2029, "2029-04-01"),
    (2030, "2030-04-21"), (2038, "2038-04-25"), (2100, "2100-03-28"),
])
def test_independent_easter_vectors(year, expected):
    assert easter_sunday(year) == date.fromisoformat(expected)


def test_statutory_holidays_remain_present_with_year_specific_rest_status():
    for year in range(2024, 2031):
        days = {r["date"][5:]: r for r in generate_year(year)}
        assert len(days) == 16
        assert sum(r["isStateHoliday"] for r in days.values()) == 6
        for month_day in ("09-01", "10-28"):
            assert days[month_day]["isStateHoliday"] is True
            assert days[month_day]["isDayOfRest"] is False
        assert days["11-17"]["isStateHoliday"] is True
        assert days["11-17"]["isDayOfRest"] is (year == 2024)
        for month_day in ("05-08", "09-15"):
            assert days[month_day]["isStateHoliday"] is False
            assert days[month_day]["isDayOfRest"] is (year != 2026)
    assert {r["date"] for r in generate_year(2027)} >= {"2027-03-26", "2027-03-29"}


def test_deterministic_unique_year_consistent_and_production_guard(tmp_path):
    payload = generate(2024, 2030)
    assert sum(map(len, payload.values())) == 112
    assert [sum(r["isDayOfRest"] for r in v) for v in payload.values()] == [14, 13, 11, 13, 13, 13, 13]
    for year, rows in payload.items():
        assert len({r["date"] for r in rows}) == len(rows)
        assert all(str(date.fromisoformat(r["date"]).year) == year and r["name"] and r["name_en"] for r in rows)
        assert [r["date"] for r in rows] == sorted(r["date"] for r in rows)
    target = tmp_path / "candidate.json"
    write_candidate(2024, 2030, target)
    assert not target.exists()  # Dry-run must not even write the candidate.
    write_candidate(2024, 2030, target, write=True)
    assert target.read_bytes() == serialize(payload)
    assert serialize(payload) == serialize(generate(2024, 2030))
    with pytest.raises(ValueError, match="--write-production"):
        write_candidate(2024, 2030, ROOT / "data/holidays.json")
    with pytest.raises(ValueError):
        generate(2024, 2031)


@pytest.mark.parametrize("year,friday,monday", [
    (2024, "2024-03-29", "2024-04-01"), (2025, "2025-04-18", "2025-04-21"),
    (2026, "2026-04-03", "2026-04-06"), (2027, "2027-03-26", "2027-03-29"),
    (2028, "2028-04-14", "2028-04-17"), (2029, "2029-03-30", "2029-04-02"),
    (2030, "2030-04-19", "2030-04-22"),
])
def test_independent_good_friday_easter_monday_dates(year, friday, monday):
    days = {r["date"]: r for r in generate_year(year)}
    for day in (friday, monday):
        assert days[day]["isDayOfRest"] is True
        assert days[day]["isStateHoliday"] is False


def test_generator_exactly_reproduces_committed_production():
    assert (ROOT / "data/holidays.json").read_bytes().replace(b"\r\n", b"\n") == serialize(generate(2024, 2030))
