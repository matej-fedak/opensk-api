#!/usr/bin/env python3
"""Offline statutory non-working-holiday calendar, law checked 2026-10-28.

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

# Existing OpenSK display labels retained exactly; September 1 is deliberately
# absent because it is not a non-working holiday in any supported year.
FIXED = {
    "01-01": ("Deň vzniku Slovenskej republiky", "Day of the Establishment of the Slovak Republic"),
    "01-06": ("Zjavenie Pána (Traja králi)", "Epiphany (Three Kings)"),
    "05-01": ("Sviatok práce", "Labour Day"),
    "05-08": ("Deň víťazstva nad fašizmom", "Victory over Fascism Day"),
    "07-05": ("Sviatok svätého Cyrila a Metoda", "Saints Cyril and Methodius Day"),
    "08-29": ("Výročie SNP", "Slovak National Uprising Anniversary"),
    "09-15": ("Sedembolestná Panna Mária", "Our Lady of Sorrows"),
    "11-01": ("Sviatok všetkých svätých", "All Saints' Day"),
    "12-24": ("Štedrý deň", "Christmas Eve"),
    "12-25": ("Prvý sviatok vianočný", "Christmas Day"),
    "12-26": ("Druhý sviatok vianočný", "St. Stephen's Day"),
}


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
    if year == 2024:
        # November 17 was still a non-working holiday before 2025-11-01.
        days["11-17"] = ("Deň boja za slobodu a demokraciu", "Struggle for Freedom and Democracy Day")
    if year == 2026:
        # §4b is explicitly limited to 2026; both resume from 2027.
        del days["05-08"], days["09-15"]
    easter = easter_sunday(year)
    movable = {
        (easter - timedelta(days=2)).strftime("%m-%d"): ("Veľký piatok", "Good Friday"),
        (easter + timedelta(days=1)).strftime("%m-%d"): ("Veľkonočný pondelok", "Easter Monday"),
    }
    assert not set(days) & set(movable)
    days.update(movable)
    return [{"date": date.fromisoformat(f"{year}-{day}").isoformat(), "name": names[0], "name_en": names[1]}
            for day, names in sorted(days.items())]


def generate(start, end):
    if start > end:
        raise ValueError("start must not exceed end")
    return {str(year): generate_year(year) for year in range(start, end + 1)}


def serialize(payload):
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def write_candidate(start, end, output, *, write_production=False):
    output = Path(output).resolve()
    production = ROOT / "data/holidays.json"
    if write_production:
        if output != production or (start, end) != (2024, 2030):
            raise ValueError("production requires the complete reviewed 2024..2030 range and holidays.json target")
    elif output.is_relative_to(ROOT / "data") and not output.is_relative_to(ROOT / "data/generated"):
        raise ValueError("production write requires --write-production")
    payload = generate(start, end)
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
    parser.add_argument("--write-production", action="store_true")
    args = parser.parse_args()
    payload = write_candidate(args.start_year, args.end_year, args.output, write_production=args.write_production)
    print(f"Generated {sum(map(len, payload.values()))} non-working holidays, {args.start_year}..{args.end_year}; rules checked {RULES_VERIFIED_ON}; output {args.output}")
