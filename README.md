# OpenSK API

OpenSK API is a FastAPI service that exposes a small set of Slovak public data through a consistent JSON envelope.

Status: `0.23.1` pre-1.0 trust-and-utility-surface milestone.

Public deployment: `https://opensk-api.onrender.com/`

OpenSK API is still before its first formal stable `1.0.0` release. Earlier `v1.x` labels in the changelog were internal development milestone labels, not formal stable releases. The current `/v1` route prefix is an API namespace and remains unchanged during the pre-1.0 reset.

See `docs/versioning.md` for the versioning policy. Future `1.0.0` is reserved for the first stable public API contract after stabilization and source/compliance review.

No API key is required. CORS is enabled for browser clients. All responses are JSON.

## Public API Surface

Use `/docs` or `/openapi.json` for parameter-level details. The table below is a concise index of the current public routes; all runtime routes read local normalized data only.

| Endpoint | Purpose | Coverage | Source status |
| --- | --- | --- | --- |
| `GET /` | Project metadata, including project SemVer and API namespace | project metadata | local service metadata |
| `GET /v1/health` | Health check | service health | local service metadata |
| `GET /v1/iban/validate/{iban}` | IBAN checksum validation with Slovak bank resolution when possible | validation endpoint | local bank dataset for bank resolution |
| `GET /v1/regions`, `GET /v1/regions/{code}` | Region list and lookup | complete | Eurostat source; reuse terms tracked |
| `GET /v1/districts`, `GET /v1/districts/{code}` | District list and lookup | complete imported | PortalVS terms may restrict reuse |
| `GET /v1/municipalities`, `GET /v1/municipalities/{code}` | Municipality list and lookup | complete imported | PortalVS terms may restrict reuse |
| `GET /v1/psc`, `GET /v1/psc/{psc}` | PSC list and lookup | partial imported | PortalVS terms may restrict reuse |
| `GET /v1/psc/search`, `GET /v1/psc/stats` | PSC search and dataset stats | partial imported | PortalVS terms may restrict reuse |
| `GET /v1/banks`, `GET /v1/banks/{code}` | Bank-code list and lookup | complete imported | NBS source/licence verification pending |
| `GET /v1/holidays/{year}` | Slovak holiday calendar by year | partial curated seed | NBS/legal-act provenance tracked |
| `GET /v1/companies/{ico}`, `GET /v1/ico/{ico}` | Seed-backed company lookup and IČO alias | seed-backed | RPO expansion/licence/privacy verification pending |
| `GET /v1/phone-areas`, `GET /v1/phone-areas/{code}` | Phone-area list and lookup | complete imported; 3 unmatched local geography links | telecom regulator licence verification pending |
| `GET /v1/phone-areas/search` | Phone-area search | complete imported; 3 unmatched local geography links | telecom regulator licence verification pending |
| `GET /v1/vehicle-registration-codes`, `GET /v1/vehicle-registration-codes/{code}` | Legacy vehicle registration district-code list and lookup | historical/reference | Slov-Lex reuse verification pending |
| `GET /v1/vehicle-registration-codes/search` | Legacy vehicle registration district-code search | historical/reference | Slov-Lex reuse verification pending |
| `GET /v1/school-facility-counts` | Aggregate school facility counts | aggregate imported | MŠVVaM lists Creative Commons BY |
| `GET /v1/school-facility-counts/stats` | Aggregate school facility count totals | aggregate imported | MŠVVaM lists Creative Commons BY |
| `GET /v1/procurement-notices` | Public procurement notice list | partial imported; 100-record TED snapshot | TED attribution-backed; not national ÚVO coverage |
| `GET /v1/procurement-notices/{id}` | Public procurement notice lookup | partial imported; 100-record TED snapshot | TED attribution-backed; not national ÚVO coverage |
| `GET /v1/procurement-notices/search` | Public procurement notice search | partial imported; 100-record TED snapshot | TED attribution-backed; not national ÚVO coverage |
| `GET /v1/procurement-notices/stats` | Public procurement notice snapshot stats | partial imported; 100-record TED snapshot | TED attribution-backed; not national ÚVO coverage |
| `GET /v1/sources` | Curated public source/licence provenance catalogue | 17 registered domains | unresolved licence status stays unresolved |
| `GET /v1/sources/{id}` | Source catalogue entry by stable registry id | 17 registered domains | internal maintainer fields are excluded |
| `GET /v1/business-days/check` | Slovak business-day check for an ISO date | 2024-2026 holiday coverage | strict error outside supported years |
| `GET /v1/business-days/add` | Add/subtract business days from an ISO date | 2024-2026 holiday coverage | strict error outside supported years |
| `GET /v1/business-days/between` | Count business days in a bounded ISO interval | 2024-2026 holiday coverage | strict error outside supported years |

