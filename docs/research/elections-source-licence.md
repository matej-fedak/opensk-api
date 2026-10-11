# Elections source and reuse evidence — OpenSK 0.23.2 spike

Verified: **2026-10-11** (local clock `2026-10-11T21:31:48+02:00`). Branch: `data/elections-spike`. Research only; no production clearance, no email sent, no commit. No `AGENTS.md` was found in the workspace search.

## Conclusion

**Official NRSR2023 provenance and a published download index are verified (high confidence). ŠÚ SR's general statistical-information policy expressly permits redistribution and commercial use and applies CC BY 4.0. However, election-specific applicability and permitted automated acquisition remain unresolved (medium confidence on applicability; no automated-acquisition approval). Keep `RESEARCH_AND_TOOLING_ONLY` / `Source/licence verification pending.` until clarified.**

The policy explicitly prohibits robots, crawlers and similar data-gathering/download tools. Do not implement an unattended fetcher or infer an exception for direct CSV/ZIP downloads. A manually supplied snapshot/offline parser is a possible workflow to ask about, not an already approved production route. Neither OGP commitments nor downloadability are used as licence evidence.

## 1. Official provenance (directly inspected 2026-10-11)

### Election archive landing page

URL: https://volby.statistics.sk/

Exact quotes (HTML text, whitespace normalized):

> Na základe § 9 zákona č. 540/2001 Z. z. o štátnej štatistike v znení neskorších predpisov zabezpečuje Štatistický úrad Slovenskej republiky organizačné, personálne, programové a technické podmienky na spracovanie výsledkov volieb a referenda konaných podľa osobitných zákonov.

> V spolupráci s Ministerstvom vnútra SR vydáva Štatistický úrad SR metodiku spracovania výsledkov hlasovania, spracováva výsledky volieb, na pokyn štátnej komisie ich zverejňuje na svojom webovom sídle.

The page links NRSR **2023** to `http://volby.statistics.sk/nrsr/nrsr2023/sk/index.html`; the HTTPS election pages were inspected directly. Confidence: **high** for publisher/provenance, not a statutory licence conclusion.

### NRSR2023 download page

URL: https://volby.statistics.sk/nrsr/nrsr2023/sk/subory_na_stiahnutie.html

Exact quotes:

> Nachádzate sa na oficiálnom webovom sídle orgánu verejnej moci Slovenskej republiky – Štatistického úradu Slovenskej republiky.

> Zdroj: Štatistický úrad SR

> Prevádzkovateľom služby je Štatistický úrad Slovenskej republiky.

> Dátum a čas zverejnenia výsledkov: 01.10.2023 14:30

HTML marks `data-phase="def"`, and navigation labels these as **Definitívne výsledky**. The publication timestamp is the page's stated historical timestamp, **not** the verification date or a verified file Last-Modified timestamp. The page loads its last-update display from `../json/dateSK.json`; that date was not fetched/verified here.

## 2. Download index and exact advertised distribution URLs

The page explicitly advertises:

| Exact visible label | Resolved link from inspected HTML |
| --- | --- |
| Súbory vo formáte XLSX (ZIP 65,4 MB) | https://volby.statistics.sk/nrsr/nrsr2023/files/NRSR2023_SK_xlsx.zip |
| Súbory vo formáte ODS (ZIP 61,7 MB) | https://volby.statistics.sk/nrsr/nrsr2023/files/NRSR2023_SK_ods.zip |
| Súbory vo formáte CSV (ZIP 215,5 MB) | https://volby.statistics.sk/nrsr/nrsr2023/files/NRSR2023_SK_csv.zip |

Sizes above are advertised display values, not measured response lengths. None of these ZIPs was downloaded or inspected by this agent.

The page calls `downloadTab('def')`. Inspected official JavaScript https://volby.statistics.sk/nrsr/nrsr2023/js/functions.js resolves the table via exact expression `"url": "../json/download"+lang+".json"`. The directly inspected Slovak index is:

https://volby.statistics.sk/nrsr/nrsr2023/json/downloadSK.json

