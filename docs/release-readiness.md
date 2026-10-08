# Release Readiness

## Current Status

OpenSK API is pre-1.0 at `0.23.1`. The public API uses `/v1`, and response `metadata.version` remains `"v1"`. Runtime requests use local normalized datasets only. The current OpenAPI schema exposes 35 GET operations: root plus 34 `/v1` operations. The candidate first stable scope is defined in `docs/1-0-scope.md`.

OpenSK API should not be released as `1.0.0` today because source/licence redistribution evidence and CI/release operations are not yet strong enough for a stable public release.

## Must-Fix Before 1.0

| Blocker | Reason | Affected endpoint/dataset | Severity | Proposed resolution | Work type |
| --- | --- | --- | --- | --- | --- |
| Resolve high-risk PortalVS redistribution uncertainty for PSC, districts, and municipalities, or exclude them from the stable contract | These are candidate 1.0 routes, but PortalVS redistribution is treated as restricted until retained evidence says otherwise. | `/v1/psc*`, `/v1/districts*`, `/v1/municipalities*` | high | Obtain written/retained terms for caching, transformation, redistribution, commercial downstream use, and attribution; if unresolved, exclude affected routes from 1.0. | legal/source, documentation, possible code |
| Keep company dataset explicitly seed-backed | Current company lookup remains seed-backed; 0.14.0 did not approve RPO production import. | `/v1/companies/{ico}`, `/v1/ico/{ico}`; `data/companies.json` | medium | Include as `INCLUDE_AS_SEED_BACKED`; no national RPO completeness implication. | product, documentation |
| Decide whether explicit TED_PARTIAL procurement remains in 1.0 | 0.19.0 adds a small TED-backed Slovak-buyer snapshot, not national ÚVO coverage. It is only appropriate for 1.0 if partial scope and attribution are explicit. | `/v1/procurement-notices*`; `data/procurement_notices.json` | medium | Keep with explicit partial coverage and exact TED attribution wording, or defer from 1.0 until ÚVO national coverage/licensing is resolved. | product, legal/source, documentation |
| Retain exact source/licence evidence for all datasets included in 1.0 | Several sources are identified but exact licence text, attribution wording, transformation permission, or redistribution permission is not retained. | Regions, banks, holidays, phone areas, vehicle registration codes, school facility counts, procurement notices | high | Store exact evidence quotes/links and update `data/sources.json`, `docs/source-compliance.md`, and evidence docs without removing warnings unless evidence supports it. | legal/source, documentation |
| Keep CI required for PRs | 1.0 needs automated validation so dataset/API breakage does not merge unnoticed. | Repository-wide | high | Require the CI workflow added in 0.13.0 as a branch protection check before final 1.0. | operational, CI |
| Complete final deployment verification from clean `main` | Public Render deployment must match the release commit and pass smoke tests. | `https://opensk-api.onrender.com/` | high | Deploy from clean `main`, verify root version, OpenAPI, representative endpoints, and public smoke test. | deployment, operational |

## Should-Fix Before 1.0

| Item | Reason | Affected endpoint/dataset | Severity | Proposed resolution | Work type |
| --- | --- | --- | --- | --- | --- |
| Decide whether direct-array list responses should remain | Some small list endpoints return arrays directly while larger collections return paginated wrappers. This is documented but inconsistent. | Regions, districts, municipalities, banks, holidays | medium | Either preserve intentionally in `docs/api-contract-v1.md` or change before 1.0 if a uniform wrapper is desired. | API contract, documentation or code |
| Document `/v1/ico/{ico}` alias as permanent if companies remain in 1.0 | 0.14.0 retained the alias for compatibility. | Companies/IČO | low | Keep documented in API contract and smoke tests. | API contract, documentation |
| Clarify PSC completeness roadmap | Partial coverage can be stable if explicit, but users need clear expectations. | PSC | medium | Add user-facing coverage notes and refresh policy if PSC stays in 1.0. | documentation, data |
| Retain exact Creative Commons BY licence version for school aggregate source | Source lists CC BY, but exact version/attribution wording is not retained. | School facility counts | medium | Store exact licence version or source wording. | legal/source, documentation |
| Document operational ownership for Render deploys | 1.0 should have an explicit deployment/redeploy check. | Render deployment | medium | Add release checklist and require public smoke after deploy. | operational, documentation |

## Accepted Limitations

