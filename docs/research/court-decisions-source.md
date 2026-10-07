# Slovak Court Decisions Source Research

Date checked: 2026-10-07

## Acquisition Decision

Acquisition decision: RESEARCH_AND_TOOLING_ONLY

Text decision: NO_PRODUCTION_DATA

Research-paper Phase 3 court-decisions status: blocked for production import

## Phase 3 Mapping

This milestone targets a future Slovak court-decisions endpoint. It does not add a production dataset, importer, or public route.

Do not add `GET /v1/court-decisions`, `GET /v1/court-decisions/{id}`, `GET /v1/court-decisions/search`, `data/court_decisions.json`, or court-decision fetch/import tooling until the production gates below pass.

## Official Source Candidates

- Ministry open-data page: `https://www.justice.gov.sk/sluzby/registre/otvorene-data/`
- Ministry Swagger UI: `https://obcan.justice.sk/pilot/api/ress-isu-service/swagger-ui/index.html`
- Ministry OpenAPI config: `https://obcan.justice.sk/pilot/api/ress-isu-service/v3/api-docs/swagger-config`
- Ministry OpenAPI spec: `https://obcan.justice.sk/pilot/api/ress-isu-service/v3/api-docs`
- Ministry public decisions page: `https://www.justice.gov.sk/sudy-a-rozhodnutia/sudy/rozhodnutia`
- Ministry courts and decisions overview: `https://www.justice.gov.sk/sudy-a-rozhodnutia/`
- Constitutional Court site: `https://www.ustavnysud.sk/`
- Constitutional Court search guidance: `https://www.ustavnysud.sk/ako-hladat`
- National open-data catalogue search attempts through `data.gov.sk`

## Ministry API Findings

The Ministry open-data page confirms that Ministry data is available through OpenAPI and Swagger UI. The page links the Swagger UI and says extended data or external-system integration requests should contact `servicedesk.mssr@justice.sk`.

The Swagger initializer exposes the OpenAPI config URL:

`https://obcan.justice.sk/pilot/api/ress-isu-service/v3/api-docs/swagger-config`

The config points to the OpenAPI spec:

`https://obcan.justice.sk/pilot/api/ress-isu-service/v3/api-docs`

The OpenAPI document identifies these relevant decision endpoints under tag `rozhodnutie`, described as services for decision list/detail:

- `GET /v1/rozhodnutie`
- `GET /v1/rozhodnutie/{id}`
- `GET /v1/rozhodnutie/autocomplete`

The spec has no top-level `security` entry and no `components.securitySchemes`, so the documented endpoints appear anonymous in the spec.

Relevant `GET /v1/rozhodnutie` search parameters include:

- `query`
- `typSuduFacetFilter`
- `krajFacetFilter`
- `okresFacetFilter`
- `odkazovanePredpisy`
- `oblastPravnejUpravyFacetFilter`
- `podOblastPravnejUpravyFacetFilter`
- `formaRozhodnutiaFacetFilter`
- `povahaRozhodnutiaFacetFilter`
- `vydaniaOd`
- `vydaniaDo`
- `ecli`
- `spisovaZnacka`
- `cisloSpisu`
- `guidSudca`
- `guidSud`
- `indexDatumOd`
- `indexDatumDo`
- `sortProperty`
- `sortDirection`
- `page`
- `size`

Useful metadata-like response schemas and fields include:

- `RozhodnutieListResponse`: `numFound`, `page`, `size`, `updateDate`, `filterList`, `rozhodnutieList`
- `BaseRozhodnutie`: `guid`, `formaRozhodnutia`, `povaha`, `sud`, `sudca`, `identifikacneCislo`, `spisovaZnacka`, `datumVydania`, `zvyraznenie`
- `Rozhodnutie`: `ecli`, `oblast`, `podOblast`, `odkazovanePredpisy`, `dokument`, `povodnySud`, `povodnaSpisovaZnacka`
- `RozhodnutieAutocompleteObject`: `guid`, `forma`, `sud`, `spisovaZnacka`

