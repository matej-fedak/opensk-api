# Dataset Format

The repository stores its reference data as JSON files under `data/`. These files are loaded directly by the application, so codes should stay string-based and preserve leading zeros.

- Raw source material is curated offline into the checked-in JSON files.
- Generated/curated JSON under `data/` is the runtime input.
- Production requests read those JSON files only; they do not call upstream sources.
- Import scripts should preview into `data/generated/` before promotion to `data/*.json`.

## Code Conventions

- Keep codes as strings, even when they are numeric-looking.
- Preserve leading zeros in bank codes and PSC values.
- Use uppercase `SK###` for region codes and `SK####` for district codes.
- Use 6-digit municipality codes.

## Null vs Omitted

- Use `null` only for optional links that are known to be unavailable yet still part of the record shape.
- Omit fields only when the dataset schema does not define them.
- For PSC records, `districtCode` and `municipalityCode` may be `null` when the local link is not available.

## Common Metadata

Where present, dataset metadata uses this shape:

```json
{
  "source": "...",
  "license": "...",
  "lastUpdated": "YYYY-MM-DD",
  "complete": true
}
```

- `source` and `license` are free-text strings.
- `lastUpdated` is an ISO date string.
- `complete` is optional and used for coverage notes on geography datasets.
- If source or licence cannot be verified, use `Source/licence verification pending.`

## Date Format

- Use `YYYY-MM-DD` for all dates.
- Holiday record dates must match the year key they live under.

## File Shapes

### `data/banks.json`

```json
{
  "metadata": { ... },
  "banks": [
    { "code": "1100", "name": "Tatra banka, a.s.", "country": "Slovakia" }
  ]
}
```

### `data/regions.json`

```json
{
  "metadata": { ... },
  "regions": [
    { "code": "SK010", "name": "Bratislavský kraj", "nameEn": "Bratislava Region", "country": "SK" }
  ]
}
```

### `data/districts.json`

```json
{
  "metadata": { ... },
  "districts": [
    { "code": "SK0101", "name": "Bratislava I", "regionCode": "SK010", "country": "SK" }
  ]
}
```

### `data/municipalities.json`

```json
{
  "metadata": { ... },
  "municipalities": [
    { "code": "528595", "name": "Bratislava - Staré Mesto", "districtCode": "SK0101", "regionCode": "SK010", "country": "SK" }
  ]
}
```

### `data/psc.json`

`psc.json` is keyed by postal code:

```json
{
  "81101": {
    "psc": "81101",
    "city": "Bratislava",
    "municipality": "Bratislava - mestská časť Staré Mesto",
    "municipalityCode": "528595",
    "district": "Bratislava I",
    "districtCode": "SK0101",
    "region": "Bratislavský kraj",
    "regionCode": "SK010",
    "country": "Slovakia"
  }
}
```

- `municipalityCode` and `districtCode` can be `null` when the local link is not available.
- PSC geography links are local seed data, not a live lookup.

### `data/holidays.json`

`holidays.json` is keyed by year string:

```json
{
  "2026": [
    { "date": "2026-01-01", "name": "...", "name_en": "..." }
  ]
}
```

- Each holiday entry uses `date`, `name`, and `name_en`.
- Years are stored as strings to keep the file stable and predictable.

## Adding a New Dataset Safely

1. Add the JSON file under `data/` with a clear schema and metadata when applicable.
2. Add shape validation to `scripts/validate_datasets.py`.
3. Add any cross-file checks to `scripts/check_referential_integrity.py`.
4. Add direct tests in `tests/test_dataset_integrity.py`.
5. Update `docs/data-sources.md` and `docs/dataset-format.md`.
6. Run `python scripts/validate_datasets.py`, `python scripts/check_referential_integrity.py`, and `python -m pytest` before committing.
