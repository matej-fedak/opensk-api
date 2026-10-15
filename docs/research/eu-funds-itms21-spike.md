# 0.23.6 — EU Funds / ITMS21+ Source Spike

> Historical spike record. **0.23.7 now promotes the narrow title-free production
> project-reference slice** described in [`../eu-funds.md`](../eu-funds.md).
> Its full acquisition is 4,574 source / 4,561 included / 13 wholly excluded,
> not the historical 4,571 population or 100-row research sample below. Current
> runtime has two EU-funds routes and 39 GET operations. Production uses
> `contractedTotal` without an unsupported currency claim, omits implementation
> dates/titles, removes ambiguous CZ325 from the seed allowlist, and requires
> complete list manifests (not details). All “not implemented”/promotion gates
> below describe the **0.23.6** outcome; current contract/refresh evidence lives
> in the production guide. CC BY remains generic after the 2026-10-15 recheck.

Checked **2026-10-14**. Research and offline tooling only. **No public EU-funds endpoint or production EU-funds dataset is added.** `/v1`, `metadata.version == "v1"`, and the existing 37 GET operations remain unchanged.

## 1. Executive decision

**Milestone verdict: `GO_PRODUCTION_NEXT`. Storage verdict: `JSON_CONTINUE`.**

The next separately approved milestone can implement a small **reviewed-legal-entity projects only** ITMS21+ reference surface. Official anonymous JSON acquisition and project-specific catalogue CC BY evidence are verified. Projects with natural-person, unspecified, missing or unreviewed beneficiary forms are **excluded entirely**, not retained with a redacted identity: stable project identifiers and canonical source URLs would make such rows trivially re-linkable. This is not authorization to publish raw upstream payloads, personal identities, all ITMS21+ projects or an all-period database. Production still needs the explicit promotion gates in section 25.

Primary period: ITMS21+, **2021–2027**. ITMS2014+, **2014–2020**, is live but remains an independently licensed, differently modelled historical candidate. Do not combine the periods or mix this domain into TED procurement notices.

## 2. Official operator and source chain

- Portal: <https://portal.itms21.sk/>; its footer identifies **Ministerstvo investícií, regionálneho rozvoja a informatizácie SR (MIRRI SR)** as service operator. Observed portal build: `4.0.3 2026-09-30`.
- Official source entry: <https://portal.itms21.sk/opendata/>. Its client-loaded content is available as JSON at <https://api.itms21.sk/public/v1/textaplikacie/WTXSYS0030>.
- Production configuration: <https://api.itms21.sk/config/v1/config> returned HTTP 200 with `appEnvironment: "PROD"`.
- Support: `itms@datacentrum.sk`, linked user-support centre <https://helpdesk.datacentrum.sk/>. No correspondence was sent.

Portal HTML/JavaScript was inspected only to locate documentation and official API URLs; it is **not** the acquisition channel. Third-party reuse examples are context, never substitute permission or canonical data.

## 3. Integration manual

Official document page: <https://eurofondy.gov.sk/dokumenty-a-publikacie/metodicke-dokumenty/dokumenty-itms21/>.

Manual: <https://eurofondy.gov.sk/wp-content/uploads/2025/06/Final_ManualOpenDataAPI_ITMS21.docx>, **version 1.0, issued 25.6.2025**, 738,067 bytes. SHA-256:

`8e98b7fa5a8f6a214d0c220fa24c023da126dcf0d1777d0571f214d1bdc773ac`

Citations below use manual sections plus line ranges in the local paragraph-only UTF-8 extraction (`manual_clean.txt`, 14,287 lines); the DOCX URL and section are the portable reference. Raw documents/captures stay outside Git.

Manual §1.1 (L154–157): “Verejné Open Data API ITMS21+ poskytujú možnosť získať verejne dostupné údaje … v podobe vhodnej na ďalšie strojové spracovanie.” “Informácie sú zverejňované vo formáte JSON … REST prístupom.” No licence is stated in the manual.

## 4. API base, access and specification mismatch

Verified operational root: **`https://api.itms21.sk/public/v1/`**, anonymous GET/JSON. The authenticated write **Open API** described by `WTXSYS0032` is separate and out of scope.