- 1.0 may expose partial datasets if coverage is explicit and behavior is stable.
- School facility counts are aggregate-only; `/v1/schools` is intentionally out of scope.
- Vehicle registration codes are historical/reference only and do not decode current full plates.
- Phone-area dataset may retain 3 unmatched local geography links if documented.
- Company lookup may remain seed-backed if this is explicit and not marketed as full RPO coverage.
- VAT registration lookup remains absent until privacy handling is approved.
- ŽRSR/trade registration lookup remains absent until source acquisition and privacy handling are approved.
- Streets/address lookup remains absent until source acquisition, reuse, and street-only privacy handling are approved.
- Healthcare-facility lookup remains absent until source acquisition, reuse, IdZZ-bearing record shape, and facility-only privacy handling are approved.
- Public procurement notices may remain TED_PARTIAL if explicit attribution, 100-record snapshot scope, and non-ÚVO status are documented.
- Institution-level school lookup remains absent until source acquisition, reuse, stable identifier, coverage, refresh, and privacy gates pass.
- Court-decision lookup remains absent until Ministry/court-source reuse/redistribution terms, metadata-only privacy projection, published-decision scope, Constitutional Court coverage, and full-text exclusion are approved.
- Free-tier Render cold starts are acceptable if smoke tests retry or operators account for them.

## Operational Readiness

- Render configuration is checked in as `render.yaml`.
- Build command is `pip install -r requirements.txt`.
- Start command is `uvicorn main:app --host 0.0.0.0 --port $PORT`.
- No application-specific environment variables are required beyond Render-provided `PORT`.
- Runtime datasets are checked in under `data/`; missing required files should fail fast through tests, dataset validation, or endpoint errors rather than silently fetching upstream data.
- `/v1/health`, `/docs`, `/openapi.json`, and `scripts/smoke_test.py` are the minimum deployment verification surfaces.
- Public smoke tests may show stale deployment versions until Render has redeployed the latest `main`.

## Post-1.0 Backlog

- Broader company/RPO import after acquisition, licence, provenance, rate-limit, and privacy clearance.
- National PSC completeness work after source rights are clear.
- Automated scheduled dataset refreshes.
- Future `/v2` cleanup if a uniform response shape is desired.
- Additional endpoint domains only after source/licence and privacy review.
- VAT registration lookup after privacy gate approval and normalized dataset-size review.
- ŽRSR/trade registration lookup after official machine-readable source, reuse, acquisition, and privacy gates pass.
- Streets/address lookup after official source/reuse gates pass and dataset size is reviewed.
- Healthcare-facility lookup after official source/reuse/privacy gates pass and dataset size is reviewed.
- Verified ÚVO NATIONAL procurement replacement or larger TED refresh after exact attribution and acquisition review.
- Institution-level schools endpoint after an approved MŠVVaM/RIS/CVTI source, stable identifier, privacy-safe field subset, and refresh workflow are verified.
- Court-decision endpoint after approved Ministry/court source reuse terms, metadata-only privacy projection, stable source URLs, and full-text exclusion are verified.

## Required Verification For 1.0

- `python scripts/validate_datasets.py`
- `python scripts/check_referential_integrity.py`
- `python -m pytest -q`
- `python -m compileall scripts routers services tests schemas`
- `git diff --check`
- Local smoke test against a running app
- Public smoke test against Render after deployment from release commit
- Documentation review for source/licence, privacy, dataset coverage, API contract, and versioning

## Proposed 1.0 Release Procedure

1. All required PRs merged.
2. Clean `main`.
3. CI green.
4. Dataset validation green.
5. Referential integrity green.
6. Test suite green.
7. Local smoke test green.
8. Render deployed from `main`.
9. Public smoke test green.
10. Docs reviewed.
11. Version changed to `1.0.0`.
12. Final PR opened.
13. Final PR merged.
14. Git tag created.
15. GitHub Release created.

Do not execute this release procedure during `0.23.1`.

## Proposed Follow-Up Issues

- Resolve 1.0 source and redistribution evidence for included datasets, especially PortalVS-backed PSC/districts/municipalities.
- Keep PSC/districts/municipalities as `INCLUDE_AFTER_COMPLIANCE_FIX` or exclude before the final 1.0 PR.
- Keep company/IČO as `INCLUDE_AS_SEED_BACKED`; alias permanence is currently resolved in favor of retaining `/v1/ico/{ico}`.
- Freeze candidate v1 API contract and resolve response-shape decisions.
- Complete production deployment and smoke-test release checklist.
