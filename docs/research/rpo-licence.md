# RPO Licence Verification

Status: RPO API documentation identifies CC BY 4.0, but production redistribution and bulk-acquisition evidence remains insufficient for OpenSK production import.

## Reviewed Sources

- `https://rpo.statistics.sk/`
- `https://rpo.minv.sk/manual.pdf`
- `https://data.slovensko.sk/`
- `https://susrrpo.docs.apiary.io/` (linked from the official RPO site, but not successfully rendered in this pass)
- `https://slovakapi.dev/rpo/getting-started/overview.md` and `https://slovakapi.dev/rpo/getting-started/local-storage.md` as community reference material

## Findings

- Current API/OpenAPI documentation identifies `Creative Commons Attribution 4.0 (CC BY 4.0)` and links `https://creativecommons.org/licenses/by/4.0/legalcode`.
- The current portal is JavaScript-rendered, so exact operator/licence evidence should be retained through browser/manual capture before production promotion.
- Attribution is required by CC BY 4.0.
- Bulk acquisition through REST is not supported by the documented search endpoint because it is filter-based, capped at 500 results, and lacks pagination.
- Third-party local-storage exports may be useful later, but provenance and redistribution compatibility must be verified before production use.

## Privacy / Scope

- RPO includes natural persons and role-holder data, not only legal entities.
- A legal-entities-only seed dataset is safer than a broad mirror while the licence and privacy posture remain incomplete.
- Excluding personal, stakeholder, and statutory-body fields is the conservative choice for this milestone.

## Conservative Conclusion

- Do not promote a broad RPO mirror into `data/` during 0.14.0.
- Do not claim full rights for bulk redistribution until official or otherwise justified acquisition terms are retained.
- Keep the company dataset seed-backed until the acquisition gate returns `PRODUCTION_IMPORT_APPROVED`.
