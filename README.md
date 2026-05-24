# OpenSK API

OpenSK API is a FastAPI service that exposes a small set of Slovak public data through a consistent JSON envelope.

No API key is required. CORS is enabled for browser clients. All responses are JSON.

## MVP Status

| Endpoint | Status | Notes |
|---|---|---|
| `GET /` | Working | Project info |
| `GET /v1/health` | Working | Health check |
| `GET /v1/holidays/2026` | Working | Static holiday dataset |
| `GET /v1/psc/81101` | Working | Static PSC seed dataset |
| `/docs` | Working | Swagger UI |
| `/openapi.json` | Working | OpenAPI schema |

## Implemented Endpoints

| Endpoint | Description |
|---|---|
| `GET /` | Project metadata and docs link |
| `GET /v1/health` | Basic service health |
| `GET /v1/holidays/{year}` | Slovak public holidays by year |
| `GET /v1/psc/{psc}` | Slovak postal code lookup |

## Planned Endpoints

| Endpoint | Description |
|---|---|
| `GET /v1/banks` | Slovak bank list |
| `GET /v1/companies/{ico}` | Company lookup |
| `GET /v1/iban/validate/{iban}` | IBAN validation |
| `GET /v1/municipalities` | Municipality data |

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

## Examples

```bash
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/v1/health
curl http://127.0.0.1:8000/v1/holidays/2026
curl http://127.0.0.1:8000/v1/psc/81101
```

Swagger docs: `http://127.0.0.1:8000/docs`

## Local Development

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
python -m pytest
```

## Data Notes

- Holiday and PSC responses currently use static seed datasets.
- The PSC dataset is intentionally limited and does not claim national coverage.
- Dataset source and license attribution must be checked per dataset before adding or publishing new data.
- Do not assume any dataset is official government data unless the source explicitly says so.

## Contributing

Contributions are welcome, especially new data sources that can be added with clear attribution and licensing.

See `CONTRIBUTING.md` for contribution guidance.

## License

The code in this repository is licensed under MIT. See `LICENSE`.
