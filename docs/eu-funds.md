# ITMS21+ project references — 0.23.7

## Scope and attribution

Source: **MIRRI SR / ITMS21+ OpenData API**, 2021–2027 programming period.
OpenSK transformed and privacy-minimized the source into project references;
this is **not an official representation**. Manual snapshots can lag upstream.
Public coverage is **partial**, not all EU funds in Slovakia: no ITMS2014+,
privacy-excluded projects, titles, payments, procurement or irregularity/debt
surface. No runtime network, database, scheduled acquisition or company join.

Licence: **CC BY, as declared by the Slovak national open-data catalogue
(version not separately identified)**. MIT applies to code, not source data.
Attribute MIRRI SR / ITMS21+, link the source/catalogue and disclose OpenSK's
normalization, field renaming and privacy minimization when reusing this slice.

Rechecked 2026-10-15 via POST to <https://data.slovensko.sk/api/sparql>, using
the exact project-specific query retained in
[`research/eu-funds-itms21-spike.md`](research/eu-funds-itms21-spike.md), §6:

- Dataset: <https://data.gov.sk/set/3dd34ab69156cd6dcdd6454f81727c88>
- Publisher: <https://data.gov.sk/id/legal-subject/50349287> (MIRRI SR).
- Distribution access URL: <https://api.itms21.sk/public/v1/projekt>.
- Attached terms node:
  <https://data.gov.sk/set/3dd34ab69156cd6dcdd6454f81727c88/resource/e2564ec083481e0711882ef79999b35e/terms-of-use>.
- `authorsWorkType`, `originalDatabaseType`, `databaseProtectedBySpecialRightsType` all
  remain `http://publications.europa.eu/resource/authority/licence/CC_BY`.
  No added restriction was present on the queried terms node. No authoritative
  version-specific licence was established: **do not substitute CC BY 4.0**.

## Acquisition and coverage

Successful acquisition window: **2026-10-15T11:37:24Z–11:42:27Z**.
Canonical collection: `https://api.itms21.sk/public/v1/projekt`.
All **4,574 source rows** acquired in **19 pages** (limit 250, final page 74),
95,271,314 response bytes. Contiguous offsets, consistent `size`, exact row
counts, unique IDs/codes and byte-identical first-page boundary recheck passed.
Two earlier attempts were discarded when size/order changed; none was promoted.
No project detail requests were made for this acquisition.

Non-personal manifest: [`research/eu-funds-acquisition-manifest.json`](research/eu-funds-acquisition-manifest.json).
It contains exact list URLs, retrieval timestamps, byte sizes and SHA-256 for
each page, never source rows or excluded identifiers. Canonical manifest hash:

`93b104884e9405581a775762e0af2fab1c804c0954d575eca3c35bd55801a30f`

Hash rule: SHA-256 of UTF-8 JSON of the manifest **without** `manifestSha256`,
with sorted keys, `ensure_ascii=False`, separators `(',', ':')`.
Raw pages stay in maintainer-selected temporary storage **outside Git**.
Hashes establish integrity/reproducibility, not a server signature or an
upstream transactional snapshot. The API offers no snapshot token: consistent
page totals/identities plus a first-page recheck cannot prove that every nested
object was unchanged throughout the five-minute window. Freshness is the
materialized acquisition, not an asserted simultaneous upstream transaction.

| Population | Projects |
| --- | ---: |
| Source collection fully acquired | 4,574 |
| Privacy-approved public production | 4,561 |
| Excluded natural persons / sole traders | 3 |
| Excluded unspecified | 4 |
| Excluded ambiguous | 6 |
| Excluded missing / newly unreviewed | 0 |

`completeAcquisition: true` describes this collection acquisition only, **not**
all Slovak funds, historical periods, or universal public project eligibility.

## Positive legal-form review

All **46 observed forms** reviewed; **40 approved**. Match `pravnaForma.kod`,
not country-colliding `kodZdroj`; an IČO is **not** eligibility evidence.
Exact approved source labels are pinned in `services/eu_funds_policy.py` and
schema-validated. Unknown/missing forms fail closed. `APPROVED_LEGAL_ENTITY`
is the sole inclusion decision; every other decision removes the **entire**
project before constructing output. No excluded code, source ID/URL, status,
amount, location or timestamp survives in public JSON or error distinctions.

