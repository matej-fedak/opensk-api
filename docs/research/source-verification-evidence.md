# Source Verification Evidence

This log records evidence checked for source and licence decisions. It is intentionally conservative and does not create legal certainty by itself.

## 2026-10-30 ŠÚ SR elections reply — REPLY_RECEIVED_RESOLVED

- Logged 2026-10-31. The maintainer supplied the institutional answers and
  confirmed **2026-10-30** as the received date. Mailbox metadata/verbatim
  correspondence was not independently inspected; no personal signatures,
  phone numbers or email headers are published. Summary:
  `elections-reuse-clarification.md`.
- **CC_BY_4_0_VERIFIED_BY_PUBLISHER_REPLY** for the election-result CSV/ODS/XLSX
  tables on volby.statistics.sk: local storage, CSV/XLSX → JSON, normalization,
  derived snapshots, public open-source API redistribution and commercial
  downstream reuse permitted. Retain publisher/source/licence links, disclose
  changes and actual acquisition date, and do not imply endorsement.
  **OpenSK nie je oficiálnou službou Štatistického úradu SR.** MIT covers code,
  not ŠÚ SR data.
- **MANUAL_OFFICIAL_DOWNLOAD_ONLY**: robots/crawlers/similar automated downloads
  remain prohibited; use the official Údaje na stiahnutie files manually,
  then process offline. No automated recheck/download is authorized here.
- **MANUAL_SOURCE_FILES_REQUIRED** at this checkpoint: no five-file manual
  production acquisition, timestamp, manifest, snapshot or results endpoint is
  claimed. Earlier research acquisition is not relabelled as manual production.
- PortalVS/telecom remain **FOLLOW_UP_SENT_AWAITING_REPLY** after manual
  follow-ups 2026-10-28. Historical entries below retain their as-of conclusions.

## 2026-10-14 NBS Bank Reply — REPLY_RECEIVED_RESOLVED

Historical PR #33 scope below. **0.23.8 now serves v226 / effective 2026-10-08**,
downloaded 2026-10-15T16:23:00Z, 1,953 original bytes, SHA-256
`b82cd0c34d89ff1a68d710fedd3e8f509065a53ae605282ad4fc29234b74fc64`.
The current page/version, exact CSV URL, CP1250 headings, all 30 domestic rows,
HTML Akt. úč. distinction and three changed codes were reconciled; bank/IBAN
normal metadata now exposes direct attribution/provenance. No new permission
inferred. Full acquisition/diff: `nbs-bank-reuse-clarification.md#0238-production-refresh`.

- The maintainer received an institutional reply from NBS, odbor komunikácie značky NBS a inštitucionálnych vzťahov, on **2026-10-14**, following manual dispatch on **2026-10-11**. This is authoritative reply evidence supplied by the maintainer, not inferred permission. The repository retains its substantive clarification, not original mail headers or a purported verbatim email.
- **NBS Terms of Use + direct clarification** (`https://nbs.sk/disclaimer-sk/`): local storage, value-preserving format/field-name conversion, public API redistribution and commercial downstream use are permitted with attribution; JSON is not the original NBS file. OpenSK-derived fields must be separated/labelled. MIT applies to code, not NBS data. NBS does not guarantee completeness/content integrity or accept associated damages liability; commercial users should verify correctness. Logos/flag/symbols need separate approval and are unused.
- Snapshot remains **v225 effective 2026-05-18**, unchanged bank responses and `BANKS_LAST_UPDATED`; **v226 effective 2026-10-08** was current at reply time, not imported in PR #33. Future refresh retains actual download date alongside version/effective date. No v225 download date is invented.
- `activePartyMarker` is OpenSK categorical normalization of **Payment system SIPS**, and `activeParty` is its derived boolean; neither reads **Akt. úč.**. Code-path mapping, source-byte limitations, all permissions and NBS's recommended (not mandatory verbatim) attribution are retained in `docs/research/nbs-bank-reuse-clarification.md`.
- Only NBS banks resolve. PortalVS, telecom and ŠÚ SR elections remain `SENT_AWAITING_REPLY`; holidays interpretation remains separate. No email sent by the agent.

