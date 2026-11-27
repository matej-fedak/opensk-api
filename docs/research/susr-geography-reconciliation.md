# 0.23.16 — ŠÚ SR Geography Reconciliation & Rights Escalation

**Technical verdict: `SUSR_TECHNICAL_FULL_REPLACEMENT_READY`.** Both manually
acquired captures reproduce every field of all **79 districts and 2,927
municipalities**, with zero material PortalVS dependency for rebuilding that
surface. This is snapshot-scoped technical evidence, not a migration decision.

**Production gate: `RIGHTS_CONFIRMATION_PENDING`.** The [2026-11-20 reply](susr-geography-clarification.md)
confirms LSUJ1/0024 and LSUJ2/0025, but the responding unit declined to decide
questions 2–6. General terms updated **2026-10-13**, rechecked **2026-11-27**, support
CC BY 4.0; **`CLASSIFIER_SPECIFIC_APPLICABILITY_PENDING`** remains. The maintainer
sent the follow-up **2026-11-27** in the existing thread: `SENT_AWAITING_REPLY`;
competent-unit routing is unverified. See the [rights review](susr-geography-rights.md).

## Manual capture and verification

The maintainer supplied the original official catalogue downloads, confirmed
**2026-11-27**, day precision only. No time of day, exact download URL, publisher
signature or export version was supplied. The files do not embed classifier
numbers; identity is based on the direct institutional reply, the maintainer's
catalogue handoff, and consistency of the two files' distinct coded content.
No new `CL000024`/`CL000025` crosswalk is asserted. Nothing was downloaded by the
tool or substituted for the captures. The earlier missing-file checkpoint is in
branch history.

| Capture | Bytes | SHA-256 | Data rows |
| --- | ---: | --- | ---: |
| LSUJ1 / 0024 | 16,123 | `8de949f0b3a5cf3981a4459bbf40c6ae93d3c890376e689054c8aa177f70a3fe` | 81 |
| LSUJ2 / 0025 | 564,546 | `ef5be6d9dccfdc24e2c0cf50790818344fe3118b3cf2763be5bae430b1a664bf` | 2,930 |

Both are UTF-8 without BOM, comma-delimited, LF, with the same 25-column header
and `DD.MM.YYYY` date fields. Exact order and header hash are in the [manifest](susr-geography-acquisition.json).
The reviewed profile rejects header/dialect drift, duplicate published codes,
invalid dates, reversal of validity/metadata dates and checksum mismatch.
Earliest `validFrom` is **2004-08-01** for both; `validTo` is populated on **1 / 2**
rows respectively. All `dateModified` values are **2019-12-27**: a row metadata
date, not acquisition, an export version, or evidence of freshness in 2026.
Open-ended validity is interpreted as published, not a guarantee of legal or
administrative currency outside this comparison. The generic format PDF did not
establish the actual header; the two captures did.

## Rebuild from official codes, then compare

- **Districts (LSUJ1):** preserve original string `code` and three-digit
  numeric `note`. Keep the 67 already decimal public codes; convert the last
  `A`–`D` to `10`–`13` for the 12 OpenSK compatibility IDs. Every domestic row is
  independently checked against its numeric `note`, including the region
  digit. E.g. `SK031A` / `510` → `SK03110`. The complete mappings are `SK031A/B`
  → `SK03110/11`, `SK032A–D` → `SK03210–13`, `SK041A–D` → `SK04110–13`, and
  `SK042A/B` → `SK04210/11`. Strip literal `Okres ` from `officialTitle` and
  verify equality to `mediumTitle` on all 79 records. The source text is preserved.
- **Municipalities (LSUJ2):** preserve full published `code`, take the original
  six-digit `note` as the public code (verified to be the exact suffix), and
  strip that suffix for an exact join to the published LSUJ1 `code`. No separate
  parent column; do not interpret `info`/`additionalInfo` as one. Normalize
  whitespace in `officialTitle`, then add ` (okres DISTRICT)` only for repeated
  names among active domestic rows. There are **95** duplicate-title groups
  covering **205** displays. Both corrections, **504173** (Vozokany, Galanta)
  and **504742** (Radošovce, Skalica), reproduce through the rule, without manual
  overrides or name-based identity inference.