The live `/pravnaforma?offset=0&limit=250` and `offset=250&limit=250` catalogue
was rechecked (482 entries); all 40 approved code/label pairs matched.
Page hashes: `288982b80d2835312b9ec1088e8f20045550cfed8151c89c43edd2c0ff671880`
and `8845aaf20fb32e580780cbe95101f404fba153980cc63f39f6fe7b923915473d`.

Newly approved versus the research seed: SK `1009111`, `1009112`, `1009113`,
`1009117`, `1009119`, `1009123`, `1009125`, `1009205`, `1009301`, `1009333`,
`1009741`; CZ `1009CZ301`, `1009CZ706`. These denote companies/cooperatives,
foundations/nonprofit legal persons, state enterprises, statutory public
research/professional bodies or registered associations—not individual traders.
Research seed `1009CZ325` was **removed**: an organizational state unit is not
established as an independent legal person. `Fondy`, other-government and
branch-association categories remain ambiguous in this review, even where a
specific member might independently qualify after separate evidence.

| Code | Count | Official source label | Decision |
| --- | ---: | --- | --- |
| 100904 | 4 | GmbH | APPROVED_LEGAL_ENTITY |
| 100906 | 3 | Verein | APPROVED_LEGAL_ENTITY |
| 100909 | 1 | Gebietskörperschaft - Gemeinde | APPROVED_LEGAL_ENTITY |
| 100910 | 2 | Körperschaft öffentlichen Rechts | APPROVED_LEGAL_ENTITY |
| 1009101 | 3 | Podnikateľ-fyzická osoba-nezapísaný v obchodnom registri | EXCLUDE_NATURAL_PERSON |
| 1009111 | 3 | Verejná obchodná spoločnosť | APPROVED_LEGAL_ENTITY |
| 1009112 | 206 | Spoločnosť s ručením obmedzeným | APPROVED_LEGAL_ENTITY |
| 1009113 | 2 | Komanditná spoločnosť | APPROVED_LEGAL_ENTITY |
| 1009117 | 2 | Nadácia | APPROVED_LEGAL_ENTITY |
| 1009119 | 42 | Nezisková organizácia | APPROVED_LEGAL_ENTITY |
| 1009120 | 91 | Nezisková organizácia poskytujúca všeobecne prospešné služby | APPROVED_LEGAL_ENTITY |
| 1009121 | 195 | Akciová spoločnosť | APPROVED_LEGAL_ENTITY |
| 1009123 | 1 | Európska spoločnosť | APPROVED_LEGAL_ENTITY |
| 1009125 | 3 | Jednoduchá spoločnosť na akcie | APPROVED_LEGAL_ENTITY |
| 100913 | 2 | Juristische Person des öffentlichen Rechts | APPROVED_LEGAL_ENTITY |
| 100914 | 1 | Anstalt des öffentlichen Rechts | APPROVED_LEGAL_ENTITY |
| 1009205 | 2 | Družstvo | APPROVED_LEGAL_ENTITY |
| 1009301 | 25 | Štátny podnik | APPROVED_LEGAL_ENTITY |
| 1009321 | 356 | Rozpočtová organizácia | APPROVED_LEGAL_ENTITY |
| 1009331 | 165 | Príspevková organizácia | APPROVED_LEGAL_ENTITY |
| 1009333 | 5 | Verejná výskumná inštitúcia | APPROVED_LEGAL_ENTITY |
| 1009381 | 2 | Fondy | EXCLUDE_AMBIGUOUS |
| 1009382 | 81 | Verejnoprávna inštitúcia | APPROVED_LEGAL_ENTITY |
| 1009383 | 1 | Iná organizácia verejnej správy | EXCLUDE_AMBIGUOUS |
| 1009701 | 198 | Združenie (zväz, spolok, spoločnosť, klub ai.) | APPROVED_LEGAL_ENTITY |
| 1009721 | 33 | Cirkevná organizácia | APPROVED_LEGAL_ENTITY |
| 1009741 | 2 | Stavovská organizácia - profesná komora | APPROVED_LEGAL_ENTITY |
| 1009751 | 43 | Záujmové združenie právnických osôb | APPROVED_LEGAL_ENTITY |
| 1009801 | 2832 | Obec (obecný úrad), mesto (mestský úrad) | APPROVED_LEGAL_ENTITY |
| 1009803 | 211 | Samosprávny kraj (úrad samosprávneho kraja) | APPROVED_LEGAL_ENTITY |
| 1009804 | 1 | Európske zoskupenie územnej spolupráce | APPROVED_LEGAL_ENTITY |
| 1009921 | 3 | Medzinárodné organizácie a združenia | APPROVED_LEGAL_ENTITY |
| 1009995 | 4 | Nešpecifikovaná právna forma | EXCLUDE_UNSPECIFIED |
| 1009CZ141 | 3 | Obecně prospěšná společnost | APPROVED_LEGAL_ENTITY |
| 1009CZ301 | 1 | Státní podnik | APPROVED_LEGAL_ENTITY |
| 1009CZ325 | 1 | Organizační složka státu | EXCLUDE_AMBIGUOUS |
| 1009CZ331 | 6 | Příspěvková organizace | APPROVED_LEGAL_ENTITY |
| 1009CZ361 | 1 | Veřejnoprávní instituce (ČT,ČRo,ČTK) | APPROVED_LEGAL_ENTITY |
| 1009CZ601 | 13 | Vysoká škola | APPROVED_LEGAL_ENTITY |
| 1009CZ641 | 1 | Školská právnická osoba | APPROVED_LEGAL_ENTITY |
| 1009CZ661 | 2 | Veřejná výzkumná instituce | APPROVED_LEGAL_ENTITY |
| 1009CZ706 | 1 | Spolek | APPROVED_LEGAL_ENTITY |
| 1009CZ736 | 2 | Pobočný spolek | EXCLUDE_AMBIGUOUS |
| 1009CZ771 | 1 | Svazek obcí | APPROVED_LEGAL_ENTITY |
| 1009CZ801 | 16 | Obec nebo městská část hlavního města Prahy | APPROVED_LEGAL_ENTITY |
| 1009CZ804 | 1 | Kraj | APPROVED_LEGAL_ENTITY |

