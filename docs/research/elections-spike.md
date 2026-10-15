# 0.23.2 — Slovak Elections Data Spike

Verified 2026-10-11. Primary election: **Voľby do Národnej rady Slovenskej republiky 2023**, voting date 2023-09-30. This is a research/tooling milestone, not production approval.

**NO PUBLIC ELECTIONS ENDPOINT IS ADDED. No production election dataset or official raw file is committed.**

## 1. Executive decision

**GO_AFTER_LICENCE_EVIDENCE** — this includes an approved acquisition workflow, not just an attribution sentence. Official aggregate data is technically tractable, internally consistent and independently usable without PortalVS. The general ŠÚ SR CC BY 4.0 policy is encouraging, but election-specific applicability and the explicit automated-download restriction must be resolved before promotion.

`JSON_CONTINUE`. No SQLite, Redis, runtime upstream requests, candidate service or all-election framework is justified. A successful parser does not authorize production redistribution.

## 2. Official source

Publisher: **Štatistický úrad Slovenskej republiky**. The archive explains its statutory responsibility for processing and publishing elections/referenda. The election page identifies itself as an official public-authority website, its operator and source as ŠÚ SR, and the results as definitive.

- Archive: <https://volby.statistics.sk/>
- Exact 2023 download page: <https://volby.statistics.sk/nrsr/nrsr2023/sk/subory_na_stiahnutie.html>
- Page-backed download index: <https://volby.statistics.sk/nrsr/nrsr2023/json/downloadSK.json>
- Definitive publication stated by the page: **2023-10-01 14:30**. This is not the retrieval date or the individual files' HTTP Last-Modified.

The JSON index is a published website mechanism, not a promised/versioned acquisition API. Pin observed links; do not extrapolate filenames across years. A directly verified election-specific DCAT/licence entry was not established by this bounded investigation.

## 3. Source/reuse evidence

Full exact wording, official URLs, date and conditions: [source/licence track](elections-source-licence.md) and [retained evidence](source-verification-evidence.md). Official general terms: <https://slovak.statistics.sk/wps/portal/ext/aboutus/webpage/terms/> (stated update 15.03.2023; checked 2026-10-11).

The terms explicitly allow:

> šíriť (kopírovať, sprostredkovávať a distribuovať verejnosti);
>
> využívať komerčne.

They name **Creative Commons Attribution License (cc-by) 4.0**, require attribution to ŠÚ SR without implying endorsement, and exclude third-party intellectual-property material. Conversely:

> používanie robotov, pavúkov (spiders, crawlers) a ďalších podobných nástrojov na zhromažďovanie a sťahovanie dát, je výslovne zakázané.

| Use | Current evidence/conclusion |
| --- | --- |
| Local retention, CSV→JSON, field normalization | CC BY reproduction/adaptation rights support these **if election applicability is confirmed**. |
| Combining with reference data | Adaptation rights are supportive; each reference source has separate rights. This design does not copy PortalVS enrichment. |
| Public API, repository snapshot, downstream commercial use | General terms support sharing/commercial reuse; obtain election-specific confirmation and retain data notices separately from code licensing. |
| Attribution | Publisher, original election/table/source URL, CC BY link, modifications, no endorsement; final wording requires retained clearance. |
| Acquisition | No permission inferred from successful requests or offered CSVs; no new fetcher or scheduled collection. |

**Confidence:** high for authority and exact general terms; medium for election-specific coverage; acquisition permission unresolved. OGP/open-data publication basis is not a licence substitute.

Agent B downloaded the research files before Agent A's restriction finding was communicated. All subsequent work uses those local bytes; new scripted acquisition was stopped. Acquisition times and exploratory retries are disclosed in the schema track, not retrospectively called approved. No raw file is redistributed in this PR. A future approved manual snapshot could support an offline importer, but that workflow is a question for the publisher, not assumed permission.

Fourth clarification package: [outreach §7](source-licence-outreach.md), To `info@statistics.sk`, CC `volby@statistics.sk`, both verified on the official election contact page. Sent manually 2026-10-11; elections, PortalVS and telecom remain **SENT_AWAITING_REPLY**. NBS bank reuse alone resolved by reply 2026-10-14; that does not clear elections or imply permission from silence.

