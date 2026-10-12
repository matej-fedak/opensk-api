# Exchange-rate source & licence verification — ECB and NBS

**Task:** OpenSK milestone 0.23.3, branch `research/exchange-rates-resilience`, Agent A (source/licence specialist).
**Verification date:** 2026-10-11 (all URLs below live-checked on this date unless stated otherwise).
**Scope:** Fresh verification of reuse terms for official EUR foreign-exchange reference-rate sources: (1) European Central Bank (ECB) euro foreign exchange reference rates; (2) National Bank of Slovakia (NBS) exchange-rate publications.

**Verdict (summary):**
- **ECB: CLEAR** for OpenSK use — free reuse (including redistribution) is explicitly granted on the ECB website under attribution conditions; the specific feeds/API return data under the ECB "Disclaimer & Copyright" terms. No open-data licence (CC/ODC) is claimed, and none is needed given the explicit permission wording. Condition 2 (inform buyers data is free) only matters if access is ever sold. Sui-generis/database right is not addressed in the wording — residual ambiguity, low practical risk. See §1.4.
- **NBS: republication only.** NBS has published no exchange-rate concept of its own since euro adoption (2009-01-01). Its machine-readable exchange-rate endpoints are redistributions of ECB reference rates (NBS XML even retains the ECB `gesmes`/eurofxref namespace). Use ECB as the canonical source.

---

## 1. European Central Bank (ECB)

### 1.1 Publisher and machine-readable sources

- Publisher: **European Central Bank, Frankfurt am Main, Germany** (ECB Copyright wording, §1.3).
- Human-readable page: https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html
- Machine-readable feeds (all live-checked 2026-10-11, HTTP 200, `text/xml`, gesmes:Envelope format):
  - Daily: `https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml` (observed latest business day 2026-10-09)
  - Last 90 days: `https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml`
  - Full history (since 1999): `https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.xml`
- SDMX 2.1 RESTful API: `https://data-api.ecb.europa.eu/service/data/EXR/...` — verified live with
  `https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A?lastNObservations=1` (HTTP 200, CSV via `Accept: text/csv`; note: `Accept: application/vnd.sdmx.data+csv` is rejected with 406 — the ECB API uses vendor type `application/vnd.ecb.data+csv;version=1.0.0`).
  - API documentation: https://data.ecb.europa.eu/help/api/overview — states: *"All disseminated data are available via the Statistical Data and Metadata eXchange (SDMX) API. We implement the SDMX 2.1 standard."* (page "All data services", https://www.ecb.europa.eu/stats/accessing-our-data/html/index.en.html)
- Confidence: **high** (all endpoints live-verified).

### 1.2 Licence / reuse terms — exact retained wording

Source: ECB website, **"Disclaimer & copyright"** page, https://www.ecb.europa.eu/services/disclaimer/html/index.en.html (footer link "Disclaimer & Copyright" on every ECB page; checked 2026-10-11). Retained verbatim:

> "Copyright © for the entire content of this website: European Central Bank, Frankfurt am Main, Germany.
>
> Subject to the exception below, users of this website may make free use of the information obtained directly from it subject to the following conditions:
>
> 1. When such information is distributed or reproduced, it must appear accurately and the ECB must be cited as the source.
>
> 2. Where the information is incorporated in documents that are sold (regardless of the medium), the natural or legal person publishing the information must inform buyers, both before they pay any subscription or fee and each time they access the information taken from this website, that the information may be obtained free of charge through this website.
>
> 3. If the information is modified by the user (e.g. by seasonal adjustment of statistical data or calculation of growth rates) this must be stated explicitly.
>
> 4. When linking to this website from business sites or for promotional purposes, this website must load into the browser's entire window (i.e. it must not appear within another website's frame).
>
> As an exception to the above, any reproduction, publication or reprint, in whole or in part, of documents that bear the name of their authors, such as ECB Working Papers and ECB Occasional Papers, in the form of a different publication (whether printed or produced electronically) is permitted only with the explicit prior written authorisation of the ECB or the authors."