Manual §4 (L14279–14287) instead advertises `https://api.itms21.sk/v1/` and `/v1/swagger.json`, with confusing TLS client-certificate wording. Anonymous production GETs demonstrably work; do not infer that credentials or client certificates are needed for those observed services. Probed Swagger/UI paths were blocked by the F5 WAF or returned infrastructure HTML; a working ITMS21+ OpenAPI document was **not** retrieved. Treat the manual/live discrepancy as an erratum, not permission to use private APIs.

## 5. Entity/service inventory

Manual §2.1 and §3 describe projects, programmes/priorities/objectives, calls/planned calls, subjects, ŽoNFP applications, ŽoP payment requests, activities, indicators, budget/intensity components, accounting documents, procurement and code lists.

| Candidate | Verified service / shape | Initial decision |
| --- | --- | --- |
| Projects | `/projekt`, `/projekt/id/{id}`, documented code lookup | Primary slice |
| Programme and call | Embedded in project; `/program`, `/vyzva` | Minimal references only |
| Beneficiary | Embedded `prijimatel` subject with legal form | Only positively reviewed legal-entity beneficiaries; all other projects excluded |
| ŽoNFP / ŽoP | Separate application/payment processes | Defer; not synonymous with projects or paid totals |
| Suppliers / partners / accounting / VO | Rich identity and relationship surface | Exclude initially |
| Code lists / legal forms / NUTS | `/ciselniky`, `/pravnaforma`, `/nuts` | Research support, no new public code-list service |
| Irregularities / receivables | Manual chapters marked “pripravuje sa v ďalších verziách” | `OUT_OF_INITIAL_SCOPE` regardless of future availability |

Presence in documentation does not prove a live endpoint exists. The portal's broad description mentions planned domains as well as delivered ones.

## 6. Licence gate — exact project-specific evidence

Checked firsthand **2026-10-14** through <https://data.slovensko.sk/api/sparql> (POST `query`, `Accept: application/sparql-results+json`). This is the national catalogue's machine-readable rights declaration by the publisher, not a third-party mirror.

- Dataset **“Zoznam projektov ITMS21+”**: <https://data.gov.sk/set/3dd34ab69156cd6dcdd6454f81727c88>.
- Publisher: `https://data.gov.sk/id/legal-subject/50349287` (**MIRRI SR**).
- Distribution: `https://data.gov.sk/set/3dd34ab69156cd6dcdd6454f81727c88/resource/e2564ec083481e0711882ef79999b35e`.
- `dcat:accessURL`: **`https://api.itms21.sk/public/v1/projekt`**.
- Terms node: distribution URI plus `/terms-of-use`.

Exact RDF values (`leg:` = `https://data.gov.sk/def/ontology/legislation/`):

```text
leg:authorsWorkType                      http://publications.europa.eu/resource/authority/licence/CC_BY
leg:originalDatabaseType                 http://publications.europa.eu/resource/authority/licence/CC_BY
leg:databaseProtectedBySpecialRightsType http://publications.europa.eu/resource/authority/licence/CC_BY
leg:personalDataContainmentType          https://data.gov.sk/def/personal-data-occurence-type/2
```

Reproducible query (then query all predicates of the returned terms URI):

```sparql
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX leg: <https://data.gov.sk/def/ontology/legislation/>
SELECT ?title ?publisher ?access ?terms ?p ?o WHERE {
  <https://data.gov.sk/set/3dd34ab69156cd6dcdd6454f81727c88>
    dct:title ?title; dct:publisher ?publisher; dcat:distribution ?distribution.
  ?distribution dcat:accessURL ?access; leg:termsOfUse ?terms.
  ?terms ?p ?o.
}
```

The retained graph declares **CC BY**, not an explicit version-specific CC BY 4.0 URL. Do not silently upgrade it to “CC BY 4.0 verified”. Keep the catalogue terms link and attribution; resolve the precise version link when packaging a production notice. The code `/2` is not an independently verified anonymisation guarantee: live subjects include personal identities and home-address fields.

## 7. Reuse conditions and legal context