Its `Code`, `Name`, `csv`, `ods`, `xlsx` fields advertise **33 table entries**, grouped below. This is a web-page index, **not a documented public API contract**.

| Code suffix (prefix `NRSR2023_SK_`) | Index contents (decoded names; groups summarized) |
| --- | --- |
| `tab_info` | Exact name: `Zoznam tabuliek` |
| `tab0a` | Exact name: `Zoznam kandidujúcich politických subjektov` |
| `tab0b` | Exact name: `Zoznam kandidátov` |
| `tab0c` | Exact name: `Územné členenie` |
| `tab0d` | Exact name: `Veková štruktúra kandidátov` |
| `tab01` | Exact name: `Súhrnné výsledky hlasovania za SR` |
| `tab02a`–`tab02e`, `tab02x` | Summary voting results: regions, electoral territorial units, districts, municipalities, polling districts, cities/city parts/municipalities |
| `tab03a`–`tab03f` | Party/subentity vote counts and shares: SR through polling districts |
| `tab04` | Exact name: `Pridelenie mandátov politickým subjektom` |
| `tab04x` | Exact name: `Súhrnné údaje k prideľovaniu mandátov politickým subjektom` |
| `tab06` | Exact name: `Zvolení poslanci Národnej rady Slovenskej republiky` |
| `tab07a`–`tab07f` | Candidate preference votes: SR through polling districts |
| `tab08a`–`tab08e`, `tab08x` | Party vote counts/shares, horizontal view: regions through polling districts and city/city-part/municipality grouping |

Representative exact resolved CSV links from that index:

- https://volby.statistics.sk/nrsr/nrsr2023/files/csv/NRSR2023_SK_tab_info.csv
- https://volby.statistics.sk/nrsr/nrsr2023/files/csv/NRSR2023_SK_tab0a.csv
- https://volby.statistics.sk/nrsr/nrsr2023/files/csv/NRSR2023_SK_tab0c.csv
- https://volby.statistics.sk/nrsr/nrsr2023/files/csv/NRSR2023_SK_tab01.csv
- https://volby.statistics.sk/nrsr/nrsr2023/files/csv/NRSR2023_SK_tab03a.csv
- https://volby.statistics.sk/nrsr/nrsr2023/files/csv/NRSR2023_SK_tab03e.csv
- https://volby.statistics.sk/nrsr/nrsr2023/files/csv/NRSR2023_SK_tab03f.csv
- https://volby.statistics.sk/nrsr/nrsr2023/files/csv/NRSR2023_SK_tab04.csv

Individual CSV/ODS/XLSX responses, checksums, embedded notices, encoding and consistency were **not verified by this agent**. Large candidate tables are advertised (`tab07e` CSV 804,2 MB; `tab07f` CSV 1,7 GB); no reason to acquire them for aggregate-only licence research.

### Different provenance: election commission minutes

The same download page also offers `NRSR2023_SK_ZapisniceOVK.zip`, with exact source label:

> Zdroj: Štátna komisia pre voľby a kontrolu financovania politických strán

Source link: https://www.minv.sk/?statnakomisia_zapisnicenr23

Do **not** assume ŠÚ SR's CC BY policy clears these third-party minutes, signatures, logos, website assets or external documents. They are excluded from this proposed aggregate-data scope.

## 3. Exact official reuse terms

Official general terms URL: https://slovak.statistics.sk/wps/portal/ext/aboutus/webpage/terms/

Directly inspected Slovak language URL (the base URL initially returned English):

https://slovak.statistics.sk/wps/portal/ext/aboutus/webpage/terms/!ut/p/z1/jZDNDoIwEISfhSfoSrGtxy0GWFPFghXsxXAiJIoejM_vHycTkb1N8s3MZphnNfN9c-_a5tZd-ub01AcvjnuzVVrPEPJiFQElMYLeWU5GsOoNxClmkTQAyqRzIMxcsbCcA3Lmp_jhxyFM848Afjy-Yv67Al8JpYuTdRmKNBoAK-kDqM1SA0kjrSLNcx0OwNgG_764np2roaMWg-ABaDPkww!!/dz/d5/L0lDUmlTUSEhL3dHa0FKRnNBLzROV3FpQSEhL3Nr/

