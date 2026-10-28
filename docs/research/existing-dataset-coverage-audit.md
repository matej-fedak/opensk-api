# Existing dataset coverage audit — 0.23.13

Baseline: main `9bdfca621c1aea43f37f1d9a62dab20e4d2c3b52`, version
0.23.12. Checked 2026-10-28 against local production files and `/v1/sources`.
No new domain or route is proposed. Historical snapshot dates below are not
claims of current national coverage. Baseline byte hashes and runtime/OpenAPI
evidence are retained privately; final before/after hashes are recorded below.

## Decisions before production changes

| Domain | Baseline records / time coverage | Source; public status / coverage | Limitation and source headroom | Technical / rights / privacy / semantics gates | Classification / recommendation |
| --- | --- | --- | --- | --- | --- |
| Banks | 30; v226 effective 2026-10-08 | NBS converter; production / complete | Complete within domestic converter; later releases are refreshes, not coverage expansion | All existing gates satisfied within approved scope; no refresh needed | **ALREADY_MEANINGFUL** |
| Holidays / business days | ~~45 dates; 2024–2026~~ → **112 dates; 2024–2030, with explicit state-holiday/day-of-rest flags** | Act 241/1993 via official Slov-Lex (primary); NBS 2026/2027 corroboration; production / partial (bounded verified window) | CORRECT_NOW: seed conflated state holiday with day of rest; 28 October missing | Deterministic; law verified 2026-10-28 with future-effective check; no personal data; bounded to reviewed horizon, subject to legislative change | **EXPANDED_VERIFIED** — see finalization section |
| PSC | 1,420 keys / 3,101 flat matches; historical classifier snapshot, freshness 2026-06-02 | PortalVS legacy classifier 42; production / partial | SOURCE_BLOCKED + RIGHTS_BLOCKED; successor has more rows but lacks approved identity/temporal/address semantics | Technical/admin mapping and reuse gates unresolved; no successor occurrence projection approved | **BLOCKED**, preserve bytes; NO_GO_SUCCESSOR_PSC |
| Companies | 4 seed records; mixed local records, not temporal registry coverage | Local company seed / RPO research; seed / seed | SOURCE_BLOCKED + PRIVACY_BLOCKED; RPO is materially larger | Acquisition/privacy gate not cleared; no new records, joins or rights inference | **BLOCKED** |
| Regions | 8; freshness 2026-05-27 | Eurostat reference; production / complete | Complete existing national reference scope | Already meaningful; no personal data; no expansion/refresh needed | **ALREADY_MEANINGFUL** |
| Districts | 79; successor acquisition 2026-10-16 | PortalVS / IS Číselníky county; production / complete | Complete administrative scope; RIGHTS_BLOCKED for public promotion | Existing IDs/relationships complete; reuse clarification pending; not an expansion candidate | **ALREADY_MEANINGFUL**, preserve bytes |
| Municipalities | 2,927; successor acquisition 2026-10-16 | PortalVS / IS Číselníky town; production / complete | Complete approved administrative/borough/military-unit scope; RIGHTS_BLOCKED for promotion | No inferred street/local-part directory; reuse still pending | **ALREADY_MEANINGFUL**, preserve bytes |
| Phone areas | 2,922; 2026-09-15 import, 2,919 geography-linked | Telecom regulator workbook; production / complete | Complete imported scope; RIGHTS_BLOCKED, not too few rows | Pending reuse reply; unresolved links do not justify name inference or field expansion | **ALREADY_MEANINGFUL**, preserve bytes |
| Vehicle codes | 93; legacy reference ending 2023-01-01 | Slov-Lex historic §36 table; historical / complete | HISTORICAL_REFERENCE / INTENTIONAL_PRODUCT_SCOPE | No approved current plate decoding/owner semantics; rights remain pending | **INTENTIONAL_LIMIT** |
| School facility counts | 1,227 aggregate rows; as of 2025-09-15 | MŠVVaM aggregate CSV; production / complete | INTENTIONAL_PRODUCT_SCOPE; source already imported within aggregate scope | Institution-level source/reuse/privacy gates separate and blocked; no need to expand aggregate schema | **ALREADY_MEANINGFUL**, no institution-level expansion |
| Procurement | 100 notices; latest 2026-09-29 demonstration snapshot (**unchanged**) | TED Search API; production / partial | Source holds a much larger corpus (68,926 notices acquired privately) | PRIVACY_BLOCKED: no deterministic source-based natural-person exclusion (`buyer-person` absent in all 68,926 rows incl. 22,730 eForms-explicit); hypothetical safe eligible corpus 0 | **BLOCKED — PRIVACY**; **NO_GO_PROCUREMENT_EXPANSION**, preserve 100-record TED_PARTIAL bytes |
| Exchange rates | 7,112 publication dates / 221,296 rates / 41 currencies; 1999-01-04–2026-10-12 | ECB full-history feed; production / complete | Complete relative to imported feed; INTENTIONAL_PRODUCT_SCOPE (EUR reference values) | Reuse verified; exact decimal strings; not every day/world currency/live prices | **ALREADY_MEANINGFUL**, no refresh |
| EU funds | 4,561 of 4,574 acquired projects; ITMS21+ 2021–2027, snapshot 2026-10-15 | MIRRI; production / partial | INTENTIONAL_PRODUCT_SCOPE + PRIVACY_BLOCKED for excluded records; 13 wholly excluded | Positive legal-form review; no natural-person/unreviewed restoration or ITMS2014+ fusion | **ALREADY_MEANINGFUL**, preserve bytes |

