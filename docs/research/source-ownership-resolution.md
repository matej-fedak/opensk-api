# 0.23.15 — Source Ownership Resolution & PortalVS Exit

**Geography verdict: `NO_GO_SUSR_GEOGRAPHY_REPLACEMENT`**

**Acquisition gate: `MANUAL_SOURCE_FILES_REQUIRED`**

**Telecom: `TELECOM_REUSE_RESOLVED`**

**PortalVS: `REPLY_RECEIVED_REDIRECTED_TO_SOURCE_OWNER`**

**PSC: `NO_GO_SUCCESSOR_PSC`**

This milestone resolves source-routing and the telecom reuse question. It does
not convert the existing PortalVS-derived geography into ŠÚ SR production and
does not promote a PSC successor. Runtime remains local JSON only. No upstream
production download, route, importer or production data migration was performed.
The agent did not send correspondence; the maintainer manually sent both
source-owner clarification requests on 2026-11-05, as recorded below.

## 1. Evidence boundary

The maintainer supplied the substance and received dates of the telecom and
PortalVS replies. Original mailbox bytes, headers and delivery metadata remain
private and were not independently inspected. No personal signatures or
unnecessary contact details are republished.

- Telecom reply received **2026-11-02**: direct institutional reuse
  clarification for the retained telephone-area request scope.
- PortalVS reply received **2026-11-02**: source-owner redirection only. It is
  not PortalVS redistribution approval, a licence grant, or evidence that the
  existing copied fields originated directly from a newly named authority.
- ŠÚ SR classifier metadata and general reuse terms were researched on
  **2026-11-05** using official pages/metadata only. No classifier CSV/XML
  production bytes were downloaded.
- Slovenská pošta's official PSC page, download link and general contact route
  were checked on **2026-11-05**. The maintainer manually sent the PSC
  clarification request that day: **`SENT_AWAITING_REPLY` — 2026-11-05**.
- The maintainer also manually sent the separate ŠÚ SR municipality/district
  classifier clarification on **2026-11-05**:
  **`SENT_AWAITING_REPLY` — 2026-11-05**. It concerns the exact authoritative
  municipality and district classifiers; CC BY 4.0 applicability to those files;
  local storage; CSV/XML → JSON transformation; public API redistribution;
  commercial downstream reuse; attribution; allowed acquisition method;
  identifier stability; municipality → district/region relationships; and special
  rows, city parts and military units. This is distinct from resolved elections
  correspondence.

Both dispatch dates and pending-reply states are maintainer-confirmed, not
independently verified mailbox evidence. Neither institution has replied to
these new requests. No Message-ID, delivery confirmation or receipt is retained
here, and no permission is inferred from sending or silence. The agent did not
send correspondence. These workflow updates do not invalidate the classifier,
terms or provenance research, and do not add a reply-waiting technical blocker:
`MANUAL_SOURCE_FILES_REQUIRED` and deterministic 79/2,927 reconciliation remain
the geography replacement gate.

## 2. Four-domain ownership and production matrix

“Source owner” below means the authority identified by the available evidence
for clarification/origin. It is not a new judicial determination of every
possible copyright or database right. Originating authority, producer of the
checked-in copy, technical intermediary and party able to clarify reuse remain
separate.

