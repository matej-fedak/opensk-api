# Import Pipeline

OpenSK API keeps runtime requests fully local. Import tooling exists so new or updated public datasets can be normalized offline before anything is promoted into `data/*.json`.

## Storage Layers

- `data/raw/` stores downloaded or manually supplied source material.
- `data/generated/` stores normalized preview output from import scripts.
- `data/*.json` remains the production runtime input for the API.
- Geography imports for regions should be checked against the Eurostat LAU 2025 correspondence table; municipalities should be imported from PortalVS classifier 9 (`Obce`) JSON/CSV exports.
- District imports are sourced from PortalVS classifier 10 filtered to Slovak rows; keep upstream notices and treat reuse as restricted until terms are fully settled.
- PSC imports are handled by `scripts/import_psc.py`; source/licence verification is still pending, so do not treat the input as redistributable without checking upstream terms. `scripts/backfill_psc_districts.py` backfills PSC `districtCode` from `municipalityCode` using local municipality mappings only; no values are inferred from names or PSC patterns. PSC coverage remains partial rather than national.
- Bank imports are handled by `scripts/import_banks.py` from offline NBS directory snapshots. Source/licence verification is still pending; runtime routes never call NBS.
- Phone-area imports are handled by `scripts/import_phone_areas.py` from local CSV/JSON/XLSX files. The official regulator source is a legacy `.xls` workbook retained under `data/raw/`; convert the `List1` sheet to CSV before importing. Runtime routes never call the regulator.
- Vehicle registration district codes are manually curated from Slov-Lex legal text into `data/vehicle_registration_codes.json`. This historical/reference dataset has no runtime upstream calls and no full-plate decoder.
- School facility aggregate counts are handled by `scripts/import_school_facility_counts.py` from the confirmed local MŠVVaM CSV. The source is aggregate RIS data, not an institution-level school directory, and runtime routes never call MŠVVaM.
- Institution-level school-directory import tooling is not present. 0.20.0 did not approve CVTI/RIS/PDF candidates for production, so adding `scripts/fetch_schools.py`, `scripts/import_schools.py`, `data/schools.json`, or `/v1/schools` would be premature.
- Public procurement notices are handled by `scripts/fetch_procurement_notices.py` and `scripts/import_procurement_notices.py`. The fetcher downloads a bounded anonymous TED Search API snapshot into `data/raw/`; the importer normalizes a privacy-scoped TED_PARTIAL runtime dataset and runtime routes never call TED or ÚVO.
- VAT registration research tooling is handled by `scripts/fetch_vat_registrations.py` and `scripts/import_vat_registrations.py` from the official Finančná správa ZIP/XML. The importer writes generated output only and refuses `data/vat_registrations.json` while the privacy gate is blocked.
- ŽRSR/trade-register import tooling is not present. 0.16.0 did not verify an official machine-readable source shape, so adding an importer would be speculative.
- Streets/Register adries import tooling is not present. 0.17.0 did not verify an approved reusable official distribution, so adding a fetcher/importer would be premature.
- Healthcare-facilities import tooling is not present. 0.18.0 did not verify an approved reusable record-level official distribution, so adding a fetcher/importer would be premature.

## Company Import Prototype

- IČO/company lookup now uses a small checked-in local seed dataset.
- Broader company coverage is still research-only and depends on licence/privacy follow-up.
- RPO production acquisition remains blocked; see `docs/research/rpo-acquisition-decision.md` and `docs/research/rpo-licence.md`.
- `scripts/import_companies.py` can normalize local RPO-style JSON fixtures into `data/generated/companies.json`, excluding natural-person/person-like records and stripping forbidden role/person fields. It still refuses to write `data/companies.json` until the acquisition gate approves production import.
- The proposed normalized record shape is documented in `docs/dataset-format.md`.
- Source evaluation notes live in `docs/research/ico-sources.md`.
- ORSR and ŽRSR are reference-only sources here; do not scrape their HTML.

Proposed offline flow:

1. Collect candidate source material into `data/raw/` or an external working directory.
2. Normalize the data into `data/generated/companies.json` as a preview only.
3. Validate identifiers, address normalization, and provenance notes.
4. Review the generated diff before any promotion into `data/`.
5. Do not publish anything that depends on unverified licensing, redistribution terms, or scraped ORSR/ŽRSR HTML.

## Workflow