`/v1/schools` is intentionally not implemented. The confirmed MŠVVaM open-data CSV is aggregate-only, and the institution-level RIS/CVTI candidates still lack verified production reuse, acquisition, identifier, coverage, and privacy gates. Procurement notices are explicit `TED_PARTIAL`; the endpoint does not claim ÚVO national vestník completeness.

## PSC Collection Surface

The PSC collection routes, pagination model, and current dataset limitations remain aligned with the shipped local-data contract.

## Dataset Tooling

The repository keeps its reference data in local JSON files under `data/`.

- `data/sources.json` is the machine-readable source registry.
- `docs/import-pipeline.md` explains the offline raw -> checked-in JSON -> production runtime flow.
- `docs/data-sources.md` lists the current dataset inventory and coverage notes.
- `docs/source-compliance.md` summarizes licence, redistribution, attribution, and risk status for each production dataset.
- `docs/source-catalogue.md` documents the curated `/v1/sources` public/internal field boundary and status mapping.
- `docs/http-caching.md` documents ETag, Last-Modified, and Cache-Control semantics.
- `docs/rate-limiting-contract.md` records the future per-IP rate-limiting contract (not implemented yet).
- `docs/adding-a-dataset.md` lists the minimum gates for adding a new dataset domain.
- `docs/dataset-format.md` documents the JSON file layout and record shapes.
- `docs/research/ico-sources.md` captures the IČO/company research notes and upstream questions.
- `docs/research/source-verification-evidence.md` records retained source-verification evidence.
- `docs/research/source-licence-questions.md` contains draft clarification questions; nothing is sent automatically.
- `docs/api-status.md` lists the endpoint status categories.
- `docs/public-api-consistency-audit.md` records the 0.12.0 public API consistency audit.
- `docs/1-0-readiness-audit.md` and `docs/release-readiness.md` track what remains before a future `1.0.0`.
- `docs/1-0-scope.md` defines the candidate first stable release scope and excluded roadmap domains.
- `docs/roadmap.md` is the living strategic roadmap (Now/Next/Watch/Later/Completed).
- `docs/research/opensk-research-roadmap-2026-q4.md` is the 2026 Q4 consolidated source-licence and roadmap research report.
- `docs/research/roadmap-council-notes.md` records the multi-perspective roadmap-council verdicts.
- `docs/research/source-licence-outreach.md` contains ready-to-send licence outreach packages; nothing is sent automatically.
- `docs/research/paper-roadmap-coverage.md` compares the May 2026 research-paper roadmap with the actual repository and verified 2026 sources.
- `docs/research/court-decisions-source.md` records why 0.22.0 remains research-only for Slovak court-decision production data.
- `docs/api-contract-v1.md` describes the candidate v1 contract for eventual `1.0.0`.
- `docs/privacy-review.md` records the current privacy review.
- `docs/research/rpo-acquisition-decision.md` records why 0.14.0 remains research/tooling-only for RPO production data.
- `docs/research/vat-source.md` records why 0.15.0 remains research/tooling-only for VAT registration production data.
- `docs/research/zrsr-source.md` records why 0.16.0 remains research-only for ŽRSR production data.
- `docs/research/streets-source.md` records why 0.17.0 remains research-only for Register adries / streets production data.
- `docs/research/healthcare-facilities-source.md` records why 0.18.0 remains research-only for healthcare-facility/provider production data.
- `docs/research/public-procurement-source.md` records why 0.19.0 uses a TED-backed partial public procurement snapshot rather than claiming ÚVO national coverage.
- `docs/research/school-directory-source.md` records why 0.20.0 remains research/tooling-only for institution-level school directory data.
- `docs/verification-backlog.md` tracks the remaining verification tasks.
- `docs/known-limitations.md` collects the current public-readiness caveats.
- `data/sources.json` and the dataset-specific research notes document source and licence verification per dataset.
- `Source/licence verification pending.` applies to any dataset whose upstream provenance is not fully confirmed.
- Runtime requests do not call upstream services; the API reads local JSON only.
- Current project versioning is pre-1.0; endpoint availability does not yet guarantee a stable `1.0.0` public contract.
- Company lookup remains seed-backed; RPO production import is blocked until a safe acquisition method is verified.
- VAT registration lookup is not public in `0.15.0`; source acquisition is verified, but privacy import is blocked because the XML has no reliable natural/legal subject marker.
- ŽRSR/trade-register lookup is not public in `0.16.0`; no safe official machine-readable acquisition route was verified.
- Streets/address lookup is not public in `0.17.0`; no approved official anonymous reproducible streets distribution was verified.
- Healthcare-facility lookup is not public in `0.18.0`; no approved machine-readable non-scraping facility source with reuse rights and deterministic privacy filtering was verified.
- Procurement notice lookup is public in `0.19.0` as a 100-record TED_PARTIAL snapshot only; it excludes national-only ÚVO notices and personal/contact/address/winner fields.
- Institution-level school lookup is not public in `0.20.0`; official RIS/CVTI candidates were identified, but production import is blocked by reuse, acquisition, identifier, coverage, and privacy gates.
- 0.21.0 freezes the candidate 1.0 scope: company/IČO remains seed-backed, PortalVS-backed districts/municipalities/PSC require compliance fixes, and research-only domains are excluded rather than treated as 1.0 blockers.
- 0.22.0 verifies a Ministry court-decision OpenAPI source, but court-decision lookup remains research-only because reuse/redistribution and metadata-only privacy gates are unresolved.
- 0.23.0 verifies PortalVS end-of-support (legacy support ends 2026-10-31; `ciselniky2.portalvs.sk` is the successor), confirms the portal's non-commercial copyright wording (districts/municipalities/PSC stay compliance-Red pending outreach), verifies ŠÚ SR elections open data as the next data spike, and prepares licence outreach packages; no endpoint or dataset is added.
- 0.23.1 adds the curated `/v1/sources` provenance catalogue, Slovak business-day utilities with strict 2024-2026 holiday coverage, deterministic ETag/Last-Modified conditional caching, project-version single-sourcing (`version.py`), unified CI, Dependabot, a manual source-health checker, and a documented (not implemented) rate-limit contract.
- Root and error envelopes now use `metadata.lastUpdated: null` instead of a daily-changing date; dataset routes keep their real dataset dates.
- Historical internal milestones include the phone-area workbook import, legacy vehicle registration district abbreviations, and aggregate school facility counts.
- `/v1/schools` is intentionally not implemented because no institution-level school source has passed production acquisition gates.
- `/v1/court-decisions` is intentionally not implemented because no court-decision source has passed reuse/redistribution and privacy gates.