- **Regions and parent links:** the first five characters of the district code
  identify one of the eight region codes; municipalities inherit the region
  through the exact district join. The [official ŠÚ SR 2019 coded table](https://volby.statistics.sk/opendata/eup/2019/EP_2019_SK_tab0c.csv)
  shows separate RŠÚJ3, LŠÚJ1, LŠÚJ2 and numeric IDs, corroborating their roles
  (e.g. `SK010` → `SK0101` → `SK0101528595`, numeric `528595`). It is a semantic
  cross-check, not a replacement input or current coverage claim. All domestic
  code decompositions, district references, eight region codes and transformed
  fields were checked against the actual captures and the served surface. These
  links are **OpenSK deterministic derivations from official codes**, not separate
  authoritative relationships. **559** municipality parent IDs receive the
  decimal compatibility transform. `country: SK` is the OpenSK domestic constant.

The build does not read baseline records to fill candidates or determine duplicate
names; the baseline is used only for comparison. `SOURCE_NAME` remains separate
from `OPEN_SK_DISPLAY_NAME`. Source-derived values, deterministic derived links,
and OpenSK compatibility/presentation values are classified separately.

## Exhaustive results

| Measure | Districts | Municipalities |
| --- | ---: | ---: |
| Source rows | 81 | 2,930 |
| Full current record matches | 79 | 2,927 |
| Unmatched current records / conflicts | 0 / 0 | 0 / 0 |
| Raw official title vs public name differences | 79 | 205 |
| Explained by presentation transform | 79 | 205 |
| Remaining name-only / relationship differences | 0 / 0 | 0 / 0 |
| Material PortalVS-only dependencies | 0 | 0 |

All **17 Bratislava** and **22 Košice** boroughs reproduce with their full
official titles, as do military units **500267**, **518581**, and **518638**
(Valaškovce). All **five source-only rows** remain in local diagnostics:

| Capture | Published code | Classification | Evidence |
| --- | --- | --- | --- |
| LSUJ1 | `SKZZZ` | `FOREIGN_PSEUDO` | Foreign title, blank numeric note; ended 2014-09-22. |
| LSUJ1 | `SKZZZZ` | `FOREIGN_PSEUDO` | Successor foreign code, blank numeric note; open-ended since 2014-09-23. |
| LSUJ2 | `SKZZZZ` | `FOREIGN_PSEUDO` | Foreign title, blank numeric note; ended 2014-09-22. |
| LSUJ2 | `SKZZZZZZZZZZ` | `FOREIGN_PSEUDO` | Successor foreign code, blank numeric note; open-ended since 2014-09-23. |
| LSUJ2 | `SK0413523551` | `INACTIVE` | Javorina military unit, numeric `523551`; ended 2010-12-31. |

No active domestic row was dropped or filled from PortalVS. Source rows and
original attributes are kept out of Git. Unknown future active source-only rows
block a verdict pending review.

## Reproduce offline

Manually acquire the identified exports from the [official catalogue](https://zber.statistics.sk/metaudaje/ciselniky)
and keep the original bytes outside the repository. No automated downloads,
browser automation, cached replacements or PortalVS substitute. For these exact
captures (replace placeholders with private paths):

```powershell
python scripts/reconcile_susr_geography.py --inspect-files --districts-file PRIVATE/LSUJ1.csv --municipalities-file PRIVATE/LSUJ2.csv --delimiter ','
python scripts/reconcile_susr_geography.py --districts-file PRIVATE/LSUJ1.csv --municipalities-file PRIVATE/LSUJ2.csv --write-diagnostics
```

Inspection is observation only (exit 2), never a manual-origin attestation.
Comparison is dry-run by default; `--write-diagnostics` writes only ignored
`data/generated/susr-geography-reconciliation.json`. Detailed stdout and the
report contain source attributes; keep them private. Missing files or schema
drift block execution, not a technical no-go. Fresh files require fresh review
and manifest metadata; do not edit hashes to bypass review. No production mode.

## Production and remaining blockers

Production is still the PortalVS-derived local snapshot with unchanged source,
freshness and licence posture. All served dataset bytes and 42 GET operations,
operation IDs, `/v1` and `metadata.version: v1` are preserved by the reconciliation.
Only the district and municipality evidence in the internal source registry
differs from the pre-milestone base. The registry records the completed technical
comparison and the pending rights escalation, not a change of production source.
PSC is separate, unchanged and `NO_GO_SUCCESSOR_PSC`. No runtime upstream.

The remaining production blocker is **exact-classifier rights applicability**
(including transformation, commercial use, attribution and acquisition).
A favourable specialist response or equivalent authoritative evidence would
only trigger consideration of a separate migration, not automatic promotion.
Exact capture URL/version remain unknown; later exports need renewed verification.

## Validation — 2026-11-27

- The two original byte hashes matched on re-read. Repeated offline runs
  produced identical reports. An independent check using the numeric district
  note and `mediumTitle` also reproduced both complete served record sets.
- **1,561 pytest tests passed** locally, including the opt-in exact-capture test
  (`OPENSK_LSUJ1_CSV` and `OPENSK_LSUJ2_CSV`). Without those private inputs, CI
  skips that test and exercises the reviewed profile with synthetic fixtures.
- **46 local HTTP smoke checks passed**. Dataset validation passed with zero
  errors and 35 retained warnings; referential integrity, documentation links,
  lint, compilation and whitespace checks passed.
- All 14 production dataset files matched the raw-byte pre-milestone baseline.
  Only the district and municipality evidence in the source registry differs;
  the public source catalogue responses are unchanged.
  The operation inventory matched the exact pre-milestone 42 GET tuples.

## Red team

| # | Question | Answer |
| --- | --- | --- |
| 1 | ŠÚ SR confirmed LSUJ1/0024? | Yes, 2026-11-20 reply. |
| 2 | Confirmed LSUJ2/0025? | Yes, same reply. |
| 3 | Confirmed exact-file CC BY 4.0? | No. |
| 4 | Authorized transformation? | No, not in that reply. |
| 5 | Authorized commercial reuse? | No, not for these files in that reply. |
| 6 | Authorized automated acquisition? | No; manual only here. |
| 7 | General terms distinguished from exact-file rights? | Yes. |
| 8 | Current 2026-10-13 wording retained? | Yes, including the load/stability/availability qualification. |
| 9 | Exact files supplied manually? | Yes, 2026-11-27, day precision. |
| 10 | Raw files out of Git? | Yes. |
| 11 | Municipality joins code-based? | Yes, exact six-digit note and coded district reference. |
| 12 | Duplicate names without fuzzy identity inference? | Yes, names only drive display formatting. |
| 13 | Special rows retained/classified? | Yes, five source-only rows classified, all 42 served borough/military records reproduced. |
| 14 | All 79 districts reproducible? | Yes, all fields match. |
| 15 | All 2,927 municipalities reproducible? | Yes, all fields match. |
| 16 | District IDs without PortalVS? | Yes, 67 direct plus 12 deterministic compatibility IDs. |
| 17 | Municipality→district without PortalVS? | Yes, checked prefix join. |
| 18 | District→region without PortalVS? | Yes, checked region prefix. |
| 19 | Display suffixes distinct from source text? | Yes, all 205 reproduced as OpenSK display changes. |
| 20 | Material PortalVS dependency for reproduction? | None; existing bytes are still PortalVS-derived. |
| 21 | Production geography unchanged? | Yes. |
| 22 | PSC unchanged? | Yes, still frozen. |
| 23 | 42 GET operations? | Yes. |
| 24 | Exact operation IDs unchanged? | Yes. |
| 25 | `/v1` unchanged? | Yes. |
| 26 | `metadata.version` still `v1`? | Yes. |
| 27 | Agent sent any email? | **NO**. |
