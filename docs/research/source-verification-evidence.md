# Source Verification Evidence

This log records evidence checked for source and licence decisions. It is intentionally conservative and does not create legal certainty by itself.

## 2026-09-28 VAT Registrations

- Official source: Finančná správa SR `Zoznam daňových subjektov registrovaných pre DPH`.
- Online list: `https://www.financnasprava.sk/sk/elektronicke-sluzby/verejne-sluzby/zoznamy/detail/_101c6128-e1f6-4a48-81ed-ad3c01220e03`.
- Export page: `https://www.financnasprava.sk/sk/elektronicke-sluzby/verejne-sluzby/zoznamy/exporty-z-online-informacnych`.
- Exact ZIP URL: `https://report.financnasprava.sk/ds_dphs.zip`.
- HEAD check: HTTP 200, 14,277,628 bytes, `Last-Modified: Mon, 28 Sep 2026 00:36:37 GMT`.
- ZIP contents inspected offline: `ds_dphs.xml` and `ds_dphs.xsd`.
- XML source update date: `28092026`, normalized to `2026-09-28`.
- Licence evidence: current PFS export page states CC0 for the relevant informational-list group; Open Data FS catalogue lists `CC 4.0 international`.
- Privacy blocker: XML has no natural/legal subject marker and includes combined name/address fields.

## 2026-09-29 ŽRSR / Trade Registrations

- Official public site: `https://www.zrsr.sk/`.
- Alternate hostname checked: `https://zrsr.minv.sk/`.
- Operator: Ministerstvo vnútra Slovenskej republiky.
- Direct request to `https://www.zrsr.sk/` returned HTML search page title `Vyhľadávanie v živnostenskom registri - Zivnostensky register Slovenskej republiky`.
- `https://zrsr.minv.sk/` failed TLS trust validation in the local research environment.
- `robots.txt`, `sitemap.xml`, `openapi.json`, and `swagger.json` did not expose an approved source; `?wsdl` returned HTML, not WSDL.
- `data.gov.sk` catalogue/API attempts returned an HTML JavaScript shell in this environment, not verified dataset JSON.
- Result: no official machine-readable source, licence/reuse permission, non-scraping acquisition route, or deterministic privacy strategy verified.

## 2026-09-29 Streets / Register Adries

- MV overview page checked by direct request: `https://pes.minv.sk/wps/wcm/connect/sk/site/main/zivotne-situacie/Register%20adries/uvod-register%20adries`.
- MV reference-data page checked by direct request: `https://pes.minv.sk/wps/wcm/connect/sk/site/main/zivotne-situacie/Register%2Badries/poskytovanie_referencnych_udajov/`.
- MV pages returned official HTML and describe Register adries services and an address-point dataset service for a municipality or municipal part.
- Dataset workflow is described as electronic service/mailbox delivery, not an anonymous reproducible bulk download.
- `data.gov.sk` search/API attempts for Register adries/street terms returned HTML application shell in this environment; no working distribution URL was verified.
- `https://registeradries.sk/api_doc` documents a JSON API requiring `api_key`, including street and address-point endpoints, but footer identifies `Virtuality, s. r. o.` and OpenStreetMap contributors; it was treated as a separate third-party candidate and not approved for production.

## 2026-09-29 Public Procurement Notices

- ÚVO public portal pages checked by direct request: `https://www.uvo.gov.sk/`, `https://www.uvo.gov.sk/verejny-obstaravatel-obstaravatel/vestnik`, `https://www.uvo.gov.sk/zaujemca-uchadzac/vestnik`, `https://www.uvo.gov.sk/open-data`, and `https://www.uvo.gov.sk/otvaranie-udajov`.
- ÚVO page/API guesses did not expose a current anonymous machine-readable national notice distribution; guesses under `/api/openapi.json`, `/api/v3/api-docs`, `/openapi.json`, and `/ext-portal/openapi.json` returned portal HTML or JSON 404.
- ÚVO `robots.txt` checked at `https://www.uvo.gov.sk/robots.txt`; it includes `User-agent: *\nDisallow: /`, so scraping HTML is not an acceptable acquisition route.
- TED Search API OpenAPI checked at `https://api.ted.europa.eu/api-v3.yaml`; it documents `PublicExpertSearchRequestV1` with `query`, `fields`, `page`, `limit`, `paginationMode`, `onlyLatestVersions`, and `iterationNextToken`.
- Live anonymous TED Search API query `buyer-country = SVK` returned HTTP 200 with `totalNoticeCount = 74693` on 2026-09-29.
- Live anonymous latest-notice query `buyer-country = SVK SORT BY publication-date DESC` returned publication number `669481-2026`, publication date `2026-09-29+02:00`, dispatch date `2026-09-26+02:00`, buyer country `SVK`, and notice type `can-standard`.
- TED Search API date values use compact `YYYYMMDD`; TED country filtering uses `SVK`, not `SK`.
- TED reuse/legal pages checked by direct request: `https://docs.ted.europa.eu/ODS/latest/reuse/`, `https://ted.europa.eu/en/legal-notice`, and `https://ted.europa.eu/en/simap/developers-corner-for-reusers`.
- Production decision: a small normalized 100-record TED_PARTIAL institutional notice-reference snapshot is approved; national ÚVO coverage remains unverified.

