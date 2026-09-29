# Privacy Review

Review date: 2026-09-29

Scope: production JSON datasets, public API schemas, and import guardrails for the pre-1.0 public API.

## Result

No intentional personal-data dataset is exposed. Current public data is institutional, geographic, reference, aggregate, or validation-oriented.

## Dataset Notes

- Companies: current lookup is a small legal-entity seed dataset. Personal, stakeholder, statutory-body, and similar role-holder fields are intentionally excluded. 0.14.0 strengthened recursive denylist validation and kept natural-person entrepreneur records excluded by default. Broader RPO expansion remains blocked until acquisition, privacy, and redistribution terms are clarified.
- VAT registrations: 0.15.0 source inspection found official XML fields for names and addresses, but no reliable natural/legal subject marker. Production import is blocked. Generated tooling output excludes names and addresses, and validation rejects personal/name/address fields recursively.
- ŽRSR/trade registrations: 0.16.0 found only a human-facing search interface for a register that includes natural-person entrepreneurs and address-like searches. No deterministic machine-readable legal/natural subject discriminator was verified, so production import and endpoint exposure are blocked.
- Streets/Register adries: street names and administrative geography links are reference data, but full address-point records can include house numbers and exact building coordinates. 0.17.0 adds no street dataset and documents a future street-only scope that excludes house numbers, coordinates, apartment information, and person-linked address data by default.
- Healthcare facilities/providers: 0.18.0 adds no healthcare-facility dataset. NCZI NR PZS is authoritative and IdZZ is stable, but no approved source was verified. e-VUC public content can include doctors, nurses, phone numbers, absences, opening hours, individual practitioner names, and operational details, so future production scope must be facility/institution reference data only with deterministic filtering.
- School facility counts: aggregate rows only. The API does not expose school names, school IDs, addresses, staff, directors, pupils, emails, or phone numbers.
- Vehicle registration codes: historical district abbreviations only. The API does not decode full plates and does not expose vehicles or owners.
- Phone areas, PSC, regions, districts, and municipalities: public geography/reference data. Some source rows include place names, not person records.
- Banks and holidays: institutional/reference data.

## Existing Protections

- Dataset validation rejects institution-level or personal school fields such as `schoolCode`, `schoolName`, `director`, `staff`, `pupil`, `birthDate`, and personal identifiers in school facility counts.
- Company docs and tests keep the current company contract seed-backed and exclude personal role-holder data.
- Runtime routes read curated local JSON instead of proxying broad upstream records.

## 1.0 Privacy Readiness

Privacy posture is acceptable for the current 1.0 candidate scope if company lookup remains seed-backed, VAT, ŽRSR, street/address, and healthcare-facility lookup remain absent, and school data remains aggregate-only. Any production RPO/company expansion, VAT registration endpoint, ŽRSR/trade-register endpoint, street/address endpoint, healthcare-facility endpoint, or institution-level school directory would need a fresh privacy review before release.
