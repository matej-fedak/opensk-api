# 0.23.10 — PortalVS Successor Geography Migration

**Districts + municipalities only. PSC is unchanged, legacy-backed and frozen.**
Technical source migration is not licence clearance; public promotion remains gated.

## Scope and acquisition

Base: main **0.23.9**, PR #36, `33ed94c53b7f07e89cb0fd944413c996d0a0870b`.
Branch: `data/portalvs-successor-geography`. Fresh manual acquisition completed
**2026-10-16T08:04:45Z**, not reused 0.23.9 raw. New raw resides privately at
`C:\Users\matej\AppData\Local\Temp\opencode\portalvs-02310\capture\`.
Only two requests were acquired; **no PSC source was requested**.

Committed non-content manifest:
[`portalvs-successor-geography-acquisition.json`](portalvs-successor-geography-acquisition.json).
Profile `portalvs-successor-geography-acquisition-v1`; canonical manifest SHA-256
`24fc83e400fce0cffda4fcae44607c1bf5785519e59966f6af00380f900ce224`.
OpenAPI reference: https://ciselniky2.portalvs.sk/api/docs.json.

| Dataset / exact URL | HTTP / Content-Type | Bytes / rows | ETag | SHA-256 |
| --- | --- | --- | --- | --- |
| Districts: https://ciselniky2.portalvs.sk/api/county.json?validity=valid | 200 / application/json; charset=utf-8 | 30,459 / 80 | `"10ce57242fccfa16"` | `308d1b35a2bbd7a82fa99966a8cac4d044fd62aa19ae249db36d864179d36194` |
| Municipalities: https://ciselniky2.portalvs.sk/api/town.json?validity=valid | 200 / application/json; charset=utf-8 | 1,105,510 / 2,928 | `"a4aeef064766d663"` | `5e13f5162f560d9d4409d91aad26569e7fe21f8342b78fc25179a0574630ad94` |

Per-response UTC times: county **08:04:42Z**, town **08:04:44Z**. Content hashes
still match the prior research observation, but these are **new responses** with
new acquisition provenance. Schema keys are recorded in the manifest; unknown
keys, missing reviewed keys or invalid types fail closed. `validTo` is the only
reviewed sparse extra key and cannot admit a retired row into this current-valid
profile. No record arrays, streets or personal workbook metadata are committed.

## Source transformations and reviewed differences

All output records are recomputed **exclusively from successor county/town**;
previous checked-in geography is used only for drift review, never fallback.
Regions remain the existing eight-region dataset, not rematerialized.

**Districts:** 80 valid rows minus the explicit `SKZZZZ` / empty note /
`Zahraničie` pseudo row = **79**. Three-digit statistical note determines region
and ordinal; successor code, `officialTitle == "Okres " + mediumTitle`, short
title and region must agree. Names come from `mediumTitle`. Duplicate identities,
unknown codes or unexpected name/relationship differences stop production writes.

| Successor | Statistical note | Unchanged public ID | Name |
| --- | --- | --- | --- |
| SK031A | 510 | SK03110 | Tvrdošín |
| SK031B | 511 | SK03111 | Žilina |
| SK032A | 610 | SK03210 | Veľký Krtíš |
| SK032B | 611 | SK03211 | Zvolen |
| SK032C | 612 | SK03212 | Žarnovica |
| SK032D | 613 | SK03213 | Žiar nad Hronom |
| SK041A | 710 | SK04110 | Stará Ľubovňa |
| SK041B | 711 | SK04111 | Stropkov |
| SK041C | 712 | SK04112 | Svidník |
| SK041D | 713 | SK04113 | Vranov nad Topľou |
| SK042A | 810 | SK04210 | Spišská Nová Ves |
| SK042B | 811 | SK04211 | Trebišov |

This is evidence validation of decimal ordinals versus A–D source suffixes,
**not a blind name/alias table**. Public records retain code/name/regionCode/country.
Old/new diff: **79 → 79**, no added/removed IDs, **zero record/name/region changes**.
Only source/freshness/acquisition metadata changes.

**Municipalities:** 2,928 valid rows minus explicit `SKZZZZZZZZZZ` / empty note /
`Zahraničie` = **2,927**. The six-digit statistical `note` must equal the composite
code suffix; its six-character district prefix must resolve in fresh county
evidence. Region derives from that district. No fuzzy, name-based district or
legacy joins. Retired/history filtering is upstream via `validity=valid`; any
retired/future row unexpectedly included fails rather than silently dropping it.

Recompute names from `officialTitle`. Exactly **205** duplicate-name records get
` (okres <district mediumTitle>)`. Unique names stay plain. Old/new diff:
**2,927 → 2,927**, no added/removed IDs, no district/region/country changes,
**2,925 records unchanged**, exactly two approved presentation corrections:

| ID | Before | After | Reason |
| --- | --- | --- | --- |
| 504173 | `Vozokany (okres (Galanta)` | `Vozokany (okres Galanta)` | Fix malformed OpenSK suffix parenthesis |
| 504742 | `Radošovce (Skalica)` | `Radošovce (okres Skalica)` | Standardize the existing exceptional suffix |

These are not municipality renames/identity changes. No other presentation change
was observed. Importer allows those exact before/after pairs (or an idempotent
refresh with no difference), not a general override flag. Any new source-driven
difference requires a separate reviewed code/policy change before writing.

## Offline refresh and replacement safety

Acquire a **new** private snapshot (after reviewing current terms/access), then
use the non-content manifest from that capture or its committed copy:

```powershell
python scripts/acquire_portalvs_successor.py --geography-only --output-dir "C:\Users\matej\AppData\Local\Temp\opencode\portalvs-new-geography"
python scripts/import_portalvs_geography.py --manifest "C:\Users\matej\AppData\Local\Temp\opencode\portalvs-new-geography\manifest.json" --capture-dir "C:\Users\matej\AppData\Local\Temp\opencode\portalvs-new-geography"
# Review the dry-run report and stop API/readers before replacement:
python scripts/import_portalvs_geography.py --manifest "C:\Users\matej\AppData\Local\Temp\opencode\portalvs-new-geography\manifest.json" --capture-dir "C:\Users\matej\AppData\Local\Temp\opencode\portalvs-new-geography" --write-production
```

Importer `scripts/import_portalvs_geography.py` is **offline only**, default dry
run (also accepts explicit `--dry-run`). Exactly geography-only profile + two
fixed URLs required; PSC/all-source profiles are rejected. It verifies manifest
checksum, UTC acquisition window, HTTP/type evidence, filenames, sizes, SHA-256,
counts and schema keys. Checksums ensure local capture integrity, not an official
cryptographic source signature. No network path or legacy fallback is invoked.

Both candidates are serialized deterministically and staged with **all current
production JSON**. Full dataset validators + referential integrity + recursive
named geography-reference checks across all JSON must pass. Production counts
79/2,927 and current identity/relationship sets must reconcile. No bypass flag.
Before writing it also checks that production context bytes have not changed
during staging, preserving concurrent maintainer edits rather than overwriting
them. Fixed production destinations are **only** `data/districts.json` and
`data/municipalities.json`; no arbitrary output/PSC/registry write option exists.

Replacement uses same-filesystem staged files, an exclusive tool-owned
`data/.portalvs-geography-transaction/` directory (gitignored), fsynced original
backups and a prepared/committed journal. Caught failures, including failure on
the second replacement, roll back both originals. If killed mid-commit, a pending
journal blocks any further import; **keep readers stopped** and run:

```powershell
python scripts/import_portalvs_geography.py --recover-production
```

Prepared state restores both checksum-verified backups; committed state verifies
both new files and finishes cleanup. Incomplete pre-journal staging requires
manual inspection, but production writes have not begun at that point. If
recovery itself fails, retain the journal/backups and resolve the filesystem
problem before restarting. This is **offline exception-safe paired replacement
with interruption recovery**, not an impossible simultaneous transaction across
two independent files for live readers, nor a power-loss/filesystem guarantee.
Deployment should publish the validated Git revision as a unit, not refresh live
in-process caches. No DB, new dependency, Redis, SDK, acquisition schedule or
runtime upstream access is introduced.

After successful write/review, update **only the two** registry entries and their
freshness constants to match the new acquisition, commit the new non-content
manifest and run the release gates. The importer deliberately does not rewrite
source registry/outreach or unrelated data. New captures + current committed
public datasets suffice for future refreshes; no old private raw is required.

## PSC freeze and referential compatibility

All **3,101 stored PSC match links** still resolve with the same municipality,
district and region IDs. Full surrounding validation includes phone areas,
vehicle registration codes, school aggregates, procurement references where
present, and every other named geography reference. No unrelated dataset was
rewritten to follow the source migration.

`data/psc.json` before **and** after SHA-256:
`4b7346bbef19a86576fa5ecaa5f7d7c2afa36be5ff711753281b3a042b42bc55`.
This is the unchanged **Windows CRLF working-tree** byte hash. The unchanged
**Git/LF blob** SHA-256 is
`db9cd5c2d833cec0d199f4a7199f9c13f77346572bbd1507503ce01774b0dc24`.
Tests pin both exact platform checkout representations and separately require
strict before/after byte equality for imports; no PSC newline rewrite is made.
The entire PSC registry entry remains identical (canonical JSON SHA-256
`9a72cd6fa891ad312612b9caab22234916761dd030e4c1e9e45fcc8c4e5e0462`).
`PSC_LAST_UPDATED` remains **2026-06-02**. All five legacy-only keys remain:
**83006, 83155, 91931, 93539, 97651**. Legacy validity dates, embedded names,
grouping/matchCount behavior, semantics and source identity are not changed.
Embedded historical PSC municipality strings may differ from the two corrected
canonical labels; codes still identify the same administrative entities. There
is no hybrid reconstruction, successor PSC input, street/detail import or PSC fix.

Protected production JSON review:

| File | Before SHA-256 | After SHA-256 |
| --- | --- | --- |
| districts.json | `a1622739cd80386da6818072ff6d2d81f491af2594b7aae0f4a5ee5b5713d70f` | `b8db6377c4ffba093dc26497c26446b581465592a1a15e7b5b7f88ebd5e362a9` |
| municipalities.json | `7bc69db25450ee019c1e5ae2897b784c241484dd648f704dffd15d6ce83a54c6` | `547338295a6b4652af196560d5b01ae75d4946a236728a6d03023a3a154231b4` |
| sources.json | `a28423df4afb64ef3fa23d03b388d22306075e8014af95689b002f522435618b` | `ac94dcf62f12b42806d15d121f006a7b766ba2f895bc02586da219aa51b136e8` |

Only these three production JSON files changed; **all 11 others are byte-identical**.
Before/after byte hashes in this table refer to the acquisition host's Windows
working tree; Git can use LF where that checkout uses CRLF.
Registry differences are limited to districts/municipalities; PSC and all other
entries stay identical. No raw captures are committed.

## Public provenance, freshness and caching

Current catalogue identities:

- `/v1/sources/districts`: **PortalVS / IS Číselníky — Slovenské okresy**, county URL.
- `/v1/sources/municipalities`: **PortalVS / IS Číselníky — Slovenské obce**, town URL.
- `/v1/sources/psc`: **PortalVS classifier 42 (PSČ obcí SR a ČR)**, legacy URL.

All retain pending rights. Mixed provenance is intentional. Historical classifier
9/10 references remain in prior evidence, not current geography source identities.
Dataset metadata records exact successor URL/bytes/SHA-256 and acquisition UTC.
No trustworthy upstream dataset-level publication date exists: `lastUpdated`,
`DISTRICTS_LAST_UPDATED`, `MUNICIPALITIES_LAST_UPDATED` are **2026-10-16**,
the UTC OpenSK acquisition date, never max/min validFrom or an inferred ETag date.
Catalogue freshness also advances to 2026-10-16; PSC's own dataset freshness does not.

Geography list/item responses keep **`Cache-Control: public, max-age=86400`**,
strong body-derived ETags and **`Last-Modified: Fri, 16 Oct 2026 00:00:00 GMT`**.
For `/v1/districts`, `/v1/districts/SK03110`, `/v1/municipalities`,
`/v1/municipalities/504173`: ETags present, If-None-Match → 304,
If-Modified-Since at the new date → 304, prior date → 200; ETags differ from
the prior responses naturally as envelope freshness changes. Ordinary PSC
responses/caching remain unchanged (`Tue, 02 Jun 2026 00:00:00 GMT`), including
the historical grouping behavior. Optional geography expansions still resolve
current canonical geography, not rewritten embedded legacy strings.

No routes/shapes are added or removed: **39 GET operations**, `/v1`,
`metadata.version == "v1"`; final project version **0.23.10**.

## Compliance and next research questions

**PortalVS `SENT_AWAITING_REPLY`** (sent 2026-10-11, no new reply provided).
Non-commercial/restricted wording and public-promotion compliance gate remain.
No CC claim, verified licence, open redistribution or commercial approval is
inferred from API access, robots, public JSON or successful technical migration.
Telecom/ŠÚ SR states remain pending; NBS remains resolved. No outreach was sent.

Legacy shutdown cannot break local runtime. Geography refresh has moved to
successor; PSC remains historical materialized data until a safe authoritative
mapping/source and truthful scope are approved. **No PSC mapping research was
performed in this branch.** The next workstream is document-only here:

1. Can REGPJ or another ŠÚ SR source establish postal/local settlement →
   settlement unit/local part → municipality → district containment?
2. Can the remaining 42 non-street rows be deterministically mapped?
3. Can incompletely mapped street-only PSCs get administrative context **without
   street-name inference**?
4. Can official Slovenská pošta evidence establish the needed containment?
5. Is there an official machine-readable crosswalk with usable reuse terms?
6. If mappings become complete, can an occurrence-only model avoid implying
   address-wide validity?

Production PSC migration is not promised. Developer adoption remains queued
after this source-cleanup/mapping decision, not another automatic data domain.

## Validation and red-team review

| Question | Answer |
| --- | --- |
| Districts exclusively from successor county? | YES |
| Municipalities exclusively from successor town? | YES |
| Legacy PortalVS needed for either refresh? | NO |
| All district IDs preserved? | YES |
| All six-digit municipality IDs preserved? | YES |
| All 12 re-letterings evidence-verified? | YES |
| Any fuzzy mapping? | NO |
| Only two reviewed display changes, 504173/504742? | YES |
| PSC production unchanged? | YES, identical SHA-256 |
| PSC current provenance unchanged? | YES, entire entry identical |
| Five legacy-only PSCs still present? | YES |
| Street/detail PSC input in production? | NO |
| REGPJ/settlement mapping research started? | NO |
| PortalVS rights claimed resolved? | NO |
| Runtime calls PortalVS? | NO |
| Route count changed? | NO, 39 GET operations |
| Unrelated production datasets byte-identical? | YES |

Local final gates (2026-10-16):

- `python scripts/validate_datasets.py`: **0 errors / 44 existing warnings**,
  14 datasets; pending rights warnings retained.
- `python scripts/check_referential_integrity.py`: passed.
- `python -m pytest -q`: **799 passed**, including **59 new geography cases**;
  synthetic input fixtures need no private captures or live source access.
- `python -m compileall scripts routers services tests schemas`: passed.
- `git diff --check`: passed; staged/full-branch checks also required before push.
- Local HTTP smoke (`scripts/smoke_test.py`): **41 passed / 0 failed**.
- Fresh capture repeated offline dry-run after replacement: **idempotent**,
  no further record differences; network access forbidden during this check.
- Production hashes, all 3,101 PSC links, complete PSC registry-entry equality,
  all 18 unchanged registry entries and 11 unchanged production JSON files checked.
- **39 GET operations**, project version **0.23.10**, metadata version **v1**;
  source catalogue correctly mixed, all three PortalVS licence states pending.
- No routers/services/dependencies or outreach package files changed; no raw,
  transaction directory, PSC/street/detail input or REGPJ work committed.

Hosted CI is reported by the PR checks, separately from these local results.
No auto-merge, tag or release; stop at PR-ready.
