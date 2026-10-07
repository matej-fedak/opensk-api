# Verification Backlog

## Must Fix For Candidate 1.0 Scope

- Send the three human-dispatched outreach packages in `docs/research/source-licence-outreach.md` (PortalVS, NBS banks, telecom regulator); retain sent/received message text under `docs/research/`.
- PortalVS classifier 42 PSC licence, caching, transformation, commercial-use, and redistribution verification; otherwise exclude PSC from the stable contract.
- PortalVS classifier 9 municipality licence, caching, transformation, commercial-use, and redistribution verification; otherwise exclude municipalities from the stable contract.
- PortalVS classifier 10 district licence, caching, transformation, commercial-use, and redistribution verification; otherwise exclude districts from the stable contract.
- Resolve whether the verified PortalVS non-commercial-only copyright wording (0.23.0) applies to classifier exports and downstream commercial users of classifier 9, 10, and 42 data.
- Archive a final PortalVS snapshot (legacy classifiers 9/10/42 and the `ciselniky2.portalvs.sk` equivalents) before the verified 2026-10-31 legacy end-of-support date, with documented acquisition provenance.
- Retain exact source/licence evidence for candidate included Yellow datasets: Eurostat regions (CC BY 4.0 wording confirmed 0.23.0), NBS banks (disclaimer wording retained 0.23.0), NBS holidays (same disclaimer), telecom regulator phone areas (workbook "ďalšie spracovanie" statement retained 0.23.0), Slov-Lex vehicle registration codes (Copyright Act 185/2015 Z. z. § 5 písm. b) exclusion verified 0.23.0), MŠVVaM school facility counts (resolve exact CC BY version via DCAT), and TED procurement notices (free-reuse/CC0-metadata wording confirmed 0.23.0).
- Keep company/IČO documentation explicitly seed-backed before including it in 1.0.

## Other Follow-Ups And Excluded Domains

- RPO acquisition gate: verify official or otherwise justified bulk/local snapshot source, provenance, licence, attribution, rate limits, privacy filtering, commercial-use, and redistribution before replacing the seed-backed company dataset.
- VAT registration privacy gate: identify a reliable natural/legal subject discriminator, or approve a documented minimum-data privacy policy, before adding `GET /v1/vat/{ico}` or promoting `data/vat_registrations.json`.
- ŽRSR acquisition gate: find official documented bulk/API/open-data access, reuse terms, non-scraping refresh workflow, and deterministic natural-person exclusion before adding trade-registration importer, dataset, or endpoint.
- Register adries streets gate: verify a working official data.gov.sk or MV-authorized street distribution, reuse terms, stable identifiers, refresh workflow, and street-only privacy scope before adding `data/streets.json` or `/v1/streets`.
- Healthcare-facilities gate: verify an official NCZI/e-VUC/data.gov.sk record-level distribution, reuse terms, IdZZ fields, refresh workflow, national or explicit coverage, and deterministic facility-only privacy filtering before adding `data/healthcare_facilities.json` or `/v1/healthcare-facilities`.
- Public procurement gate: verify a current anonymous machine-readable ÚVO national notice distribution, explicit reuse/redistribution terms, refresh workflow, and privacy scope before changing `/v1/procurement-notices` from TED_PARTIAL to NATIONAL.
- Retain exact TED/Publications Office attribution wording and verify whether a larger or scheduled TED snapshot remains compatible with source limits and OpenSK privacy scope.
- Institution-level school-directory gate: verify explicit MŠVVaM/RIS/CVTI reuse rights, documented non-scraping export workflow, stable EDUID/current identifier semantics, national/scope coverage, refresh cadence, and privacy-safe institution-only fields before adding `/v1/schools` or `data/schools.json`.
- Court-decision gate: verify Ministry/court-source reuse, caching, transformation, attribution, redistribution, commercial downstream use, stable per-decision source URLs, published-decision scope, metadata-only privacy projection, and full-text exclusion before adding `/v1/court-decisions` or `data/court_decisions.json`.
- Elections spike (next data candidate, `volby.statistics.sk`): confirm explicit ŠÚ SR reuse terms beyond the OGP resolution 59/2015 publication basis, verify CSV encoding (reported Windows-1250/CP1250) and format stability on import, measure municipality-code join rate against `data/municipalities.json` via "Územné členenie" tables, bound file sizes (some preferential-vote CSVs are near 1.5 GB), and produce a go/no-go record before any `/v1/elections*` production work.
- NBS bank-code directory source/licence, local-caching, transformation, attribution, commercial-use, and redistribution-term verification.
- NBS holidays exact disclaimer retention and confirmation that curated JSON redistribution is permitted.
- Telecom regulator phone-area licence/reuse verification and follow-up on 3 source municipality rows that do not link to local municipality codes.
- Slov-Lex legal-text reuse, attribution, transformation, commercial-use, and redistribution verification for legacy vehicle registration district-code data.
- Retain exact Creative Commons BY attribution wording and licence-version details for the MŠVVaM school facility aggregate CSV.
- Monitor PSC rows whose municipality mappings could become unresolved in future source refreshes.
- Keep `docs/source-compliance.md`, `docs/research/source-verification-evidence.md`, and `data/sources.json` aligned after each source-owner answer.
