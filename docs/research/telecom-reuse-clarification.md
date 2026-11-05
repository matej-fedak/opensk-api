# Telecom telephone-area reuse clarification — 2026-11-02

**TELECOM_REUSE_RESOLVED · REPLY_RECEIVED_RESOLVED ·
DIRECT_INSTITUTIONAL_REUSE_CLARIFICATION**

This records maintainer-supplied institutional reply evidence. The original
mailbox message, headers and delivery metadata are retained privately and were
not independently inspected by the agent. No email was sent by the agent.

## Authority, source and reply

- Authority: **Úrad pre reguláciu elektronických komunikácií a poštových
  služieb**.
- Named institutional responder: **Ing. Marián Jurkovič**. Personal contact
  details are not repeated here.
- Reply received: **2026-11-02**, following the maintainer's manual request on
  2026-10-11 and manual follow-up on 2026-10-28.
- Covered source page:
  <https://www.teleoff.gov.sk/urad/odbory-oddelenia/odbor-regulacie-elektronickych-komunikacii/cislovanie/1.html>
- Existing production source workbook:
  <https://www.teleoff.gov.sk/files/urad/odbory-oddelenia/odbor-regulacie-elektronickych-komunikacii/cislovanie/30.xls>
  (`List1`), the page's `Zoznam obcí SR zaradených do jednotlivých primárnych
  oblastí` workbook.
- Substantive answer supplied by the maintainer: “verejne dostupné údaje
  zverejnené na [the exact page above] o slovenských telefónnych oblastiach je
  možné použiť v zmysle nižšie požadovaného.” The answer refers back to the
  original clarification request.

The retained source evidence identifies the same page, workbook and worksheet
used for the checked-in import. The reply therefore resolves reuse of the
existing source, not an obligation to acquire a new snapshot. Existing source
acquisition and schema evidence remains in `source-verification-evidence.md`
and the phone-area importer history.

## Exact requested scope mapped to the answer

The retained prepared request in `source-licence-outreach.md` §4 is not assumed
to be a byte-for-byte archived sent email. It is the request text retained by
the project and the scope to which the supplied answer refers.

| Requested use | Evidence in the retained request | Result of the 2026-11-02 answer |
| --- | --- | --- |
| Local workbook storage/caching for runtime, without live upstream queries | Explicit question 2 | Permitted for the requested OpenSK use scope |
| XLS → normalized JSON transformation | Request preamble says OpenSK redistributes normalized data through a JSON API; question 1 asks whether “ďalšie spracovanie” includes that redistribution | Permitted for the described transformation/redistribution scope |
| Public open-source API redistribution of normalized municipality-to-primary-area mappings | Preamble and explicit question 1 | Permitted |
| Commercial downstream use by API consumers | Explicit question 3 | Permitted |
| Derived joins to local municipality, district and region codes | Explicit question 6 | Permitted |
| Exact attribution wording | Explicit question 4 | **Not supplied**; no mandatory wording is invented |
| Mandatory version/update-date notices | Explicit question 5 | **Not supplied**; retain actual provenance conservatively, without inventing a rule |

The reply is deliberately not expanded to logos, website design, unrelated
regulator datasets, guaranteed accuracy, a service-level commitment, automated
acquisition, or any licence beyond the requested telephone-area use scope.

## Licence and attribution boundary

This is **direct institutional reuse clarification**, not a statement that the
data are CC BY, CC0, MIT, or under a formally named Open Data licence. The
source workbook's “údaje určené na ďalšie spracovanie zo strany prijímateľa”
statement and the 2026-11-02 answer are retained as the actual basis.

No exact attribution formula was supplied. OpenSK uses factual, conservative
attribution rather than presenting the following as mandatory verbatim text:

> Zdroj: Úrad pre reguláciu elektronických komunikácií a poštových služieb.

OpenSK also retains the original source-page URL and discloses its XLS → local
JSON normalization and local geography joins. The transformed JSON is not
represented as the regulator's original workbook. MIT covers OpenSK code, not
the regulator's data. No official endorsement is implied.

## Production decision

The production source identity is already the exact regulator page/workbook
covered by the reply, so **only compliance/source metadata changes**. No data
refresh is required or justified merely by receiving permission:

- 2,922 unique municipality-to-primary-area rows;
- 2,919 rows joined to local municipality/district/region geography;
- three unmatched source rows retained without invented geography links;
- `data/phone_areas.json` and `PHONE_AREAS_LAST_UPDATED` unchanged, including
  the byte-frozen historical embedded `metadata.license` string; the newer
  reply is exposed through the maintained registry/public source projection;
- runtime remains local JSON only, with no upstream call or automatic
  downloader.

Future monitoring/refresh must be deliberate and provenance-preserving; public
availability and download links do not by themselves authorize automated
collection. A future workbook snapshot requires the usual source identity,
hash, schema, row-count and diff review before promotion.

## Public source-catalogue state

`phoneAreas` records: reuse verified by direct institutional clarification on
2026-11-02; redistribution allowed for the requested OpenSK scope, including
commercial downstream use; coverage remains **complete** in the existing
source-relative sense; risk reduced from pending to **low** because the specific
production use is directly answered. The absence of a formal licence name or
mandatory exact attribution sentence is disclosed rather than treated as an
unresolved redistribution blocker.

Final verdict: **TELECOM_REUSE_RESOLVED**.
