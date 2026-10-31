# NR SR 2023 aggregate election results — 0.23.14

**NRSR2023_PRODUCTION · JSON_CONTINUE · MANUAL_OFFICIAL_DOWNLOAD_ONLY ·
CC_BY_4_0_VERIFIED_BY_PUBLISHER_REPLY · AGGREGATE_NO_PERSON_RECORDS**

The ŠÚ SR reply received **2026-10-30** resolves reuse. The maintainer manually
downloaded the five files and confirmed this happened during the handoff on
**2026-10-31**, approximately **17:20 UTC / 18:20 CET**. This is explicitly
**approximate-minute precision**, based on the maintainer's “just now” account
and the session clock, not an invented exact download time or filesystem mtime.
All five files were freshly rehashed and match the 0.23.2 historical digests;
old research files were not substituted. Headers, UTF-8/comma/LF format and row
counts match; no source revision was found.

Non-content acquisition record (individual official URLs, bytes, SHA-256,
headers/header hashes, encoding, row counts and time precision):
[elections-nrsr2023-acquisition.json](research/elections-nrsr2023-acquisition.json).
Its `MANIFEST_PREPARED_SEMANTIC_REVIEW_REQUIRED` status describes the acquisition
stage, not production approval; subsequent full import/reconciliation is recorded
here. No source CSVs, personal machine paths or email signatures are committed.

Production artifact: **`data/elections_nrsr_2023.json`**, **1,985,346 bytes**,
SHA-256 (LF):
`dde3a904767682499b48e4e23d61f25c54db2b7d157856fd23dea34a40633f7c`.
One file contains election metadata, national totals, national parties, native
unit summaries and centralized provenance; no duplicated production lookup files.

## Manual acquisition and refresh procedure

1. Open the official NR SR 2023 **Údaje na stiahnutie** page manually:
   <https://volby.statistics.sk/nrsr/nrsr2023/sk/subory_na_stiahnutie.html>.
2. Manually download these **five CSV files**, preserving the original bytes
   and filenames (do not open/resave them in spreadsheet software):

   | File | Required role | Expected data rows |
   | --- | --- | ---: |
   | `NRSR2023_SK_tab0c.csv` | Election-native territory dictionary | 2,927 |
   | `NRSR2023_SK_tab02d.csv` | Municipality/unit aggregate summary | 2,927 |
   | `NRSR2023_SK_tab01.csv` | National aggregate reconciliation control | 1 |
   | `NRSR2023_SK_tab03a.csv` | National political-subject results and mandates | 25 |
   | `NRSR2023_SK_tab0a.csv` | Political-subject names/numbers/abbreviations | 25 |

   Save to a **private directory outside this repository**, for example
   `%LOCALAPPDATA%\Temp\opencode\elections-02314\`. Provide its location
   and the actual acquisition timestamp (with timezone and honest precision).
   The agent will not download files, infer their acquisition from filesystem
   modification times, or substitute the 0.23.2 research bytes.
3. Do **not** download candidate/preference/elected-person files, precinct
   tables or a bulk archive. `tab03e` is not required or promoted. Optional
   regional/district reconciliation controls `tab02a`/`tab02c` are not required
   for this initial handoff.
4. Run the offline manifest-preparation tool after the files are supplied:

   ```powershell
   python scripts/prepare_elections_manifest.py --source-dir <private-directory> --manually-acquired-at <actual-ISO-timestamp-with-timezone> --attest-manual-download
   ```

   This defaults to **dry-run** and prints a non-content manifest. To save a
   private candidate add `--write-manifest <private-manifest.json>`. It accepts
   only the five fixed NRSR2023 filenames, reuses the researched UTF-8/comma
   parser, verifies exact headers and row counts, and records hashes, byte
   sizes, reviewed headers and historical-hash comparison. It does **not**
   certify full semantic reconciliation or write production election JSON.
   A historical hash mismatch is reported for review, not an automatic rejection
   or proof that the publisher revised the export.
5. Review the candidate manifest and any differences, then run the explicit
   NRSR2023 production adapter (default is dry-run). Example with `$source`
   set to the private input directory:

   ```powershell
   python scripts/import_elections.py `
     --territory "$source/NRSR2023_SK_tab0c.csv" `
     --results "$source/NRSR2023_SK_tab02d.csv" `
     --national-results "$source/NRSR2023_SK_tab01.csv" `
     --party-summary "$source/NRSR2023_SK_tab03a.csv" `
     --party-list "$source/NRSR2023_SK_tab0a.csv" `
     --acquisition-manifest docs/research/elections-nrsr2023-acquisition.json `
     --verified-on 2026-10-31 --dry-run
   ```

   Use the actual verification date on refresh, not this example date. Add
   `--acquisition-time-precision approximate-minute` when preparing a manifest
   from a user-attested approximate time; never fabricate exact precision.
   Review changes before replacing the committed non-content manifest. The
   manifest writer refuses overwrites; preserve prior evidence and deliberately
   review the replacement. Production import checks file identity, raw-byte
   hashes, reviewed headers/cardinalities, native joins and count/percentage/
   national/party reconciliation. Hash drift from the historical research
   baseline requires documented source-difference review plus
   `--acknowledge-source-revision`; it is not proof of a publisher revision.
   After review, replace `--dry-run` with **`--write-production`** (fixed output
   path, atomic replacement only after complete validation). Update freshness
   and source metadata from the real snapshot, run full validation/smoke,
   inspect the diff and commit. Never automate downloading or monitoring.

