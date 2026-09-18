# OpenSK API

OpenSK API is a FastAPI service that exposes a small set of Slovak public data through a consistent JSON envelope.

Status: `0.10.0-dev` pre-1.0 development build.

OpenSK API is still before its first formal stable `1.0.0` release. Earlier `v1.x` labels in the changelog were internal development milestone labels, not formal stable releases. The current `/v1` route prefix is an API namespace and remains unchanged during the pre-1.0 reset.

See `docs/versioning.md` for the versioning policy. Future `1.0.0` is reserved for the first stable public API contract after stabilization and source/compliance review.

No API key is required. CORS is enabled for browser clients. All responses are JSON.

## Endpoint Matrix

### Stable

| Endpoint | Status | Notes |
| --- | --- | --- |
| `GET /` | stable | Project info |
| `GET /v1/health` | stable | Health check |
| `GET /v1/iban/validate/SK...` | stable | Slovak IBAN validation |
| `GET /v1/regions` | stable | Static regions dataset |
| `GET /v1/regions/SK010` | stable | Static region lookup |
| `GET /v1/districts` | stable | Complete districts dataset; PortalVS terms may restrict reuse |
| `GET /v1/districts/SK0101` | stable | Complete district lookup; PortalVS terms may restrict reuse |
| `GET /v1/municipalities` | stable | Static municipalities dataset |
| `GET /v1/municipalities/528595` | stable | Static municipality lookup |
| `GET /v1/banks` | stable | Static NBS bank-code dataset; source/licence verification pending |
| `GET /v1/banks/1100` | stable | Static bank-code lookup; source/licence verification pending |
| `GET /v1/phone-areas` | stable | Static imported phone-area list; source/licence verification pending |
| `GET /v1/phone-areas/02` | stable | Static imported phone-area lookup; source/licence verification pending |
| `GET /v1/phone-areas/search?q=Bratislava` | stable | Static imported phone-area search; source/licence verification pending |
| `GET /v1/vehicle-registration-codes` | stable | Static legacy district-code reference; not a current plate lookup |
| `GET /v1/vehicle-registration-codes/BA` | stable | Static legacy district-code lookup; does not identify vehicles or owners |
| `GET /v1/vehicle-registration-codes/search?q=Trencin` | stable | Static legacy district-code search; does not decode full plates |
| `GET /v1/school-facility-counts` | stable | Static MŠVVaM aggregate school facility counts; not a school directory |
| `GET /v1/school-facility-counts/stats` | stable | Static aggregate totals by geography and school kind |

### Seed-backed

| Endpoint | Status | Notes |
| --- | --- | --- |
| `GET /v1/holidays/2026` | seed-backed | Static holiday dataset |
| `GET /v1/companies/{ico}` | seed-backed | Local company lookup, no live upstream calls |
| `GET /v1/ico/{ico}` | seed-backed | Alias for local company lookup |

### Partial Dataset

| Endpoint | Status | Notes |
| --- | --- | --- |
| `GET /v1/psc/81101` | partial dataset | Expanded static PSC dataset with partial geography links |
| `GET /v1/psc` | partial dataset | PSC collection surface with `limit` / `offset`; partial coverage only |
| `GET /v1/psc/search?q=...` | partial dataset | PSC search surface; partial coverage only |
| `GET /v1/psc/stats` | partial dataset | Local PSC dataset stats; PortalVS source terms are restrictive |

### Platform

| Endpoint | Status | Notes |
| --- | --- | --- |
| `/docs` | stable | Swagger UI |
| `/openapi.json` | stable | OpenAPI schema |

## PSC Collection Surface

The PSC collection routes, pagination model, and current dataset limitations remain aligned with the shipped local-data contract.

## Dataset Tooling

The repository keeps its reference data in local JSON files under `data/`.

