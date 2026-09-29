# Public Procurement Notice Source Research

Date checked: 2026-09-29

## Acquisition decision

Acquisition decision: PRODUCTION_IMPORT_APPROVED

Coverage decision: TED_PARTIAL

Final report: Acquisition decision: PRODUCTION_IMPORT_APPROVED
Coverage decision: TED_PARTIAL

Research-paper Phase 3 public-procurement status: partially implemented through TED

## Phase 3 mapping

This milestone targets the research-paper Phase 3 `public procurement` item. It does not replace the national ÚVO register and does not claim complete Slovak procurement coverage.

## Official source candidates

- National authority: Úrad pre verejné obstarávanie (ÚVO)
- National portal: https://www.uvo.gov.sk/
- ÚVO procurement-notice portal pages: https://www.uvo.gov.sk/verejny-obstaravatel-obstaravatel/vestnik and https://www.uvo.gov.sk/zaujemca-uchadzac/vestnik
- TED Search API:https://api.ted.europa.eu/v3/notices/search
- TED API documentation: https://docs.ted.europa.eu/api/latest/ and https://docs.ted.europa.eu/api/latest/search.html
- TED reuse documentation: https://docs.ted.europa.eu/ODS/latest/reuse/
- TED legal notice: https://ted.europa.eu/en/legal-notice
- National open-data catalogue: https://data.gov.sk/
- EU open-data catalogue: https://data.europa.eu/

## ÚVO findings

The ÚVO website is reachable and contains official public procurement publication information, electronic forms guidance, vestník pages, procurement dictionaries, and links to national registers. The checked pages describe the national publication process and are the appropriate authority for Slovak national procurement notices.

A production-ready national machine-readable ÚVO distribution was not verified in this environment:

- no current anonymous bulk notice archive was verified;
- no documented current CSV, XML, JSON, or stable downloadable notice distribution with clear field definitions was found from the checked page links;
- `https://www.uvo.gov.sk/open-data` and `https://www.uvo.gov.sk/otvaranie-udajov` returned portal pages, but no machine-readable notice distribution link was identified from the page HTML;
- OpenAPI guesses under `/api`, `/api/openapi.json`, `/api/v3/api-docs`, `/openapi.json`, and `/ext-portal/openapi.json` returned portal HTML or a JSON 404 for an unknown endpoint;
- `https://www.uvo.gov.sk/robots.txt` disallows general crawling for `User-agent: *`, so HTML scraping is not acceptable for OpenSK acquisition;
- `data.gov.sk` search attempts returned the JavaScript application shell in this environment, not a verified machine-readable distribution.

Therefore `Coverage decision: NATIONAL` is not justified for 0.19.0.

## TED findings

TED provides an official public Search API and notice XML/PDF links. The OpenAPI is exposed at `https://api.ted.europa.eu/api-v3.yaml` and documents `PublicExpertSearchRequestV1` body properties including `query`, `fields`, `page`, `limit`, `paginationMode`, `onlyLatestVersions`, and `iterationNextToken`.

Verified request details:

- Slovak buyer-country query value is `SVK`; `SK` is rejected by the API as an unsupported country value.
- A live anonymous request with query `buyer-country = SVK` returned HTTP 200 with `totalNoticeCount: 74693` on 2026-09-29.
- Sorting by latest notices works with expert query syntax: `buyer-country = SVK SORT BY publication-date DESC`.
- Publication-date query values use compact `YYYYMMDD`, not `YYYY-MM-DD`.
- The public API supports page-number pagination up to 15,000 notices and iteration pagination for larger result sets.
- Normal API responses include a `links.xml.MUL` URL for each notice. The milestone stores this source link but does not fetch or serve raw notice XML at runtime.
- An initial live latest-notice result on 2026-09-29 had publication number `669481-2026`; the final bounded 100-notice snapshot acquired later the same day begins with publication number `670654-2026`, publication date `2026-09-29`, buyer country `SVK`, and notice type `can-standard`.

The checked TED Search API fields used for the normalized OpenSK snapshot are all public notice-reference fields:

- `publication-number`
- `publication-date`
- `dispatch-date`
- `notice-type`
- `notice-title`
- `buyer-name`
- `buyer-country`
- `place-of-performance-city-proc`
- `place-of-performance-post-code-proc`
- `place-of-performance-country-proc`
- `deadline-date-lot`

No street address, personal contact, phone, email, organisation identifier, winner, tenderer, subcontractor, beneficial-owner, or natural-person field is imported.

## Licence and reuse

TED legal and reuse documentation was checked from the official domain. TED/SIMAP reuse documentation and the legal notice support the use of TED notices with attribution, while the exact notice wording and attribution requirements should be retained with the source evidence.

OpenSK stores only a small normalized reference snapshot derived from the public Search API response. It links back to the TED XML URL and clearly identifies the snapshot as `TED_PARTIAL`, not the national ÚVO register.

Required attribution wording for this dataset:

`Source: TED (Tenders Electronic Daily), EU Open Data Portal; OpenSK normalized reference snapshot, partial Slovak-buyer coverage.`

## Privacy decision

OpenSK procurement scope is institutional notice-reference data only:

- TED publication number
- notice title
- notice type
- publication and dispatch dates
- buyer institutional names
- buyer country
- place-of-performance city, postal code, and country where present as procedure-level reference fields
- tender deadline date where present
- TED source URL

Excluded by default:

- personal names and contact persons
- phone, fax, email, and internet/contact fields
- street-level addresses
- organisation identifiers unless separately justified
- winner/tenderer/subcontractor names and countries
- beneficial-owner fields
- lot-level descriptive text, performance/pricing details, and procedural legal narrative
- raw XML/PDF/HTML notice body storage

TED search responses can contain broad multilingual values. The importer selects Slovak or English title/buyer display values only and rejects unexpected personal/contact/address keys before writing.

## Coverage decision

Coverage is `TED_PARTIAL`:

- It includes TED notices where TED Search API reports `buyer-country = SVK`.
- It does not claim to include below-threshold national-only ÚVO vestník notices.
- It does not claim to be a legal national procurement register snapshot.
- Geography is not linked to local municipality/district/region codes in 0.19.0 because TED procedure-level city/postal fields do not provide stable official municipality identifiers.

The checked live source reported 74,693 historical Slovak-buyer notices. The checked-in 0.19.0 snapshot intentionally contains the latest 100 notices returned by the API at acquisition time to keep the local static dataset small and reviewable.

## Candidate normalized record

```json
{
  "id": "669481-2026",
  "title": "Slovensko – Stavebné práce ...",
  "noticeType": "can-standard",
  "publicationDate": "2026-09-29",
  "dispatchDate": "2026-09-26",
  "buyerNames": ["SLOVENSKÝ VODOHOSPODÁRSKY PODNIK, š.p."],
  "buyerCountry": "SK",
  "placeOfPerformance": {
    "city": null,
    "postalCode": null,
    "country": "SK"
  },
  "tenderDeadline": null,
  "regionCode": null,
  "districtCode": null,
  "municipalityCode": null,
  "sourceUrl": "https://ted.europa.eu/en/notice/669481-2026/xml"
}
```

Dates are normalized to `YYYY-MM-DD` by removing the TED timezone suffix. TED country `SVK` is normalized to OpenSK country code `SK` while provenance remains documented in metadata and source research.

## Endpoint decision

0.19.0 adds a conservative read-only endpoint surface backed only by the checked-in static snapshot:

- `GET /v1/procurement-notices`
- `GET /v1/procurement-notices/{id}`
- `GET /v1/procurement-notices/search?q=...`
- `GET /v1/procurement-notices/stats`

List filters are intentionally narrow: `noticeType`, `year`, `limit`, and `offset`.

Runtime behavior remains local. No API request calls TED, ÚVO, XML/PDF links, or any upstream service.

## Remaining blockers

- Verify a current anonymous machine-readable ÚVO national notice distribution with explicit reuse/redistribution terms before changing coverage to `NATIONAL`.
- Retain exact TED legal-notice and attribution wording as local evidence when the release process requires it.
- Verify an official reliable mapping between TED place-of-performance city/postal fields and local municipality codes before adding geography links.
- Revisit privacy if future fields include winners, contact points, organization identifiers, addresses, or narrative notice text.