## Record contract

Exact nested models: `schemas/eu_funds.py` (`extra="forbid"`, strict types).
Dataset: `data/eu_funds_projects.json`, 4,561 sorted records, **5,325,091 bytes**,
snapshot date **2026-10-15**. Only these project structures are allowed:

- `projectCode` = official `kod`, primary identity. All 4,561 included codes
  unique, min/max length **10/10**, observed character set
  `0123456789ABCDFGHIJKLMNPQRSTUVWXYZ`; path-safe ASCII uppercase/digits.
  Contract accepts `[A-Z0-9]{10}`, without claiming cross-period uniqueness.
- `sourceId`: unique positive upstream ID, plus canonical official
  `sourceUrl` (`https://api.itms21.sk/public/v1/projekt/id/{sourceId}`). Manual
  §2, list-service description states **“ID a Kódy (ak existujú) sú nemenné,
  a je možné si ich zapamätať”**. Both are traceability for eligible legal
  entities only, not alternate publication of excluded projects.
- `status`: source `label`, `inImplementation` (`vrealizacii`) and `completed`
  (`ukonceny`), without an invented ACTIVE/FINISHED enum.
- `programme`: `code`, `nameSk`, optional `shortName` and `cci`; `call`:
  `code`, `nameSk`. Seven programmes and 378 calls in the public population
  (384 calls in the full source population).
- `beneficiary`: legal-entity `name`, optional valid eight-digit source
  string `ico`, `legalForm.code/nameSk`. Preserve leading digits. No RPO join;
  invalid/non-Slovak-format IČO is omitted and counted, never truncated.
  Current snapshot: zero invalid IČO omissions.
- `implementationRegions`: sorted unique `nuts/nameSk` references. All
  observed source implementation codes are the eight Slovak **NUTS3** regions
  `SK010`, `SK021`, `SK022`, `SK023`, `SK031`, `SK032`, `SK041`, `SK042`.
  Exact code/label validation is self-contained and checked against local
  Eurostat regions; no PortalVS dependency, seat/district/municipality inference
  or fuzzy matching. No foreign/unexpected codes observed, despite some
  foreign legal-entity beneficiaries. A later unexpected code is reported and
  not projected until reviewed; malformed codes fail without logging values.
