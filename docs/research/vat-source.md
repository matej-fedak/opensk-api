# VAT Registration Source Research

Date checked: 2026-09-28

## Acquisition decision

Acquisition decision: RESEARCH_AND_TOOLING_ONLY

Source gate: SOURCE_IMPORT_APPROVED

Privacy gate: PRIVACY_IMPORT_BLOCKED

## Official source

- Dataset name: Zoznam daňových subjektov registrovaných pre DPH
- Operator/source: Finančná správa Slovenskej republiky / Finančné riaditeľstvo SR
- Online list: https://www.financnasprava.sk/sk/elektronicke-sluzby/verejne-sluzby/zoznamy/detail/_101c6128-e1f6-4a48-81ed-ad3c01220e03
- Export page: https://www.financnasprava.sk/sk/elektronicke-sluzby/verejne-sluzby/zoznamy/exporty-z-online-informacnych
- Exact ZIP URL: https://report.financnasprava.sk/ds_dphs.zip
- Open Data catalogue: https://opendata.financnasprava.sk/opendata/show/zoznam-danovych-subjektov-registrovanych-pre-dph1
- Open Data API docs: https://opendata.financnasprava.sk/page/openapi

## Current export evidence

- ZIP status: HTTP 200 by HEAD request
- ZIP size: 14,277,628 bytes
- ZIP Last-Modified: Mon, 28 Sep 2026 00:36:37 GMT
- ZIP content type: application/zip
- ZIP contents: `ds_dphs.xml`, `ds_dphs.xsd`
- XML size: 126,325,913 bytes
- XML filename: `ds_dphs.xml`
- XSD filename: `ds_dphs.xsd`
- XML root: `ZoznamSubjektovRegistrovanychkDPH`
- Record element: `ITEM` under `DS_DPHS`
- Source update date in XML: `28092026`, normalized as `2026-09-28`
- Online-list page displayed `Posledná aktualizácia dát: 28. 9. 2026`
- Update cadence: daily according to Open Data FS API documentation
- XML record count checked: 317,233 `ITEM` records

## XML fields discovered

- `IC_DPH`
- `ICO`
- `NAZOV_DS`
- `OBEC`
- `PSC`
- `ULICA_CISLO`
- `STAT`
- `DRUH_REG_DPH`
- `DATUM_REG`
- `DATUM_ZMENY_DRUHU_REG`
- `PLAT_DPH_OD`

Observed registration types:

- `§4`: 226,320
- `§7a`: 74,902
- `§5`: 9,405
- `§7`: 5,141
- `§4b`: 1,465

Observed data-quality counts from the 2026-09-28 XML:

- Missing IČO: 11,475
- Invalid IČO: 25
- Missing IČ DPH: 0
- Invalid IČ DPH by local format check: 0
- Duplicate IČO among non-empty exact IČO values: 0
- Duplicate IČ DPH values: 126
- Multiple registrations per IČO: 0 in this snapshot
- Source date format: `DDMMYYYY`
- Record date format: `DD.MM.YYYY`

## Licence evidence

The current PFS export page states that all data in the first informational-list group, including `Zoznam daňových subjektov registrovaných pre DPH`, is published under CC0 and links to http://creativecommons.org/publicdomain/zero/1.0/.

The Open Data FS catalogue entry for the same dataset lists `Licencia: CC 4.0 international`.

Most authoritative current interpretation for the exact ZIP export is the current PFS export-page CC0 statement, because it appears directly below the downloadable ZIP group that contains `ds_dphs.zip`. The catalogue discrepancy is retained and not hidden. Production promotion is nevertheless blocked by privacy, not by acquisition/licence.

## Privacy decision

The XML includes natural persons, legal entities, names, municipalities, postal codes, street/address text, and state. The schema has no reliable natural/legal subject marker. It exposes only one combined name field, `NAZOV_DS`, and does not split first name, surname, legal-entity name, or subject type.

Natural persons cannot be excluded deterministically from the current XML without heuristics such as company suffixes or name-shape detection. Those heuristics are not acceptable for production privacy handling.

For 0.15.0, generated tooling output omits names and addresses, but production `data/vat_registrations.json` is not promoted because the source can still include natural-person entrepreneurs by IČO/IČ DPH and the privacy policy has not approved that minimum-data exposure.

## Endpoint decision

No public endpoint is added in 0.15.0.

Preferred future canonical endpoint remains `GET /v1/vat/{ico}` if privacy and production import are approved later.

The Slovak alias `GET /v1/dph/{ico}` is not added in 0.15.0. The current API generally prefers English resource names, and adding duplicate aliases would enlarge the eventual frozen contract without a compatibility need.

## Runtime impact

No production VAT JSON is checked in, so there is no runtime load/startup impact in 0.15.0.

The official XML is about 126 MB and the ZIP is about 14 MB. A future production promotion must measure normalized JSON size before committing data or adding a service.
