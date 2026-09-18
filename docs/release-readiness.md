# Release Readiness

## Current Status

OpenSK API is pre-1.0 at `0.13.0`. The public API uses `/v1`, and response `metadata.version` remains `"v1"`. Runtime requests use local normalized datasets only. The current OpenAPI schema exposes 26 GET operations: root plus 25 `/v1` operations.

OpenSK API should not be released as `1.0.0` today because source/licence redistribution evidence and CI/release operations are not yet strong enough for a stable public release.

## Must-Fix Before 1.0

| Blocker | Reason | Affected endpoint/dataset | Severity | Proposed resolution | Work type |
| --- | --- | --- | --- | --- | --- |
| Resolve high-risk PortalVS redistribution uncertainty for PSC, or exclude PSC from 1.0 scope | PSC is partial and has `riskLevel: high`; redistribution is treated as restricted. Shipping it as stable without a decision is risky. | `/v1/psc`, `/v1/psc/{psc}`, `/v1/psc/search`, `/v1/psc/stats`; `data/psc.json` | high | Obtain written/retained terms for caching, transformation, redistribution, commercial downstream use, and attribution; if unresolved, remove PSC from 1.0 public scope or mark it experimental outside the stable contract. | legal/source, documentation, possible code |
| Resolve PortalVS district and municipality redistribution uncertainty, or document an explicit exclusion strategy | Districts and municipalities are foundational for geography links, but redistribution remains restricted/pending. | `/v1/districts`, `/v1/municipalities`, geography links in PSC, phone areas, school facility counts | high | Retain exact allowed-use evidence or decide whether these endpoints can be included in 1.0 under conservative terms. | legal/source, documentation |
| Resolve company dataset strategy | Current company lookup is seed-backed, not full RPO coverage. This is acceptable only if 1.0 explicitly commits to seed-backed lookup and does not imply comprehensive IČO search. | `/v1/companies/{ico}`, `/v1/ico/{ico}`; `data/companies.json` | high | Choose and document one strategy: keep seed-backed as stable with narrow scope, or defer company endpoints from 1.0 until RPO/licence/privacy work is complete. | product, legal/source, documentation |
| Retain exact source/licence evidence for all datasets included in 1.0 | Several sources are identified but exact licence text, attribution wording, transformation permission, or redistribution permission is not retained. | Regions, banks, holidays, phone areas, vehicle registration codes, school facility counts | high | Store exact evidence quotes/links and update `data/sources.json`, `docs/source-compliance.md`, and evidence docs without removing warnings unless evidence supports it. | legal/source, documentation |
| Keep CI required for PRs | 1.0 needs automated validation so dataset/API breakage does not merge unnoticed. | Repository-wide | high | Require the CI workflow added in 0.13.0 as a branch protection check before final 1.0. | operational, CI |
| Complete final deployment verification from clean `main` | Public Render deployment must match the release commit and pass smoke tests. | `https://opensk-api.onrender.com/` | high | Deploy from clean `main`, verify root version, OpenAPI, representative endpoints, and public smoke test. | deployment, operational |

## Should-Fix Before 1.0

| Item | Reason | Affected endpoint/dataset | Severity | Proposed resolution | Work type |
| --- | --- | --- | --- | --- | --- |
| Decide whether direct-array list responses should remain | Some small list endpoints return arrays directly while larger collections return paginated wrappers. This is documented but inconsistent. | Regions, districts, municipalities, banks, holidays | medium | Either preserve intentionally in `docs/api-contract-v1.md` or change before 1.0 if a uniform wrapper is desired. | API contract, documentation or code |
| Decide whether `/v1/ico/{ico}` alias is permanent | Alias is useful but duplicates company lookup route. | Companies/IČO | medium | Keep and document as permanent alias, or remove before 1.0. | API contract, documentation or code |
| Clarify PSC completeness roadmap | Partial coverage can be stable if explicit, but users need clear expectations. | PSC | medium | Add user-facing coverage notes and refresh policy if PSC stays in 1.0. | documentation, data |
| Retain exact Creative Commons BY licence version for school aggregate source | Source lists CC BY, but exact version/attribution wording is not retained. | School facility counts | medium | Store exact licence version or source wording. | legal/source, documentation |
| Document operational ownership for Render deploys | 1.0 should have an explicit deployment/redeploy check. | Render deployment | medium | Add release checklist and require public smoke after deploy. | operational, documentation |

## Accepted Limitations

- 1.0 may expose partial datasets if coverage is explicit and behavior is stable.
- School facility counts are aggregate-only; `/v1/schools` is intentionally out of scope.
- Vehicle registration codes are historical/reference only and do not decode current full plates.
- Phone-area dataset may retain 3 unmatched local geography links if documented.
- Company lookup may remain seed-backed if this is explicit and not marketed as full RPO coverage.
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

- Broader company/RPO import after licence and privacy clearance.
- National PSC completeness work after source rights are clear.
- Automated scheduled dataset refreshes.
- Future `/v2` cleanup if a uniform response shape is desired.
- Additional endpoint domains only after source/licence and privacy review.

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

Do not execute this release procedure during `0.13.0`.

## Proposed Follow-Up Issues

- Resolve 1.0 source and redistribution evidence for included datasets.
- Decide PSC 1.0 inclusion strategy.
- Decide company/IČO 1.0 scope and alias permanence.
- Freeze candidate v1 API contract and resolve response-shape decisions.
- Complete production deployment and smoke-test release checklist.