## 4. Dataset inventory

The election index contains 33 tables. Relevant aggregate inputs: territorial dictionary `tab0c`, municipality summary `tab02d`, municipality political-subject votes `tab03e`, tiny national/regional/district controls `tab01`/`tab02a`/`tab02c`, party national totals `tab03a` and institutional party list `tab0a`.

Horizontal party table `tab08d` is an alternative to evaluate later, not imported in parallel or claimed equivalent without inspection. Candidate lists, elected-person lists, preference-vote tables and commission minutes are out of scope. No candidate/person records or bulk archives were downloaded. Catalogue-advertised candidate preference files reach 804.2 MB/1.7 GB; they are irrelevant to the aggregate storage decision.

## 5. Selected 2023 files

All exact selected URLs have prefix **`https://volby.statistics.sk/nrsr/nrsr2023/files/csv/`** followed by the filenames below. Responses were HTTP 200, final URL unchanged, Content-Type `text/csv`, retrieved 2026-10-11 UTC. Source bytes and manifests remain only in the approved temporary research directory.

| File | Role | Bytes | Rows | SHA-256 |
| --- | --- | ---: | ---: | --- |
| `NRSR2023_SK_tab0c.csv` | Required native territory | 231,229 | 2,927 | `479fe57712c4a1500e466ddd2bf7b967e1aeec69fceb34326a2683f29519fa1f` |
| `NRSR2023_SK_tab02d.csv` | Required municipality summary | 361,393 | 2,927 | `cbabf05cf3d64bd92106670363c538fbaf0b9ea3a547339b917c022c1f484a5e` |
| `NRSR2023_SK_tab03e.csv` | Optional aggregate party votes | 6,009,826 | 44,272 | `f560181346e002fbe287d5a34b5e20db09da85bfa9e93ea04026b1cce13ef887` |
| `NRSR2023_SK_tab01.csv` | National reconciliation control | 423 | 1 | `539bce1f2141b9bb789ad1ea627bfa9acc1ce40d9414e3f992b387abc0f4b0fd` |

Territory + turnout alone needs **592,622 bytes**; the three core files total **6,602,448 bytes**. Party-level input is manageable and materially improves a potential municipality result widget. It remains optional, not a prerequisite for the narrower turnout preview.

The [schema track](elections-data-schema.md) contains literal URLs, hashes, timestamps, HTTP freshness and sizes for all 17 measured files, including supporting controls and historical samples. CSVs contain headers/data, no retained embedded licence declaration was established; external rights evidence remains necessary.

## 6. Encoding and CSV format

NR SR 2023: **strict UTF-8, no BOM, comma delimiter, double-quoted text, LF newlines, dot decimals, no thousands separators**, one header row. No blank cells in the selected three tables. Quoted political-subject names include commas: a real CSV parser is mandatory. No lossy decoding or CP1250 fallback.

Positive evidence includes UTF-8 diacritics and strict CP1250 failures on territory/result files. A successful CP1250 decode of a small file can still produce mojibake; ASCII-only historic tables cannot uniquely identify an encoding without their companion files. This corrects the roadmap's CP1250 hypothesis, not a source change.

## 7. Schema analysis

Exact headers and mappings are retained in the schema track and pinned in `scripts/import_elections.py`. Territory has nine columns; summary has 18; party municipality results have 14. Shared prefix: region/circuit/district/municipality codes and names. Summary adds configured/confirmed precincts, registered/participating voters, submitted envelopes, valid votes and four percentages.

Counts are nonnegative integers; official percentages truncate to two decimals. Preserve source percentages and validate with decimal arithmetic. **Valid-vote share uses participating voters, not submitted envelopes.** Preferential-voter aggregate columns in the party input are not candidate votes and are unnecessary for the preview's public-field allowlist.

`tab03e` is sparse: positive-vote pairs only, **44,272** of the possible 73,175 pairs. Missing pairs are not parser errors when the complete verified table reconciles to municipality totals. Do not invent zero rows from an incomplete input or treat political-subject numbers as timeless party identities.

## 8. Geography identifiers

Election identifier is the official file-prefix token **`NRSR2023`**, scoped to this profile, not a claim of a universal government election-ID standard. Preserve source code strings and labels with the election identity:

