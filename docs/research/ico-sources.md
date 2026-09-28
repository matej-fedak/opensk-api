# IČO / Company Source Research

Status: research/tooling milestone with a small checked-in local seed dataset.

This note records source evaluation for the company/IČO dataset. It does not claim complete coverage or broader redistribution rights beyond what was directly verified.

## Summary

- Use official RPO lookup for single-record verification only after live endpoint behavior is verified for the intended workflow.
- Do not use RPO V2 / local storage for production until provenance and reuse terms are verified.
- Keep ORSR and ŽRSR as secondary references only.
- Keep RPVS separate as a future domain.
- Limit the first public company surface to legal entities.

## Source Matrix

| Source name | Source URL | API docs URL | Access method | Auth required | Licence / terms | Update cadence | Data fields | Limitations | Recommendation | Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Official RPO REST API, current public docs | `https://rpo.statistics.sk/`, `https://rpot.statistics.sk/` | `https://susrrpo.docs.apiary.io` metadata and OpenAPI-derived docs | HTTP REST lookup by IČO and related filters | No auth in the published spec | API/OpenAPI docs identify CC BY 4.0; exact official portal evidence still needs retained capture | Nightly / up to 24h lag | Identifiers, names, addresses, legal forms, legal statuses, source register, modification date, activities, statutory bodies, stakeholders, organization units | Includes natural persons and role-holder personal data; search returns max 500 and no pagination; not suitable for broad collection | Candidate for single-record verification and future offline tooling, not production bulk import yet | Medium |
| RPO V2 / local storage export, Slovensko.Digital community docs | `https://ekosystem.slovensko.digital/otvorene-api` | `https://slovakapi.dev/rpo/getting-started/overview.md` and `https://slovakapi.dev/rpo/getting-started/local-storage.md` | REST lookup plus batch export / local mirror workflow | No auth for public docs/endpoints | Community infrastructure; provenance and redistribution compatibility require verification before OpenSK production use | Live API nightly; exports monthly initial plus daily incremental; export retention about 45 days; data lag up to 24h | Same core entity fields as detail API; export docs mention identifiers, names, addresses, legal form, legal status, activities, statutory bodies, stakeholders, and organization units | Not the official source of truth; may include personal-role data; terms and upstream coverage need verification | Investigate only if official bulk access is unsuitable; not approved for production in 0.14.0 | Medium |
| `data.slovensko.sk` RPO metadata / catalog layer | `https://data.slovensko.sk/` | Catalog metadata, not a company API | Discovery/catalog only | Not verified | Do not assume redistribution rights from the catalog alone | Not verified | Metadata pointers only | No stable RPO-specific payload was directly verified in this pass | Useful for discovery, not as the primary source | Medium |
| ORSR reference only | `https://www.orsr.sk/` | No public API docs verified | Manual website lookup by IČO / company name | No auth for public lookup | Website terms apply; redistribution rights not verified | Court-level pages show updates, but no machine-readable cadence was verified | Company name, IČO, seat, court/registry details, status | HTML lookup only; not suitable for bulk import; do not scrape HTML | Secondary cross-check only | High |
| ŽRSR reference only | `https://www.zrsr.sk/` | No public API docs verified | Manual website lookup by IČO / trade name | No auth for public lookup | Website terms apply; redistribution rights not verified | No public machine-readable cadence verified | Name, IČO, address, trade-register details, active-only search | HTML lookup only; not suitable for bulk import; do not scrape HTML | Secondary cross-check only | High |

## Privacy Notes

- RPO includes natural persons, not just legal entities.
- Stakeholder and statutory-body fields can expose personal names and addresses.
- Historical data can surface past personal-role records.
- For a first release, avoid exposing FO entrepreneurs and personal-role data unless legal review explicitly covers it.

See `docs/research/rpo-licence.md` for the current licence verification status.

## Prototype Guidance

- Keep any broader expansion separate from the checked-in local seed dataset until the acquisition gate passes.
- Do not store a full raw mirror in-repo until redistribution terms and source-intended access patterns are confirmed.
- Do not claim official completeness or bulk redistribution rights.
- Current 0.14.0 decision: `RESEARCH_AND_TOOLING_ONLY`; see `docs/research/rpo-acquisition-decision.md`.