## 2026-10-15 ITMS21+ production recheck (0.23.7)

- Project endpoint remains official/anonymous JSON; complete bounded list acquisition: 4,574 source rows, 19 pages, 2026-10-15T11:37:24Z–11:42:27Z. Exact per-page URLs/times/bytes/hashes and canonical digest retained in `eu-funds-acquisition-manifest.json`; no raw personal payloads committed. First-page boundary unchanged, all IDs/codes unique, totals/ranges consistent; no transactional upstream snapshot guarantee.
- Project-specific catalogue publisher MIRRI `legal-subject/50349287`, distribution `/public/v1/projekt` and attached terms node remain unchanged. SPARQL recheck of all terms triples retains `authorsWorkType`, `originalDatabaseType`, `databaseProtectedBySpecialRightsType` = `http://publications.europa.eu/resource/authority/licence/CC_BY`; no new restriction on that node. Precise version not separately identified, **not** independently verified CC BY 4.0. Source query/URLs in the historical spike §6; current notices and evidence in `../eu-funds.md`.
- All 46 observed forms reviewed against live 482-entry `/pravnaforma` catalogue: 40 positive code/label approvals, 4 ambiguous, one natural-person and one unspecified category. 4,561 projects included, 13 excluded entirely. Titles/dates/rich personal fields omitted; `contractedTotal` preserves total contracted amount without an unverified currency suffix. Full normalized storage measurements support `JSON_CONTINUE`. Two production routes, 39 GET operations; prior research-only statements below are historical.

## 2026-10-14 ITMS21+ EU Funds (0.23.6)

- Official source: `https://api.itms21.sk/public/v1/`, anonymous project JSON, confirmed through the official portal and integration manual v1.0 (25.6.2025). Measured totals: 4,571 projects, 12,955 subjects, 9,075 ŽoNFP; counts are observed service totals, not an all-spending audit.
- Licence: “Zoznam projektov ITMS21+”, `https://data.gov.sk/set/3dd34ab69156cd6dcdd6454f81727c88`, publisher MIRRI (`legal-subject/50349287`), distribution accessURL exactly `/public/v1/projekt`. Queried firsthand via `https://data.slovensko.sk/api/sparql`; `authorsWorkType`, `originalDatabaseType`, `databaseProtectedBySpecialRightsType` each equal `http://publications.europa.eu/resource/authority/licence/CC_BY`. Precise version URL not stated; personal-data catalogue marker is not trusted as anonymisation proof.
- Verdict `GO_PRODUCTION_NEXT` / `JSON_CONTINUE`, **research-only** registry and preview tooling, no public EU-funds route or production dataset. Positive 28-form legal-entity gate; all natural-person/sole-trader/unspecified/missing/unreviewed beneficiary projects excluded entirely, including codes/IDs/URLs and matching-detail manifests. Counts distinguish captured source rows from included projects; no excluded-row code list is persisted. Suppliers/partners/descriptions/addresses/contacts excluded.
- Exact manual/project-capture hashes, URLs, quotes, licence query, privacy red-team, monetary distinctions, volume estimates and remaining production gates: `docs/research/eu-funds-itms21-spike.md`. Raw artifacts stay outside Git. No correspondence sent and no PortalVS/elections compliance change.

## 2026-10-11 ECB Euro Reference Rates (0.23.3 SPIKE)

- Verdict: **CLEAR** — ECB "Disclaimer & copyright" retains explicit free-use permission ("users of this website may make free use of the information obtained directly from it") subject to accurate reproduction, ECB attribution, explicit statement of modifications, and no framing; "for information purposes only / transaction use strongly discouraged" notice retained from the reference-rates page.
- Full retained wording, checked URLs, feed byte/hash evidence and residual questions (sui-generis right, no published rate limits, undocumented revision policy): `docs/research/exchange-rates-source-verification.md` and `docs/research/exchange-rates-data-schema.md`. NBS verified as republication-only (excluded as canonical). Synthesis/decision: `docs/research/exchange-rates-spike.md`. Raw downloads stay in the temp dir; no raw upstream file is committed. No ECB outreach is required; an optional sui-generis draft remains `READY_FOR_USER_TO_SEND`, unsent.