- Region: eight domestic codes, plus foreign scope `9`.
- Electoral territorial circuit: 49 domestic codes, plus `900`.
- Administrative district: 79 domestic codes, plus `900`.
- Municipality/unit: six-digit code; `599999` is foreign voting, not a physical municipality.
- Political subject: list number `1`–`25`, election-scoped, not a global party identifier.

Circuit is **not district**: circuit `101` groups Bratislava districts `101`–`105`. Current `SK…` geography IDs and native numeric election codes are different namespaces. No guessed padding or name-based IDs are introduced. Historical sample code sets agree for these three elections, but that is bounded evidence, not an all-year stability guarantee.

## 9. Municipality join results

Native territory→summary: **2,927/2,927**, identical keys/shared fields/precinct counts, no duplicates. Contemporary OpenSK municipalities: **2,926/2,927 (99.9658%)**; domestic match rate **100%**.

- Official-only: `599999 / Cudzina`, hierarchy `9/900/900`, 18 precincts, **57,856 valid votes**. Keep it in national totals and a separate foreign scope (`foreignResults` in the preview); excluding it destroys reconciliation. It is not every historical vote mailed from abroad.
- Local-only: `518638 / Valaškovce (vojenský obvod)`. No election row; do not synthesize zeros or infer the legal reason.
- **270 exact name differences**, including 17 Bratislava and 22 Košice city parts, disambiguators and spacing. Code joins succeed; no fuzzy repair. No whole-city rows are double-counted on top of city parts.
- All eight domestic regions and 79 districts have unambiguous membership-derived current-geography crosswalks, no hierarchy conflicts; district names agree. Foreign scope has no local geographic parent.

**PortalVS independence: YES.** Canonical geography is the election's own dictionary. Current geography is optional diagnostics only, with no copied names, parent IDs or hard foreign keys in normalized output. Removing PortalVS files must leave preview bytes identical; absence disables the comparison, not election ingestion. No claim that these historic native labels replace a current municipality registry.

## 10. Aggregate consistency checks

National `tab01`, municipal sums, district sums and region sums agree exactly for every integer measure, including foreign voting:

| Measure | National |
| --- | ---: |
| Configured precincts | 6,014 |
| Confirmed precincts | 6,013 |
| Registered voters | 4,388,872 |
| Participating voters | 3,007,123 |
| Submitted envelopes | 3,002,948 |
| Valid votes | **2,967,896** |

All municipality count inequalities, territory joins and four decimal/truncation equations pass. Party sums equal each municipality's valid votes and national party controls; no duplicate municipality/party key, negative count or percentage outside 0–100. Published party percentages need not sum to precisely 100 after truncation.

Only `524140 / Prešov` has 65 confirmed of 66 configured precincts. The official page explicitly excludes precinct 34 by State Commission decision. Do not fail ingestion on the assumption that definitive results mean 100% of configured precincts. This is a coverage limitation, not a parsing anomaly. Cross-year foreign/postal-vote semantics and blank mandate cells require explicit interpretation, never blanket blank→zero conversion.

## 11. Privacy assessment

**Aggregate public statistics only.** Preview scope: historical election metadata, native territorial labels/codes, turnout counts and approved party/list vote aggregates. No candidate profiles/names/IDs, birth dates, addresses, contacts, elected-person lists, voter identities or candidate preference results. Person-oriented files are excluded at acquisition, not merely filtered after download; exact headers and output allowlists fail closed on schema expansion.

Agent C correctly challenges “aggregate equals anonymized”: small municipalities and low-count party cells can support inference when combined with outside knowledge. This spike neither claims zero privacy risk nor adds cross-register/person profiling. Keep municipality level, avoid precincts and personal enrichment, preserve the foreign-voting aggregate, and document the measured low-count situation before a public release. Exact release wording and any justified withholding rule require maintainer review; withholding must not become fabricated zero and complementary totals must be considered. Public availability and CC BY do not themselves waive privacy rights.

