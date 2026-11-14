# OpenSK API

**One consistent developer interface to Slovakia's fragmented public data.**

Look up administrative geography, postal codes and bank codes; validate a Slovak IBAN, calculate business days, or read historical ECB reference rates. FastAPI serves checked-in, normalized snapshots: requests never depend on an upstream service.

**[Live API](https://opensk-api.onrender.com)** · **[Interactive docs](https://opensk-api.onrender.com/docs)** · **[Five-minute quickstart](docs/quickstart.md)** · **[OpenAPI JSON](https://opensk-api.onrender.com/openapi.json)**

```bash
curl "https://opensk-api.onrender.com/v1/municipalities/528595"
```

## Status and important limitations

**Pre-1.0: not a complete or live official register.** The current project version is single-sourced in [`version.py`](version.py) and returned by `GET /`. The API namespace and response metadata version remain `/v1` and `v1`; they are independent of the project version. There are 42 GET operations.

No API key is required. Browser clients are supported through CORS. On Render, an application limiter allows 100 requests per 60 seconds per client IP; health checks are exempt. Free-tier cold starts can delay the first request.

**MIT covers the code, not all source data.** Inspect [`/v1/sources`](https://opensk-api.onrender.com/v1/sources) and the [compliance review](docs/source-compliance.md) before reusing a dataset. PortalVS-derived districts, municipalities and PSC still have unresolved redistribution rights; public promotion remains gated. A source-owner redirect or an unanswered clarification request is not permission.

## What you can use

| API group | Scope and key limitation |
| --- | --- |
| `/v1/regions`, `/v1/districts`, `/v1/municipalities` | 8 regions, 79 districts and 2,927 municipality records. Current district/municipality bytes remain PortalVS-derived. |
| `/v1/psc` | Partial historical postal-code lookup, search and stats; not address validation. One code can have multiple administrative matches. |
| `/v1/banks`, `/v1/iban/validate/{iban}` | NBS domestic bank snapshot v226, effective 2026-10-08. IBAN validation checks Slovak structure and checksum, not account existence; responses are `no-store`. |
| `/v1/holidays/{year}`, `/v1/business-days/*` | Statutory calendar verified for 2024–2030. State-holiday and day-of-rest flags distinguish working holidays. |
| `/v1/exchange-rates/*` | Local ECB EUR reference-rate history since 1999-01-04. Exact publication dates, decimal strings, informational use only; not live prices. |
| `/v1/companies/{ico}`, `/v1/ico/{ico}` | Four checked-in seed organizations, not full RPO coverage. |
| `/v1/phone-areas` | Regulator numbering snapshot; three local geography links remain unmatched. |
| `/v1/vehicle-registration-codes` | Historical district abbreviations, not current plate or vehicle lookup. |
| `/v1/school-facility-counts` | Aggregate facility counts, not an institution-level school directory. |
| `/v1/procurement-notices` | 100-record `TED_PARTIAL` snapshot, not complete national ÚVO coverage. |
| `/v1/eu-funds/projects` | 4,561 privacy-reviewed ITMS21+ project references; partial scope, no project titles or unsafe beneficiaries. |
| `/v1/elections` | Definitive NRSR2023 selected unit summaries and national parties; no candidate, precinct or municipality-party records. Small-area contextual-inference risk remains. |
| `/v1/sources` | Public provenance, freshness, coverage and reuse conditions for 20 registered domains, including research-only domains. |

See the [route/status inventory](docs/api-status.md) or interactive docs for every operation and parameter. Lists do not all use the same pagination shape. A `404` means absent from the local snapshot, not necessarily legally invalid.

## Examples

```bash
curl "https://opensk-api.onrender.com/v1/psc/01001?include=geography"
curl "https://opensk-api.onrender.com/v1/banks/1100"
curl "https://opensk-api.onrender.com/v1/business-days/check?date=2026-10-08"
curl "https://opensk-api.onrender.com/v1/exchange-rates/latest?currency=USD"
curl "https://opensk-api.onrender.com/v1/elections/NRSR2023/results?municipalityCode=528595"
```

Responses use a consistent JSON envelope:

```json
{
  "data": {},
  "metadata": {
    "source": "OpenSK API",
    "lastUpdated": null,
    "version": "v1"
  },
  "error": null
}
```

Dataset responses carry their actual freshness date; root/error metadata uses `null`. Operational health is the documented current-date exception. Errors use `data: null` and a structured error. Cacheable responses support ETag revalidation; account-bearing IBAN responses do not. [Response contract](docs/api-contract-v1.md) · [HTTP caching](docs/http-caching.md).

## Architecture

```text
Official source → offline acquisition/import → reviewed data/*.json
                                                  ↓
                                     cached local services
                                                  ↓
                                         FastAPI routers
```

- `routers/`: request validation and HTTP contracts.
- `services/`: local loading, lookups, filtering and utilities.
- `schemas/`: typed responses, examples and dataset contracts.
- `scripts/`: offline acquisition, normalization, validation and benchmarks.
- `tests/`: API contracts, failure paths, privacy gates and dataset integrity.
- `docs/`: developer guides and source/decision evidence.

No runtime scraping, database, API key or upstream network dependency is required. New data goes through explicit source, reuse, privacy and validation gates rather than automatic publication.

## Local development

Use **Python 3.12.16**, matching [`.python-version`](.python-version), CI and the Render runtime declaration.

### Bash (Linux/macOS)

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes -r requirements-dev.txt
python -m pytest -q
uvicorn main:app --reload --no-access-log
```

### PowerShell (Windows)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --require-hashes -r requirements-dev.txt
python -m pytest -q
uvicorn main:app --reload --no-access-log
```

Open **http://127.0.0.1:8000/docs**. The server occupies that terminal; use another activated terminal for further checks. If PowerShell activation is restricted, call `.\.venv\Scripts\python.exe` directly instead of changing system execution policy.

Production installs only the hash-locked `requirements.txt`; development dependencies are separate. [Contribution and dependency-update workflow](CONTRIBUTING.md).

## Data maintenance and documentation

- [Dataset inventory and coverage](docs/data-sources.md)
- [Offline import pipeline](docs/import-pipeline.md) and [dataset format](docs/dataset-format.md)
- [Adding a dataset](docs/adding-a-dataset.md)
- [Source compliance](docs/source-compliance.md), [privacy review](docs/privacy-review.md) and [known limitations](docs/known-limitations.md)
- [Election scope/refresh](docs/elections.md) and [EU-funds scope/refresh](docs/eu-funds.md)
- [Research index: current decisions versus historical records](docs/research/README.md)
- [Roadmap](docs/roadmap.md), [release readiness](docs/release-readiness.md) and [versioning](docs/versioning.md)
- [Changelog](CHANGELOG.md)

Imports default to dry-run. Keep source captures in the documented private/raw location and normalized previews under `data/generated/`; review dataset diffs before promotion. Some sources require manual acquisition or have unresolved rights. Do not automate those sources merely because a URL is available.

## Deployment

[`render.yaml`](render.yaml) defines a standard Python/ASGI service with health checks and checks-passed deployment gating:

```bash
python -m pip install --require-hashes -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port "$PORT" --no-access-log
```

Apply the Blueprint configuration and require the CI check through GitHub repository rules; local files alone do not configure existing dashboard settings. Other ASGI-compatible Python hosts are possible, but serverless/edge runtimes can require packaging and lifecycle changes.

Uvicorn access logs are disabled to avoid logging account identifiers in IBAN paths. This does not control reverse-proxy/CDN logs; their retention and redaction require a separate hosting review. Do not submit real account identifiers in public bug reports.

After deployment from the intended commit:

```bash
python scripts/smoke_test.py --base-url https://opensk-api.onrender.com --expect-rate-limit
```

## Contributing and security

[Contributions](CONTRIBUTING.md) are welcome, especially well-evidenced source and data improvements. Follow the [Code of Conduct](CODE_OF_CONDUCT.md). Report sensitive issues privately using [the security policy](SECURITY.md).

## License

Code: [MIT](LICENSE). Data: the individual source terms, attribution and limitations recorded in `/v1/sources` and the compliance documentation. OpenSK is not an official government service and does not imply publisher endorsement.
