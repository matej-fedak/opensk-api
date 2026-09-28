# RPO Acquisition Decision

Date checked: 2026-09-18

Decision: `RESEARCH_AND_TOOLING_ONLY`

## Source Decision Report

1. Current official RPO operator: the current RPO portal identifies the Ministry of Interior SR (`Ministerstvo vnútra Slovenskej republiky`) as operator; historical API documentation still references ŠÚ SR infrastructure.
2. Current official RPO portal: `https://rpot.statistics.sk/` and `https://rpo.statistics.sk/` render the current JavaScript RPO portal.
3. Licence statement and exact evidence: the public RPO API/OpenAPI documentation references `Creative Commons Attribution 4.0 (CC BY 4.0)` with URL `https://creativecommons.org/licenses/by/4.0/legalcode`; exact official portal-visible licence evidence still needs retained browser/manual capture before production promotion.
4. Available official REST documentation: Apiary metadata for `https://susrrpo.docs.apiary.io/` exposes production base `https://api.statistics.sk/rpo/v1/`. Slovensko.Digital documentation mirrors an OpenAPI description and examples.
5. Verified REST base URL(s): `https://api.statistics.sk/rpo/v1/` is documented as production in Apiary/OpenAPI-derived material.
6. Whether single-IČO lookup works: documented search flow is `GET /search?identifier={ico}` followed by `GET /entity/{id}`. Live verification from this environment was inconclusive due timeout/transport constraints, so production tooling must not rely on it yet.
7. Whether pagination/listing exists: search documentation says results are capped at 500 and there is no pagination.
8. Whether broad/bulk export exists: Slovensko.Digital documentation describes object-storage `batch-init` and `batch-daily` compressed JSON exports, but this was not verified as an official MV SR/ŠÚ SR bulk publication with clear redistribution terms.
9. Whether bulk collection is explicitly supported or reasonably intended: official REST search is not suitable for broad collection because it has no pagination and requires filters. The third-party/local-storage path may be suitable later only after provenance and reuse terms are verified.
10. Rate-limit information: no official rate-limit terms were retained in this pass.
11. Data freshness/update cadence: documentation indicates REST/local-storage data refreshes overnight and may lag up to 24 hours; mirror local-storage docs describe monthly init batches and daily incremental batches retained for about 45 days.
12. Entity-type coverage: RPO covers legal entities, entrepreneurs, and public authorities; upstream records can include natural-person entrepreneurs, statutory bodies, stakeholders, organisational units, and other role/person data.
13. Privacy-sensitive fields present upstream: upstream detail schemas include statutory bodies, stakeholders, person names, addresses, authorizations, and related role data.
14. Whether legal entities can be isolated safely: likely possible from RPO fields such as legal form/source register, but not verified enough for production filtering. OpenSK policy remains to exclude natural-person entrepreneur/person-like records by default.
15. Whether a reproducible local snapshot can be produced: not yet for OpenSK production. A future snapshot may be possible from a verified official bulk export or verified mirror, but that gate has not passed.
16. Estimated dataset size: unknown for a safe OpenSK production snapshot. Mirror docs imply multi-part compressed init batches and a full register scale that must be measured before committing any production JSON.
17. Recommended acquisition strategy: keep production company data seed-backed for 0.14.0; harden importer/privacy validation; continue source verification for official bulk or verified mirror before data promotion.

Decision: `RESEARCH_AND_TOOLING_ONLY`

## Production Promotion Gate

`data/companies.json` must not be replaced until all of these are true: acquisition source verified, acquisition method documented, licence/reuse documented, privacy scope approved, natural-person policy documented, importer deterministic, forbidden personal fields excluded, dataset validation passes, duplicate IČOs resolved, production file size assessed, tests pass, and docs updated.
