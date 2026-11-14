# Development Plan

> **Archived MVP plan — not instructions for the current branch.** This file
> preserves the original foundation checklist and architecture intentions.
> For current 0.23.15 decisions, use the [roadmap](docs/roadmap.md),
> [API contract](docs/api-contract-v1.md), [release readiness](docs/release-readiness.md)
> and [research index](docs/research/README.md). Historical checklist items below
> do not certify current test or deployment status.

## MVP Checklist
- `GET /v1/health` works.
- `GET /v1/holidays/2026` works.
- `GET /v1/psc/81101` works.
- `/docs` works.
- README has real `curl` examples.
- Tests pass.
- Every normal API response includes `metadata.source` and `metadata.lastUpdated`.
- The deployed URL is public.

## Architecture Rules
- Keep FastAPI.
- Keep all public endpoints under `/v1`.
- No authentication for public read-only endpoints.
- Enable CORS globally.
- Use a consistent response envelope:

```json
{
  "data": "...",
  "metadata": {
    "source": "...",
    "lastUpdated": "YYYY-MM-DD",
    "version": "v1"
  },
  "error": null
}
```

- Errors should be structured and include English and Slovak where reasonable.
- Prefer static JSON datasets for MVP.
- Do not add scraping yet.
- Do not add database infrastructure yet unless absolutely necessary.
- Avoid large rewrites.