The older prototype `--party-results` argument is for unapproved research
previews only. The production path explicitly rejects it, current-geography
enrichment and `--write-preview`. Production does not read `tab03e`.

No requests/httpx/curl/wget, scripted browser downloads, automated probes,
crawlers, polling or scheduled source downloads are permitted. Offline hashing
and parsing are permitted. Runtime must read local materialized JSON only.

## Production scope and identifiers

One election: **NRSR2023**, Voľby do Národnej rady Slovenskej republiky 2023,
voting date **2023-09-30**, definitive historical results (not live reporting).
The ID names this OpenSK adapter, not a universal government election standard.

- Election metadata and national totals.
- 2,927 election-native unit summaries: 2,926 domestic and **599999 / Cudzina**,
  `unitType=foreign`, hierarchy `9 / 900 / 900`. Retain its **57,856 valid
  votes** in national reconciliation; it is not a Slovak municipality and must
  not gain a current OpenSK municipality/district/region mapping.
- 25 national political-subject results, source-native party numbers as
  strings `1`–`25`, names/abbreviations, valid votes, exact decimal percentages
  and nullable mandate values. These numbers are election-scoped, not global
  party IDs. Populated mandate counts sum to 150; source blanks are not zeros.
- All territory labels/parents come from the election dictionary, not PortalVS.
  No zero result is synthesized for current-only unit 518638 / Valaškovce.

Verified reconciliation against the manually downloaded files and production:
6,014 configured / 6,013 confirmed precincts; 4,388,872 registered voters;
3,007,123 participating; 3,002,948 submitted envelopes; **2,967,896 valid
votes**, also the national party-vote sum. Prešov's excluded precinct 34 is a
documented source limitation: confirmed and configured counts must not be
forced equal.

Implemented API (three explicit stable operation IDs):

- `GET /v1/elections` — `list_elections`, actually materialized elections only.
- `GET /v1/elections/{electionId}/results` — `list_election_results`, native
  region/district/municipality exact filters combined with AND; page default
  50/max 100, stable native geography order; no match is an empty 200 page.
- `GET /v1/elections/{electionId}/parties` — `list_election_parties`, national
  results in numeric election-local party-number order, no local party cells.

