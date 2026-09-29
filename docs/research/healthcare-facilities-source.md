# Healthcare Facilities / Provider Source Research

Date checked: 2026-09-29

## Acquisition decision

Acquisition decision: RESEARCH_AND_TOOLING_ONLY

Research-paper Phase 3 healthcare-facilities status: blocked

## Phase 3 mapping

This milestone targets the research-paper Phase 3 `medical facilities` item. It does not add another domain.

## Official source candidates

- Primary official register: Narodny register poskytovatelov zdravotnej starostlivosti (NR PZS)
- Operator: Narodne centrum zdravotnickych informacii (NCZI)
- NCZI NR PZS page: https://www.nczisk.sk/Registre/Narodne-administrativne-registre/Narodny-register-poskytovatelov-zdravotnej-starostlivosti/Pages/default.aspx
- e-VUC portal: https://www.e-vuc.sk/
- e-VUC IdZZ page: https://www.e-vuc.sk/e-vuc/pre-poskytovatelov-zdravotnej-starostlivosti/identifikator-zdravotnickeho-zariadenia.html?page_id=74559
- National catalogue: https://data.gov.sk/

## NCZI NR PZS findings

The NCZI page confirms NR PZS as a national administrative register of healthcare providers and part of the data foundation of the National Health Information System.

The page describes NR PZS functions as registration, information, integration, statistical support, eHealth support, and source data for the National Health Portal. It lists provider categories including ambulatory providers, inpatient providers, pharmacy-care providers, dental technicians, opticians, independent-practice licence holders, spa facilities, mobile sampling points, and others.

The page identifies upstream data sources such as permit registers maintained by permitting authorities, the UDZS provider register, RPO, population/person registers, organization registers, the trade register, the commercial register, nonprofit registers, and selected health-insurance-contract data.

No public anonymous record-level NR PZS download, API, SOAP service, WSDL, CSV, XML, JSON, XLS/XLSX export, or downloadable archive suitable for OpenSK production import was verified from the NR PZS page.

## NCZI aggregate statistics findings

NCZI publishes structured statistical outputs under `Siet poskytovatelov zdravotnej starostlivosti`. Current pages include XLSX and ODS downloads such as:

- `Prehlad siete zdravotnej starostlivosti - druhy zdravotnickych zariadeni za rok 2024`
- `Prehlad siete zdravotnej starostlivosti - druhy a odborne zameranie utvarov v zdravotnickych zariadeniach za rok 2024`

Those datasets are aggregate statistical tables at Slovak Republic and regional level. They are derived from NR PZS and annual statistical reports, but they are not a facility directory and do not provide institution-level facility records with IdZZ, provider IČO, operating address, status, or municipality links. Aggregate statistical outputs are therefore not approved as the production source for `/v1/healthcare-facilities`.

## e-VUC / Register zdravotnictva findings

The e-VUC portal exposes public healthcare directory pages across all eight self-governing regions. The portal describes its healthcare content as information produced by self-governing regions and supplemented by MZ SR, SUKL, and RUVZ data. It presents itself as a guaranteed source for this public-facing portal content.

The portal lists ambulances, pharmacies, pharmacy emergency services, ambulatory emergency services, health districts, institutional healthcare facilities, home nursing agencies, mobile sampling points, hospitals, and related patient-facing content.

The e-VUC provider section states that self-governing regions use the `Register zdravotnictva` system by CRYSTAL CONSULTING, s.r.o., with the AMBULANCIA application for provider data maintenance and electronic communication with regional authorities. Access to AMBULANCIA requires provider login credentials.

No documented public export, API, JSON feed, XML feed, SOAP service, integration interface, downloadable archive, or open-data distribution was verified for production acquisition. Public HTML directory pages alone are not approved because scraping or reverse-engineering undocumented frontend behavior is outside the source gate.

## IdZZ verification

e-VUC documents `Identifikator zdravotnickeho zariadenia` (IdZZ) as a stable healthcare-facility identifier that accompanies a facility through its whole life and after the permit to operate terminates. It uniquely identifies the facility across public-administration information systems.

The documented format is:

```text
AA-12345678-A0001
```

Components:

- two-character issuing-authority code, such as `61` for Bratislavsky samospravny kraj or `68` for Kosicky samospravny kraj
- eight-digit provider IČO, left-padded with zeros if needed
- five-character alphanumeric sequence with one alphabetic character followed by four digits, assigned within the provider IČO
- hyphens between components