Measured minima: **13 registered, 11 participating, 11 valid votes**; respectively **3, 7 and 7** units below 20. There are **16,291 positive party cells below five votes**, minimum one, and **zero unanimous municipalities**. These are real residual inference risks, not identifying records or proof of anonymity. The local research preview is deliberately unsuppressed and not approved for public redistribution. The proposed privacy path is a historical municipality-statistics service without personal linkage, not a voter-affiliation inference tool; a later production review must explicitly accept or mitigate these small cells rather than claiming the privacy gate is automatically cleared.

## 12. File-size/storage assessment

`JSON_CONTINUE`. Existing runtime JSON totals **3,687,740 bytes** before this addition. Selected source aggregates total about 6.30 MiB; the 1.7 GB candidate file does not change the architecture because it is excluded. Measured turnout-only preview with national control: **1,969,104 bytes**. Readable party-bearing preview: **13,460,755 bytes (12.84 MiB)**; the identical JSON tree serialized compactly is **10,064,334 bytes (9.60 MiB)**. Long-form repeated names/keys and indentation matter; don't equate source CSV size with normalized storage.

For five comparable parliamentary snapshots, rough same-shape estimates are **9.85 MB turnout-only**, **67.30 MB readable party-bearing**, or **50.32 MB compact**, not measurements of five historical elections. Several families need separate profiles and measured budgets; avoid eager loading every election into every worker.

**An advisory review trigger was reached:** Agent C's proposed 10 MiB per-election ceiling is exceeded by the readable full preview. It is a reviewer proposal, not an existing binding project constant or a SQLite mandate. Compact serialization falls below it; a future representation can avoid repeating municipality/party labels through dictionaries, or start turnout-only. Keep this reviewed scope/serialization choice explicit. An illustrative nested 100-largest-unit page is **336,276 compact bytes** (size simulation only, no route/latency claim). Offline importer Python allocations peak at **130,126,574 bytes**, retained **29,018,941 bytes** under `tracemalloc`; this is not process RSS or deployed FastAPI/multiworker memory. Deployment budgets remain a production implementation gate. No storage migration is justified by these measurements.

## 13. Historical/schema-drift sample

Bounded **NR SR 2020** and **referendum 2023** samples were acquired before the restriction finding; no historical production normalization.

- 2020 prefix `NRSR_2020_SK_` differs; pipe delimiter, technical uppercase headers and decimal commas. `tab0c` includes `TYP_OBCE`; some aggregate CSV links are null and national controls require a small XLSX with multirow headers.
- Referendum territory is `tab0b`, while `tab0c` is a different concept. Pipe/uppercase schema; `P_HL` means all ballots, `P_PHL` valid ballots, not parliamentary valid votes/percentage. Yes/no and invalid-voter denominators differ.
- Same municipality code sets in these samples, but precinct counts/foreign-unit names and postal-vote handling differ. Referendum configured precincts exceed result-row counts; no blanket equality rule.

**Resolution:** one explicit NR SR 2023 profile now, family/year-specific adapters later. Do not implement a generic all-election mapper, guessed delimiters, shared percent denominators or a universal filename template. Full byte-level/header/semantic evidence is in the schema track.

## 14. Materialized-data strategy

Approved source acquisition → local explicit input paths → strict profile normalization/validation → ignored `data/generated/` preview → human rights/privacy/semantic review → future production promotion in a separate milestone. No fetcher or runtime upstream request. No raw official files in Git; keep measured URLs/hashes and tiny synthetic fixtures. Acquisition must first be approved; this sequence is a proposed strategy, not an exception to the source policy.

Prototype commands for **already locally supplied** research files:

```powershell
python scripts/import_elections.py --territory <tab0c.csv> --results <tab02d.csv> --dry-run
python scripts/import_elections.py --territory <tab0c.csv> --results <tab02d.csv> --party-results <tab03e.csv> --national-results <tab01.csv> --dry-run
```

Default behavior is dry-run; explicit preview writing is restricted to `data/generated/`. Deterministic output has hashes/provenance without a request clock, local absolute paths or PortalVS-derived enrichment. Failed parsing/schema/native joins/aggregate validation prevent writing. Preview generation is not production approval; no `data/elections.json` is created.

Historical corrections are manual and review-driven: retain source hash/revision, rerun validation, inspect semantic differences, then atomically promote a complete snapshot only in a later approved milestone. Election date, official publication timestamp, acquisition timestamp and materialized revision are distinct. Never refresh upstream per request or advertise live election reporting. Additional years/families require new evidence/fixtures.

