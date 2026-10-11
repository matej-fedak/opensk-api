# Elections spike: independent integration, product and privacy review

Review date: 2026-10-11. Scope: `0.23.2` research spike, NR SR 2023 aggregate results. Author role: Agent C, independent of licence and acquisition/schema-measurement tracks. This review creates no endpoint, dataset, importer or production approval.

## Recommendation

**Continue a bounded research/import prototype; do not promote elections to production yet.** Prefer one NR SR family-specific importer, one election, municipality-level turnout and political-subject vote totals, with election-native geography. Do not build a generic election engine, candidate directory, precinct service or longitudinal comparison platform.

**`JSON_CONTINUE` is the recommended architectural direction, conditionally, not a measured pass.** Keep the offline, reviewed, checked-in JSON architecture if the selected normalized output and deployment measurements meet an explicit budget. This verdict does not certify file size, licensing, privacy or demand. A failed budget should first reduce scope or defer the addition, not automatically trigger a database migration.

The spike is useful even if the final decision is no production addition: it can establish reproducibility and whether native geography avoids the PortalVS dependency. A technically successful prototype alone is not a product justification.

## Evidence boundary

Inspected repository evidence:

- `README.md`, `DEVELOPMENT_PLAN.md`, `docs/api-contract-v1.md`: local JSON only, FastAPI, no runtime upstream calls or new database infrastructure; bounded collections use `limit`/`offset` and the standard envelope.
- `docs/adding-a-dataset.md`, `docs/import-pipeline.md`: production needs acquisition, reuse, privacy, identifiers, normalization, validation, provenance and offline tests; generated previews are not production data.
- `services/geography_service.py`, `data/municipalities.json`, `data/districts.json`: current municipality/district reference data is PortalVS-derived; existing API code formats are not proof of equivalence to election geography.
- `services/procurement_notice_service.py`, `routers/procurement_notices.py`: a nearby collection precedent, but full-load/copy/filter behavior needs measurement before copying it to a larger domain.
- `services/http_cache.py`, `docs/http-caching.md`: body-hash ETags, date-only semantic Last-Modified and buffering of response bodies.
- `docs/privacy-review.md`, `docs/research/roadmap-council-notes.md`, `docs/research/opensk-research-roadmap-2026-q4.md`: aggregate scope and earlier claims of safety/value, challenged below.