Licence evidence supports copying/storing, transforming, redistribution and commercial reuse, with attribution and modification disclosure. All three rights layers are expressly covered; access alone was **not** used to infer permission.

Proposed attribution: **“Source: MIRRI SR / ITMS21+ OpenData API; CC BY per the national catalogue. OpenSK transformed and minimized the source data; not an official representation.”** Link the source and project-specific terms.

Portal text `WTXSYS0030` invites “vzniku aplikácií tretích strán postavených na spracovávaní sprístupnených informácií/dát”. MIRRI's <https://mirri.gov.sk/sekcie/informatizacia/o-sekciach/centralna-datova-kancelaria/otvorene-udaje/> says reuse is available “v rozsahu priloženej licencie použitia”. These corroborate, not replace, the project licence.

<https://eur-lex.europa.eu/eli/reg/2021/1060/oj> **Article 49(3)–(4)** requires lists of supported operations in open, machine-readable formats allowing data to be “sorted, searched, extracted, compared and reused”. Annex IX concerns communication-material rights, **not** the list-of-operations schema. Natural-person name removal after two years is a source publication rule, not authority for OpenSK to retain those identities indefinitely.

CC BY does not supply an independent GDPR legal basis. The source GDPR notice <https://api.itms21.sk/public/v1/gdpr> names MIRRI and statutory processing under Act 121/2022. Its statement about no third-country transfers describes **MIRRI's processing**; it is not an established licence restriction on all downstream hosting. No such hosting restriction is invented here.

## 8. Live sample and measured coverage

All counts are upstream response `size` values observed on **2026-10-14**, not audited exhaustive totals or proof of all EU spending in Slovakia.

| GET under `/public/v1/` | Status | Observation |
| --- | --- | --- |
| `projekt?offset=0&limit=1` | 200 | 4,571 projects; 16,174-byte response |
| `projekt?offset=0&limit=100` | 200 | 100 rows, size 4,571; 2,799,437 bytes |
| `projekt/id/25682` | 200 | 75,118-byte rich detail |
| `projekt/id/21730` | 200 | 56,405-byte comparison detail |
| `subjekt?offset=0&limit=100` | 200 | 12,955 subjects; 100 sampled |
| `zonfp?offset=0&limit=1` | 200 | 9,075 applications |
| `program?limit=0` / `vyzva?limit=0` | 200 | 7 programmes / 184 calls |
| `pravnaforma` | 200 | 482 legal-form entries |
| `projekt?vrealizacii=true&limit=1` | 200 | size 4,121; filter works |

A `/nuts` count of 129,672 was observed with no result rows in that capture; its scope was not established. Do not mislabel that number as Slovakia's municipalities or current NUTS regions.

## 9. Project schema and identifier strategy

Manual §2.1.1 (L310–328): **“ID a Kódy (ak existujú) sú nemenné, a je možné si ich zapamätať.”** Project lists are documented ascending by ID (§3.8.1, L3757–3758).

Use **`projectCode` = `kod`** as candidate public key; retain the upstream numeric ID and canonical detail URL for traceability. An embedded programme's `kodCCI` identifies the programme, **not** the project. Do not use beneficiary IČO as a project identifier. Codes need period/source namespacing if historical sources are introduced later; no cross-period uniqueness is claimed.

List JSON envelope: `{offset, limit, size, results}`. Rows contain a project, call/programme links, beneficiary, locations, state flags, dates and total contracted sum. Details add NFP/provided amounts and much deeper activity/description/budget/relationship data. The prototype accepts list pages plus optional matching detail files, rejects duplicate codes/IDs and detail/list identity mismatches.

## 10. Monetary semantics

Manual project detail model §3.8.2 (L4137–4340):

