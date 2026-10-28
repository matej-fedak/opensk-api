# TED buyer privacy evidence spike — 0.23.13

Checked **2026-10-28**. Research-only on `data/expand-existing-coverage`, starting
at `0ec659788133d82d57ed2500f63fbed89113fe4d`; version `0.23.13-dev`.

## Verdict

**NO_GO_PROCUREMENT_EXPANSION** under the reviewed Search projection and required
source-based legal-person gate. Of **68,926** acquired notices, **zero** have any
returned `buyer-person` value. This includes **22,730 explicitly identified eForms
notices**. No defensible newer-year boundary cures the missing discriminator.
Neither procurement nor holidays are promoted. This is not a finding that all
buyers are natural persons; it is a finding that their status cannot be approved
using this evidence. It does not revoke or independently certify the existing
100-record production snapshot.

## Problem and method

The earlier full-history capture exposed individual/sole-trader buyer labels
inside the approved `buyer-name` field. A field-name allowlist cannot ensure its
values are institutional names. This spike used **no name/suffix/honorific, IČO,
punctuation, capitalization, word-count, regex or ML legal-status classifier** and
no manual institutional whitelist. Names were used only to revisit previously
observed private diagnostic cases, not to decide eligibility.

The original capture had no privacy markers. A second, private metadata-only
capture used the same query, cutoff, latest-only option and identity:

```text
POST https://api.ted.europa.eu/v3/notices/search
query: buyer-country = SVK AND publication-date <= 20261028
paginationMode: ITERATION
onlyLatestVersions: true
limit: 250
fields: publication-number, publication-date, buyer-country, buyer-person,
        buyer-legal-type, buyer-identifier, customization-id, notice-subtype
```

Dates/countries verify the join scope; customization/subtype support source-native
generation analysis. No names, titles, contacts or addresses were requested again.
TED automatically includes format links even with a narrow field list; these were
retained only in private hash-verified pages, never fetched or emitted by the
analyzer. No notice XML/PDF/HTML/detail download or other registry query occurred.

Second capture: **21:47:19.154461Z–21:51:53.214599Z**, 68,926 reported/acquired,
**277 pages** (276 nonempty + empty terminal), **311,941,265 bytes**; HTTP 277 × 200,
16 retried 429s. Zero acquisition-scope/date/identity errors and stable totals.
Full non-content summary and hashes:
[procurement-buyer-privacy-acquisition.json](procurement-buyer-privacy-acquisition.json).
Original evidence: [procurement-coverage-acquisition.json](procurement-coverage-acquisition.json).

Both manifests, every page hash/size, query/profile/selected fields, request/token
chain, timeout flags, stable total, uniqueness and terminal empty page were
verified offline. Canonical identity is exact numeric zero-padding of the TED
publication number, not fuzzy identity. **Exact ID sets agree: 68,926 shared,
0 original-only, 0 metadata-only**. Joined publication dates and buyer-country
arrays also agree exactly. Separate PITs do not prove that every unrequested field
was unchanged between runs; no such claim is needed for these joins.
Latest-only is an explicit verified request option; the selected response has no
independent per-row obsolete-version assertion, so this is not a separate audit
of TED's internal version graph.

