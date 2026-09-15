# Raw Source Files

Raw files in this directory are retained only when they are small and useful for reproducible offline imports.

- `teleoff-phone-areas-30.xls`: official telecom regulator workbook downloaded from `https://www.teleoff.gov.sk/files/urad/odbory-oddelenia/odbor-regulacie-elektronickych-komunikacii/cislovanie/30.xls`.
- `teleoff-phone-areas-30.csv`: UTF-8 CSV conversion of the workbook's `List1` sheet for `scripts/import_phone_areas.py`.
- `minedu-school-facility-counts-2025-09-15.csv`: MŠVVaM `Register škôl a školských zariadení` aggregate CSV downloaded from `https://data.slovensko.sk/download?id=2ca3a9f8-819a-4ea1-8315-769c4fcc57da`; source page lists data validity `15.9.2025`, periodicity `polročne`, licence `Creative Commons BY`, and contact `opendata@minedu.sk`.

Runtime API routes never read from this directory and never call upstream sources.
