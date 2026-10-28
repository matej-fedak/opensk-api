# Source Licence Outreach Package

These are prepared outreach packages for the human maintainer to send. Do not send emails automatically. This document pairs each open licence question with a verified contact, the retained evidence discovered during the 0.23.0 research review, and a ready-to-send Slovak message where a message is still required.

**Dispatch/reply status, updated 2026-10-28:** the human maintainer sent all four packages manually on **2026-10-11**. NBS's bank-directory reply was received **2026-10-14** and resolves bank reuse under its Terms of Use. The maintainer sent manual follow-ups on the three unanswered packages on **2026-10-28**; no reply has been received since. Current states:

| Package | State |
| --- | --- |
| PortalVS (§1) | `FOLLOW_UP_SENT_AWAITING_REPLY` (2026-10-28) |
| NBS banks (§2) | `REPLY_RECEIVED_RESOLVED` |
| Telecom regulator (§4) | `FOLLOW_UP_SENT_AWAITING_REPLY` (2026-10-28) |
| ŠÚ SR elections (§7) | `FOLLOW_UP_SENT_AWAITING_REPLY` (2026-10-28) |

No permission is inferred for the three unanswered items; a sent follow-up is not an approval either. No Message-ID, mail headers, delivery confirmation or exact sent/received body is independently archived in this repository. The drafts are historical prepared texts, not asserted byte-for-byte sent copies. The NBS substantive clarification is recorded below and in `nbs-bank-reuse-clarification.md`, without unnecessary email metadata.

Related documents:

- `docs/research/source-licence-questions.md` holds the original draft question lists.
- `docs/research/source-verification-evidence.md` holds retained source evidence.
- `docs/source-compliance.md` holds the per-dataset compliance matrix.

## 1. PortalVS Classifiers 9, 10, and 42 — FOLLOW_UP_SENT_AWAITING_REPLY (highest priority)

State: `FOLLOW_UP_SENT_AWAITING_REPLY` — human maintainer states the message was sent manually on 2026-10-11 (To `helpdesk@portalvs.sk`, CC `portalvs@portalvs.sk`) and a follow-up was sent manually on 2026-10-28. No reply received as of 2026-10-28; no permission is inferred from sending. The draft below is the prepared text, not a retained copy of the sent message.

Datasets affected: districts, municipalities, PSC. These three datasets are `INCLUDE_AFTER_COMPLIANCE_FIX` for the candidate 1.0 scope, so this outreach is the single highest-value compliance action in the project.

### Verified 2026-10-07 findings (direct verification)

1. A site banner on `ciselniky.portalvs.sk` states: "Spustili sme novú verziu číselníkov! Podpora doterajšieho systému končí 31.10.2026." The earlier scepticism about whether a hard end-of-support date existed is resolved: the deadline is real and shown on the official portal.
2. The replacement system is `ciselniky2.portalvs.sk` ("IS Číselníky"), operated by MŠVVaM SR. It exposes a REST API returning JSON/XML/CSV. The equivalent classifiers are named `slovenske-obce` (municipalities), `slovenske-okresy` (districts), and `psc-sk` (postal codes).
3. The portal copyright page states that content is reserved and available "iba k nekomerčnému použitiu" (non-commercial use only). This is the critical finding: if the non-commercial restriction applies to the classifier exports OpenSK redistributes, then downstream commercial use of OpenSK data cannot be promised, and even OpenSK's own redistribution must be confirmed.
4. Official contacts: `helpdesk@portalvs.sk` (user support) and `portalvs@portalvs.sk` (data-exchange mailbox).
5. Operator of the classifier system: Ministerstvo školstva, výskumu, vývoja a mládeže SR (MŠVVaM).

### Open questions the message must cover

- Whether classifiers 9, 10, and 42 (and their `ciselniky2` equivalents) may be reused outside the PortalVS website.
- Whether redistribution of normalized classifier data through an open-source public API is allowed.
- Whether local caching of classifier snapshots for runtime use is allowed.
- Whether transformation (JSON conversion, field normalization, filtering, derived municipality -> district links) counts as permitted use.
- Whether downstream commercial use is permitted despite the non-commercial copyright wording.
- Exact required attribution wording.
- Whether the 31.10.2026 end-of-support date also affects data availability history (i.e., whether a final snapshot export is offered).
- Whether any required notices or version identifiers must be preserved.

