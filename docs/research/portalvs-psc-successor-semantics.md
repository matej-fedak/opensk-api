# 0.23.9 — PortalVS PSC Semantics & Successor Mapping Spike

> **Follow-up, 0.23.11:** [administrative mapping evidence](psc-administrative-mapping.md)
> reproduces these historical counts, then tests explicit REGPJ paths. One of
> the remaining 42 rows gains a snapshot-qualified parent; Kolónia stays ambiguous,
> 40 stay unmatched, and the previously unique Orechová Potôň-Lúky postal-part
> candidate has conflicting REGPJ parent evidence. No candidate here was approved
> automatically. PSC remains unchanged / `NO_GO_SUCCESSOR_PSC`; geography alone
> migrated in 0.23.10. The historical analysis below is retained, not overwritten.

**RESEARCH ONLY — NO PRODUCTION DATA MIGRATION — NO CURRENT SOURCE REGISTRY
PROMOTION — NO ROUTE CHANGES — NO LICENCE INFERENCE.** Evidence checked 2026-10-15.

## 1. Executive decision

- **PSC: `NO_GO_SUCCESSOR_PSC`.** Postal assignment semantics are now better
  evidenced, but administrative mappings and a truthful complete-enough projection
  remain unresolved. Neither full nor partial promotion is approved.
- **DISTRICTS: `GO_PRODUCTION_NEXT` (`DISTRICTS_GO`).** All 79 identities, names
  and region links reconcile; all 12 re-letterings are deterministic.
- **MUNICIPALITIES: `GO_PRODUCTION_NEXT` (`MUNICIPALITIES_GO`).** All 2,927 IDs
  and district/region links reconcile. Two presentation differences have been
  reviewed below; no guessed identities are needed.
- Recommend **0.23.10 — PortalVS Successor Geography Migration**, districts and
  municipalities only, with PSC explicitly remaining legacy-backed. This is
  technical feasibility, **not rights clearance** or permission to promote publicly.

The 0.23.3 feasibility verdict was sample-level and overstated PSC readiness.
In particular, excluding street rows does **not** retain all 1,415 successor PSCs,
and `obce` is not always a canonical administrative municipality. This full-source
audit supersedes those PSC assumptions, not the historical evidence capture.

## 2. Source snapshot

