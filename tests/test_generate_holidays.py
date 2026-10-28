from datetime import date
import json

import pytest

from scripts.generate_holidays import easter_sunday, generate, generate_year, serialize, write_candidate, ROOT


# Independent known Gregorian Easter Sundays, including century/exception years;
# 2026/2027 are corroborated by the official NBS table, not generator output.
@pytest.mark.parametrize("year,expected", [
    (1900, "1900-04-15"), (1954, "1954-04-18"), (2000, "2000-04-23"),
    (2024, "2024-03-31"), (2025, "2025-04-20"), (2026, "2026-04-05"),
    (2027, "2027-03-28"), (2028, "2028-04-16"), (2029, "2029-04-01"),
    (2030, "2030-04-21"), (2038, "2038-04-25"), (2100, "2100-03-28"),
])
def test_independent_easter_vectors(year, expected):
    assert easter_sunday(year) == date.fromisoformat(expected)


def test_statutory_exceptions_are_not_commemorative_days():
    for year in range(2024, 2031):
        days = {r["date"][5:] for r in generate_year(year)}
        assert "01-01" in days and "12-26" in days
        assert "09-01" not in days and "10-28" not in days
        assert ("11-17" in days) == (year == 2024)
        assert ("05-08" in days) == (year != 2026)
        assert ("09-15" in days) == (year != 2026)
    assert {r["date"] for r in generate_year(2027)} >= {"2027-03-26", "2027-03-29"}


def test_deterministic_unique_year_consistent_and_production_guard(tmp_path):
    payload = generate(2024, 2030)
    assert sum(map(len, payload.values())) == 90
    assert [len(v) for v in payload.values()] == [14, 13, 11, 13, 13, 13, 13]
    for year, rows in payload.items():
        assert len({r["date"] for r in rows}) == len(rows)
        assert all(str(date.fromisoformat(r["date"]).year) == year and r["name"] and r["name_en"] for r in rows)
    target = tmp_path / "candidate.json"
    write_candidate(2024, 2030, target)
    assert target.read_bytes() == serialize(payload)
    assert serialize(payload) == serialize(generate(2024, 2030))
    with pytest.raises(ValueError, match="--write-production"):
        write_candidate(2024, 2030, ROOT / "data/holidays.json")
    with pytest.raises(ValueError):
        generate(2024, 2031)
