# Import Pipeline

OpenSK API keeps runtime requests fully local. Import tooling exists so new or updated public datasets can be normalized offline before anything is promoted into `data/*.json`.

## Storage Layers

- `data/raw/` stores downloaded or manually supplied source material.
- `data/generated/` stores normalized preview output from import scripts.
- `data/*.json` remains the production runtime input for the API.
- Geography imports for regions and municipalities should be checked against the Eurostat LAU 2025 correspondence table and workbook.
- District imports are sourced from PortalVS classifier 10 filtered to Slovak rows; keep upstream notices and treat reuse as restricted until terms are fully settled.
- PSC imports are handled by `scripts/import_psc.py`; source/licence verification is still pending, so do not treat the input as redistributable without checking upstream terms. The imported PSC dataset currently keeps `districtCode` null because the source does not supply a reliable district mapping, and coverage is partial rather than national.

## Company Import Prototype

- IČO/company lookup now uses a small checked-in local seed dataset.
- Broader company coverage is still research-only and depends on licence/privacy follow-up.
- RPO licence verification remains pending; see `docs/research/rpo-licence.md`.
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
python scripts/import_geography.py --dataset municipalities --input data/raw/EU-27-LAU-2025-NUTS-2024.xlsx --dry-run --output data/generated/municipalities.json
```

```bash
python scripts/import_psc.py --input data/raw/psc-source.csv --output data/generated/psc.json --dry-run
```

```bash
python scripts/import_companies.py --input data/raw/rpo_sample.json --output data/generated/companies.json --dry-run
```

## Write Workflow

Only `--write` writes files.

```bash
python scripts/import_geography.py --dataset municipalities --input data/raw/EU-27-LAU-2025-NUTS-2024.xlsx --output data/generated/municipalities.json --write
```

```bash
python scripts/import_psc.py --input data/raw/psc-source.csv --output data/generated/psc.json --write
```

```bash
python scripts/import_companies.py --input data/raw/rpo_sample.json --output data/generated/companies.json --write
```

The importer refuses to write when validation fails. Referential integrity failures also block writes unless `--allow-incomplete` is explicitly provided.

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