- `financials.contractedTotal`: exact nonnegative **total contracted amount**
  from `celkovaZazmluvnenaSuma`. Manual §3 project list (field labelled
  “Celková zazmluvnená suma”; local extraction L5844–5847) establishes meaning,
  **not currency**. Therefore **no `Eur` suffix/currency claim**. Parsed directly
  with `Decimal`, serialized as decimal string, no binary float, arithmetic,
  rounding or fabricated two decimals. This is **not** contracted NFP,
  requested, approved, provided, paid or certified money.
- `sourceUpdatedAt`: upstream `updatedAt` epoch milliseconds converted
  deterministically to UTC ISO-8601; source row update only, not proof of
  nested freshness. No implementation start/end dates.

Project titles (`name`, `title`, `nazov` at project level), descriptions,
addresses, tax/contact fields, statutory persons, partners, suppliers,
accounts, detail-only amounts/activity/budget fields and rich domains are
not projected. Tests use synthetic unsafe subjects only, never real excluded
source identifiers. No title-person detection heuristic is used.

## API

- `GET /v1/eu-funds/projects`: standard paginated envelope, default `limit=50`,
  max 200, `offset=0`. `count` is returned page size, `total` is filtered size.
- Exact optional filters: `programmeCode` (six digits), `callCode` (nonempty
  printable source identifier, max 256, no angle brackets), `beneficiaryIco`
  (eight digits), `nuts` (NUTS-shaped code), `inImplementation`, `completed`
  (only case-insensitive `true`/`false`). AND semantics, surrounding whitespace
  trimmed, no fuzzy/text search. `limit` 1–200 and nonnegative `offset` up to
  2,147,483,647 are decimal integers.
- `GET /v1/eu-funds/projects/{projectCode}`: present 200; valid unknown **404
  NOT_FOUND**; malformed code **400 INVALID_FORMAT**. Privacy-excluded projects
  behave identically to ordinary nonexistent codes. No exclusion oracle.
- Malformed filters/pagination: **400 INVALID_FORMAT**, existing global error
  envelope/source. Success source names MIRRI/ITMS21+ and OpenSK transformation;
  `metadata.lastUpdated` comes from snapshot acquisition, `version="v1"`.
- Both routes: `STATIC_CACHE_CONTROL` (`public, max-age=86400`), strong
  body-derived ETag, Last-Modified from the matching snapshot constant,
  conditional 304s. Different filtered bodies have different ETags. Existing
  global rate limiter applies; no per-domain quota.

OpenAPI: **37 → 39 GET operations**; `/v1` unchanged. Source id `euFunds`:
public `production`, licence `verified`, coverage `partial` (internal registry
uses its existing `imported` status, mapped to production by the service).

## Manual acquisition / refresh

1. Recheck project-specific publisher/distribution/terms and schema evidence.
   **Stop** if the authoritative rights grant disappears or worsens. Recheck
   all observed legal forms; positive code/label additions need intentional
   evidence/review, not absence from a denylist.
2. Select a **new/empty external temporary directory**. On Windows, for example:

   ```powershell
   python scripts/acquire_itms21_projects.py --output-dir "C:\Users\matej\AppData\Local\Temp\opencode\itms-refresh" --page-size 250
   ```

   Stdlib fetching, fixed official project-list host/URL, no redirects, bounded
   page/response size, 60 s timeout, at most three attempts on transient
   network/429/5xx, Retry-After honored (stop if >120 s), polite 1.5 s pacing,
   OpenSK-identifying User-Agent. Never called by runtime/CI/scheduler. A
   failure creates **no complete manifest**; discard/retry separately rather
   than merging captures. No detail-fetch explosion. Never log row bodies/names.
3. Dry-run is default. A **fresh clone** can refresh using the checked-in
   `data/eu_funds_projects.json` as its previous baseline and only the **new**
   complete private acquisition. No previous raw capture is required:

   ```powershell
   python scripts/import_itms21_projects.py --manifest "C:\external\new\manifest.json"
   ```

   New raw byte sizes/hashes, manifest hash, offsets, sizes and unique
   IDs/codes must verify before any production write. The importer is offline.
   Reports contain counts/legal-form review, not excluded project lists.