### Draft message (Slovak), send to helpdesk@portalvs.sk, CC portalvs@portalvs.sk

Subject: Dopyt k licenčným podmienkam číselníkov 9, 10 a 42 (Obce, Okresy, PSČ) pre opakované použitie v open-source API

```
Dobrý deň,

v rámci verejne dostupného, nekomerčného open-source projektu OpenSK API
(vyplňte URL repozitára), ktorý poskytuje slovenské
referenčné údaje cez jednotné JSON API, by som Vás chcel požiadať o
objasnenie licenčných podmienok právne súvisiacich s číselníkmi dostupnými
na portáli ciselniky.portalvs.sk a v novom systéme ciselniky2.portalvs.sk.

Konkrétne ide o:
- číselník 9 "Obce" (resp. "slovenske-obce" v IS Číselníky),
- číselník 10 "Okres" (resp. "slovenske-okresy"),
- číselník 42 "PSČ obcí SR a ČR" (resp. "psc-sk").

Prosím o zodpovedanie nasledujúcich otázok:

1. Je dovolené opakované použitie údajov z týchto číselníkov mimo portálu
   PortalVS, napríklad v open-source projekte?
2. Je dovolené redistribuovať normalizované údaje z týchto číselníkov cez
   verejné API (verejne prístupný HTTPS endpoint)?
3. Je dovolené lokálne ukladať (cache/snapshot) údaje z číselníkov pre
   beh API bez živých dotazov na PortalVS?
4. Je transformácia údajov (konverzia do JSON, normalizácia názvov polí,
   odvodenie väzieb obec -> okres) povolená?
5. Stránka autorských práv portálu uvádza použitie "iba k nekomerčnému
   použitiu". Vzťahuje sa toto obmedzenie aj na strojovo čitateľné výstupy
   číselníkov, alebo sú číselníky určené na opakované použitie bez
   komerčného obmedzenia? Môžu následní používatelia redistribuovaných údajov
   (vrátane komerčných používateľov) údaje ďalej používať?
6. Aká presná atribučná formulácia (uvedenie zdroja) sa vyžaduje?
7. Ovplyvňuje ukončenie podpory doterajšieho systému k 31.10.2026 dostupnosť
   historických údajov? Bude poskytnutý finálny export dát z pôvodného systému?
8. Existujú povinné označenia verzie číselníka alebo iné náležitosti, ktoré
   musí redistribútor zachovať?

Vopred ďakujem za odpoveď. Odpoveď použijem na aktualizáciu dokumentácie
licenčného stavu v repozitári projektu.

S pozdravom
[Meno]
```

## 2. NBS Bank-Code Directory — REPLY_RECEIVED_RESOLVED

State: **`REPLY_RECEIVED_RESOLVED`** — sent manually 2026-10-11 (To `info@nbs.sk`); institutional clarification received by the maintainer **2026-10-14** from NBS, odbor komunikácie značky NBS a inštitucionálnych vzťahov. This is real reply evidence, not inferred permission. The original mail remains private; the draft below is historical.

Dataset affected: banks; reuse resolved, served snapshot still **v225 / 2026-05-18**. The reply identified upstream **v226 / 2026-10-08**; refresh is separate and not performed in PR #33.

### Verified 2026-10-07 findings

The NBS website disclaimer (retained wording from the official NBS legal/disclaimer page): "Information published on this website may be stored, reproduced, and further used provided that the source is acknowledged and that neither the content nor other properties of the respective electronic file are modified in any way."

### Resolved by the 2026-10-14 reply

