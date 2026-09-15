# Raw Source Files

Raw files in this directory are retained only when they are small and useful for reproducible offline imports.

- `teleoff-phone-areas-30.xls`: official telecom regulator workbook downloaded from `https://www.teleoff.gov.sk/files/urad/odbory-oddelenia/odbor-regulacie-elektronickych-komunikacii/cislovanie/30.xls`.
- `teleoff-phone-areas-30.csv`: UTF-8 CSV conversion of the workbook's `List1` sheet for `scripts/import_phone_areas.py`.

Runtime API routes never read from this directory and never call upstream sources.
