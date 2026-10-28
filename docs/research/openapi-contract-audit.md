# OpenAPI contract audit — 0.23.12

## Before implementation (0.23.11)

Base: `500d41824c211060ad77bc8a11b8a750b1966c50`. Captured before route annotations
or PSC implementation changed, using actual `app.openapi()` and TestClient for every GET.
Reproduce capture: `python scripts/audit_openapi_contract.py --output <private-directory>`.
Large raw OpenAPI/runtime bodies are private evidence; compact body digests are committed
in `tests/fixtures/public-contract-baseline.json`. Health clock and root SemVer are normalized
only for comparisons; no other fields or nulls are removed.

**39 GET operations; 9 typed success contracts, 30 generic `dict[str, object]` surfaces.**
The latter all publish `additionalProperties: true`, not a discoverable envelope/data model.
**0 explicit stable operation IDs; 0 response examples; 0 documented application errors.**
All 39 have summaries/descriptions/tags, but descriptions often omit scope and parameters
omit examples, formats, parser defaults and limits. FastAPI advertises its default 422
detail schema on parameterized routes even though the application returns an OpenSK envelope.

Required/nullability issues: generic contracts cannot express required envelope fields,
nullable metadata.lastUpdated (root/errors), nullable PSC geography/codes/validTo, phone
links, company address/date fields or procurement deadlines. Existing source models mark
some nullable fields optional although current responses include them. Bank additive provenance
and historical array/object/page variations must remain. Query strings stay strings where
manual parsing deliberately produces 400; making them validated ints/enums would change behavior.

### Per-operation inventory

All entries below are GET. `G` = generic object/additionalProperties; `$ref` = existing typed
contract. No operation has response examples. 429 applies to every operation except health
when the existing per-process client-IP limiter is enabled. 422 is genuinely used for the
holiday integer path and procurement integer year filters; other listed 400s are manual.

#### GET `/`

- Current ID: `root__get`; tag: `meta`.
- Summary: Project info
- Description: Returns project SemVer, API namespace version, and the documentation URL.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200; actual applicable application statuses: 429.
- Runtime request: `/`; `data` shape: `{name: str, version: str, apiVersion: str, apiNamespace: str, docs_url: str}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - none
- Limitations: Not explicitly discoverable in operation description. Examples: none.

#### GET `/v1/health`

- Current ID: `health_v1_health_get`; tag: `health`.
- Summary: Service health
- Description: Returns a simple health check payload with a UTC timestamp.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200; actual applicable application statuses: none.
- Runtime request: `/v1/health`; `data` shape: `{status: str, timestamp: str}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - none
- Limitations: Not explicitly discoverable in operation description. Examples: none.

#### GET `/v1/banks`

- Current ID: `list_banks_v1_banks_get`; tag: `banks`.
- Summary: List Slovak banks
- Description: Returns the local Národná banka Slovenska converter snapshot, transformed by OpenSK. Metadata carries NBS source/version/effective/download provenance and attribution. NBS Terms of Use apply to data, not MIT. Participation fields are OpenSK-derived from SIPS, not general bank operating status.
- Success: `#/components/schemas/BanksResponse`.
- Documented statuses: 200; actual applicable application statuses: 429.
- Runtime request: `/v1/banks`; `data` shape: `[{code: str, name: str, bic: str, swift: str, alphabeticCode: null, activeParty: bool, activePartyMarker: str, country: str}]`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - none
- Limitations: Some scope wording is present; see exact description above. Examples: none.

#### GET `/v1/banks/{code}`

- Current ID: `get_bank_v1_banks__code__get`; tag: `banks`.
- Summary: Bank lookup by code
- Description: Returns one bank from the local NBS converter snapshot. Additive metadata identifies NBS, source version/effective/download provenance, attribution and OpenSK transformation/derived fields. JSON is not the original NBS file; MIT covers code, not NBS data.
- Success: `#/components/schemas/BankResponse`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 404, 429.
- Runtime request: `/v1/banks/1100`; `data` shape: `{code: str, name: str, bic: str, swift: str, alphabeticCode: null, activeParty: bool, activePartyMarker: str, country: str}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `path code` required=True: `{"type": "string", "title": "Code"}`
- Limitations: Some scope wording is present; see exact description above. Examples: none.

#### GET `/v1/iban/validate/{iban}`

- Current ID: `validate_iban_endpoint_v1_iban_validate__iban__get`; tag: `iban`.
- Summary: Validate IBAN
- Description: OpenSK performs ISO 13616 checksum validation; NBS does not validate the checksum. Slovak bank-code resolution uses the local NBS converter only. Metadata on every validation result declares that resolution dataset's version, effective/download provenance, NBS attribution and OpenSK transformation. NBS Terms of Use govern bank data; MIT covers code.
- Success: `#/components/schemas/IbanValidationResponse`.
- Documented statuses: 200, 422; actual applicable application statuses: 429.
- Runtime request: `/v1/iban/validate/SK3109000000000000000001`; `data` shape: `{inputIban: str, normalizedIban: str, countryCode: str, supportedCountry: bool, checksumValid: bool, bankCode: str, bankName: str, valid: bool}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `path iban` required=True: `{"type": "string", "title": "Iban"}`
- Limitations: Not explicitly discoverable in operation description. Examples: none.

#### GET `/v1/holidays/{year}`

- Current ID: `get_holidays_v1_holidays__year__get`; tag: `holidays`.
- Summary: Holiday calendar by year
- Description: Returns Slovak public holidays for the requested year from the static seed dataset.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200, 422; actual applicable application statuses: 404, 422, 429.
- Runtime request: `/v1/holidays/2026`; `data` shape: `[{date: str, name: str, name_en: str}]`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `path year` required=True: `{"type": "integer", "title": "Year"}`
- Limitations: Some scope wording is present; see exact description above. Examples: none.

#### GET `/v1/psc`

- Current ID: `list_psc_endpoint_v1_psc_get`; tag: `psc`.
- Summary: List PSC records
- Description: Returns the static PSC dataset with pagination and filters.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 429.
- Runtime request: `/v1/psc?psc=01001&limit=1`; `data` shape: `{items: [{psc: str, city: str, deliveryPost: str, municipality: str, municipalityCode: str, district: null, districtCode: str, region: str, regionCode: str, country: str, validFrom: str, validTo: null}], count: int, total: int, limit: int, offset: int}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `query psc` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional PSC filter.", "title": "Psc"}`
  - `query regionCode` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional region code filter.", "title": "Regioncode"}`
  - `query districtCode` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional district code filter.", "title": "Districtcode"}`
  - `query municipalityCode` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional municipality code filter.", "title": "Municipalitycode"}`
  - `query deliveryPost` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional delivery post substring filter.", "title": "Deliverypost"}`
  - `query municipalityName` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional municipality name substring filter.", "title": "Municipalityname"}`
  - `query hasGeography` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional geography presence filter.", "title": "Hasgeography"}`
  - `query limit` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional page size.", "title": "Limit"}`
  - `query offset` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional result offset.", "title": "Offset"}`
- Limitations: Not explicitly discoverable in operation description. Examples: none.

