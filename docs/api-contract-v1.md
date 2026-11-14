# Candidate v1 API Contract

Status: pre-1.0 candidate. This document describes the intended compatibility surface for a future `1.0.0`; it is not a permanent compatibility promise until `1.0.0` is released.

## Namespace And Versions

- Public API routes use the `/v1` namespace.
- Response `metadata.version` is the API contract marker and remains `"v1"`.
- Project SemVer, currently `0.23.15`, is separate from the `/v1` API namespace.
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

`data` may be an object, array, or collection wrapper depending on endpoint history. `metadata.source` should identify the local dataset or service source. `metadata.lastUpdated` is the ISO freshness date of the underlying dataset; since 0.23.1 it is explicitly `null` for root and error responses where no dataset is involved. **Health is the operational exception**: its live timestamp changes per request and its metadata uses today's UTC date, not dataset freshness; it is `no-store`.

Standard metadata keys are `source`, `lastUpdated`, `version`; **dataset-specific
metadata MAY add provenance fields** without replacing them or requiring every
endpoint to adopt source-specific fields. Since 0.23.8, bank/IBAN success metadata
adds `sourceVersion`, `sourceEffectiveDate`, `sourceDownloadedAt`, `sourceUrl`,
`sourceFileUrl`, `sourceSha256`, `sourceBytes`, `termsUrl`, `attribution`,
`transformation`, all from the local NBS dataset. Effective date determines
freshness and cacheable bank-route Last-Modified, not download date. IBAN
validation is `no-store` with no Last-Modified or ETag despite carrying local
bank provenance. NBS supplies Slovak bank resolution;
OpenSK performs ISO checksum validation. Bank list data stays an array, lookup
stays an object; no provenance route added. Generic error metadata is unchanged.

## Error Envelope

Application-level errors should use this envelope:

```json
{
  "data": null,
  "metadata": {
    "source": "OpenSK API",
    "lastUpdated": null,
    "version": "v1"
  },
  "error": {
    "code": "INVALID_FORMAT",
    "message": "English message",
    "messageSk": "Slovak message"
  }
}
```

Manually validated malformed route/query values return 400. Existing framework integer validation (holiday year path and procurement year query) retains 422, wrapped in this same envelope rather than FastAPI's default `detail` object. Unknown but valid resource identifiers return 404 (absence from the local snapshot, not legal invalidity). Dataset-unavailable 503 is implemented only by company/IČO routes. Dates outside verified holiday coverage on business-day routes return 400 with code `UNSUPPORTED_YEAR`.

## HTTP Caching Semantics

Cacheable successful GET responses have a strong body-hash `ETag`, semantic per-dataset `Last-Modified` where applicable and conditional 304s with an empty body. `If-None-Match` uses weak comparison and takes precedence by header presence, even for a nonmatch. Cache-Control categories are static 86400, search 900, meta/latest-FX 3600; **health and IBAN validation are `no-store` with no validators or 304s**. Revalidation saves transfer, not endpoint computation/serialization. See [HTTP caching](http-caching.md) for the normative policy. Per-IP rate limiting (100 requests/60 s, 429 + `RATE_LIMITED`, `Retry-After`, `X-RateLimit-*` headers) is implemented per [rate-limiting contract](rate-limiting-contract.md); `/v1/health` is exempt.

## Pagination And Search

Filterable collection endpoints use `limit` and `offset` where pagination is implemented.

- List defaults are `limit=100`, `offset=0` for PSC, phone areas, vehicle codes, school counts and procurement; ITMS21+ projects and election results use `limit=50`, `offset=0`.
- Search defaults are currently `limit=50`, `offset=0`.
- Maximums are `500` for the legacy list-style endpoints and `200` for searches; those endpoints allow zero limits and offsets `0–1000000000`. ITMS21+ lists allow limits **`1–200`** and election results **`1–100`**; both allow offsets **`0–2147483647`**. Numeric validation is bounded and uses ASCII decimal digits, not arbitrary Unicode numeric characters.
- Paginated responses use `{ "items": [], "count": 0, "total": 0, "limit": 100, "offset": 0 }`.

Older small geography/bank/holiday endpoints return arrays directly and are candidates to preserve for compatibility unless changed before `1.0.0`.

## Runtime Architecture

Runtime routes read checked-in local JSON datasets or perform local validation only. Imports, source downloads, and transformations happen offline through scripts. No public request path should call upstream government or third-party services.

## Endpoint Naming

- Collection routes use plural nouns where practical.
- Static `/search` and `/stats` routes must be registered before dynamic `/{code}` routes.
- `/v1/ico/{ico}` is retained as an intentional compatibility alias for `/v1/companies/{ico}`.

## Candidate Stable Route Groups

The `1.0.0` candidate stable contract is scoped in `docs/1-0-scope.md`.

Stable-candidate routes include service metadata/health, the curated source catalogue, IBAN validation, regions, banks, phone areas, bounded business-day utilities and local ECB reference rates, subject to retained evidence/conditions.

Limited stable-candidate routes include districts, municipalities, PSC, the bounded statutory calendar, seed-backed companies/IČO, vehicle registration codes, school facility counts, TED_PARTIAL procurement notices, title-free positively reviewed legal-entity ITMS21+ references and selected NRSR2023 aggregate results only with their documented limitations and required source-compliance fixes. Together these groups cover the current **42 GET operations**, not a promise of complete official coverage or a released 1.0 contract.

Research-only domains with no stable routes include VAT, ŽRSR/trade registrations, streets/Register adries, healthcare facilities, institution-level schools, court decisions, and national statistics endpoints.

Routes whose source-compliance inclusion is unresolved before final `1.0.0` must be excluded from the stable contract or documented as experimental/pre-1.0 before release.

## Partial Datasets

Partial, seed-backed, historical/reference, and aggregate-only datasets may be stable API contracts if coverage and limitations are explicit. A stable endpoint does not imply exhaustive official coverage.

## Backwards Compatibility Expectations

0.23.12 corrects `/v1/psc/{psc}` for grouped PSC records: `matchCount` now counts logical flat matches and `matches` contains those flat records, consistent with list/search behavior. Primary fields come from the existing deterministic match ordering over normalized records. Optional geography resolves each match and the same primary. The underlying dataset, source provenance and coverage are unchanged. This is a pre-1.0 correctness fix, **not a data/source migration**; no successor PSC semantics are introduced. PSC remains a partial historical local lookup, not address validation or municipality-wide validity. Full [OpenAPI/compatibility audit](research/openapi-contract-audit.md).

After `1.0.0`, compatible changes include additive response fields, new optional query parameters, and new endpoints. Breaking response-shape changes, route removals, renamed fields, or changed error semantics should require a future `/v2` or a documented deprecation process.