## 15. Proposed API shape

Design sketch only, not registered routes or a finalized contract:

1. `GET /v1/elections`: small catalogue of actually imported elections (family/date, final status, levels/measures, snapshot revision, limitations).
2. `GET /v1/elections/{electionId}/results`: bounded municipality/unit summary items, optional nested sparse party votes, exact native municipality/district/region filters and AND semantics; a municipality filter can supply a single-item lookup without another initial route.

Use the standard envelope with `{items,count,total,limit,offset}`, stable native-code ordering, proposed default 50/max 100 for party-bearing pages pending measurement. `total` counts filtered geographical units, not party rows. Unknown election ID: 404; invalid filters: 400; no matches: empty page. No party filter until its item semantics are justified; no candidates/precincts/search/arbitrary analytics. Identify foreign voting as a separate unit type and clarify inclusion/filter behavior.

Provenance: ŠÚ SR, election/table URLs, reviewed data licence/change notices, election identity, precise coverage and snapshot revision. Historical results can be corrected: body-hash ETag plus static cache policy, no unconditional immutable claim. Omit Last-Modified unless a trustworthy representation revision can be provided; election date is not freshness. Agent C found a pre-existing `If-None-Match` precedence concern in current middleware; it is recorded as a future integration test/fix gate, **not changed in this spike**.

## 16. Developer value

Plausible users: civic-tech/browser result widgets, journalism maps, education/research and turnout dashboards. No usage/interview evidence is claimed. Official bulk downloads already serve many research workflows; this should not become another unbounded mirror.

Concrete maintainer-demo task: from the locally normalized preview, select one official municipality code, display its turnout/valid votes and list-vote counts with election-native labels, and compare turnout with the published national summary. A small JSON query avoids each browser parsing a sparse CSV and joining its territory fields. That is a demonstrable convenience, **not market-demand validation**. One election cannot support historical trend claims, and party numbers/names are not stable identities across elections.

## 17. Risks/limitations and specialist synthesis

Independent tracks retained rather than manufactured consensus:

- **Agent A — source/licence:** strong general CC BY evidence, but unresolved election coverage and automated acquisition. This overrides the roadmap's earlier optimistic open-data assumption.
- **Agent B — data/schema:** exact bytes/joins/totals support a technically useful aggregate prototype; CP1250 hypothesis rejected, historical schemas are not reusable unchanged.
- **Agent C — integration/privacy/product:** no demonstrated demand, no automatic anonymization, avoid PortalVS dependency and generic infrastructure; disk size alone cannot certify production memory/latency.

Resolution: the lead accepts a narrowly scoped aggregate technical path, not unrestricted publication. Keep party input optional and native geography canonical; retain rights/acquisition as the decisive unresolved evidence gate. Numeric size/page proposals are future budgets, not measured production guarantees. Different rounded size labels appear in archive/tree and election-specific indexes; actual downloaded bytes/hashes win for this spike. No claim of agreement about demand, all-year schemas or zero privacy risk.

Limitations include the excluded Prešov precinct, sparse party rows, special foreign scope, current-versus-historical geography, correction monitoring without a source stability SLA, low-count cells, and unverified election-specific DCAT/licence/acquisition coverage. Existing source email status is unchanged. No external reply was assumed or absorbed into this branch.

## 18. Production gates

| Gate | Spike outcome / remaining action |
| --- | --- |
| Official publisher | Verified, high confidence. |
| Reproducible technical acquisition | Explicit observed URLs/hashes/schema; repeatable offline transformation. **Permitted acquisition unresolved**, no fetcher/automation approved. |
| Reuse rights | General CC BY 4.0 retained; confirm election coverage, repository/API/commercial scope and acquisition/attribution conditions. |
| Aggregate-only privacy | No person-level inputs/output; maintain minimization and approve residual small-cell release policy before shipping. |
| Deterministic transformation | Strict profile prototype and synthetic offline tests; failed validation must not write. |
| Stable identifiers | Election-scoped native geography/list codes; no timeless party/historical code guarantee. |
| Size/storage | Manageable aggregate inputs, `JSON_CONTINUE`; production process/page/headroom measurements still required during implementation. |
| Validation | Native joins, count/percentage relationships and independent totals pass; keep source exceptions explicit. |
| Refresh/history | Manual correction-driven snapshots with hashes, named maintenance owner and family/year review, not live refresh. |
| Developer use case | Concrete bounded widget/dashboards hypothesis; do not claim observed demand or all-history coverage. |