Independent official consultation: [ŠÚ SR download index](https://volby.statistics.sk/tree.html), accessed 2026-10-11. The NR SR 2023 section lists municipality summary `NRSR2023_SK_tab02d.csv` (332.88 KB), municipality political-subject votes `NRSR2023_SK_tab03e.csv` (5.36 MB), horizontal municipality votes `NRSR2023_SK_tab08d.csv` (738.53 KB), political subjects `NRSR2023_SK_tab0a.csv` (1.49 KB), territorial division `NRSR2023_SK_tab0c.csv` (205.78 KB), and table information `NRSR2023_SK_tab_info.csv` (2.52 KB). It separately lists candidates and preferential-vote files, including `tab07f` advertised at 1.52 GB.

These are **index-advertised sizes and descriptions**, not measured download sizes, inspected CSV schemas or normalized JSON sizes. No election CSV was downloaded for this review. Encoding, counts, coverage, special rows, geography equivalence and reconciliation remain unverified here. The index establishes official availability and the OGP publication basis, not this review's reuse approval. Licence conclusions belong to the retained rights evidence, not an inference from the words "open data".

## Challenge the product assumptions

| Assumption | Independent assessment |
| --- | --- |
| "Highest value-to-risk data addition" | A roadmap preference, not demonstrated demand. This review found no cited user interviews, usage evidence or committed integration requiring elections. |
| "CSV-to-JSON provides value" | Plausible for browser clients wanting a bounded local query without parsing CSV/CP1250. Official downloads already serve bulk analysis; another mirror may add little. |
| "Municipality aggregates are useful without candidates" | Plausible for turnout displays and local political-subject tallies. Not sufficient for candidate lookup, preference voting, mandate simulation or explaining election outcomes. Those are excluded, not promised. |
| "One historical election makes a comparison API" | False. A 2023 snapshot cannot support a time series; current boundaries and party labels are not historical identities. |
| "Aggregate means privacy-safe" | Lower risk, not automatic safety. Small electorates and unanimous cells can disclose or strongly suggest political choices when combined with external knowledge. |
| "High PortalVS join rate means ready" | It diagnoses compatibility only. It neither approves PortalVS-derived enrichment nor validates historic boundaries or complete election coverage. |
| "Small horizontal CSV means small runtime dataset" | Not necessarily: unpivoting expands rows and repeated JSON keys; Python objects and response buffering expand memory further. |

Before production, demonstrate at least one concrete task and a reproducible client query that is materially easier than the official download. This may be a documented maintainer demo or an actual user's requirement; label which, and do not present a demo as market validation. If the actual task is bulk historical research, link to the official files instead of expanding the API.

## Privacy: a narrower scope than the earlier notes

1. Allow only election metadata, official territorial labels/codes, political-subject list labels/codes, and approved aggregate counts. Party/coalition names are institutional list labels, not evidence of an individual voter's affiliation. Do not silently generalize this rule to independent candidates in municipal elections.
2. Do not acquire candidate lists (`tab0b`), elected-member files (`tab06`), preferential-vote files (`tab07*`), biographies, ages, occupations, residences or contact details. They are unnecessary for this product even when official and small. Do not download them merely to remove their fields later.
3. Exclude voter-level information, polling-place addresses/coordinates, candidate identifiers and names, raw source rows/blobs and person-linked enrichment. No cross-register matching, inferred individual political preferences, household profiles or person-search functionality.
4. Start at municipality level, not precinct (`okrsky`) level. Municipality-only is a minimization choice, not anonymization proof. Before shipping, inspect low-count/zero-denominator cells, unanimous outcomes and any special territories; document a defensible release rule and residual risk. If suppression is required, show an explicit withheld state, never zero, and consider complementary totals that could reconstruct withheld values.
5. Validate via a field allowlist plus recursive forbidden-field tests; unknown columns or person-related structures must fail closed. Confirm permitted labels come from the political-subject file, not candidate tables. Use minimal synthetic fixtures rather than candidate-personal fixtures in Git or logs.

The current privacy note's allowance for "candidate personal details beyond officially published result tables" is too ambiguous for this addition: **no candidate-personal output at all** is the recommended scope. This is a future review condition, not an edit to that note or a legal conclusion that all published municipal totals are personal data.

## PortalVS-independent geography

The canonical territorial dictionary must come from the selected election's official `Územné členenie`, with labels and hierarchy retained as they were for that election. Build only the geography required by the selected aggregates; deduplicate repeated territorial entries using checked source keys, not names.

- Use source-native code strings, preserving leading zeros, with an explicit namespace and election identity. A key is election + territorial level + native code (or a verified composite if the file requires one). Do not assume codes are globally stable across years.
- Keep election-native region, district and electoral administrative units distinct. `územný obvod` is not automatically an OpenSK district; do not synthesize `SK0101`-style keys by padding or concatenating unverified source codes.
- Validate all result keys against this native dictionary. Every unresolved key must be explained; silently dropping unmatched results is unacceptable. Special/overseas voting units, city districts, municipality changes and summary rows require explicit classifications if encountered; their existence and exact representation are not asserted here.
- A read-only comparison against today's `data/municipalities.json` may report matched/unmatched codes and explain differences. Do not copy PortalVS-derived names, parent links or attributes into the election product. No fuzzy-name joins, PSC joins or inference from code appearance.
- First production version should have no required OpenSK geography links. Optional crosswalks are a later, separately sourced/rights-reviewed feature; if added, keep native geography intact and mark verified/null links and their source/date.
- Test that normalized output is identical when the PortalVS files are absent. Results filtering must not call `get_municipality()` or require a currently existing municipality. A former or special election territory is not invalid merely because today's geography lacks it.

Thus a poor contemporary PortalVS join rate need not block a coherent native-geography product. A poor **native source join** does block it. Election-native geography is scoped historical reference data, not a replacement national municipality registry.

## Tiny hypothetical API, only after promotion gates

This is a design sketch, not an implemented or approved contract. Two read-only routes would suffice:

- `GET /v1/elections`: small catalogue of actually imported elections, including identity, family/date, supported territorial level, measures, historical/final status, coverage limitations and snapshot revision. No claim to all Slovak elections.
- `GET /v1/elections/{electionId}/results`: paginated **municipality-summary records** for that election, optionally exact-filtered by election-native municipality, district or region code. No initial `/search`, `/stats`, candidates, precincts, map tiles or arbitrary analytics.

Prefer one item per municipality with its approved turnout counts and a bounded array of political-subject vote counts. This keeps one municipality coherent within a page and avoids repeating turnout once per party or accidentally summing it repeatedly. Nested vote arrays must have a measured maximum, not unlimited payloads. Keep party codes election-scoped; vote share uses valid political-subject votes as its documented denominator, not registered electors. Source turnout definitions must determine which counts are exposed; do not invent a field mapping in advance of schema evidence.

If inspection shows a coherent turnout-only preview but no verified party-vote normalization, label it turnout-only. Do not call it full election results. Do not add a party filter until a real task justifies its semantics; stripping other parties or whole municipality records changes the meaning of the item.

Pagination/filter contract:

- Reuse `{items, count, total, limit, offset}` inside the normal response envelope, default `limit=100`, `offset=0`, maximum `500` subject to the measured response budget. The existing contract permits `limit=0`; either preserve this for a new collection or explicitly document a different rule before stabilization.
- `total` counts filtered municipality records before pagination; `count` counts returned records, not parties or ballots. No implicit filters or ordering by electoral performance.
- Sort by a documented native composite territorial key; sort nested subjects by native list code. Apply exact filters with AND semantics before paging; preserve stable ordering across restarts.
- Reject malformed or unsupported filter values with structured 400; unknown valid election identity is 404; a valid territorial filter with no matches yields an empty page. Validate formats from the selected source, not current geography validators. Offset beyond the end also returns an empty page.
- No unbounded dump parameter. Clients needing bulk data should use the official download. Pagination remains stable within a snapshot; do not claim cross-revision cursor consistency. Expose revision so clients can detect a refresh and restart a multi-page read.

## Provenance, freshness and cache constraints

Retain a small offline manifest: exact selected URLs/file names and descriptions, acquisition timestamp, raw SHA-256 and measured bytes, verified encoding/delimiter/schema, transformation version, row/key counts, territory scope, exclusions, validation report and rights/attribution evidence. For public output, provide a curated source reference, election date, coverage and snapshot revision; do not leak local paths, research logs or arbitrary raw upstream metadata. Extend `/v1/sources` deliberately after approval rather than exposing the internal registry verbatim.

Election date, acquisition date and dataset revision date are different. A corrected 2023 result imported in 2026 is not "updated 2023" just because voting happened then. Do not fabricate a source publication date where absent. Set envelope freshness consistently with the reviewed snapshot; keep acquisition evidence separately and use null for an unknown date where the contract permits it.

Use the existing body-hash ETag and static `public, max-age=86400` policy for bounded historical result GETs; each filter/page is its own URL representation. An HTTP 304 saves transfer, not initial JSON load, filtering or body hashing in the current implementation. Historical final results can still be corrected, so avoid an unconditional immutable-cache claim.

Two existing implementation constraints need explicit future testing, not changes in this spike:

- `ConditionalCachingMiddleware` falls through to `If-Modified-Since` when a supplied `If-None-Match` does not match. ETag conditional precedence must be respected; otherwise a changed body can receive an incorrect 304 from an old date validator.
- Last-Modified currently comes from a date-only route-prefix map. Same-day revisions cannot be distinguished, and a shared `/elections` date would not accurately represent multiple snapshots. Use a valid representation revision timestamp if available, or omit Last-Modified and rely on ETag until a safe mapping exists. Do not reuse the election date as that validator.

These are relevant integration gates because corrections/history are central here; they do not authorize a caching rewrite in the research spike.

## Importer, maintenance and `JSON_CONTINUE` budget

Choose one **NR SR-specific importer with an explicit 2023 profile**. It should accept only the allowlisted turnout, party-vote, party-list and native-territory inputs plus minimal explanation/control files. Recognize exact expected headers and fail on drift; dry-run first, generated preview only, no runtime download. Small parsing helpers may be reused, but no plugin registry, universal column matcher, guessed auto-detection or generic election DSL.

Horizontal `tab08d` is an interesting acquisition option, not automatically the correct one. Verify equivalence to the required political-subject totals and list order before selecting it; do not import both horizontal and vertical views into production. Cheap SR summary/party totals may serve as reconciliation controls without becoming another public territorial level.

Checks must cover deterministic byte output, duplicate territorial/subject keys, integer/nonnegative counts, missing versus zero, strict decoding, separators/decimal conventions, totals and documented rounding. Never sum mixed city/borough/summary layers or assume a domestic municipal sum includes every SR vote; explain any reconciliation difference from source evidence.

For `JSON_CONTINUE`, Agent B's measured evidence should include:

| Measurement | Acceptance condition for this recommendation |
| --- | --- |
| Acquisition bytes | Explicit file allowlist; enforced per-file and total byte caps, including streamed bytes if Content-Length is absent/wrong. No bulk archive or candidate/preference downloads. |
| Output size | Actual UTF-8 JSON bytes and municipality/party counts recorded; one-election output fits a reviewed cap. Suggested starting ceiling: 10 MiB total normalized output for this addition, a proposal rather than an existing project rule. |
| Runtime memory/startup | Measure full parse, retained objects/indexes, response buffering and more than one worker on the deployment class. Approve only with explicit process/headroom and cold-start budgets; disk size alone is not a pass. |
| Page size/latency | Measure worst-case 500-municipality page including nested subject totals and middleware hashing. Suggested ceiling: 1 MiB serialized page; lower the page maximum if needed. Define and measure a deployment latency budget, not an invented benchmark claim. |
| Repository history | No raw multi-MB/GB mirrors in Git; small reviewed fixtures and manifest sufficient to reproduce acquisition. Review actual JSON diffs and cumulative retained revision bytes. |

The proposed numerical caps are conservative review starting points, not measured results or guarantees. If an honestly scoped aggregate snapshot exceeds them, revisit the representation and limit first. Separate one-election files and lazy per-election loading are a reasonable later adjustment; eagerly load-all-years plus unbounded `lru_cache` is not. No database, background scheduler, cache server or generic query engine is justified by this spike.

Maintenance should be manual, offline and correction-driven: one named owner, pinned input manifest, reproducible command, reviewed semantic diff, validation, then atomic promotion of a complete snapshot and matching provenance. Do not auto-refresh a historical result on every request or imply real-time election reporting. Keep prior revisions reproducible through Git/manifests, not a public revision browser initially; do not silently overwrite old election geography with current labels.

Every additional year/family needs its own schema/rights/privacy/budget review. Historic boundary changes, party renames/coalitions and code reuse prohibit naive trend joins. An EP adapter or old NR SR profile should be added only for demonstrated need and verified fixtures; municipal and regional candidate-oriented families remain out of scope. Extract shared abstractions only after multiple reviewed adapters show genuine commonality.

## Conditions for a later production decision

Production is conditional on **all**, not merely a combined optimistic score:

1. Retained explicit rights evidence approves the chosen aggregate files, transformation, caching and redistribution; attribution is implementable. This review does not substitute for Agent A's work.
2. Agent B's exact schema/acquisition evidence confirms reproducibility, strict decoding, native geography integrity, keys, coverage and source-total reconciliation, with special/excluded rows explicitly accounted for.
3. A fresh privacy review approves the exact municipality/party fields and low-count policy; no candidate-personal files or hidden raw-row leakage enter outputs, fixtures or logs.
4. A concrete bounded client task supports an API rather than merely duplicating official bulk downloads; absent that evidence, research-only remains an acceptable outcome.
5. Measured output/runtime/page/history budgets support `JSON_CONTINUE`, with a named maintenance owner and correction workflow.
6. Offline importer/validator/integrity/route tests, source-catalogue projection, deterministic pagination and conditional-cache correction tests pass. A malformed input or failed gate leaves the last known-good dataset untouched.
7. Public wording says exactly "NR SR 2023, municipality-level aggregate snapshot" (or the narrower verified scope), excludes unsupported years/families/candidates/precincts and does not promise national historical coverage or live election service.

**Independent bottom line:** a small native-geography aggregate snapshot is technically plausible and lower-risk than candidate/preference imports, but neither demonstrated demand nor production readiness follows from the download index. Continue bounded JSON research; promote only if the separate rights, measurement, privacy, utility and maintenance gates actually pass. Do not make PortalVS compliance or a generic elections framework a prerequisite, and do not let successful acquisition expand the product scope.
