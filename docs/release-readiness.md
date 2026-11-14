# Release Readiness

## Current Status

OpenSK API is pre-1.0. The authoritative project version is in [`version.py`](../version.py) and `GET /`; `/v1` and response `metadata.version: "v1"` remain independent namespace identifiers. Runtime requests use local normalized datasets only. OpenAPI exposes 42 GET operations. The candidate stable scope is defined in [1-0-scope.md](1-0-scope.md).

The published legacy `v1.0.0` tag points to an application reporting `1.0.0-rc.6`. Before any stable release, choose and document an unused version/tag under the [versioning policy](versioning.md); never move or overwrite the existing tag silently. “1.0 readiness” below names a stability milestone, not permission to reuse that tag.

OpenSK API should not be released as `1.0.0` today because source/licence redistribution evidence (notably PortalVS) is still unresolved — and sending clarification outreach is not permission. Operational guardrails (application rate limiting, daily scheduled public smoke monitoring) are in place since 0.23.5; public promotion remains gated by source compliance, not by operations.

## Must-Fix Before 1.0

| Blocker | Reason | Affected endpoint/dataset | Severity | Proposed resolution | Work type |
| --- | --- | --- | --- | --- | --- |
| Resolve high-risk PortalVS redistribution uncertainty for PSC, districts, and municipalities, or exclude them from the stable contract | These are candidate 1.0 routes, but PortalVS redistribution is treated as restricted until retained evidence says otherwise. | `/v1/psc*`, `/v1/districts*`, `/v1/municipalities*` | high | Obtain written/retained terms for caching, transformation, redistribution, commercial downstream use, and attribution; if unresolved, exclude affected routes from 1.0. | legal/source, documentation, possible code |
| Keep company dataset explicitly seed-backed | Current company lookup remains seed-backed; 0.14.0 did not approve RPO production import. | `/v1/companies/{ico}`, `/v1/ico/{ico}`; `data/companies.json` | medium | Include as `INCLUDE_AS_SEED_BACKED`; no national RPO completeness implication. | product, documentation |
| Decide whether explicit TED_PARTIAL procurement remains in 1.0 | 0.19.0 adds a small TED-backed Slovak-buyer snapshot, not national ÚVO coverage. It is only appropriate for 1.0 if partial scope and attribution are explicit. | `/v1/procurement-notices*`; `data/procurement_notices.json` | medium | Keep with explicit partial coverage and exact TED attribution wording, or defer from 1.0 until ÚVO national coverage/licensing is resolved. | product, legal/source, documentation |
| Retain exact source/licence evidence for all datasets included in 1.0 | Several sources still need evidence; bank reuse is resolved by the 2026-10-14 NBS clarification (refresh/mapping maintenance separate). | Regions, holidays, phone areas, vehicle registration codes, school facility counts, procurement notices | high | Store exact evidence quotes/links and update `data/sources.json`, `docs/source-compliance.md`, and evidence docs without removing warnings unless evidence supports it. | legal/source, documentation |
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
- Build command is `python -m pip install --require-hashes -r requirements.txt`; CI installs the separate development lock, constrained to the same runtime versions.
- Python is declared in `.python-version`; CI reads that file and Render's native Python runtime uses it. Update the interpreter patch and dependency locks deliberately and test in a fresh environment.
- Start command is `uvicorn main:app --host 0.0.0.0 --port $PORT --no-access-log`. Account-bearing paths are not logged by Uvicorn; proxy/CDN logging still needs a hosting-side review.
- The Blueprint declares `autoDeployTrigger: checksPass`. Apply/sync the Blueprint and verify this setting in Render; require the `verify` CI job through GitHub branch rules. These external settings are not established merely by editing the repository.
- No application-specific environment variables are required beyond Render-provided `PORT` and `RENDER`; the rate limiter is auto-enabled under `RENDER=true` and can be overridden with `OPENSK_RATE_LIMIT_ENABLED` (`auto|true|false`).
- The application rate limiter (100 requests/60 s/client-IP, fixed window, in-memory process-local) protects the single-instance deployment; policy and evidence in `docs/rate-limiting-contract.md`. It is not a globally exact quota across multiple instances; revisit shared-state limiting on that documented trigger.
- The `Public Smoke` GitHub Actions workflow runs `scripts/smoke_test.py --expect-rate-limit` daily (06:17 UTC, `workflow_dispatch` available) against the public deployment with a bounded `/v1/health` warm-up for free-tier cold starts. It is a best-effort daily external check — not an uptime SLA, incident management, or latency monitoring. Its own Actions failure status is the alerting channel; no external monitoring service is used. Caveat: GitHub auto-disables scheduled workflows after 60 days of repository inactivity — re-enable via any commit or the Actions UI.
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
- `python -m ruff check .`
- `python scripts/check_docs.py`
- `python -m pip_audit -r requirements.txt --disable-pip --require-hashes`
- `python -m compileall -q main.py version.py scripts routers services tests schemas`
- `git diff --check`
- Local smoke test against a running app
- Public smoke test against Render after deployment from release commit
- Documentation review for source/licence, privacy, dataset coverage, API contract, and versioning

## Proposed 1.0 Release Procedure

1. Resolve or explicitly exclude source/privacy blockers for every included route group; freeze the intended stable contract.
2. Resolve legacy tag ambiguity and select an unused release version/tag. Update `version.py`, changelog, lockfiles if needed and release documentation in the final release PR.
3. Review and merge that PR through required CI. Record the exact resulting commit SHA; start from clean `main`.
4. Install hash-locked development dependencies in a fresh environment and run all required verification above, including a local smoke test against that exact versioned commit.
5. Deploy that exact commit to Render after checks pass. Confirm Render's deployed commit and root/OpenAPI versions, then run the public smoke suite with `--expect-rate-limit`.
6. Only after those checks succeed, create the chosen immutable tag at the verified commit and publish release notes with coverage, licensing, compatibility and migration caveats.
7. If code or version changes after verification, repeat deployment and smoke verification before tagging. Do not tag a different commit from the one tested.

This checklist documents a future explicit release operation; it is not an instruction to publish a stable release while blockers remain.

## Proposed Follow-Up Issues

- Resolve 1.0 source and redistribution evidence for included datasets, especially PortalVS-backed PSC/districts/municipalities.
- Keep PSC/districts/municipalities as `INCLUDE_AFTER_COMPLIANCE_FIX` or exclude before the final 1.0 PR.
- Keep company/IČO as `INCLUDE_AS_SEED_BACKED`; alias permanence is currently resolved in favor of retaining `/v1/ico/{ico}`.
- Freeze candidate v1 API contract and resolve response-shape decisions.
- Complete production deployment and smoke-test release checklist.
