# 0.23.16-dev — ŠÚ SR Geography Reconciliation & Rights Escalation

## Current result: blocked acquisition, not a technical verdict

**`MANUAL_SOURCE_FILES_REQUIRED`**. No exact official LSUJ1/0024 or LSUJ2/0025
CSV/XML has been supplied. Actual source hashes, schema, row counts, special-row
counts, relationship differences and remaining PortalVS dependencies are
**unknown**, not zero. `technicalVerdict` is **null**. Neither synthetic examples,
the catalogue page nor the generic format PDF establish real reproduction of
the **79 districts / 2,927 municipalities**. The version stays **`0.23.16-dev`**;
this draft does not claim successful milestone completion.

Source identity is confirmed by the [reply received 2026-11-20](susr-geography-clarification.md).
Separately, **`GENERAL_SUSR_TERMS_SUPPORT_CC_BY_4_0`** is supporting evidence;
**`CLASSIFIER_SPECIFIC_APPLICABILITY_PENDING`** and **`RIGHTS_CONFIRMATION_PENDING`**
remain. The responding unit explicitly declined questions 2–6. Follow-up was
manually sent **2026-11-27** in the existing thread, **`SENT_AWAITING_REPLY`**;
competent-unit routing is unverified. [Rights analysis](susr-geography-rights.md).

Production remains the PortalVS snapshot; no source, licence or freshness upgrade
and no geography/PSC promotion. All 14 other served JSON datasets are protected;
only district/municipality evidence in `data/sources.json` changes. No runtime
upstream, route, SDK, DB or Redis is introduced. PSC remains
**`NO_GO_SUCCESSOR_PSC`**, independent of geography.

## Manual handoff and observation