Interpretation for OpenSK:
- Reproduction and distribution are **explicitly permitted free of charge**, commercial use is contemplated (condition 2 sets rules for sale, it does not prohibit it). **Attribution: "the ECB must be cited as the source."**
- Transformation (e.g., reformatting into OpenSK structures) must be **stated explicitly** (condition 3).
- OpenSK never sells the data → condition 2 inapplicable; documenting it anyway is good practice.
- The exception clause covers authored **documents** (Working/Occasional Papers) and does not apply to statistical data feeds.
- Confidence: **high** (verbatim quote retained).

### 1.3 Required disclaimers (ECB reference rates)

From the reference-rates page itself (https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html, checked 2026-10-11):

> "The reference rates are usually updated at **around 16:00 CET** every working day, except on TARGET closing days. They are based on the daily concertation procedure between central banks across Europe, which normally takes place around 14:10 CET. **The reference rates are published for information purposes only. Using the rates for transaction purposes is strongly discouraged.**"

From the Disclaimer section of the same legal page (ichi liability carve-out specific to FX rates):

> "While the euro short-term rate (€STR), the euro foreign exchange reference rates and other price information published on this website are based on sources which the ECB considers to be reliable, the ECB accepts no responsibility or liability for any loss, damage, expense or claim incurred in connection with any decision made or action or inaction on the part of any party in reliance upon such publication."

OpenSK must propagate: (a) "Source: European Central Bank" attribution; (b) the "for information purposes only / strongly discouraged for transactions" notice at least once prominently (e.g., dataset documentation and/or API response metadata).

### 1.4 Transformation / caching / redistribution status

| Activity | Supportable? | Basis |
|---|---|---|
| Download feeds / query API, automated | **Yes** | Terms permit "free use"; ECB explicitly offers machine-to-machine channels (SDMX API, feeds, RSS, MID). robots.txt (www.ecb.europa.eu, checked 2026-10-11) does not disallow `/stats/`; it sets `Crawl-delay: 5` for `User-agent: *` — treat ≥5 s between requests to the website host as the expected etiquette. No published rate-limit numbers were found for data-api.ecb.europa.eu (help API overview page contains no rate-limit text; residual low-priority question). |
| Local caching / storage in repo | **Yes** (implicit but clear) | "Free use ... distributed or reproduced ... accurately ... ECB cited as source" — storage is a necessary means of reproduction; nothing prohibits it. |
| Redistribution via public API | **Yes** | Explicitly covered: "When such information is distributed or reproduced, it must appear accurately and the ECB must be cited as the source." |
| Commercial redistribution | Contemplated (with disclosure duty, condition 2) | Not needed by OpenSK. |
| Sui-generis database right | **Not addressed** in ECB wording | Unresolved theoretical point: ECB's permission text does not mention Directive 96/9/EC sui-generis rights over the database as such. The grant "users ... may make free use of the information obtained directly from it" is broad and, in practice, ECB statistics are reused globally under it. Confidence this is a real blocker: **low**. If belt-and-braces assurance is wanted, ask ECB (draft in §3). |

### 1.5 Update schedule, timezone, business-day basis, revisions

