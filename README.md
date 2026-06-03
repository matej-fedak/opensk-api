# OpenSK API

OpenSK API is a FastAPI service that exposes a small set of Slovak public data through a consistent JSON envelope.

Status: research milestone `v1.0.0-rc.1`.

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
| `GET /v1/psc/81101` | Working | Expanded static PSC dataset with geography links |
| `GET /v1/psc` | Working | PSC collection surface with `limit` / `offset` pagination |
| `GET /v1/psc/search?q=...` | Working | PSC search surface |
| `GET /v1/psc/stats` | Working | PSC dataset stats |
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
| `GET /v1/psc` | Slovak postal code list/filter endpoint with `limit` and `offset` |
| `GET /v1/psc/search` | Slovak postal code search endpoint |
| `GET /v1/psc/stats` | Slovak postal code dataset statistics |
| `GET /v1/psc/{psc}` | Slovak postal code lookup, optional `include=geography` |

## PSC Collection Surface

The `v1.0.0-rc.1` docs cover the PSC collection routes and pagination model.

| Endpoint | Notes |
| --- | --- |
| `GET /v1/psc` | PSC collection list, paginated with `limit` and `offset` |
| `GET /v1/psc/search?q=Bratislava` | PSC search by `q` |
| `GET /v1/psc/stats` | PSC dataset statistics |

## Dataset Tooling

The repository keeps its reference data in local JSON files under `data/`.

- `data/sources.json` is the machine-readable source registry.
- `docs/import-pipeline.md` explains the offline raw -> checked-in JSON -> production runtime flow.
- `docs/data-sources.md` lists the current dataset inventory and coverage notes.
- `docs/dataset-format.md` documents the JSON file layout and record shapes.
- `docs/research/ico-sources.md` captures the IČO/company research notes and upstream questions.
- `Source/licence verification pending.` applies to any dataset whose upstream provenance is not fully confirmed.
- Runtime requests do not call upstream services; the API reads local JSON only.
- `v1.0.0-rc.1` documents the PSC collection surface, pagination, stats/search examples, and the company research prototype notes.

## Dataset Import Pipeline

The import pipeline is offline-only and defaults to dry-run.

```bash
python scripts/import_geography.py --dataset municipalities --input data/raw/EU-27-LAU-2025-NUTS-2024.xlsx --dry-run
python scripts/import_geography.py --dataset municipalities --input data/raw/EU-27-LAU-2025-NUTS-2024.xlsx --output data/generated/municipalities.json --write
python scripts/import_psc.py --input data/raw/psc-source.csv --output data/generated/psc.json --dry-run
python scripts/import_psc.py --input data/raw/psc-source.csv --output data/generated/psc.json --write
python scripts/validate_datasets.py
python scripts/check_referential_integrity.py
```

Use `data/raw/` for source material and `data/generated/` for normalized previews. Promote generated files into `data/*.json` only after review.

## Upcoming: IČO/company lookup research

Company/IČO work is still prototype-only. No public company endpoint is shipped yet.

- Source notes: `docs/research/ico-sources.md`
- Proposed schema: `docs/dataset-format.md`
- Registry entry: `data/sources.json`

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
curl http://opensk-api.onrender.com/v1/psc?limit=25&offset=0
curl "http://opensk-api.onrender.com/v1/psc/search?q=Bratislava"
curl http://opensk-api.onrender.com/v1/psc/stats
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
- Holiday responses currently use a static seed dataset.
- Holiday and PSC datasets use stable `lastUpdated` values for release reproducibility.
- Banks use a small static seed dataset and IBAN validation runs locally without network access.
- The bank dataset is intentionally incomplete and should not be presented as exhaustive.
- The PSC dataset is expanded beyond the original tiny seed-only sample, but it still does not claim national coverage.
- The checked-in PSC file currently covers 5 postal codes and only partially links geography.
- PSC source/licence verification is still pending, so do not present the dataset as official or redistributable without checking the upstream terms.
- Imported PSC data currently has `districtCode: null`; that field is unavailable in the imported source data.
- PSC source rows can repeat the same postal code; the importer/preview should surface that with `matchCount` and `matches` before choosing a canonical runtime record.
- `GET /v1/psc` returns paginated PSC match records with `limit` and `offset`.
- `GET /v1/psc/search?q=...` searches PSC records by PSC prefix, municipality, and delivery post.
- `GET /v1/psc/stats` exposes local dataset totals and geography coverage.
- IČO/company work is research-only; do not treat it as a shipped API surface.
- Regions are complete for the 8 Slovak self-governing regions and are verified against the Eurostat LAU 2025 correspondence table.
- Municipalities are expanded from the Eurostat LAU 2025 workbook, but district codes remain null because that source does not provide district mappings.
- Districts are still seed-only and the district-level source remains unverified.
- Source notes live in `docs/data-sources.md`, and file format notes live in `docs/dataset-format.md`.
- Research notes for company/IČO work live in `docs/research/ico-sources.md`.
- Use `Source/licence verification pending.` when a dataset's upstream provenance is not fully confirmed.
- Do not assume any dataset is official government data unless the source explicitly says so.

## Contributing

Contributions are welcome, especially new data sources that can be added with clear attribution and licensing.

See `CONTRIBUTING.md` for contribution guidance.

## License

The code in this repository is licensed under MIT. See `LICENSE`.