## 2026-09-29 Healthcare Facilities / Providers

- NCZI NR PZS page checked by direct request: `https://www.nczisk.sk/Registre/Narodne-administrativne-registre/Narodny-register-poskytovatelov-zdravotnej-starostlivosti/Pages/default.aspx`.
- NCZI page confirms NR PZS as the national administrative register of healthcare providers and lists provider categories and upstream register sources, but no public record-level bulk/API/export route was verified.
- NCZI `Siet poskytovatelov zdravotnej starostlivosti` page checked by direct request: `https://www.nczisk.sk/Statisticke_vystupy/Tematicke_statisticke_vystupy/Siet_poskytovatelov_zdravotnej_starostlivosti/Pages/default.aspx`.
- NCZI statistical page exposes XLSX/ODS aggregate statistical outputs by Slovak Republic and region, derived partly from NR PZS, but not a facility directory with IdZZ and operating addresses.
- e-VUC portal checked by direct request: `https://www.e-vuc.sk/` and `https://www.e-vuc.sk/o-portali-e-vuc.html?page_id=199`.
- e-VUC presents healthcare directory content for all eight self-governing regions and describes source data from self-governing regions supplemented by MZ SR, SUKL, and RUVZ.
- e-VUC IdZZ page checked by direct request: `https://www.e-vuc.sk/e-vuc/pre-poskytovatelov-zdravotnej-starostlivosti/identifikator-zdravotnickeho-zariadenia.html?page_id=74559`; it documents IdZZ format, components, immutability, non-reuse, and termination semantics.
- e-VUC published-data page checked by direct request: `https://www.e-vuc.sk/e-vuc/pre-poskytovatelov-zdravotnej-starostlivosti/zoznam-zverejnovanych-udajov.html?page_id=66315`; it confirms public portal content can include doctors, nurses, phone numbers, absences, opening hours, and related operational fields.
- e-VUC AMBULANCIA page checked by direct request: `https://www.e-vuc.sk/e-vuc/pre-poskytovatelov-zdravotnej-starostlivosti/aplikacia-ambulancia.html?page_id=92224`; it describes the authenticated provider application backed by Register zdravotnictva.
- `data.gov.sk` search/API attempts for healthcare-provider terms returned HTML application shell in this environment; no working distribution URL was verified.