- `data/sources.json` is the machine-readable source registry.
- `docs/import-pipeline.md` explains the offline raw -> checked-in JSON -> production runtime flow.
- `docs/data-sources.md` lists the current dataset inventory and coverage notes.
- `docs/source-compliance.md` summarizes licence, redistribution, attribution, and risk status for each production dataset.
- `docs/dataset-format.md` documents the JSON file layout and record shapes.
- `docs/research/ico-sources.md` captures the IČO/company research notes and upstream questions.
- `docs/research/source-verification-evidence.md` records retained source-verification evidence.
- `docs/research/source-licence-questions.md` contains draft clarification questions; nothing is sent automatically.
- `docs/api-status.md` lists the endpoint status categories.
- `docs/verification-backlog.md` tracks the remaining verification tasks.
- `docs/known-limitations.md` collects the current public-readiness caveats.
- `data/sources.json` and the dataset-specific research notes document source and licence verification per dataset.
- `Source/licence verification pending.` applies to any dataset whose upstream provenance is not fully confirmed.
- Runtime requests do not call upstream services; the API reads local JSON only.
- Current project versioning is pre-1.0; endpoint availability does not yet guarantee a stable `1.0.0` public contract.
- Historical internal milestones include the phone-area workbook import, legacy vehicle registration district abbreviations, and aggregate school facility counts.
- `/v1/schools` is intentionally not implemented because the confirmed MŠVVaM school-register CSV is aggregate, not per-school, data.

## Dataset Import Pipeline

The import pipeline is offline-only and defaults to dry-run.

```bash
python scripts/import_geography.py --dataset municipalities --input data/raw/portalvs-classifier-9.json --dry-run --output data/generated/municipalities.json
python scripts/import_geography.py --dataset municipalities --input data/raw/portalvs-classifier-9.csv --output data/generated/municipalities.json --write
python scripts/import_psc.py --input data/raw/psc-source.csv --output data/generated/psc.json --dry-run
python scripts/import_psc.py --input data/raw/psc-source.csv --output data/generated/psc.json --write
python scripts/import_banks.py --input data/raw/nbs-bank-directory.csv --output data/generated/banks.json --dry-run
python scripts/import_banks.py --input data/raw/nbs-bank-directory.csv --output data/generated/banks.json --write
python scripts/import_phone_areas.py --input data/raw/phone-areas.csv --output data/generated/phone_areas.json --dry-run
python scripts/import_phone_areas.py --input data/raw/phone-areas.xlsx --output data/generated/phone_areas.json --write
python scripts/import_school_facility_counts.py --input data/raw/minedu-school-facility-counts-2025-09-15.csv --output data/generated/school_facility_counts.json --dry-run
python scripts/backfill_psc_districts.py --dry-run
python scripts/backfill_psc_districts.py --write
python scripts/validate_datasets.py
python scripts/check_referential_integrity.py
```

Use `data/raw/` for source material and `data/generated/` for normalized previews. Promote generated files into `data/*.json` only after review.

## Company Lookup

Company/IČO lookup is backed by a small checked-in local seed dataset, not full RPO coverage.

- Source notes: `docs/research/ico-sources.md`
- Licence notes: `docs/research/rpo-licence.md`
- Proposed schema: `docs/dataset-format.md`
- Registry entry: `data/sources.json`
- No live upstream calls are made by the API routes.
- Personal/stakeholder fields are intentionally excluded from the public response.
- Public-readiness status is documented in `docs/api-status.md` and `docs/known-limitations.md`.

## Response Envelope

```json
{
  "data": {},
  "metadata": {
    "source": "OpenSK API",
    "lastUpdated": "YYYY-MM-DD",
    "version": "v1"
  },
  "error": null
}
```

Error responses use the same envelope with `data: null` and a structured error object.

## Examples

```bash
curl <base-url>/
curl <base-url>/v1/health
curl <base-url>/v1/psc/stats
curl <base-url>/v1/psc/search?q=Bratislava
curl <base-url>/v1/banks
curl <base-url>/v1/regions
curl <base-url>/v1/vehicle-registration-codes/BA
curl <base-url>/v1/school-facility-counts/stats
curl <base-url>/v1/companies/50158635
```

PSC source previews can expose repeated codes like this:

```json
{
  "data": {
    "psc": "81101",
    "matchCount": 2,
    "matches": [
      { "psc": "81101", "city": "Bratislava" },
      { "psc": "81101", "city": "Bratislava - mestská časť Staré Mesto" }
    ]
  },
  "metadata": {
    "source": "OpenSK API PSC import preview",
    "lastUpdated": "YYYY-MM-DD",
    "version": "v1"
  },
  "error": null
}
```

Swagger docs: `https://opensk-api.onrender.com/docs`