#### GET `/v1/psc/search`

- Current ID: `search_psc_endpoint_v1_psc_search_get`; tag: `psc`.
- Summary: Search PSC records
- Description: Searches the static PSC dataset by query string.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 429.
- Runtime request: `/v1/psc/search?q=01001&limit=1`; `data` shape: `{items: [{psc: str, city: str, deliveryPost: str, municipality: str, municipalityCode: str, district: null, districtCode: str, region: str, regionCode: str, country: str, validFrom: str, validTo: null}], count: int, total: int, limit: int, offset: int}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `query q` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Search query.", "title": "Q"}`
  - `query limit` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional page size.", "title": "Limit"}`
  - `query offset` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional result offset.", "title": "Offset"}`
- Limitations: Not explicitly discoverable in operation description. Examples: none.

#### GET `/v1/psc/stats`

- Current ID: `stats_psc_endpoint_v1_psc_stats_get`; tag: `psc`.
- Summary: PSC dataset stats
- Description: Returns lightweight local statistics for the PSC dataset.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200; actual applicable application statuses: 429.
- Runtime request: `/v1/psc/stats`; `data` shape: `{recordCount: int, uniquePscCount: int, multiMatchPscCount: int, geographyCoverage: {municipalityCode: {count: int, percentage: float}, regionCode: {count: int, percentage: float}, districtCode: {count: int, percentage: float}}, source: {name: str, licenceStatus: str}}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - none
- Limitations: Not explicitly discoverable in operation description. Examples: none.

#### GET `/v1/psc/{psc}`

- Current ID: `get_psc_v1_psc__psc__get`; tag: `psc`.
- Summary: Postal code lookup
- Description: Looks up a Slovak postal code in the expanded static PSC dataset.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 404, 429.
- Runtime request: `/v1/psc/01001`; `data` shape: `{psc: str, city: str, deliveryPost: str, municipality: str, municipalityCode: str, district: null, districtCode: str, region: str, regionCode: str, country: str, validFrom: str, validTo: null, matchCount: int, matches: [{psc: str, city: str, deliveryPost: str, municipality: str, municipalityCode: str, district: null, districtCode: str, region: str, regionCode: str, country: str, validFrom: str, validTo: null, matchCount: int, matches: [{psc: str, city: str, deliveryPost: str, municipality: str, municipalityCode: str, district: null, districtCode: str, region: str, regionCode: str, country: str, validFrom: str, validTo: null}]}]}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `path psc` required=True: `{"type": "string", "title": "Psc"}`
  - `query include` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional response expansion. Supported value: geography.", "title": "Include"}`
- Limitations: Not explicitly discoverable in operation description. Examples: none.

#### GET `/v1/companies/{ico}`

- Current ID: `get_company_v1_companies__ico__get`; tag: `companies`.
- Summary: Company lookup by IČO
- Description: Looks up a company in the local checked-in dataset.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 404, 503, 429.
- Runtime request: `/v1/companies/50158635`; `data` shape: `{ico: str, name: str, legalForm: str, legalStatus: str, sourceRegister: str, address: {street: str, registrationNumber: null, buildingNumber: str, municipality: str, postalCode: str, country: str, municipalityCode: null, regionCode: null, districtCode: null}, establishedOn: null, terminatedOn: null, updatedAt: str, source: {name: str, recordId: str}}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `path ico` required=True: `{"type": "string", "title": "Ico"}`
- Limitations: Not explicitly discoverable in operation description. Examples: none.

#### GET `/v1/ico/{ico}`

- Current ID: `get_company_by_ico_v1_ico__ico__get`; tag: `companies`.
- Summary: Company lookup by IČO alias
- Description: Alias for the local company lookup endpoint.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 404, 503, 429.
- Runtime request: `/v1/ico/50158635`; `data` shape: `{ico: str, name: str, legalForm: str, legalStatus: str, sourceRegister: str, address: {street: str, registrationNumber: null, buildingNumber: str, municipality: str, postalCode: str, country: str, municipalityCode: null, regionCode: null, districtCode: null}, establishedOn: null, terminatedOn: null, updatedAt: str, source: {name: str, recordId: str}}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `path ico` required=True: `{"type": "string", "title": "Ico"}`
- Limitations: Not explicitly discoverable in operation description. Examples: none.

#### GET `/v1/regions`

- Current ID: `list_regions_v1_regions_get`; tag: `regions`.
- Summary: List regions
- Description: Returns the complete static regions dataset.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200; actual applicable application statuses: 429.
- Runtime request: `/v1/regions`; `data` shape: `[{code: str, name: str, nameEn: str, country: str}]`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - none
- Limitations: Not explicitly discoverable in operation description. Examples: none.

#### GET `/v1/regions/{code}`

- Current ID: `get_region_by_code_v1_regions__code__get`; tag: `regions`.
- Summary: Region lookup by code
- Description: Returns one Slovak region from the static geography dataset.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 404, 429.
- Runtime request: `/v1/regions/SK010`; `data` shape: `{code: str, name: str, nameEn: str, country: str}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `path code` required=True: `{"type": "string", "title": "Code"}`
- Limitations: Not explicitly discoverable in operation description. Examples: none.

#### GET `/v1/districts`

- Current ID: `list_districts_endpoint_v1_districts_get`; tag: `districts`.
- Summary: List districts
- Description: Returns the static districts dataset, optionally filtered by region code.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 404, 429.
- Runtime request: `/v1/districts?regionCode=SK010`; `data` shape: `[{code: str, name: str, regionCode: str, country: str}]`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `query regionCode` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional region code filter.", "title": "Regioncode"}`
- Limitations: Not explicitly discoverable in operation description. Examples: none.

#### GET `/v1/districts/{code}`

- Current ID: `get_district_by_code_v1_districts__code__get`; tag: `districts`.
- Summary: District lookup by code
- Description: Returns one Slovak district from the static geography dataset.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 404, 429.
- Runtime request: `/v1/districts/SK0101`; `data` shape: `{code: str, name: str, regionCode: str, country: str}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `path code` required=True: `{"type": "string", "title": "Code"}`
- Limitations: Not explicitly discoverable in operation description. Examples: none.

#### GET `/v1/municipalities`

- Current ID: `list_municipalities_endpoint_v1_municipalities_get`; tag: `municipalities`.
- Summary: List municipalities
- Description: Returns the static municipalities seed dataset, optionally filtered by region or district code.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 404, 429.
- Runtime request: `/v1/municipalities?districtCode=SK0101`; `data` shape: `[{code: str, name: str, regionCode: str, districtCode: str, country: str}]`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `query regionCode` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional region code filter.", "title": "Regioncode"}`
  - `query districtCode` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional district code filter.", "title": "Districtcode"}`
- Limitations: Some scope wording is present; see exact description above. Examples: none.

#### GET `/v1/municipalities/{code}`