Only procurement and holidays are eligible for production expansion. No source
acquisition/research is reopened for any blocked domain. Follow-up emails sent by
the maintainer on 2026-10-28 do not establish permission; no correspondence is sent
by the agent and no pending licence state is upgraded.

## Initial source verification

TED official search documentation, OpenAPI, reuse guide and legal notice were
rechecked on 2026-10-28:

- https://docs.ted.europa.eu/api/latest/search.html
- https://api.ted.europa.eu/api-v3.yaml (OpenAPI 3.1.0 / API 3.0.0;
  456,129 bytes; SHA-256 `7df29b0c4e64368e1feffa592083f69978db1f9125776e93bc6b269954ef6c11`)
- https://docs.ted.europa.eu/ODS/latest/reuse/
- https://ted.europa.eu/en/simap/developers-corner-for-reusers
- https://ted.europa.eu/en/legal-notice

Current official OpenAPI still supports POST `/v3/notices/search`, expert query,
explicit fields, `onlyLatestVersions=true`, PAGE_NUMBER (15,000 maximum results)
and ITERATION (no result-count limit). Both allow at most 250 notices / 10,000
selected fields per page. ITERATION uses an Elasticsearch point-in-time view,
expires next OJS release +24h, terminates on an empty page, and reports a total
matching count. Tokens must not repeat and totals must remain consistent.
Field names can change without an API-version bump; importer validation is required.

Live probe `buyer-country = SVK AND publication-date <= 20261028`, ITERATION,
latest-only, approved eleven fields: HTTP 200 JSON, reported **68,926** notices,
two returned records, `timedOut=false`, next token present. This is fresh probe
evidence, **not the final acquisition count or an expected-count constant**.
Earliest probe record is in 2016: available history is not unlimited history.
Current legal notice explicitly allows commercial/noncommercial procurement-notice
reuse unless otherwise noted, with third-party/personal-content reservations;
editorial CC BY and metadata CC0 are distinct. No material reuse regression found.

Holiday evidence: consolidated law 241/1993 effective 2025-11-01 (261/2025),
previous effective version 2024-01-01 (530/2023), plus official NBS 2026/2027 table
and Labour Inspectorate guidance. **Existing seed is not legally correct for the
non-working-day concept**: remove September 1 in 2024–2026, November 17 in
2025–2026, and May 8 / September 15 in 2026 only. Unaffected historical rows and
names must remain exact. No payroll-premium or TARGET semantics are introduced.
Future years can be generated under currently enacted standing rules, explicitly
as-of the evidence check, not a guarantee against future legislative changes.

- https://static.slov-lex.sk/static/SK/ZZ/1993/241/20251101.html (§2(3), §4b)
- https://static.slov-lex.sk/static/SK/ZZ/1993/241/20240101.html (§2(3))
- https://nbs.sk/o-narodnej-banke/sviatky-v-sr/
- https://www.ip.gov.sk/aktuality/sviatky-8-maj-15-september-2026-z-pohladu-pracovneho-prava.html

## Pause decision — no production promotion

The maintainer explicitly selected **Pause for privacy decision** after the full
acquisition exposed natural-person/sole-trader buyers. **0.23.13 is unfinished**;
no production data, source catalogue, freshness or public API change is approved
or made. Version remains `0.23.13-dev`; no PR/tag/release or outreach.

