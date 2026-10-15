# NBS bank-directory reuse clarification — 2026-10-14

The clarification/PR #33 sections below are historical (0.23.6); the final
**0.23.8 production refresh** section records the current served v226 snapshot,
row-by-row source audit and direct bank/IBAN response attribution.

## Evidence and scope

The human maintainer received an authoritative institutional reply on **2026-10-14** from **Národná banka Slovenska, odbor komunikácie značky NBS a inštitucionálnych vzťahov**, concerning “Prevodník identifikačných kódov pre tuzemský platobný styk pre Slovenskú republiku”. Outreach was sent manually **2026-10-11**; state is now **`REPLY_RECEIVED_RESOLVED`**.

This record preserves the substantive clarification supplied by the maintainer, not a purported verbatim email or independently archived mail headers. Original correspondence is held privately by the maintainer. No personal email metadata is published and no additional message was sent.

Governing basis: **NBS Terms of Use + direct institutional clarification**, not CC BY, CC0 or a new open-data licence.

- Canonical source: <https://nbs.sk/platby/vseobecne-informacie/ciselniky-a-registre/prevodnik-sk/>.
- Terms: <https://nbs.sk/disclaimer-sk/>.
- This clarification covers the **bank converter**. It does **not** resolve the separate curated holidays transformation question.

## Resolved permissions and conditions

| Topic | NBS clarification |
| --- | --- |
| Local storage | Explicitly permitted. |
| CSV → JSON and renamed API fields | Permitted if underlying values remain unchanged. The transformed JSON is **not the original NBS electronic file** and must not be presented as such. Link the original and document the column-to-field mapping. |
| Derived fields | Permitted if clearly separated/labelled as OpenSK-derived, not represented as NBS-supplied data. NBS's own **“Akt. úč.”** column has source-defined semantics and must not be confused with OpenSK fields. |
| Public open-source API | Explicitly permitted with NBS attribution and the transformation/derived-field conditions above. |
| Commercial downstream use | Not excluded by the terms; allowed subject to those conditions. Downstream users must also attribute NBS. NBS does not guarantee completeness/content integrity or accept liability for associated damages; commercial users should verify correctness. |
| Code versus data | MIT covers OpenSK source code, **not NBS data**. NBS-origin data, including `data/banks.json`, remains subject to NBS Terms of Use. |
| NBS logo, flag and symbols | Separate approval required; none is needed or used by this work. |

NBS recommends attribution equivalent to:

> Zdroj: Národná banka Slovenska, Prevodník identifikačných kódov pre tuzemský platobný styk pre Slovenskú republiku, verzia 225, platnosť od 2026-05-18, https://nbs.sk/platby/vseobecne-informacie/ciselniky-a-registre/prevodnik-sk/. Údaje previedol do formátu JSON projekt OpenSK; odvodené polia nie sú údajmi NBS.

This is **recommended wording**, not an assertion that this exact sentence is legally mandatory. Preserve its substance: institution, converter title, actual served version/effective date, original-source link, JSON transformation and separation of derived fields. Attribution and the source conditions also apply to downstream commercial users.

## Snapshot and refresh boundary (historical 0.23.6 / PR #33)

- **Served snapshot stays version 225, effective 2026-05-18**, 30 domestic rows. `BANKS_LAST_UPDATED` remains `2026-05-18`.
- **At reply time**, NBS identified upstream **version 226, effective 2026-10-08**. This is the reply's dated statement, not a newly downloaded snapshot or a claim about every later date.
- **No bank data refresh in PR #33.** No v226 raw file, no `data/banks.json` changes, no bank endpoint record/envelope changes.
- Future small refresh: retain source version, effective date and actual download date, as strongly recommended by NBS; synchronize periodically and reconcile values against the original. The v225 download date is not established here; do not substitute a verification date for it.
- The frozen v225 file still contains its old `metadata.license` placeholder. It is superseded by this clarification and `data/sources.json`, not a current unresolved rights determination. The file is deliberately not edited in this PR, and that legacy metadata is not returned by bank routes. The old bank importer's metadata template also needs alignment during the later refresh.

## Source-column → API-field audit

Audit target: `scripts/import_banks.py` (`normalize_bank_record`, `_normalize_active_marker`, `_is_domestic_record`) and unchanged runtime `data/banks.json`. The importer explicitly selects these English CSV column names; the original v225 CSV bytes are not retained in the repository, so this audit proves the code path, not an independent row-by-row reproduction from archived source bytes.

