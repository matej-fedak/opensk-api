# RPO Licence Verification

Status: Licence/redistribution verification remains pending.

## Reviewed Sources

- `https://rpo.statistics.sk/`
- `https://rpo.minv.sk/manual.pdf`
- `https://data.slovensko.sk/`
- `https://susrrpo.docs.apiary.io/` (linked from the official RPO site, but not successfully rendered in this pass)
- `https://slovakapi.dev/rpo/getting-started/overview.md` and `https://slovakapi.dev/rpo/getting-started/local-storage.md` as community reference material

## Findings

- Official public rights terms were not conclusively verified in this pass.
- Community reference material points to `CC BY 4.0`, but that is not the same as an independently verified official terms page.
- Attribution may be required, but that was not fully confirmed from an official rights notice here.
- Bulk redistribution rights were not verified directly from the official source.

## Privacy / Scope

- RPO includes natural persons and role-holder data, not only legal entities.
- A legal-entities-only seed dataset is safer than a broad mirror while the licence and privacy posture remain incomplete.
- Excluding personal, stakeholder, and statutory-body fields is the conservative choice for this milestone.

## Conservative Conclusion

- Do not promote a broad RPO mirror into `data/`.
- Do not claim full rights for bulk redistribution.
- Keep the company dataset withheld until official licence and redistribution terms are verified.
