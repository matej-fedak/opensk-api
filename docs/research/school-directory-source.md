# Institution-Level School Directory Source Research

Date checked: 2026-10-07

## Acquisition decision

Acquisition decision: RESEARCH_AND_TOOLING_ONLY

Research-paper Phase 3 schools status: blocked for production import

## Phase 3 mapping

This milestone targets the research-paper Phase 3 `schools` item. It does not change the existing aggregate school endpoints:

- `GET /v1/school-facility-counts`
- `GET /v1/school-facility-counts/stats`

The existing MŠVVaM open-data CSV remains aggregate-only and must not be reinterpreted as institution-level school records.

## Official Source Candidates

- MŠVVaM open-data CSV: `https://www.minedu.sk/dataset-register-skol-a-skolskych-zariadeni/`
- MŠVVaM register page with category PDFs: `https://www.minedu.sk/register-skol-a-skolskych-zariadeni-slovenskej-republiky/`
- RIS / CRINFO public portal: `https://crinfo.iedu.sk/RISPortal/`, including `/register/` and `/catalogue/`
- CVTI current registers page: `https://www.cvtisr.sk/cvti-sr-vedecka-kniznica/informacie-o-skolstve/registre/aktualne-registre.html?page_id=9331`
- CVTI school/facility XLS lists: `https://www.cvtisr.sk/cvti-sr-vedecka-kniznica/informacie-o-skolstve/registre/zoznamy-skol-a-skolskych-zariadeni.html?page_id=9332`
- National open-data catalogue search attempts through `data.gov.sk` / `data.slovensko.sk`

## Findings

The confirmed MŠVVaM open-data CSV is authoritative and lists Creative Commons BY, format CSV, contact `opendata@minedu.sk`, periodicity `polročne`, and data validity `15.9.2025`. It contains aggregate RIS rows only, with fields such as school kind/type, NUTS3, LAU1, founder categories, and `Počet organizačných zložiek`. It has no institution-level school code, name, address, municipality, or school status fields. It is suitable only for `schoolFacilityCounts`.

The MŠVVaM register page is official and links category PDFs hosted by CVTI, including secondary schools, kindergartens, primary schools, primary art/language schools, special schools, school clubs, other schools/facilities, church schools/facilities, and private schools/facilities. Representative PDF URLs were reachable with HTTP 200, for example `stat_ms.pdf`, `stat_zs.pdf`, `siet_ss.pdf`, and `stat_cvc.pdf`. These are not approved as a production acquisition source because PDF extraction would be brittle and no open redistribution/licence terms were verified on the register page.

The RIS / CRINFO public portal exposes a public `Registre regionálneho školstva` screen and a `Stiahnuť CSV` link pattern in the rendered HTML, plus an `Aktuálne prehľady vybraných údajov` screen showing fields such as EDUID, type, name, address, region, district, pupil counts, employee counts, batch status, and RFO matching counts. This confirms that institution-level data exists in RIS. Production import is still not approved because the list content is JS-loaded, no stable documented bulk API/export contract was found, the public catalogue page includes privacy-sensitive counts/status fields outside OpenSK scope, and reuse/redistribution terms were not verified for this export surface.

The CVTI `Aktuálne registre` page says register contents can be opened in Excel. The CVTI `Zoznamy škôl a školských zariadení` page exposes direct XLS links for categories such as `ms_z.xls`, `zs_z.xls`, `GYM_Z.XLS`, and `cvc_z.xls`. The page says the lists contain school/facility address, contact data mail and phone, and total pupil/client/accommodation counts, while current contact data is not provided based on a MŠVVaM instruction. It also says only schools/facilities submitting statistical reports are listed. Representative XLS HEAD checks returned HTTP 200 and Excel content types. These files are machine-readable enough for research, but production import is blocked because no explicit open licence/reuse grant was verified, coverage is statistical-reporting scope rather than clearly the full legal register, and the page describes fields that require privacy minimization.

`data.gov.sk` / `data.slovensko.sk` search attempts in this environment returned the JavaScript application shell rather than verified CKAN/action JSON distributions. No separate institution-level open-data distribution was confirmed.

The CVTI `Školy-obce` site provides interactive/filterable municipal school statistics for kindergartens and primary schools, but it is municipal/statistical reporting content, not a verified national institution directory source for OpenSK production import.

## Identifier Decision

EDUID appears on RIS public pages and is likely the current school/facility identifier candidate. Historical mentions of `KODSKO` were not verified as the current public, unique, stable, and persistent identifier for all target records. Production import remains blocked until the stable identifier is explicitly verified from an approved source with field definitions.

## Privacy Decision

Future school or education-institution production scope must be institution reference data only. Recursively exclude personal/contact/operational fields including `director`, `deputyDirector`, `principal`, `personName`, `firstName`, `lastName`, `personalEmail`, `personalPhone`, `directPhone`, `responsiblePerson`, `staff`, `employee`, birth data, personal identifiers, pupil/person-level data, RFO matching counts, batch status, raw error-file links, and individual contact fields.

Preferred future fields remain official code or EDUID, institutional name, school type/kind, institutional address, municipality, founder category, legal form, teaching language, and establishment/termination or operating status, but only after source rights and field semantics are verified.

## Endpoint Decision

No production endpoint is added in 0.20.0.

Do not add `/v1/schools`, `/v1/education-institutions`, `data/schools.json`, or institution-level import tooling until all production gates pass. Keep `schoolFacilityCounts` separate because it is aggregate data.

## Remaining Blockers

- Verify explicit licence/reuse terms for CVTI XLS lists or RIS CSV exports, including caching, transformation, redistribution, attribution, and downstream commercial use.
- Verify a documented anonymous reproducible bulk/API/export workflow that is not frontend scraping and does not depend on private undocumented endpoints.
- Verify stable identifier semantics, preferably EDUID or a documented current equivalent, including uniqueness and persistence.
- Verify national/scope coverage, especially whether XLS statistical-reporting lists exclude schools/facilities that do not submit a specific statistical report.
- Define a privacy-safe field subset that excludes contacts, staff/person fields, pupil/person-level data, RFO matching counts, and operational batch/error fields.
- Verify refresh cadence and source freshness for any candidate source.
- Confirm whether the endpoint should be `/v1/schools` or `/v1/education-institutions` based on final source scope.
