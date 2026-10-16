# PortalVS → IS Číselníky (ciselniky2) source resilience

> **Current production, 0.23.10 (2026-10-16):** districts and municipalities
> have migrated to fresh successor county/town captures; 79 / 2,927 records,
> all IDs preserved, two reviewed municipality display corrections. Refresh no
> longer needs legacy PortalVS. **PSC is unchanged and legacy-backed**, with
> successor promotion still NO_GO. Rights remain `SENT_AWAITING_REPLY`, no
> runtime upstream dependency. See [migration/refresh evidence](portalvs-successor-geography-migration.md).
> The remainder below retains historical 0.23.3/0.23.9 provenance and findings.

> **0.23.9 full-source correction (2026-10-15):** this is historical 0.23.3
> feasibility evidence, **not proof of PSC promotion readiness**. Excluding
> `ulica` retains 1,293, not 1,415 PSCs; 84 non-street rows lack the original
> exact municipality join. `obce` may be a locality/municipality part; absence
> of five PSCs does not establish legal retirement. See
> [PSC semantics spike](portalvs-psc-successor-semantics.md) for the superseding
> `NO_GO_SUCCESSOR_PSC` decision and independent geography GO verdicts.

Milestone 0.23.3, verified live on **2026-10-11** (all timestamps UTC, same day).
Scope: technical resilience and provenance only. Rights remain unresolved
(non-commercial-only portal copyright wording; clarification `SENT_AWAITING_REPLY`
2026-10-11 — see `docs/research/source-licence-outreach.md` §1). This document draws
no licence conclusion, redistributes no raw data, and commits no raw snapshots.
Temporary snapshots/manifests live only in
`C:\Users\matej\AppData\Local\Temp\opencode\portalvs` (`manifest-2026-10-11.json`,
`probe3-results.json`, six JSON snapshots, county format samples, OpenAPI spec).

## 1. Live re-verification (2026-10-11)

### 1.1 Legacy system — `ciselniky.portalvs.sk` — STILL UP, deadline unchanged

- End-of-support banner still present on every page, quoted verbatim:
  > **"Spustili sme novú verziu číselníkov! Podpora doterajšieho systému končí 31.10.2026."**
  > (link: `https://ciselniky2.portalvs.sk/` — "Zistiť viac")
- Machine-readable REST export endpoints all return **HTTP 200, `application/json`**, single
  unpaginated JSON array (a `?limit=1` probe returned the full 5 MB body — query params are
  ignored, no pagination, no ETag, no `Last-Modified`):
  - classifier 9 Obce → `/api/rest/json/9` — **34,438 records** (worldwide + history), 5,032,175 bytes, sha256 `9a2d5167…`
  - classifier 10 Okres → `/api/rest/json/10` — **157 records** (79 SK + 77 CZ + 1 "Zahraničie"), 16,576 bytes, sha256 `e903020e…`
  - classifier 42 PSČ obcí SR a ČR → `/api/rest/json/42` — **19,465 records**, 2,565,439 bytes, sha256 `7767b47f…`
- Update-version metadata: none (no version IDs, no ETag/Last-Modified). Freshness proxies:
  per-record `validity_from`/`validity_to`. Observed maxima: classifier 9 `2026-10-09` (any row),
  but Slovak *current* rows max `2012-10-01`; classifier 10 max `2018-07-31` (CZ rows) / `2010-01-01` (SK);
  **classifier 42 max `2018-10-09` — legacy PSC content is stale for ~8 years.**
- Notable late change in classifier 9: `code_su` is now a **composite LAU-style code**
  (e.g. `SK0326511226` for Ábelová; the 6-digit statistical code survives as the suffix and
  also as the plain `code` field on SK rows). The portal about-page documents: 200 records/page
  in HTML UI, CSV export unpaginated; items identified by code (+ validity date for history).

### 1.2 Successor — `ciselniky2.portalvs.sk` ("IS Číselníky", MŠVVaM SR) — UP

- Official human-facing slugs → API endpoints (discovered via documented export links on each
  classifier page, plus the OpenAPI spec — no scraping beyond link discovery):
  - `slovenske-obce` → `https://ciselniky2.portalvs.sk/api/town`
  - `slovenske-okresy` → `https://ciselniky2.portalvs.sk/api/county`
  - `psc-sk` → `https://ciselniky2.portalvs.sk/api/postal_code_sk`
  - Czech rows are **separate classifiers**: `ceske-obce` → `/api/town_cz`,
    `Obce - CRŠ` → `/api/town_foreign`, `psc-cz` → `/api/postal_code_cz`.
