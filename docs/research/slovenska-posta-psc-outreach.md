# Slovenská pošta — PSČ source-owner clarification package

**SENT_AWAITING_REPLY (2026-11-05) · PSC_RIGHTS_PENDING · NO_GO_SUCCESSOR_PSC**

PortalVS replied on **2026-11-02** that the underlying source of its PSC
classifier is **Slovenská pošta**. That identifies the source owner; it does
not grant reuse, transformation, public API redistribution or commercial
rights, and it does not resolve the documented street/administrative mapping
problems.

The agent did not send correspondence. The maintainer manually sent this
clarification request on **2026-11-05**; state is **`SENT_AWAITING_REPLY`** and
reply is pending. No institutional reply, licence or source-owner approval is
claimed. The repository retains no Message-ID, delivery confirmation or
receipt, and the prepared text below is not asserted to be a byte-for-byte copy
of the sent message.

## Verified official contact route

Checked live on **2026-11-05**:

- Official contact page: <https://www.posta.sk/podpora/kontakty>
- Official “Všeobecné otázky a požiadavky” mailbox:
  **zakaznickyservis@slposta.sk**
- Official PSC lookup/download page: <https://www.posta.sk/psc>
- Official downloadable postcode ZIP linked from that page:
  <https://www.posta.sk/files/6811e10125b182cd7cd9e3a9/postove-smerovacie-cisla-na-stiahnutie.zip>

The general institutional service mailbox is the appropriate initial routing
request; no individual employee's contact details are needed or published.
The page/mailbox verifies a contact route, not a licensing decision. The ZIP
remains a technical source candidate only.

## Subject

Dopyt k podmienkam opakovaného použitia a redistribúcie údajov PSČ v open-source API OpenSK

## Prepared Slovak message

```text
Dobrý deň,

pripravujem objasnenie podmienok pre open-source projekt OpenSK API, ktorý
poskytuje slovenské referenčné údaje cez jednotné JSON API. PortalVS nás
2. novembra 2026 odkázal pri otázke zdroja číselníka PSČ na Slovenskú poštu.

Ide o oficiálne údaje dostupné zo stránky https://www.posta.sk/psc, najmä
súbor „poštové smerovacie čísla na stiahnutie“ a prípadné súvisiace zoznamy
poštových obcí, miestnych častí a ulíc. Zamýšľaný rozsah je referenčná
geografia a validácia PSČ. OpenSK neposkytuje osobné adresy, záznamy o osobách,
údaje o zákazníkoch ani obsah zásielok. Bežné požiadavky API by používali len
lokálny materializovaný snapshot; neplánujeme scraping webových stránok ani
živé dotazovanie vašich služieb pri každej požiadavke.

Prosím o objasnenie týchto otázok:

1. Je dovolené lokálne uchovávať a používať oficiálne súbory PSČ, poštových
   obcí, miestnych častí a ulíc ako snapshot pre beh API? Vzťahuje sa prípadné
   povolenie aj na uchovanie historických snapshotov s dátumom získania a
   verziou zdroja?
2. Je dovolené previesť CSV/XLSX do normalizovaného JSON, premenovať polia,
   filtrovať záznamy a vytvárať explicitne označené odvodené väzby, ak
   pôvodný zdroj a naše úpravy zreteľne uvedieme?
3. Je dovolené redistribuovať takto spracované referenčné údaje cez verejné
   open-source API a zverejniť dátový snapshot v open-source repozitári?
4. Môžu následní používatelia API a redistribuovaných údajov používať tieto
   údaje aj komerčne? Existujú obmedzenia, ktoré musíme odovzdať používateľom?
5. Aká licencia a presná atribučná formulácia sa na tieto údaje vzťahuje?
   Je potrebné zachovať konkrétne označenie verzie, dátumu platnosti alebo
   iné právne či zdrojové oznámenie?
6. Aký spôsob získavania je povolený pre lokálny snapshot a jeho občasnú
   aktualizáciu? Je dostatočné manuálne stiahnutie uvedeného oficiálneho ZIP,
   alebo existuje povolené strojové rozhranie/export s podmienkami, ktoré
   môžeme použiť bez scrapingu?
7. Poskytuje Slovenská pošta autoritatívny strojovo spracovateľný vzťah
   PSČ → obec/mestská časť → okres/kraj, prípadne stabilné identifikátory
   a dátumy platnosti jednotlivých väzieb? Ak je viac administratívnych alebo
   poštových významov jedného PSČ, aká je ich správna sémantika?
8. Podliehajú niektoré polia obce, mestskej/miestnej časti, ulice alebo adresy
   osobitným obmedzeniam, právam tretích strán alebo zákazu ďalšej distribúcie?
   Môžeme spracovávať len referenčnú úroveň bez čísel adries a bez akýchkoľvek
   osobných údajov?
9. Ak tento dopyt patrí inému pracovisku alebo oprávnenému správcovi údajov,
   prosím o jeho postúpenie alebo kontakt na príslušné pracovisko.

Odpoveď použijem výhradne na dokumentovanie skutočného rozsahu povolení.
Bez jednoznačnej odpovede nebudem predpokladať povolenie redistribúcie,
transformácie ani komerčného použitia. Pri prípadnom zverejnení odôvodnenia
nedám do verejného repozitára osobné kontaktné údaje ani hlavičky e-mailu.

Ďakujem za objasnenie.

S pozdravom
[Meno]
[URL repozitára OpenSK API]
```

## Evidence boundary and next action

Questions 1–6 and 8 address rights/acquisition/notices; question 7 addresses
machine-readable administrative semantics; question 8 also checks whether
address-related fields require special treatment. Historical-snapshot retention
is explicitly included in question 1. No permission is inferred from preparing
or sending this request.

Until actual new evidence arrives:

- `data/psc.json` stays unchanged and partial;
- the successor 13,700-row PSC dataset is not promoted;
- `PSC_RIGHTS_PENDING`, `NO_GO_SUCCESSOR_PSC`, `MAPPING_PARTIAL`,
  `CONTRACT_CLARIFICATION_REQUIRED`, `NO_SOURCE_READY`, unresolved street/admin
  mappings and truthful occurrence semantics remain in force;
- no PSC source licence upgrade or runtime/upstream acquisition is made.

The maintainer's manual dispatch on 2026-11-05 changes outreach workflow only;
reply is pending. Only substantive new evidence should trigger a fresh evidence
review; do not automatically queue another PSC migration or evidence loop.
