# Candidate v1 API Contract

Status: pre-1.0 candidate. This document describes the intended compatibility surface for a future `1.0.0`; it is not a permanent compatibility promise until `1.0.0` is released.

## Namespace And Versions

- Public API routes use the `/v1` namespace.
- Response `metadata.version` is the API contract marker and remains `"v1"`.
- Project SemVer, such as `0.13.0`, is separate from the `/v1` API namespace.
- Root metadata exposes both project version and API namespace fields.

## Success Envelope

Successful API responses use this envelope:

```json
{
  "data": {},
  "metadata": {
    "source": "OpenSK API static dataset label",
    "lastUpdated": "YYYY-MM-DD",
    "version": "v1"
  },
  "error": null
}
```

`data` may be an object, array, or collection wrapper depending on endpoint history. `metadata.source` should identify the local dataset or service source. `metadata.lastUpdated` should be present when the source has a known update date.

## Error Envelope

Application-level errors should use this envelope:

```json
{
  "data": null,
  "metadata": {
    "source": "OpenSK API",
    "lastUpdated": "YYYY-MM-DD",
    "version": "v1"
  },
  "error": {
    "code": "INVALID_FORMAT",
    "message": "English message",
    "messageSk": "Slovak message"
  }
}
```

Malformed route or query values return 400. Unknown but valid resource identifiers return 404. Dataset-unavailable responses should use 503 only when a required local dataset cannot be loaded.

## Pagination And Search

Filterable collection endpoints use `limit` and `offset` where pagination is implemented.

- List defaults are currently `limit=100`, `offset=0`.
- Search defaults are currently `limit=50`, `offset=0`.
- Current maximums are `500` for list-style endpoints and `200` for search-style endpoints.
- Paginated responses use `{ "items": [], "count": 0, "total": 0, "limit": 100, "offset": 0 }`.

Older small geography/bank/holiday endpoints return arrays directly and are candidates to preserve for compatibility unless changed before `1.0.0`.

## Runtime Architecture

Runtime routes read checked-in local JSON datasets or perform local validation only. Imports, source downloads, and transformations happen offline through scripts. No public request path should call upstream government or third-party services.

## Endpoint Naming

- Collection routes use plural nouns where practical.
- Static `/search` and `/stats` routes must be registered before dynamic `/{code}` routes.
- Aliases such as `/v1/ico/{ico}` are intentional compatibility routes and should remain documented if retained for `1.0.0`.

## Partial Datasets

Partial, seed-backed, historical/reference, and aggregate-only datasets may be stable API contracts if coverage and limitations are explicit. A stable endpoint does not imply exhaustive official coverage.

## Backwards Compatibility Expectations

After `1.0.0`, compatible changes include additive response fields, new optional query parameters, and new endpoints. Breaking response-shape changes, route removals, renamed fields, or changed error semantics should require a future `/v2` or a documented deprecation process.