## Local Development

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
python -m pytest
```

## Deployment

Render is the recommended MVP host because it is simple, GitHub-based, and gives the app a public HTTPS URL. The app is still a standard FastAPI project, so it can move later to Fly.io, Koyeb, Railway, Vercel, or Cloudflare with minimal changes.

### Manual Render Setup

1. Create a new Render Web Service.
2. Connect the GitHub repository.
3. Use the Python environment.
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Smoke Tests After Deploy

```bash
curl https://opensk-api.onrender.com/
curl https://opensk-api.onrender.com/v1/health
curl https://opensk-api.onrender.com/v1/holidays/2026
curl https://opensk-api.onrender.com/v1/psc/81101
open https://opensk-api.onrender.com/docs
```

The free Render instance may sleep when idle and can cold-start on the first request.

## Data Notes

- Raw source material is handled offline and curated into the checked-in JSON datasets under `data/`.
- Production requests read those local JSON files only.
- Holiday responses currently use a static seed dataset.
- Holiday and PSC datasets use stable `lastUpdated` values for release reproducibility.
- Banks are imported from the NBS domestic payment-system identification-code directory snapshot effective `2026-05-18`; source/licence verification remains pending.
- Phone areas are imported from the telecom regulator's machine-processable workbook; licence/reuse verification remains pending.
- Vehicle registration district codes are legacy/reference data from Slov-Lex legal text; they are not reliable for current plate lookup and do not decode full licence plates.
- School facility counts are aggregate rows from the MŠVVaM `Register škôl a školských zariadení` CSV, valid as of `2025-09-15`; the API does not provide institution-level `/v1/schools` lookup.
- School aggregate responses exclude school names, addresses, directors, staff, pupils, personal emails, and phone numbers.
- IBAN validation and Slovak bank-code resolution run locally without network access.
- The PSC dataset is expanded beyond the original tiny seed-only sample, but it does not claim national coverage.
- PSC coverage and source/licence details are tracked in `docs/data-sources.md`; the dataset remains partial and may contain repeated postal-code records.
- PSC redistribution is restricted by upstream PortalVS terms, so do not present the dataset as open redistribution material.
- Imported PSC source data does not provide reliable district links, so PSC `districtCode` is backfilled locally from `municipalityCode` using verified municipality -> district mappings.
- PSC `districtCode` coverage is 100% for current local PSC records; no values are inferred from names or PSC patterns.
- PSC source rows can repeat the same postal code; the importer/preview should surface that with `matchCount` and `matches` before choosing a canonical runtime record.
- `GET /v1/psc` returns paginated PSC match records with `limit` and `offset`.
- `GET /v1/psc/search?q=...` searches PSC records by PSC prefix, municipality, and delivery post.
- `GET /v1/psc/stats` exposes local dataset totals and geography coverage.
- IČO/company work uses a local seed dataset; do not treat it as exhaustive or a full register.
- Regions cover the 8 Slovak self-governing regions and are verified against the Eurostat LAU 2025 correspondence table.
- Municipalities are sourced from PortalVS classifier 9 (`Obce`) and the checked-in dataset currently covers the 2,927 regular Slovak municipality rows used by the runtime API.
- Municipality district mappings come from PortalVS classifier 9 `code_su` and are validated against the local districts dataset.
- PortalVS source/licence verification is still pending; do not treat the municipality dataset as open redistribution material.
- Districts are imported from PortalVS classifier 10 and cover all Slovak districts; PortalVS terms may restrict reuse.
- ORSR and ŽRSR stay reference-only in research notes; this repository does not scrape them.
- Source notes live in `docs/data-sources.md`, and file format notes live in `docs/dataset-format.md`.
- Research notes for company/IČO work live in `docs/research/ico-sources.md`.
- Remaining verification tasks are tracked in `docs/verification-backlog.md`.
- Dataset compliance status is summarized in `docs/source-compliance.md`.
- Verification evidence and draft licence questions are tracked under `docs/research/`.
- Use `Source/licence verification pending.` when a dataset's upstream provenance is not fully confirmed.
- Do not assume any dataset is official government data unless the source explicitly says so.

## Contributing

Contributions are welcome, especially new data sources that can be added with clear attribution and licensing.

See `CONTRIBUTING.md` for contribution guidance.

## License

The code in this repository is licensed under MIT. See `LICENSE`.
