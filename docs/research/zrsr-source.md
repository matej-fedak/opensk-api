# ŽRSR Source Research

Date checked: 2026-09-29

## Acquisition decision

Acquisition decision: RESEARCH_AND_TOOLING_ONLY

Machine-readable source gate: SOURCE_ACCESS_BLOCKED

Licence/reuse gate: REUSE_BLOCKED

Privacy gate: PRIVACY_BLOCKED

Acquisition reproducibility gate: ACQUISITION_BLOCKED

Research-paper Phase 2 ŽRSR status: blocked / no safe machine-readable source

## Official source

- Official public site: https://www.zrsr.sk/
- Alternate hostname checked: https://zrsr.minv.sk/
- Operator: Ministerstvo vnútra Slovenskej republiky
- Register: Živnostenský register Slovenskej republiky

The reachable public site is a human-facing search interface. It supports search dimensions such as IČO, business/trade name, natural-person name/surname, municipality/address, and active-record filtering. It is not treated as a machine-readable source.

## Source discovery findings

- `https://www.zrsr.sk/` returned HTML with title `Vyhľadávanie v živnostenskom registri - Zivnostensky register Slovenskej republiky` by direct request.
- `https://zrsr.minv.sk/` failed TLS trust validation in the local research environment.
- The markdown web fetcher could not fetch either ŽRSR hostname.
- Common discovery URLs such as `/robots.txt`, `/sitemap.xml`, `/openapi.json`, and `/swagger.json` did not expose a documented API or distribution.
- `https://www.zrsr.sk/?wsdl` returned the same HTML search page, not a WSDL document.

No official bulk export, open-data dataset, documented REST API, documented SOAP/WSDL endpoint, CSV/XML/JSON distribution, or downloadable archive was verified.

## data.gov.sk findings

The national open-data catalogue web app returned a JavaScript shell through the available fetch tools. Attempts to query `https://data.gov.sk/api/action/package_search` for terms including `Živnostenský register`, `živnostenské oprávnenia`, `register živností`, and `Ministerstvo vnútra živnostenský` returned HTML rather than usable catalogue JSON in this environment.

No verified working data.gov.sk dataset distribution was found for ŽRSR during this milestone.

## Electronic-service/API findings

The MV SR site links to electronic services at `https://portal.minv.sk/`, but no public anonymous documented ŽRSR bulk, list, lookup, XML, JSON, REST, or SOAP acquisition route suitable for OpenSK offline import was verified.

If a future SOAP/WSDL or integration service exists but requires eID, government credentials, private network access, client certificates, or registered integration access, it should remain unsuitable for OpenSK public offline acquisition unless a separate public route is documented.

## Licence and reuse

No current machine-readable source licence was verified.

Public search visibility is not treated as permission to cache, transform, redistribute, or allow commercial downstream reuse. Exact reuse, caching, transformation, attribution, redistribution, and commercial-use terms remain blocked/pending.

## Privacy classification

ŽRSR visibly supports searching natural-person entrepreneurs and address-like fields. Potential data categories include:

| Field category | Classification | 0.16.0 policy |
| --- | --- | --- |
| IČO | conditionally acceptable | Future safe lookup key if source/privacy gates pass |
| Trade registration status | conditionally acceptable | Future candidate field |
| Trade activity names/codes | conditionally acceptable | Future candidate field if verified in source |
| Establishment/termination dates | conditionally acceptable | Future candidate field |
| Source register | safe reference | Future candidate field |
| Natural-person name | personal | Excluded |
| Residence/private address | personal | Excluded |
| Birth data or personal identifiers | personal | Excluded |
| Personal contacts | personal | Excluded |
| Responsible representatives or related persons | personal/role-holder | Excluded |
| Operating premises address | conditionally acceptable | Not included by default; needs separate privacy review |

Natural-person entrepreneurs remain excluded by default. No deterministic machine-readable legal/natural subject discriminator was verified, and heuristics based on name shape, suffixes, punctuation, or capitalization are not acceptable.

## RPO overlap

Current checked-in company data is seed-backed and does not satisfy ŽRSR coverage.

RPO research indicates that future verified RPO data may include source register and activity-related fields, but 0.14.0 did not approve RPO production acquisition. RPO is therefore not treated as a ŽRSR substitute in 0.16.0. A future verified RPO snapshot could potentially satisfy part of the research-paper functional intent only if source provenance explicitly identifies ŽRSR-origin records and the required trade fields are present with privacy filtering.

## Third-party sources

No third-party mirror was promoted. Third-party use would require verified provenance, original source, update schedule, licensing, redistribution rights, field transformations, and natural-person handling. Discovery remains research-only.

## Importer and endpoint decision

No importer was added because no real documented machine-readable source shape was verified.

No production dataset was added.

No public endpoint was added.

If all gates pass in a future milestone, the preferred canonical endpoint should be evaluated as `GET /v1/trades/{ico}`. No `/v1/zrsr/{ico}` alias should be added automatically.