Unknown elections return 404; malformed filters/page bounds return 400
`INVALID_FORMAT`; well-formed filters without matches return 200 with empty
`items`, `count=0`, `total=0`. Code filters are trimmed, case-sensitive and use
the native source widths (region 1 digit, district 3, municipality/unit 6).
Pagination is `items/count/total/limit/offset`, stable region/circuit/district/
unit-code order; counts are integers and percentages exact source strings
(two decimals, truncation). `validVotePercent` uses **participating voters**,
not submitted envelopes. `precinctCount` means configured precincts;
`confirmedPrecinctCount` need not equal it. Original proven 0.23.2 parsing and
field meanings were retained. `unitType` explicitly distinguishes foreign.
National totals are exposed in the one-item election catalogue; the party
endpoint is an unpaginated 25-item array, with nullable `seats` for 18 blanks.

```text
GET /v1/elections
GET /v1/elections/NRSR2023/results?municipalityCode=528595
GET /v1/elections/NRSR2023/results?regionCode=9&districtCode=900&municipalityCode=599999
GET /v1/elections/NRSR2023/parties
```

528595 is the actual election-native Bratislava-Staré Mesto row, not a current
PortalVS enrichment. Filtering 518638 correctly returns an empty page.
Existing `/v1`, envelope version `v1`, cache/rate-limit infrastructure and
previous 39 operation IDs remain unchanged; actual OpenAPI is **42 GETs**.
All three operations have closed typed success/error contracts and validated
examples. Static caching uses body ETags and snapshot-date Last-Modified;
the snapshot can change only through a reviewed manual refresh, not requests.

## Privacy boundaries

**Aggregate official election statistics; no voter, candidate or person-level
records are included. Small-area aggregates may still permit contextual
inference when combined with external information.**

No municipality-party cells, precinct results, candidate preferences/profiles,
elected-person lists, voter identities, commission minutes/signatures, addresses,
contacts, personal enrichment or voter-affiliation inference functionality.
The 0.23.2 finding of 16,291 positive municipality-party cells below five votes
remains a separate deferred release decision, not resolved by the licence reply.

## Licence and snapshot semantics

Publisher: **Štatistický úrad Slovenskej republiky**. Licence: **CC BY 4.0**,
confirmed directly by the publisher reply (see
[clarification](research/elections-reuse-clarification.md)). Local storage,
transformation, API redistribution and commercial downstream reuse are allowed;
automated website downloading remains prohibited.

> Zdroj: Štatistický úrad SR – výsledky príslušných volieb.
> Licencia: Creative Commons Attribution 4.0 (CC BY 4.0).
> Údaje boli ďalej spracované projektom OpenSK.

Source: the official download page above. Licence:
<https://creativecommons.org/licenses/by/4.0/>. Modifications:
CSV → JSON, normalized fields, election-native joins and the narrowed aggregate
projection. **OpenSK nie je oficiálnou službou Štatistického úradu SR.**
No endorsement is implied; MIT covers OpenSK code, not ŠÚ SR data.

Keep dates distinct:

- `electionDate`: 2023-09-30.
- `sourcePublishedAt`: the historical page stated 2023-10-01 14:30; its timezone
  was not established in the research, so do not invent an offset or treat it
  as a per-file publication timestamp.
- `manuallyAcquiredAt`: **2026-10-31T17:20:00Z, approximate-minute** as described
  above. Never derive it from source HTTP Last-Modified or local mtime.
- OpenSK `lastUpdated`: actual production snapshot acquisition/verification
  date: **2026-10-31**, `ELECTIONS_NRSR2023_LAST_UPDATED`. It is not election
  day, source publication time or email receipt.

Refresh stays manual: download approved finalized files → record provenance →
offline import → reconciliation/validation → diff review → explicit promotion.
No automatic second-election adapter, generic framework, DB, Redis or SDK.
## Storage measurements — JSON_CONTINUE

Reproduce offline: `python scripts/benchmark_elections.py --output <private-json>`.
Python 3.14.5, Windows 11, AMD64 Family 25 Model 117; five samples, median below.
These are local measurements, not a hosted/multiworker SLA or network latency.