1. Capture raw source material locally.
2. Run an importer in dry-run mode first.
3. Inspect the generated diff under `data/generated/`.
4. Run validation and referential integrity checks.
5. Promote the generated JSON into the checked-in `data/` files only after review.

## Dry Run First

Dry run is the default. Use it to preview what would be generated without writing files.

```bash
python scripts/import_geography.py --dataset municipalities --input data/raw/portalvs-classifier-9.json --dry-run --output data/generated/municipalities.json
```

```bash
python scripts/import_psc.py --input data/raw/psc-source.csv --output data/generated/psc.json --dry-run
python scripts/backfill_psc_districts.py --dry-run
```

```bash
python scripts/import_companies.py --input data/raw/rpo_sample.json --output data/generated/companies.json --dry-run
```

```bash
python scripts/import_banks.py --input data/raw/nbs-bank-directory.csv --output data/generated/banks.json --dry-run
```

```bash
python scripts/import_phone_areas.py --input data/raw/phone-areas.csv --output data/generated/phone_areas.json --dry-run
python scripts/import_phone_areas.py --input data/raw/phone-areas.xlsx --output data/generated/phone_areas.json --dry-run
python scripts/import_phone_areas.py --input data/raw/teleoff-phone-areas-30.csv --output data/generated/phone_areas.json --dry-run
python scripts/import_school_facility_counts.py --input data/raw/minedu-school-facility-counts-2025-09-15.csv --output data/generated/school_facility_counts.json --dry-run
python scripts/fetch_procurement_notices.py --limit 100 --dry-run
python scripts/fetch_procurement_notices.py --limit 100 --write
python scripts/import_procurement_notices.py --input data/raw/procurement-notices-ted-search.json --output data/generated/procurement_notices.json --dry-run
python scripts/import_vat_registrations.py data/raw/ds_dphs.zip --output data/generated/vat_registrations.json
```

## Write Workflow

Only `--write` writes files.

```bash
python scripts/import_geography.py --dataset municipalities --input data/raw/portalvs-classifier-9.csv --output data/generated/municipalities.json --write
```

```bash
python scripts/import_psc.py --input data/raw/psc-source.csv --output data/generated/psc.json --write
python scripts/backfill_psc_districts.py --write
```

```bash
python scripts/import_companies.py --input data/raw/rpo_sample.json --output data/generated/companies.json --write
```

```bash
python scripts/import_banks.py --input data/raw/nbs-bank-directory.csv --output data/generated/banks.json --write --last-updated 2026-05-18
```

```bash
python scripts/import_phone_areas.py --input data/raw/phone-areas.xlsx --output data/generated/phone_areas.json --write --last-updated YYYY-MM-DD
python scripts/import_phone_areas.py --input data/raw/teleoff-phone-areas-30.csv --output data/generated/phone_areas.json --write --last-updated 2026-09-15
python scripts/import_school_facility_counts.py --input data/raw/minedu-school-facility-counts-2025-09-15.csv --output data/generated/school_facility_counts.json --write --last-updated 2025-09-15
python scripts/import_procurement_notices.py --input data/raw/procurement-notices-ted-search.json --output data/generated/procurement_notices.json --write
python scripts/import_vat_registrations.py data/raw/ds_dphs.zip --output data/generated/vat_registrations.json --write
```

The importer refuses to write when validation fails. Referential integrity failures also block writes unless `--allow-incomplete` is explicitly provided.

`scripts/import_vat_registrations.py` additionally refuses production output at `data/vat_registrations.json` until the VAT privacy gate is approved.

Procurement refreshes use the reviewed generated output flow by default. Promote `data/procurement_notices.json` only after validating the TED_PARTIAL snapshot and reviewing the diff.

## Validation Workflow

Run the dataset checks before promotion:

```bash
python scripts/validate_datasets.py
python scripts/check_referential_integrity.py
```

## Adding a New Source

1. Add a source entry to `data/sources.json`.
2. Place raw material in `data/raw/` if it is small enough for Git; otherwise keep it outside the repo and document the download step.
3. Extend `scripts/import_geography.py` or add a dataset-specific importer such as `scripts/import_psc.py`.
4. Add/extend validation before any write step.
5. Add tests for both dry-run and write behavior.

## Review Guidance

- Review generated JSON diffs before copying anything into `data/`.
- Do not overwrite a known-good checked-in dataset until the new output has passed validation and integrity checks.
- The API must never fetch upstream data at request time.