- Schedule: "around 16:00 CET every working day, except on TARGET closing days" — business-day basis is the **TARGET calendar** (TARGET closing-day list: https://www.ecb.europa.eu/ecb/contacts/working-hours/html/index.en.html). Concertation procedure "normally takes place around 14:10 CET" (ECB page) — note NBS page quotes it as 14:15 CET, minor upstream vs. downstream wording difference; ECB canonical value is "around 14:10 CET".
- Revisions/corrections: not found as an explicit revision-policy statement on the checked pages. Reference rates are point-in-time published once per TARGET day; the SDMX `EXR` series carry status/obs attributes. Treat "revision behaviour undocumented in the pages checked" as an open low-risk question. Confidence: **medium**.

### 1.6 DCAT / open-data catalogue entries

- The ECB Data Portal (https://data.ecb.europa.eu/) is the official catalogue, with dataset-level metadata and API help (https://data.ecb.europa.eu/help/api/overview).
- A **data.europa.eu (EU Open Data Portal) DCAT entry specifically for the euro FX reference rates could not be verified** on 2026-10-11 (search attempts returned nothing; the hub search API endpoint used rejected the query). Not blocking: reuse does not depend on a DCAT registration. Confidence: **not verified**.

### 1.7 Automated offline acquisition

- **Supportable, explicit-design**: ECB provides feeds (XML), an SDMX API, RSS, and a "Market Information Dissemination (MID)" system described as "structured and suitable for automatic processing" ("All data services" page). No robots.txt prohibition on the relevant paths; `Crawl-delay: 5` applies to the website host. Verdict: **CLEAR** — automated acquisition is not merely tolerated, it is ECB's intended consumption mode. Confidence: **high**.

---

## 2. National Bank of Slovakia (NBS)

### 2.1 What NBS publishes

Exchange-rates section: https://nbs.sk/en/statistics/exchange-rates/ contains:

- **"ECB foreign exchange reference rates"**: https://nbs.sk/en/statistics/exchange-rates/ecb-foreign-exchange-reference-rates/ — page text quotes ECB wording and notes RUB suspension (ECB decision of 1 March 2022) and HRK removal (Croatia's euro adoption, 2023). Explicit machine-readability note on that page:
  > "Information on the automated processing of ECB exchange rate files — As of 18.5.2022, the URL structure for the exchange rate list source data has changed.
  > Current exchange rate of the ECB — XML: https://nbs.sk/export/en/exchange-rate/latest/xml ; CSV: https://nbs.sk/export/en/exchange-rate/latest/csv ; PDF: https://nbs.sk/export/en/exchange-rate/latest/pdf
  > URL structure: https://nbs.sk/export/en/exchange-rate/YYYY-MM-DD/file_type"
- "Monthly, cumulative and annual exchange rates" (NBS-computed aggregates of ECB daily rates — the only conceivable NBS value-add).
- "Exchange Rates of Selected Foreign Currencies against the EUR" and "Historical Exchange Rates in SKK" (pre-2009 archive).

**Live verification 2026-10-11:** `https://nbs.sk/export/en/exchange-rate/latest/xml` returns HTTP 200 with a `gesmes:Envelope` document using the ECB namespace `http://www.ecb.int/vocabulary/2002-08-01/eurofxref` and subject "Reference rates" — i.e., the file is the ECB's own feed format redistributed. The CSV for 9.10.2026 matches the ECB daily rates exactly (USD 1.1206, JPY 177.34, CZK 24.369, ...).

### 2.2 NBS value-add verdict

- **Republication only** for daily EUR reference rates. Slovakia uses the euro since 2009-01-01; NBS no longer sets or computes any rate of its own in this domain. The only NBS-specific artefacts are (a) redistributed ECB files via a convenience endpoint, and (b) derived monthly/cumulative/annual aggregates. The historical SKK kurzový lístok (pre-2009) is a distinct historical concept, irrelevant to live EUR rates.
- For OpenSK: **use ECB directly**; the NBS endpoint adds no data, only mirror risk. Confidence: **high**.

### 2.3 NBS reuse terms (for completeness)

NBS Disclaimer (https://nbs.sk/en/disclaimer_en/, checked 2026-10-11), verbatim:

> "Information published on this website may be stored, reproduced, and further used\* provided that the source is acknowledged and that neither the content nor other properties of the respective electronic file are modified in any way."

Note the condition "**neither the content nor other properties of the respective electronic file are modified in any way**" — stricter than ECB for file-level redistribution, and irrelevant for OpenSK since we will source from ECB. If anything came from NBS aggregates, transformation for redistribution would be ambiguous under this wording. Confidence: **high** on wording; **not applicable** in practice.

---

## 3. Unresolved questions & (optional) outreach draft

1. **ECB sui-generis/database right not addressed** in the Copyright wording (reuse grant is broad but does not name Directive 96/9/EC rights). Practical risk: low.
2. **No published quantitative rate limits** found for `data-api.ecb.europa.eu` / Data Portal API (only `Crawl-delay: 5` on the website robots.txt). Operational etiquette: single daily pull after ~16:00 CET is trivially within any sane limit.
3. **Revision/correction policy** for published reference rates not stated on the pages checked.
4. **DCAT registration** on data.europa.eu for the FX dataset not verified.

No clarification from ECB is required to proceed (verdict is CLEAR under the published terms). Should the project want written certainty on point 1, the following is **READY_FOR_USER_TO_SEND** (NOT sent):

> **EN** — To: ECB statistical information request (form: https://form.ecb.europa.eu/services/rest/statisticalinformationrequest/)
> Subject: Reuse confirmation – euro foreign exchange reference rates in an open-source public API
> Body: "Dear ECB Statistics team, we operate the open-source project OpenSK, which caches the euro foreign exchange reference rates (eurofxref XML feeds and/or SDMX dataset EXR) and redistributes them, unmodified in value, through a free public API with 'Source: European Central Bank' attribution and the 'for information purposes only' notice. Your 'Disclaimer & copyright' page grants free use of website information subject to attribution and accuracy conditions. Could you please confirm that (a) this includes the machine-readable statistical feeds/API, and (b) you make no claim under the sui-generis database right (Directive 96/9/EC) that would restrict such caching and redistribution? Thank you."
>
> **SK** — Predmet: Potvrdenie opätovného použitia – referenčné výmenné kurzy eura v open-source verejnom API
> Telo: "Dobrý deň, prevádzkujeme open-source projekt OpenSK, ktorý ukladá do vyrovnávacej pamäte referenčné výmenné kurzy eura (XML kanály eurofxref a/alebo dataset EXR cez SDMX) a bez zmeny hodnôt ich ďalej poskytuje cez bezplatné verejné API s uvedením zdroja 'European Central Bank' a poznámkou, že kurzy slúžia len na informačné účely. Vaša stránka 'Disclaimer & copyright' umožňuje bezplatné použitie informácií z webu za podmienky uvedenia zdroja a presnosti. Potvrďte nám, prosím, že (a) toto sa vzťahuje aj na strojovo čitateľné štatistické kanály/API a (b) neuplatňujete nárok z práva sui generis k databáze (smernica 96/9/ES), ktorý by takéto ukladanie a šírenie obmedzoval. Ďakujeme."

---

## Appendix — checked URLs (all on 2026-10-11)

| URL | Result |
|---|---|
| https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html | 200; wording quoted in §1.3, §1.5 |
| https://www.ecb.europa.eu/services/disclaimer/html/index.en.html | 200; Copyright & Disclaimer wording quoted in §1.2, §1.3 |
| https://www.ecb.europa.eu/stats/accessing-our-data/html/index.en.html | 200; data services incl. SDMX API, MID |
| https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml | 200 XML (rates as of 2026-10-09) |
| https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml | 200 XML |
| https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.xml | 200 XML |
| https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A?lastNObservations=1 | 200 (CSV via `Accept: text/csv`); USD=1.1206 for 2026-10-09 |
| https://www.ecb.europa.eu/robots.txt | 200; `Crawl-delay: 5`, no disallow of `/stats/` |
| https://nbs.sk/en/statistics/exchange-rates/ | 200; section listing |
| https://nbs.sk/en/statistics/exchange-rates/ecb-foreign-exchange-reference-rates/ | 200; automated-processing export URLs |
| https://nbs.sk/export/en/exchange-rate/latest/xml | 200; ECB-namespace gesmes file (republication) |
| https://nbs.sk/export/en/exchange-rate/latest/csv | 200; values identical to ECB daily |
| https://nbs.sk/en/disclaimer_en/ | 200; NBS reuse wording quoted in §2.3 |
