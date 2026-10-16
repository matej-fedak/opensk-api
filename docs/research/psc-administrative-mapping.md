# 0.23.11 — PSC Administrative Mapping Evidence Spike

**RESEARCH ONLY · NO PSC PRODUCTION MIGRATION · NO ROUTE CHANGES · NO FUZZY
MAPPING · NO LICENCE INFERENCE · NO AUTOMATIC OUTREACH.** Checked 2026-10-16.

## 1. Executive verdict

| Axis | Decision |
| --- | --- |
| Administrative mapping | **MAPPING_PARTIAL** |
| Product semantics | **CONTRACT_CLARIFICATION_REQUIRED** |
| Future primary source | **NO_SOURCE_READY** (postal ZIP is a technical candidate, not an approved replacement) |
| REGPJ reuse | **PENDING**: general CC BY 4.0 policy identified; exact register/third-party coverage not independently cleared |
| Slovenská pošta reuse | **UNKNOWN**: free lookup/download is not redistribution/transformation permission |
| PortalVS reuse | **PENDING / SENT_AWAITING_REPLY**, portal-wide non-commercial wording retained |
| Overall next step | **NO_GO_SUCCESSOR_PSC** |

REGPJ supplies useful **explicit spatial relationships**, not a universal postal
crosswalk. All 2,927 administrative IDs reconcile, but one of 42 remaining
non-street rows gains a unique snapshot-qualified parent; Kolónia remains
ambiguous and 40 rows remain unmatched. None of the 63 incomplete street-only
PSCs becomes complete. A previously unique postal-part candidate yields
**conflicting administrative paths**, demonstrating why candidate counts are not
promotion approval. Missing borough identity, unknown spatial snapshot validity
and reuse gaps prevent a truthful full rematerialization.

Park PSC production work; **developer adoption / OpenAPI correctness is next**.
Do not promise a 0.23.12 PSC migration or schedule another evidence loop without
new authoritative material. All production JSON and runtime behavior are frozen.

## 2. Starting blockers from 0.23.9

Re-ran `scripts/analyze_portalvs_psc_successor.py` first against the retained
2026-10-15 capture and postal ZIP, then reproduced the same counts with a fresh
2026-10-16 capture. The new analyzer explicitly separates **historical baseline
normalization/candidates** from its stricter current evidence model.

- **13,700** source rows: **2,790 obec / 173 detail_sc / 10,737 ulica**.
- **1,415** PSCs: **1,293** represented in non-street rows; **122** street-only.
- Original **84** exact-title/district failures: **65 obec / 19 detail_sc**, **82
  locality/district pairs**, **69 PSCs**.
- Baseline publisher/title candidates: **15** normalized titles, **26** postal
  paired-label candidates, **one** postal-part candidate. None had production approval.
- Remaining **42 source rows** = **41 unresolved + one ambiguous**, across **40 pairs**.
- Street-only baseline: **54** single-municipality candidate PSCs + **five** fully
  mapped multi-municipality candidate PSCs = **59** complete candidates; **63 incomplete**.

Those counts are reproduced, not reinterpreted as already approved joins. With
REGPJ, the 15 normalized titles have exact structural evidence; the 26 paired
labels still lack the stricter exact chain; the old single part candidate becomes
a source-path conflict (§9). Baseline artifacts remain historical evidence.

## 3. Source acquisitions