The acquisition completed 2026-10-28T21:23:21.101159Z–21:28:05.490605Z:
**68,926 reported / 68,926 acquired**, 276 nonempty pages plus one empty terminal
page, **466,528,049 raw bytes**; zero duplicate canonical publication identities,
zero acquisition scope/date errors, stable reported total throughout. HTTP attempts:
277 successful 200s, six retried 429s, one retried 502. Full raw pages/tokens and
page hashes stay private under
`C:\Users\matej\AppData\Local\Temp\opencode\ted-02313\full-v2\`.
Committed non-content summary: `procurement-coverage-acquisition.json`.

Important source/schema findings, **not permission to loosen production**:

- Historic publication numbers are sometimes unpadded (`150-2017`); exact numeric
  zero-padding preserves the current six-digit public ID format. Initial strict
  acquisition failed closed; the complete second run handles this explicitly.
- 54 records omit the selected optional `buyer-name`; the existing production
  validator requires nonempty names. Do not invent missing buyers.
- 39 notices among rows with named buyers have a non-Slovak procedure-level place
  country. A Slovak buyer does not imply performance in Slovakia. The current
  production validator permits only SK/null and remains unchanged pending review.
- 15 rows among named-buyer records have a non-five-digit postcode (including
  source city labels and invalid lengths). No postcode/geography inference is
  justified. Draft candidate handling is not a promoted policy.
- A screening pass found 4,155 distinct Slovak buyer display labels and 17
  honorific/no-obvious-institution-marker candidates. Manual inspection distinguishes
  named hospitals from individual/sole-trader buyers. **This screening is not a
  complete privacy classifier or approval**, and no actual personal names/record
  IDs from it are committed. A field allowlist does not prevent personal names
  from occurring inside an otherwise approved buyer-name field (or free text).

**Procurement production status: NO_EXPANSION / PAUSED_PRIVACY_DECISION.** The
current 100-record production file is byte-identical, not replaced by the acquired
corpus. No complete-TED production claim, no silent exclusions/redaction, no
arbitrary recent-period fallback to evade privacy. Latest-only and PIT/query count
agreement establish acquisition coverage, not institutional identity or privacy.
The importer draft explicitly refuses `--write-production` while paused.

### Required decision before resuming

Approve a source-based institutional-buyer/privacy classification and exclusion
strategy separately, including how joint buyers, missing buyer identity and free
text are handled. The current eleven-field projection provides no authoritative
legal-form marker. Do not classify legal entities by honorific/suffix/name guesses,
add identifiers/fields or fetch details without separately approving that scope.
If unsafe/unclassified notices must be excluded, define and disclose that narrower
scope instead of calling it every matching TED notice. Source completeness and
privacy-safe production coverage are separate axes.

Holiday law verification supports an offline 2024–2030 candidate (90 non-working
holidays after seven evidenced historical corrections). The generator and its
independent Easter tests are retained as **unpromoted tooling**. No holiday
production write, freshness bump, description/example update or business-day
coverage change has happened. Future statutory dates remain as-of checked law,
not a guarantee against later amendments.

The 100-record baseline benchmark is private in `ted-02313/benchmark-before.json`:
73,616 working-checkout bytes; median JSON parse 0.512 ms; cold service load 1.129 ms;
retained traced load heap 209,111 bytes; RSS after load 28,766,208 bytes; last-ID
lookup 0.009 ms; representative searches 2.53–3.246 ms. Environment: Python 3.14.5,
Windows 11, AMD64 Family 25 Model 117. No safe expanded candidate has been promoted
or benchmarked, so **no final storage verdict** or before/after performance claim
is made. No database/index/Redis/dependency change is justified from this pause.

Pause checkpoint validation: **37 targeted acquisition/generator/import tests
passed**, including an explicit test that procurement production promotion is
blocked. `git diff --check` passed. All **14 production JSON byte hashes** match
the pre-work main baseline exactly; `data/` and the production dataset validator
have no content diff. Actual OpenAPI still has **39 GET operations** with the same
complete path/method/operationId inventory. Full milestone validation, smoke,
hosted CI and PR-ready status are **not claimed** at this unfinished checkpoint.

## Subsequent buyer-privacy evidence spike — 2026-10-28

[Buyer privacy report](procurement-buyer-privacy.md):
**NO_GO_PROCUREMENT_EXPANSION** with the reviewed source fields. A separately
authorized metadata-only capture reconciles exactly with all 68,926 original
identities; `buyer-person` is absent in every row, including 22,730 positively
identified eForms notices. Hypothetical eligible corpus: **0**; all 68,926 excluded
as unknown. BT-11/BT-501 do not establish a deterministic buyer-specific legal-
person guarantee, and independent arrays have no demonstrated complete buyer
join. This adds evidence to, rather than rewrites, the original pause.

## Finalization — 2026-10-28

The maintainer settled both pending decisions; the milestone leaves
`0.23.13-dev` as **`0.23.13`**:

- **Procurement: BLOCKED — PRIVACY / NO_GO_PROCUREMENT_EXPANSION**
  (locked, not reopened). Production stays the byte-identical 100-record
  `TED_PARTIAL` snapshot; procurement freshness is unchanged; none of the
  68,926 privately acquired records is served. Reopen only with a genuinely
  new authoritative buyer-privacy discriminator with complete buyer
  association — do not repeat the acquisition or infer status from
  names/suffixes/IČO-like values/BT-11/identifiers/regexes. Evidence:
  `procurement-buyer-privacy.md`; state: `data/sources.json`
  (`procurementNotices`).
- **Holidays/business days: EXPAND_NOW / CORRECT_NOW →
  EXPANDED_VERIFIED (2024–2030).** The statutory-holiday vs day-of-rest
  conflation is corrected additively (`isStateHoliday` / `isDayOfRest`), the
  missing 28 October rows are added for all seven years, the 2025-11-01
  transition and the 2026 §4b exception are date-exact, and business-day
  semantics now consume `isDayOfRest` instead of dataset membership. No new
  routes; 39 GET operations, `/v1` and `metadata.version` `v1` unchanged.
  Evidence: `holiday-calendar-correctness.md`; generator `scripts/generate_holidays.py`
  output is test-locked byte-identical to `data/holidays.json`.

All other domains keep their classifications and byte-frozen production data.
Full milestone validation (dataset validation, referential integrity, pytest,
compileall, OpenAPI inventory, before/after hashes, smoke) is recorded in the
final report for this milestone.
