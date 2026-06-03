# Known Limitations

- RPO company data is pending licence verification.
- Company lookup is dataset-pending and may return `503 DATASET_UNAVAILABLE` until a local dataset is approved.
- RPO includes natural-person entrepreneurs and role-holder personal data.
- Personal, stakeholder, statutory-body, and similar fields are intentionally excluded from the public company response.
- Districts remain seed/partial data and are not claimed as complete.
- Banks remain a small non-exhaustive seed dataset.
- PSC records currently keep `districtCode` null in the checked-in dataset when no reliable local mapping exists.
- PSC source/licence verification remains pending.
- The API has no SLA and is deployed as a hobby/public-readiness project.
- The project is not an official government endpoint and has no official endorsement.
