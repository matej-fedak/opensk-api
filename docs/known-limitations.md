# Known Limitations

- RPO company data is pending licence and privacy verification.
- Company lookup is backed by a small checked-in seed set, not a complete company register or full RPO coverage.
- RPO includes natural-person entrepreneurs and role-holder personal data.
- Personal, stakeholder, statutory-body, and similar fields are intentionally excluded from the public company response.
- Districts remain partial data and are not claimed as complete.
- Banks remain a small non-exhaustive seed dataset.
- PSC and other checked-in datasets are partial or seed-backed where the upstream provenance is still being verified.
- PSC records currently keep `districtCode` null in the checked-in dataset when no reliable local mapping exists.
- PSC redistribution is restricted by upstream PortalVS terms, and the dataset is not open redistribution material.
- Some datasets are manually curated or imported from sources with incomplete attribution or redistribution clarity.
- Remaining source follow-up items are tracked in `docs/verification-backlog.md`.
- The API has no SLA and is deployed as a hobby/public-readiness project.
- The project is not an official government endpoint and has no official endorsement.
