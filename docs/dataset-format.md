# Dataset Format

The repository stores its reference data as JSON files under `data/`. These files are loaded directly by the application, so codes should stay string-based and preserve leading zeros.

- Raw source material is curated offline into the checked-in JSON files.
- Generated/curated JSON under `data/` is the runtime input.
- Production requests read those JSON files only; they do not call upstream sources.
- Import scripts should preview into `data/generated/` before promotion to `data/*.json`.
- For geography datasets, regions are verified against the Eurostat LAU 2025 correspondence table; municipalities are imported from PortalVS classifier 9 (`Obce`) with district mappings derived from `code_su`; districts are imported from PortalVS classifier 10 filtered to Slovak rows.

## Source Registry And Public Projection

`data/sources.json` is the internal, maintainer-facing registry. The public `GET /v1/sources*` surface serves a typed curated projection only (`services/sources_service.py`); internal fields such as `redistributionStatus`, `riskLevel`, `nextAction`, `notes`, `sourceFileUrl`, `sourceDocumentationUrl`, and `candidateSourceUrls` are never exposed. The public schema, field boundary, and status mapping are documented in `docs/source-catalogue.md`.

Since 0.23.1, API `metadata.lastUpdated` is an ISO dataset-freshness date or an explicit `null` for meta and error responses; it is never the request-time date.

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
- Licence/acquisition verification notes for broader RPO expansion live in `docs/research/rpo-licence.md` and `docs/research/rpo-acquisition-decision.md`.
- Production `data/companies.json` remains seed-backed in `0.14.0`; RPO-style local files may be normalized by `scripts/import_companies.py` into `data/generated/companies.json` only until the acquisition gate approves production promotion.
- Company validation fails if personal or role-holder fields such as statutory bodies, stakeholders, beneficial owners, person names, birth numbers, private addresses, personal email, or personal phone leak into production JSON.

## VAT Registrations

- `data/vat_registrations.json` is not present in 0.15.0 because production promotion is privacy-blocked.
- Generated research output from `scripts/import_vat_registrations.py` uses `data/generated/vat_registrations.json` and is not a public runtime dataset.
- Future production shape is expected to be `{ "ico": "12345678", "registrations": [{ "vatId": "SK...", "registrationType": "§4", "registeredOn": "YYYY-MM-DD", "vatPayerFrom": null, "registrationTypeChangedOn": null }] }`.
- Names and addresses from the source XML are intentionally excluded from generated output and forbidden in validation.

## Trade Registrations / ŽRSR

- `data/trade_registrations.json` is not present in 0.16.0 because no safe official machine-readable source was verified.
- No importer schema is defined for ŽRSR because the milestone did not verify a real source shape.
- Future candidate fields may include IČO, status, source register, trade activities, and establishment/termination dates, but fields must not be finalized until source access and privacy gates pass.
- Person names, residence/private addresses, birth data, personal contacts, responsible-person data, and role-holder data are excluded by default.

## Streets / Register Adries

- `data/streets.json` is not present in 0.17.0 because no approved production source was verified.
- No street importer schema is defined because the milestone did not verify a reusable official source shape.
- Future candidate records should use official stable street identifiers only if documented by the selected source.
- Do not expose house numbers, apartment data, building coordinates, or person-linked address data by default.

## Public Procurement Notices

- `data/procurement_notices.json` is present in 0.19.0 as a 100-record checked-in TED_PARTIAL snapshot.
- Source is the anonymous TED Search API query `buyer-country = SVK SORT BY publication-date DESC`; this is not the complete ÚVO national register.
- The normalized record shape is institutional notice-reference data only: TED publication number, title, notice type, publication/dispatch/deadline dates, buyer institutional names, buyer country, procedure-level place city/postal/country where present, and a TED XML source URL.
- TED country `SVK` is normalized to `SK`; TED dates with timezone suffixes are normalized to `YYYY-MM-DD`.
- `regionCode`, `districtCode`, and `municipalityCode` are currently `null` because TED city/postal fields do not provide stable official Slovak municipality identifiers.
- Do not expose personal/contact fields, phone/email/fax, street-level addresses, winners, tenderers, subcontractors, beneficial owners, organization identifiers, raw XML/PDF/HTML bodies, or narrative lot text by default.
- Dataset metadata must keep `complete: false`, `coverage: "partial"`, `coverageDecision: "TED_PARTIAL"`, and `acquisitionDecision: "PRODUCTION_IMPORT_APPROVED"`.

## Court Decisions