- Current ID: `get_municipality_by_code_v1_municipalities__code__get`; tag: `municipalities`.
- Summary: Municipality lookup by code
- Description: Returns one Slovak municipality from the static geography seed dataset.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 404, 429.
- Runtime request: `/v1/municipalities/528595`; `data` shape: `{code: str, name: str, regionCode: str, districtCode: str, country: str}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `path code` required=True: `{"type": "string", "title": "Code"}`
- Limitations: Some scope wording is present; see exact description above. Examples: none.

#### GET `/v1/phone-areas`

- Current ID: `list_phone_areas_endpoint_v1_phone_areas_get`; tag: `phone-areas`.
- Summary: List phone area records
- Description: Returns the static Slovak primary telephone area dataset with pagination and filters.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 429.
- Runtime request: `/v1/phone-areas?limit=1`; `data` shape: `{items: [{code: str, name: str, municipalityCode: str, municipalityName: str, districtCode: str, regionCode: str, country: str}], count: int, total: int, limit: int, offset: int}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `query code` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional phone area code filter.", "title": "Code"}`
  - `query municipalityCode` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional municipality code filter.", "title": "Municipalitycode"}`
  - `query municipalityName` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional municipality name substring filter.", "title": "Municipalityname"}`
  - `query regionCode` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional region code filter.", "title": "Regioncode"}`
  - `query districtCode` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional district code filter.", "title": "Districtcode"}`
  - `query limit` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional page size.", "title": "Limit"}`
  - `query offset` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional result offset.", "title": "Offset"}`
- Limitations: Not explicitly discoverable in operation description. Examples: none.

#### GET `/v1/phone-areas/search`

- Current ID: `search_phone_areas_endpoint_v1_phone_areas_search_get`; tag: `phone-areas`.
- Summary: Search phone area records
- Description: Searches the static Slovak primary telephone area dataset by query string.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 429.
- Runtime request: `/v1/phone-areas/search?q=Bratislava&limit=1`; `data` shape: `{items: [{code: str, name: str, municipalityCode: null, municipalityName: str, districtCode: null, regionCode: null, country: str}], count: int, total: int, limit: int, offset: int}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `query q` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Search query.", "title": "Q"}`
  - `query limit` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional page size.", "title": "Limit"}`
  - `query offset` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional result offset.", "title": "Offset"}`
- Limitations: Not explicitly discoverable in operation description. Examples: none.

#### GET `/v1/phone-areas/{code}`

- Current ID: `get_phone_area_v1_phone_areas__code__get`; tag: `phone-areas`.
- Summary: Phone area lookup by code
- Description: Returns all static phone area records for one Slovak primary telephone area code.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 404, 429.
- Runtime request: `/v1/phone-areas/02`; `data` shape: `{code: str, items: [{code: str, name: str, municipalityCode: str, municipalityName: str, districtCode: str, regionCode: str, country: str}], count: int}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `path code` required=True: `{"type": "string", "title": "Code"}`
- Limitations: Not explicitly discoverable in operation description. Examples: none.

#### GET `/v1/vehicle-registration-codes`

- Current ID: `list_vehicle_registration_codes_endpoint_v1_vehicle_registration_codes_get`; tag: `vehicle-registration-codes`.
- Summary: List legacy vehicle registration district codes
- Description: Returns static historical Slovak vehicle registration district abbreviations. This does not decode full plates and is not reliable for current plate lookup.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 429.
- Runtime request: `/v1/vehicle-registration-codes?limit=1`; `data` shape: `{items: [{code: str, districtName: str, districtCode: null, regionCode: str, validFrom: null, validTo: str, status: str, notes: str}], count: int, total: int, limit: int, offset: int}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `query code` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional two-letter legacy district abbreviation filter.", "title": "Code"}`
  - `query districtName` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional district name substring filter.", "title": "Districtname"}`
  - `query regionCode` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional region code filter.", "title": "Regioncode"}`
  - `query districtCode` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional district code filter.", "title": "Districtcode"}`
  - `query limit` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional page size.", "title": "Limit"}`
  - `query offset` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional result offset.", "title": "Offset"}`
- Limitations: Some scope wording is present; see exact description above. Examples: none.

#### GET `/v1/vehicle-registration-codes/search`

- Current ID: `search_vehicle_registration_codes_endpoint_v1_vehicle_registration_codes_search_get`; tag: `vehicle-registration-codes`.
- Summary: Search legacy vehicle registration district codes
- Description: Searches static historical district abbreviations by code, district name, or local geography code. It does not decode full vehicle plates.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 429.
- Runtime request: `/v1/vehicle-registration-codes/search?q=Trencin&limit=1`; `data` shape: `{items: [{code: str, districtName: str, districtCode: str, regionCode: str, validFrom: null, validTo: str, status: str, notes: str}], count: int, total: int, limit: int, offset: int}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `query q` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Search query.", "title": "Q"}`
  - `query limit` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional page size.", "title": "Limit"}`
  - `query offset` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional result offset.", "title": "Offset"}`
- Limitations: Some scope wording is present; see exact description above. Examples: none.

#### GET `/v1/vehicle-registration-codes/{code}`

- Current ID: `get_vehicle_registration_code_endpoint_v1_vehicle_registration_codes__code__get`; tag: `vehicle-registration-codes`.
- Summary: Legacy vehicle registration district code lookup
- Description: Returns one static historical Slovak vehicle registration district abbreviation. This is not a current plate lookup.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 404, 429.
- Runtime request: `/v1/vehicle-registration-codes/BA`; `data` shape: `{code: str, districtName: str, districtCode: null, regionCode: str, validFrom: null, validTo: str, status: str, notes: str}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `path code` required=True: `{"type": "string", "title": "Code"}`
- Limitations: Some scope wording is present; see exact description above. Examples: none.

#### GET `/v1/school-facility-counts`

- Current ID: `list_school_facility_counts_endpoint_v1_school_facility_counts_get`; tag: `school-facility-counts`.
- Summary: List school facility aggregate counts
- Description: Returns static aggregate school facility count rows from the MŠVVaM register dataset. This is not an institution-level school directory.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 429.
- Runtime request: `/v1/school-facility-counts?limit=1`; `data` shape: `{items: [{schoolKindShort: str, schoolTypeShort: str, kindLevel1: str, kindLevel2: str, regionName: str, regionCode: str, districtName: str, districtCode: str, organizationalUnitCount: int, founderOwnershipType: str, founderType: str, country: str}], count: int, total: int, limit: int, offset: int}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `query schoolKind` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional source school-kind abbreviation filter.", "title": "Schoolkind"}`
  - `query schoolType` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional source school-type abbreviation filter.", "title": "Schooltype"}`
  - `query regionName` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional region name substring filter.", "title": "Regionname"}`
  - `query regionCode` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional region code filter.", "title": "Regioncode"}`
  - `query districtName` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional district name substring filter.", "title": "Districtname"}`
  - `query districtCode` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional district code filter.", "title": "Districtcode"}`
  - `query founderOwnershipType` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional founder ownership type filter.", "title": "Founderownershiptype"}`
  - `query founderType` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional founder type filter.", "title": "Foundertype"}`
  - `query limit` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional page size.", "title": "Limit"}`
  - `query offset` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional result offset.", "title": "Offset"}`
- Limitations: Some scope wording is present; see exact description above. Examples: none.

