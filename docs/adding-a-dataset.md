# Adding a New Dataset Domain

The minimum-gates checklist for adding any new dataset/domain to OpenSK. Each gate must be documented before merge; skipped gates mean research-only status.

1. **Authoritative source** — an official primary source is identified (no scraping human-facing portals).
2. **Machine-readable acquisition** — a documented reproducible download/export/API exists (CSV/JSON/XML/OpenAPI), acquired offline into `data/raw/`.
3. **Reuse/licence** — reuse, caching, transformation, and redistribution terms are verified and retained in `docs/research/source-verification-evidence.md`. Unresolved means the dataset cannot ship as production.
4. **Privacy** — personal data (names, contacts, natural persons, sensitive identifiers) is excluded or the domain is rejected; see `docs/privacy-review.md`.
5. **Stable identifiers** — records have deterministic stable IDs suitable for detail routes.
6. **Local normalization** — an offline `scripts/import_*.py` (dry-run-first) normalizes source data into the checked-in JSON shape.
7. **Validation** — `scripts/validate_datasets.py` covers the new dataset (shape, duplicates, forbidden fields).
8. **Referential integrity** — links to geography/dataset codes validated in `scripts/check_referential_integrity.py` where relevant.
9. **Source metadata** — a `data/sources.json` entry with status, coverage, source URL, licence status, attribution, lastChecked; the public `/v1/sources` projection picks it up via the curated mapping in `services/sources_service.py`.
10. **Tests** — dataset validation tests, service tests, route tests, smoke-test extension; all offline, no network.
11. **No runtime upstream dependency** — API routes read the checked-in local JSON only.

After the gates pass: add the router with the standard envelope (`metadata.lastUpdated` = dataset date), register OpenAPI tags in `main.py`, extend `docs/api-status.md`, `README.md`, `CHANGELOG.md`, and `docs/source-catalogue.md` curated values.
