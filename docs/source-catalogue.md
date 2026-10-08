# Public Source Catalogue (`/v1/sources`)

`GET /v1/sources` and `GET /v1/sources/{id}` expose a **curated public projection** of the internal source registry (`data/sources.json`). The registry contains maintainer workflow material; the public surface deliberately exposes only consumer-relevant provenance. The registry file is never served verbatim.

## Public Schema

Each entry has the typed shape (`schemas/sources.py`):

```json
{
  "id": "procurementNotices",
  "name": "Public procurement notices",
  "status": "production",
  "coverage": "partial",
  "source": { "name": "TED Search API Slovak-buyer procurement notice snapshot", "url": "https://..." },
  "licence": { "status": "identified", "name": "TED / Publications Office reuse terms", "termsUrl": "https://ted.europa.eu/en/legal-notice" },
  "attribution": "Source: TED (Tenders Electronic Daily), EU Open Data Portal; ...",
  "lastUpdated": "2026-09-29",
  "lastChecked": "2026-09-29",
  "updateCadence": "manual",
  "limitations": ["Includes only Slovak-buyer notices in the current 100-record TED snapshot.", "Not the national UVO procurement register."]
}
```

All keys are always present; unavailable values are explicit `null`, never omitted.

## Public vs Internal Field Boundary

| Internal registry field | Public exposure |
| --- | --- |
| `status`, `coverage` (internal vocabulary) | mapped to public enums |
| `sourceName`, `sourceUrl` | `source.name`, `source.url` |
| `licence` (long text) | replaced by curated `licence.name` or `null` |
| `licenceStatus` (long text) | mapped to `licence.status` |
| `termsUrl` | exposed only when it is a real URL ("pending" becomes `null`) |
| `attribution` | passed through |
| `lastChecked`, `lastUpdated`, `updateCadence` | exposed (`updateCadence` curated per id) |
| **Internal-only, never exposed** | `redistributionStatus`, `riskLevel`, `nextAction`, `notes`, `sourceFileUrl`, `sourceDocumentationUrl`, `candidateSourceUrls`, `updateFrequency` |

## Public Status Vocabulary

`status` (how available the domain is via OpenSK):

- `production` — served from a checked-in runtime dataset
- `seed` — served from a small seed-backed dataset (companies)
- `historical` — served, but explicitly historical/reference only (vehicle registration codes)
- `research` — investigated, with retained tooling/evidence, but not served (VAT registrations)
- `blocked` — gates confirmed failing; not served (ŽRSR, streets, healthcare facilities, school directory, court decisions)

`coverage` (how much of the domain the served data covers): `complete`, `partial`, `seed`, or `null` (not served). Status and coverage are independent: `production + partial` is a first-class combination (TED snapshot).

`licence.status`: `verified`, `identified`, `pending`, `blocked` — derived deterministically from the internal `licenceStatus` wording. Nothing is upgraded manually; unresolved stays unresolved.

## Mapping Rules (deterministic, snapshot-tested)

1. Runtime dataset present and id is companies -> `seed`; vehicle registration codes -> `historical`; otherwise -> `production`.
2. No runtime dataset and internal `redistributionStatus` starts with "blocked" -> `blocked`; otherwise -> `research`.
3. Coverage: `complete -> complete`, `partial -> partial`, `seed-backed -> seed`, `unknown -> null`.
4. Licence: `licenceStatus` starting with "blocked" -> `blocked`; containing "pending" -> `pending`; containing "identified/listed/retained" -> `identified`; containing "verified" -> `verified`; otherwise `pending`.

Per-id curated values (public names, limitations, update cadences, licence names) live in `services/sources_service.py`.

## Filters

`GET /v1/sources` supports `status`, `coverage`, and `q` (substring over id, public name, and source name). No pagination: the registry is small and list-style small routes in OpenSK return arrays directly.