## Dataset Import Pipeline

The import pipeline is offline-only and defaults to dry-run.

```bash
python scripts/import_geography.py --dataset municipalities --input data/raw/portalvs-classifier-9.json --dry-run --output data/generated/municipalities.json
python scripts/import_geography.py --dataset municipalities --input data/raw/portalvs-classifier-9.csv --output data/generated/municipalities.json --write
python scripts/import_psc.py --input data/raw/psc-source.csv --output data/generated/psc.json --dry-run
python scripts/import_psc.py --input data/raw/psc-source.csv --output data/generated/psc.json --write
python scripts/import_banks.py --input data/raw/nbs-bank-directory.csv --output data/generated/banks.json --dry-run
python scripts/import_banks.py --input data/raw/nbs-bank-directory.csv --output data/generated/banks.json --write
python scripts/import_phone_areas.py --input data/raw/phone-areas.csv --output data/generated/phone_areas.json --dry-run
python scripts/import_phone_areas.py --input data/raw/phone-areas.xlsx --output data/generated/phone_areas.json --write
python scripts/import_school_facility_counts.py --input data/raw/minedu-school-facility-counts-2025-09-15.csv --output data/generated/school_facility_counts.json --dry-run
python scripts/fetch_procurement_notices.py --limit 100 --write
python scripts/import_procurement_notices.py --input data/raw/procurement-notices-ted-search.json --output data/generated/procurement_notices.json --dry-run
python scripts/fetch_vat_registrations.py --output data/raw/ds_dphs.zip
python scripts/import_vat_registrations.py data/raw/ds_dphs.zip --output data/generated/vat_registrations.json --write
python scripts/backfill_psc_districts.py --dry-run
python scripts/backfill_psc_districts.py --write
python scripts/validate_datasets.py
python scripts/check_referential_integrity.py
```

Use `data/raw/` for source material and `data/generated/` for normalized previews. Promote generated files into `data/*.json` only after review.

`scripts/import_vat_registrations.py` intentionally refuses to write `data/vat_registrations.json` while the VAT privacy gate remains blocked.

`scripts/import_procurement_notices.py` can promote a reviewed TED_PARTIAL snapshot to `data/procurement_notices.json`, but refresh edits should be reviewed as dataset diffs before commit.

## Company Lookup

Company/IČO lookup is backed by a small checked-in local seed dataset, not full RPO coverage.

- Source notes: `docs/research/ico-sources.md`
- Licence notes: `docs/research/rpo-licence.md`
- Proposed schema: `docs/dataset-format.md`
- Registry entry: `data/sources.json`
- No live upstream calls are made by the API routes.
- Personal/stakeholder fields are intentionally excluded from the public response.
- Public-readiness status is documented in `docs/api-status.md` and `docs/known-limitations.md`.

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