4. Review counts, legal-form decisions, geography anomalies and refresh report:
   previous/new included counts, added/removed **published** counts, current
   privacy-exclusion/upstream-removal counts, changed **published** legal-form
   set, changed published project count and source population change. Inspect
   status/money diffs. Old raw is optional enrichment only (semantics below).
5. Explicit `--write-production` writes **only** `data/eu_funds_projects.json`,
   atomically and deterministically. If previously public codes disappear or
   become excluded, review then explicitly add `--acknowledge-removals`.
   Ordinary money/status changes require no removal acknowledgement. Optional
   `--write-preview` stays inside ignored `data/generated/`; research
   `--projects/--detail` input cannot write production.

   ```powershell
   # No removals: no previous acquisition or acknowledgement needed.
   python scripts/import_itms21_projects.py --manifest "C:\external\new\manifest.json" --write-production
   # After reviewing published removals/privacy withdrawals:
   python scripts/import_itms21_projects.py --manifest "C:\external\new\manifest.json" --write-production --acknowledge-removals
   ```

6. Update non-personal manifest/evidence, `EU_FUNDS_LAST_UPDATED` and source
   catalogue date from actual acquisition, then docs/counts/measurements. Run
   validators, integrity checks, pytest, compileall, local smoke and diff checks.
   Inspect Git status/tracked files: **never add raw source pages or excluded
   identifier diagnostics**. Review normalized diff before committing.

Raw captures remain sensitive temporary maintainer material, not a public
archive; restrict access/retention. **They may be discarded after validating
and importing them to the maintainer's satisfaction**. Secure archival is
optional, never operationally required for future safe refreshes. Commit only
the privacy-minimized dataset and non-personal manifest, never excluded
identifiers or deterministic identity hashes as tracking substitutes.
This repository retains no raw bodies.
There is no automatic refresh, network importer, database or CI acquisition.

### Refresh report and optional enrichment

The base report always uses **old committed public JSON + new complete source**:

| Field | Meaning without any previous raw acquisition |
| --- | --- |
| `previousIncludedCount`, `newIncludedCount` | Old/new public record counts |
| `addedPublishedProjectCodesCount` | New public codes absent from old public JSON |
| `removedPublishedProjectCodesCount` | Previously public codes absent from new public JSON |
| `projectsBecomingPrivacyExcludedCount` | Removed public codes present in the new exclusion set |
| `projectsRemovedUpstreamCount` | Removed public codes absent from the new complete source population |
| `changedPublishedProjectsCount` | Previously public, still public records with changed normalized content |
| `changedPublishedLegalFormCodeSet` | Added/removed form codes comparing public records to public records |
| `sourcePopulationChange` | New source count minus old dataset metadata's source count |
| `previousRawAcquisitionUsed` | `false` |
| `projectsBecomingNewlyEligibleCount` | `null` (unknown split, never fabricated) |

Every removed public project still present upstream must be accounted for by
the new exclusion set; an unexplained disappearance **fails closed**, even
with acknowledgement. All published removals require `--acknowledge-removals`
before production replacement. Dry-run succeeds with a complete candidate and
review report for explained removals; a blocked write leaves old JSON unchanged.
Routine reports contain counts, not removed/excluded project identifiers.

Without old raw evidence, a newly published code could be a new upstream
project **or** a previously excluded one becoming eligible. Source IDs,
timestamps, ordering and current legal forms cannot establish this distinction.
Only the added-public count is known; no source-level legal-form-set change or
new-upstream-public count is claimed in the base report.

**Optional** richer comparison, only if a prior acquisition was securely kept:

```powershell
python scripts/import_itms21_projects.py --manifest "C:\external\new\manifest.json" --previous-manifest "C:\secure\optional-archive\old\manifest.json"
```

The supplied old manifest must match the committed dataset's
`sourceManifestSha256`, and all its pages/hashes/coverage must validate. A
contradictory/corrupt supplied archive fails, never silently ignored. Successful
enrichment sets `previousRawAcquisitionUsed=true` and reports
`projectsBecomingNewlyEligibleCount` (added public codes in old source),
`newUpstreamPublishedProjectsCount` (added public codes absent from old source)
and `changedSourceLegalFormCodeSet` (old source forms versus new source forms).
The candidate dataset and removal guard do not depend on this enrichment.