| Upstream field | Exact source meaning | Candidate output / decision |
| --- | --- | --- |
| `celkovaZazmluvnenaSuma` | “Celková zazmluvnená suma” | `contractedTotalEur` (list) |
| `zazmluvnenaSumaNfp` | “Zazmluvnená suma NFP” | `contractedNfpEur` (detail) |
| `poskytnuteProstriedky` | “Poskytnuté finančné prostriedky prijímateľovi (NFP)” | `providedNfpEur` (detail); not certified expenditure or an independently reconciled cash ledger |
| `celkovaZazmluvnenaSumaPovodna` | “Pôvodná celková zazmluvnená suma” | Defer original-versus-amended history |
| `financnyPlan[].suma` | Amount by funding-source link | Defer: do not invent a universal EU/state/private split |
| Programme `sumaEu/sumaSr/sumaSpolu` | Programme-level sums | Never relabel as project money |
| ŽoNFP requested amounts | Application process | Not approved/contracted project amounts; defer |

The first three fields are not interchangeable; equal values in one project do not establish synonymy. No “funding received = total project cost”, requested/approved conflation, aggregate paid percentage or balance arithmetic is implemented.

Live JSON carries long BigDecimal number lexemes. Parse with `parse_float=Decimal`, validate finite/nonnegative amounts, format without Decimal-context rounding, and emit **decimal strings**. No binary floating-point money or forced two-decimal rounding.

## 11. States and dates

`stav` is an optional Slovak display string, not a verified stable English enum. In 100 rows: 95 “Zmluva uzavretá”, four “Projekt riadne ukončený (K)”, one “Zmluva uzavretá - pozastavenie realizácie projektu”. This is a sample, not the full vocabulary.

Keep `label`, `inImplementation` (`vrealizacii`) and `completed` (`ukonceny`). Do not fabricate a complete status taxonomy from those three strings. Pause/extraordinary termination/exclusion flags and cancellation semantics require separate review before expansion.

Live `createdAt`/`updatedAt` and implementation date fields are epoch **milliseconds**, despite inconsistent manual type annotations. Preserve implementation timestamps as UTC ISO **instants** (`...StartAt`/`...EndAt`), not UTC-truncated calendar dates: source local-midnight values can become the previous day in UTC. Slovak calendar-date interpretation remains a production-contract decision.

## 12. Geography and joins

Manual `miestoRealizacie`: “Miesta realizácie - číselník NUTS”. Sample detail `miestoRealizacieFull` has `nuts2`, `nuts3`, `lokalita`, `stat`; no municipality identifier was established in that sample. **SK010 is NUTS3**, SK01 is NUTS2.

All eight distinct location codes in the 100-project capture match the eight local `data/regions.json` codes: **8/8 distinct code joins**, no name matching. This is not a nationwide municipality-level match-rate audit. Multiple locations must remain arrays; never choose the beneficiary's seat as implementation location or allocate a project's full amount to every region and then sum it.

District/municipality joins are not promised. Keep NUTS references self-contained, preserve foreign-location uncertainty, and do not make EU-funds coverage depend on PortalVS permissions or RPO completeness.

## 13. Privacy field classification

| Field family | Classification | Initial treatment |
| --- | --- | --- |
| Codes, canonical source URLs, money, locations, state/timestamps | Linkable project facts, not anonymous merely because names are absent | Emit only for positively eligible legal-entity projects |
| Beneficiary name/IČO/legal form | Identity; personal for sole traders | Positive reviewed legal-entity gate; otherwise exclude entire project |
| Project title | Potential identifying text even without beneficiary name | Unsafe project excluded entirely; legal-entity title review still required before production |
| Subject street/home address, DIČ, IČ DPH | High-risk personal identifiers | Always exclude |
| Partners, suppliers, accounting-document identities | Additional personal/relationship surface | Always exclude |
| `popis*`, `ucel`, capacity descriptions, VO free text | Arbitrary HTML/free text, possible names/contacts | Always exclude initially |
| Evaluators, contacts, email/phone | Not found in examined subject/project models; absence not guaranteed across future schemas | Never pass through unknown fields |
| Irregularities/debts | Allegations and sensitive financial/reputational facts | `OUT_OF_INITIAL_SCOPE` |

**IČO does not mean legal person.** Five of the first 100 subject rows were natural persons, including sole traders with IČO and private citizens without IČO. No real natural-person names, tax IDs or home addresses are retained in repository fixtures or this report.

## 14. Legal-form gate and whole-project exclusion