- Local storage and public open-source API redistribution are permitted with NBS attribution.
- Value-preserving CSV → JSON conversion and field renaming are permitted; transformed JSON is **not the original NBS file**. Link the source and disclose the source-column mapping.
- OpenSK-derived fields are permitted if separately labelled, not presented as NBS-supplied data. Audit: `activePartyMarker` normalizes **Payment system SIPS** and `activeParty` derives a boolean from it; neither reads NBS's **Akt. úč.** column. Detailed mapping and limitations: `nbs-bank-reuse-clarification.md`.
- Commercial downstream use is allowed under the same conditions, including downstream attribution. NBS gives no completeness/content-integrity guarantee or associated damages liability; commercial users should verify correctness.
- **MIT covers code, not NBS data**. NBS data remains under <https://nbs.sk/disclaimer-sk/> plus the clarification, not a new CC licence.
- Recommended attribution preserves NBS, converter title, actual version/effective date, original-source URL, OpenSK JSON conversion and separation of derived fields. The exact recommended sentence is not mandatory wording.
- Future refresh should retain version/effective/download dates; v225's actual download date is not established here. NBS logo/flag/symbols require separate approval and are not used.
- Holidays remain a separate unresolved transformation/evidence question; this reply does not grant blanket holiday clearance.

### Historical questions in the dispatched package (answered above)

- Whether converting the CSV directory to JSON, normalizing field names, adding `activeParty`, and filtering inactive/non-SK rows counts as a modification under the NBS disclaimer.
- Whether redistribution of the normalized bank-code dataset through an open-source public API is allowed.
- Whether local caching of snapshots is allowed for runtime use.
- Exact required attribution wording.
- Whether downstream commercial use is allowed.
- Whether inactive rows may be redistributed with an explicit inactive marker.
- Whether any required version/effective-date notices must be preserved.

### Draft message (Slovak), send to info@nbs.sk

Subject: Dopyt k podmienkam ďalšieho použitia adresára identifikačných kódov domáceho platobného systému

```
Dobrý deň,

v rámci verejného open-source projektu OpenSK API, ktorý poskytuje slovenské
referenčné bankové kódy cez JSON API, by som Vás chcel požiadať o objasnenie
podmienok ďalšieho použitia adresára identifikačných kódov domáceho
platobného systému v SR, publikovaného na stránke Národnej banky Slovenska.

Právne upozornení webu NBS uvádza, že informácie možno uchovávať,
rozmnožovať a ďalej používať za predpokladu uvedenia zdroja a bez akéhokoľvek
upravenia obsahu príslušného elektronického súboru.

Prosím o zodpovedanie nasledujúcich otázok:

1. Predstavuje konverzia adresára z CSV do JSON formátu, normalizácia názvov
   polí a doplnenie ukazovateľa aktívneho účastníka "úpravu" v zmysle právneho
   upozornenia?
2. Je povolená redistribúcia takto normalizovaného datasetu cez verejné
   open-source API?
3. Je povolené lokálne uloženie snapshotu adresára pre potreby behu API?
4. Aká presná atribučná formulácia sa vyžaduje?
5. Je dovolené následné komerčné použitie koncovými používateľmi?
6. Je dovolené redistribuovať aj neaktívne riadky explicitne označené ako
   neaktívne?
7. Existujú povinné verziové označenia alebo oznamy o dátume účinnosti, ktoré
   musia byť zachované?

Vopred ďakujem za odpoveď, ktorú použijem na doplnenie licenčnej dokumentácie
projektu.

S pozdravom
[Meno]
```

## 3. NBS Holidays — EMAIL LIKELY NOT NECESSARY, EVIDENCE RETENTION REQUIRED

State: `DIRECT_CONTACT_MAY_NOT_BE_NECESSARY`.

Dataset affected: holidays (partial/curated seed; candidate 1.0 Yellow).

Reasoning, recorded conservatively:

- Holiday dates are facts, not a creative dataset; the NBS disclaimer explicitly permits storage, reproduction, and further use with attribution and without modification of the reproduced file.
- The OpenSK holiday JSON is a curated list of dates cross-checked against Act 241/1993 Z. z.; it does not reproduce an NBS file verbatim.

Required action even without an email:

- Retain the exact NBS disclaimer wording and source URL in `docs/research/source-verification-evidence.md` (exact quote above in section 2 is the same disclaimer).
- Retain the Act 241/1993 Z. z. reference (© Slov-Lex legal text; see section 5 for the legal-text copyright position).
- Keep attribution "National Bank of Slovakia holidays page and Act 241/1993 Z. z." in docs and dataset metadata.

The 2026-10-14 bank-directory reply (section 2) does not expressly cover curated holidays. Keep the holidays evidence/interpretation work separate.