## 2026-10-11 PortalVS Legacy/Successor Resilience (0.23.3)

- Both systems live-verified; the legacy end-of-support banner (2026-10-31) is unchanged; dated transition manifests + SHA-256 snapshots for legacy classifiers 9/10/42 and successor `slovenske-obce`/`slovenske-okresy`/`psc-sk` are retained in the maintainer's temp dir only (not committed; rights pending). Verdict `SUCCESSOR_COMPATIBLE_WITH_TRANSFORM_CHANGES`; evidence and per-dataset analysis: `docs/research/portalvs-source-resilience.md`. No licence conclusion drawn.

## 2026-10-11 Outreach Dispatch Record (updated by NBS reply 2026-10-14)

- The human maintainer states that four clarification packages in `docs/research/source-licence-outreach.md` were sent manually on **2026-10-11**: §1 PortalVS classifiers 9/10/42 (To `helpdesk@portalvs.sk`, CC `portalvs@portalvs.sk`), §2 NBS bank-code directory (To `info@nbs.sk`), §4 telecom-regulator phone-area workbook (To `marian.jurkovic@teleoff.gov.sk`, CC `legal@teleoff.gov.sk`), §7 ŠÚ SR NRSR2023 elections (To `info@statistics.sk`, CC `volby@statistics.sk`).
- Current states: NBS banks **`REPLY_RECEIVED_RESOLVED`** (2026-10-14); PortalVS, telecom and ŠÚ SR elections **`SENT_AWAITING_REPLY`**. Silence is not approval for those three. No Message-ID, delivery receipt, exact sent/received body or mailbox headers are independently archived here; substantive NBS evidence is recorded above, original correspondence retained privately.

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

## 2026-10-07 Institution-Level School Directory

- MŠVVaM aggregate open-data page checked by direct request: `https://www.minedu.sk/dataset-register-skol-a-skolskych-zariadeni/`. It lists RIS origin, validity `15.9.2025`, periodicity `polročne`, licence `Creative Commons BY`, format `CSV`, contact `opendata@minedu.sk`, and download URL `https://data.slovensko.sk/download?id=2ca3a9f8-819a-4ea1-8315-769c4fcc57da`; source remains aggregate-only.
- MŠVVaM institution register page checked by direct request: `https://www.minedu.sk/register-skol-a-skolskych-zariadeni-slovenskej-republiky/`. It exposes category PDF links hosted under CVTI, including `stat_ms.pdf`, `stat_zs.pdf`, `siet_ss.pdf`, and `stat_cvc.pdf`; no open licence/reuse terms were verified for PDF extraction.
- Representative PDF HEAD checks returned HTTP 200 and `application/pdf` for kindergarten, primary-school, secondary-school, and other-school/facility PDFs.
- RIS portal checked by direct request: `https://crinfo.iedu.sk/RISPortal/register/` and `https://crinfo.iedu.sk/RISPortal/catalogue/`. The register page HTML contains `register/ExportCSV?id={{item.poradie}}`, and the catalogue page exposes EDUID, institution name, address, pupil/employee counts, RFO matching counts, batch status, and error-file columns. No documented stable public bulk/API contract or reuse terms were verified.
- CVTI current-register page checked by direct request: `https://www.cvtisr.sk/cvti-sr-vedecka-kniznica/informacie-o-skolstve/registre/aktualne-registre.html?page_id=9331`. It says register contents can be opened in Excel and links to RIS.
- CVTI XLS list page checked by direct request: `https://www.cvtisr.sk/cvti-sr-vedecka-kniznica/informacie-o-skolstve/registre/zoznamy-skol-a-skolskych-zariadeni.html?page_id=9332`. It exposes direct XLS category files, says lists contain address, contact data mail and phone while current contact data is not provided based on MŠVVaM instruction, total pupil/client/accommodation counts, and only schools/facilities submitting statistical reports.
- Representative XLS HEAD checks returned HTTP 200 and `application/vnd.ms-excel` for `ms_z.xls`, `zs_z.xls`, `GYM_Z.XLS`, and `cvc_z.xls`; no explicit open licence/reuse terms were verified.
- `data.gov.sk` / `data.slovensko.sk` search attempts for school-register terms returned JavaScript application shells in this environment; no separate institution-level machine-readable distribution was verified.
- Production decision: `RESEARCH_AND_TOOLING_ONLY`; no `/v1/schools`, `/v1/education-institutions`, `data/schools.json`, or importer is added.

