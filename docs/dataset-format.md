# Dataset Format

The repository stores its reference data as JSON files under `data/`. These files are loaded directly by the application, so codes should stay string-based and preserve leading zeros.

- Raw source material is curated offline into the checked-in JSON files.
- Generated/curated JSON under `data/` is the runtime input.
- Production requests read those JSON files only; they do not call upstream sources.
- Import scripts should preview into `data/generated/` before promotion to `data/*.json`.
- For geography datasets, regions are verified against the Eurostat LAU 2025 correspondence table; municipalities are imported from the Eurostat LAU 2025 workbook with nullable district links; districts remain unverified seed data.

## Company Seed Dataset

The repository now includes a small checked-in company seed dataset for the local lookup endpoints. Broader coverage is still research-only.

Proposed normalized company dataset shape:

```json
{
  "metadata": {
    "source": "Verified public organizational contact pages",
    "lastUpdated": "YYYY-MM-DD",
    "complete": false
  },
  "companies": [
    {
      "ico": "50158635",
      "name": "Slovensko.Digital",
      "legalForm": "občianske združenie",
      "legalStatus": "active",
      "sourceRegister": "Register občianskych združení",
      "address": {
        "street": "Staré grunty",
        "registrationNumber": null,
        "buildingNumber": "18",
        "municipality": "Bratislava",
        "postalCode": "84104",
        "country": "SK",
        "municipalityCode": null,
        "regionCode": null,
        "districtCode": null
      },
      "establishedOn": null,
      "terminatedOn": null,
      "updatedAt": "2026-06-03",
      "source": {
        "name": "https://slovensko.digital/kontakt/",
        "recordId": "kontakt"
      }
    }
  ]
}
```

Each `companies[]` item uses this shape:

```json
{
  "ico": "50158635",
  "name": "Slovensko.Digital",
  "legalForm": null,
  "legalStatus": null,
  "sourceRegister": "Register občianskych združení",
  "address": {
    "street": "Staré Grunty",
    "registrationNumber": "205",
    "buildingNumber": "18",
    "municipality": "Bratislava - Karlova Ves",
    "postalCode": "84104",
    "country": "SK",
    "municipalityCode": null,
    "regionCode": null,
    "districtCode": null
  },
  "establishedOn": "2016-01-29",
  "terminatedOn": null,
  "updatedAt": "2025-10-03",
  "source": {
    "name": "RPO V2",
    "recordId": "6562824"
  }
}
```

- `ico` stays a string and should preserve leading zeros.
- `legalForm`, `legalStatus`, `sourceRegister`, `establishedOn`, `terminatedOn`, and `updatedAt` are optional in the source but should be present in the normalized output as strings or `null`.
- `address` is normalized and should not be stored only as a free-form text blob.
- `registrationNumber`, `buildingNumber`, `municipalityCode`, `districtCode`, and `regionCode` follow the same string/null conventions as the geography datasets.
- The schema is the normalized shape used by the checked-in seed dataset.
- Keep personal, stakeholder, statutory-body, and other role-holder fields out of this prototype.
- Do not scrape ORSR/ŽRSR for this dataset; they are reference-only.
- Licence verification notes for broader RPO expansion live in `docs/research/rpo-licence.md`.

## Code Conventions

- Keep codes as strings, even when they are numeric-looking.
- Preserve leading zeros in bank codes and PSC values.
- Use uppercase `SK###` for region codes and `SK####` for district codes.
- Use 6-digit municipality codes.

## Null vs Omitted

- Use `null` only for optional links that are known to be unavailable yet still part of the record shape.
- Omit fields only when the dataset schema does not define them.
- For PSC records, `districtCode` and `municipalityCode` may be `null` when the local link is not available.
- For imported municipality records, `districtCode` may be `null` because the Eurostat LAU workbook does not provide district mappings.
- In the current imported PSC data, `districtCode` is `null` throughout because the source data does not provide a reliable district mapping.

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
    { "code": "507814", "name": "Bernolákovo", "districtCode": null, "regionCode": "SK010", "country": "SK" }
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
- Imported municipality rows may have `districtCode: null` when the source workbook does not provide district mappings.
- Imported PSC rows currently have `districtCode: null` in the checked-in dataset.
- PSC geography links are local data, not a live lookup.
- The PSC source may contain multiple rows for the same postal code; importer previews should report that with `matchCount` and `matches` before selecting a canonical runtime record.

### PSC List/Search Responses

`GET /v1/psc` and `GET /v1/psc/search` both return a paginated envelope:

```json
{
  "data": {
    "items": [],
    "count": 0,
    "total": 0,
    "limit": 100,
    "offset": 0
  },
  "metadata": { ... },
  "error": null
}
```

- `items` contains flattened PSC match records.
- `count` is the number of items returned for the current page.
- `total` is the total number of records after filters/search before pagination.
- `limit` and `offset` are echoed back after validation.
- Search uses the same item shape as the list endpoint.

### PSC Stats

`GET /v1/psc/stats` returns local dataset totals and geography coverage:

```json
{
  "data": {
    "recordCount": 3101,
    "uniquePscCount": 1420,
    "multiMatchPscCount": 759,
    "geographyCoverage": {
      "municipalityCode": { "count": 3101, "percentage": 100.0 },
      "regionCode": { "count": 3101, "percentage": 100.0 },
      "districtCode": { "count": 0, "percentage": 0.0 }
    },
    "source": {
      "name": "PortalVS Číselníky classifier 42",
      "licenceStatus": "Source/licence verification pending."
    }
  }
}
```

Example preview shape for an ambiguous PSC code:

```json
{
  "data": {
    "psc": "81101",
    "matchCount": 2,
    "matches": [
      { "psc": "81101", "city": "Bratislava" },
      { "psc": "81101", "city": "Bratislava - mestská časť Staré Mesto" }
    ]
  }
}
```

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