## 4. Telecom Regulator Phone-Area Workbook — FOLLOW_UP_SENT_AWAITING_REPLY

State: `FOLLOW_UP_SENT_AWAITING_REPLY` — human maintainer states the message was sent manually on 2026-10-11 (To `marian.jurkovic@teleoff.gov.sk`, CC `legal@teleoff.gov.sk`) and a follow-up was sent manually on 2026-10-28. No reply received as of 2026-10-28; no permission is inferred from sending. The draft below is the prepared text, not a retained copy of the sent message.

Dataset affected: phone areas (complete imported; candidate 1.0 Yellow; 3 unmatched source municipality rows remain).

### Verified 2026-10-07 findings

- The retained machine-processable workbook (`30.xls`, `List1` sheet) states that the data are "údaje určené na ďalšie spracovanie zo strany prijímateľa" (data intended for further processing by the recipient). This is a positive reuse signal for processing, but it does not explicitly address public redistribution or commercial downstream use.
- Verifiable contacts: data owner `marian.jurkovic@teleoff.gov.sk` (workbook publisher, Ing. Marián Jurkovič); legal questions `legal@teleoff.gov.sk`.

### Open questions the message must cover

- Whether the "ďalšie spracovanie" statement includes redistribution of normalized municipality-to-primary-area mappings through an open-source public API.
- Whether local caching of workbook snapshots is allowed for runtime use.
- Whether downstream commercial use is allowed.
- Exact required attribution wording.
- Whether version/update-date notices must be preserved.
- Whether partial or derived mappings (for example local municipality-code joins) are permitted.

### Draft message (Slovak), send to marian.jurkovic@teleoff.gov.sk, CC legal@teleoff.gov.sk

Subject: Dopyt k podmienkam ďalšieho použitia a redistribúcie údajov o mapovaní obcí na primárne telefónne obvody

```
Dobrý deň,

v rámci verejného open-source projektu OpenSK API redistribuujem cez JSON API
mapovanie slovenských obcí na primárne telefónne obvody, vytvorené z Vami
publikovaného strojovo spracovateľného súboru (30.xls, hárok List1).

Súbor uvádza, že ide o "údaje určené na ďalšie spracovanie zo strany
prijímateľa". Prosím o objasnenie rozsahu tohto povolenia:

1. Zahŕňa "ďalšie spracovanie" aj redistribúciu normalizovaných údajov cez
   verejné open-source API?
2. Je dovolené lokálne uloženie snapshotu súboru pre potreby behu API bez
   živých dotazov na stránky úradu?
3. Je dovolené následné komerčné použitie údajov koncovými používateľmi API?
4. Aká presná atribučná formulácia sa vyžaduje?
5. Existujú povinné oznamy o verzii alebo dátume aktualizácie, ktoré musia
   byť pri redistribúcii zachované?
6. Sú dovolené odvodené väzby (napr. priradenie lokálnych kódov obcí, okresov
   a krajov k riadkom mapovania)?

Vopred ďakujem za odpoveď, ktorú použijem na doplnenie licenčnej dokumentácie
projektu.

S pozdravom
[Meno]
```

## 5. Slov-Lex Legal Text (Vehicle Registration District Codes) — CONTACT LIKELY NOT NECESSARY

State: `DIRECT_CONTACT_MAY_NOT_BE_NECESSARY`.

Dataset affected: vehicle registration codes (historical/reference; candidate 1.0 Yellow).

### Verified 2026-10-07 findings

The current Slovak Copyright Act is zákon č. 185/2015 Z. z. (Autorský zákon). Section 5 contains lettered (not numbered) exclusions. Section 5 písm. b) excludes copyright protection for, among other things:

- "text právneho predpisu, úradné rozhodnutie alebo súdne rozhodnutie, technická norma, ako aj spolu s nimi vytvorená prípravná dokumentácia a ich preklad, bez ohľadu na to, či spĺňajú podmienky podľa § 3 ods. 1"

Vyhláška MV SR č. 9/2009 Z. z. (§ 36 ods. 2), the source of the historical vehicle registration district abbreviations, is a legal text within this exclusion. Conservatively recorded: direct contact is likely not necessary for a small factual reference table extracted from the legal text, but attribution to Slov-Lex and the regulation should be retained and, if doubt remains, the fallback contact is `helpdesk@slov-lex.sk`.