#### GET `/v1/school-facility-counts/stats`

- Current ID: `get_school_facility_count_stats_endpoint_v1_school_facility_counts_stats_get`; tag: `school-facility-counts`.
- Summary: School facility aggregate count stats
- Description: Returns local totals for the aggregate school facility count dataset. It does not expose per-school, staff, or pupil data.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200; actual applicable application statuses: 429.
- Runtime request: `/v1/school-facility-counts/stats`; `data` shape: `{recordCount: int, totalOrganizationalUnitCount: int, regionLinkedCount: int, districtLinkedCount: int, totalsByRegion: {SK010: int, SK021: int, SK022: int, SK023: int, SK031: int, SK032: int, SK041: int, SK042: int}, totalsByDistrict: {SK0101: int, SK0102: int, SK0103: int, SK0104: int, SK0105: int, SK0106: int, SK0107: int, SK0108: int, SK0211: int, SK0212: int, SK0213: int, SK0214: int, SK0215: int, SK0216: int, SK0217: int, SK0221: int, SK0222: int, SK0223: int, SK0224: int, SK0225: int, SK0226: int, SK0227: int, SK0228: int, SK0229: int, SK0231: int, SK0232: int, SK0233: int, SK0234: int, SK0235: int, SK0236: int, SK0237: int, SK0311: int, SK03110: int, SK03111: int, SK0312: int, SK0313: int, SK0314: int, SK0315: int, SK0316: int, SK0317: int, SK0318: int, SK0319: int, SK0321: int, SK03210: int, SK03211: int, SK03212: int, SK03213: int, SK0322: int, SK0323: int, SK0324: int, SK0325: int, SK0326: int, SK0327: int, SK0328: int, SK0329: int, SK0411: int, SK04110: int, SK04111: int, SK04112: int, SK04113: int, SK0412: int, SK0413: int, SK0414: int, SK0415: int, SK0416: int, SK0417: int, SK0418: int, SK0419: int, SK0421: int, SK04210: int, SK04211: int, SK0422: int, SK0423: int, SK0424: int, SK0425: int, SK0426: int, SK0427: int, SK0428: int, SK0429: int}, totalsBySchoolKind: {GYM: int, JŠ: int, KON: int, MŠ: int, SOŠ: int, SŠŠ: int, ZUŠ: int, ZŠ: int, ŠUP: int, ŠVVP: int}, totalsBySchoolType: {GYM: int, JŠ: int, KON: int, MŠ: int, OU: int, PŠ: int, SOŠ: int, SŠŠ: int, ZUŠ: int, ZŠ: int, ŠGYM: int, ŠMŠ: int, ŠSOŠ: int, ŠUP: int, ŠZŠ: int}, totalsByFounderType: {cirkev, náboženská spoločnosť: int, iný orgán štátnej správy: int, obec, mesto: int, regionálny úrad školskej správy: int, samosprávny kraj: int, súkromník: int, zahraničný subjekt: int}}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - none
- Limitations: Some scope wording is present; see exact description above. Examples: none.

#### GET `/v1/procurement-notices`

- Current ID: `list_procurement_notices_endpoint_v1_procurement_notices_get`; tag: `procurement-notices`.
- Summary: List public procurement notices
- Description: Returns a checked-in partial TED Search API snapshot of Slovak-buyer public procurement notices. This is not the complete national ÚVO procurement register.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 422, 429.
- Runtime request: `/v1/procurement-notices?limit=1`; `data` shape: `{items: [{id: str, title: str, noticeType: str, publicationDate: str, dispatchDate: str, buyerNames: [str], buyerCountry: str, placeOfPerformance: {city: str, postalCode: str, country: str}, tenderDeadline: null, regionCode: null, districtCode: null, municipalityCode: null, sourceUrl: str}], count: int, total: int, limit: int, offset: int}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `query noticeType` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional TED notice-type filter.", "title": "Noticetype"}`
  - `query year` required=False: `{"anyOf": [{"type": "integer", "maximum": 2100, "minimum": 2000}, {"type": "null"}], "description": "Optional publication-year filter.", "title": "Year"}`
  - `query limit` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional page size.", "title": "Limit"}`
  - `query offset` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional result offset.", "title": "Offset"}`
- Limitations: Some scope wording is present; see exact description above. Examples: none.

#### GET `/v1/procurement-notices/search`

- Current ID: `search_procurement_notices_endpoint_v1_procurement_notices_search_get`; tag: `procurement-notices`.
- Summary: Search public procurement notices
- Description: Searches the checked-in partial TED snapshot by publication number, notice title, buyer name, or place city. The endpoint does not call upstream TED or ÚVO services.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 422, 429.
- Runtime request: `/v1/procurement-notices/search?q=Bratislava&limit=1`; `data` shape: `{items: [{id: str, title: str, noticeType: str, publicationDate: str, dispatchDate: str, buyerNames: [str], buyerCountry: str, placeOfPerformance: {city: str, postalCode: str, country: str}, tenderDeadline: null, regionCode: null, districtCode: null, municipalityCode: null, sourceUrl: str}], count: int, total: int, limit: int, offset: int, query: str}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `query q` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Search text for id, title, buyer names, or place city.", "title": "Q"}`
  - `query noticeType` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional TED notice-type filter.", "title": "Noticetype"}`
  - `query year` required=False: `{"anyOf": [{"type": "integer", "maximum": 2100, "minimum": 2000}, {"type": "null"}], "description": "Optional publication-year filter.", "title": "Year"}`
  - `query limit` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional page size.", "title": "Limit"}`
  - `query offset` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional result offset.", "title": "Offset"}`
- Limitations: Some scope wording is present; see exact description above. Examples: none.

#### GET `/v1/procurement-notices/stats`

- Current ID: `get_procurement_notice_stats_endpoint_v1_procurement_notices_stats_get`; tag: `procurement-notices`.
- Summary: Public procurement notice snapshot stats
- Description: Returns totals for the checked-in TED_PARTIAL public procurement notice snapshot, explicitly including partial-coverage flags.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200; actual applicable application statuses: 429.
- Runtime request: `/v1/procurement-notices/stats`; `data` shape: `{recordCount: int, coverage: str, coverageDecision: str, acquisitionDecision: str, totalNoticesAtSource: int, noticeTypes: {can-modif: int, can-standard: int, cn-desg: int, cn-standard: int, pin-rtl: int}, publicationYears: {2026: int}, deadlineCount: int, regionLinkedCount: int, districtLinkedCount: int, municipalityLinkedCount: int}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - none
- Limitations: Some scope wording is present; see exact description above. Examples: none.

#### GET `/v1/procurement-notices/{id}`

- Current ID: `get_procurement_notice_endpoint_v1_procurement_notices__id__get`; tag: `procurement-notices`.
- Summary: Public procurement notice by TED publication number
- Description: Returns one record from the checked-in partial TED snapshot. The source URL links back to TED XML, but the API does not fetch or serve raw XML/PDF/HTML.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200, 422; actual applicable application statuses: 404, 429.
- Runtime request: `/v1/procurement-notices/670654-2026`; `data` shape: `{id: str, title: str, noticeType: str, publicationDate: str, dispatchDate: str, buyerNames: [str], buyerCountry: str, placeOfPerformance: {city: str, postalCode: str, country: str}, tenderDeadline: null, regionCode: null, districtCode: null, municipalityCode: null, sourceUrl: str}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `path id` required=True: `{"type": "string", "title": "Id"}`
- Limitations: Some scope wording is present; see exact description above. Examples: none.