| Domain | Originating source / authority | Current checked-in production copy and producer | Intermediary / technical route | Rights and reuse evidence | Resolution |
| --- | --- | --- | --- | --- | --- |
| Districts | PortalVS identifies **Štatistický úrad Slovenskej republiky** as the main/legal classifier authority. Exact replacement classifier: ŠÚ SR `CL000024` / `0024`. | PortalVS successor county rows acquired 2026-10-16, normalized by the existing OpenSK importer. All 79 public records remain this snapshot's output. | PortalVS / IS Číselníky `county.json?validity=valid` is the actual production acquisition API. Register adries / MV SR was described only as a common technical implementation route; it is not the production source or an automatic substitute. | PortalVS redistribution remains unresolved. ŠÚ SR terms are verified for an independently acquired `CL000024` replacement, not retroactively for PortalVS bytes. | Owner direction resolved; production exit blocked at acquisition/reconciliation. |
| Municipalities | PortalVS's listed source and reply identify **Štatistický úrad SR**. Exact replacement classifier: ŠÚ SR `CL000025` / `0025`. | PortalVS successor town rows acquired 2026-10-16, normalized and display-disambiguated by OpenSK. All 2,927 public records remain this snapshot's output. | PortalVS / IS Číselníky `town.json?validity=valid` is the actual production acquisition API. ŠÚ SR metadata/catalogue is a candidate authoritative acquisition route only. | PortalVS redistribution remains unresolved. ŠÚ SR terms are verified for an independently acquired `CL000025` replacement. | Owner direction resolved; production exit blocked at acquisition/reconciliation. |
| PSC | PortalVS identifies **Slovenská pošta** as the underlying source. | Historical PortalVS classifier 42 snapshot, with only the previously documented local municipality/district compatibility derivations. Bytes remain frozen and partial. | PortalVS classifier 42 is the current distribution copy. The official Slovenská pošta PSC page/ZIP is a future technical candidate, not an approved replacement or a source of administrative semantics by itself. | Neither PortalVS's redirect nor public downloadability grants reuse. The maintainer manually sent Slovenská pošta clarification on 2026-11-05: `SENT_AWAITING_REPLY`, no permission inferred. Postal reuse, transformation, API/commercial redistribution, attribution and acquisition remain unanswered. | `NO_GO_SUCCESSOR_PSC`; no production or coverage change. |
| Telephone areas | **Úrad pre reguláciu elektronických komunikácií a poštových služieb**, exact existing numbering page and `30.xls` / `List1` workbook. | Regulator workbook transformed offline by OpenSK to 2,922 normalized mappings; 2,919 have local geography joins and three remain unmatched. | Offline XLS/CSV conversion and local JSON; no runtime upstream call. Local municipality/district/region joins still consume the current PortalVS-derived geography and are not independent ŠÚ SR joins. | The regulator's 2026-11-02 reply resolves the exact retained request: local snapshots, XLS → normalized JSON, public API redistribution, commercial downstream use and the requested derived joins. | Reuse resolved for that scope only; production bytes/freshness unchanged. See `telecom-reuse-clarification.md`. |

The telecom answer is not a formal licence name, mandatory attribution formula,
version-notice rule, automated-acquisition authorization, accuracy guarantee or
endorsement. Factual attribution and OpenSK's transformation disclosure are
retained without presenting them as regulator-mandated verbatim wording.

## 3. Verified ŠÚ SR classifiers and reuse

### 3.1 Exact classifier identities

| Property | Municipalities | Districts |
| --- | --- | --- |
| MetaIS identifier | `CL000025` | `CL000024` |
| ŠÚ SR classifier code | `0025` | `0024` |
| Exact Slovak name | `Lokálna štatistická územná jednotka 2 – obec` | `Lokálna štatistická územná jednotka 1 – okres` |
| Code structure | `Č6` | `Č3` |
| Main gestor | Štatistický úrad Slovenskej republiky | Štatistický úrad Slovenskej republiky |
| Metadata version / basic classifier | `1.0` / `Áno` | `1.0` / `Áno` |
| Effective from / validity date | 2008-10-01 / 2019-01-11 | 2008-10-01 / 2019-01-11 |
| Expiry | unlimited | unlimited |
| MetaIS record | <https://metais.slovensko.sk/data-objects/codelists/2936?orderBy=itemCode&sortDirection=ASC> | <https://metais.slovensko.sk/data-objects/codelists/2935?orderBy=itemCode&sortDirection=ASC> |
| Reuse verdict | `SUSR_REUSE_VERIFIED` | `SUSR_REUSE_VERIFIED` |

The MetaIS-basic-classifier status supports harmonization with public-
administration standards; the reviewed ŠÚ SR record does not expose a separate
per-record boolean with that exact label. Do not invent one.

Municipality metadata explicitly states that military-district information is
included for statistical purposes. It does not enumerate current military-row
codes/names. Supplementary municipality attributes include classifier `0051`
and minority-language names; district metadata lists `RPO`, `RPN` and `FIN`.
Raw row counts, complete item schemas and hierarchy links cannot be established
from the reviewed metadata alone. No current special-purpose, foreign or
military row may be inferred or silently deleted before inspecting actual
bytes and applying an explicit reviewed production policy.

### 3.2 Current metadata/download endpoint limitation

The live catalogue is:

<https://zber.statistics.sk/metaudaje/ciselniky>

Its current JavaScript builds downloads through the portlet resource
`p_p_resource_id=generateFile`, using each row's `clCode`, `clId`, `clVersion`,
`hier` and `fileType=CSV|XML`. The catalogue itself was live on recheck.
Previously observed friendly detail and combined REST metadata URLs, and the
previously listed static `/rest/v1/.../susr_obce.csv`,
`susr_okresy.csv` and corresponding XML paths, returned **404 on the final
recheck**. They are therefore **not** represented here as currently verified
production download URLs. No row-specific `generateFile` URL was invoked and
no CSV/XML body was acquired.

A future maintainer handoff must use current official catalogue row links and
supply the exact selected CSV or XML files, their final URLs, actual acquisition
timestamp, bytes and SHA-256. The catalogue HTML, metadata and terms do not
substitute for those files.