### Retention requirements even without an email

- Attribute Slov-Lex and Vyhláška MV SR č. 9/2009 Z. z. in docs and dataset metadata.
- Retain the exact § 5 písm. b) wording and statute number in `docs/research/source-verification-evidence.md`.
- Keep the conservative wording in docs: the dataset is historical/reference only and must not be presented as current plate lookup.

## 6. Sources Verified During 0.23.0 As Already Adequately Licensed (no outreach)

These are recorded so the compliance matrix can move from "terms page identified" to "retained evidence on file":

- Eurostat LAU/NUTS correspondence tables: Eurostat reuse policy confirms Creative Commons Attribution 4.0 (CC BY 4.0). Exact retained wording belongs in the evidence doc; attribution to Eurostat retained in docs and metadata. Regions therefore remain Yellow until the evidence entry is written, not because the licence is unknown.
- TED / Publications Office of the EU: TED reuse terms confirm that TED data "can be freely reused, for commercial or non-commercial purposes" and TED metadata are published as CC0, subject to the TED legal notice and source attribution. Exact wording retention is the remaining step for the procurement Yellow row.
- MŠVVaM school facility aggregate CSV: source page lists "Creative Commons BY" without a version number. This is a minor ambiguity only; attribution to MŠVVaM SR is retained. Optional: resolve the exact CC BY version from the dataset's DCAT metadata before a follow-up email; do not block on it.

## Dispatch Checklist

1. ~~Send section 1 (PortalVS) first~~ — done 2026-10-11 (`SENT_AWAITING_REPLY`); the reply still blocks the Red compliance rows and the candidate 1.0 inclusion of districts, municipalities, and PSC.
2. ~~Send section 2 (NBS banks) and section 4 (telecom)~~ — done 2026-10-11. NBS banks are `REPLY_RECEIVED_RESOLVED` on 2026-10-14; telecom and ŠÚ SR elections received manual follow-ups on 2026-10-28 and remain `FOLLOW_UP_SENT_AWAITING_REPLY`.
3. After each reply, update `docs/source-compliance.md`, `docs/research/source-verification-evidence.md`, and `data/sources.json` in the same commit so they stay aligned.
4. Retain the exact sent message text and received replies under `docs/research/` (redact personal email addresses before committing, if desired). The exact sent bodies are currently retained privately by the maintainer, not in this repository.
5. If no reply arrives within a reasonable interval, record a follow-up date in `docs/verification-backlog.md` rather than letting the item go stale.

## What Not To Do

- Do not send any of these messages automatically from CI, scripts, or agent tooling.
- Do not remove `Source/licence verification pending.` warnings before a reply or retained evidence exists.
- Do not present the 31.10.2026 PortalVS deadline as an emergency removal trigger; the correct response is outreach plus a mirrored-snapshot contingency (see `docs/research/roadmap-council-notes.md`, contested item on removal order).
- Do not claim official endorsement from any of these institutions.

## 7. NRSR2023 Elections — COVERAGE AND ACQUISITION CLARIFICATION REQUIRED

State: `FOLLOW_UP_SENT_AWAITING_REPLY` — human maintainer states the message was sent manually on 2026-10-11 (To `info@statistics.sk`, CC `volby@statistics.sk`) and a follow-up was sent manually on 2026-10-28. No reply received as of 2026-10-28; no permission is inferred from sending, and a sent request is not an approval. The draft below is the prepared text, not a retained copy of the sent message.

Verified **2026-10-11**: `https://volby.statistics.sk/nrsr/nrsr2023/sk/kontakty.html` lists `info@statistics.sk` as Informačný servis and `volby@statistics.sk` as Obsahový správca a technický prevádzkovateľ. These are verified public contacts, not an inferred licensing-officer address.

To: `info@statistics.sk`; CC: `volby@statistics.sk`.

Evidence: `docs/research/elections-source-licence.md`. General ŠÚ SR terms expressly permit distribution/commercial use and name CC BY 4.0, but also expressly prohibit robots/crawlers/similar data-gathering/download tools. Election-subdomain coverage and an approved acquisition route need clarification; offered downloads alone are not permission.