#### GET `/v1/sources`

- Current ID: `list_sources_endpoint_v1_sources_get`; tag: `sources`.
- Summary: List public source catalogue
- Description: Returns the curated public provenance catalogue for served and researched datasets.
- Success: `#/components/schemas/SourceListResponse`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 429.
- Runtime request: `/v1/sources?status=historical`; `data` shape: `[{id: str, name: str, status: str, coverage: str, source: {name: str, url: str}, licence: {status: str, name: null, termsUrl: null}, attribution: str, lastUpdated: str, lastChecked: str, updateCadence: str, limitations: [str]}]`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `query status` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional public status filter.", "title": "Status"}`
  - `query coverage` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional coverage filter.", "title": "Coverage"}`
  - `query q` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional name/source substring filter.", "title": "Q"}`
- Limitations: Not explicitly discoverable in operation description. Examples: none.

#### GET `/v1/sources/{source_id}`

- Current ID: `get_source_endpoint_v1_sources__source_id__get`; tag: `sources`.
- Summary: Source catalogue entry
- Description: Returns one curated public source provenance entry by its stable registry id.
- Success: `#/components/schemas/SourceDetailResponse`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 404, 429.
- Runtime request: `/v1/sources/psc`; `data` shape: `{id: str, name: str, status: str, coverage: str, source: {name: str, url: str}, licence: {status: str, name: null, termsUrl: null}, attribution: str, lastUpdated: str, lastChecked: str, updateCadence: str, limitations: [str]}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `path source_id` required=True: `{"type": "string", "title": "Source Id"}`
- Limitations: Not explicitly discoverable in operation description. Examples: none.

#### GET `/v1/business-days/check`

- Current ID: `check_business_day_v1_business_days_check_get`; tag: `business-days`.
- Summary: Check a business day
- Description: Returns whether an ISO date is a Slovak business day (Monday-Friday, not a known public holiday).
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 429.
- Runtime request: `/v1/business-days/check?date=2026-10-08`; `data` shape: `{date: str, weekday: int, isWeekend: bool, isHoliday: bool, holidayName: null, isBusinessDay: bool, supportedYears: [int]}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `query date` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "ISO date to check.", "title": "Date"}`
- Limitations: Not explicitly discoverable in operation description. Examples: none.

#### GET `/v1/business-days/add`

- Current ID: `add_business_days_endpoint_v1_business_days_add_get`; tag: `business-days`.
- Summary: Add business days
- Description: Adds (or subtracts) business days from an ISO date using local Slovak holiday data.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 429.
- Runtime request: `/v1/business-days/add?date=2026-10-08&days=1`; `data` shape: `{date: str, days: int, result: str, resultIsBusinessDay: bool, supportedYears: [int]}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `query date` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "ISO start date.", "title": "Date"}`
  - `query days` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Business days to add (negative to subtract).", "title": "Days"}`
- Limitations: Not explicitly discoverable in operation description. Examples: none.

#### GET `/v1/business-days/between`

- Current ID: `business_days_between_endpoint_v1_business_days_between_get`; tag: `business-days`.
- Summary: Count business days
- Description: Counts business days in a bounded inclusive ISO date interval using local Slovak holiday data.
- Success: `G: object / additionalProperties=true`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 429.
- Runtime request: `/v1/business-days/between?from=2026-10-08&to=2026-10-09`; `data` shape: `{from: str, to: str, totalDays: int, weekendDays: int, holidayDays: int, holidays: [empty], businessDays: int, supportedYears: [int]}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `query from` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "ISO start date (inclusive).", "title": "From"}`
  - `query to` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "ISO end date (inclusive).", "title": "To"}`
- Limitations: Not explicitly discoverable in operation description. Examples: none.

#### GET `/v1/exchange-rates/latest`

- Current ID: `get_latest_rates_v1_exchange_rates_latest_get`; tag: `exchange-rates`.
- Summary: Latest ECB EUR reference rates in the OpenSK snapshot
- Description: Returns the newest ECB publication date available in the current materialized OpenSK snapshot — not a live or today's market rate; the snapshot may lag the latest ECB publication until refreshed offline. Source: European Central Bank euro foreign exchange reference rates, transformed by OpenSK from the official ECB eurofxref XML feed into normalized JSON (rate values reproduced verbatim as decimal strings; no rounding, inversion or arithmetic). Direction: `1 EUR = rate units of the foreign currency` (USD = "1.16" means 1 EUR = 1.16 USD). Rates are published by the ECB for information purposes only; the ECB strongly discourages using them for transaction or settlement purposes, and they are not live market prices. Currency availability changes historically (legacy euro-area and suspended series are included).
- Success: `#/components/schemas/ExchangeRateDayResponse`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 404, 429.
- Runtime request: `/v1/exchange-rates/latest?currency=USD`; `data` shape: `{date: str, base: str, directionSemantics: str, rates: {USD: str}, notice: str}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `query currency` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional ISO 4217 alpha-3 currency filter (case-insensitive).", "title": "Currency"}`
- Limitations: Some scope wording is present; see exact description above. Examples: none.

#### GET `/v1/exchange-rates/{date}`

- Current ID: `get_rates_for_date_v1_exchange_rates__date__get`; tag: `exchange-rates`.
- Summary: ECB EUR reference rates for an exact publication date
- Description: Returns the ECB rate set published on exactly `{date}` (ISO YYYY-MM-DD). If the ECB published nothing on that date (weekend, TARGET holiday, or a date outside snapshot coverage), the response is 404 — never a neighbouring, previous or nearest date. Source: European Central Bank euro foreign exchange reference rates, transformed by OpenSK from the official ECB eurofxref XML feed into normalized JSON (rate values reproduced verbatim as decimal strings; no rounding, inversion or arithmetic). Direction: `1 EUR = rate units of the foreign currency` (USD = "1.16" means 1 EUR = 1.16 USD). Rates are published by the ECB for information purposes only; the ECB strongly discourages using them for transaction or settlement purposes, and they are not live market prices. Currency availability changes historically (legacy euro-area and suspended series are included).
- Success: `#/components/schemas/ExchangeRateDayResponse`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 404, 429.
- Runtime request: `/v1/exchange-rates/1999-01-04?currency=USD`; `data` shape: `{date: str, base: str, directionSemantics: str, rates: {USD: str}, notice: str}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `path date` required=True: `{"type": "string", "title": "Date"}`
  - `query currency` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Optional ISO 4217 alpha-3 currency filter (case-insensitive).", "title": "Currency"}`
- Limitations: Some scope wording is present; see exact description above. Examples: none.

#### GET `/v1/eu-funds/projects`