IdZZ is documented as immutable and unique. Reuse of an already assigned IdZZ for another facility is not permitted. Deletion of an already assigned IdZZ and facility record is not possible. Termination of a permit terminates the facility and IdZZ validity, and restoring a terminated IdZZ is not possible.

IdZZ is suitable as the canonical OpenSK facility ID if an approved source exposes it. OpenSK should not invent a replacement ID while IdZZ exists and is available from the selected source.

## KPZS findings

e-VUC separately documents `Kod poskytovatela zdravotnej starostlivosti` (KPZS). KPZS is issued by UDZS after a valid permit and can exist multiple times for one facility, while every healthcare facility has exactly one IdZZ. KPZS encodes professional focus and activity type and is mainly used for communication with health insurers and eHealth. KPZS is not preferred as the primary OpenSK facility identifier.

## data.gov.sk findings

Search attempts for `zdravotnicke zariadenia`, `poskytovatelia zdravotnej starostlivosti`, `register poskytovatelov`, `NR PZS`, `ambulancie`, `nemocnice`, `zdravotnictvo`, `NCZI`, and `e-VUC` through the available `data.gov.sk` API paths returned the JavaScript application shell as HTML, not usable catalogue JSON.

No working data.gov.sk healthcare-provider distribution URL was verified in this environment. No production acquisition was approved from catalogue metadata alone.

## Licence and reuse

No production-compatible licence or reuse grant was verified for a local OpenSK healthcare-facilities snapshot.

Public portal visibility, aggregate statistical downloads, registry-information pages, or authenticated provider applications are not treated as permission to cache, transform, redistribute, or permit commercial downstream use of institution-level facility records.

## Privacy decision

Healthcare-provider sources can mix institutional data with personal data, including doctors, nurses, individual practitioner names, personal contact details, representatives, statutory bodies, and personal addresses for natural-person providers.

OpenSK's future default scope should be facility/institution reference data only:

- IdZZ
- provider IČO
- institutional provider name when safe
- facility name and type
- specialty or professional focus
- operating status
- institutional operating address
- municipality, district, and region links

Excluded by default:

- doctor names
- nurse names
- individual practitioner names where they identify a natural person
- personal phone or email
- statutory representatives
- responsible persons
- birth or personal identifiers
- private/residential addresses
- appointment slots, vacations, absences, opening-hours changes, performance/pricing files, and patient-facing operational notices

e-VUC explicitly documents that its public portal publishes doctors, nurses, phone numbers, absences, opening hours, facility information, and similar operational fields. Any future import from e-VUC or a derived source must have deterministic field-level privacy filtering and must not rely on company-name suffix heuristics to classify natural persons.

## National coverage

NCZI NR PZS is national in scope as the official administrative register, but no public production acquisition route was verified.

e-VUC presents all eight self-governing regions and public healthcare directory categories, but no approved machine-readable export was verified. Therefore national coverage cannot be claimed for an OpenSK production dataset.

## Candidate future data model

Only if a production source is approved, a minimal candidate record is:

```json
{
  "id": "61-12345678-A0001",
  "providerIco": "12345678",
  "providerName": "Example Health s.r.o.",
  "name": "Ambulancia vseobecneho lekarstva",
  "facilityType": "ambulancia",
  "specialties": ["Vseobecne lekarstvo"],
  "status": "active",
  "address": {
    "street": "Hlavna 1",
    "postalCode": "81101",
    "municipality": "Bratislava"
  },
  "municipalityCode": null,
  "districtCode": null,
  "regionCode": null,
  "validFrom": null,
  "validTo": null
}
```

Use only fields reliably available from the approved source. Do not invent missing values. Facility operating location is more important than provider registered-office location.

## Endpoint decision

No public endpoint is added in 0.18.0.

If all gates pass in a future milestone, the preferred route surface is:

- `GET /v1/healthcare-facilities`
- `GET /v1/healthcare-facilities/{id}`
- `GET /v1/healthcare-facilities/search?q=...`

Potential list filters should stay narrow: `municipalityCode`, `districtCode`, `regionCode`, `facilityType`, `specialty`, `status`, `limit`, and `offset`.

## Final blocker

Find a documented official NCZI or e-VUC machine-readable export, official data.gov.sk distribution, or another clearly authorized source with record-level facility data, IdZZ, national or explicitly scoped coverage, clear reuse rights, reproducible non-scraping refresh, and deterministic privacy filtering before adding importer, dataset, service, or endpoint code.
