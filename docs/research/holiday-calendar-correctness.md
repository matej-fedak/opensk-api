# Holiday calendar correctness — 0.23.13

Legal/source verification completed **2026-10-28**. Final verdict:
**HOLIDAYS_EXPANDED_VERIFIED, supported range 2024–2030** (112 statutory
holiday dates, 16 per year, plus separate day-of-rest status).

## Previous data semantics and the bug

The 2024–2026 `data/holidays.json` seed (45 dates, 15/year) conflated two
distinct legal concepts from Act No. 241/1993 Coll. (štátny sviatok vs deň
pracovného pokoja). Every listed date was implicitly treated as a non-working
day, and working state holidays were omitted entirely. Consequences verified
against the pre-change runtime (private baseline `ted-02313/calendar/`):

- 2025-09-01, 2026-09-01: listed and wrongly non-business.
- 2025-11-17, 2026-11-17: listed and wrongly non-business.
- 2026-05-08, 2026-09-15: listed and wrongly non-business.
- 28 October: **absent from the calendar in all years** (2025-10-28 and
  2026-10-28 correctly business days only by omission, with `isHoliday=false`).

## Law versions reviewed (Slov-Lex, 2026-10-28)

Primary source: official Slov-Lex static consolidated texts of
**Act No. 241/1993 Coll.** — `https://static.slov-lex.sk/static/SK/ZZ/1993/241/`.

- Version effective **2024-01-01 through 2025-10-31** (`20240101.html`,
  amendment 530/2023). §1 lists the state holidays; §2(1) makes state holidays
  days of rest unless the Act says otherwise; §2(2) adds ten further statutory
  dates of rest (6 Jan, Good Friday, Easter Monday, 1 May, 8 May, 15 Sep,
  1 Nov, 24–26 Dec); §2(3) exempts **1 September and 28 October** from
  day-of-rest status.
- Version effective **from 2025-11-01** (`20251101.html`, amendment
  **Act 261/2025**, Art. IV / Art. XXII). §2(3) additionally exempts
  **17 November**, so 17 November 2025 is already a working state holiday.
  §4b is a **2026-only** exception: **8 May and 15 September 2026** are not
  days of rest; both dates remain statutory holiday dates and resume
  day-of-rest status from 2027.
- **Future-effective check:** the 241/1993 version history on Slov-Lex lists
  the 2025-11-01 version as current with **no later or future-effective time
  version**; the 261/2025 transitional/effectivity provisions schedule nothing
  beyond 2025-11-01 for these sections; the separate staged effectivity of
  261/2025's own other articles (its later consolidated versions) does not
  touch the holiday calendar. No published amendment changing 2027–2030
  calendar rules was found as of the check date. Future years therefore follow
  currently enacted standing rules and remain **subject to legislative
  change**; regenerate/reverify before extending beyond 2030.

Corroboration only (never the generation input):

- NBS *Sviatky v SR* 2026/2027 — `https://nbs.sk/o-narodnej-banke/sviatky-v-sr/`
  (working 1 Sep / 28 Oct / 17 Nov in both years; working 8 May / 15 Sep in
  2026 only; both back to days of rest in 2027).
- Labour Inspectorate 2026 guidance —
  `https://www.ip.gov.sk/aktuality/sviatky-8-maj-15-september-2026-z-pohladu-pracovneho-prava.html`.
- U.S. Census Bureau X-13AS Easter table (1600–2099) for independent
  Good Friday/Easter Monday vectors 2024–2030 —
  `https://www.census.gov/data/software/x13as/genhol/easter-dates.html`.

## Implemented data model

Additive fields on every `Holiday` record (routes, envelope, operation IDs,
`/v1`, `metadata.version` unchanged):

- `isStateHoliday`: date is a §1 state holiday (6 fixed dates).
- `isDayOfRest`: the date is a statutory day of rest under the applicable
  §2/§4b version **for that year**; independent of weekday/weekend.

Year-specific matrix for the exceptional dates (S = isStateHoliday,
R = isDayOfRest):

| Date | 2024 | 2025 | 2026 | 2027–2030 |
| --- | --- | --- | --- | --- |
| 8 May | F/T | F/T | **F/F** (§4b) | F/T |
| 1 September | T/F | T/F | T/F | T/F |
| 15 September | F/T | F/T | **F/F** (§4b) | F/T |
| 28 October | T/F | T/F | T/F | T/F |
| 17 November | T/T | **T/F** (from 2025-11-01) | T/F | T/F |

The 2025-11-01 transition is date-exact inside 2025: 17 November 2025 falls
after the amendment took effect, so it is already working. No 2026 rule is
applied retroactively to 2024–2025.