- Current ID: `list_projects_v1_eu_funds_projects_get`; tag: `eu-funds`.
- Summary: List privacy-approved ITMS21+ project references
- Description: MIRRI SR / ITMS21+ project references, 2021–2027 only. CC BY, as declared by the Slovak national open-data catalogue (version not separately identified). OpenSK transformed/privacy-minimized the source; not an official representation. Only positively reviewed legal-entity beneficiary projects are exposed; natural-person, ambiguous/missing/unreviewed forms are wholly excluded. Titles are omitted. Manual local snapshot, not live; can lag upstream. No ITMS2014+, payment, procurement or irregularity/receivable surface. contractedTotal is an exact decimal string of celkovaZazmluvnenaSuma (total contracted amount), not paid funds; the manual does not separately establish currency, so no EUR claim is made.
- Success: `#/components/schemas/ListResponse`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 429.
- Runtime request: `/v1/eu-funds/projects?limit=1`; `data` shape: `{items: [{projectCode: str, sourceId: int, status: {label: str, inImplementation: bool, completed: bool}, programme: {code: str, nameSk: str, shortName: str, cci: str}, call: {code: str, nameSk: str}, beneficiary: {name: str, ico: str, legalForm: {code: str, nameSk: str}}, implementationRegions: [{nuts: str, nameSk: str}], financials: {contractedTotal: str}, sourceUpdatedAt: str, sourceUrl: str}], count: int, total: int, limit: int, offset: int}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `query limit` required=False: `{"type": "string", "description": "Page size 1–200 (default 50).", "default": "50", "title": "Limit"}`
  - `query offset` required=False: `{"type": "string", "description": "Nonnegative offset (default 0).", "default": "0", "title": "Offset"}`
  - `query programmeCode` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Exact six-digit programme code.", "title": "Programmecode"}`
  - `query callCode` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Exact source call code; case-sensitive, printable, max 256 characters.", "title": "Callcode"}`
  - `query beneficiaryIco` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Exact eight-digit IČO after the legal-entity privacy gate.", "title": "Beneficiaryico"}`
  - `query inImplementation` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "true/false, case-insensitive; AND with other filters.", "title": "Inimplementation"}`
  - `query completed` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "true/false, case-insensitive; AND with other filters.", "title": "Completed"}`
  - `query nuts` required=False: `{"anyOf": [{"type": "string"}, {"type": "null"}], "description": "Exact verified implementation NUTS reference; no seat/geography inference.", "title": "Nuts"}`
- Limitations: Some scope wording is present; see exact description above. Examples: none.

#### GET `/v1/eu-funds/projects/{projectCode}`

- Current ID: `get_project_v1_eu_funds_projects__projectCode__get`; tag: `eu-funds`.
- Summary: Look up an ITMS21+ project by official project code
- Description: MIRRI SR / ITMS21+ project references, 2021–2027 only. CC BY, as declared by the Slovak national open-data catalogue (version not separately identified). OpenSK transformed/privacy-minimized the source; not an official representation. Only positively reviewed legal-entity beneficiary projects are exposed; natural-person, ambiguous/missing/unreviewed forms are wholly excluded. Titles are omitted. Manual local snapshot, not live; can lag upstream. No ITMS2014+, payment, procurement or irregularity/receivable surface. contractedTotal is an exact decimal string of celkovaZazmluvnenaSuma (total contracted amount), not paid funds; the manual does not separately establish currency, so no EUR claim is made.
- Success: `#/components/schemas/DetailResponse`.
- Documented statuses: 200, 422; actual applicable application statuses: 400, 404, 429.
- Runtime request: `/v1/eu-funds/projects/401000B287`; `data` shape: `{projectCode: str, sourceId: int, status: {label: str, inImplementation: bool, completed: bool}, programme: {code: str, nameSk: str, shortName: str, cci: str}, call: {code: str, nameSk: str}, beneficiary: {name: str, ico: str, legalForm: {code: str, nameSk: str}}, implementationRegions: [{nuts: str, nameSk: str}], financials: {contractedTotal: str}, sourceUpdatedAt: str, sourceUrl: str}`.
- Parameters (actual OpenAPI; required/default/nullable captured literally):
  - `path projectCode` required=True: `{"type": "string", "title": "Projectcode"}`
- Limitations: Some scope wording is present; see exact description above. Examples: none.

## Production freeze baseline

Working-checkout SHA-256 (Windows bytes; final must match in this checkout).
Git/LF comparison in tests normalizes checkout line endings, not dataset contents.

| File | Before = after SHA-256 (same working checkout) |
| --- | --- |
| data/banks.json | `736c633074c521c7c4e1b48a7602a700ce7006897d36bbb047bcc9d6a65f2e60` |
| data/companies.json | `b2ce76bb0d60676fb1581049e6ff3f7ef250d8068d9bea83da36d542b615a063` |
| data/districts.json | `9b7fd0752b416383d6fc7247555614b040a91d7f789a9bf82baa4bd245efe66b` |
| data/eu_funds_projects.json | `1981a8fdb3232e449e2cca5c17cb30a12baada7b7e611fcbead02aa790605ee1` |
| data/exchange_rates.json | `ad08a3db3130333d18362010c87bfd94c899c108bc1acfa7d954c57209f87105` |
| data/holidays.json | `dfb2f3616fa9671bbe758388f68c9b99dc47f98e0faac5863787482b7f942b9d` |
| data/municipalities.json | `d5a7209d18eb1506f573f7b95550d63cbb99598c96686b76cf5b16270de01c95` |
| data/phone_areas.json | `5bb85a40cca6b8d1770ce92f32426595d7414985900dda1cb5db7ec3d033a57c` |
| data/procurement_notices.json | `443a16cbd6758fa05421285a7fb80425d9130f8725f08ba38be028736bdb8c55` |
| data/psc.json | `4b7346bbef19a86576fa5ecaa5f7d7c2afa36be5ff711753281b3a042b42bc55` |
| data/regions.json | `d835a28c06a80aeb72fff62f9b7cba20db5a07f8c91e189afca57dfaa3894e85` |
| data/school_facility_counts.json | `088edc4e0ab13f8960d39ff1449dae5bfde0463aeed7fbdb4b327771b82fbeeb` |
| data/sources.json | `6451f423077f2e13933dbaa5a2810c99d56bacba9205db9ec714f0d401055f9d` |
| data/vehicle_registration_codes.json | `8e9ecc4a7cb6be5f36f609fdf26e54f8bf8989c669abe7bedd8b2061687540e2` |

## After implementation (0.23.12)

### Coverage and client-tool readiness

| Measure (operations, not individual schemas) | Before | After |
| --- | ---: | ---: |
| Public GET operations | 39 | 39 |
| Intentional typed success contract | 9 | 39 |
| Generic/untyped success object | 30 | 0 |
| Explicit stable unique operationId | 0 | 39 |
| Operation-level success response examples | 0 | 39 |
| Operations documenting applicable typed application errors | 0 | 38 |
| Operations with parameter descriptions and examples for every parameter | 0 of 32 parameterized operations | 32 of 32 |

