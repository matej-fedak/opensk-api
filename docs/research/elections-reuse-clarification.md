# ŠÚ SR elections reuse clarification

**State: REPLY_RECEIVED_RESOLVED**  
**Reply received: 2026-10-30**  
**Acquisition mode: MANUAL_OFFICIAL_DOWNLOAD_ONLY**  
**Licence verdict: CC_BY_4_0_VERIFIED_BY_PUBLISHER_REPLY**

Authority: **Štatistický úrad Slovenskej republiky** (ŠÚ SR).
The maintainer supplied the substantive institutional answers and confirmed the
received date in this implementation session. This is a summary of that
first-party account, not a claim that the agent inspected mailbox metadata or
archived a verbatim email. Original correspondence should remain with the
maintainer; personal signatures, phone numbers and mail headers are not published.

## Questions and substantive answers

The 2026-10-11 clarification request, followed up manually on 2026-10-28,
asked about election-specific licensing, local retention/transformation,
API/repository redistribution, commercial downstream use, acquisition and
attribution. The reply confirms:

1. **CC BY 4.0 applies to the CSV/ODS/XLSX election-result tables published on
   volby.statistics.sk.** This resolves the election-applicability question
   left open in the 0.23.2 spike.
2. Local storage, CSV/XLSX → JSON transformation, field normalization and
   derived snapshots are permitted.
3. Redistribution through a public open-source API and commercial downstream
   reuse are permitted under CC BY 4.0, with attribution.
4. Modifications must be disclosed. Attribution must not imply endorsement by
   ŠÚ SR of OpenSK or downstream applications.
5. **Automated robots/crawlers and similar automated website-download tools
   remain prohibited.** The reply does not grant a one-off scripting exception.
6. Use the official files under **Údaje na stiahnutie**, downloaded **manually
   by the maintainer**, followed by offline processing. Repeated automated
   downloading of finalized results is generally unnecessary because those
   exports normally do not change after publication; this is not an immutability
   guarantee.

No source-owner messages were sent by the agent. PortalVS and telecom remain
**FOLLOW_UP_SENT_AWAITING_REPLY** (2026-10-28); this reply does not clear them.

## Attribution and licence separation

Recommended wording supplied by ŠÚ SR:

> Zdroj: Štatistický úrad SR – výsledky príslušných volieb.
> Licencia: Creative Commons Attribution 4.0 (CC BY 4.0).
> Údaje boli ďalej spracované projektom OpenSK.

Retain alongside it:

- Original source: <https://volby.statistics.sk/nrsr/nrsr2023/sk/subory_na_stiahnutie.html>
- Licence: <https://creativecommons.org/licenses/by/4.0/>
- Explicit transformation disclosure: OpenSK parses selected CSV tables into
  JSON, normalizes field names, joins the election-native territory dictionary
  and retains only the approved aggregate scope; it is not the original file.
- Actual manual acquisition timestamp and OpenSK snapshot verification date
  once known, separately from election/publication dates.
- **OpenSK nie je oficiálnou službou Štatistického úradu SR.** No endorsement
  of OpenSK or downstream applications is implied.

MIT applies to OpenSK code, **not** to the underlying ŠÚ SR election data.

## Separate production gates

The reply resolves reuse rights, not proof of a particular production
acquisition or every privacy/product question. Milestone 0.23.14 permits only
NRSR2023 election-native unit summaries and national political-subject results.
Municipality-party cells (`tab03e`), precinct results and all candidate/person
records remain excluded. Small-area summaries still have contextual-inference
risk; no anonymity or zero-risk claim is made.

**Subsequent production acquisition: 2026-10-31.** The maintainer manually
downloaded all five required CSVs and confirmed the download happened “just
now” during the handoff. Acquisition time is recorded as approximately
**2026-10-31T17:20:00Z** with explicit approximate-minute precision (session
clock, not an exact download timestamp or mtime). All five freshly rehashed
files match the research digests and reviewed schemas/cardinalities. Full
native/national/party reconciliation passed before explicit production write.
**NRSR2023_PRODUCTION**, snapshot verified 2026-10-31; actual non-content
[manifest](elections-nrsr2023-acquisition.json) and [production scope](../elections.md).
The earlier `MANUAL_SOURCE_FILES_REQUIRED` pause is retained in commit history;
the reply itself did not satisfy that separate input gate.