### 3.3 Applicable reuse terms

Official terms page:

<https://slovak.statistics.sk/wps/portal/ext/aboutus/webpage/terms/!ut/p/z1/jZBBDoIwEEXPwgk60ELrskUpNVUoWMFuDCtCoujCeH4RXRgTkdlN8t7Pn0EO1cj1zb1rm1t36ZvTsB9cdNzrnAnhc8iKNQGVxBzEzmClI1SNgKHqBbBtsQK147kcSB9IiNwcP5Y8JVQDMC1DUDy1xcJgDBzP8-HHcJjnTwBuOr5CbkSmLviX4b5L8meH0sbJpgwiSd7Ax5OXAhTV1DAlcCYCdD1ba2voVOt5D6xwOgY!/dz/d5/L0lDUmlTUSEhL3dHa0FKRnNBLzROV3FpQSEhL3Nr/>

Title: `Podmienky pre využívanie a ďalšie zverejňovanie štatistických
informácii Štatistického úradu SR`. Displayed last update: **13.10.2026**.

The terms permit statistical information published through ŠÚ SR websites,
public databases and electronic services to be disseminated (copied,
communicated and distributed publicly), used/quoted in other works and used
commercially, subject to the conditions. They require ŠÚ SR attribution, no
implication of endorsement, notice of **CC BY 4.0** when disseminating
(preferably with a direct licence link), and respect for applicable third-party
rights. No classifier-specific reuse exception was found in the reviewed
`CL000024`/`CL000025` metadata.

The automation language is not evidence of a universal automated-download
permission: it addresses automated collection that would disproportionately
burden or threaten service stability. Independently of that wording, this
milestone deliberately requires human review and **manual official source-file
handoff**. Public availability, terms permission and a download button do not
waive the acquisition-evidence gate.

CC BY 4.0 applies to a future properly acquired ŠÚ SR snapshot under these
terms. It does not relicense historical PortalVS acquisition bytes or prove
that OpenSK's display transformations are ŠÚ SR originals.

## 4. Current production ID and field provenance

Strict provenance labels below describe the evidence that generated the
current checked-in values, not merely whether another source could corroborate
them.

### 4.1 Districts

| Field | Classification | Reason |
| --- | --- | --- |
| `code` | `OPEN_SK_COMPATIBILITY_VALUE` | Decimal public IDs are generated from PortalVS statistical notes while preserving the established OpenSK namespace. Twelve letter-suffixed PortalVS codes are deterministically re-lettered; they are not proven direct ŠÚ SR identifiers. |
| `name` | `PORTALVS_ONLY` as current-byte provenance | Taken from the successor county title. Independent authoritative agreement would not rewrite its acquisition history. |
| `regionCode` | `PORTALVS_ONLY` derivation | Derived from the PortalVS statistical note and existing OpenSK region mapping. |
| `country` | `OPEN_SK_COMPATIBILITY_VALUE` | OpenSK emits the constant `SK`. |

The 12 explicit compatibility mappings retained by the importer are:

| PortalVS code | Statistical note | OpenSK public `code` | Name |
| --- | ---: | --- | --- |
| `SK031A` | 510 | `SK03110` | Tvrdošín |
| `SK031B` | 511 | `SK03111` | Žilina |
| `SK032A` | 610 | `SK03210` | Veľký Krtíš |
| `SK032B` | 611 | `SK03211` | Zvolen |
| `SK032C` | 612 | `SK03212` | Žarnovica |
| `SK032D` | 613 | `SK03213` | Žiar nad Hronom |
| `SK041A` | 710 | `SK04110` | Stará Ľubovňa |
| `SK041B` | 711 | `SK04111` | Stropkov |
| `SK041C` | 712 | `SK04112` | Svidník |
| `SK041D` | 713 | `SK04113` | Vranov nad Topľou |
| `SK042A` | 810 | `SK04210` | Spišská Nová Ves |
| `SK042B` | 811 | `SK04211` | Trebišov |

These values preserve API compatibility. They do not prove that ŠÚ SR publishes
the same `SK…` strings.

### 4.2 Municipalities

| Field | Classification | Reason |
| --- | --- | --- |
| `code` | `PORTALVS_ONLY` as current-byte provenance | Read from the PortalVS town `note`. REGPJ independently corroborates all 2,927 six-digit administrative IDs, but the bytes were not directly regenerated from REGPJ or `CL000025` in this milestone. |
| `name` | `PORTALVS_ONLY` plus reviewed OpenSK presentation | Source title plus OpenSK `(okres …)` disambiguation for 205 duplicate-name records and two reviewed display corrections (`504173`, `504742`). The suffix is not a ŠÚ SR source title. |
| `districtCode` | Derivation `PORTALVS_ONLY`; identifier namespace `OPEN_SK_COMPATIBILITY_VALUE` | Resolved through the PortalVS composite-code district prefix and the compatibility district map. |
| `regionCode` | `PORTALVS_ONLY` derivation | Inherited through the current district mapping. |
| `country` | `OPEN_SK_COMPATIBILITY_VALUE` | OpenSK emits the constant `SK`. |