- OpenAPI 3 spec: `https://ciselniky2.portalvs.sk/api/docs.json`
  (title "Dokumentácia API - Číselníky Portal VŠ", version 1.0.0, **license: null**, 48 paths).
- Formats per endpoint: `.json` (UTF-8), `.xml`, `.csv` (UTF-8, `;`-delimited), `.csvwin`
  (windows-1250), `.jsonld` (Hydra-style collection with `totalItems`). Verified on `/api/county.*`.
- Pagination/bulk: **none needed** — each endpoint returns the complete array in one response
  (town ≈ 1.1 MB, psc-sk ≈ 2.5 MB). Weak ETags present (content-hash style, e.g.
  `"caaf11e7581eb87f"`) — usable for change detection; no `Last-Modified`.
- Validity filter: `?validity=valid|invalid` documented for `/api/town` and `/api/county`
  (verified: town 2,928 valid + 2 invalid; county 80 valid + 1 invalid). **`/api/postal_code_sk`
  silently ignores the filter** (13,700 rows returned for all parameter values).
- Version/update metadata: per-record `validFrom` (and sparse `validTo`); no dataset-level
  version identifier beyond ETag. town/county content max `validFrom` = `2014-09-23`.
- robots.txt **permits the API explicitly**: `Allow: /api/` with the comment
  `# Verejné API a RSS sú dostupné pre indexáciu` (public API and RSS available for indexing);
  only `/admin/`, auth and account paths are disallowed. Legacy `robots.txt` is empty (no rules).
- The portal-wide copyright page still says information may be downloaded **"iba k nekomerčnému
  použitiu"** (non-commercial use only). The successor publishes no separate licence page and no
  `license` in its OpenAPI info. Rights question unchanged → outreach pending.

## 2. Transition manifests (2026-10-11, temp dir only — not committed)

| Snapshot (temp file) | URL | Records | Bytes | SHA-256 (first 12) | Top-level fields |
|---|---|---|---|---|---|
| `legacy-9-obce.json` | `…/api/rest/json/9` | 34,438 | 5,032,175 | `9a2d516766a0` | code, name, code_su, county_code, country_code, validity_from, validity_to |
| `legacy-10-okres.json` | `…/api/rest/json/10` | 157 | 16,576 | `e903020e924b` | code, name, country_code, validity_from, validity_to |
| `legacy-42-psc.json` | `…/api/rest/json/42` | 19,465 | 2,565,439 | `7767b47ffb4a` | municipality_code, postalcode, delivery_post, validity_from, validity_to |
| `c2-town-slovenske-obce.json` | `…/api/town.json` | 2,930 | 1,106,346 | `45856d723ede` | sortNumber, code, officialTitle, mediumTitle, shortTitle (+En), note, noteEn, includes(Also), excludes, info, additionalInfo, infoEn, unitOfMeasure, validFrom (sparse validTo) |
| `c2-county-slovenske-okresy.json` | `…/api/county.json` | 81 | 30,845 | `12467d52ba59` | same generic shape as town |
| `c2-postal_code_sk-psc-sk.json` | `…/api/postal_code_sk.json` | 13,700 | 2,525,777 | `e4c83b436c05` | dulica, psc, dposta, posta, obce, typZaznamu, kodOkresu, kraj, name_translations (sparse: ulica, poznamka) |
| `ciselniky2-openapi.json` | `…/api/docs.json` | 48 paths | 464,274 | `9c9a08a42173` | OpenAPI 3 document |

Identifier/code fields: legacy 9/10 = `code`; legacy 42 = `municipality_code`+`postalcode`;
successor town/county = `code` (composite; `note` carries the 6-digit municipality / 3-digit
district statistical code); successor psc-sk = `psc` (+ `kodOkresu` 3-digit district code).

## 3. Compatibility analysis (successor vs `data/municipalities.json`, `data/districts.json`, `data/psc.json`)

Counts table (as of 2026-10-11):