Related court endpoints exist under tags such as `sud`, `sudca`, and `obcianPojednavania`. These were not approved for production import in this milestone because the target is court decisions and the same reuse/privacy gates apply.

## Constitutional Court Findings

The Constitutional Court guidance page documents public search features for decisions, the collection of findings and resolutions, dates, case numbers, proceeding types, ECLI, legal provisions, and subject keywords. It confirms ECLI semantics for Constitutional Court decisions and gives examples such as `ECLI:SK:USSR:2002:4.US.14.2002.1`.

No documented anonymous machine-readable API, bulk export, feed, or open-data distribution was verified for Constitutional Court decisions in this milestone. Constitutional Court data is therefore not approved for production import.

## Licence And Reuse Decision

Production import is blocked. The Ministry API is official and documented, but the checked pages did not verify explicit terms for local caching, transformation, public redistribution, downstream commercial use, attribution, or retention of derived snapshots by OpenSK.

The national open-data catalogue API/search attempts returned the JavaScript application shell in this environment, not verifiable dataset metadata or distributions with reusable court-decision terms.

Public availability through a search API is not treated as permission to cache, transform, and redistribute a checked-in public dataset. The milestone therefore stays `RESEARCH_AND_TOOLING_ONLY`.

## Privacy Decision

Court decisions can contain personal data and sensitive case facts even when published. Full text is not approved.

Potential privacy-risk fields in the inspected API include:

- judge/person names such as `sudca.meno`, `krstneMeno`, and `priezvisko`
- participant arrays such as `navrhovatelia`, `odporcovia`, and `obzalovani`
- addresses and contact fields such as `adresa`, `adresaString`, `email`, and `telKontakty`
- case identifiers such as `spisovaZnacka`, `identifikacneCislo`, `cisloSpisu`, and `ecli`
- text-bearing or document fields such as `predmet`, `poznamky`, `zvyraznenie`, and `dokument`

Future production scope, if reuse is approved, must be metadata-only and must recursively exclude participant names, representatives, lawyers, judges unless separately approved, addresses, emails, phones, IBANs, bank accounts, birth data, identity documents, personal identifiers, raw participant structures, snippets/highlights, and full text.

Future code must not attempt de-anonymization, identity inference, correlation to other registers, address reconstruction, or participant fingerprinting.

## Future Candidate Shape

If reuse and privacy gates pass later, a production record should prefer a minimal metadata shape:

```json
{
  "id": "...",
  "ecli": "ECLI:SK:...",
  "court": {
    "id": "...",
    "name": "..."
  },
  "caseNumber": "...",
  "decisionType": "...",
  "agenda": "...",
  "decidedOn": "YYYY-MM-DD",
  "publishedOn": null,
  "finality": null,
  "sourceUrl": "...",
  "textAvailable": true
}
```

Do not include full text, snippets, document bodies, party lists, representatives, addresses, contact details, bank/payment identifiers, birth data, identity-document data, or person identifiers by default.

## Endpoint Decision

No production endpoint is added in 0.22.0.

Do not add `/v1/court-decisions` until all of these gates pass:

- authoritative source confirmed
- documented machine-readable acquisition confirmed
- licence/reuse/redistribution/commercial-use/caching/transformation terms verified
- strict metadata-only privacy projection defined and tested
- full-text exclusion enforced unless separately approved
- exact published-decision scope known

## Remaining Blockers

- Verify Ministry API reuse terms for caching, transformation, attribution, redistribution, commercial downstream use, and retained local snapshots.
- Verify whether `data.gov.sk` exposes a court-decision distribution with machine-readable metadata and clear licence terms.
- Verify whether the Ministry API supports a stable source URL per decision without exposing full text or personal fields.
- Verify exact field semantics for `guid`, `ecli`, court identifiers, case numbers, decision form/type, decision date, publication/index date, and document availability.
- Verify the published-decision scope and exclusions for general courts, administrative courts, Supreme Court, Supreme Administrative Court, and any historical/abolished courts.
- Verify whether Constitutional Court decisions have an approved API/export/feed or must remain excluded.
- Define and test a recursive privacy denylist before any generated output is promoted.