Non-content provenance:
[`psc-administrative-mapping-acquisition.json`](psc-administrative-mapping-acquisition.json).
Private directory: `C:\Users\matej\AppData\Local\Temp\opencode\psc-02311\`.
No raw workbook/ZIP/array or street/house/author dump is committed.

### REGPJ

- [Official source page](https://slovak.statistics.sk/wps/portal/ext/Databases/REGPJ/),
  states page update **2025-08-18**, links [REGPJ2020.zip](https://slovak.statistics.sk/wps/wcm/connect/2fd6b6d9-9be8-4af4-b0e5-bb68357074e1/REGPJ2020.zip?MOD=AJPERES&CVID=oYTDUNS&CVID=oYTDUNS&CVID=n2ARbRp).
- Local direct requests returned **HTTP 403, Cloudflare challenge**. No challenge
  bypass. Maintainer downloaded the linked ZIP manually and supplied it locally.
- Verified **2026-10-16T09:11:00Z**: **722,009 bytes**, SHA-256
  `445cd5698c8173b0afbc0004c16045bdf4596a678e0a50bba0fff3297b44cab5`.
  Exact browser acquisition UTC and response status/Content-Type/ETag/Last-Modified
  were not supplied and are **null**, not guessed as HTTP 200/application ZIP.
  Verification time is not fabricated acquisition time.
- Members: **REGPJ2020.ods (312,755 bytes)** and **REGPJ2020.xlsx (556,547 bytes)**.
  No README, CSV, validity file or relationship-codebook accompanies them. Analysis
  uses XLSX; ODS is an alternate representation, not a separately certified source.
  XML is UTF-8; no legacy CSV encoding guess or replacement decoding is needed.
- ZIP member save timestamps: **2024-04-30 21:01:28 / 21:00:42**, timezone unknown.
  ODS modified metadata: **2024-04-30T19:01:29Z**. These are save metadata, not an
  authoritative register effective date. Filename `2020` is not an as-of guarantee.

### Slovenská pošta

- [Official postcode page](https://www.posta.sk/psc), downloaded 08:45:57Z,
  HTTP 200, HTML, 119,603 bytes, SHA-256
  `588b4cbf2fa7e76a97585765c3b4033e96833cb8d481cfd8ca19524256ba6445`.
- Its [published ZIP](https://www.posta.sk/files/6811e10125b182cd7cd9e3a9/postove-smerovacie-cisla-na-stiahnutie.zip)
  acquired **2026-10-16T08:46:00Z**, HTTP **200**, `application/x-zip-compressed`,
  **731,276 bytes**, SHA-256
  `7f9e3686df8c3f67ca121f8581f334e9c5dd5b28cec7b97e106e3b73a356d54c`;
  no ETag or Last-Modified. Same content hash as 0.23.9, freshly downloaded.
- Members: **OBCE.xlsx 247,197**, **ULICE.xlsx 398,774**, **POBoxy.xlsx 162,264 bytes**.
  Sheet names and archive timestamps are in the manifest. OBCE sheets: `obce`,
  `detail SČ`, `popis`, `miestne časti`. Basic locality rows **2,953** (some refer
  to detail lists), detailed assignment rows **173**, **1,281 non-self part relations**.
  ULICE contains **10,737** street assignments. P.O.BOX has separate sheets
  `PSČ_POBOXov`, `zmeny`, `rušenie pôšt` and is not used as territorial assignment evidence.
- OBCE has **11 formula cells**: only existing cached scalar values are read,
  never recalculated or rewritten. That preserves publisher bytes and agrees with
  the captured successor signatures. Raw detail sheet has 179 XML rows, 175
  non-empty parsed rows and 173 assignment rows; these counts are different concepts.
- Embedded modified dates **2026-09-25** and archive timestamps are file metadata,
  not assignment effective dates. `popis` says generally at least monthly refresh.

### PortalVS

Fresh complete acquisition **2026-10-16T09:05:47Z** (county/town/PSC), all HTTP
200 JSON; per-source sizes/rows/hashes/ETags in the manifest. PSC:
https://ciselniky2.portalvs.sk/api/postal_code_sk.json, **2,525,777 bytes**,
SHA-256 `e4c83b436c058b5b8bc8c34ef5432a9f17c1a0ce2a46a8e4039a5a42b77ff96f`,
ETag `"caaf11e7581eb87f"`; all 13,700 rows equal the retained capture.
Full acquisition manifest checksum:
`d53a24b79800193b817d6fb31359f9d59bd2f8881d6e0a7b3a220077836b1e61`.
[Classifier page](https://ciselniky2.portalvs.sk/ciselniky/psc-sk) names Slovenská
pošta as source and states **content change 2026-10-04 03:15:09**, timezone not
given. This is source-page update evidence, not a postal assignment validity date.
No production source is changed by this acquisition.

## 4. REGPJ schema and territorial hierarchy

One XLSX sheet **`REGPJ`**, one header + **7,216 data rows**. All 15 columns:

```text
RSUJ2 | NAZRSUJ2 | RSUJ3 | KRJ | NAZKRJ = NAZRSUJ3 | OKS | LSUJ1 |
NAZOKS = NAZLSUJ1 | LSUJ2 | ICZUJ | NAZZUJ = NAZLSUJ2 |
ICUTJ | NAZUTJ | ICZSJ | NAZZSJ
```

The official page defines **LŠÚJ2** as municipality, Bratislava/Košice city
district, or military district; **ÚTJ** as cadastral territory; **ZSJ** as
settlement locality or urban district in selected cities. There is **no per-row
subtype flag** distinguishing the latter two: do not invent separate settlement
or urban-district tables. No streets, street IDs, address points, street-to-LŠÚJ2
relations, coordinates, validity dates, history flags or certified dataset as-of.

| Representation | Observed identifiers / relationship |
| --- | --- |
| RŠÚJ2 | Four `RSUJ2` codes/names, e.g. `SK01`; not the eight-region level |
| Region | Eight `RSUJ3` codes (OpenSK region IDs), explicit `KRJ` and names |
| District / LŠÚJ1 | 79 `OKS` statistical codes and 79 `LSUJ1` source-form codes/names |
| Municipality / LŠÚJ2 | 2,927 six-digit `ICZUJ` codes; `LSUJ2` is a 12-character composite; parent district and region supplied in **the same row** |
| Cadastral territory / ÚTJ | 3,532 six-digit `ICUTJ`; each has one explicit ICZUJ parent in this capture |
| ZSJ | 7,033 five-digit stored `ICZSJ` values; **127 occur under multiple ICZUJ parents** |

Flattened rows explicitly associate ICZSJ/ICUTJ with ICZUJ/OKS/RSUJ3. Joins use
those supplied columns, **not similar code prefixes**. Composite equality is
checked as corroboration, not used to manufacture parentage. The relation is not
a universal ZSJ → single municipality tree: preserve **all** published parent
paths. Names are not globally unique. There are **28 identical repeated rows**
(26 groups), leaving **7,188 distinct relationship rows**. They add no independent
identities; contradictory duplicate administrative/cadastral identities fail.
ZSJ **22699** has two names under the same municipality in different cadastral
rows: `Sídlisko osloboditeľov` / `Sídlisko osloboditeľov I`. Neither is repaired
or treated as an undocumented alias. ZSJ multi-parent rows are retained, not errors.

### Exact evidence method

1. Verify explicit local manifests/hashes/sizes and reviewed workbook/schema.
2. Reconcile each ICZUJ to current OpenSK code; validate supplied OKS/region via
   successor county evidence and current OpenSK relationships. Validate the
   source-form LŠÚJ1 column against that county evidence.
3. Compare the **entire** postal locality against LŠÚJ2, ÚTJ and ZSJ names.
   Allowed normalization: NFC, casefold, collapsed whitespace, three reviewed
   Unicode dash variants and spaces around a dash. Preserve other punctuation
   and word boundaries. No prefix/suffix stripping or abbreviation expansion.
4. Use postal district and region as exact context where supplied; street rows
   have no district. Region-only matches retain every candidate in that region.
5. Alternatively match an entire published postal part label, follow its explicit
   `miestne časti` parent and district, then require that **full parent name** to
   match REGPJ LŠÚJ2. No delivery-post or generic paired-column inference.
6. Union all explicit paths. Multiple parents stay ambiguous. Disjoint direct
   versus postal-parent paths are a source-path conflict, never source voting.
7. Emit full source row references/unit IDs/parent codes and snapshot validity
   qualification. Only one surviving structural parent gets
   `AUTHORITATIVE_DETERMINISTIC`; **this label does not certify current containment
   or approve production**. Invalid/historic units with explicit end dates (in
   synthetic controls) are excluded; the actual archive has no such fields.

Raw `obec` versus `detail_sc` does not identify which homonymous REGPJ unit type
was intended. Therefore a municipality-name match is not allowed to silently
override a different exact ZSJ/cadastral parent. This conservative ambiguity is
part of the measured ceiling, not hidden loss.

## 5. OpenSK municipality reconciliation

**2,927/2,927 exact six-digit administrative IDs**, **zero missing/extra**; all
district/region relationships agree with current successor-backed OpenSK geography.
All corresponding LŠÚJ2 composite/source district representations agree with the
fresh county/town profile. There is no foreign pseudo administrative unit in this
archive; no history marker permits silently selecting old/current duplicate rows.

Bratislava has **17** canonical borough IDs, Košice **22**, not aggregate city IDs.
Three military units are explicit: **500267 Záhorie**, **518581 Lešť**, **518638
Valaškovce** (each named `vojenský obvod`). Javorina is not in this file/current
OpenSK set; do not reintroduce it. These findings validate administrative code
reconciliation, **not current cadastral/ZSJ containment over time**.

One REGPJ administrative label differs from **all** fresh successor title fields:
**599913**, REGPJ `Vyšné Opátske`, current `Košice - mestská časť Vyšné Opátske`.
Its exact ID and relationships reconcile; no heuristic prefix removal or rename
is needed. Nothing rewrites municipalities/districts.

## 6. Non-street unresolved mappings

[Diagnostics A](psc-administrative-mapping-diagnostics.md#a-all-42-remaining-non-street-source-rows)
lists **all 42 source rows**, not just examples:

| Result among the 42 | Rows |
| --- | ---: |
| Direct REGPJ administrative match | 0 |
| ZSJ parent (also corroborated by ÚTJ) | **1** |
| Cadastral-only parent, excluding the same row above | 0 |
| Postal part + exact REGPJ administrative parent | 0 |
| Ambiguous | **1** |
| No exact contextual parent path | **40** |

**Nižné Valice, 98252, district 609** exactly matches REGPJ row **4785**:
ZSJ **24105** and ÚTJ **841056** both explicitly parent to ICZUJ **515795 Valice**.
No delivery-post inference was used (delivery post is Nižná Kaloša). The source
snapshot path is deterministic; current sub-municipal validity is still unknown.

**Kolónia, 07642, district 811** has ZSJ **20395 → 528188 Boťany** and ZSJ
**26868 → 543896 Veľké Trakany**, corroborated by postal-part rows 104/1592.
The PSC row provides **no distinguishing spatial-unit code**. Delivery post
Veľké Trakany cannot select one; it remains `AUTHORITATIVE_BUT_AMBIGUOUS`.

The remaining full labels have no exact path in context, including composite
names for Tatry/local parts. A human may recognize a suffix, but stripping it
would manufacture a join. A lack of exact match does not prove the locality is
invalid, nonexistent or outside Slovakia. All 19 remaining `detail_sc` rows
remain unmatched; no approved default `dposta = posta` is introduced.

## 7. Street-only PSC mappings

All **122** street-only PSCs were re-evaluated without using street names.
The previous **59** complete candidates remain structurally complete: **54
single-municipality + five multi-municipality**. No additional PSC becomes complete.

[Diagnostics B](psc-administrative-mapping-diagnostics.md#b-all-63-previously-incomplete-street-only-pscs)
covers all **63** previous incomplete cases:

| Mutually exclusive status | PSCs | Source rows / details |
| --- | ---: | --- |
| Newly fully mapped | **0** | None |
| Partly mapped | **2** | `96001`: 182/184 rows; `96221`: 6/16 rows; 12 remaining ambiguous rows combined |
| Ambiguous-only with no mapped rows | **0** | Ambiguity is contained in the two partial PSCs, not counted twice |
| Blocked by aggregate-city/missing street-admin hierarchy | **61** | 2,941 rows, no borough parent |
| Other wholly unmatched | **0** | None |

Total for these 63: **3,141 rows**, **188 structurally mapped**, **12 ambiguous**,
**2,941 semantically insufficient**. Across all 122: **5,770 rows**, **2,817
mapped**, **12 ambiguous**, **2,941 insufficient**. No street code/delivery-post
shortcut makes a partial PSC complete. Report JSON includes full label sets,
delivery-post counts, region-label sets, candidate municipality IDs and row-state
counts for all 122, plus the complete 1,415-PSC summary. Postal locality identity
is name-only in these rows; district is absent, so homonyms within one region
cannot be resolved merely because one candidate is geographically closer.

All **12** ambiguous street rows in those two partial PSCs are `Lieskovec` rows
with **no region as well as no district** (two in 96001, ten in 96221). The model
does not borrow a region from other rows sharing a PSC/delivery post. Non-null
region sets and missing-region counts are reported separately; region-only
filtering is used only for rows that actually supply it.

## 8. Bratislava and Košice

`Bratislava` and `Košice` denote aggregate postal city labels, not one canonical
OpenSK borough. Region corroborates the city area but cannot select among 17/22
administrative units. Assigning every city-labelled PSC to all boroughs would
invent occurrence in boroughs not established by source data.

REGPJ has no street/identifier/address table. Therefore it cannot establish
street → borough for these assignments. The full source has **3,096 aggregate
city street rows** (more than the 2,941 in street-only PSCs); some occur in PSCs
also having non-street records, so only auditing the 122 would miss that gap.

### Conditional official address-register fallback

Only after the REGPJ gap was established, rechecked official MV pages:
[overview](https://pes.minv.sk/wps/wcm/connect/sk/site/main/zivotne-situacie/Register%20adries/uvod-register%20adries),
[reference-data service](https://pes.minv.sk/wps/wcm/connect/sk/site/main/zivotne-situacie/Register%2Badries/poskytovanie_referencnych_udajov/)
and their official portal navigation. Current pages expose breadcrumbs/login or
portal home, not a documented downloadable national street/admin crosswalk.
The earlier [0.17.0 evidence](streets-source.md) documented eID/electronic-mailbox
delivery, not anonymous bulk acquisition. No new authorized export/schema/reuse
grant was established in this bounded recheck. A targeted national-catalogue
search did not establish a distribution; that is **not proof none exists**.

Fallback remains **BLOCKED** for this workflow. An official street-ID → borough
hierarchy is a potential future path **only with** documented identifiers,
reproducible acquisition and separately verified reuse/privacy minimization.
No private frontend endpoint, unofficial maps/geocoders or address-point/person
data was queried, acquired or used. Third-party `registeradries.sk` remains excluded.

## 9. Postal locality-part evidence

`miestne časti` explicitly supplies full local-part → parent label, district,
region and a type column; it is better evidence than guessing what `DOBEC` or
delivery post means. But postal and administrative parentage are not guaranteed
interchangeable. Both steps must survive independent REGPJ reconciliation.

Critical **new conflict**, outside the remaining 42: **93052, Orechová Potôň-Lúky**.
Postal sheet row **1061** places it under **Orechová Potôň**, whose REGPJ LŠÚJ2
ID is **501859** (rows 560–563). Direct full-label equality (reviewed dash spacing)
finds REGPJ ZSJ **24427** in row **625**, cadastral **844276 Blatná lúka**, under
**555746 Vieska** in the same district. Both paths have explicit source evidence;
there is no authoritative distinguishing key in the PSC row. Classify
**SOURCE_CONFLICT**, do not vote or silently keep 0.23.9's unique postal candidate.

The 26 earlier basic-sheet paired-label candidates are **not** approved merely
because an adjoining publisher cell has a familiar full municipality name.
The needed administrative-alias/parent semantics are not documented by a general
abbreviation expansion rule. In the strict exact-chain model they remain
`NO_MATCH`; the 15 punctuation-normalized official titles obtain structural
REGPJ paths. This is evidence refinement, not unexplained count reinterpretation.

`detail SČ` also has `miestne pomenovanie` and house-number columns. The 19
remaining composite-label detail rows provide no new exact full locality-to-REGPJ
parent via that naming cell; house ranges are not parsed as identity clues.
No street/house data is emitted. Full-layer candidate disagreements are retained
even when one path is administrative and another is a same-named ZSJ.

## 10. Conflicts and temporal alignment

- **One disjoint direct/postal-parent path conflict** (93052 above); 105 other
  ambiguous assignment rows have multiple same-name/explicit-parent candidates.
  These are not proof that a particular source is factually wrong: concepts,
  name collisions or dates may differ. Source voting is prohibited.
- **45 postal district-label differences** under exact normalization: 37 use
  `Nové Mesto n.Váhom` versus the full district name; eight others include Lešť
  labels in a district column, Raková composite notes, Handlová in the Ráztočno
  rows, and **detail row 158** labelled district `Poprad` with code **505** for
  `Vysoké Tatry-Podbanské`. These are **diagnostic label differences**, not 45
  proven wrong-code findings. No abbreviation expansion or code/label override
  is performed. The latter composite case remains unresolved.
- **127 ZSJ codes have multiple administrative parents**; **28 duplicate full
  relationship rows** and one two-name ZSJ code are explicitly accounted for.
- Administrative IDs/relationships all agree current-to-snapshot, but that does
  not prove all lower-level ZSJ/cadastral parentage is unchanged since capture.

REGPJ has **no certified current/as-of date or history filter** in the download.
Its file-save proxy is **878 days before** postal file-save dates, **899 days
before acquisition**; the REGPJ page date is 424 days before acquisition. These
are **metadata age gaps, not certified data-age calculations**. The title year
2020 is not used as legal validity. The administrative ID set is unchanged;
currentness of affected lower-level relationships (including Nižné Valice and
the Orechová Potôň-Lúky disagreement) remains **UNKNOWN** without dated change
records. No claim is made that they definitely changed or definitely did not.
PortalVS source-page content change and fresh valid town/county filters provide
separate current source context, not missing validity for REGPJ or PSC assignments.

## 11. Reuse and licensing

No correspondence was sent. Existing PortalVS/telecom/ŠÚ SR outreach states stay
unchanged; NBS remains resolved. Research does not upgrade any production registry.

| Source | Owner / exact terms evidence | Reuse assessment |
| --- | --- | --- |
| REGPJ | ŠÚ SR; [official general terms](https://slovak.statistics.sk/wps/portal/ext/aboutus/webpage/terms/), page updated **2026-10-13**, permits copying/public communication/commercial use with attribution, CC BY 4.0 link, no endorsement; excludes third-party intellectual property and liability | **PENDING for this specific register chain**. General open policy is positively identified, but no register-specific declaration or coverage of contributed cadastral/ZSJ material was established. CC BY permits adaptation within its covered scope; do not infer that every third-party element is covered. |
| Postal ZIP | Slovenská pošta; [lookup/download page](https://www.posta.sk/psc), `OBCE.xlsx/popis`, [general service-terms page](https://www.posta.sk/podpora/postove-obchodne-a-financne-podmienky) | **UNKNOWN** for redistribution, commercial downstream use and transformed public API. `popis` offers free lookup/download, explains completeness/cadence, but provides no explicit open licence/attribution or transformation grant. Service conditions are not a verified dataset licence. No numeric automation permission established; only a bounded public download was made, no interactive scraping. |
| PortalVS PSC | MŠVVaM/PortalVS, postal underlying source; [copyright page](https://www.portalvs.sk/sk/autorske-prava), checked 2026-10-16T08:46:00Z, 36,987 bytes, hash `88559df11aba1596ebd03d456ce3b2a236a3ab3cd47e666027f3523b868f0820` | **PENDING / SENT_AWAITING_REPLY**. Same `iba k nekomerčnému použitiu` wording and notice-preservation condition. No separate successor PSC licence verified. Commercial redistribution/transformation clarification not received. |

**Material policy observation, not an outreach resolution:** current ŠÚ SR terms
prohibit robots/crawlers downloading **in a manner causing high load, instability
or restricted availability**, rather than the earlier recorded blanket wording.
This narrower current text is recorded here; it does not establish dataset-specific
third-party coverage, bypass Cloudflare, or change the pending elections outreach.
Manual REGPJ download avoided the technical challenge; no bulk crawler was added.

If the maintainer later chooses to ask: seek REGPJ effective date/history and
register-specific CC BY/third-party scope; postal ZIP commercial redistribution,
transformation/attribution conditions, column semantics and the conflicting
part/administrative path. The source-owner pages identify the responsible
institutions. **No email is drafted as sent or dispatched automatically.**

## 12. Mapping coverage ceiling

These are **snapshot-qualified exact-chain structural counts**, not a certified
current crosswalk, national-address coverage or an approved import. The 0.23.9
candidate model and the stricter all-unit model are deliberately not interchangeable.

| All successor PSCs (1,415) | Count |
| --- | ---: |
| All source rows have one non-conflicting structural parent | **1,228** |
| Some but not all rows have one parent | **105** |
| No structurally mapped rows | **82** |
| Multiple known municipalities, including partial PSCs | **745** |
| Multiple known municipalities among complete PSCs | **678** |
| PSCs with street-scoped assignments | **208** |
| PSCs with `detail_sc` / house-number scope | **145** |
| PSCs with street **or** house-number scope (union) | **339** |

The last five overlap the first three and each other. `82` includes more than the
61 aggregate-city street-only cases; not all no-map codes are street-only. Full
1,415-PSC summaries are in generated JSON, not a copied street dump in Git.

| Source rows | Unique structural parent | Ambiguous | No exact path | Aggregate-city insufficient | Path conflict | Total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `obec` | 2,670 | 72 | 47 | 0 | 1 | 2,790 |
| `detail_sc` | 150 | 4 | 19 | 0 | 0 | 173 |
| `ulica` | 7,612 | 29 | 0 | 3,096 | 0 | 10,737 |
| **Total** | **10,432** | **105** | **66** | **3,096** | **1** | **13,700** |

This is the maximum **under the reviewed exact evidence method**, not a proof
that future authoritative identifiers could never improve it. Unknown REGPJ
temporal validity qualifies every structural count; **no current production-ready
PSC projection is approved**. Excluding an inconvenient category or ambiguous
row was not accepted as a product coverage policy, so there is no implicit
`MAPPING_COMPLETE_WITH_EXPLICIT_EXCLUSIONS` or GO_PARTIAL decision.

## 13. Product semantic implications

Verdict: **CONTRACT_CLARIFICATION_REQUIRED**. A defensible eventual wording is
"this PSC occurs at one or more addresses/localities within this administrative
municipality," only after identity/containment and temporal scope are established.
It is **not** "this PSC is valid for all addresses in that municipality."

| Type | Truthful possible occurrence claim after identity proof | Must not claim after discarding detail |
| --- | --- | --- |
| `obec` | Publisher reports a territorial postal assignment for this mapped municipality/locality | A sole canonical postcode or universal municipality-wide address validity without that evidence |
| `detail_sc` | Some house-number-scoped addresses/localities in the mapped municipality use the PSC | Address-wide validity; house-number distinctions are essential to exact address lookup |
| `ulica` | Some street/address-scoped occurrences in the mapped municipality use the PSC | Borough containment from aggregate city/delivery post; universal validity after stripping street/orientation detail |

Current API is a partial postal-code lookup supporting multiple administrative
matches, not address validation; `city` represents delivery-post presentation,
not a parent municipality. Existing docs do not positively establish the
existential/address-scope caveat needed for a new street-derived occurrence model.
A future contract proposal must document coverage, scope/deduplication/counting
and not-found semantics explicitly. No runtime/docs contract wording is silently
changed by this spike; these are research conclusions only.

Existing grouped lookup/count discrepancy (§3 of the 0.23.9 document):
**BLOCKS_MIGRATION** of a truthful new multi-occurrence dataset until reviewed
and corrected before promotion (could be a separately reviewed precursor or
part of an authorized future migration). It exists independently today; no bug
fix belongs here. `01001` still has one outer grouped lookup match containing
two stored/collection matches. Do not interpret that current count as new coverage.

## 14. Future source strategy

**NO_SOURCE_READY** now. Technically the official postal ZIP is a
**POST_PRIMARY_SOURCE_CANDIDATE**: postal authority, documented territorial versus
P.O.BOX scope, at-least-monthly stated cadence, reproducible currently working
public ZIP, observed stable sheet structure and full assignment content. All
2,790/173/10,737 corresponding PortalVS signatures were corroborated in 0.23.9;
fresh identical bytes reproduce that lineage. The versionless download can move
or change schema, offers no certified assignment validity and has unverified
redistribution/transformation rights. It is not automatically promotion-ready.

PortalVS offers convenient documented JSON/ETags but reproduces postal labels
without administrative codes and with unresolved rights. REGPJ offers spatial
parentage, not postal authority/current address scope. **Combined evidence is
needed to investigate containment**, but combining sources cannot erase
conflicts, temporal gaps or any source's conditions. No primary source or
production identity was switched.

## 15. Remaining blockers

1. **40 of the target 42 source rows still have no exact contextual spatial path;
   Kolónia stays ambiguous.** The single new path lacks certified lower-level
   currentness. Composite/abbreviated postal labels need identifiers or an
   authoritative explicit alias relation, not text surgery.
2. Aggregate Bratislava/Košice labels lack borough identity; no reproducibly
   approved official street/admin hierarchy was obtained. Two other incomplete
   street-only PSCs retain ambiguous rows.
3. Postal-part versus REGPJ path disagreement for Orechová Potôň-Lúky, multiple
   ZSJ parents/name collisions and unknown temporal validity cannot be voted away.
4. Postal ZIP/PortalVS reuse and register-specific scope remain uncleared.
5. Occurrence-only contract clarification and the grouped lookup count issue
   would still be required even after a complete, dated crosswalk existed.

## 16. Recommended next milestone

**NO_GO_SUCCESSOR_PSC. Park PSC and proceed to a developer adoption / OpenAPI
correctness pass.** Do not preselect 0.23.12 PSC production, a contract redesign
without mappings, or another speculative evidence task. Keep historical PSC
production and current successor geography unchanged, with no runtime dependency
on either source host.

Reopen PSC only upon a specific new authoritative distinguishing crosswalk,
dated spatial/address hierarchy or source-owner clarification. Future work may
evaluate it against these negative controls, but no automatic outreach is authorized.

Offline reproduction (all inputs explicit; external/ignored output only):

```powershell
python scripts/analyze_psc_administrative_mapping.py --portalvs-manifest "C:\Users\matej\AppData\Local\Temp\opencode\psc-02311\portalvs\manifest.json" --portalvs-capture "C:\Users\matej\AppData\Local\Temp\opencode\psc-02311\portalvs" --regpj-zip "C:\Users\matej\AppData\Local\Temp\opencode\psc-02311\REGPJ2020.zip" --post-zip "C:\Users\matej\AppData\Local\Temp\opencode\psc-02311\post-psc.zip" --evidence-manifest docs/research/psc-administrative-mapping-acquisition.json --output "C:\Users\matej\AppData\Local\Temp\opencode\psc-02311\mapping-analysis.json"
```

No network or production writer/flag. Exact member/schema/hash validation,
explicit-parent checks and deterministic JSON. The analyzer reuses the prior
baseline helper solely to reproduce its historical counts, not approve its
publisher candidates. Tests generate small synthetic archives and need no retained
raw files. Fresh future evidence requires an explicitly reviewed new manifest;
neither runtime nor future tests require the private 0.23.9/0.23.11 captures.

## 17. Validation and production safety

Branch `research/psc-administrative-mapping`, base main **0.23.10** / PR #37,
`670237a69755d04c7396f686dc8d72319ad50c53`. Final project version **0.23.11**,
API namespace `/v1`, envelope metadata version `v1`, **39 GET operations**.

All **14 production JSON files must remain byte-identical**. Acquisition-host
Windows working-tree SHA-256 before/after (Git/LF can differ only in checkout encoding):

| Protected file | Unchanged Windows SHA-256 |
| --- | --- |
| `data/psc.json` | `4b7346bbef19a86576fa5ecaa5f7d7c2afa36be5ff711753281b3a042b42bc55` |
| `data/districts.json` | `9b7fd0752b416383d6fc7247555614b040a91d7f789a9bf82baa4bd245efe66b` |
| `data/municipalities.json` | `d5a7209d18eb1506f573f7b95550d63cbb99598c96686b76cf5b16270de01c95` |
| `data/sources.json` | `6451f423077f2e13933dbaa5a2810c99d56bacba9205db9ec714f0d401055f9d` |

PSC Git/LF blob hash remains
`db9cd5c2d833cec0d199f4a7199f9c13f77346572bbd1507503ce01774b0dc24`.
All five legacy-only PSCs, embedded labels/validity, registry entry, freshness,
grouping/matchCount and cache behavior remain untouched. No district/municipality
rematerialization, source-registry promotion, street API, DB, Redis, SDK,
scheduled/manual-outreach dispatch or runtime upstream code was added.

Local final gates (2026-10-16):

- `python scripts/validate_datasets.py`: **0 errors / 44 existing warnings**, 14
  datasets; no rights/coverage warning suppressed.
- `python scripts/check_referential_integrity.py`: passed.
- `python -m pytest -q`: **834 passed** including **35 new synthetic evidence and
  negative-control cases**; no live calls or retained official archives required.
- `python -m compileall scripts routers services tests schemas`: passed.
- `git diff --check`: passed; full-branch/staged checks before push.
- Local HTTP smoke (`scripts/smoke_test.py`): **41 passed / 0 failed**.
- All 14 production JSON byte hashes match the pre-work main baseline. `data/`,
  routers/services/schemas, dependency files and outreach package have no diff.
- **39 GET operations**, project **0.23.11**, `/v1` and metadata version **v1**;
  PSC conditional caching/freshness checked unchanged.
- All **105 curated blocker table rows** exactly checked against the generated
  evidence report, including missing region context. Full analysis repeated
  byte-identically with network access forbidden. Acquisition-host canonical
  report SHA-256:
  `ba1a23524047474a3034e97c322b927af6e1bb84c986d0987dbc743ee98ef5e8`.

Hosted CI is reported by PR checks separately from local results. No auto-merge,
tag, release, production deployment or source promotion is part of this spike.
