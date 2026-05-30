# OpenSK API

OpenSK API is a FastAPI service that exposes a small set of Slovak public data through a consistent JSON envelope.

Status: MVP release `v0.6.0`.

No API key is required. CORS is enabled for browser clients. All responses are JSON.

## MVP Status

| Endpoint | Status | Notes |
| --- | --- | --- |
| `GET /` | Working | Project info |
| `GET /v1/banks` | Working | Static bank list |
| `GET /v1/banks/1100` | Working | Static bank lookup |
| `GET /v1/iban/validate/SK...` | Working | Slovak IBAN validation |
| `GET /v1/health` | Working | Health check |
| `GET /v1/holidays/2026` | Working | Static holiday dataset |
| `GET /v1/regions` | Working | Static regions dataset |
| `GET /v1/districts` | Working | Static districts seed dataset |
| `GET /v1/municipalities` | Working | Static municipalities seed dataset |
| `GET /v1/psc/81101` | Working | Static PSC seed dataset with geography links |
| `/docs` | Working | Swagger UI |
| `/openapi.json` | Working | OpenAPI schema |

## Implemented Endpoints

| Endpoint | Description |
| --- | --- |
| `GET /` | Project metadata and docs link |
| `GET /v1/banks` | List Slovak banks |
| `GET /v1/banks/{code}` | Slovak bank lookup |
| `GET /v1/iban/validate/{iban}` | Slovak IBAN validation |
| `GET /v1/health` | Basic service health |
| `GET /v1/holidays/{year}` | Slovak public holidays by year |
| `GET /v1/regions` | Slovak regions list |
| `GET /v1/regions/{code}` | Slovak region lookup |
| `GET /v1/districts` | Slovak districts list, optional `regionCode` filter |
| `GET /v1/districts/{code}` | Slovak district lookup |
| `GET /v1/municipalities` | Slovak municipalities list, optional `regionCode` and `districtCode` filters |
| `GET /v1/municipalities/{code}` | Slovak municipality lookup |
| `GET /v1/psc/{psc}` | Slovak postal code lookup, optional `include=geography` |

## Planned Endpoints

| Endpoint | Description |
| --- | --- |
| `GET /v1/companies/{ico}` | Company lookup |


## Dataset Tooling

The repository keeps its reference data in local JSON files under `data/`.

- `data/sources.json` is the machine-readable source registry.
- `docs/import-pipeline.md` explains the offline raw -> checked-in JSON -> production runtime flow.
- `docs/data-sources.md` lists the current dataset inventory and coverage notes.
- `docs/dataset-format.md` documents the JSON file layout and record shapes.
- `Source/licence verification pending.` applies to any dataset whose upstream provenance is not fully confirmed.
- Runtime requests do not call upstream services; the API reads local JSON only.
- No new public endpoints were added in `v0.6.0`.

## Dataset Import Pipeline

The import pipeline is offline-only and defaults to dry-run.

```bash
python scripts/import_geography.py --dataset municipalities --input data/raw/example.csv --dry-run
python scripts/import_geography.py --dataset municipalities --input data/raw/example.csv --output data/generated/municipalities.json --write
python scripts/validate_datasets.py
python scripts/check_referential_integrity.py
```

Use `data/raw/` for source material and `data/generated/` for normalized previews. Promote generated files into `data/*.json` only after review.

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
curl http://opensk-api.onrender.com/
curl http://opensk-api.onrender.com/v1/banks
curl http://opensk-api.onrender.com/v1/banks/1100
curl http://opensk-api.onrender.com/v1/iban/validate/SK0009000000000000000001
curl http://opensk-api.onrender.com/v1/health
curl http://opensk-api.onrender.com/v1/holidays/2026
curl http://opensk-api.onrender.com/v1/regions
curl http://opensk-api.onrender.com/v1/regions/SK010
curl http://opensk-api.onrender.com/v1/districts
curl http://opensk-api.onrender.com/v1/districts?regionCode=SK010
curl http://opensk-api.onrender.com/v1/municipalities
curl http://opensk-api.onrender.com/v1/municipalities?districtCode=SK0101
curl http://opensk-api.onrender.com/v1/psc/81101
curl http://opensk-api.onrender.com/v1/psc/81101?include=geography
```

Swagger docs: `http://opensk-api.onrender.com/docs`

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
- Holiday and PSC responses currently use static seed datasets.
- Holiday and PSC datasets use stable `lastUpdated` values for release reproducibility.
- Banks use a small static seed dataset and IBAN validation runs locally without network access.
- The bank dataset is intentionally incomplete and should not be presented as exhaustive.
- The PSC dataset is intentionally limited and does not claim national coverage.
- PSC geography links are only present where mappings are available in the local seed data.
- PSC is still a seed dataset, not a full national postal code source.
- Regions are complete for the 8 Slovak self-governing regions.
- Districts are seed-only in this release.
- Municipalities are seed-only in this release.
- Geography datasets include provisional seed identifiers where not fully verified.
- Source notes live in `docs/data-sources.md`, and file format notes live in `docs/dataset-format.md`.
- Use `Source/licence verification pending.` when a dataset's upstream provenance is not fully confirmed.
- Do not assume any dataset is official government data unless the source explicitly says so.

## Contributing

Contributions are welcome, especially new data sources that can be added with clear attribution and licensing.

See `CONTRIBUTING.md` for contribution guidance.

## License

The code in this repository is licensed under MIT. See `LICENSE`.