## 2026-10-07 Slovak Court Decisions

- Ministry open-data page checked by direct request: `https://www.justice.gov.sk/sluzby/registre/otvorene-data/`. It says data is available through OpenAPI/Swagger UI and links `https://obcan.justice.sk/pilot/api/ress-isu-service/swagger-ui/index.html`; extended data or external-system integration requests should contact `servicedesk.mssr@justice.sk`.
- Swagger initializer checked by direct request: `https://obcan.justice.sk/pilot/api/ress-isu-service/swagger-ui/swagger-initializer.js`. It points to `https://obcan.justice.sk/pilot/api/ress-isu-service/v3/api-docs/swagger-config`.
- Swagger config checked by direct request: `https://obcan.justice.sk/pilot/api/ress-isu-service/v3/api-docs/swagger-config`. It points to `https://obcan.justice.sk/pilot/api/ress-isu-service/v3/api-docs`.
- OpenAPI spec checked by direct request: `https://obcan.justice.sk/pilot/api/ress-isu-service/v3/api-docs`. It documents anonymous-looking decision endpoints `GET /v1/rozhodnutie`, `GET /v1/rozhodnutie/{id}`, and `GET /v1/rozhodnutie/autocomplete`, with ECLI, case number, court, judge, legal-area, decision-form, decision-date, sorting, facet, and pagination parameters/fields.
- Ministry public decisions page checked by direct request: `https://www.justice.gov.sk/sudy-a-rozhodnutia/sudy/rozhodnutia`; the page shell is official, but no separate redistribution licence was verified from the checked content.
- Constitutional Court guidance checked by direct request: `https://www.ustavnysud.sk/ako-hladat`. It documents public decision search by text, case number, ECLI, dates, proceeding type, legal provisions, collection number, and subject keywords; no documented anonymous API/bulk export was verified.
- `data.gov.sk` API/search attempts returned only the JavaScript application shell in this environment; no verified court-decision catalogue distribution or terms were retained.
- Privacy risk is high because the inspected API schemas expose or reference judge/person names, participants, addresses/contact fields, snippets/highlights, and document/text fields.
- Production decision: `RESEARCH_AND_TOOLING_ONLY`; text decision: `NO_PRODUCTION_DATA`; no `/v1/court-decisions`, `data/court_decisions.json`, fetcher, importer, or full-text storage is added.

