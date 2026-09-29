# Streets / Register Adries Source Research

Date checked: 2026-09-29

## Acquisition decision

Acquisition decision: RESEARCH_AND_TOOLING_ONLY

Research-paper Phase 3 streets status: blocked

## Phase 3 mapping

This milestone targets the research-paper Phase 3 `streets / address data` item. It does not add another domain.

## Official source candidates

- Primary official system: Register adries
- Operator: Ministerstvo vnútra Slovenskej republiky
- MV overview page: https://pes.minv.sk/wps/wcm/connect/sk/site/main/zivotne-situacie/Register%20adries/uvod-register%20adries
- MV reference-data page: https://pes.minv.sk/wps/wcm/connect/sk/site/main/zivotne-situacie/Register%2Badries/poskytovanie_referencnych_udajov/
- National catalogue: https://data.gov.sk/
- Secondary source candidate: https://registeradries.sk/ and https://registeradries.sk/api_doc

## data.gov.sk findings

Search attempts for `register adries`, `ulica`, `ulice`, `adresný bod`, and `Ministerstvo vnútra register adries` through the available `data.gov.sk` API paths returned the JavaScript application shell as HTML, not usable catalogue JSON.

No working data.gov.sk distribution URL was verified in this environment. No production acquisition was approved from catalogue metadata alone.

## MV Register adries findings

Direct requests to the MV pages returned official HTML pages:

- `Register adries | Ministerstvo vnútra Slovenskej republiky`
- `Poskytnutie referencnych údajov z Registra adries | Ministerstvo vnútra Slovenskej republiky`

The MV content describes Register adries as a central reference register and lists reference-data services. It also describes an address-point dataset service for a municipality or municipal part.

The dataset service is documented as an electronic service that produces data for a requested municipality/municipal part and sends the result to the user's electronic mailbox on the central public administration portal. The page identifies eID/no-eID service categories; the dataset workflow is not an anonymous reproducible bulk download suitable for automated OpenSK refresh.

No public anonymous bulk download, national street export, stable distribution index, WSDL/schema suitable for offline acquisition, or documented open-data API was verified.

## registeradries.sk findings

`https://registeradries.sk/api_doc` documents a JSON POST API requiring `api_key`. It includes endpoints for regions, districts, municipalities, municipal parts, streets, house numbers, orientation numbers, postal codes, and coordinates.

The documented street endpoints include:

- `zoznam_ulic`
- `detail_ulica`

The API examples include fields such as `id_ulica`, `ulica`, `id_obec`, `id_cast_obce`, `kod_okresu`, and `kod_kraja`.

The site footer identifies `Virtuality, s. r. o.` and OpenStreetMap contributors. This is a separate source candidate with an API-key model and its own operator/terms. It was not approved as an official MV production source. Provenance, source freshness, API-key terms, caching, transformation, redistribution, attribution, and commercial downstream rights remain unverified.

## Licence and reuse

No production-compatible licence or reuse grant was verified for a local OpenSK streets snapshot.

Public reference status, human-readable pages, authenticated mailbox delivery, or third-party API documentation are not treated as permission to cache, transform, redistribute, or permit commercial downstream use.

## Scope decision

The preferred future OpenSK scope remains street names linked to municipalities, districts, and regions. Full address-point data is not needed for 0.17.0 and should not be exposed by default.

## Candidate future data model

Only if a production source is approved, a minimal candidate record is:

```json
{
  "id": "official-source-street-id",
  "name": "Hlavná",
  "municipalityCode": "123456",
  "municipalPart": null,
  "districtCode": "SK....",
  "regionCode": "SK...",
  "country": "SK"
}
```

Do not invent IDs. Only expose `id` if the selected upstream source documents a stable street identifier.

## Privacy decision

Street names and administrative geography links are generally reference data. Full address-point records can include house numbers, coordinates, and residence-level location data. 0.17.0 therefore defaults to streets and administrative links only and does not import or expose building coordinates, house numbers, apartment information, or person-linked address data.

## Endpoint decision

No public endpoint is added in 0.17.0.

If all gates pass in a future milestone, the preferred route surface is `GET /v1/streets` with filters such as `municipalityCode`, `districtCode`, `regionCode`, `q`, `limit`, and `offset`. A detail route should only be added if a stable official street identifier is verified.

## Final blocker

Find a working official data.gov.sk distribution, MV-authorized bulk export, or other authoritative machine-readable source with clear reuse rights, reproducible non-scraping refresh, documented identifiers, and privacy-safe street-only scope before adding importer, dataset, service, or endpoint code.
