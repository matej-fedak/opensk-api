# Elections — manual acquisition handoff (0.23.14 in progress)

**MANUAL_SOURCE_FILES_REQUIRED.** No election results are served yet. The
licence gate is resolved by the ŠÚ SR reply received **2026-10-30**, but the
production input gate is not. Project version remains `0.23.14-dev`.

## What the maintainer needs to do

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
   and the actual acquisition timestamp (with timezone) when resuming work.
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
5. Resume the implementation: inspect any differences, finish the national
   party adapter and full reconciliation, review the non-content acquisition
   manifest for commit at `docs/research/elections-nrsr2023-acquisition.json`,
   then validate and explicitly promote the complete materialized snapshot.
   The manifest does not exist yet: there are no actual acquisition facts to
   record. No guessed timestamp, hash or manual-acquisition claim is committed.

No requests/httpx/curl/wget, scripted browser downloads, automated probes,
crawlers, polling or scheduled source downloads are permitted. Offline hashing
and parsing are permitted. Runtime must read local materialized JSON only.

## Approved scope to implement after the input gate

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

Expected reconciliation (not yet checked against manual production inputs):
6,014 configured / 6,013 confirmed precincts; 4,388,872 registered voters;
3,007,123 participating; 3,002,948 submitted envelopes; **2,967,896 valid
votes**, also the national party-vote sum. Prešov's excluded precinct 34 is a
documented source limitation: confirmed and configured counts must not be
forced equal.

Proposed API (not registered at this checkpoint):

- `GET /v1/elections` — `list_elections`, actually materialized elections only.
- `GET /v1/elections/{electionId}/results` — `list_election_results`, native
  region/district/municipality exact filters combined with AND; page default
  50/max 100, stable native geography order; no match is an empty 200 page.
- `GET /v1/elections/{electionId}/parties` — `list_election_parties`, national
  results in numeric election-local party-number order, no local party cells.

Unknown elections return 404 after implementation. Existing `/v1`, envelope
version `v1`, cache/rate-limit infrastructure and previous 39 operation IDs
remain unchanged; successful completion will add exactly three GET operations.

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
<https://creativecommons.org/licenses/by/4.0/>. Planned modifications:
CSV → JSON, normalized fields, election-native joins and the narrowed aggregate
projection. **OpenSK nie je oficiálnou službou Štatistického úradu SR.**
No endorsement is implied; MIT covers OpenSK code, not ŠÚ SR data.

Keep dates distinct:

- `electionDate`: 2023-09-30.
- `sourcePublishedAt`: the historical page stated 2023-10-01 14:30; its timezone
  was not established in the research, so do not invent an offset or treat it
  as a per-file publication timestamp.
- `manuallyAcquiredAt`: actual maintainer-attested download timestamp, not
  supplied yet. Never derive it from source HTTP Last-Modified or local mtime.
- OpenSK `lastUpdated`: actual production snapshot acquisition/verification
  date, to be set only on promotion, not to election day or email receipt.

Refresh stays manual: download approved finalized files → record provenance →
offline import → reconciliation/validation → diff review → explicit promotion.
No automatic second-election adapter, generic framework, DB, Redis or SDK.
Production storage measurements and final `JSON_CONTINUE` verdict await real
inputs; the older research measurements are not a production benchmark.

## Preparation checkpoint validation — 2026-10-31

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