Private workspace:
`C:\Users\matej\AppData\Local\Temp\opencode\ted-02313\privacy\`.
Raw pages, tokens, identifier values, review titles and buyer labels are not
committed. `scripts/analyze_procurement_buyer_privacy.py` reproduces aggregates:

```powershell
python scripts/analyze_procurement_buyer_privacy.py --original "C:\Users\matej\AppData\Local\Temp\opencode\ted-02313\full-v2" --metadata "C:\Users\matej\AppData\Local\Temp\opencode\ted-02313\privacy\metadata" --output "C:\Users\matej\AppData\Local\Temp\opencode\ted-02313\privacy\analysis.json"
```

## Current official evidence and semantics

1. [Search field catalogue](https://docs.ted.europa.eu/ODS/latest/reuse/field-list.html),
   SHA-256 `79324dc627ee846f137e8cf4d069509784d51dcc7770f592dcd58096e261a419`.
2. [Current Search OpenAPI](https://api.ted.europa.eu/api-v3.yaml), API 3.0.0,
   SHA-256 `ad200964a9ce2e477702836917ee5711df7d6c278c6dddc16a7d62bf55dcac8c`.
3. eForms SDK **1.15** [Parties](https://docs.ted.europa.eu/eforms/latest/schema/parties.html),
   especially role requirements, table 3 and Winner/tenderer;
   SHA-256 `9b7dd90473a2ad2e9cd61b970695627a93ccb43372a8dcd95815dfb9d2e569e7`.
4. [Identifiers and references](https://docs.ted.europa.eu/eforms/latest/schema/identifiers.html),
   especially BT-501, OPT-002, OPT-200, OPT-300 and BT-13720;
   SHA-256 `17f3c349c003e03ccc5380e8c7694caa1173267e081a7d67e5205145132836c5`.
5. [BT-633](https://docs.ted.europa.eu/eforms/latest/reference/business-terms/BT-633.html),
   [BT-11](https://docs.ted.europa.eu/eforms/latest/reference/business-terms/BT-11.html),
   [BT-501](https://docs.ted.europa.eu/eforms/latest/reference/business-terms/BT-501.html),
   and [BT-11 code list](https://docs.ted.europa.eu/eforms/latest/reference/code-lists/buyer-legal-type.html)
   version **20250618-0**. Eight documentation captures have private URL/status/
   timestamp/byte/hash records in `official-evidence.json`.

| Search field | Verified mapping / meaning | Privacy role |
| --- | --- | --- |
| `buyer-person` | `BT-633-Organization[OPT-200-Organization-Company = OPT-300-Procedure-Buyer]`; independent boolean array | Explicit true = natural person; false = juridical person, **where applicable**. Never equate absent with false. |
| `buyer-legal-type` | `BT-11-Procedure-Buyer`; independent string array; procurement authority/entity categories | **CORROBORATING_EVIDENCE**, not a demonstrated general non-natural-person guarantee. |
| `buyer-identifier` | `BT-501-Organization-Company` with the same buyer-role selector; independent string array | Authority-issued organisation identifiers, not a natural/legal-person test; values never committed. |
| `organisation-person-buyer` | Same BT-633 concept, catalogue mapping lacks the explicit buyer-role selector | Not a superior discriminator or a join key; not acquired. |
| `organisation-identifier-buyer`, `corporate-body` | BT-501 mappings; OpenAPI string arrays | Despite its name, `corporate-body` is **not** a corporate-status boolean; not acquired. |
| `tenderer-legal-form-description-lot`, `tenderer-legal-form-lot` | [BT-76](https://docs.ted.europa.eu/eforms/latest/reference/business-terms/BT-76.html) / [BT-761](https://docs.ted.europa.eu/eforms/latest/reference/business-terms/BT-761.html) | Tenderer legal-form requirements, not proof of the actual buyer's legal identity. |

**Applicability is decisive.** Parties defines BT-633 true/false in the
Winner/tenderer section. Table 3 says **“Only for economic operators (tenderer,
winner, service provider …)”**; the buyer-role requirements mark Natural Person
**“—” (not applicable)**. A Search field's existence therefore does not promise
that buyer notices have an explicit false indicator. Not-applicable is not a
source assertion that all buyers are juridical persons. The all-missing corpus
is consistent with these documented limitations, not evidence of false status.

BT-11 includes authority/public-body/public-undertaking categories, but also
`org-sub*` (subsidised contracting organisations), `def-cont` (defence contractor)
and `spec-rights-entity`. The reviewed documentation supplies procurement
categories, not a proved buyer-by-buyer non-natural-person guarantee or a safe
subset mapping with complete Search association. Even an authority-looking code
must not stand in for all buyers on a joint notice. No code is adopted as the
primary discriminator. Observed legacy values `8`, `9`, `Z`, `grp-p-aut` are not
silently coerced into the current code list or treated as approval.

Parties explicitly permits **one or more BT-501 identifiers for one organisation**.
Neither identifier presence, count, format nor a business-number-like value
establishes legal-person status. No identifier pattern was evaluated for approval.

## Completeness: all 68,926 notices

Marker groups are disjoint: true-only, false-only, no values, mixed true/false,
malformed. Python integers/strings/null/scalars are not accepted as booleans.
An empty array would supply no status, not false; none occurred here.

| Measure | Notices |
| --- | ---: |
| `buyer-person` explicitly true-only | 0 |
| Explicitly false-only | 0 |
| Missing | **68,926** |
| Mixed true/false | 0 |
| Malformed/unexpected | 0 |
| BT-11 present / missing / malformed | **67,430 / 1,496 / 0** |
| BT-501 present / missing / malformed | **68,288 / 638 / 0** |

All missing markers are **absent keys**, not returned nulls, empty arrays or
false values. Explicit-true and explicit-false *occurrences*, including any mixed
row, are also both zero. BT-11 “present” below means nonempty string array, not
that every string belongs to the current code list.

### By publication year

In **every row of every breakdown below**, true-only / false-only / mixed /
malformed counts are **0 / 0 / 0 / 0**; missing marker count equals Total.
BT-11 and identifier malformed counts are zero throughout. This convention also
applies to schema and name-cardinality breakdowns, without hiding zero groups.

| Year | Total = marker missing | BT-11 present | BT-11 missing | Identifier present | Identifier missing | Eligible |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2016 | 801 | 801 | 0 | 792 | 9 | 0 |
| 2017 | 5,191 | 5,191 | 0 | 5,072 | 119 | 0 |
| 2018 | 5,874 | 5,874 | 0 | 5,783 | 91 | 0 |
| 2019 | 5,587 | 5,587 | 0 | 5,475 | 112 | 0 |
| 2020 | 5,718 | 5,718 | 0 | 5,651 | 67 | 0 |
| 2021 | 6,757 | 6,757 | 0 | 6,714 | 43 | 0 |
| 2022 | 9,058 | 9,058 | 0 | 9,002 | 56 | 0 |
| 2023 | 8,802 | 8,580 | 222 | 8,726 | 76 | 0 |
| 2024 | 6,923 | 6,477 | 446 | 6,885 | 38 | 0 |
| 2025 | 7,624 | 7,174 | 450 | 7,612 | 12 | 0 |
| 2026 | 6,591 | 6,213 | 378 | 6,576 | 15 | 0 |

### By exact source notice type

Use exact `notice-type` values rather than invent a schema generation from a
type prefix. `brin-*` business-register notices are present in the approved query;
the query is not, by itself, a guarantee that every hit is a procurement notice.
Their 486 rows are not silently dropped to improve completeness percentages.

| Source type | Total = marker missing | BT-11 present | BT-11 missing | Identifier present | Identifier missing |
| --- | ---: | ---: | ---: | ---: | ---: |
| brin-ecs | 476 | 425 | 51 | 0 | 476 |
| brin-eeig | 10 | 7 | 3 | 0 | 10 |
| can-desg | 136 | 136 | 0 | 136 | 0 |
| can-modif | 5,752 | 4,311 | 1,441 | 5,752 | 0 |
| can-social | 11 | 11 | 0 | 11 | 0 |
| can-standard | 28,969 | 28,969 | 0 | 28,938 | 31 |
| cn-desg | 149 | 149 | 0 | 149 | 0 |
| cn-social | 13 | 13 | 0 | 13 | 0 |
| cn-standard | 20,062 | 20,061 | 1 | 20,040 | 22 |
| corr | 11,352 | 11,352 | 0 | 11,259 | 93 |
| pin-buyer | 6 | 6 | 0 | 6 | 0 |
| pin-cfc-social | 2 | 2 | 0 | 2 | 0 |
| pin-cfc-standard | 1 | 1 | 0 | 1 | 0 |
| pin-only | 1,062 | 1,062 | 0 | 1,058 | 4 |
| pin-rtl | 104 | 104 | 0 | 104 | 0 |
| pin-tran | 24 | 24 | 0 | 22 | 2 |
| qu-sy | 25 | 25 | 0 | 25 | 0 |
| subco | 3 | 3 | 0 | 3 | 0 |
| veat | 769 | 769 | 0 | 769 | 0 |

### Deterministically identifiable schema generation

`customization-id = eforms-sdk-x.y` is positive eForms evidence (OPT-002).
**22,730** notices carry it; SDKs 1.7: 10,605; 1.9: 1; 1.10: 58; 1.11: 2,058;
1.12: 20; 1.13: 9,945; 1.14: 43. All also have `notice-subtype`.
**46,196** omit both fields: legacy-compatible/unresolved, **not deterministically
certified legacy** from absence alone. No XML-generation field was captured for
those rows, so an exact legacy/eForms binary partition is unavailable. Calendar
year and `cn-standard`/`can-standard` alone are not schema-generation evidence.

| Source generation evidence | Total = marker missing | BT-11 present | BT-11 missing | Identifier present | Identifier missing |
| --- | ---: | ---: | ---: | ---: | ---: |
| Explicit eForms SDK | 22,730 | 21,234 | 1,496 | 22,676 | 54 |
| Generation unresolved | 46,196 | 46,196 | 0 | 45,612 | 584 |

Year/generation detail: 2016–2022 are entirely unresolved (counts/completeness as
above); the transition and newer years are:

| Year / evidence | Total = marker missing | BT-11 present | BT-11 missing | Identifier present | Identifier missing |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2023 / explicit eForms | 1,603 | 1,381 | 222 | 1,603 | 0 |
| 2023 / unresolved | 7,199 | 7,199 | 0 | 7,123 | 76 |
| 2024 / explicit eForms | 6,912 | 6,466 | 446 | 6,885 | 27 |
| 2024 / unresolved | 11 | 11 | 0 | 0 | 11 |
| 2025 / explicit eForms | 7,624 | 7,174 | 450 | 7,612 | 12 |
| 2026 / explicit eForms | 6,591 | 6,213 | 378 | 6,576 | 15 |

Thus newer eForms do **not** provide the buyer marker reliably: they provide none
in this capture. No first defensible bounded production year can be identified.

## Cardinality and buyer association

Search OpenAPI describes separate scalar arrays, not a collection of buyer
objects with shared identity keys. No reviewed documentation guarantees positional
correspondence, null placeholders, uniqueness or complete per-buyer coverage.
**Do not zip arrays, even when their lengths happen to agree.**

XML has organisation technical IDs `OPT-200-Organization-Company` and buyer
references `OPT-300-Procedure-Buyer`. Those are not exposed as properties in the
reviewed Search OpenAPI, nor are `buyer-id`, `organisation-id` or
`BT-13720-Organization`. BT-13720 is documented as conveyed by XML structural
links, not a recoverable Search join. XML capability is not evidence that these
flattened results retain it. No extra source-native Search identity field was
found that resolves the association.

**Actual single-buyer notice count: unknown. Actual multi-buyer notice count:
unknown. Buyer-to-marker association: not established.** The following are
measured *value cardinalities*, explicitly not asserted buyer identity counts:

| Field / measurement | Missing or zero values | One value | More than one value | Maximum values |
| --- | ---: | ---: | ---: | ---: |
| buyer-person | 68,926 | 0 | 0 | 0 |
| buyer-name: maximum count within one language | 54 | 68,247 | 625 | 163 |
| buyer-name: sum across all languages | 54 | 67,665 | 1,207 | 1,464 |
| buyer-identifier | 638 | 44,717 | 23,571 | 324 |
| buyer-legal-type | 1,496 | 58,089 | 9,341 | 163 |

Multiple language versions are not multiple buyers; one name value is not proof
that no other buyer was omitted. Multiple identifiers can belong to one buyer.
**22,946** notices have one name value per language but multiple identifier values;
**8,761** have different maximum-per-language name and legal-type lengths (where
legal-type is a returned array). Neither equal nor unequal cardinality proves
legal identity or alignment. Research aggregates retain full histograms privately.

The requested single/multi breakdown can only be supplied as this transparent
name-value proxy; true identity-based breakdowns cannot be reconstructed:

| Name-value proxy, not buyer count | Total = marker missing | BT-11 present | BT-11 missing | Identifier present | Identifier missing |
| --- | ---: | ---: | ---: | ---: | ---: |
| One per language | 68,247 | 66,840 | 1,407 | 67,663 | 584 |
| Multiple within a language | 625 | 590 | 35 | 625 | 0 |
| No name values | 54 | 0 | 54 | 0 | 54 |

## Previously observed sole-trader diagnostics (private sample)

Revisited **six exact previously observed buyer labels**, taking earliest/latest
retained notice per label and deduplicating identical endpoints: **11 notices**.
This is a diagnostic sample, not a legal-status adjudication, name-based
classifier, whitelist or exhaustive count of sole traders. No additional labels
were screened by name pattern. All 11 have **missing BT-633**, `buyer-legal-type =
["8"]`, **one BT-501 value**, one buyer-name value per language, and no
customization ID/subtype. They therefore remain **unknown/excluded**, not
source-confirmed natural or juridical persons. Code `8` has no adopted current
BT-11 non-natural guarantee. Identifier presence would wrongly appear reassuring
if treated as legal-person proof.

Opaque private-ledger references below intentionally omit publication IDs, names,
identifier values, locations and titles. References are truncated hashes; they
are pseudonymous traceability aids, **not an anonymity guarantee**. Mapping and
hash inputs stay private.

| Internal reference | Year | Source type | Generation evidence | Marker / gate |
| --- | ---: | --- | --- | --- |
| 436fe62e1865aef2 | 2018 | can-standard | Unresolved | Missing / exclude unknown |
| 2af9b0630270d18d | 2017 | cn-standard | Unresolved | Missing / exclude unknown |
| f754260f11620a27 | 2023 | can-modif | Unresolved | Missing / exclude unknown |
| 0b9ef9de8d9b1933 | 2017 | cn-standard | Unresolved | Missing / exclude unknown |
| 59d906792a656ef0 | 2018 | can-standard | Unresolved | Missing / exclude unknown |
| b521b2cdcba1ff2d | 2020 | cn-standard | Unresolved | Missing / exclude unknown |
| f68efe02c0b64ed1 | 2022 | can-standard | Unresolved | Missing / exclude unknown |
| cf5ea0de85d995bd | 2018 | cn-standard | Unresolved | Missing / exclude unknown |
| ac075ba3d7938dc8 | 2019 | can-modif | Unresolved | Missing / exclude unknown |
| 83ed281aa0b3df1c | 2020 | cn-standard | Unresolved | Missing / exclude unknown |
| deb755b187d6dd60 | 2021 | can-standard | Unresolved | Missing / exclude unknown |

## Hypothetical gates — not adopted production policy

| Candidate | Required evidence | Eligible | Outcome |
| --- | --- | ---: | --- |
| A | Every buyer explicitly false, with deterministic identity/marker association and complete buyer coverage | **0** | No false markers; association also unproved. |
| B | A plus recognized institutional BT-11 | **0** | BT-11 cannot replace A or supply the missing join. |
| C | Superior documented source-native institutional discriminator | **0** | None established in reviewed fields/semantics; not a missing-as-false fallback. |

Strongest justified evaluation is fail-closed A with B only corroborating; C
does not exist as an evidenced implementation. Disjoint whole-notice accounting:

| Result | Notices |
| --- | ---: |
| Acquired | 68,926 |
| Eligible | **0** |
| Excluded explicit natural (true-only or mixed) | **0** |
| Excluded unknown status | **68,926** |
| Additional excluded ambiguous/multi-buyer (after unknown/explicit exclusions) | **0** |

The last zero is **not** proof there are no multi-buyer/ambiguous notices. All
already fail as unknown, including all 625 multi-name-value rows. No row is counted
twice. Any future true or mixed marker excludes the entire notice; any unknown
buyer also excludes the entire notice. Selectively stripping a buyer is not
approved. All-false arrays without completeness/association would still be
ambiguous, not eligible.

Acquired publication range: **2016-10-27–2026-10-28**. Earliest/latest *eligible*
publication: **not applicable**; eligible years: none; eligible count in every
year 2016–2026: **zero**. A useful many-thousands filtered corpus is not evidenced,
and limiting to newer years cannot restore it. These counts are not national
Slovak procurement coverage or a claim of historical availability before 2016.

## Retained output / title privacy review

Reviewed the existing normalization choice (Slovak, then English, then available
language) and a **bounded 110-title sample**, ten per publication year selected
by deterministic hashed-ID order, plus the **11 diagnostic titles** above. This
was a qualitative review of already captured values, not regex/NLP person
detection or an eligibility classifier. Private sample text and mapping remain
outside Git.

- **One of the 110 titles contains a personal name** as part of a school's
  commemorative institutional name (private reference `0be839dfd7f78630`). That is
  not itself evidence of a living-person disclosure or reason to drop all titles.
- The 11 diagnostic titles are generic goods/service descriptions and did not
  repeat those buyer labels. No contact email/phone, private residence or other
  direct personal detail was identified in these **121 reviewed title values**.
  This bounded finding is **not** a corpus-wide absence guarantee, across all
  titles or language variants.
- Titles are free text; especially newer eForms titles retain project-specific
  narrative. An institutional-buyer gate would not automatically establish title
  safety. Keep a separate output-content privacy review before any future
  promotion, without treating every title as unsafe or silently redacting it.
- `buyerNames` is the directly observed blocker. City/postcode/country describe
  procedure performance, not approved personal-address fields; linked to an
  individual buyer they may still reveal contextual/location information. IDs,
  dates, deadlines and source URLs are reference metadata but can link back to
  the person's public notice. Therefore the remedy is **whole-notice exclusion
  for unknown/natural/ambiguous buyers**, not declaring every other field safe
  after removing only buyerNames. No source details/contact/winner enrichment
  or production schema change is proposed.

## Validation and production freeze

Targeted acquisition/privacy/import tests cover strict booleans (including false
vs zero/string/null), missing/mixed/unknown whole-notice exclusions, refusal to
join equal-length arrays, multilingual name-count proxies, schema uncertainty,
ID/date drift, page hashes, request tokens, duplicates, totals, terminal
truncation, unexpected fields, minimal separate metadata profile and the existing
production-pause guard. Checkpoint results:

- `python -m pytest -q tests/test_acquire_procurement_notices.py tests/test_analyze_procurement_buyer_privacy.py tests/test_import_procurement_notices.py tests/test_generate_holidays.py`:
  **60 passed**.
- `python -m compileall scripts tests`: passed.
- `git diff --check` (including staged new files before commit): passed.
- All **14 production JSON byte hashes** equal both the original main baseline
  and the privacy-spike checkpoint baseline. Protected runtime/schema/freshness/
  version paths have no diff from `0ec6597`.
- Actual OpenAPI paths and components equal the pre-expansion baseline exactly:
  **39 GET operations** (root plus 38 `/v1` operations), unchanged operation IDs.
  Local procurement GET smoke returns metadata version `v1`.
- Committed non-content metadata manifest agrees with the fully verified private
  manifest, and every aggregate group has all markers missing.

Full milestone CI / full test suite / hosted CI are not required or claimed.

No procurement/calendar/source-catalogue JSON, runtime, routes, schemas, response
shapes, freshness constants, dependencies or operation IDs are changed. Holiday
tooling remains retained and unpromoted. **39 GET operations**, `/v1`, metadata
version `v1` and project `0.23.13-dev` remain unchanged. No push, PR, outreach, tag
or release. Any future broader source acquisition, privacy-policy change,
calendar-only promotion or research-only milestone closure needs the maintainer's
separate decision.