| Dataset | Legacy export today | Successor today | Local OpenSK file | Verdict |
|---|---|---|---|---|
| Municipalities | 34,438 rows (worldwide); SK current 2,935 rows / 2,927 distinct codes | 2,930 rows = 2,927 Slovak municipalities + 1 retired military district + 2 "Zahraničie" pseudo-rows (2,928 valid incl. pseudo-row) | 2,927 records | **equivalent** after deterministic filtering |
| Districts | 157 rows (79 SK + 77 CZ + 1 foreign) | 81 rows = 79 SK districts + 2 pseudo-rows (80 valid) | 79 records | **equivalent names/coverage; 12 codes re-lettered** |
| PSC | 19,465 rows, 4,094 distinct PSCs (1,420 SK + 2,674 CZ); stale since 2018-10-09 | 13,700 rows, 1,415 distinct PSCs, Slovak-only; obec 2,790 / detail_sc 173 / ulica 10,737 rows | 1,420 PSC keys, 3,101 matches | **equivalent PSC values minus 5 retired; more detail rows; no municipality codes** |

The ten brief questions, answered:

1. **Official identifiers/slugs** — see §1.2: page slugs `slovenske-obce` / `slovenske-okresy` /
   `psc-sk`; API paths `/api/town` / `/api/county` / `/api/postal_code_sk`; OpenAPI version 1.0.0.
2. **Stable codes identical?** — Yes for the identifiers OpenSK actually carries: all **2,927
   local 6-digit municipality codes are present verbatim as the successor town `note` field**
   (zero missing). District **names match verbatim for all 79** (`mediumTitle`), and each county
   record keeps the legacy 3-digit code in `note`. PSC **values are a strict subset**: all 1,415
   successor PSC values exist in legacy 42's Slovak subset (zero newly-invented PSCs).
3. **Field names/semantics** — Changed. town/county use a generic multilingual shape
   (`officialTitle`/`mediumTitle`/`shortTitle` + `En` variants, `note`, …) instead of legacy
   `name`/`code`. psc-sk is a new schema entirely: `dposta` = legacy `delivery_post`
   (spot-checked: "Žilina 1", "Bratislava 1", "Banská Bystrica 1" match), `obce` = municipality
   **name** (no code), `kodOkresu` = 3-digit district code, plus new street-level rows
   (`typZaznamu=ulica`) that legacy 42 never had.
