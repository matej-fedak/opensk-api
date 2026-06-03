# IČO / Company Source Research

Status: research notes with a small checked-in local seed dataset.

This note records source evaluation for the company/IČO dataset. It does not claim complete coverage or broader redistribution rights beyond what was directly verified.

## Summary

- Use official RPO lookup for single-record verification.
- Use RPO V2 / local storage for bulk import and sync.
- Keep ORSR and ŽRSR as secondary references only.
- Keep RPVS separate as a future domain.
- Limit the first public company surface to legal entities.

## Source Matrix

| Source name | Source URL | API docs URL | Access method | Auth required | Licence / terms | Update cadence | Data fields | Limitations | Recommendation | Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Official RPO REST API, Štatistický úrad SR | `https://rpo.statistics.sk/` | `https://susrrpo.docs.apiary.io` | HTTP REST lookup by IČO and related queries | No auth in the published spec | Mirrored OpenAPI says CC BY 4.0, but official redistribution terms still need verification | Nightly / up to 24h lag | Identifiers, names, addresses, legal forms, legal statuses, source register, modification date, activities, statutory bodies, stakeholders, organization units | Includes natural persons and role-holder personal data; search can return up to 500 results; no confirmed pagination model in the public spec | Primary source for single-record lookup and verification | Medium |
| RPO V2 / local storage export, Slovensko.Digital community docs | `https://ekosystem.slovensko.digital/otvorene-api` | `https://slovakapi.dev/rpo/getting-started/overview.md` and `https://slovakapi.dev/rpo/getting-started/local-storage.md` | REST lookup plus batch export / local mirror workflow | No auth for public docs/endpoints | Community infrastructure, not the official state API; licence/redistribution still needs direct verification | Live API nightly; exports monthly initial plus daily incremental; export retention about 45 days; data lag up to 24h | Same core entity fields as the lookup API; export docs mention identifiers, names, addresses, legal form, legal status, activities, statutory bodies, stakeholders, and organization units | Community mirror, not the official source of truth; V2 describes legal entities first, not all possible register records | Best option for bulk/sync and local prototype mirroring | Medium |
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

- Keep any broader expansion separate from the checked-in local seed dataset.
- Do not store a full raw mirror in-repo until redistribution terms are confirmed.
- Do not claim official completeness or bulk redistribution rights.