Evidence retention: the maintainer retains the sent message and any dated reply privately, including the responding institution, named files, licence scope, acquisition permission and attribution conditions. Add exact relevant wording and its date to `source-verification-evidence.md`; redact personal contact details before publishing. Human-dispatched 2026-10-11 per the dispatch-status note at the top of this document; a draft is not permission and a sent request is not an approval.

Subject: NRSR2023 — potvrdenie CC BY 4.0 a povoleného spôsobu získania a opakovaného použitia agregovaných výsledkov

```text
Dobrý deň,

pripravujem výskumný prototyp verejného open-source projektu OpenSK API
(vyplňte URL repozitára), ktorý má sprístupňovať slovenské verejné údaje
cez jednotné JSON API. Volebné údaje zatiaľ do produkčného API nezaraďujeme.

Chcel by som si overiť podmienky pre definitívne výsledky volieb do NR SR
2023 z oficiálneho zdroja:
https://volby.statistics.sk/nrsr/nrsr2023/sk/subory_na_stiahnutie.html

Zamýšľaný rozsah je obmedzený na agregované výsledky (účasť, počty a podiely
hlasov pre politické subjekty a mandáty), zoznam politických subjektov
a volebné územné členenie. Neplánujeme preberať zápisnice volebných komisií,
podpisy, grafické prvky ani osobné profily kandidátov či údaje o voličoch.

Všeobecné podmienky ŠÚ SR na stránke
https://slovak.statistics.sk/wps/portal/ext/aboutus/webpage/terms/
uvádzajú povolenie šírenia a komerčného využívania informácií a licenciu
Creative Commons Attribution License (cc-by) 4.0. Súčasne výslovne zakazujú
používanie robotov, pavúkov a podobných nástrojov na zhromažďovanie
a sťahovanie dát. Preto si nechcem domýšľať rozsah povolení ani výnimky.

Prosím o potvrdenie:

1. Vzťahuje sa CC BY 4.0 aj na uvedené CSV/ODS/XLSX tabuľky NRSR2023
   zverejnené na subdoméne volby.statistics.sk, vrátane zoznamu politických
   subjektov a volebného územného členenia? Existujú výnimky pre konkrétne
   tabuľky alebo práva tretích strán?
2. Je podľa týchto podmienok dovolené lokálne uložiť snapshot, previesť CSV
   do JSON, normalizovať názvy polí, filtrovať tabuľky a odvodiť agregované
   ukazovatele, pričom úpravy a odvodené hodnoty budú zreteľne označené?
3. Je dovolené takto spracované údaje redistribuovať cez verejné API
   a zverejniť dátový snapshot alebo malú dátovú testovaciu vzorku vo
   verejnom open-source repozitári s oddeleným označením dátovej licencie?
   Zahŕňa povolenie aj následné komerčné použitie používateľmi API?
4. Vzťahuje sa zákaz robotov a podobných nástrojov aj na jednorazové
   skriptované stiahnutie výslovne ponúkaných CSV/ZIP súborov a prípadnú
   kontrolu ich aktualizácií? Ak áno, prosím o odporučenie povoleného postupu
   (napr. manuálne stiahnutie a následné offline spracovanie) alebo
   oficiálneho strojového rozhrania a jeho prevádzkových podmienok.
5. Akú presnú atribúciu a odkazy, označenie úprav, dátumu/verzie a prípadné
   upozornenia na zodpovednosť máme zachovať v API, dokumentácii a repozitári?

Navrhujeme uvádzať zdroj „Štatistický úrad Slovenskej republiky — Voľby do
Národnej rady Slovenskej republiky 2023, definitívne výsledky“, odkaz na
originálnu stránku a CC BY 4.0, opis našich úprav a výslovné upozornenie,
že projekt nie je podporovaný ani schválený Štatistickým úradom SR.

Ak tento dopyt patrí inému útvaru, prosím o jeho postúpenie alebo kontakt
na príslušné pracovisko. Odpoveď použijeme ako podklad pre dokumentáciu
licenčného stavu projektu; pred prípadným zverejnením odpovede odstránime
osobné kontaktné údaje.

Ďakujem za objasnenie.

S pozdravom
[Meno]
```
