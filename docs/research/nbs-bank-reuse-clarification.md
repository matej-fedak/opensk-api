# NBS bank-directory reuse clarification — 2026-10-14

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

## Snapshot and refresh boundary

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