| API field | Selected source column / rule | Classification |
| --- | --- | --- |
| `code` | `Payment system code SR`; trim/remove spaces, zero-pad to 4 digits | Renamed, normalized NBS data (identifier value preserved) |
| `name` | `Payment service provider`; whitespace normalization | Renamed, normalized NBS data |
| `bic` | `SWIFT 8`; remove spaces, uppercase | Renamed, normalized NBS data |
| `swift` | Same `SWIFT 8` value as `bic` | Renamed compatibility alias of normalized NBS data |
| `alphabeticCode` | No separate corresponding column in the v225 CSV import; `null` | OpenSK schema placeholder, not an additional NBS datum |
| `activePartyMarker` | **`Payment system SIPS`**, not `Akt. úč.`; canonicalization below | **OpenSK-derived categorical normalization of an NBS column**, not a verbatim NBS marker or renamed `Akt. úč.` |
| `activeParty` | Boolean from the same selected SIPS marker | **OpenSK-derived boolean**, not an NBS-supplied flag |
| `country` | Domestic-country/BIC filter; output constant `SK` | OpenSK-derived scope label |

Marker rules in the existing importer (accepted aliases include research/JSON input conveniences, not evidence of all tokens in the original CSV):

- `X`, `C`, `ÁNO`, `ANO`, `YES`, `TRUE`, `1` → `(activeParty=true, activePartyMarker="C")`.
- `K` → `(true, "K")`.
- `Ø`, `O`, `0`, empty, `NIE`, `NO`, `FALSE` → `(false, "Ø")`.
- Unknown marker → error. On CSV, `Payment system SIPS` is selected before `activePartyMarker`, `activeParty`, `Active party` aliases.

**Neither output field reads `Akt. úč.`.** Do not claim either reproduces that column or that `activeParty` establishes a bank's general legal/current operating status. The current 21 true / nine false rows describe OpenSK's participation projection, not a freshly verified list of active/inactive institutions. Tests protect the implementation mapping but do not certify source semantics.

No genuine numeric/record-value error was established from the available source bytes; the misrepresentation was documentation treating the marker as a preserved NBS field. Correct that disclosure now, without changing bank behavior. At the later v226 refresh, review the converter's source documentation and **both** participation-related columns, retain their distinct meanings, verify the mapping row-by-row, and label OpenSK derivations explicitly rather than silently switching inputs.

## 0.23.8 production refresh

### Acquisition and scope

The official converter page was inspected **before** acquiring the CSV. It
still displayed **version 226**, effective **8. 10. 2026**, on 2026-10-15; this
is a current page observation, not merely reuse of the reply's dated statement.

| Provenance | Value |
| --- | --- |
| Version / source effective date | **226 / 2026-10-08** |
| Actual download completion (UTC) | **2026-10-15T16:23:00Z** |
| Exact official CSV URL | `https://nbs.sk/dokument/a5050ba9-1b79-4a1b-82c6-0f3a0b666af4/stiahnut/?force=true` |
| Response bytes | **1,953** |
| SHA-256 of original downloaded bytes | `b82cd0c34d89ff1a68d710fedd3e8f509065a53ae605282ad4fc29234b74fc64` |
| Encoding / separator | **CP1250 / semicolon** (HTTP declares UTF-8, but bytes are not valid UTF-8) |
| Source rows / included domestic / excluded CZ BIC rows | **38 / 30 / 8** |
| OpenSK SIPS projection true / false | **21 / 9** |

Raw acquisition is local temporary material, not committed; URL, actual
timestamp, source bytes/hash, version and effective date are retained in
`data/banks.json`. `lastUpdated` and `BANKS_LAST_UPDATED` are **2026-10-08**,
not the download date, reply date or today's date. The v225 download date
remains unknown; no retroactive acquisition provenance was invented.

### Explicit source-column audit

The current CSV has a title row `Prevodník identifikačných kódov SR;;;`, then
these **four exact headings**. This differs from the old English-header parser;
the importer now has an intentional reviewed Slovak profile, not a guessed
column-order fallback. Unknown/missing headings or changed row widths fail
closed before production writing. The English profile remains supported.

| Current CSV column | Previous English column meaning | API field / rule |
| --- | --- | --- |
| `Kód platobného styku` | `Payment system code SR` | `code`: trim/normalize whitespace and pad to four digits, preserving identity/leading zeros |
| `Poskytovateľ platobných služieb` | `Payment service provider` | `name`: source text, whitespace normalized only; no translation or stylistic correction |
| `SWIFT kód 8` | `SWIFT 8` | `bic`: normalized BIC or null; `swift` remains the same compatibility alias; no inferred BICs |
| `Systém SIPS` | `Payment system SIPS` | `activePartyMarker`: OpenSK categorical normalization; `activeParty`: OpenSK boolean derived from it |
| No corresponding CSV column | — | `alphabeticCode`: null OpenSK schema placeholder |
| Domestic BIC/scope selection | — | `country`: OpenSK-derived `SK`; eight non-SK BIC rows excluded |

Independent row-by-row reconciliation against the downloaded CP1250 bytes
matched **all 30** public codes, whitespace-normalized provider names, BICs,
null placeholders and SIPS projections. The observed SIPS tokens are **`x`
and empty**: `x → C / true`, empty `→ Ø / false`. No SIPS participation changes
occurred relative to v225. The existing reviewed `K → K / true` normalization
remains supported; unrecognized markers fail.

