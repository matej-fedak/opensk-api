# Development Plan

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

## Commit Rules
- Work on `mvp-foundation`.
- Keep commits small and logical.
- After each logical block, run tests or import checks.
- Inspect the diff before committing.
- Commit message style:
  - `chore: ...` for planning and maintenance.
  - `feat: ...` for endpoint work.
  - `test: ...` for test-only changes.