`metadata.lastUpdated` carries the dataset freshness date; meta and error responses report an explicit `null` instead of a request-time date.

Error responses use the same envelope with `data: null` and a structured error object.

## Examples

```bash
curl <base-url>/
curl <base-url>/v1/health
curl <base-url>/v1/psc/stats
curl <base-url>/v1/psc/search?q=Bratislava
curl <base-url>/v1/banks
curl <base-url>/v1/regions
curl <base-url>/v1/vehicle-registration-codes/BA
curl <base-url>/v1/school-facility-counts/stats
curl <base-url>/v1/procurement-notices/stats
curl <base-url>/v1/procurement-notices/search?q=Bratislava
curl <base-url>/v1/companies/50158635
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

Swagger docs: `https://opensk-api.onrender.com/docs`

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
- Banks are imported from the NBS domestic payment-system identification-code directory snapshot effective `2026-05-18`; source/licence verification remains pending.
- Phone areas are imported from the telecom regulator's machine-processable workbook; licence/reuse verification remains pending.
- Vehicle registration district codes are legacy/reference data from Slov-Lex legal text; they are not reliable for current plate lookup and do not decode full licence plates.
- School facility counts are aggregate rows from the MŠVVaM `Register škôl a školských zariadení` CSV, valid as of `2025-09-15`; the API does not provide institution-level `/v1/schools` lookup.
- Institution-level RIS/CVTI school-directory candidates are research-only in 0.20.0; no `data/schools.json` or `/v1/schools` endpoint is shipped.
- School aggregate responses exclude school names, addresses, directors, staff, pupils, personal emails, and phone numbers.
- Public procurement notices are a normalized 100-record TED Search API snapshot of Slovak-buyer notices, acquired 2026-09-29; coverage is `TED_PARTIAL`, not the complete national ÚVO vestník.
- Procurement API responses exclude personal/contact data, street addresses, winners, tenderers, subcontractors, beneficial owners, organization identifiers, and raw XML/PDF/HTML notice bodies.
- IBAN validation and Slovak bank-code resolution run locally without network access.
- The PSC dataset is expanded beyond the original tiny seed-only sample, but it does not claim national coverage.
- PSC coverage and source/licence details are tracked in `docs/data-sources.md`; the dataset remains partial and may contain repeated postal-code records.
- PSC redistribution is restricted by upstream PortalVS terms, so do not present the dataset as open redistribution material.
- Imported PSC source data does not provide reliable district links, so PSC `districtCode` is backfilled locally from `municipalityCode` using verified municipality -> district mappings.
- PSC `districtCode` coverage is 100% for current local PSC records; no values are inferred from names or PSC patterns.
- PSC source rows can repeat the same postal code; the importer/preview should surface that with `matchCount` and `matches` before choosing a canonical runtime record.
- `GET /v1/psc` returns paginated PSC match records with `limit` and `offset`.
- `GET /v1/psc/search?q=...` searches PSC records by PSC prefix, municipality, and delivery post.
- `GET /v1/psc/stats` exposes local dataset totals and geography coverage.
- IČO/company work uses a local seed dataset; do not treat it as exhaustive or a full register.
- Regions cover the 8 Slovak self-governing regions and are verified against the Eurostat LAU 2025 correspondence table.
- Municipalities are sourced from PortalVS classifier 9 (`Obce`) and the checked-in dataset currently covers the 2,927 regular Slovak municipality rows used by the runtime API.
- Municipality district mappings come from PortalVS classifier 9 `code_su` and are validated against the local districts dataset.
- PortalVS source/licence verification is still pending; do not treat the municipality dataset as open redistribution material.
- Districts are imported from PortalVS classifier 10 and cover all Slovak districts; PortalVS terms may restrict reuse.
- ORSR and ŽRSR stay reference-only in research notes; this repository does not scrape them.
- Source notes live in `docs/data-sources.md`, and file format notes live in `docs/dataset-format.md`.
- Research notes for company/IČO work live in `docs/research/ico-sources.md`.
- Remaining verification tasks are tracked in `docs/verification-backlog.md`.
- Candidate 1.0 inclusion and exclusion decisions are tracked in `docs/1-0-scope.md`.
- Dataset compliance status is summarized in `docs/source-compliance.md`.
- Verification evidence and draft licence questions are tracked under `docs/research/`.
- Use `Source/licence verification pending.` when a dataset's upstream provenance is not fully confirmed.
- Do not assume any dataset is official government data unless the source explicitly says so.

## Contributing

Contributions are welcome, especially new data sources that can be added with clear attribution and licensing.

See `CONTRIBUTING.md` for contribution guidance.

## License

The code in this repository is licensed under MIT. See `LICENSE`.