**`Akt. úč.` is a separate HTML display heading, not a second column in this
CSV**. The NBS page explains C/Ø/K as SIPS participation markers. That supports
participation semantics, **not** a guarantee that a bank is currently operating.
Neither derived API field selects `Akt. úč.` as its input. Synthetic regressions
include both headings with deliberately contradictory values and prove SIPS
alone drives the result (including a blank SIPS marker).

### Reviewed v225 → v226 changes

30 → 30 public records; **no codes added or removed**. Every differing record
was reviewed:

| Code | Field | Previous normalized value | New source-derived value |
| --- | --- | --- | --- |
| `3100` | `name` | `Prima banka Slovensko, a.s. - Code for running payments` | `Prima banka Slovensko, a.s. – kód pre dobeh platieb` |
| `7930` | `name` | `Wustenrot stavebná sporiteľňa, a.s.` | `Bausparkasse Wüstenrot Aktiengesselschaft, pobočka zahraničnej banky` |
| `9956` | `bic`, `swift` | null | `PYYUSK22` |

The CSV spells `Aktiengesselschaft`; the HTML page spells `Aktiengesellschaft`.
**The CSV spelling is preserved**, not silently corrected from a different
representation. The 3100 change restores the supplied Slovak text rather than
retaining an old translated name. No other row fields changed; SIPS projection
totals remain 21/9 and all `alphabeticCode` values remain null. No stale rows or
invented historical retention were added.

### Direct public attribution

`GET /v1/banks`, `GET /v1/banks/{code}` and every normal
`GET /v1/iban/validate/{iban}` result now carry additive, typed metadata:
`source`, `lastUpdated`, `version="v1"`, `sourceVersion`, `sourceEffectiveDate`,
`sourceDownloadedAt`, `sourceUrl`, `sourceFileUrl`, `sourceBytes`, `sourceSha256`,
`termsUrl`, `attribution` and `transformation`. Values derive from the one local
bank dataset, not independently hardcoded router versions. `/v1/sources/banks`
remains aligned; its internal fields are still excluded from that catalogue's
curated public projection.

Bank success source names **Národná banka Slovenska** and OpenSK transformation.
IBAN source explicitly says **OpenSK API / ISO 13616 IBAN checksum validation;
Slovak bank-code resolution from Národná banka Slovenska converter**. NBS is
only the source for resolution, not the checksum validator. Invalid/non-Slovak
validation results declare the same local resolution dataset without claiming
it was used to validate the checksum. Standard error envelopes remain global.

Current attribution (recommended substance, not immutable legal formula):

> Zdroj: Národná banka Slovenska, Prevodník identifikačných kódov pre tuzemský platobný styk pre Slovenskú republiku, verzia 226, platnosť od 2026-10-08, https://nbs.sk/platby/vseobecne-informacie/ciselniky-a-registre/prevodnik-sk/. Údaje previedol do formátu JSON projekt OpenSK; odvodené polia nie sú údajmi NBS.

Transformation metadata distinguishes field renaming/normalization and derived
`activePartyMarker`, `activeParty`, `country`, and absent-field placeholder
`alphabeticCode`. JSON is **not** the original NBS file. Rights remain **NBS
Terms of Use + direct clarification**, not MIT/CC data licensing; downstream
attribution and NBS's completeness/liability limitations apply. **No NBS symbols
or branding assets used.**

### Manual refresh workflow

Inspect the official page first; use its then-current version/effective date,
not a permanently assumed v226. Download offline into local temporary storage
and record actual completion time. No runtime/scheduled fetching or database.
Example for the actual acquisition above:

```powershell
python scripts/import_banks.py --input "C:\external\nbs-v226.csv" --source-version 226 --effective-date 2026-10-08 --downloaded-at 2026-10-15T16:23:00Z --source-file-url "https://nbs.sk/dokument/a5050ba9-1b79-4a1b-82c6-0f3a0b666af4/stiahnut/?force=true" --previous-source-version 225 --dry-run
```

SHA-256 and byte size are calculated from the actual input bytes. All provenance
arguments are explicit; no `date.today()` freshness fallback. Review the
deterministic report (versions/effective dates/counts, added/removed/changed
codes, provider/BIC/SIPS changes and totals), then add
`--output data/banks.json --write`. `--compare-with` can choose a local previous
snapshot; `--previous-source-version` supplies evidence-backed version context
only for legacy snapshots missing that field (v225 here). Validation precedes
writing; no change acknowledgement is needed for these manually reviewed bank
changes. Keep generated backup files out of Git.

Update `BANKS_LAST_UPDATED` to source effective date, source catalogue and docs,
run all validation/smoke checks and inspect Git diff before committing. Strong
body ETags change with new data/provenance; Last-Modified is 2026-10-08 for the
three routes, with both conditional 304 forms retained. No route added:
**39 GET operations**, namespace `/v1`, metadata version `v1`. Other datasets,
outreach states and holidays' separate licence question are unchanged.
