#!/usr/bin/env python3
"""Offline statutory holiday calendar with separate day-of-rest status.

Law 241/1993, versions 2024-01-01 and 2025-11-01 (§2, §4b). No network,
no NBS-table copy, no payroll/settlement calendar. Future years describe currently
enacted rules, not a guarantee that legislation cannot change.
"""

import argparse
from datetime import date, timedelta
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES_VERIFIED_ON = "2026-10-28"
VERIFIED_FIRST_YEAR = 2024
VERIFIED_LAST_YEAR = 2030

# §1 state holidays; §2(2) adds ten other holiday dates (including Easter).
# Existing display labels stay unchanged. Working holidays remain in the data.
STATE_HOLIDAYS = frozenset({"01-01", "07-05", "08-29", "09-01", "10-28", "11-17"})
FIXED = {
    "01-01": ("Deň vzniku Slovenskej republiky", "Day of the Establishment of the Slovak Republic"),
    "01-06": ("Zjavenie Pána (Traja králi)", "Epiphany (Three Kings)"),
    "05-01": ("Sviatok práce", "Labour Day"),
    "05-08": ("Deň víťazstva nad fašizmom", "Victory over Fascism Day"),
    "07-05": ("Sviatok svätého Cyrila a Metoda", "Saints Cyril and Methodius Day"),
    "08-29": ("Výročie SNP", "Slovak National Uprising Anniversary"),
    "09-01": ("Deň Ústavy Slovenskej republiky", "Constitution Day of the Slovak Republic"),
    "09-15": ("Sedembolestná Panna Mária", "Our Lady of Sorrows"),
    "10-28": ("Deň vzniku samostatného česko-slovenského štátu", "Day of the Establishment of the Independent Czechoslovak State"),
    "11-01": ("Sviatok všetkých svätých", "All Saints' Day"),
    "11-17": ("Deň boja za slobodu a demokraciu", "Struggle for Freedom and Democracy Day"),
    "12-24": ("Štedrý deň", "Christmas Eve"),
    "12-25": ("Prvý sviatok vianočný", "Christmas Day"),
    "12-26": ("Druhý sviatok vianočný", "St. Stephen's Day"),
}
NOVEMBER_TRANSITION = date(2025, 11, 1)  # Act 261/2025, Art. IV / Art. XXII


def is_day_of_rest(day):
    """Holiday-specific §2/§4b status, independent of weekday/weekend.

    Called only for §1/§2 holiday dates, not arbitrary calendar dates. This
    intentionally does not label all Sundays as holiday records.
    """
    month_day = day.strftime("%m-%d")
    if month_day in {"09-01", "10-28"}:  # §2(3), from 2024-01-01 throughout horizon
        return False
    if month_day == "11-17" and day >= NOVEMBER_TRANSITION:
        return False
    if date(2026, 1, 1) <= day < date(2027, 1, 1) and month_day in {"05-08", "09-15"}:
        return False  # §4b; neither date ceases being a statutory holiday
    return True


def easter_sunday(year):
    """Gregorian Meeus/Jones/Butcher computus; independently checked vectors."""
    if not 1583 <= year <= 4099:
        raise ValueError("Gregorian computus range is 1583..4099")
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month, day0 = divmod(h + l - 7 * m + 114, 31)
    return date(year, month, day0 + 1)


def generate_year(year):
    if not VERIFIED_FIRST_YEAR <= year <= VERIFIED_LAST_YEAR:
        raise ValueError("outside reviewed statutory calendar horizon 2024..2030")
    days = dict(FIXED)
    easter = easter_sunday(year)
    movable = {
        (easter - timedelta(days=2)).strftime("%m-%d"): ("Veľký piatok", "Good Friday"),
        (easter + timedelta(days=1)).strftime("%m-%d"): ("Veľkonočný pondelok", "Easter Monday"),
    }
    if set(days) & set(movable):
        raise ValueError("duplicate fixed/movable holiday date")
    days.update(movable)
    return [{"date": date.fromisoformat(f"{year}-{day}").isoformat(), "name": names[0], "name_en": names[1],
             "isStateHoliday": day in STATE_HOLIDAYS,
             "isDayOfRest": is_day_of_rest(date.fromisoformat(f"{year}-{day}"))}
            for day, names in sorted(days.items())]


def generate(start, end):
    if start > end:
        raise ValueError("start must not exceed end")
    return {str(year): generate_year(year) for year in range(start, end + 1)}


def serialize(payload):
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def write_candidate(start, end, output, *, write=False, write_production=False):
    output = Path(output).resolve()
    production = ROOT / "data/holidays.json"
    if write_production:
        if output != production or (start, end) != (2024, 2030):
            raise ValueError("production requires the complete reviewed 2024..2030 range and holidays.json target")
    elif output.is_relative_to(ROOT / "data") and not output.is_relative_to(ROOT / "data/generated"):
        raise ValueError("production write requires --write-production")
    payload = generate(start, end)
    if not (write or write_production):
        return payload  # Dry-run by default, including candidate targets.
    output.parent.mkdir(parents=True, exist_ok=True)
    # One atomic replacement, never partial production JSON.
    staging = output.with_suffix(".candidate")
    staging.write_bytes(serialize(payload))
    staging.replace(output)
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-year", type=int, required=True)
    parser.add_argument("--end-year", type=int, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "data/generated/holidays.json")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Validate and summarize without writing (default)")
    mode.add_argument("--write", action="store_true", help="Write an unpromoted candidate")
    mode.add_argument("--write-production", action="store_true")
    args = parser.parse_args()
    payload = write_candidate(args.start_year, args.end_year, args.output, write=args.write, write_production=args.write_production)
    mode = "written" if args.write or args.write_production else "dry-run, not written"
    print(f"Generated {sum(map(len, payload.values()))} statutory holidays, {args.start_year}..{args.end_year}; rules checked {RULES_VERIFIED_ON}; {mode}: {args.output}")