| Measurement | Result |
| --- | ---: |
| Production JSON | 1,985,346 bytes; 2,927 units + 25 parties |
| JSON parse | 19.686 ms |
| Service cold load (including full strict validation/reconciliation) | 76.561 ms |
| Retained / peak traced load heap (separate traced run) | 8,773,674 / 10,865,287 bytes |
| Process RSS after cold load | 49,201,152 bytes (whole benchmark process, not dataset-only heap) |
| Service list / exact foreign filter | 1.750 / 1.190 ms |
| TestClient HTTP catalogue / first results page | 3.648 / 5.700 ms |
| TestClient HTTP filtered results / national parties | 4.185 / 2.317 ms |

This narrow artifact is substantially smaller than the historical 12.84 MiB
research preview that included municipality-party rows. No storage trigger
justifies DB/Redis adoption; **JSON_CONTINUE**. No SDK/new dependency added.

## Historical preparation checkpoint — before manual file handoff

Started only after PR #40 merged: updated `main` base
`0b5d3bae4a563b0149327ad04e9ff179840e468a`, version 0.23.13, clean tree;
the completed 0.23.13 feature branch has the same file tree as that base.
Work is on `feat/elections-production-surface`, version **0.23.14-dev**.

- `python scripts/validate_datasets.py`: 0 errors / 42 warnings; the two
  elections rights/acquisition-policy pending warnings are now resolved by the
  reply. This does not certify missing production inputs.
- Referential integrity, compileall and diff checks pass.
- `python -m pytest -q`: **1,105 passed**, including 18 offline manifest
  cases (manual attestation, supplied timestamp/timezone, schema/cardinality,
  excluded-table boundaries, deterministic non-content output and write guards).
- Local HTTP smoke: **41/41 passed**, server stopped afterward.
- Exact **39 GET path/method/operationId inventory unchanged**; OpenAPI refs
  resolve and existing examples validate. `/v1` and `metadata.version=v1` remain.
- All **13 non-catalogue production JSON byte hashes** match the base; only
  `data/sources.json` records the new reply. Source-catalogue freshness reflects
  this evidence update (2026-10-31); no election snapshot freshness is invented.
- No source downloads, raw CSVs, production election JSON or actual acquisition
  manifest; no new runtime upstream, DB, Redis, SDK or source polling.

This is **not PR-ready** and not `NRSR2023_PRODUCTION`. Blocker:
**MANUAL_SOURCE_FILES_REQUIRED**. No push/PR/hosted CI, merge, tag or release
is claimed for this preparation checkpoint. Once the manual inputs arrive,
complete the importer/snapshot/service/three routes, measure storage and run
full milestone validation again before promotion and PR creation.

## Final privacy red team (0.23.14)

1. **Person names?** No person-name fields or person records. Official
   political-subject labels (including surname-derived labels such as
   “Kotlebovci”) remain institutional source labels, not candidate profiles.
2. **Candidate records?** No; party-list candidate-count metadata is validated
   offline but not emitted, and no candidate tables are acquired.
3. **Precinct results?** No; only aggregate configured/confirmed precinct counts.
4. **Municipality-party cells?** No; `tab03e` is not a production input.
5. **Voter identities?** No.
6. **Contacts/addresses?** No.
7. **Voter-affiliation lookup?** No; no person query or local party-vote surface.
8. **Foreign voting?** Retained as foreign 599999/Cudzina, never a municipality.
9. **PortalVS dependency?** None; historical dictionary is authoritative.
10. **API redistribution authorized?** Yes, direct publisher reply 2026-10-30.
11. **Transformation authorized?** Yes, including CSV/XLSX → JSON/normalization.
12. **Commercial downstream reuse?** Yes, under CC BY 4.0 attribution.
13. **Automated website downloads prohibited?** Yes; no exception inferred.
14. **Downloader added?** No; manual files only, all processing offline.
15. **Attribution visible?** Yes, `/v1/sources/elections`, metadata source, docs.
16. **Non-endorsement?** Explicit in source catalogue, snapshot, docs/OpenAPI.
17. **Modifications disclosed?** Yes: selected CSV → JSON/native join/field normalization.
18. **MIT separated from data CC BY 4.0?** Explicitly; MIT covers code only.

