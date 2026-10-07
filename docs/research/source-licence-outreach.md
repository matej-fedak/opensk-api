# Source Licence Outreach Package

These are prepared outreach packages for the human maintainer to send. Do not send emails automatically. This document pairs each open licence question with a verified contact, the retained evidence discovered during the 0.23.0 research review, and a ready-to-send Slovak message where a message is still required.

Related documents:

- `docs/research/source-licence-questions.md` holds the original draft question lists.
- `docs/research/source-verification-evidence.md` holds retained source evidence.
- `docs/source-compliance.md` holds the per-dataset compliance matrix.

## 1. PortalVS Classifiers 9, 10, and 42 — SEND REQUIRED (highest priority)

State: `READY_FOR_USER_TO_SEND`.

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

## 2. NBS Bank-Code Directory — SEND REQUIRED

State: `READY_FOR_USER_TO_SEND`.

Dataset affected: banks (complete imported; candidate 1.0 Yellow).

### Verified 2026-10-07 findings

The NBS website disclaimer (retained wording from the official NBS legal/disclaimer page): "Information published on this website may be stored, reproduced, and further used provided that the source is acknowledged and that neither the content nor other properties of the respective electronic file are modified in any way."

Interpretation split, recorded conservatively:

- The disclaimer permits storage, reproduction, and further use with attribution.
- The disclaimer prohibits modification of the content or other properties of the respective file.
- OpenSK converts the NBS CSV to JSON, normalizes field names, and derives `activeParty`. It is unresolved upstream whether that normalization counts as "modification" within the meaning of the disclaimer. Contact: `info@nbs.sk`.

### Open questions the message must cover

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

If the NBS bank-directory reply (section 2) reveals stricter terms than expected, re-evaluate holidays contact at that time.

## 4. Telecom Regulator Phone-Area Workbook — SEND REQUIRED

State: `READY_FOR_USER_TO_SEND`.

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

1. Send section 1 (PortalVS) first; it blocks the Red compliance rows and the candidate 1.0 inclusion of districts, municipalities, and PSC.
2. Send section 2 (NBS banks) and section 4 (telecom) in the same week; replies determine whether their Yellow rows can advance.
3. After each reply, update `docs/source-compliance.md`, `docs/research/source-verification-evidence.md`, and `data/sources.json` in the same commit so they stay aligned.
4. Retain the exact sent message text and received replies under `docs/research/` (redact personal email addresses before committing, if desired).
5. If no reply arrives within a reasonable interval, record a follow-up date in `docs/verification-backlog.md` rather than letting the item go stale.

## What Not To Do

- Do not send any of these messages automatically from CI, scripts, or agent tooling.
- Do not remove `Source/licence verification pending.` warnings before a reply or retained evidence exists.
- Do not present the 31.10.2026 PortalVS deadline as an emergency removal trigger; the correct response is outreach plus a mirrored-snapshot contingency (see `docs/research/roadmap-council-notes.md`, contested item on removal order).
- Do not claim official endorsement from any of these institutions.