No usefulness score overrides failed rights/privacy gates. Before production, obtain and retain clarification, decide exact field/coverage/low-cell notices, assign ownership, measure deployment budgets and implement route/pagination/cache tests. Existing PortalVS rights remain separate; elections must remain viable if those reference files disappear.

## 19. Final recommendation

**GO_AFTER_LICENCE_EVIDENCE**. Real official data proves a useful, reproducible, native-geography aggregate technical model. General reusable-data terms do not yet clear election-specific acquisition/redistribution. Retain research-only state (`/v1/sources/elections`: research, coverage null, licence pending), no results route and no production election file.

## 20. Recommended next milestone

**0.23.3 — Elections Reuse & Acquisition Evidence**: the smallest evidence/outreach milestone. The maintainer sends the prepared ŠÚ SR question manually and retains the reply or equivalent authoritative election-specific terms covering the selected files and approved acquisition. Do not schedule production implementation until that gate closes; no dependency on sending the three other source emails first.

### Offline prototype validation record

Lead independently reran the final importer on the four already retrieved official inputs, with optional current-geography diagnostics and `--dry-run`. Parsed rows: territory **2,927**, results **2,927**, party results **44,272**, national control **1**. Strict UTF-8/comma profile, zero errors, no missing/orphan native joins, no write. All six national control totals match; party rows reconcile to municipal valid votes. Independent Agent B analysis additionally checked published regional/district and national per-party controls; the prototype's optional `tab01` does **not** independently validate each party against `tab03a`.

Final readable preview SHA-256: **`8aa4a5e085db78a656868d572100daeba03ef31240e889a93621a4d86f9dd561`**, size **13,460,755 bytes**. Lead local Python 3.14 dry-run **1.87 s**, repeated without PortalVS reference **2.19 s**, explicit preview-write run **2.14 s**; timing is one machine/run, not an SLA. With and without reference, preview bytes/hash are identical. Current joins: **2,926**, one foreign unmatched, **269 whitespace-normalized name mismatches** versus the **270 exact string mismatches** in raw schema research. The normalization difference is diagnostic whitespace only, not fuzzy matching or rewritten output names.

An explicit `--write-preview --output data/generated/elections_nrsr2023_preview.json` run produced the same ignored local preview. No official source file or generated dataset is committed; no production data/endpoint exists. The prototype caps each input and combined inputs at 16 MiB, rejects unexpected headers/dialect/encoding/width/identifiers, enforces count/percentage/native memberships and output field allowlists, and keeps reference failures diagnostic-only.

Synthetic tests cover strict UTF-8/BOM/CP1250 rejection, CSV quoting, headers/widths/delimiters, numeric conversion, truncation/denominators, invalid rows, duplicates, parent/name consistency, national/party totals, optional/unmatched geography, determinism, privacy exclusions, input-size limits, dry-run/CLI behavior and generated-only writes. No test accesses the internet. Full verification results are recorded in the PR; source/schema evidence includes all independent controls and bounded historical samples. No deployment performance or public release safety is claimed by an offline import measurement.

Final local gates at project version **0.23.2**: dataset validation **12 reports / 0 errors / 51 warnings** (the two additional warnings are honest elections rights/acquisition pending states), referential integrity passed, **326 pytest tests passed**, compileall passed and `git diff --check` clean. This includes **81 synthetic importer cases** and **3 spike-scope tests**, with the 242 baseline tests retained. Final independent review found and fixed malformed optional-reference names and oversized-count Decimal errors, adding fail-closed/diagnostic-only regressions; valid official preview bytes are unchanged. Local uvicorn smoke: **35/35**. Fourteen sampled existing dataset/utility responses retained exactly the same bodies, statuses and cache validators as the pre-spike baseline. Source-catalogue research addition and project version are the only intended public-visible changes; namespace `/v1` and envelope version `v1` remain unchanged.