## Generation rules

`scripts/generate_holidays.py` (offline, deterministic, no runtime network):

- 14 fixed statutory dates + Gregorian computus Good Friday/Easter Monday
  per year; duplicate fixed/movable collision raises.
- Day-of-rest resolution order: §2(3) fixed working state holidays
  (09-01, 10-28, all years) → 11-17 on/after 2025-11-01 → §4b 2026
  (05-08, 09-15) → otherwise true.
- Explicit `--start-year`/`--end-year` inside the reviewed 2024–2030 horizon;
  dry-run by default (no file written); `--write` for candidates;
  `--write-production` only for the full reviewed range targeting
  `data/holidays.json`, atomically replaced.
- Output is stable-sorted by date; validator enforces year keys, per-year date
  membership, ISO format, uniqueness, ascending order, non-empty SK/EN names,
  boolean flags, plus structural §1/§2(3) invariants for the reviewed horizon.
- Easter: Meeus/Jones/Butcher Gregorian computus, range-asserted
  (1583–4099), no dependency. Independent vectors: Census table
  1900/1954/2000/2100 exception years; NBS 2026 (Good Friday 2026-04-03,
  Easter Monday 2026-04-06) and 2027 (2027-03-26, 2027-03-29); Census
  2028-04-14/17, 2029-03-30/04-02, 2030-04-19/22. Good Friday and
  Easter Monday are days of rest (not §1 state holidays) in all supported
  years.

## Before/after

Dataset: **45** dates (2024–2026, 15/year, implicit all-non-working) →
**112** dates (2024–2030, 16/year; day-of-rest counts
14/13/11/13/13/13/13 per year 2024–2030). `data/holidays.json` SHA-256
(LF): `35a880a20fc6efd6d4b25ba210872a6c1df9d0944ffce88bf2de389e659ae805`.
Generator output is byte-identical to the committed production file (locked
by `tests/test_generate_holidays.py`).

Representative `GET /v1/business-days/check` corrections (before → after,
`isBusinessDay`):

| Date | Before | After |
| --- | --- | --- |
| 2025-09-01 | false (bug) | **true** |
| 2025-10-28 | true, `isHoliday=false` | true, `isHoliday=true`, `isDayOfRest=false` |
| 2025-11-17 | false (bug) | **true** |
| 2026-05-08 | false (bug) | **true** |
| 2026-09-01 | false (bug) | **true** |
| 2026-09-15 | false (bug) | **true** |
| 2026-10-28 | true, `isHoliday=false` | true, `isHoliday=true`, `isDayOfRest=false` |
| 2026-11-17 | false (bug) | **true** |

Unchanged: true days of rest (e.g. 2026-01-01, Good Friday 2026-04-03,
2026-12-24/25) stay non-business; weekend precedence stays (2024-09-01 and
2024-11-17 were Sundays → non-business; 2027-05-08 is a Saturday →
non-business as weekend and restored day of rest).

Business-day rule is now: **Monday–Friday AND NOT a statutory day of rest**.
The check response adds `isDayOfRest`; `isHoliday=true` can validly coexist
with `isBusinessDay=true`. Interval `holidayDays`/`holidays` count only
weekday days of rest — working state holidays no longer increment them
(verified: window containing 2026-09-01 → `holidayDays=0`; Christmas window
unchanged at 2). `add` skips weekends and days of rest only, traversing
2026-05-08 / 09-01 / 09-15 / 10-28 / 11-17 as business days. Supported-year
boundaries: 2024 and 2030 accepted; 2023 and 2031 rejected with
`UNSUPPORTED_YEAR`, including cross-boundary `add`.

This remains an ordinary Monday–Friday calendar minus statutory days of rest —
**not** a TARGET settlement calendar, NBS payment-system calendar,
bank-specific settlement calendar, employer schedule, shop-opening calendar,
or authority opening-hours calendar.

## Freshness and provenance

- `HOLIDAYS_LAST_UPDATED = "2026-10-28"` — the authoritative
  calendar-law/source verification date, not the occurrence date of future
  holidays and not an NBS publication date. Business-day metadata inherits it.
- `data/sources.json` holidays entry: Act 241/1993 (official Slov-Lex) is the
  primary basis; NBS is corroboration, **not** a generated-dataset licence;
  no licence state is upgraded. Exact supported years, the 2025-11-01
  transition, the 2026 temporary exception, and the "subject to legislative
  change" caveat are recorded.
- The calendar is intentionally a bounded, verified window (2024–2030), not a
  claim of being permanently future-proof.