Retained acquisition: `C:\Users\matej\AppData\Local\Temp\opencode\portalvs-0239\`.
Three-array manifest acquisition timestamp: **2026-10-15T19:08:55Z** (completion
time, not a legal validity date). Manifest SHA-256:
`e0ffc341f1e65641187e7e0948fb1dd7b866f7e20e278dab6f37b8da1673afb5`.

| Official URL | Rows | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| https://ciselniky2.portalvs.sk/api/county.json?validity=valid | 80 | 30,459 | `308d1b35a2bbd7a82fa99966a8cac4d044fd62aa19ae249db36d864179d36194` |
| https://ciselniky2.portalvs.sk/api/town.json?validity=valid | 2,928 | 1,105,510 | `5e13f5162f560d9d4409d91aad26569e7fe21f8342b78fc25179a0574630ad94` |
| https://ciselniky2.portalvs.sk/api/postal_code_sk.json | 13,700 | 2,525,777 | `e4c83b436c058b5b8bc8c34ef5432a9f17c1a0ce2a46a8e4039a5a42b77ff96f` |

Each returned HTTP 200 JSON, one complete array, with ETags respectively
`"10ce57242fccfa16"`, `"a4aeef064766d663"`, `"caaf11e7581eb87f"`.
PSC types: **2,790 `obec`, 173 `detail_sc`, 10,737 `ulica`**. There are
**1,415** source PSCs; **2,963** non-street rows cover **1,293** PSCs; **122**
PSCs occur only in street rows. These reproduce the paused acquisition findings.

Authoritative evidence (no search-result snippet is used as proof):

- [Successor OpenAPI](https://ciselniky2.portalvs.sk/api/docs.json), version
  1.0.0, 473,638 bytes, SHA-256
  `a1e6373bf76b3c7f20c085314bd939f6b4784191b50b832668f2bfa76edc5860`.
  PSC schema describes fields and an enum, not a full record-type ontology.
- [PSČ slovenské classifier](https://ciselniky2.portalvs.sk/ciselniky/psc-sk),
  checked 19:21:50Z, identifies **Slovenská pošta** as source. SHA-256
  `e4180b03bf6de8764b6c3e29023071731c071c7dd167b1d43a42193a52ef180f`.
- [Town classifier](https://ciselniky2.portalvs.sk/ciselniky/slovenske-obce),
  checked 19:21:51Z, SHA-256
  `0c7fcff94a869643e1f4be24e03e37f7544af6ddebec40880fc3e5001af789b6`.
- [Official postal lookup](https://www.posta.sk/psc), checked 19:21:50Z,
  SHA-256 `588b4cbf2fa7e76a97585765c3b4033e96833cb8d481cfd8ca19524256ba6445`,
  links [the downloadable postcode ZIP](https://www.posta.sk/files/6811e10125b182cd7cd9e3a9/postove-smerovacie-cisla-na-stiahnutie.zip).
  ZIP acquired **19:22:05Z**, HTTP 200, 731,276 bytes, SHA-256
  `7f9e3686df8c3f67ca121f8581f334e9c5dd5b28cec7b97e106e3b73a356d54c`.
  Contains `OBCE.xlsx`, `ULICE.xlsx`, `POBoxy.xlsx`. No interactive results were
  scraped, no scale queries were made, and no workbook author metadata is published.
- `OBCE.xlsx` sheets **`popis`**, **`obce`**, **`detail SČ`**, **`miestne časti`**
  supply publisher prose and explicit postal/locality relationships. There are
  2,953 basic locality rows, 173 detailed assignment rows and 1,281 non-self
  locality-part relations in the analyzer's reviewed field selection. Basic rows
  include references to detail lists, not 2,953 five-digit assignments.
- All **2,790** successor `obec` rows match publisher basic-sheet signatures
  (PSC, postal locality, delivery locality, delivery post). All **173** `detail_sc`
  rows match (PSC, locality, district, post). All **10,737** `ulica` rows match
  `ULICE.xlsx` (locality, street, PSC, delivery post); only the equality count is
  emitted, never street values or their hashes. This corroborates the source
  lineage and type interpretation; it is not a municipality-code crosswalk.
- [Postal developer documentation](https://www.posta.sk/podpora/dokumentacia-pre-vyvojarov),
  checked 19:21:50Z, SHA-256
  `6795ed8ea6975bdc600fe0cbed590eeeec38e30abd4cffc057b94f9f69f5a338`.
  Public pickup-point XML feeds and shipping APIs are not an administrative PSC
  crosswalk. No additional documented postcode API with cleared redistribution
  rights was established in this bounded review.

The official ZIP is a useful **future source candidate**, not a source switch.
Its `popis` offers free lookup/download and says updates are generally at least
monthly. That does **not** establish commercial redistribution/relicensing rights;
clearer reuse rights remain **UNKNOWN**.

## 3. Current OpenSK PSC contract semantics

Audited `routers/psc.py`, `services/psc_service.py`, `schemas/common.py`, README
PSC examples/limitations, `docs/api-status.md`, `docs/data-sources.md`,
`docs/dataset-format.md`, `tests/test_app.py`, `tests/test_import_psc.py`.
No typed PSC entity schema promises municipality-wide validity.

- `/v1/psc/{psc}` is explicitly **"Postal code lookup"**, a local partial
  snapshot lookup, not address validation or a municipality's sole canonical PSC.
  Not-found means no local data, not a legal declaration that a PSC is invalid.
- The intended `matches` relationship is postal code occurrence associated with
  locality/delivery post and an administrative municipality where known.
  It does **not explicitly** assert validity for every address in that municipality.
  However, existing wording does not positively explain existential/street-scoped
  semantics either. It must not silently acquire that stronger interpretation.
- `municipality`/`municipalityCode` refer to local administrative geography;
  `city` is a legacy presentation field: **all 3,101 stored matches have
  `city == deliveryPost`**, not necessarily the administrative municipality name.
  Delivery-post labels must never be used as proof of municipal containment.
- Collection/search flatten the stored `matches` arrays; multiple municipalities
  per PSC already exist. Example `01001` has two stored/collection matches,
  Žilina (`517402`) and Žilinská Lehota (`517801`). This proves multiplicity, not
  municipality-wide validity or arbitrary sub-municipality-to-borough mapping.
- **Existing implementation discrepancy, not fixed here:** lookup indexing reads
  grouped source entries, unlike collection flattening. For `01001`, the live
  local service reports top-level `matchCount == 1` and one outer `matches` entry
  containing the two stored matches. Thus current lookup count is not reliable
  evidence of administrative coverage. Existing tests cover examples and synthetic
  repeated flat records, not a guarantee that every grouped lookup is flattened.
  Track a separate contract-correctness review; no runtime shape/count fix belongs
  in this research spike.

Conclusion: a **carefully documented occurrence-only** street-free projection
could fit the intended lookup concept; the current API is **not sufficient proof**
that silently collapsing any street assignment is safe. Neither street nor house
detail may be discarded while claiming full-address or municipality-wide validity.

## 4. Successor record-type semantics

`obce` is a **field**; `obec` (singular) is the actual enum value. OpenAPI alone
only labels `typZaznamu` "Typ záznamu". The postal publisher's `popis` provides
the substantive context, corroborated by full signature comparisons above:

| Type | Entity/assignment evidenced | Administrative or locality level? | Street context required? | Remaining UNKNOWN |
| --- | --- | --- | --- | --- |
| `obec` | Basic territorial postcode assignment from the basic locality list | Municipality **or some municipality parts**, not guaranteed administrative municipality | No street for the basic assignment; publisher refers elsewhere where addresses need finer detail | Formal guarantee that every label is an administrative identity/alias; universal municipality-wide coverage |
| `detail_sc` | Territorial postcode detail by **súpisné číslo**, for municipalities without a street system having several postcodes/delivery posts | Locality/address-number subset, **not** a municipality-wide assignment | Street not required; **house-number context matters** | Complete lossless field mapping of detailed ranges; treating `posta` as an interchangeable `dposta` |
| `ulica` | Territorial postcode assignment in a street list, potentially differentiated by orientation number | Street/address subset of postal locality, not inherently an administrative borough | **Yes for choosing the correct address PSC**; orientation numbers can also matter | Canonical administrative municipality/borough for every row; a formal successor-specific contract for collapsed projections |

Publisher `popis`: "Územné PSČ sú zverejňované v súboroch: OBCE.xls a ULICE.xls";
the prose uses historical `.xls` names while the linked ZIP contains `.xlsx`.
It says `detail SČ` is needed for an address and its specific súpisné číslo where
there is no street system and more than one PSC; the street list must be checked
for street/orientation-number addresses with more than one territorial PSC.
It separately describes P.O.BOX postcodes; those are **not** equated to territorial
assignments here.

Types can coexist for one PSC. Observed PSC distribution by type combination:

| Types present | PSC count |
| --- | ---: |
| `obec` only | 1,076 |
| `detail_sc` only | 32 |
| `ulica` only | 122 |
| `obec` + `detail_sc` | 99 |
| `obec` + `ulica` | 72 |
| `detail_sc` + `ulica` | 5 |
| all three | 9 |

Omission from non-street rows therefore **does not establish invalidity**: all 122
street-only PSCs have official street assignment evidence. It also does not by
itself prove that an entire municipality has that PSC. The publisher says street
lists are not supplied for other municipalities with one delivery post and one
PSC for all addresses; absence of street rows is not evidence of no streets.

All 10,737 street rows omit `kodOkresu`; 12 also omit `kraj`. Three non-street
rows omit `kraj`, but all 2,963 supply a district. Supplied district/region context
has zero conflicts in the reviewed comparison. All `detail_sc` rows lack `dposta`
but supply `posta`; no automatic fallback is approved. Successor PSC assignment
validity dates are absent: a future projection must use null, not legacy dates,
translation validity dates, workbook modification dates or acquisition time.

## 5. Non-street unresolved analysis

Baseline exact title aliases = successor `officialTitle`, `mediumTitle`,
`shortTitle`, NFC and whitespace normalization, **plus district context**.
Reproduced **84 rows: 65 `obec`, 19 `detail_sc`; 82 pairs; 69 PSCs**; zero
ambiguous baseline joins and zero region conflicts. All 84 have zero exact
candidates; no previous guessed mappings were silently carried forward.

[Diagnostics table A](portalvs-psc-successor-diagnostics.md#a-all-82-unresolved-localitydistrict-pairs-84-rows)
records every pair, types, PSCs, district/region, normalized candidates and
publisher evidence row references. JSON adds all relevant candidate town fields.

| Research classification | Pairs | Source rows | Meaning |
| --- | ---: | ---: | --- |
| `ALTERNATE_OFFICIAL_NAME` | 15 | 15 | Exact normalized published town title; punctuation/case/space only |
| `DELIVERY_LOCALITY` | 26 | 26 | Official postal paired-label candidate; not an approved administrative alias |
| `MUNICIPALITY_PART` | 1 | 1 | Explicit publisher part relation yields one candidate |
| `AMBIGUOUS` | 1 | 1 | Publisher lists Kolónia under two municipalities in the same district |
| `UNRESOLVED` | 39 | 41 | No candidate established by these exact checks |

Thus **0 new baseline exact joins**, **15 normalized-title candidates**, **27
additional unique publisher-backed candidates**, and **42 rows without a unique
candidate (41 unresolved + 1 ambiguous)**. Approved automatic mappings: **zero**.
No unsupported classification as `PSEUDO_LOCALITY`, `EXACT_MUNICIPALITY` or a
specific parent is made for the remaining rows. For example, a familiar composite
name or a locality repeated in a second district is not permission to strip a
prefix, split on a hyphen, repair spelling, override a district or infer containment.

## 6. Authoritative alias and locality evidence

Town OpenAPI documents `includes` = "Zahŕňa", `includesAlso` = "Zahŕňa aj",
`excludes` = "Nezahŕňa"; these are generic classification descriptions,
**not a documented structured alias/parent relation**. Across all 2,927 regular
town rows, all three are empty. `info` and `additionalInfo` each occur in 610
rows, holding language-name information in this snapshot, not a complete
municipality-parts crosswalk. `note` has the six-digit statistical identifier;
the generic OpenAPI calls it "Poznámka", so shape/uniqueness/reconciliation checks
are essential, not blind trust in that label. No documented alternative-name
field was established beyond the published title fields. These optional fields
do **not** solve the remaining identities.

Postal evidence is kept separate from successor-only matching:

- `Belá - Dulice` → published `Belá-Dulice` is a normalized title candidate,
  not a fuzzy correction. Diacritics are retained.
- `Bohdanovce n/Trnavou` pairs with `Bohdanovce nad Trnavou` on publisher
  basic-sheet row 140, with the same PSC/district. The script follows the
  **published pair**, never a general `n/` expansion rule. Class `DELIVERY_LOCALITY`
  acknowledges that paired postal labels do not formally guarantee administrative
  alias identity. The same constraint applies to the other 25 additional pairs.
- `Orechová Potôň-Lúky` is explicitly listed under `Orechová Potôň` in the
  official locality-parts sheet, row 1061; normalized parent title + correct
  district identifies candidate `501859`. This is stronger parent-locality evidence,
  still not a production mapping decision in this milestone.
- `Kolónia`, district 811, matches locality parts under both Boťany (`528188`,
  row 104) and Veľké Trakany (`543896`, row 1592). It remains ambiguous; delivery
  post or proximity must not choose a winner.

No individually invented aliases are committed. The analyzer compares full
labels (Unicode NFC, casefold, whitespace/punctuation only), never approximate
spelling, substrings, edit distance, district-only assignment or closest names.

## 7. Ulica-only PSC analysis

[Diagnostics table B](portalvs-psc-successor-diagnostics.md#b-all-122-ulica-only-pscs)
covers **every one of the 122 PSCs**: row/locality/district/delivery-post counts,
locality text, unique candidate IDs, missing/ambiguous row counts and class.

| Class | PSCs | Street rows | Interpretation |
| --- | ---: | ---: | --- |
| `SAFE_TO_COLLAPSE_CANDIDATE` | 54 | 1,611 | Every row has one normalized-title candidate and all point to one municipality |
| `MULTI_MUNICIPALITY` | 6 | 1,202 | At least two uniquely identified municipalities; five PSCs have complete candidate coverage |
| `AMBIGUOUS` | 1 | 16 | `96221`, Lieskovec has multiple same-region title candidates |
| `INSUFFICIENT_EVIDENCE` | 61 | 2,941 | No canonical candidate established, primarily aggregate Bratislava/Košice labels |

There are **5,770 street rows** in these PSCs. All 122 have one distinct delivery
post each, but that plainly does not imply one municipality. `02401`, `03601`,
`91701`, `94901`, `95141` have complete multi-municipality title candidates;
`96001` is multi-municipality but still has two ambiguous rows. **59**, not 60,
PSCs have complete candidate coverage across single/multi classifications.

Street rows supply **no district code**. A normalized title unique within the
supplied region can establish a **research candidate**; it cannot turn an aggregate
city into one of OpenSK's administrative boroughs. No street-to-borough matching
is attempted. The 54 CAND PSCs are candidates for further review, not a statement
that collapsed production responses are approved.

## 8. Risks of collapsing street assignments

Authoritative publisher evidence supports the **existence of territorial PSC
assignments** in street rows. Removing street detail can truthfully express
"this PSC occurs somewhere in municipality Y" **if** Y is deterministically
established and deduplication preserves that existential meaning. It cannot
express "use this PSC for any address in Y". `detail_sc` has the analogous
house-number problem even though it is not a street row.

The current intended lookup is compatible with multiplicity but lacks explicit
address-scope caveats, and its grouped lookup/count discrepancy complicates
coverage claims. Administrative mappings are still incomplete. Therefore:

1. Using a street row as research **input** is not a street API; no such input
   is imported or published here.
2. A future occurrence-only product decision would need explicit wording, no
   address-validation claim, reviewed locality/borough mappings, correct
   deduplication/count behavior, nullable validity dates and honest subset metadata.
3. Neither dropping street strings nor an existing "partial" disclaimer alone
   makes promotion semantically safe. Municipalities must not be broadened from
   postal localities or selected by delivery post.

## 9. District migration verdict

**`DISTRICTS_GO` / `GO_PRODUCTION_NEXT`**, independently of PSC (rights gate unchanged).

Full/valid/invalid probes: **81 / 80 / 1** source rows. Valid excludes the old
foreign pseudo row; exclude the remaining explicit foreign pseudo code to obtain
**79** Slovak districts. The in-memory prototype equals all 79 existing public
records (code/name/region/country); zero fuzzy joins, additions or removals.

Three-digit statistical `note` determines the region and district ordinal;
the successor suffix encodes ordinals 10–13 as A–D. Keep existing decimal public
IDs, verify both representations agree, fail on unknowns/duplicates:

| Successor | Public | Statistical | Successor | Public | Statistical |
| --- | --- | --- | --- | --- | --- |
| SK031A | SK03110 | 510 | SK031B | SK03111 | 511 |
| SK032A | SK03210 | 610 | SK032B | SK03211 | 611 |
| SK032C | SK03212 | 612 | SK032D | SK03213 | 613 |
| SK041A | SK04110 | 710 | SK041B | SK04111 | 711 |
| SK041C | SK04112 | 712 | SK041D | SK04113 | 713 |
| SK042A | SK04210 | 810 | SK042B | SK04211 | 811 |

Regions themselves are not rematerialized. No prototype has a production writer.

## 10. Municipality migration verdict

**`MUNICIPALITIES_GO` / `GO_PRODUCTION_NEXT`**, independently of PSC (rights gate unchanged).

Full/valid/invalid probes: **2,930 / 2,928 / 2**. The valid capture omits Javorina
(`523551`, retired 2010-12-31) and an old foreign pseudo row. Exclude the remaining
explicit foreign pseudo code: **2,927** regular municipalities. All six-digit
`note` IDs are present/unique, identical to current public IDs, and equal the
suffix of their composite source code. The district prefix must resolve exactly
via county source-code/statistical-code evidence. Zero ID additions/removals,
zero district/region changes; all **3,101 existing PSC match links** still resolve
to the same district/region IDs with prototype geography (zero failures).

205 municipality records require deterministic duplicate-name disambiguation:
published official title + ` (okres <district mediumTitle>)`. Exactly two names
differ from current presentation, reviewed as OpenSK suffix consistency rather
than administrative renames:

| ID | Existing name | Prototype name | Review |
| --- | --- | --- | --- |
| 504173 | `Vozokany (okres (Galanta)` | `Vozokany (okres Galanta)` | Existing unmatched parenthesis; successor title Vozokany, district Galanta |
| 504742 | `Radošovce (Skalica)` | `Radošovce (okres Skalica)` | Existing exceptional suffix; same published title and district, standardized suffix |

A future production PR should call out these two display changes explicitly (or
choose a reviewed presentation-preservation policy), without changing IDs or
silently rewriting legacy PSC labels. PSC provenance and its historical labels
must remain explicit; no hybrid PSC reconstruction is needed for geography alone.

## 11. PSC migration options

These are **diagnostic ceilings/counts, not approved outputs**:

| Strategy | Source rows retained/candidate | Distinct PSCs | Blocking issue |
| --- | ---: | ---: | --- |
| Baseline exact non-street titles + district | 2,879 | 1,277 | Drops 84 rows, 16 non-street PSCs entirely, all 122 street-only PSCs |
| Normalized published titles, non-street | 2,894 | 1,282 | Still drops 69 rows; type/delivery-post semantics and omitted coverage remain |
| Publisher-enriched **candidates**, non-street | 2,921 | 1,286 | 42 rows lack unique candidate; postal pairs not approved administrative aliases |
| All non-street, if every mapping were solved | 2,963 | 1,293 | Hypothetical; cannot cover the 122 street-only PSCs |
| All source PSCs including reviewed street evidence | 13,700 input rows | 1,415 | Missing borough/locality mappings and occurrence-only contract decision |

If the 54 single-municipality street-only candidates were eventually approved,
they would add 54 disjoint PSCs (e.g. 1,277 → 1,331 with the baseline subset).
Including the five completely mapped multi-municipality candidates would add 59
(1,277 → 1,336). These are arithmetic possibilities only, **not safe strategies
approved by this spike**; 63 street-only PSCs still lack complete candidates.

[Diagnostics table C](portalvs-psc-successor-diagnostics.md#c-all-69-affected-non-street-pscs)
quantifies all **69** non-street affected PSCs. **53** have some exact rows;
**16** disappear entirely if unresolved rows are dropped. Every unique enriched
candidate in these affected rows adds a municipality not already covered by an
exact row for that PSC; remaining rows have UNKNOWN additional coverage, never
assumed duplicates. Silent dropping would therefore hide known candidate coverage
and unresolved source assignments, not just harmless duplicates. Future
administrative `matchCount` needs explicit deduplication, and the existing lookup
count issue (§3) cannot be used to excuse undercoverage.

All five local-only PSCs remain absent from this full successor snapshot:
`83006`, `83155`, `91931`, `93539`, `97651`. Absence is established;
**retirement dates/legal retirement are UNKNOWN**. They remain in **unchanged
legacy production** solely because this is not a migration; no fallback/hybrid
output is approved. Future successor output must not preserve them without
successor evidence.

Final decision: **`NO_GO_SUCCESSOR_PSC`**, not `GO_PARTIAL_SUCCESSOR_PSC`.
Reduced coverage has not been accepted by a maintainer product decision, and
neither mapping completeness nor truthful current response semantics is established.

## 12. Rights and compliance state

Rechecked [PortalVS copyright](https://www.portalvs.sk/sk/autorske-prava) at
**2026-10-15T19:38:05Z**: HTTP 200, 36,987 bytes, SHA-256
`88559df11aba1596ebd03d456ce3b2a236a3ab3cd47e666027f3523b868f0820`,
byte-identical to the 19:07:11Z preparatory check. Text still says
**"iba k nekomerčnému použitiu"** and requires preservation of notices.
Successor OpenAPI has no separate licence. robots API allowance and successful
technical download are **not** redistribution permission.

PortalVS clarification sent **2026-10-11**, no reply supplied/recorded:
**`SENT_AWAITING_REPLY`**. Telecom and ŠÚ SR remain `SENT_AWAITING_REPLY`;
NBS remains `REPLY_RECEIVED_RESOLVED`. No email was sent, no permission inferred,
no outreach/compliance file or production registry state changed. Public
promotion remains gated. No broad legal analysis has been reopened.

## 13. Recommended next action

1. Queue **0.23.10 — PortalVS Successor Geography Migration**, only districts +
   municipalities. New complete captures + verified manifest, fail-closed offline
   importer, dry-run default, stage/validate both files before replacement; preserve
   IDs and explicitly review the two display changes. Move only their provenance
   after successful production rematerialization. Keep PSC historical-source
   provenance and all its current bytes unchanged.
2. Keep PSC migration paused. Seek authoritative locality/borough crosswalks,
   clarification of `posta` vs `dposta` in detail rows, and an explicit
   occurrence-only product/coverage decision. Do not send outreach automatically.
   Consider official postal ZIP as evidence/candidate source only after its own
   reuse assessment; no source switch is scheduled here.
3. Review the existing grouped lookup/count discrepancy separately before any
   future PSC projection. Do not broaden `/v1` semantics to compensate for data loss.
4. Developer adoption / OpenAPI correctness stays near-term **after source cleanup**,
   not another automatically selected data domain. Legacy support deadline remains
   2026-10-31; local runtime data has no dependency on the old host being available.

Offline reproduction (all paths local; no network in analyzer):

```powershell
python scripts/analyze_portalvs_psc_successor.py --manifest "C:\Users\matej\AppData\Local\Temp\opencode\portalvs-0239\capture\manifest.json" --post-zip "C:\Users\matej\AppData\Local\Temp\opencode\portalvs-0239\post-psc.zip" --output "C:\Users\matej\AppData\Local\Temp\opencode\portalvs-0239\semantics-analysis.json"
```

`--post-zip` is optional: without it baseline/type/coverage/geography diagnostics
still run, but publisher candidates are absent (not silently assumed). Input
manifest/hash/size/row counts, source schema/types and identity conflicts are
checked. Output may only be outside the repository or under ignored
`data/generated/`; there is **no production-import flag**. The manual acquisition
utility is separate, bounded to the three official URLs, disallows redirects,
stores raw only outside Git and is never invoked by runtime, tests or CI.
No new dependency, DB, Redis, scheduler, SDK or retention obligation was added.
Future analysis can use **new** captures and checked-in public geography; old raw
captures are not required to refresh or run tests. Historical reproduction of
these exact counts naturally requires this snapshot; the committed summary
retains evidence if private captures are later deleted.

## 14. Validation and production safety

Production baseline: main **0.23.8**, PR #35, commit
`97aa23c0454cf826bb3afaf7a6a0d60d37ba5817`. Research branch
`research/portalvs-psc-semantics`; version 0.23.9 at PR readiness.
All production JSON (not just the protected four) must equal that baseline.

| Protected file | Unchanged SHA-256 |
| --- | --- |
| `data/districts.json` | `a1622739cd80386da6818072ff6d2d81f491af2594b7aae0f4a5ee5b5713d70f` |
| `data/municipalities.json` | `7bc69db25450ee019c1e5ae2897b784c241484dd648f704dffd15d6ce83a54c6` |
| `data/psc.json` | `4b7346bbef19a86576fa5ecaa5f7d7c2afa36be5ff711753281b3a042b42bc55` |
| `data/sources.json` | `a28423df4afb64ef3fa23d03b388d22306075e8014af95689b002f522435618b` |

Local gates passed on 2026-10-15:

- `python scripts/validate_datasets.py`: **0 errors / 44 existing warnings**,
  14 datasets; no warning/compliance status was suppressed.
- `python scripts/check_referential_integrity.py`: passed.
- `python -m pytest -q`: **740 passed**, including 46 new research/tooling cases;
  synthetic fixtures only, no retained raw or live requests needed by tests.
- `python -m compileall scripts routers services tests schemas`: passed.
- `git diff --check`: passed.
- Local HTTP smoke via `scripts/smoke_test.py`: **41 passed / 0 failed**.
- OpenAPI: **39 GET operations**, project version **0.23.9**, unchanged `/v1`
  and checked `metadata.version == "v1"` envelopes.
- All **14 production JSON files** match pre-spike byte hashes; registry,
  outreach/compliance files, routers, services and schemas unchanged.
- All **273 curated table rows** checked against the retained-capture report;
  complete analysis repeated byte-identically with network access forbidden.
  Canonical JSON report SHA-256:
  `6fcbb60e397f0bd0e618b657212e6b01f942fb0cce48524ffc805cb0f91bdb69`.

Raw captures and optional generated reports remain external/ignored; only these
curated diagnostics and non-content hashes are committed. Hosted CI status belongs
to the PR checks; local results above do not claim a hosted CI run. No auto-merge,
tag, release, public deployment or successor promotion is part of this spike.