Residual caveat: aggregate does not mean anonymous. Small-area contextual
inference remains possible with external information; no zero-risk claim or
invented suppression rule. A future local party-cell release is a separate
decision; no automatic second election is queued.

## Final contract red team (0.23.14)

1. **Old 39 operation IDs unchanged?** Yes; preserved baseline fixture and exact subset test.
2. **Exactly three new GETs?** Yes, exact paths/IDs listed above (42 total).
3. **`/v1` unchanged?** Yes.
4. **Metadata version `v1`?** Yes.
5. **Unknown election 404?** Yes, both election-specific routes.
6. **No matches 200 empty page?** Yes, including non-election unit 518638.
7. **Native IDs strings?** Yes; no lossy integer ID normalization.
8. **Party number election-scoped?** Yes, explicit in schema/docs.
9. **Percentages accurate?** Exact source strings; Decimal truncation validation.
10. **599999 reconciles?** Yes, 57,856 valid votes and native foreign hierarchy.
11. **National totals reconcile?** All six integer measures, including foreign voting.
12. **Party votes reconcile?** 25 national rows sum to 2,967,896 valid votes.
13. **Seats sum to 150?** Yes; 18 source blanks preserved as null.
14. **6,013/6,014 confirmation accepted?** Yes; Prešov 65/66 retained and documented.
15. **Runtime entirely local?** Yes; no source or current-geography calls/reads.

The geography refresh validator now recognizes this exact election artifact as
its own namespace and validates it internally, instead of interpreting native
numeric election codes as PortalVS foreign keys. Other datasets retain their
existing checks. No unrelated production JSON was modified.

## Final milestone validation — 2026-10-31

At `PROJECT_VERSION = "0.23.14"`:

- Dataset validation: **15 reports / 0 errors / 42 existing unrelated warnings**;
  elections has 2,927 validated unit records, no errors/warnings.
- Referential integrity: passed, including separate election-native validation.
- Full pytest: **1,190 passed** (0.23.13 baseline 1,087); no source network access.
- `python -m compileall scripts routers services tests schemas`: passed.
- `git diff --check`: passed.
- Local uvicorn HTTP smoke: **46/46 passed**, including discovery, both result
  routes, domestic unit 528595 and foreign unit 599999; server stopped afterward.
- Actual OpenAPI: **42 GET operations**, exact prior 39 path/method/operationId
  inventory retained; only `list_elections`, `list_election_results`,
  `list_election_parties` added. All references resolve and examples validate
  against the typed models. `/v1` and metadata version `v1` unchanged.
- Production files: only new `data/elections_nrsr_2023.json` and updated
  `data/sources.json`; all **13** other production JSON files are byte-identical
  to main base `0b5d3bae4a563b0149327ad04e9ff179840e468a`, including holidays
  and the 100-record procurement snapshot. No raw CSVs in Git.
- No automated source downloader, runtime upstream dependency, DB, Redis, SDK,
  outreach, tag or release. Hosted CI is reported on the PR, not inferred from
  these local checks; no auto-merge.

Verdicts: **NRSR2023_PRODUCTION**, **JSON_CONTINUE**,
**MANUAL_OFFICIAL_DOWNLOAD_ONLY**, **CC_BY_4_0_VERIFIED_BY_PUBLISHER_REPLY**,
**AGGREGATE_NO_PERSON_RECORDS** with the residual small-area caveat.
Next: maintainer-run **5–10 external-developer pilot**, no automatically queued
second election or data-domain milestone.