Title: **Podmienky pre využívanie a ďalšie zverejňovanie štatistických informácii Štatistického úradu SR**. Stated page update: **15.03.2023**. Inspected **2026-10-11**. Attempts on `susr.statistics.sk` returned transport errors; the working `slovak.statistics.sk` page supplied the direct evidence. Quotes below preserve source wording; only HTML/whitespace formatting is removed.

Scope lead-in:

> Štatistické informácie zverejnené prostredníctvom internetových stránok Štatistického úradu SR www.statistics.sk

Permissions, following `je možné:`:

> šíriť (kopírovať, sprostredkovávať a distribuovať verejnosti);
>
> využívať a citovať v iných dielach;
>
> využívať komerčne.

Attribution / non-endorsement condition:

> ako zdroj informácii bude uvedený Štatistický úrad Slovenskej republiky (nesmie tým však vzniknúť dojem, že Štatistický úrad SR podporuje užívateľov informácii a údajov alebo spôsob, akým dielo užívajú);

Named licence and notice condition:

> v prípade šírenia informácii Štatistický úrad SR uplatňuje použitie medzinárodnej verejnej licencie Creative Commons Attribution License (cc-by) 4.0 a vzniká povinnosť uviesť podmienky tejto licencie, najlepšie priamym odkazom na internetovú stránku www.statistics.sk;

Third-party exception:

> pravidlá upravujúce opakované použitie dokumentov Štatistického úradu SR neplatia pre dokumenty, na ktoré sa vzťahujú práva duševného vlastníctva tretích strán;

Liability and availability:

> Štatistický úrad SR sa zrieka zodpovednosti za prípadné škody spôsobené v dôsledku používania dát z internetových stránok Štatistického úradu SR alebo externých stránok, na ktoré sa tu odkazuje;
>
> Štatistický úrad SR si vyhradzuje právo z prevádzkových alebo odborných dôvodov dočasne obmedziť prístup k týmto informáciám aj bez predchádzajúceho upozornenia.

**Acquisition restriction (must not be omitted):**

> používanie robotov, pavúkov (spiders, crawlers) a ďalších podobných nástrojov na zhromažďovanie a sťahovanie dát, je výslovne zakázané.

Confidence: **high** that these are the general published terms. **Medium** for coverage of election downloads: they are published on an official ŠÚ SR website, but the policy names `www.statistics.sk` and the inspected election download page has no dataset-specific licence link or explicit subdomain coverage declaration. Ask the publisher rather than silently treating the general policy as full production clearance. Acquisition permission is distinct from downstream reuse rights.

## 4. What CC BY 4.0 would permit and require, if confirmed applicable

Directly inspected licence legal code: https://creativecommons.org/licenses/by/4.0/legalcode.en (2026-10-11). The official ŠÚ SR policy links https://creativecommons.org/licenses/by/4.0/legalcode .

Exact excerpts:

- Section 2(a)(1)(A): `reproduce and Share the Licensed Material, in whole or in part; and`
- Section 2(a)(1)(B): `produce, reproduce, and Share Adapted Material.`
- Section 2(a)(4): `The Licensor authorizes You to exercise the Licensed Rights in all media and formats whether now known or hereafter created, and to make technical modifications necessary to do so.`
- Section 3(a)(1)(B): `indicate if You modified the Licensed Material and retain an indication of any previous modifications; and`
- Section 3(a)(1)(C): `indicate the Licensed Material is licensed under this Public License, and include the text of, or the URI or hyperlink to, this Public License.`
- Section 4(a): `for the avoidance of doubt, Section 2(a)(1) grants You the right to extract, reuse, reproduce, and Share all or a substantial portion of the contents of the database;`
- Section 2(b)(1): `Moral rights, such as the right of integrity, are not licensed under this Public License, nor are publicity, privacy, and/or other similar personality rights;`

