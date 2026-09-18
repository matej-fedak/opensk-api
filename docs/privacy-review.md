# Privacy Review

Review date: 2026-09-18

Scope: production JSON datasets, public API schemas, and import guardrails for the pre-1.0 public API.

## Result

No intentional personal-data dataset is exposed. Current public data is institutional, geographic, reference, aggregate, or validation-oriented.

## Dataset Notes

- Companies: current lookup is a small legal-entity seed dataset. Personal, stakeholder, statutory-body, and similar role-holder fields are intentionally excluded. Broader RPO expansion remains blocked until privacy and redistribution terms are clarified.
- School facility counts: aggregate rows only. The API does not expose school names, school IDs, addresses, staff, directors, pupils, emails, or phone numbers.
- Vehicle registration codes: historical district abbreviations only. The API does not decode full plates and does not expose vehicles or owners.
- Phone areas, PSC, regions, districts, and municipalities: public geography/reference data. Some source rows include place names, not person records.
- Banks and holidays: institutional/reference data.

## Existing Protections

- Dataset validation rejects institution-level or personal school fields such as `schoolCode`, `schoolName`, `director`, `staff`, `pupil`, `birthDate`, and personal identifiers in school facility counts.
- Company docs and tests keep the current company contract seed-backed and exclude personal role-holder data.
- Runtime routes read curated local JSON instead of proxying broad upstream records.

## 1.0 Privacy Readiness

Privacy posture is acceptable for the current 1.0 candidate scope if company lookup remains seed-backed and school data remains aggregate-only. Any RPO/company expansion or institution-level school directory would need a fresh privacy review before release.