- `data/court_decisions.json` is not present in 0.22.0 because court-decision reuse/redistribution and privacy gates remain blocked.
- No court-decision importer schema is defined for production because 0.22.0 chose `RESEARCH_AND_TOOLING_ONLY` and `NO_PRODUCTION_DATA`.
- Future candidate records must be metadata-only and should include only an approved local id, ECLI, court id/name, case number, decision type, agenda, decision/publication/finality dates, source URL, and text-availability flag after rights and scope are verified.
- Do not expose full text, snippets/highlights, party/participant names, representatives, lawyers, judges, addresses, emails, phones, IBANs/bank accounts, birth data, identity documents, personal identifiers, or raw participant structures by default.

## Healthcare Facilities / Providers

- `data/healthcare_facilities.json` is not present in 0.18.0 because no approved production source was verified.
- No healthcare-facility importer schema is defined because the milestone did not verify a reusable official record-level source shape.
- Future candidate records should use IdZZ as `id` if exposed by the approved source.
- Do not expose doctor names, nurse names, individual practitioner names, personal contacts, representatives, responsible persons, birth/personal identifiers, private addresses, appointment slots, absences, or pricing/performance files by default.

## Code Conventions

- Keep codes as strings, even when they are numeric-looking.
- Preserve leading zeros in bank codes and PSC values.
- Use uppercase `SK###` for region codes and region-prefixed district codes such as `SK0101` or `SK03210`.
- Use 6-digit municipality codes.

## Null vs Omitted

- Use `null` only for optional links that are known to be unavailable yet still part of the record shape.
- Omit fields only when the dataset schema does not define them.
- For PSC records, `districtCode` and `municipalityCode` may be `null` when the local link is not available.
- For imported municipality records, `districtCode` is required and is derived from PortalVS classifier 9 `code_su`.
- PSC source data does not provide a reliable district mapping; checked-in PSC `districtCode` values are backfilled locally from `municipalityCode`.
- Vehicle registration code `districtCode` is nullable when a legacy legal-table row does not map to one current local district.
- School facility counts do not include `municipalityCode`, school identifiers, school names, or addresses because the confirmed source CSV contains aggregate rows only.
- Procurement notice geography code fields are defined but currently null; they must not be inferred from city names, buyer names, or postal codes without an official verified mapping.

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
    {
      "code": "1100",
      "name": "Tatra banka, a.s.",
      "bic": "TATRSKBX",
      "swift": "TATRSKBX",
      "alphabeticCode": null,
      "activeParty": true,
      "activePartyMarker": "C",
      "country": "SK"
    }
  ]
}
```

- `code` is the four-digit domestic payment-system identification code.
- `bic` and `swift` are uppercase 8- or 11-character identifiers when available; both are retained for API compatibility.
- `alphabeticCode` is `null` for current NBS CSV imports because the CSV snapshot does not expose a separate alphabetic domestic code.
- `activePartyMarker` preserves the normalized NBS participation marker: `C` and `K` map to `activeParty: true`, `Ø` maps to `activeParty: false`.
- `country` is `SK` for runtime bank rows.

### `data/regions.json`

```json
{
  "metadata": { ... },
  "regions": [
    { "code": "SK010", "name": "Bratislavský kraj", "nameEn": "Bratislava Region", "country": "SK" }
  ]
}
```

### `data/phone_areas.json`

```json
{
  "metadata": { ... },
  "phoneAreas": [
    {
      "code": "02",
      "name": "Bratislava",
      "municipalityCode": "528595",
      "municipalityName": "Bratislava - mestská časť Staré Mesto",
      "districtCode": "SK0101",
      "regionCode": "SK010",
      "country": "SK"
    }
  ]
}
```

- `code` is the Slovak primary telephone area code, currently validated as `0#` or `0##`.
- One code can have multiple municipality rows.
- `municipalityCode`, `districtCode`, and `regionCode` are nullable for imported rows when source matching is not reliable.
- Current checked-in data is imported from the retained telecom regulator workbook; source/licence verification remains pending.

### `data/vehicle_registration_codes.json`

```json
{
  "metadata": { ... },
  "vehicleRegistrationCodes": [
    {
      "code": "BA",
      "districtName": "Bratislava",
      "districtCode": null,
      "regionCode": "SK010",
      "validFrom": null,
      "validTo": "2023-01-01",
      "status": "legacy",
      "notes": "Legacy district abbreviation; not reliable for current plate lookup."
    }
  ]
}
```

