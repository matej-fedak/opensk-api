# Verification Backlog

- Retain exact Eurostat LAU 2025 workbook reuse notice and attribution requirements.
- PortalVS classifier 42 PSC licence, caching, transformation, commercial-use, and redistribution verification.
- PortalVS classifier 9 municipality licence, caching, transformation, commercial-use, and redistribution verification.
- PortalVS classifier 10 district licence, caching, transformation, commercial-use, and redistribution verification.
- RPO acquisition gate: verify official or otherwise justified bulk/local snapshot source, provenance, licence, attribution, rate limits, privacy filtering, commercial-use, and redistribution before replacing the seed-backed company dataset.
- VAT registration privacy gate: identify a reliable natural/legal subject discriminator, or approve a documented minimum-data privacy policy, before adding `GET /v1/vat/{ico}` or promoting `data/vat_registrations.json`.
- ŽRSR acquisition gate: find official documented bulk/API/open-data access, reuse terms, non-scraping refresh workflow, and deterministic natural-person exclusion before adding trade-registration importer, dataset, or endpoint.
- Register adries streets gate: verify a working official data.gov.sk or MV-authorized street distribution, reuse terms, stable identifiers, refresh workflow, and street-only privacy scope before adding `data/streets.json` or `/v1/streets`.
- Healthcare-facilities gate: verify an official NCZI/e-VUC/data.gov.sk record-level distribution, reuse terms, IdZZ fields, refresh workflow, national or explicit coverage, and deterministic facility-only privacy filtering before adding `data/healthcare_facilities.json` or `/v1/healthcare-facilities`.
- NBS bank-code directory source/licence, local-caching, transformation, attribution, commercial-use, and redistribution-term verification.
- NBS holidays exact disclaimer retention and confirmation that curated JSON redistribution is permitted.
- Telecom regulator phone-area licence/reuse verification and follow-up on 3 source municipality rows that do not link to local municipality codes.
- Slov-Lex legal-text reuse, attribution, transformation, commercial-use, and redistribution verification for legacy vehicle registration district-code data.
- Retain exact Creative Commons BY attribution wording and licence-version details for the MŠVVaM school facility aggregate CSV.
- Monitor PSC rows whose municipality mappings could become unresolved in future source refreshes.
- Keep `docs/source-compliance.md`, `docs/research/source-verification-evidence.md`, and `data/sources.json` aligned after each source-owner answer.