No current field is relabelled `DETERMINISTIC_DERIVATION_FROM_SUSR` without an
actual deterministic rebuild from supplied ŠÚ SR bytes.

### 4.3 PSC and telephone-area joins

PSC codes, city strings, historical municipality matches and coordinates remain
PortalVS-derived. `districtCode` is an OpenSK compatibility value backfilled
through the current municipality map. Slovenská pošta source-owner direction
does not change any of those provenance labels or repair postal semantics.

Telephone area designation, source confidence and workbook names are regulator-
sourced. Local `municipalityCode`, district and region joins resolve through
current geography records, so their present relationship derivation remains
PortalVS-dependent even though the workbook independently supplies geographic
facts. No production phone-area row was refreshed or relabelled.

## 5. Acquisition and deterministic replacement gate

The repository root, checked-in raw-data directory and available research
manifests contain no exact manually supplied current `CL000024`/`0024` or
`CL000025`/`0025` CSV/XML source files. The retained REGPJ evidence from 0.23.11
is corroborating research, not either exact classifier handoff. Consequently:

- **Manual source files are required.** Their exact format choice, final URLs,
  bytes, hashes and actual acquisition timestamp are not established.
- No raw row count or schema has been assumed. No download failure was retried
  through a scraper or an alternative unofficial mirror.
- No importer was run against unrelated REGPJ, PortalVS or stale research bytes.

Before any future production write, all of the following must pass in one
reviewed milestone:

1. Supply both exact current official classifier files manually, with actual
   acquisition evidence and verified final catalogue row URLs.
2. Recheck the applicable terms and record attribution, CC BY 4.0,
   modification and non-endorsement notices for the new source.
3. Validate encoding, schema, identifiers, validity and every exceptional row;
   decide military/special-purpose content explicitly rather than silently
   dropping it.
4. Reconcile exactly **79 districts** and **2,927 municipalities**, including
   all current public IDs, names/display policy, district/region relationships,
   all 12 compatibility re-letterings and every downstream reference.
5. Produce deterministic before/after diffs and prove no residual
   PortalVS-only mapping is presented as direct ŠÚ SR data. Preserve OpenSK
   compatibility values only with explicit provenance.
6. Re-run dataset/referential integrity, all tests, hash review and local API
   smoke checks before any explicit promotion. PSC remains a separate frozen
   decision, not an implicit geography output.

Those replacement checks cannot be executed without the source files. The
current unchanged production counts and references are validated, but that is
not a migration reconciliation.

## 6. Final decisions and remaining dependencies

- **Geography:** `NO_GO_SUSR_GEOGRAPHY_REPLACEMENT` because exact manual source
  bytes and deterministic replacement evidence are absent. Existing district
  and municipality JSON and freshness stay unchanged.
- **PortalVS:** `REPLY_RECEIVED_REDIRECTED_TO_SOURCE_OWNER`. No
  `PORTALVS_REUSE_APPROVED` claim is made. Public-promotion compliance remains blocked
  while current production is PortalVS-derived.
- **Telecom:** direct requested-scope reuse resolved; only source registry,
  public projection and documentation change. `data/phone_areas.json` and
  `PHONE_AREAS_LAST_UPDATED` remain unchanged.
- **PSC:** `NO_GO_SUCCESSOR_PSC`; `data/psc.json` and freshness remain frozen.
  Source-owner direction resolves neither rights nor street/admin/temporal
  mapping blockers. `PSC_RIGHTS_PENDING`, `MAPPING_PARTIAL`,
  `CONTRACT_CLARIFICATION_REQUIRED` and `NO_SOURCE_READY` remain unchanged.
  `docs/research/slovenska-posta-psc-outreach.md` records maintainer dispatch
  on 2026-11-05: `SENT_AWAITING_REPLY`, no permission inferred.
- **ŠÚ SR geography outreach:** `SENT_AWAITING_REPLY` after maintainer dispatch
  on 2026-11-05; no reply or new permission. `CL000024` / `0024` and `CL000025` /
  `0025` remain valid candidates; the existing manual-file/reconciliation gate,
  technical verdicts and production provenance remain unchanged.
- **Next priority:** the maintainer-run external-developer pilot remains next;
  no automatic geography retry, PSC evidence loop, new data domain, scheduled
  acquisition or runtime upstream dependency is queued.