- `code` is a two-letter legacy district abbreviation from Slov-Lex legal text for vehicle registration numbers.
- `status` is always `legacy`.
- `districtCode` and `regionCode` link to local geography only where that mapping is reliable.
- This dataset is historical/reference data only; it does not decode full licence plates, identify vehicles, or identify owners.
- `validFrom` is currently null because exact start dates are not retained per abbreviation; `validTo` marks the start of the post-2023 allocation model and should not be read as the expiry of already issued plates.

### `data/districts.json`

```json
{
  "metadata": { ... },
  "districts": [
    { "code": "SK0101", "name": "Bratislava I", "regionCode": "SK010", "country": "SK" }
  ]
}
```

### `data/school_facility_counts.json`

```json
{
  "metadata": { ... },
  "schoolFacilityCounts": [
    {
      "schoolKindShort": "GYM",
      "schoolTypeShort": "GYM",
      "kindLevel1": "SŠ",
      "kindLevel2": "GYM",
      "regionName": "Bratislavský",
      "regionCode": "SK010",
      "districtName": "Bratislava I",
      "districtCode": "SK0101",
      "organizationalUnitCount": 2,
      "founderOwnershipType": "cirkevná",
      "founderType": "cirkev, náboženská spoločnosť",
      "country": "SK"
    }
  ]
}
```

- `organizationalUnitCount` is an integer count from the source field `Počet organizačných zložiek`.
- `regionCode` comes from source `NUTS3` and is validated against local regions.
- `districtCode` comes from source `LAU1`; alphabetical LAU suffixes are transformed only when they match local district code, name, and region.
- This file contains aggregate rows only, not institution records. Do not add `schoolCode`, `schoolName`, `address`, director/staff/pupil fields, email, or phone fields.
- `/v1/schools` is intentionally not implemented for this source.

### `data/schools.json`

This file is intentionally absent in 0.20.0. Institution-level school-directory candidates did not pass production acquisition gates. Do not create `data/schools.json` from aggregate `schoolFacilityCounts`, PDFs, frontend scraping, or XLS/RIS exports until reuse rights, documented acquisition, stable identifier semantics, coverage, refresh process, and privacy-safe field rules are verified.

### `data/procurement_notices.json`

```json
{
  "metadata": {
    "source": "TED Search API Slovak-buyer procurement notice snapshot",
    "sourceUrl": "https://api.ted.europa.eu/v3/notices/search",
    "license": "TED / Publications Office reuse terms; preserve attribution.",
    "termsUrl": "https://ted.europa.eu/en/legal-notice",
    "lastUpdated": "2026-09-29",
    "complete": false,
    "coverage": "partial",
    "coverageDecision": "TED_PARTIAL",
    "acquisitionDecision": "PRODUCTION_IMPORT_APPROVED",
    "snapshotLimit": 100,
    "totalNoticesAtSource": 74693
  },
  "procurementNotices": [
    {
      "id": "669481-2026",
      "title": "Slovensko – Stavebné práce ...",
      "noticeType": "can-standard",
      "publicationDate": "2026-09-29",
      "dispatchDate": "2026-09-26",
      "buyerNames": ["Slovenský verejný obstarávateľ"],
      "buyerCountry": "SK",
      "placeOfPerformance": {
        "city": "Bratislava",
        "postalCode": "81101",
        "country": "SK"
      },
      "tenderDeadline": "2026-10-15",
      "regionCode": null,
      "districtCode": null,
      "municipalityCode": null,
      "sourceUrl": "https://ted.europa.eu/en/notice/669481-2026/xml"
    }
  ]
}
```

- `id` is the TED publication number and must match `123456-YYYY`.
- `buyerNames` contains institutional buyer labels only; the importer prefers Slovak then English localized values.
- `placeOfPerformance` uses TED procedure-level city/postal/country reference fields only; no street address is stored.
- Geography codes remain null until an official stable mapping is verified.
- The checked-in file intentionally contains 100 latest Slovak-buyer TED notices from acquisition time; `totalNoticesAtSource` records the larger live source count without claiming it is checked in.

### `data/municipalities.json`

```json
{
  "metadata": { ... },
  "municipalities": [
    { "code": "507814", "name": "Bernolákovo", "districtCode": "SK0102", "regionCode": "SK010", "country": "SK" }
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
- Imported municipality rows should include `districtCode` when sourced from PortalVS classifier 9.
- Imported PSC source rows do not provide reliable district links; checked-in PSC `districtCode` values are backfilled from `municipalityCode` using local municipality mappings.
- PSC `districtCode` coverage is 100% for current local PSC records, with no values inferred from names or PSC patterns.
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
      "districtCode": { "count": 3101, "percentage": 100.0 }
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
