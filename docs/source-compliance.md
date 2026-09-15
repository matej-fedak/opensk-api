# Source Compliance

OpenSK API serves checked-in JSON files at runtime. No API route calls upstream services, and this project is not an official government endpoint.

This page records the current source-compliance posture. It is not legal advice. Keep conservative warnings until the relevant source owner confirms reuse and redistribution terms.

| Dataset | Runtime scope | Source | Source URL | Terms URL | Licence status | Redistribution status | Attribution wording | Terms basis | Risk | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Regions | complete | Eurostat LAU 2025 correspondence table | `https://ec.europa.eu/eurostat/web/nuts/local-administrative-units` | `https://ec.europa.eu/info/legal-notice_en` | Reuse terms identified; redistribution verification still required. | Verify before redistribution. | Attribute Eurostat as the source when reusing LAU correspondence data. | official terms page, exact workbook notice still pending in repo | medium | Retain exact Eurostat reuse notice for the LAU 2025 workbook and confirm redistribution conditions. |
| Districts | complete imported | PortalVS classifier 10 (Okres) | `https://ciselniky.portalvs.sk/api/rest/json/10` | pending | Source/licence verification pending. | Restricted / not open redistribution. | Attribute PortalVS classifier 10 if reuse is approved; exact wording pending. | pending | pending | Ask PortalVS whether classifier 10 may be cached and redistributed through an open-source API. |
| Municipalities | complete imported | PortalVS classifier 9 (Obce) | `https://ciselniky.portalvs.sk/api/rest/json/9` | pending | Source/licence verification pending. | Restricted / not open redistribution. | Attribute PortalVS classifier 9 if reuse is approved; exact wording pending. | pending | pending | Ask PortalVS whether classifier 9 may be cached and redistributed through an open-source API. |
| PSC | partial imported | PortalVS classifier 42 (PSČ obcí SR a ČR) | `https://ciselniky.portalvs.sk/classifier/show/42/` | pending | Source/licence verification pending. | Restricted / not open redistribution. | Attribute PortalVS classifier 42 if reuse is approved; exact wording pending. | pending | high | Ask PortalVS whether classifier 42 may be cached, transformed, and redistributed. |
| Banks | complete imported | NBS directory of domestic payment-system identification codes | `https://nbs.sk/en/payments/general-information/directories-and-registers/directory-identification-codes-domestic-payment-system-in-sr/` | pending | Source/licence verification pending. | Pending verification. | Attribute the National Bank of Slovakia directory if reuse is approved; exact wording pending. | official source page, terms pending | pending | Ask NBS whether the directory may be cached, transformed, and redistributed in an open-source API. |
| Holidays | partial/curated seed | NBS holidays page and Act 241/1993 | `https://www.nbs.sk/en/about-the-bank/holidays-in-slovakia/` | pending | Reuse statement identified; exact dataset redistribution terms should be retained on file. | Allowed with attribution and no modification, pending retained evidence. | Attribute the National Bank of Slovakia holidays page and Act 241/1993 where applicable. | official source page plus legal act reference; exact notice pending in repo | medium | Retain the exact NBS disclaimer text and confirm curated JSON redistribution conditions. |
| Companies | seed-only | Verified public organizational contact pages | Multiple official contact pages | pending | Source/licence verification pending for broader redistribution. | Pending verification. | Attribute each verified organizational source where practical; exact wording is source-specific and pending. | source-specific pages, RPO expansion pending | pending | Ask ŠÚ SR/RPO about reuse, local caching, redistribution, commercial use, bulk limits, and privacy constraints. |
| Phone areas | complete imported | Úrad pre reguláciu elektronických komunikácií a poštových služieb numbering data | `https://www.teleoff.gov.sk/urad/odbory-oddelenia/odbor-regulacie-elektronickych-komunikacii/cislovanie/1.html` | pending | Source/licence verification pending. | Pending verification. | Attribute the telecom regulator numbering data if reuse is approved; exact wording pending. | official source page and retained workbook URL | pending | Verify reuse, caching, transformation, redistribution, commercial-use, and attribution terms for the retained workbook. |

## Current Rules

- Runtime requests must read local files only.
- Do not add new endpoint domains until unresolved licence and redistribution questions are reduced.
- Do not scrape ORSR, ŽRSR, or unstable HTML pages for runtime data.
- Do not remove `Source/licence verification pending.` or risk warnings without retained evidence.
- Do not claim official endorsement.

## Unresolved Questions

- Whether PortalVS classifiers can be redistributed through an open-source API and by downstream commercial users.
- Whether transformed/local JSON snapshots count as modified data under NBS terms.
- Whether the NBS bank-code directory has a specific attribution or no-modification requirement.
- Whether RPO or ŠÚ SR permits local caching and public redistribution, especially when source material can include natural-person entrepreneurs or role-holder personal data.
- Whether each source has required notices that must be preserved verbatim in docs or API metadata.