| Requested use | Evidence-based result, conditional on election-data coverage |
| --- | --- |
| Redistribution through a public API | Express distribution permission + CC Share right; retain attribution/licence/change notices |
| Transformation CSV → JSON, field normalization, filtering, aggregation/derived metrics | CC adaptation and format rights permit it; identify modifications and separate derived values from official values |
| Local storage/snapshot | Reproduction right supports storage; acquisition restrictions still apply to how it is obtained |
| Checked-in data or fixtures in a public repository | Public sharing/reproduction rights support it, but repository use is not named explicitly by ŠÚ SR; ask confirmation and keep data notices distinct from the code licence |
| Commercial use, including downstream recipients | Expressly permitted in general ŠÚ SR policy; CC BY is not NC |
| Attribution | Identify `Štatistický úrad Slovenskej republiky`, original dataset/source URL, CC BY 4.0 link, modifications; retain supplied copyright/licence/disclaimer notices and reasonably practicable source links; no endorsement |

CC BY also prohibits additional downstream restrictions (2(a)(5)(B)); an adapter's licence must not prevent compliance (3(a)(4)). The project code licence does not erase upstream data obligations. Candidate/person-level privacy clearance is **not** supplied by a copyright licence; prefer aggregate-only scope pending separate assessment.

Proposed attribution after confirmation (not publisher-approved wording):

> Zdroj: Štatistický úrad Slovenskej republiky — Voľby do Národnej rady Slovenskej republiky 2023, definitívne výsledky (https://volby.statistics.sk/nrsr/nrsr2023/sk/subory_na_stiahnutie.html). Údaje: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). OpenSK API: konverzia CSV do JSON, normalizácia názvov polí a výber agregovaných tabuliek; odvodené ukazovatele sú označené osobitne. Projekt nie je podporovaný ani schválený Štatistickým úradom SR.

Also retain terms URL, acquisition/verification date, file/table IDs, measured hashes and publication timestamp in eventual snapshot metadata. This is an implementation recommendation, not a claimed upstream mandatory hash requirement.

## 5. Verified contacts and unresolved questions

Official election contact URL: https://volby.statistics.sk/nrsr/nrsr2023/sk/kontakty.html (directly inspected 2026-10-11, **high** confidence).

Exact contact labels:

> Informačný servis
>
> e-mail: info@statistics.sk
>
> Obsahový správca a technický prevádzkovateľ
>
> V prípade problémov s obsahom alebo prístupnosťou služby kontaktujte obsahového správcu a technického prevádzkovateľa.
>
> e-mail: volby@statistics.sk

Use **To: info@statistics.sk; CC: volby@statistics.sk**. Neither mailbox is claimed to be a designated licensing officer; ask routing if needed. The archive root independently publishes `info@statistics.sk` for questions/comments.

Unresolved:

1. Confirm CC BY 4.0 coverage of NRSR2023 CSV/ODS/XLSX on `volby.statistics.sk`, specifically aggregate result tables and election territorial/party lists, not third-party minutes/assets.
2. Confirm repository fixtures/snapshots, public JSON API, transformations/derived aggregates and downstream commercial use under those terms.
3. Clarify whether the robot/tool prohibition applies to one-off scripted downloads of explicitly offered files and future checks; obtain an approved manual/offline workflow or a documented permitted machine interface. No exception is assumed.
4. Confirm exact attribution, disclaimer/change/version notices and any table-specific third-party exceptions.
5. Inspect actual selected distributions for embedded notices, hashes, version consistency after an approved acquisition path is chosen. This agent has no such byte-level evidence.

Ready-to-send Slovak draft is appended to `docs/research/source-licence-outreach.md` under **NRSR2023 elections**; state `READY_FOR_USER_TO_SEND`, **unsent**. No raw dataset files were downloaded or placed in the repository by this agent. Any later raw downloads must stay in `C:\Users\matej\AppData\Local\Temp\opencode\elections`.