| Source | Exact page checked | Date checked | Evidence quote or paraphrase | Result | Confidence | Remaining uncertainty |
| --- | --- | --- | --- | --- | --- | --- |
| Eurostat LAU 2025 correspondence table | `https://ec.europa.eu/eurostat/web/nuts/local-administrative-units` | `2026-05-27` | The project records the Slovak regions as verified offline against the LAU 2025 workbook; Eurostat legal notice URL is tracked separately. | Regions source is identified and official; redistribution conditions still need exact retained wording. | medium | Exact workbook notice and attribution requirements should be kept on file. |
| PortalVS classifier 10 (Okres) | `https://ciselniky.portalvs.sk/api/rest/json/10` | `2026-07-20` | Local REST export contains Slovak and non-Slovak rows; checked-in districts are filtered to 79 Slovak districts. | Source is identified; licence and redistribution remain pending/restrictive. | low | Need written confirmation for caching, transformation, redistribution, commercial use, and attribution. |
| PortalVS classifier 9 (Obce) | `https://ciselniky.portalvs.sk/api/rest/json/9` | `2026-09-07` | Local REST export was filtered to 2,927 current Slovak municipality rows; `districtCode` is derived from `code_su`. | Source is identified; licence and redistribution remain pending/restrictive. | low | Need written confirmation for caching, transformation, redistribution, commercial use, excluded rows, and attribution. |
| PortalVS classifier 42 (PSČ obcí SR a ČR) | `https://ciselniky.portalvs.sk/classifier/show/42/` | `2026-09-07` | Current runtime dataset contains 1,420 PSC keys and 3,101 source match records; coverage is partial and geography links are locally backfilled. | Source is identified; redistribution is treated as restricted until clarified. | low | Need written confirmation for postal-code classifier redistribution and whether partial transformed snapshots are allowed. |
| NBS bank-code directory | `https://nbs.sk/platby/vseobecne-informacie/ciselniky-a-registre/prevodnik-sk/` | `2026-10-15` acquisition | v226 / effective 2026-10-08, downloaded 2026-10-15T16:23:00Z; 30 domestic rows, source bytes/hash retained; full column/row audit. | Verified NBS terms + institutional clarification permit storage, value-preserving conversion, public API and commercial reuse with direct attribution/disclosure. | low | Monitor future versions manually, preserve acquisition provenance and derived-field separation; `nbs-bank-reuse-clarification.md`. |
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

## 2026-10-11 NRSR2023 Elections — 0.23.2 Source/Licence Spike

- Direct official evidence and exact quotes: `docs/research/elections-source-licence.md` (actual local verification clock `2026-10-11T21:31:48+02:00`).
- Official index: `https://volby.statistics.sk/nrsr/nrsr2023/sk/subory_na_stiahnutie.html`; page states `Zdroj: Štatistický úrad SR` and `Dátum a čas zverejnenia výsledkov: 01.10.2023 14:30`.
- Page-driven file index: `https://volby.statistics.sk/nrsr/nrsr2023/json/downloadSK.json`; 33 advertised tables with CSV/ODS/XLSX links. ZIP link: `https://volby.statistics.sk/nrsr/nrsr2023/files/NRSR2023_SK_csv.zip` (advertised 215,5 MB, not downloaded/measured here).
- General official terms: `https://slovak.statistics.sk/wps/portal/ext/aboutus/webpage/terms/` (Slovak language page last update 15.03.2023; exact working language-specific URL retained in the election note). Exact permissions: `šíriť (kopírovať, sprostredkovávať a distribuovať verejnosti);`, `využívať a citovať v iných dielach;`, `využívať komerčne.` Policy names `Creative Commons Attribution License (cc-by) 4.0`, requires ŠÚ SR attribution/no endorsement, and excludes third-party IP.
- Critical exact restriction: `používanie robotov, pavúkov (spiders, crawlers) a ďalších podobných nástrojov na zhromažďovanie a sťahovanie dát, je výslovne zakázané.` No automated-download exception inferred from the file index.
- Contact verified from `https://volby.statistics.sk/nrsr/nrsr2023/sk/kontakty.html`: information service `info@statistics.sk`; content/technical administrator `volby@statistics.sk`.
- Confidence: high for official provenance/index/general-policy wording/contact; medium for general policy coverage of election subdomain; no affirmative automated acquisition approval. Election minutes list a separate commission/MV source and are excluded from this scope.
- Decision: retain `RESEARCH_AND_TOOLING_ONLY` / source/licence verification pending until election-specific coverage and approved acquisition workflow are clarified. Outreach was `READY_FOR_USER_TO_SEND` at spike completion; update 2026-10-11 (0.23.3): the human maintainer states the message was sent manually on 2026-10-11 — `SENT_AWAITING_REPLY`, no reply received, no permission inferred. No raw dataset downloads or production changes by source/licence agent.
- Independent data-track byte/response/header/hash evidence and historical samples: `docs/research/elections-data-schema.md`. The lead's final offline transformation and rights/privacy/storage synthesis are in `docs/research/elections-spike.md`; raw files remain outside Git, with no new scripted acquisition after the restriction was communicated. Technical success does not supply acquisition or redistribution permission.