The before example count is **operation response examples**; exchange-rate schema
fields already had examples reachable by its two operations. All 39 now have
validated whole-envelope examples; long non-paginated arrays are explicitly
labelled excerpts. PSC also has a full `include=geography` example. Actual captured
400/404/422 examples are operation-specific; 429/503 examples match existing handlers.
Health has no applicable application error or 429; this is intentional, not a gap.

All parameters are reviewed in `schemas/openapi.py` against parser behavior,
including defaults/maxima, enum-like strings, exact versus substring matching,
case/diacritic handling, date input and required query values. Document refinements
are **OpenAPI-only**, never fed into FastAPI request validators. An important
audit correction: district codes accept `SK` plus **four or five** digits, not only
the often-described `SK####` (e.g. `SK03111`). Business dates also retain Python's
existing ISO basic/week-date acceptance; exchange dates remain strict YYYY-MM-DD.
Required manual query parameters are marked required in OpenAPI while omission
continues to return the established **400**, not 422. Genuine framework integer
422 paths remain holiday year and procurement year; all use `ErrorResponse`, not
the framework's default detail-list schema. 503 is only on the two company routes.

All schema references resolve, names are distinct, path parameters correspond to
placeholders, IDs are unique and serialization is JSON-safe. Required nullable
fields and aliases are checked against actual payloads. No undocumented success
polymorphism: every operation preserves its historical array/object/page shape.
No OpenAPI validator dependency existed; bounded structural/ref checks and
Pydantic validation suffice here. **No SDK was generated or published.**

Remaining intentional maps (not untyped objects): ECB `rates` is
`dict[str, str]` for varying currency codes; school stats' five `totalsBy*` maps
and procurement stats' `noticeTypes`/`publicationYears` are `dict[str, int]` for
variable categories. Their typed `additionalProperties` is necessary. No
unconstrained `additionalProperties: true` remains. Error codes/messages remain
strings because codes vary by operation; descriptions list relevant families.
Existing EU-fund defaulted serialization fields remain defaulted internally and
are marked required in serialization schema, not removed from responses.

FastAPI normally removes null values from literal OpenAPI examples. The small
documentation helper restores the captured example payloads after generation so
`error: null`, nullable `lastUpdated`, and nullable dataset fields are not silently
lost. This affects **OpenAPI only**. New response models reject unknown fields
rather than silently filter them; optional geography is not injected. Existing
bank/source/exchange/EU serialization behavior is preserved.

### Reviewed final inventory

The complete method/path/ID set is locked by
`tests/fixtures/public-operations.json`; tests compare it exactly, not just a
subset or count. Models below refer to focused domain contracts; `SuccessResponse`
and `Page` only describe envelopes/wrappers already present, not new wrappers.

| Operation | Stable ID | Success model |
| --- | --- | --- |
| GET `/` | `get_root` | `SuccessResponse[ProjectInfo]` |
| GET `/v1/health` | `get_health` | `SuccessResponse[Health]` |
| GET `/v1/banks` | `list_banks` | `BanksResponse` |
| GET `/v1/banks/{code}` | `get_bank` | `BankResponse` |
| GET `/v1/iban/validate/{iban}` | `validate_iban` | `IbanValidationResponse` |
| GET `/v1/holidays/{year}` | `get_holidays` | `SuccessResponse[list[Holiday]]` |
| GET `/v1/psc` | `list_psc` | `SuccessResponse[Page[PSCMatch]]` |
| GET `/v1/psc/search` | `search_psc` | `SuccessResponse[Page[PSCMatch]]` |
| GET `/v1/psc/stats` | `get_psc_stats` | `SuccessResponse[PSCStats]` |
| GET `/v1/psc/{psc}` | `get_psc` | `SuccessResponse[PSCLookup]` |
| GET `/v1/companies/{ico}` | `get_company` | `SuccessResponse[Company]` |
| GET `/v1/ico/{ico}` | `get_company_by_ico` | `SuccessResponse[Company]` |
| GET `/v1/regions` | `list_regions` | `SuccessResponse[list[Region]]` |
| GET `/v1/regions/{code}` | `get_region` | `SuccessResponse[Region]` |
| GET `/v1/districts` | `list_districts` | `SuccessResponse[list[District]]` |
| GET `/v1/districts/{code}` | `get_district` | `SuccessResponse[District]` |
| GET `/v1/municipalities` | `list_municipalities` | `SuccessResponse[list[Municipality]]` |
| GET `/v1/municipalities/{code}` | `get_municipality` | `SuccessResponse[Municipality]` |
| GET `/v1/phone-areas` | `list_phone_areas` | `SuccessResponse[Page[PhoneArea]]` |
| GET `/v1/phone-areas/search` | `search_phone_areas` | `SuccessResponse[Page[PhoneArea]]` |
| GET `/v1/phone-areas/{code}` | `get_phone_area` | `SuccessResponse[PhoneAreaLookup]` |
| GET `/v1/vehicle-registration-codes` | `list_vehicle_registration_codes` | `SuccessResponse[Page[VehicleRegistrationCode]]` |
| GET `/v1/vehicle-registration-codes/search` | `search_vehicle_registration_codes` | `SuccessResponse[Page[VehicleRegistrationCode]]` |
| GET `/v1/vehicle-registration-codes/{code}` | `get_vehicle_registration_code` | `SuccessResponse[VehicleRegistrationCode]` |
| GET `/v1/school-facility-counts` | `list_school_facility_counts` | `SuccessResponse[Page[SchoolFacilityCount]]` |
| GET `/v1/school-facility-counts/stats` | `get_school_facility_count_stats` | `SuccessResponse[SchoolFacilityStats]` |
| GET `/v1/procurement-notices` | `list_procurement_notices` | `SuccessResponse[Page[ProcurementNotice]]` |
| GET `/v1/procurement-notices/search` | `search_procurement_notices` | `SuccessResponse[ProcurementSearch]` |
| GET `/v1/procurement-notices/stats` | `get_procurement_notice_stats` | `SuccessResponse[ProcurementStats]` |
| GET `/v1/procurement-notices/{id}` | `get_procurement_notice` | `SuccessResponse[ProcurementNotice]` |
| GET `/v1/sources` | `list_sources` | `SourceListResponse` |
| GET `/v1/sources/{source_id}` | `get_source` | `SourceDetailResponse` |
| GET `/v1/business-days/check` | `check_business_day` | `SuccessResponse[BusinessDayCheck]` |
| GET `/v1/business-days/add` | `add_business_days` | `SuccessResponse[BusinessDayAddition]` |
| GET `/v1/business-days/between` | `count_business_days` | `SuccessResponse[BusinessDayInterval]` |
| GET `/v1/exchange-rates/latest` | `get_exchange_rates_latest` | `ExchangeRateDayResponse` |
| GET `/v1/exchange-rates/{date}` | `get_exchange_rates_by_date` | `ExchangeRateDayResponse` |
| GET `/v1/eu-funds/projects` | `list_eu_funds_projects` | `ListResponse` |
| GET `/v1/eu-funds/projects/{projectCode}` | `get_eu_funds_project` | `DetailResponse` |

### PSC correction and compatibility