Privacy verdict: **`REVIEWED_LEGAL_ENTITY_PROJECTS_ONLY`**. Whole-project exclusion is necessary; there is **no linkable project-level fallback** for unsafe beneficiaries. A name/title-redacted row with `projectCode`, `sourceId` or `sourceUrl` still exposes a trivial path to the underlying person.

The 482-entry catalogue uses `pravnaForma.kod`; `kodZdroj` collides across countries. The manually identified natural/person-adjacent set is:

```text
100900000 1009001 100901
1009100 1009101 1009102 1009103 1009104 1009105
1009106 1009107 1009108 1009109 1009110
1009422 1009752
1009CZ101 1009CZ102 1009CZ104 1009CZ105
1009CZ106 1009CZ107 1009CZ108 1009CZ425
```

These 24 codes cover citizens, sole traders/farmers/liberal professions, foreign natural persons and the cautiously excluded association without legal personality. `1009995` (unspecified form) is separately unsafe. This is an inspected catalogue snapshot, **not** a proof that all other/future codes are legal entities.

The prototype positively allows only **28 reviewed legal-entity codes seen in the project sample** (`LEGAL_ENTITY_FORMS` in the script). Missing, unknown, natural-person and unspecified forms **exclude the entire project before output construction**, including all IDs, URLs, money, locations, state/timestamps and title. No fuzzy/name-based classification. Re-review new forms explicitly; absence from the natural-person denylist is never approval.

Exclusions are aggregate counters only: `excludedNaturalPersonProjects` and `excludedUnreviewedBeneficiaryProjects` (the latter includes unspecified/missing forms). `includedProjects` counts only eligible rows. Generated preview metadata contains no excluded-row code list, raw capture filenames or excluded-detail URLs. Complete acquisition provenance stays in the **local diagnostic report**, not the public-style candidate payload.

A supplied detail for an excluded project is recognized by matching code and ID but is not enriched, emitted or listed in preview source metadata. Identity mismatch or a detail with no corresponding list row still fails consistency validation; the mere presence of an excluded project's matching detail does not fail or reinstate it. If a richer detail explicitly supplies an unsafe/unreviewed beneficiary, it also excludes the project even when the earlier list row passed. Missing/non-object beneficiary blocks fail closed as exclusions. An all-excluded valid input yields an empty `projects` array and honest counters, not a privacy-unsafe fallback.

## 15. Privacy red-team answers

1. Natural-person beneficiaries possible? Subject participation is verified; two sampled natural persons' project queries returned zero. That does not prove absence across all projects.
2. SZČO possible? Yes, natural-person legal forms and IČO-bearing subjects observed.
3. IČO sufficient? **No**.
4. Evaluator names? Not found in examined public models; excluded if introduced.
5. Contact persons? Not found in examined public models; excluded.
6. Personal email/phone? Not observed in examined models; never allowed through.
7. Home addresses? Yes in subject payloads; excluded even for legal entities.
8. Natural-person suppliers? Possible; supplier links lack the discriminator, so exclude all supplier identities.
9. Free-text risk? Yes; descriptions are excluded. Unsafe beneficiary projects, including titles, are wholly excluded; legal-entity titles still need production review.
10. Irregularities sensitivity? High; no initial import even if an endpoint appears later.
11. Allowlist sufficient? A positive reviewed-entity gate plus whole-project exclusion closes the identified re-linkability failure. Title/schema review remains a production gate; this is **not** a blanket guarantee for upstream data.
12. Project-level fallback viable? **No for unsafe/unreviewed beneficiaries.** Code/ID/canonical URL makes a redacted row trivially dereferenceable. No RPO join is needed to exclude it fail-closed.

## 16. Pagination and incremental semantics

Manual §2.1.1 (L310–328): `linkApi` switches link/full objects; `minId` returns `ID > minId`; `minId` plus `limit` provides paging; `limit=-1` is documented unbounded. Live `offset`/`limit` works. Sort/filters are per-entity, not automatically universal.

`modifiedSince` is documented as Unix timestamp, only detecting changes on the root entity, not nested collections (L319–320). Tested project requests:

- `modifiedSince=2026-01-01` → 404.
- `modifiedSince=1767225600` (epoch seconds) → 200, full size 4,571.
- `modifiedSince=1893456000` (2030, epoch seconds) → 200, full size 4,571.

**These seconds-form probes did not filter.** Because observed entity timestamps are milliseconds, a unit mismatch remains a plausible explanation; do not overclaim the parameter is broken for every valid unit/endpoint. No trusted incremental mechanism is established. The implementation does not rely on it.

Manual §1.2 (L162–163) already recommends re-listing services, fetching details and comparing attributes because some changes cannot be caught by `modifiedSince`.

## 17. Offline snapshot and refresh strategy

Future maintainer acquisition: paced official JSON requests, bounded pages, explicit URL/status/retrieval time/SHA-256 manifest, then offline projection. Raw captures remain private/local and short-lived; never commit full upstream subjects.

Re-list all project state coverage, compare IDs/codes and content, re-fetch required details, detect removed/changed records, and publish an atomic reviewed snapshot. Root `updatedAt` can help triage but **cannot** prove nested content is unchanged. Periodic full detail reconciliation remains necessary. Disappearance may be deletion or loss of publishability, not merely a transient failure (§1.3, L169–173).

Preview imports accept partial list captures deliberately; `size=4571` with 100 rows does **not** make the result complete. `sourcePopulationObserved` records the observed source total; `inputRows` counts captured rows; `includedProjects` counts only the approved beneficiary subset. Reject inconsistent page totals and duplicate IDs/codes, including duplicates among excluded rows. This prototype is not an acquisition crawler, scheduled refresh job or production atomic writer.

## 18. HTTP behavior and upstream load

Manual error model (L378–385): 200 / 400 / 404 / 500. Live malformed timestamp produced 404, not necessarily the documented 400. Successful captures have JSON/HSTS and F5 cookies; no ETag/Last-Modified/Cache-Control or compression was observed in those samples. Infrastructure can return HTML even with 200; validate content/schema, not status alone.

No numeric rate limit was found. This is **not** unlimited-load authorization. Research used small requests with approximately 1.5–2-second gaps; any acquisition must handle 429/5xx, bounded backoff, stop on WAF challenges and avoid retry storms. Do not bypass the WAF. XLSX export routes are documented but were not chosen as canonical for this JSON spike.

## 19. Volume measurements

| Artifact | Measured bytes | SHA-256 |
| --- | ---: | --- |
| 100-project JSON list | 2,799,437 | `b729b5f0f5a8f4c4d96fa032a404d54843c3dc8075475ffc541b69d8928ac4df` |
| Project 25682 detail | 75,118 | `027b78d1bf691007d8c01eadcc71441ebf4e937338cd3613a9fca78dfb5c397c` |
| Project 21730 detail | 56,405 | `162c21c854265a130def65aade8d2c20228eb5280b37d729ba36c689b7091c99` |

Raw 100-row page extrapolation: **about 128 MB** for 4,571 rows (wire JSON), not a downloaded full snapshot. A separate re-serialization estimate was ~135 MB; do not confuse that estimate with wire bytes. Detail expansion plausibly adds hundreds of MB and thousands of requests; those are estimates, not measured full acquisition.

With the corrected exclusion policy, the 100-project capture plus two matching details yields **100 eligible projects, 0 exclusions**, **152,272 bytes pretty / 103,791 compact**. This does not establish eligibility of all **4,571 observed source projects**. A roughly 7.0 MB pretty / 4.8 MB compact all-source-size extrapolation is a sizing scenario, **not** a complete candidate coverage claim. Five natural-person subjects in the distinct subject sample must not be described as five natural-person project beneficiaries.

## 20. Storage verdict

**`JSON_CONTINUE`.** A few thousand narrowly projected projects at an estimated few MB does not justify changing the runtime architecture. Raw upstream payload bloat is an **offline acquisition** concern, not a reason to serve that bloat or add SQLite. No SQLite, DB or Redis is implemented.

Projection timing/memory on a 100-row sample and runtime parse of the resulting preview are diagnostic only; a full normalized production snapshot is not yet acquired. Promotion should measure cold parse, retained/peak heap, filtered lookup cost and cold-start impact. Revisit storage if multi-period/deep child records materially grow those measured costs; do not trigger a datastore change just because the raw list is large.

