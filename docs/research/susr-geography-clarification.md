# ŠÚ SR geography: technical source confirmation and rights escalation

## Evidence boundary and correspondence

The maintainer supplied the reply's substance and confirmed its received date as
**2026-11-20**. The original geography request was manually sent **2026-11-05**.
Dates have **day precision**: no time, timezone, message headers, receipt or
verbatim email is independently retained here. Personal signatures and mailbox
metadata remain private. This document is a substantive summary, not a quotation
of a purported archived message.

**Reply state:**
`REPLY_RECEIVED_TECHNICAL_SOURCE_CONFIRMED_RIGHTS_ESCALATION_REQUIRED`.

The maintainer also confirmed sending a follow-up **2026-11-27**, as a reply in
the existing thread. That follow-up is **`SENT_AWAITING_REPLY`**. Its exact body,
recipient unit and forwarding to the competent expert unit have not been
independently established; do not claim that a named specialist department has
received it. Sending is not permission. **The agent sent no correspondence.**

PSC correspondence is separate. No new Slovenská pošta reply was supplied;
its existing 2026-11-05 `SENT_AWAITING_REPLY` and `NO_GO_SUCCESSOR_PSC` states
are unchanged.

## What the responding unit directly confirmed

| Classifier number | Acronym | Official name |
| --- | --- | --- |
| `0024` | `LSUJ1` | Lokálna štatistická územná jednotka 1 – okres |
| `0025` | `LSUJ2` | Lokálna štatistická územná jednotka 2 – obec |

Both are publicly available through the
[official classifier catalogue](https://zber.statistics.sk/metaudaje/ciselniky).
The authority recommends using them directly to preserve origin and consistency
with current ŠÚ SR-managed data. This establishes **technical/source identity**,
not classifier-specific reuse approval or evidence that the existing production
snapshot was acquired from ŠÚ SR.

The older `CL000024`/`CL000025` MetaIS findings remain dated 0.23.15 research.
The reply confirms `0024`/`0025` and `LSUJ1`/`LSUJ2`; it does not independently
verify an internal-ID crosswalk. Do not use a guessed CL identifier to select
source bytes. Reconfirm any such equivalence from official metadata before
recording it as a current relationship.

## Technical invariants from the reply

- Keep published codes as strings, in their original form. Do not use a
  municipality name as an identity key or repair an unknown code by name.
- Duplicate names across districts/regions are legitimate. Join by unique
  codes, never by fuzzy matching, accent stripping or a name-only alias table.
- Interpret municipality membership in higher units using official classifiers
  and the valid territorial structure. A code's shape alone does not prove its
  parent relationship.
- Distinguish a direct official relationship from **OpenSK deterministic
  derivation from official codes**; derived links are not independently
  authoritative. Require documented, verified field/hierarchy semantics.
- Preserve every published row and distinguishing attribute for review,
  including Bratislava and Košice boroughs, military districts/Valaškovce and
  technical, foreign or other special records. Classify any source-only record
  explicitly; do not silently discard it to force a 79/2,927 count.
- Keep `SOURCE_NAME` separate from `OPEN_SK_DISPLAY_NAME`. OpenSK's existing
  district suffixes and reviewed presentation corrections are not ŠÚ SR text.

These invariants govern the offline reconciliation tooling and synthetic tests.
They do not establish the actual CSV schema, source row counts, coded hierarchy
or technical replacement verdict before the exact manual files are inspected.

## Questions the unit explicitly declined to decide

The responding unit stated that questions **2–6** were outside its professional
competence and recommended referral to the relevant expert departments. It did
**not** decide:

- whether CC BY 4.0 applies to these exact classifiers/files;
- permission for further transformation;
- commercial downstream reuse;
- required attribution; or
- automated acquisition.

Accordingly this is **not** `REPLY_RECEIVED_RESOLVED`, and no
classifier-specific reuse approval is inferred. The general terms are supporting
evidence only; see [the current rights review](susr-geography-rights.md).

## Follow-up scope (not a retained sent-message transcript)

Request expert confirmation of applicability to the exact `0024`/`LSUJ1` and
`0025`/`LSUJ2` CSV/XML distributions: local snapshots, value-preserving JSON
transformation, explicit OpenSK compatibility/display derivations, public API
redistribution, commercial downstream use, attribution/modification/non-endorsement
notices and permitted future acquisition. Ask for routing to the competent unit
if the recipient cannot decide. The maintainer's sending confirmation does not
establish that this wording was sent verbatim or that routing has completed.

## Production boundary

The [0.23.15 record](source-ownership-resolution.md) is historical, including its
then-pending reply and broader reuse interpretation. This reply supersedes that
interpretation for current decisions. Production districts/municipalities still
come from PortalVS; no production rights upgrade or migration follows from this
reply. PSC, phone areas and all unrelated production snapshots remain unchanged.