**0.23.12 corrects `/v1/psc/{psc}` for grouped PSC records: `matchCount` now
counts logical flat matches and `matches` contains those flat records, consistent
with list/search behavior. The underlying dataset, source provenance and coverage
are unchanged.** This is a pre-1.0 correctness fix, not a data migration. There
are currently no known external consumers, but clients depending on the erroneous
extra nested container must adjust; this is not hidden as a purely additive change.

Before: `01001` lookup returned `matchCount=1` and one outer match containing its
own `matchCount=2`/`matches`. After: `matchCount=2`, two flat matches for **Mojš
517801** and **Žilina 517402**, identical to collection/filter/search identities.
Current production data identifies 517801 as **Mojš**, not Žilinská Lehota; no
label/source correction is inferred from earlier research prose.

Primary is **Mojš 517801** from normalized records under the unchanged reviewed
sort key (resolvable municipality, open-ended validity, delivery post/name/code;
ties retain deterministic flat collection order). Each match resolves its own
region/district/municipality with `include=geography`; primary geography matches
the first flat match. Optional unresolved geography stays absent. No double
matches or repeated geography wrappers. Single-match groups also lose the
erroneous outer storage container. Flat collection/search/stats bodies do not change.

| Change | Runtime JSON change? | Intentional? | Breaking? | Notes |
| --- | --- | --- | --- | --- |
| Typed success/error models | No for established responses | Yes | No observed runtime break | All 39 representative bodies validate; no field filtering/renaming/null injection |
| PSC grouped lookup/count | **Yes** | **Yes, correctness fix** | Clients relying on buggy nesting must adjust | Primary flat fields + flat matches, same dataset; includes geography variant and single-match groups |
| Explicit operation IDs | OpenAPI only | Yes | Tooling names change | Reviewed stable IDs replace generated artifacts; URLs unchanged |
| Parameter/error/examples/docs annotations | OpenAPI only | Yes | No runtime change | Manual 400 preserved; genuine 422 envelope documented |
| Project SemVer | Root `data.version`, OpenAPI `info.version` | Yes | No namespace change | 0.23.11 → 0.23.12; metadata.version remains v1 |
| README/quickstart/pilot | No | Yes | No | No messages sent, infrastructure added or source permission inferred |
| Data/provenance/freshness/cache policy/limiter | **No** | Frozen | No | Affected PSC body-derived ETags may change; Last-Modified unchanged |

Evidence: `public-contract-baseline.json` preserves normalized pre-change body
digests and cache/Last-Modified for all 39 operations; 38 match exactly afterwards
(health clock/root SemVer normalization only), with the explicit PSC lookup
exception independently checked. It includes both company aliases, all historical
shape variants, bank additive metadata and an invalid-checksum IBAN (200 false).
Copy-paste docs use the separate smoke helper's valid **synthetic** IBAN
`SK5409000000000000000001`, checked to return `valid=true`; neither example is a
payment/account-existence claim. No giant response/OpenAPI snapshot is committed.

### Red-team checklist

| Question | Result |
| --- | --- |
| 1. Any production JSON changed? | **NO**, all 14 same-checkout hashes equal before/after; canonical Git-byte fixture also checked |
| 2. Any source/licence state changed? | **NO**, sources/outreach package unchanged |
| 3. Route count changed? | **NO — 39 GET operations** |
| 4. `/v1` changed? | **NO** |
| 5. metadata.version changed? | **NO — v1** |
| 6. Normal payload shape changed? | **Only approved PSC grouped lookup correction**, plus expected root project-version bump |
| 7. PSC matches flat? | **YES**, no grouped container in any indexed logical record |
| 8. matchCount equals len(matches)? | **YES** |
| 9. Lookup/list share logical records? | **YES**, index uses load_psc_records; search uses same loader |
| 10. PSC JSON modified? | **NO** |
| 11. Successor semantics introduced? | **NO**, PSC stays historical/partial and parked |
| 12. Partial/seed/aggregate limits visible? | **YES**, operation descriptions, not README alone |
| 13. Stable unique IDs for every GET? | **YES**, complete locked inventory |
| 14. Intentional success schema for every GET? | **YES**, 39/39 |
| 15. Response model filtering/renaming? | **NO** in checked payloads; model round trips and baseline digests checked |
| 16. Manual malformed input changed to 422? | **NO**, manual 400 cases retained; existing integer 422 unchanged |
| 17. Standard errors documented? | **YES**, only applicable statuses; health exempt, 503 companies only |
| 18. README/quickstart examples verified? | **YES**, local actual-data request tests and synthetic checksum assertion |
| 19. SDK generated? | **NO** |
| 20. Dataset/source added? | **NO** |

No runtime network, acquisitions, database, Redis, source-rights research or
automatic outreach. Health remains operational/no-store/rate-limit exempt. Cache
policy, limiter identity logic and 100/60/IP budget are unchanged. Strong ETag
still uses exact response-body SHA-256 (existing first-32-hex representation),
matching If-None-Match yields **304 / empty body**; Last-Modified retains dataset
dates, including PSC **2026-06-02**. Public docs and schema remain `/docs` and
`/openapi.json`; no frontend or route added. Data Git tree remains
`29bb5725338bd7989b34097ce61cd9da11cf9e33`.

### Validation record

Final local gates (2026-10-28), project **0.23.12**:

- `python scripts/validate_datasets.py`: **0 errors / 44 existing warnings**, all
  14 datasets; no pending rights/coverage warning suppressed.
- `python scripts/check_referential_integrity.py`: passed.
- `python -m pytest -q`: **1,016 passed** (182 added contract/PSC/docs tests).
- `python -m compileall scripts routers services tests schemas`: passed.
- `git diff --check`: passed; staged/full-branch checks also required before push.
- Local HTTP smoke: **41 passed / 0 failed**. Actual `curl.exe` against all **12
  distinct README/quickstart targets** passed with expected 200/400/404 statuses;
  URLs/query strings match the public-base examples. No deployed-version or source
  acquisition call was needed.
- Runtime success-model validation and baseline comparison across **all 39**
  operations; only PSC lookup differs after root-SemVer/health-clock normalization.
  Existing other response ETags are identical; root ETag changes with project
  SemVer and affected PSC lookup ETag changes with its approved body correction.
- Additional exhaustive local check of **all 1,420 PSC lookups**: flat matches,
  count/list parity, deterministic primary and expanded-geography model validation.
- OpenAPI JSON serialization, 39 GETs, exact paths/IDs, all refs/examples/models,
  standard error envelopes, manual 400s, existing 422s, 429 headers/exemption and
  company-only 503 verified offline. Every conditional response checked 304/empty.
- **All 14 production JSON byte hashes equal before/after in the same checkout**
  (table above); canonical LF hashes locked separately for cross-platform CI.
  `data/`, cache/limiter implementations, dependency file and outreach package have
  zero diff from main. Source/freshness/reuse verdicts remain frozen.

Hosted CI is reported separately by PR checks; no auto-merge/tag/release.

Next: the maintainer-run [5–10 developer pilot](../developer-adoption.md), with
concrete feedback before another implementation milestone or SDK. Source-owner
reply monitoring stays separate. **PSC remains PARKED / NO_GO_SUCCESSOR_PSC.**