Earlier local diagnostic (Python 3.14, one run, tracemalloc enabled, pre-review manifest shape): 100-row offline projection plus two details ~249 ms, ~17.7 MB peak / 0.54 MB retained traced heap; parsing that 152,498-byte preview ~4.0 ms, 0.72 MB peak / 0.42 MB retained. Those same 100 projects pass the stricter eligibility policy. These are Python allocations, not process RSS or production-instance benchmarks; full-snapshot costs are not claimed as measured.

## 21. Importer prototype and allowlist

`scripts/import_itms21_projects.py` has **no network code** and no production-write mode. Default dry-run; explicit preview writes only `.json` beneath gitignored `data/generated/`, with resolved-path escape protection. Inputs are local UTF-8 JSON plus official URL provenance; money uses Decimal; source file hashes are reported.

Output **only for positively reviewed legal-entity projects**: project code/source ID, reviewed project title, source state label/flags, programme/call codes and names, reviewed beneficiary name/IČO/form, NUTS location refs, contracted total, optional matching-detail NFP/provided amounts and timestamp instants, source updated instant and detail URL. Unsafe/unreviewed projects produce no output record at all. Unknown fields are never passed through; partial/detail coverage is not filled with zero amounts.

Example using already downloaded local files (paths illustrative; this command does not download):

```powershell
python scripts/import_itms21_projects.py --projects "C:\captures\projects.json=https://api.itms21.sk/public/v1/projekt?offset=0&limit=100" --detail "C:\captures\25682.json=https://api.itms21.sk/public/v1/projekt/id/25682" --dry-run
```

Add `--write-preview` instead of `--dry-run` only after reviewing the report. A supplied `--retrieved-at` is maintainer metadata, not independent evidence of capture time. Full input paths/URLs and per-detail acquisition metadata remain in the local stdout report. Preview manifests omit local paths/query filters and excluded-detail entries; excluded projects cannot leak back through their manifest URLs or filenames.

## 22. Candidate public contract — not implemented

A later project-reference service is limited to **positively reviewed legal-entity beneficiary projects**. It must explain source population versus acquired/eligible coverage, whole-project privacy exclusions, source snapshot date and differing monetary meanings. It must never expose an unsafe project's identifiers/URLs as a redacted fallback. “Complete ITMS21+ projects” is not justified; “complete relative to the approved legal-entity projection” would require measured full acquisition plus eligibility coverage.

Route naming, models, pagination, cache/freshness semantics and status vocabulary belong to that future milestone. **No proposed path is advertised as an available route.** No national procurement coverage claim and no join to `/v1/procurement-notices` (TED-based and independently scoped).

## 23. ITMS2014+ historical comparison

Verified live: <https://www.itms2014.sk/> and <https://www.itms2014.sk/open-data>. <https://opendata.itms2014.sk/> redirects to working `/swagger/`; <https://opendata.itms2014.sk/v2/swagger.json> returned HTTP 200, approximately 434 KB, 50 paths.

ITMS2014+ v2 uses plural/state-bucket routes such as `/projekty/vrealizacii`, `/projekty/ukoncene`, application/payment-state lists and irregularity/receivable services. This differs from ITMS21+'s singular project route, embedded graph and currently undelivered irregularity chapters. Track B found CC0 catalogue declarations for historical distributions; **do not inherit those terms into ITMS21+** or extrapolate one period's schema into the other.

Historical extension must retain distinct source/period/license provenance and independently establish mapping/volume/privacy. No ITMS2014+ records or normalization are shipped in this milestone.

## 24. Delegated research and lead reconciliation

Four independent research tracks were launched: **A** source/API/acquisition and historical operations; **B** licence/reuse; **C** schema/money/product; **D** privacy red-team. C and its retry timed out, but left captures and analysis notes; the lead completed C from those artifacts. D's retry delivered the privacy report. Reports/captures remain in the local research temp directory, not runtime/Git.