| Source | Exact page checked | Date checked | Evidence quote or paraphrase | Result | Confidence | Remaining uncertainty |
| --- | --- | --- | --- | --- | --- | --- |
| Eurostat LAU 2025 correspondence table | `https://ec.europa.eu/eurostat/web/nuts/local-administrative-units` | `2026-05-27` | The project records the Slovak regions as verified offline against the LAU 2025 workbook; Eurostat legal notice URL is tracked separately. | Regions source is identified and official; redistribution conditions still need exact retained wording. | medium | Exact workbook notice and attribution requirements should be kept on file. |
| PortalVS classifier 10 (Okres) | `https://ciselniky.portalvs.sk/api/rest/json/10` | `2026-07-20` | Local REST export contains Slovak and non-Slovak rows; checked-in districts are filtered to 79 Slovak districts. | Source is identified; licence and redistribution remain pending/restrictive. | low | Need written confirmation for caching, transformation, redistribution, commercial use, and attribution. |
| PortalVS classifier 9 (Obce) | `https://ciselniky.portalvs.sk/api/rest/json/9` | `2026-09-07` | Local REST export was filtered to 2,927 current Slovak municipality rows; `districtCode` is derived from `code_su`. | Source is identified; licence and redistribution remain pending/restrictive. | low | Need written confirmation for caching, transformation, redistribution, commercial use, excluded rows, and attribution. |
| PortalVS classifier 42 (PSČ obcí SR a ČR) | `https://ciselniky.portalvs.sk/classifier/show/42/` | `2026-09-07` | Current runtime dataset contains 1,420 PSC keys and 3,101 source match records; coverage is partial and geography links are locally backfilled. | Source is identified; redistribution is treated as restricted until clarified. | low | Need written confirmation for postal-code classifier redistribution and whether partial transformed snapshots are allowed. |
| NBS bank-code directory | `https://nbs.sk/en/payments/general-information/directories-and-registers/directory-identification-codes-domestic-payment-system-in-sr/` | `2026-09-12` | Directory version 225, effective from `2026-05-18`, was used to import 30 domestic Slovak payment-system code rows; foreign/non-SK BIC rows were excluded. | Source is official and identified; licence and redistribution remain pending. | medium | Need exact terms URL, attribution wording, local caching permission, modification/normalization permission, and commercial-use status. |
| NBS holidays page and Act 241/1993 | `https://www.nbs.sk/en/about-the-bank/holidays-in-slovakia/` | `2026-05-25` | Existing registry notes an NBS disclaimer allowing reuse with attribution and no modification, but exact retained quote is not yet stored in this repo. | Treat as medium confidence until exact disclaimer text and applicability to curated JSON are retained. | medium | Need exact quote, terms URL, and confirmation that curated JSON redistribution is permitted. |
| Verified public organizational contact pages | Multiple official organization pages | `2026-06-03` | Current company lookup is a small legal-entity seed dataset; personal/stakeholder fields are intentionally excluded. | Seed source pages are individually checked, but broader RPO reuse is not approved. | low | Need RPO/ŠÚ SR clarification for bulk reuse, local caching, public redistribution, commercial users, and privacy restrictions. |
| RPO API documentation | `https://susrrpo.docs.apiary.io/`; `https://api.statistics.sk/rpo/v1/` identified as production base; Slovensko.Digital docs reviewed as non-official mirror documentation | `2026-09-18` | Apiary/OpenAPI-derived documentation identifies the production REST base and `Creative Commons Attribution 4.0 (CC BY 4.0)`. Slovensko.Digital docs describe local-storage batch exports, daily updates, and privacy-sensitive fields, but this is not retained as official production acquisition approval. | Useful for research and importer readiness. Not sufficient to replace the seed-backed production dataset. | medium | Need exact official portal licence/operator evidence, verified supported bulk/local snapshot acquisition, rate limits, source provenance, and redistribution terms before production import. |
| Telecom regulator phone-area workbook | `https://www.teleoff.gov.sk/urad/odbory-oddelenia/odbor-regulacie-elektronickych-komunikacii/cislovanie/1.html`; file `https://www.teleoff.gov.sk/files/urad/odbory-oddelenia/odbor-regulacie-elektronickych-komunikacii/cislovanie/30.xls` | `2026-09-15` | Page link text identifies `Zoznam obcí SR zaradených do jednotlivých primárnych oblastí` and describes the Excel file as data for further recipient processing. Workbook columns are `Číselný kód obce`, `Názov obce`, `Názov okresu`, `Názov kraja`, `NDC`, and `PO`. | Source page and file are identified and retained locally; licence and redistribution remain pending. | medium | Need reuse terms, attribution terms, visible update date retention, and confirmation that local transformed JSON redistribution is allowed. |
| Legacy vehicle registration district abbreviations | `https://static.slov-lex.sk/static/SK/ZZ/2009/9/20191201.html` | `2026-09-15` | Slov-Lex static text for `9/2009 Z. z. Vyhláška Ministerstva vnútra Slovenskej republiky, ktorou sa vykonáva zákon o cestnej premávke...`; § 36 ods. 2 states `Pre potreby evidenčného čísla sa označenie okresov ustanovuje takto:` followed by abbreviation-to-district rows such as `BA, BD, BE, BI, BL, BT` for `Bratislava`. | Official legal text source identified; transformed dataset is historical/reference only. Licence and redistribution remain pending. | medium | Need exact Slov-Lex reuse terms, attribution wording, transformation/redistribution permission, and confirmation of current legal cutover wording. |
| MŠVVaM school facility aggregate counts | `https://www.minedu.sk/dataset-register-skol-a-skolskych-zariadeni/`; CSV `https://data.slovensko.sk/download?id=2ca3a9f8-819a-4ea1-8315-769c4fcc57da` | `2026-09-15` | Page identifies `Register škôl a školských zariadení`; description says data comes from RIS, is valid to `15.9.2025`, update periodicity is `polročne`, licence is `Creative Commons BY`, format is `CSV`, contact is `opendata@minedu.sk`, and source headers are aggregate fields including `Druh školy skrátený`, `NUTS3`, `LAU1`, and `Počet organizačných zložiek`. | Source is official and licence is listed as Creative Commons BY. CSV contains aggregate rows only, so `/v1/schools/{code}` was intentionally not implemented. | medium | Need exact CC BY licence version and attribution wording; monitor future semiannual refreshes. |

## Evidence Rules

- Prefer exact quoted source terms and archived local notes over assumptions.
- If evidence is paraphrased, keep the confidence level below high.
- Do not treat public availability as permission to redistribute.
- Do not treat official-source status as official endorsement.
