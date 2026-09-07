# OpenSK API

OpenSK API is a FastAPI service that exposes a small set of Slovak public data through a consistent JSON envelope.

Status: `v1.3.0` municipality district mapping release.

`v1.0.0` was the first stable seed-backed public API release. `v1.0.1` was a patch cleanup release. `v1.1.0` improved source metadata and verification coverage. `v1.2.0` expanded the district dataset. `v1.3.0` populates municipality district mappings without adding endpoints; PortalVS reuse remains pending.

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

### Seed-backed

| Endpoint | Status | Notes |
| --- | --- | --- |
| `GET /v1/banks` | seed-backed | Static bank list |
| `GET /v1/banks/1100` | seed-backed | Static bank lookup |
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

The `v1.2.0` docs keep the PSC collection routes, pagination model, and current dataset limitations aligned with the shipped release.

## Dataset Tooling

The repository keeps its reference data in local JSON files under `data/`.

- `data/sources.json` is the machine-readable source registry.
- `docs/import-pipeline.md` explains the offline raw -> checked-in JSON -> production runtime flow.
- `docs/data-sources.md` lists the current dataset inventory and coverage notes.
- `docs/dataset-format.md` documents the JSON file layout and record shapes.
- `docs/research/ico-sources.md` captures the IČO/company research notes and upstream questions.
- `docs/api-status.md` lists the endpoint status categories.
- `docs/verification-backlog.md` tracks the remaining verification tasks.
- `docs/known-limitations.md` collects the current public-readiness caveats.
- `data/sources.json` and the dataset-specific research notes document source and licence verification per dataset.
- `Source/licence verification pending.` applies to any dataset whose upstream provenance is not fully confirmed.
- Runtime requests do not call upstream services; the API reads local JSON only.
- `v1.3.0` is the municipality mapping pass: no new endpoints, just municipality district enrichment and validation updates.

## Dataset Import Pipeline

The import pipeline is offline-only and defaults to dry-run.

```bash
python scripts/import_geography.py --dataset municipalities --input data/raw/portalvs-classifier-9.json --dry-run --output data/generated/municipalities.json
python scripts/import_geography.py --dataset municipalities --input data/raw/portalvs-classifier-9.csv --output data/generated/municipalities.json --write
python scripts/import_psc.py --input data/raw/psc-source.csv --output data/generated/psc.json --dry-run
python scripts/import_psc.py --input data/raw/psc-source.csv --output data/generated/psc.json --write
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
- Banks use a small static seed dataset and IBAN validation runs locally without network access.
- The bank dataset is intentionally incomplete and should not be presented as exhaustive.
- The PSC dataset is expanded beyond the original tiny seed-only sample, but it does not claim national coverage.
- PSC coverage and source/licence details are tracked in `docs/data-sources.md`; the dataset remains partial and may contain repeated postal-code records.
- PSC redistribution is restricted by upstream PortalVS terms, so do not present the dataset as open redistribution material.
- Imported PSC data currently has `districtCode: null`; that field is unavailable in the imported source data.
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
- Use `Source/licence verification pending.` when a dataset's upstream provenance is not fully confirmed.
- Do not assume any dataset is official government data unless the source explicitly says so.

## Contributing

Contributions are welcome, especially new data sources that can be added with clear attribution and licensing.

See `CONTRIBUTING.md` for contribution guidance.

## License

The code in this repository is licensed under MIT. See `LICENSE`.