Reconciliation corrections: licence proof is the **project-specific publisher graph**, not merely an unrelated catalogue entry; CC BY version was not explicit; `/2` is not proof of anonymisation; source GDPR transfer statements are not downstream licence restrictions; `modifiedSince` observations are unit-limited; SK010 is NUTS3; wire versus reserialized sizes differ; unknown forms fail closed; exact instants avoid UTC date loss; Decimal normalization must not round. PR review additionally rejected the earlier name/title-redaction fallback: IDs/URLs remain linkable, so unsafe projects and their detail manifests are now excluded entirely. Specialist recommendations were reviewed, not copied as authority.

## 25. Production gates and remaining risks

Before a separately approved promotion:

1. Retain/recheck this exact project catalogue grant and resolve the version-specific licence link for public notices; attribute MIRRI, disclose transformation, no endorsement.
2. Acquire consistent source coverage and matching-detail scope; measure approved legal-entity coverage separately from the source population and distinguish partial from complete.
3. Refresh/review the positive legal-form allowlist; natural-person, sole-trader, unspecified, missing and unreviewed forms exclude entire projects and identifiers/URLs, including any matching details. Review title text even for legal-entity projects; no free-text/contact/address/supplier/partner expansion by default.
4. Finalize monetary/currency and timestamp/calendar semantics; no requested/contracted/provided conflation.
5. Implement offline refresh/correction/removal review and validate nested changes; never rely solely on the tested seconds-form `modifiedSince`.
6. Measure the full **normalized** dataset's JSON memory/latency and join/filter costs before storage reassessment.
7. Approve runtime schema/coverage/cache/error contracts, source notices and offline fixtures; add no runtime upstream dependency.

No source correspondence is needed to continue research; optional clarification may reduce version/rate-limit uncertainty but was **not sent**. PortalVS and elections/outreach compliance states are unchanged. Existing platform-wide public-promotion restrictions remain independent of this source verdict.

## 26. Validation and evidence retention

Offline tests cover reviewed-entity inclusion, entire-project exclusion for all unsafe/unreviewed categories, absence of excluded IDs/URLs/title/facts anywhere in preview JSON, safe handling of supplied excluded details, honest counters, forbidden-field non-passthrough, exact decimals, timestamp conversion, duplicate/schema errors, deterministic records, source provenance, dry-run and generated-only path guards. Scope tests prohibit production EU-funds data/routes and preserve 37 GET operations plus `/v1` metadata.

Required final gates: dataset validation, referential integrity, full pytest, compileall, `git diff --check` and local smoke. No raw manual, upstream personal data, API capture or generated preview is committed. Source evidence is retained above as exact URLs/wording/date plus hashes; local raw-artifact retention is not a repository availability guarantee.

Initial pre-review verification: 519 tests, 0 dataset errors / 51 compliance warnings and 39/39 smoke checks passed. **PR #33 follow-up: 542 tests passed; 0 dataset errors / 44 warnings; referential integrity, compileall and whitespace checks passed; local smoke 39/39 passed.** The bank warnings disappeared because the actual NBS reply resolves reuse, not because warnings were suppressed. Bank file SHA-256 and bank endpoint JSON match the pre-follow-up baseline; `BANKS_LAST_UPDATED=2026-05-18` and `PROJECT_VERSION=0.23.6` remain unchanged. The real-capture corrected dry-run includes 100 eligible projects/two details, with zero exclusions in that sample; generated output remains ignored. The curated catalogue has 20 entries, without a data route.

## 27. Final recommendation and next milestone

Proceed only with a **reviewed-legal-entity-projects-only candidate** in a separately approved promotion, not all-source coverage or a generic EU-funds framework. Unsafe/unreviewed beneficiaries exclude the whole project because stable codes and source URLs trivially re-link name-redacted records. Keep ITMS2014+ historical extension, ŽoNFP/ŽoP, suppliers/partners, procurement fusion, irregularities/debts, free-text descriptions and automated acquisition deferred.

Final milestone verdict: **`GO_PRODUCTION_NEXT`**. Final storage verdict: **`JSON_CONTINUE`**. This branch delivers research, privacy-aware offline preview tooling and a research source catalogue entry only; it does not promote EU-funds data to production or change PortalVS/elections permissions.