## Storage measurements

Local Windows / Python 3.14 measurements on this full production snapshot:

| Metric | Measured |
| --- | ---: |
| Normalized JSON | 5,325,091 bytes / 4,561 projects |
| JSON cold parse (median of 5) | 73.66 ms |
| Service cold load including parse/typed validation (median of 3) | 320.12 ms |
| Tracemalloc retained / peak during cold load | 29,818,122 / 38,141,691 bytes |
| Process RSS (app imported, EU slice loaded, before tracing) | 100,233,216 bytes |
| Warm indexed code lookup (10k mean) | 0.203 µs |
| List filter scan (`401000`, completed=false; 100 mean) | 3.70 ms |
| Default 50-project JSON response | 49,641 bytes |

Timing uses `perf_counter` / `timeit`, cold caches explicitly cleared and GC
run between loads; no upstream used. RSS is whole test-process working set,
not a per-dataset retained-heap estimate or all-domain deployment peak.
Normal responses use typed validated local objects and a process-local cache.

Review triggers: this file is below 50 MB, 100k records and 3 s cold load;
measured process RSS below 400 MB; no joins/full-text requirement or frequent
refresh pressure. Validator top-level total is 20,548 records. Counting nested
ECB rates instead of date records gives approximately 234,732 records overall
(also below 250k; record-count conventions matter). These are review triggers,
not automatic migration rules. **Storage verdict: `JSON_CONTINUE`**. No SQLite.

## Red-team decision

All 14 milestone risk questions answer **NO**: natural-person/SZČO projects,
denylist-only eligibility, excluded identifiers/URLs/facts, project titles,
addresses/contact/tax fields, ITMS2014+, runtime upstream calls, all-Slovak-
funds coverage claims, unimported paid/provided claims, binary-float money,
invented CC BY version, lookup exclusion oracle and raw personal-data captures
in Git. Exact nested schema + synthetic exclusion/hash/removal/HTTP regressions
enforce the policy; this cannot independently guarantee upstream classification
accuracy, so every refresh still requires review.

NBS snapshot remains v225 / 2026-05-18; outreach states unchanged: banks
`REPLY_RECEIVED_RESOLVED`; PortalVS/telecom/ŠÚ SR `SENT_AWAITING_REPLY`.
Platform public-promotion gate remains unresolved PortalVS compliance.

## Milestone validation

- Dataset validation: **14 datasets, 0 errors / 44 existing compliance warnings**;
  EU-funds validator: 4,561 records, 0 errors/warnings.
- Referential integrity: passed. Full offline suite after the PR #34 refresh
  correction: **643 tests passed** (including discarded-old-capture fresh-clone,
  CLI, upstream/privacy removal, unexplained disappearance and optional-enrichment
  regressions).
- `compileall scripts routers services tests schemas` and diff whitespace checks:
  passed. Local HTTP smoke: **41/41 passed**, including both new routes and
  required typed OpenAPI paths.
- Final version **0.23.7**, API namespace `/v1`, metadata version `v1`, exactly
  **39 GET operations**. `euFunds` public production/partial/verified.
- Bank file SHA-256, date constant and endpoint JSON matched retained pre-work
  baseline; every non-`euFunds` source-registry entry was unchanged from main.
  Excluded raw source codes/IDs were checked locally against public project
  identities (zero overlap), without recording excluded identifiers.
- No dependency/database/production scheduler change, no raw captures or real
  personal-subject fixtures added. CI results are attached to the milestone PR.

Refresh follow-up red-team answers: **YES** a fresh clone can refresh without
old raw; **YES** every published disappearance still needs acknowledgement;
**YES** current privacy transitions and **YES** upstream removals are detectable
from the new acquisition; **NO** newly-eligible history is invented without old
evidence; **YES** optional old evidence enables richer statistics; **NO** old raw
retention is mandatory; **NO** raw pages are committed; **NO** excluded identities
or matching hashes are added; **YES** existing privacy/manifest/removal protections
remain intact. The current 4,561-record / 2026-10-15 public snapshot is unchanged.