4. **Record-count equivalence** — Confirmed above: municipalities exact (2,927 = 2,927);
   districts exact (79 = 79); PSC values 1,415 vs local 1,420 (see #6).
5. **Non-Slovak rows** — The successor **split them out**: `psc-sk` contains **zero Czech rows**
   (verified: every `psc` is 5 digits and region/district codes are Slovak-only), and Czech data
   lives in `postal_code_cz`/`town_cz`/`town_foreign`. The legacy-42 Czech-filter problem
   disappears; the only exclusions still needed are the explicit pseudo-rows
   ("Zahraničie": `SKZZZZ`, `SKZZZZZZZZZZ`, `SKZZZ`) and the retired military district.
6. **Retired records** — Legacy keeps history in-line via `validity_to` (1,053 expired rows in
   classifier 9; none in 10/42). Successor keeps retired records server-side, excluded via
   `?validity=valid` (town: 2 invalid — `Javorina (vojenský obvod)`, validTo 2010-12-31, code
   523551 [not in OpenSK, matching the local "special-purpose rows excluded" rule]; one old
   Zahraničie pseudo-row, validTo 2014-09-22). psc-sk carries **no validity fields at all**;
   five PSCs present locally and in legacy 42 (`83006`, `83155`, `91931`, `93539`, `97651`) are
   absent from the successor — consistent with postal-code retirements after legacy 42 went stale
   (2018). Local `validFrom: "2010-01-01"` values cannot be re-derived from psc-sk.
7. **District-code re-lettering** — the one real identifier shift: 12 districts now carry
   Eurostat LAU letter codes — `SK03110→SK031A` Tvrdošín(510), `SK03111→SK031B` Žilina(511),
   `SK03210→SK032A` Veľký Krtíš(610), `SK03211→SK032B` Zvolen(611), `SK03212→SK032C` Žarnovica(612),
   `SK03213→SK032D` Žiar nad Hronom(613), `SK04110→SK041A` Stará Ľubovňa(710), `SK04111→SK041B`
   Stropkov(711), `SK04112→SK041C` Svidník(712), `SK04113→SK041D` Vranov nad Topľou(713),
   `SK04210→SK042A` Spišská Nová Ves(810), `SK04211→SK042B` Trebišov(811). The old↔new mapping is
   deterministic 1:1 by name and by the 3-digit `note` code; town composite codes embed the new
   district codes (559 of 2,927 municipalities are in these 12 districts, so naive
   prefix-derivation of local `districtCode` from successor town codes would require the mapping).
8. **Name semantics** — successor `officialTitle` is the plain municipality name; 205 local
   records carry an OpenSK-side disambiguation suffix "(okres X)" (e.g. `Jablonové (okres Malacky)`
   vs `Jablonové`). That remains an importer transformation, unchanged in principle.
9. **Deterministic rebuild** — Yes, from public API JSON only. Rebuild recipe per dataset:
   municipalities = fetch `town.json?validity=valid`, drop pseudo-rows (`SKZZ*`), take `note` as
   `code`, derive `districtCode` via `code[0:6]` + the 12-entry letter-code mapping (or via
   `note` → local six-digit code join), apply the existing name-disambiguation rule; result =
   exactly 2,927 records with identical codes. Districts = `county.json?validity=valid` minus
   pseudo-row → 79 records; keep local codes via the mapping (names/3-digit notes prove it).
   PSC = `postal_code_sk.json`, take `typZaznamu != ulica` rows (or retain street rows as new
   detail), group by `psc`; `kodOkresu`→district via county `note`; `obce` name→`municipalityCode`
   via town (name+district join, exactly the join `import_psc.py` already performs);
   `validFrom/validTo` need new defaults. No scraping, no runtime upstream calls, deterministic
   given a pinned snapshot.
10. **Public API contract impact** — None required. Canonical OpenSK shapes
    (`code`, `name`, `regionCode`, `districtCode`, `psc`, `matches[]`, …) can be produced
    byte-compatibly in semantics; the decision whether to adopt the 12 new district codes or keep
    the existing ones is an internal data-decision (mapping documented in #7), not a forced
    contract change. The only coverage delta is the 5 retired PSCs and optionally the new
    street-level PSC detail.

### Per-dataset verdicts

- **Municipalities (9 → `slovenske-obce`)**: COMPATIBLE — identical code set (2,927),
  transform changes only (field rename, validity filter, pseudo-row exclusion, district-code
  mapping for 12 re-lettered districts).
- **Districts (10 → `slovenske-okresy`)**: COMPATIBLE — 79/79 name-identical; note the 12
  Eurostat LAU re-lettered codes; Czech rows separated into `town_cz`-style equivalents.
- **PSC (42 → `psc-sk`)**: COMPATIBLE WITH DATA DRIFT — Slovak-only output (filter no longer
  needed), 1,415 PSCs (5 local PSCs retired upstream), municipality linkage now by **name, not
  code**, no validity dates, plus 10,737 new street-level rows the current importer can ignore.

## 4. Acquisition-method check

- Previous acquisition (per `scripts/import_geography.py`, `scripts/import_psc.py`,
  `docs/import-pipeline.md`, `docs/data-sources.md`): **manual, offline** — legacy exports were
  downloaded (e.g. via `scripts/fetch_source.py` or by hand) into `data/raw/`, then transformed
  by offline importers into `data/generated/` and validated; API routes never call upstream
  ("local materialized JSON only" per `docs/roadmap.md`). No raw PortalVS snapshots are retained
  in the repository (`data/raw/` holds only small permissible sources; `psc.json` lastUpdated
  `2026-06-02`, municipalities `2026-09-07`).
- Scripted download of the ciselniky2 API is **technically reasonable and not robot-restricted**:
  robots.txt explicitly allows `/api/`, responses are few-MB single GETs with ETags, and the
  OpenAPI spec documents the endpoints. The only caution is legal, not technical: the portal
  family's non-commercial-only copyright wording and the unanswered 2026-10-11 outreach mean any
  download/redistribution remains subject to the pending clarification. Nothing was blocked, so
  snapshots were captured to the temp dir for this research only and **not committed**.

## Verdict

SUCCESSOR_COMPATIBLE_WITH_TRANSFORM_CHANGES