1. The maintainer manually opens the [official catalogue](https://zber.statistics.sk/metaudaje/ciselniky),
   searches **0024 / LSUJ1** and **0025 / LSUJ2**, verifies the official titles,
   and downloads CSV. Optional XML may clarify metadata; it is not yet parsed by
   this tool. No requests/httpx/curl/wget/PowerShell download, browser automation,
   scraper, cached web substitute or PortalVS substitute is permitted.
2. Keep exact bytes in a private directory **outside the repository**. Record the
   genuine acquisition date/time, precision and timezone if known; exact download
   URL if observed; source version/validity/metadata date if present. Do not use
   filesystem mtime, inspection time or guessed precision as acquisition time.
3. Run local observation, replacing the relative placeholders with private paths:

   ```powershell
   python scripts/reconcile_susr_geography.py --inspect-files --districts-file PRIVATE/0024.csv --municipalities-file PRIVATE/0025.csv --delimiter ";"
   ```

   Observation prints only non-content file metadata and leaves acquisition
   claims/timestamps null. Exit **2** is expected: it is not reconciliation or
   profile approval. Comma is also supported explicitly. No file is written by
   default; no network is used. Do not commit terminal output containing private
   paths or unreviewed source metadata.
4. Review the actual header/dialect/validity and coded parent semantics. The
   generic official PDF documents an attribute vocabulary, **not these CSVs' exact
   schema**. The provisional profile requires `code`, `officialTitle`, `validFrom`,
   strict UTF-8 with correctly recorded optional BOM and comma/semicolon. It
   rejects unknown columns, duplicate codes, row-width drift and invalid dates.
   A mismatch means **stop and adapt the reviewed profile/tests**, not strip an
   unknown field, guess an encoding or pretend that the source is unusable.
5. Only after genuine manual origin/schema review, fill the non-content
   [acquisition manifest](susr-geography-acquisition.json): every required file
   field, real bytes/SHA-256/encoding/delimiter/rowCount/headers/headerSha256,
   actual acquisition metadata and reviewed transformation/relationship evidence.
   Unknown version/validity/date/download URL may be null, not invented. Never
   put local paths or raw rows in the manifest. Header hash is SHA-256 of the
   compact UTF-8 JSON header array, preserving spelling and order.
6. Reviewed states are `acquisitionStatus: MANUAL_FILES_SUPPLIED`,
   `sourceProfileStatus: REVIEWED_MANUAL_FILES`; each transformation profile uses
   `id: susr-geography-csv-v1`, `reviewStatus: REVIEWED_MANUAL_SOURCE`, an explicitly
   selected source name field and reviewed transforms. These are human evidence
   assertions, not permissions or publisher signatures.

The tool currently supports parent relationships only when an actual retained
source field has verified coded semantics (`DIRECT_SOURCE_CODE_FIELD`, field,
official evidence URL, description, `verified: true`). Generic `info`/`additionalInfo`
are **not assumed** to be relationship columns. Absent evidence leaves candidate
fields null. If the source instead needs a documented hierarchy or another
cleared source, extend and test that explicit evidence profile; do not fill
candidate parents from production or names. Such extensions are not implemented
or established by this blocked draft.

## Reconciliation and review policy

```powershell
python scripts/reconcile_susr_geography.py --districts-file PRIVATE/0024.csv --municipalities-file PRIVATE/0025.csv
python scripts/reconcile_susr_geography.py --districts-file PRIVATE/0024.csv --municipalities-file PRIVATE/0025.csv --write-diagnostics
```

Dry-run is the default. The second command writes only ignored
`data/generated/susr-geography-reconciliation.json`; it cannot promote production.
Generated diagnostics retain source attributes locally and must not be committed
as a raw dump. Without files, `--write-diagnostics` can record the honest blocked
status with null result counts. Exit codes: **0** full candidate reproduction,
**1** partial/no-go comparison, **2** missing evidence, review needed or input error.
Rights remain pending even on exit 0.

- Codes remain strings; municipality identity joins only on original six-digit
  code. Duplicate names are allowed. No fuzzy/name-only identity inference.
- `SOURCE_NAME`, `OPEN_SK_DISPLAY_NAME`, candidate fields and actual production
  values remain distinct. Every compared field is classified as `DIRECT_SUSR`,
  `DETERMINISTIC_DERIVATION_FROM_SUSR`, `OPEN_SK_COMPATIBILITY_VALUE`,
  `OTHER_VERIFIED_SOURCE` (reserved for an evidenced future profile), or
  `PORTALVS_ONLY` (not independently reproduced in this comparison).
- The provisional district formatter maps a three-digit source code's first
  digit to the explicit OpenSK region namespace and decimal suffix. This is an
  **OpenSK compatibility transform**, not a confirmed source-code hierarchy or
  authoritative relationship. Capture loading requires a reviewed
  `districtIdDerivation` with id `opensk-district-namespace-v1`, `verified: true`,
  official evidence URL and description. It must be checked against genuine codes and
  independent coded parents before real readiness is accepted. Its synthetic
  success does not prove PortalVS-free reproduction of official identifiers.
- All 12 historical/public ID pairs are explicitly audited:

  | Historical aliases | Current public IDs |
  | --- | --- |
  | `SK031A`, `SK031B` | `SK03110`, `SK03111` |
  | `SK032A`, `SK032B`, `SK032C`, `SK032D` | `SK03210`, `SK03211`, `SK03212`, `SK03213` |
  | `SK041A`, `SK041B`, `SK041C`, `SK041D` | `SK04110`, `SK04111`, `SK04112`, `SK04113` |
  | `SK042A`, `SK042B` | `SK04210`, `SK04211` |

- For duplicate source names within the represented production surface, the
  candidate formatter adds ` (okres DISTRICT)` from candidate source-derived
  parents, never the production parent. All **205** current suffixes must be
  checked, not assumed reproduced. Codes **504173 / 504742** are separately
  exposed for review; no hardcoded name override asserts that they already match.
- All source rows/attributes are retained in local diagnostics. Source-only rows
  need `FOREIGN_PSEUDO`, `TECHNICAL`, `INACTIVE`, `OUT_OF_SCOPE`,
  `MISSING_FROM_OPEN_SK` or `OTHER`, with reviewed reasons and retained evidence
  fields. Unreviewed source-only rows block the verdict. Explicit validity may
  establish an inactive row as of acquisition; no silent filtering to force counts.
- Current special-unit presence is audited by codes: **17 Bratislava boroughs**,
  **22 Košice boroughs**, military units **500267**, **518581**, **518638**
  (Valaškovce). Actual official special attributes/extra units remain uninspected.
- Diagnostics include source/matched/unmatched/conflict counts, per-field
  differences, displays, relationships, compatibility categories and unreproduced
  fields. The remaining-dependency counter counts unresolved fields plus missing
  records; it does not measure legal provenance of unchanged production bytes.
- No `0024 ↔ CL000024` or `0025 ↔ CL000025` crosswalk is newly asserted from the
  reply; older MetaIS findings remain historical unless directly reverified.

## Completion gates

With genuine reviewed files, select exactly one final technical verdict:

- **`SUSR_TECHNICAL_FULL_REPLACEMENT_READY`**: all 79/2,927 current records/fields
  reproduced, all special rows classified, all 12 IDs/205 displays/corrections
  checked and zero material unresolved PortalVS dependency.
- **`SUSR_TECHNICAL_PARTIAL_REPLACEMENT_READY`**: substantial reproduction with
  specific unresolved fields/parents/identifiers. Review the actual extent;
  the tool's preliminary partial label is not proof of substantial coverage.
- **`NO_GO_SUSR_TECHNICAL_REPLACEMENT`**: inspected source semantics cannot
  deterministically reproduce the surface; record the exact blocker.

Do not select any of these merely because files are missing. Lock real aggregate
invariants only after actual reconciliation, rerun validators/full tests/smoke and
raw-byte safety checks, then finalize `0.23.16` if the milestone is complete.
Even a full technical result leaves production **`RIGHTS_CONFIRMATION_PENDING`**.
Only exact-classifier rights confirmation can trigger consideration of a separate
small migration; none is queued automatically. If technically unsuitable, park
the exact blocker. The external-developer pilot is independent.

## Red team — explicit answers at this checkpoint

| # | Question | Answer |
| --- | --- | --- |
| 1 | ŠÚ SR directly confirmed LSUJ1/0024? | **Yes**, maintainer-supplied reply received 2026-11-20. |
| 2 | Directly confirmed LSUJ2/0025? | **Yes**, same reply. |
| 3 | Explicit CC BY 4.0 applicability to exact files? | **No**; declined competence, specialist determination pending. |
| 4 | Explicit transformation authorization? | **No**, not in this reply. |
| 5 | Explicit commercial reuse authorization? | **No**, not for exact classifiers in this reply. |
| 6 | Explicit automated-acquisition authorization? | **No**; milestone remains manual only. |
| 7 | General terms distinguished from classifier confirmation? | **Yes**, separate supporting-evidence and applicability states. |
| 8 | Current 2026-10-13 wording accurately retained? | **Yes**, rechecked 2026-11-27, including qualified automation restriction. |
| 9 | Exact source files manually supplied? | **No**: `MANUAL_SOURCE_FILES_REQUIRED`. |
| 10 | Raw source files kept out of Git? | **Yes**; none supplied or committed; private inputs only. |
| 11 | Municipality joins code-based? | **Yes** in tooling; actual-file join not yet executed. |
| 12 | Duplicate names without fuzzy identity inference? | **Yes** in synthetic safeguards; names are presentation only. |
| 13 | Special records retained/classified? | Tool retains every row and gates unreviewed extras; **actual rows not inspected**. |
| 14 | All 79 districts reproducible? | **Unknown**, no manual files. |
| 15 | All 2,927 municipalities reproducible? | **Unknown**, no manual files. |
| 16 | District IDs generated without PortalVS? | **Not established**; provisional compatibility formatter is not actual-source proof. |
| 17 | Municipality→district without PortalVS? | **Not established**; verified coded source relationship required. |
| 18 | District→region without PortalVS? | **Not established**; verified field/hierarchy evidence required. |
| 19 | OpenSK display suffixes distinct from source names? | **Yes**; 205 baseline suffixes, never represented as ŠÚ SR source text. |
| 20 | Any material field still requires PortalVS? | Current production is PortalVS-derived; independent candidate dependency count **unknown**, not zero. |
| 21 | Production geography unchanged? | **Yes**, protected hashes; no promotion. |
| 22 | PSC unchanged? | **Yes**, bytes/freshness/source and `NO_GO_SUCCESSOR_PSC` preserved. |
| 23 | Exactly 42 GET operations? | **Yes**, inventory guarded. |
| 24 | All operation IDs unchanged? | **Yes**, exact baseline inventory guarded. |
| 25 | `/v1` unchanged? | **Yes**, no router/runtime changes. |
| 26 | `metadata.version` still `v1`? | **Yes**, response checks retained. |
| 27 | Agent sent any email? | **NO**. Only maintainer-confirmed dispatch is recorded. |

## Validation evidence boundary

Synthetic tests establish parser/join/write/no-network safeguards only. They are
not official captures, rights evidence or a real technical replacement verdict.
The acquisition manifest pins the pre-work protected LF hashes and operation
inventory; an additional private pre-work record permits exact working-tree-byte
comparison independently of Windows/Linux checkout line endings. Source-registry
fixture changes must be limited to the two intentional evidence updates. Local
validation and CI results are reported in the PR; no CI success is inferred before
it runs. No merge, tag or release is authorized.

Local checkpoint **2026-11-27**, Python **3.14.5**:

- Dataset validation: **15 datasets, zero errors**, 35 retained compliance/coverage
  warnings; referential integrity passed.
- Full pytest: **1,548 passed**; focused reconciliation/evidence/ownership tests:
  **55 passed**. These do not establish actual classifier reproduction.
- Local uvicorn HTTP smoke: **46 passed, zero failed**; server stopped afterward.
- Ruff, compilation, changed Markdown local-link targets and whitespace: passed.
- All **14 protected raw-byte hashes** and the exact **42-operation inventory**
  match the pre-work baseline. Registry delta is only `lastChecked`, `nextAction`,
  `notes` for districts/municipalities. Preserved 0.23.15 record matches the base
  exactly. No public-response digest fixture needed updating.

GitHub CI is a separate check; local success is not a claim that remote CI ran or
passed, nor grounds for clearing the manual-input or rights gates.
