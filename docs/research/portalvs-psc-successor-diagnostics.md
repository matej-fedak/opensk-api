# PortalVS PSC successor — curated research diagnostics

RESEARCH ONLY. Snapshot **2026-10-15T19:08:55Z**. No mapping or collapse is approved.
See [decision and evidence](portalvs-psc-successor-semantics.md). This intentionally
small derivative is not a source dump and contains no streets, house ranges or
workbook author metadata. Full field-level candidate evidence is emitted by the
offline analyzer to a private/ignored JSON report.

## A. All 82 unresolved locality/district pairs (84 rows)

Exact NFC/whitespace municipality candidates are **empty for every pair**.
`Normalized` lists case/whitespace/punctuation-normalized successor title candidates.
`Candidates` includes normalized titles and/or official postal evidence, **not approved joins**.
For each candidate the JSON report also supplies `officialTitle`, `mediumTitle`,
`shortTitle`, `note`, `includes`, `includesAlso`, `excludes`, `info`, `additionalInfo`.
The last five fields provide no established parent-locality mapping (§6 of decision).

Classes: TITLE = `ALTERNATE_OFFICIAL_NAME` (normalized published title only);
POST = `DELIVERY_LOCALITY` (paired publisher labels, not a formal official alias);
PART = `MUNICIPALITY_PART` (explicit publisher part relation);
AMB = `AMBIGUOUS`; UNK = `UNRESOLVED`.
Evidence `O<n>` = `OBCE.xlsx`, sheet `obce`, row n;
`M<n>` = sheet `miestne časti`, row n, from the ZIP identified in §2.
`none` means the bounded exact checks found no supporting relation, not that the locality is invalid.
District is source statistical code; region is the literal source context, not a guessed code.

| Source locality | District/region | Type | PSC(s) | Rows | Class | Normalized | Candidates | Evidence |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| Belá - Dulice | 506/ZI | obec | 03811 | 1 | TITLE | 512052 | 512052 Belá-Dulice | O76 |
| Bohdanovce n/Trnavou | 207/TA | obec | 91909 | 1 | POST | - | 506796 Bohdanovce nad Trnavou | O140 |
| Chminian. Jakubovany | 707/PV | obec | 08233 | 1 | POST | - | 524531 Chminianske Jakubovany | O822 |
| Chrašťany | 407/NI | obec | 95175 | 1 | UNK | - | - | none |
| Chrenovec - Brusno | 307/TC | obec | 97232 | 1 | TITLE | 514021 | 514021 Chrenovec-Brusno | O836 |
| Cinobaňa-Žihľava | 607/BC | obec | 98545 | 1 | UNK | - | - | none |
| Dolný Lieskov-Tŕstie | 306/TC | obec | 01822 | 1 | UNK | - | - | none |
| Družstevná pri Horn. | 806/KI | obec | 04431 | 1 | POST | - | 521345 Družstevná pri Hornáde | O490 |
| Dvorníky - Včeláre | 806/KI | obec | 04402 | 1 | TITLE | 559873 | 559873 Dvorníky-Včeláre | O537 |
| Galanta-Javorinka | 202/TA | obec | 92501 | 1 | UNK | - | - | none |
| Gbely - Cunín | 206/TA | obec | 90848 | 1 | UNK | - | - | none |
| Granč - Petrovce | 704/PV | obec | 05305 | 1 | TITLE | 526517 | 526517 Granč-Petrovce | O592 |
| Gregorovce | 608/BC | obec | 98252 | 1 | UNK | - | - | none |
| Hermanovce n/ Topľou | 713/PV | obec | 09434 | 1 | POST | - | 544221 Hermanovce nad Topľou | O641 |
| Horné Saliby - časť Hrušov | 202/TA | detail_sc | 92502 | 1 | UNK | - | - | none |
| Hrabovec n/ Laborcom | 702/PV | obec | 06701 | 1 | POST | - | 520225 Hrabovec nad Laborcom | O743 |
| Hriňová-Biele Vody | 604/BC | obec | 97653 | 1 | UNK | - | - | none |
| Hriňová-Vrchslatina | 604/BC | obec | 97653 | 1 | UNK | - | - | none |
| Hrnčiarovce n/Parnou | 207/TA | obec | 91935 | 1 | POST | - | 581020 Hrnčiarovce nad Parnou | O769 |
| Jastrabie pri Michal | 807/KI | obec | 07211 | 1 | POST | - | 522546 Jastrabie pri Michalovciach | O922 |
| Kaloša-Téška | 609/BC | obec | 98251 | 1 | UNK | - | - | none |
| Kamenec pod Vtáč. | 307/TC | obec | 97244 | 1 | POST | - | 514063 Kamenec pod Vtáčnikom | O964 |
| Kamenica n/Cirochou | 702/PV | obec | 06783 | 1 | POST | - | 520331 Kamenica nad Cirochou | O966 |
| Kokšov - Bakša | 806/KI | obec | 04413 | 1 | TITLE | 521558 | 521558 Kokšov-Bakša | O1038 |
| Kolónia | 811/KI | obec | 07642 | 1 | AMB | - | 528188 Boťany; 543896 Veľké Trakany | M104,M1592 |
| Kostolná - Záriečie | 309/TC | obec | 91304 | 1 | TITLE | 506133 | 506133 Kostolná-Záriečie | O1083 |
| Kostoľany n/Hornádom | 806/KI | obec | 04431 | 1 | POST | - | 582514 Kostoľany nad Hornádom | O1077 |
| Kostoľany p/Tribečom | 407/NI | obec | 95177 | 1 | POST | - | 500429 Kostoľany pod Tribečom | O1078 |
| Krivosúd - Bodovka | 309/TC | obec | 91311 | 1 | TITLE | 506168 | 506168 Krivosúd-Bodovka | O1180 |
| Križovany n/Dudváhom | 207/TA | obec | 91924 | 1 | POST | - | 556483 Križovany nad Dudváhom | O1184 |
| Krásnohor. Dlhá Lúka | 808/KI | obec | 04945 | 1 | POST | - | 525863 Krásnohorská Dlhá Lúka | O1161 |
| Krásnohor. Podhradie | 808/KI | obec | 04941 | 1 | POST | - | 525871 Krásnohorské Podhradie | O1162 |
| Kráľovce - Krnišov | 605/BC | obec | 96265 | 1 | TITLE | 518531 | 518531 Kráľovce-Krnišov | O1152 |
| Kysihýbel | 602/BC | obec | 96901 | 1 | UNK | - | - | none |
| Lešť (vojenský obvod)-Kamenný Vrch | 610/BC | obec | 99201 | 1 | UNK | - | - | none |
| Lešť (vojenský obvod)-Kamenný vrch | 611/BC | detail_sc | 99201 | 1 | UNK | - | - | none |
| Lovčica - Trubín | 613/BC | obec | 96623 | 1 | TITLE | 517038 | 517038 Lovčica-Trubín | O1362 |
| Matejovce n.Hornádom | 810/KI | obec | 05321 | 1 | POST | - | 543349 Matejovce nad Hornádom | O1497 |
| Medzibrodie n/Oravou | 503/ZI | obec | 02601 | 1 | POST | - | 509833 Medzibrodie nad Oravou | O1511 |
| Muľa-Hámor | 610/BC | obec | 99102 | 1 | UNK | - | - | none |
| Nedožery - Brezany | 307/TC | obec | 97212 | 1 | TITLE | 514209 | 514209 Nedožery-Brezany | O1615 |
| Nižné Valice | 609/BC | obec | 98252 | 1 | UNK | - | - | none |
| Okoč-Jánošíkovo na Ostrove | 201/TA | obec | 93010 | 1 | UNK | - | - | none |
| Orechová Potôň-Lúky | 201/TA | obec | 93052 | 1 | PART | - | 501859 Orechová Potôň | M1061 |
| Perín - Chym | 806/KI | obec | 04474 | 1 | TITLE | 521876 | 521876 Perín-Chym | O1837 |
| Petrovce n/Laborcom | 807/KI | obec | 07101 | 1 | POST | - | 522902 Petrovce nad Laborcom | O1848 |
| Plavé Vozokany-Medvecké | 402/NI | obec | 93541 | 1 | UNK | - | - | none |
| Plevník - Drienové | 306/TC | obec | 01826 | 1 | TITLE | 513474 | 513474 Plevník-Drienové | O1873 |
| Poruba p/Vihorlatom | 807/KI | obec | 07232 | 1 | POST | - | 522945 Poruba pod Vihorlatom | O1934 |
| Ruská Voľa n/Popr. | 710/PV | obec | 06542 | 1 | POST | - | 526991 Ruská Voľa nad Popradom | O2126 |
| Rychňava | 602/BC | obec | 96901 | 1 | UNK | - | - | none |
| Ráztočno-Remata | 307/TC | obec | 97251 | 1 | UNK | - | - | none |
| Sebedín - Bečov | 601/BC | obec | 97401 | 1 | TITLE | 508977 | 508977 Sebedín-Bečov | O2153 |
| Slatinka n/Bebravou | 301/TC | obec | 95653 | 1 | POST | - | 505480 Slatinka nad Bebravou | O2213 |
| Tovarnian.Polianka | 713/PV | obec | 09401 | 1 | POST | - | 529206 Tovarnianska Polianka | O2506 |
| Trenč.Bohuslavice | 304/TC | obec | 91307 | 1 | POST | - | 506583 Trenčianske Bohuslavice | O2522 |
| Trenč.Jastrabie | 309/TC | obec | 91322 | 1 | POST | - | 506591 Trenčianske Jastrabie | O2523 |
| Trenč.Stankovce | 309/TC | obec | 91311 | 1 | POST | - | 545741 Trenčianske Stankovce | O2525 |
| Turč.Štiavnička | 506/ZI | obec | 03851 | 1 | POST | - | 512702 Turčianska Štiavnička | O2560 |
| Turčok-Turčocký Železník | 608/BC | obec | 04964 | 1 | UNK | - | - | none |
| Vysoké Tatry-Dolný Smokovec | 706/PV | detail_sc | 05981 | 1 | UNK | - | - | none |
| Vysoké Tatry-Horný Smokovec | 706/PV | detail_sc | 06201 | 1 | UNK | - | - | none |
| Vysoké Tatry-Kežmarské Žľaby | 706/PV | detail_sc | 05960 | 1 | UNK | - | - | none |
| Vysoké Tatry-Nová Polianka | 706/PV | detail_sc | 05983 | 1 | UNK | - | - | none |
| Vysoké Tatry-Nový Smokovec | 706/PV | detail_sc | 06201 | 1 | UNK | - | - | none |
| Vysoké Tatry-Podbanské | 505/ZI | detail_sc | 03242 | 1 | UNK | - | - | none |
| Vysoké Tatry-Starý Smokovec | 706/PV | detail_sc | 06201 | 1 | UNK | - | - | none |
| Vysoké Tatry-Tatranská Kotlina | 706/PV | detail_sc | 05954,05955 | 2 | UNK | - | - | none |
| Vysoké Tatry-Tatranská Lesná | 706/PV | detail_sc | 05960 | 1 | UNK | - | - | none |
| Vysoké Tatry-Tatranská Lomnica | 706/PV | detail_sc | 05960,06201 | 2 | UNK | - | - | none |
| Vysoké Tatry-Tatranská Polianka | 706/PV | detail_sc | 06201 | 1 | UNK | - | - | none |
| Vysoké Tatry-Tatranské Matliare | 706/PV | detail_sc | 05960 | 1 | UNK | - | - | none |
| Vysoké Tatry-Tatranské Zruby | 706/PV | detail_sc | 06201 | 1 | UNK | - | - | none |
| Vysoké Tatry-Vyšné Hágy | 706/PV | detail_sc | 05984 | 1 | UNK | - | - | none |
| Vysoké Tatry-Štrbské Pleso | 706/PV | detail_sc | 05985 | 1 | UNK | - | - | none |
| Výčapy - Opatovce | 403/NI | obec | 95144 | 1 | TITLE | 500941 | 500941 Výčapy-Opatovce | O2786 |
| Vŕbovec | 807/KI | obec | 07101 | 1 | UNK | - | - | none |
| Záhorčie | 612/BC | obec | 96681 | 1 | UNK | - | - | none |
| Červenica pri Sabin. | 708/PV | obec | 08256 | 1 | POST | - | 524298 Červenica pri Sabinove | O337 |
| Ľudvikov dvor | 806/KI | obec | 04015 | 1 | UNK | - | - | none |
| Štiavnička | 601/BC | obec | 97681 | 1 | UNK | - | - | none |
| Žitná - Radiša | 301/TC | obec | 95641 | 1 | TITLE | 505811 | 505811 Žitná-Radiša | O2951 |

## B. All 122 ulica-only PSCs

All rows have **no source district code**. District counts below measure supplied
codes (zero), not inferred districts. Candidate administrative IDs use a unique
normalized published title within supplied region context (or nationally if
region absent). This is not a district-only or fuzzy join. JSON additionally
records candidate district IDs and literal source region contexts.

CAND = `SAFE_TO_COLLAPSE_CANDIDATE`, all rows point to one municipality;
MULTI = `MULTI_MUNICIPALITY`, at least two known municipalities (96001 also has
ambiguous rows); AMB = `AMBIGUOUS`; INSUF = `INSUFFICIENT_EVIDENCE`.
`Missing/ambiguous` counts rows without a candidate / with several candidates.
Only CAND rows and MULTI rows with `0/0` have complete candidate coverage.
None has production collapse approval. A shared delivery post is not an
administrative boundary. Bratislava/Košice are not canonical borough identities.

| PSC | Ulica rows | Locality count | Source districts | Delivery posts | Source localities | Unique candidate IDs | Missing/ambiguous | Class |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| 01003 | 114 | 1 | 0 | 1 | Žilina | 517402 | 0/0 | CAND |
| 01007 | 17 | 1 | 0 | 1 | Žilina | 517402 | 0/0 | CAND |
| 01008 | 61 | 1 | 0 | 1 | Žilina | 517402 | 0/0 | CAND |
| 01009 | 31 | 1 | 0 | 1 | Žilina | 517402 | 0/0 | CAND |
| 01014 | 27 | 1 | 0 | 1 | Žilina | 517402 | 0/0 | CAND |
| 01015 | 15 | 1 | 0 | 1 | Žilina | 517402 | 0/0 | CAND |
| 01704 | 3 | 1 | 0 | 1 | Považská Bystrica | 512842 | 0/0 | CAND |
| 01706 | 2 | 1 | 0 | 1 | Považská Bystrica | 512842 | 0/0 | CAND |
| 01707 | 7 | 1 | 0 | 1 | Považská Bystrica | 512842 | 0/0 | CAND |
| 02401 | 34 | 2 | 0 | 1 | Kysucké Nové Mesto; Žilina | 509256,517402 | 0/0 | MULTI |
| 02404 | 17 | 1 | 0 | 1 | Kysucké Nové Mesto | 509256 | 0/0 | CAND |
| 03403 | 29 | 1 | 0 | 1 | Ružomberok | 510998 | 0/0 | CAND |
| 03406 | 20 | 1 | 0 | 1 | Ružomberok | 510998 | 0/0 | CAND |
| 03601 | 226 | 2 | 0 | 1 | Martin; Vrútky | 512036,557358 | 0/0 | MULTI |
| 04001 | 403 | 1 | 0 | 1 | Košice | - | 403/0 | INSUF |
| 04011 | 162 | 1 | 0 | 1 | Košice | - | 162/0 | INSUF |
| 04012 | 41 | 1 | 0 | 1 | Košice | - | 41/0 | INSUF |
| 04013 | 33 | 1 | 0 | 1 | Košice | - | 33/0 | INSUF |
| 04014 | 17 | 1 | 0 | 1 | Košice | - | 17/0 | INSUF |
| 04017 | 68 | 1 | 0 | 1 | Košice | - | 68/0 | INSUF |
| 04022 | 38 | 1 | 0 | 1 | Košice | - | 38/0 | INSUF |
| 04023 | 25 | 1 | 0 | 1 | Košice | - | 25/0 | INSUF |
| 05205 | 10 | 1 | 0 | 1 | Spišská Nová Ves | 526355 | 0/0 | CAND |
| 05331 | 20 | 1 | 0 | 1 | Spišská Nová Ves | 526355 | 0/0 | CAND |
| 05938 | 28 | 1 | 0 | 1 | Štrba | 523933 | 0/0 | CAND |
| 05941 | 9 | 1 | 0 | 1 | Štrba | 523933 | 0/0 | CAND |
| 05951 | 20 | 1 | 0 | 1 | Poprad | 523381 | 0/0 | CAND |
| 08631 | 5 | 1 | 0 | 1 | Bardejov | 519006 | 0/0 | CAND |
| 81101 | 51 | 1 | 0 | 1 | Bratislava | - | 51/0 | INSUF |
| 81102 | 64 | 1 | 0 | 1 | Bratislava | - | 64/0 | INSUF |
| 81103 | 50 | 1 | 0 | 1 | Bratislava | - | 50/0 | INSUF |
| 81104 | 89 | 1 | 0 | 1 | Bratislava | - | 89/0 | INSUF |
| 81105 | 32 | 1 | 0 | 1 | Bratislava | - | 32/0 | INSUF |
| 81106 | 44 | 1 | 0 | 1 | Bratislava | - | 44/0 | INSUF |
| 81107 | 34 | 1 | 0 | 1 | Bratislava | - | 34/0 | INSUF |
| 81108 | 28 | 1 | 0 | 1 | Bratislava | - | 28/0 | INSUF |
| 81109 | 29 | 1 | 0 | 1 | Bratislava | - | 29/0 | INSUF |
| 82101 | 29 | 1 | 0 | 1 | Bratislava | - | 29/0 | INSUF |
| 82102 | 43 | 1 | 0 | 1 | Bratislava | - | 43/0 | INSUF |
| 82103 | 41 | 1 | 0 | 1 | Bratislava | - | 41/0 | INSUF |
| 82104 | 71 | 1 | 0 | 1 | Bratislava | - | 71/0 | INSUF |
| 82105 | 82 | 1 | 0 | 1 | Bratislava | - | 82/0 | INSUF |
| 82106 | 90 | 1 | 0 | 1 | Bratislava | - | 90/0 | INSUF |
| 82107 | 122 | 1 | 0 | 1 | Bratislava | - | 122/0 | INSUF |
| 82108 | 58 | 1 | 0 | 1 | Bratislava | - | 58/0 | INSUF |
| 82109 | 45 | 1 | 0 | 1 | Bratislava | - | 45/0 | INSUF |
| 83000 | 6 | 1 | 0 | 1 | Bratislava | - | 6/0 | INSUF |
| 83005 | 1 | 1 | 0 | 1 | Bratislava | - | 1/0 | INSUF |
| 83007 | 2 | 1 | 0 | 1 | Bratislava | - | 2/0 | INSUF |
| 83101 | 104 | 1 | 0 | 1 | Bratislava | - | 104/0 | INSUF |
| 83102 | 63 | 1 | 0 | 1 | Bratislava | - | 63/0 | INSUF |
| 83103 | 57 | 1 | 0 | 1 | Bratislava | - | 57/0 | INSUF |
| 83104 | 48 | 1 | 0 | 1 | Bratislava | - | 48/0 | INSUF |
| 83106 | 95 | 1 | 0 | 1 | Bratislava | - | 95/0 | INSUF |
| 83107 | 51 | 1 | 0 | 1 | Bratislava | - | 51/0 | INSUF |
| 83151 | 6 | 1 | 0 | 1 | Bratislava | - | 6/0 | INSUF |
| 83152 | 18 | 1 | 0 | 1 | Bratislava | - | 18/0 | INSUF |
| 83153 | 7 | 1 | 0 | 1 | Bratislava | - | 7/0 | INSUF |
| 83154 | 8 | 1 | 0 | 1 | Bratislava | - | 8/0 | INSUF |
| 84002 | 3 | 1 | 0 | 1 | Bratislava | - | 3/0 | INSUF |
| 84008 | 3 | 1 | 0 | 1 | Bratislava | - | 3/0 | INSUF |
| 84009 | 2 | 1 | 0 | 1 | Bratislava | - | 2/0 | INSUF |
| 84101 | 56 | 1 | 0 | 1 | Bratislava | - | 56/0 | INSUF |
| 84102 | 31 | 1 | 0 | 1 | Bratislava | - | 31/0 | INSUF |
| 84103 | 38 | 1 | 0 | 1 | Bratislava | - | 38/0 | INSUF |
| 84104 | 73 | 1 | 0 | 1 | Bratislava | - | 73/0 | INSUF |
| 84105 | 27 | 1 | 0 | 1 | Bratislava | - | 27/0 | INSUF |
| 84106 | 60 | 1 | 0 | 1 | Bratislava | - | 60/0 | INSUF |
| 84107 | 56 | 1 | 0 | 1 | Bratislava | - | 56/0 | INSUF |
| 84108 | 12 | 1 | 0 | 1 | Bratislava | - | 12/0 | INSUF |
| 84110 | 54 | 1 | 0 | 1 | Bratislava | - | 54/0 | INSUF |
| 85000 | 2 | 1 | 0 | 1 | Bratislava | - | 2/0 | INSUF |
| 85009 | 5 | 1 | 0 | 1 | Bratislava | - | 5/0 | INSUF |
| 85101 | 73 | 1 | 0 | 1 | Bratislava | - | 73/0 | INSUF |
| 85102 | 11 | 1 | 0 | 1 | Bratislava | - | 11/0 | INSUF |
| 85103 | 7 | 1 | 0 | 1 | Bratislava | - | 7/0 | INSUF |
| 85104 | 20 | 1 | 0 | 1 | Bratislava | - | 20/0 | INSUF |
| 85105 | 9 | 1 | 0 | 1 | Bratislava | - | 9/0 | INSUF |
| 85106 | 8 | 1 | 0 | 1 | Bratislava | - | 8/0 | INSUF |
| 85107 | 19 | 1 | 0 | 1 | Bratislava | - | 19/0 | INSUF |
| 85110 | 117 | 1 | 0 | 1 | Bratislava | - | 117/0 | INSUF |
| 90203 | 23 | 1 | 0 | 1 | Pezinok | 508179 | 0/0 | CAND |
| 91101 | 168 | 1 | 0 | 1 | Trenčín | 505820 | 0/0 | CAND |
| 91106 | 14 | 1 | 0 | 1 | Trenčín | 505820 | 0/0 | CAND |
| 91108 | 18 | 1 | 0 | 1 | Trenčín | 505820 | 0/0 | CAND |
| 91701 | 222 | 2 | 0 | 1 | Trnava; Zavar | 506745,507768 | 0/0 | MULTI |
| 91702 | 37 | 1 | 0 | 1 | Trnava | 506745 | 0/0 | CAND |
| 91705 | 24 | 1 | 0 | 1 | Trnava | 506745 | 0/0 | CAND |
| 91708 | 38 | 1 | 0 | 1 | Trnava | 506745 | 0/0 | CAND |
| 91926 | 20 | 1 | 0 | 1 | Zavar | 507768 | 0/0 | CAND |
| 92003 | 19 | 1 | 0 | 1 | Hlohovec | 507032 | 0/0 | CAND |
| 92701 | 92 | 1 | 0 | 1 | Šaľa | 504025 | 0/0 | CAND |
| 93405 | 39 | 1 | 0 | 1 | Levice | 502031 | 0/0 | CAND |
| 94360 | 10 | 1 | 0 | 1 | Nána | 556092 | 0/0 | CAND |
| 94504 | 29 | 1 | 0 | 1 | Komárno | 501026 | 0/0 | CAND |
| 94505 | 35 | 1 | 0 | 1 | Komárno | 501026 | 0/0 | CAND |
| 94655 | 26 | 1 | 0 | 1 | Pribeta | 501328 | 0/0 | CAND |
| 94703 | 22 | 1 | 0 | 1 | Hurbanovo | 501140 | 0/0 | CAND |
| 94901 | 489 | 3 | 0 | 1 | Lužianky; Nitra; Nitrianske Hrnčiarovce | 500011,556696,580899 | 0/0 | MULTI |
| 94905 | 42 | 1 | 0 | 1 | Nitra | 500011 | 0/0 | CAND |
| 94907 | 31 | 1 | 0 | 1 | Nitra | 500011 | 0/0 | CAND |
| 94911 | 59 | 1 | 0 | 1 | Nitra | 500011 | 0/0 | CAND |
| 95141 | 47 | 2 | 0 | 1 | Lužianky; Nitra | 500011,580899 | 0/0 | MULTI |
| 95197 | 18 | 1 | 0 | 1 | Žitavany | 582816 | 0/0 | CAND |
| 95503 | 6 | 1 | 0 | 1 | Topoľčany | 504998 | 0/0 | CAND |
| 95704 | 14 | 1 | 0 | 1 | Bánovce nad Bebravou | 542652 | 0/0 | CAND |
| 95801 | 65 | 1 | 0 | 1 | Partizánske | 505315 | 0/0 | CAND |
| 95804 | 32 | 1 | 0 | 1 | Partizánske | 505315 | 0/0 | CAND |
| 95806 | 5 | 1 | 0 | 1 | Partizánske | 505315 | 0/0 | CAND |
| 96001 | 184 | 3 | 0 | 1 | Dobrá Niva; Lieskovec; Zvolen | 518158,518298 | 0/2 | MULTI |
| 96202 | 16 | 1 | 0 | 1 | Vígľaš | 518921 | 0/0 | CAND |
| 96221 | 16 | 2 | 0 | 1 | Lieskovec; Zvolen | 518158 | 0/10 | AMB |
| 96223 | 31 | 1 | 0 | 1 | Očová | 518662 | 0/0 | CAND |
| 97404 | 34 | 1 | 0 | 1 | Banská Bystrica | 508438 | 0/0 | CAND |
| 97409 | 25 | 1 | 0 | 1 | Banská Bystrica | 508438 | 0/0 | CAND |
| 97411 | 48 | 1 | 0 | 1 | Banská Bystrica | 508438 | 0/0 | CAND |
| 97632 | 16 | 1 | 0 | 1 | Badín | 508454 | 0/0 | CAND |
| 97646 | 22 | 1 | 0 | 1 | Valaská | 509086 | 0/0 | CAND |
| 97663 | 9 | 1 | 0 | 1 | Predajná | 508934 | 0/0 | CAND |
| 97703 | 19 | 1 | 0 | 1 | Brezno | 508497 | 0/0 | CAND |
| 98403 | 29 | 1 | 0 | 1 | Lučenec | 511218 | 0/0 | CAND |
| 98505 | 41 | 1 | 0 | 1 | Kokava nad Rimavicou | 511498 | 0/0 | CAND |

## C. All 69 affected non-street PSCs

`Exact`/`Dropped` are source rows, not deduplicated administrative matches.
`Extra candidates` would add administrative coverage if verified; this is **not**
an approved matchCount calculation. No unique candidate is already covered by
an exact row in these affected PSCs. `Still unassigned` includes ambiguous rows.
For those rows additional coverage remains UNKNOWN, never assumed redundant.

| PSC | Exact rows | Dropped rows | PSC disappears | Extra candidate municipality IDs | Already covered candidate IDs | Still unassigned |
| --- | ---: | ---: | --- | --- | --- | ---: |
| 01822 | 4 | 1 | no | - | - | 1 |
| 01826 | 0 | 1 | yes | 513474 | - | 0 |
| 02601 | 10 | 1 | no | 509833 | - | 0 |
| 03242 | 2 | 1 | no | - | - | 1 |
| 03811 | 0 | 1 | yes | 512052 | - | 0 |
| 03851 | 0 | 1 | yes | 512702 | - | 0 |
| 04015 | 0 | 1 | yes | - | - | 1 |
| 04402 | 8 | 1 | no | 559873 | - | 0 |
| 04413 | 1 | 1 | no | 521558 | - | 0 |
| 04431 | 1 | 2 | no | 521345,582514 | - | 0 |
| 04474 | 0 | 1 | yes | 521876 | - | 0 |
| 04941 | 1 | 1 | no | 525871 | - | 0 |
| 04945 | 1 | 1 | no | 525863 | - | 0 |
| 04964 | 1 | 1 | no | - | - | 1 |
| 05305 | 6 | 1 | no | 526517 | - | 0 |
| 05321 | 2 | 1 | no | 543349 | - | 0 |
| 05954 | 0 | 1 | yes | - | - | 1 |
| 05955 | 1 | 1 | no | - | - | 1 |
| 05960 | 0 | 4 | yes | - | - | 4 |
| 05981 | 1 | 1 | no | - | - | 1 |
| 05983 | 0 | 1 | yes | - | - | 1 |
| 05984 | 0 | 1 | yes | - | - | 1 |
| 05985 | 0 | 1 | yes | - | - | 1 |
| 06201 | 0 | 6 | yes | - | - | 6 |
| 06542 | 2 | 1 | no | 526991 | - | 0 |
| 06701 | 5 | 1 | no | 520225 | - | 0 |
| 06783 | 2 | 1 | no | 520331 | - | 0 |
| 07101 | 4 | 2 | no | 522902 | - | 1 |
| 07211 | 2 | 1 | no | 522546 | - | 0 |
| 07232 | 2 | 1 | no | 522945 | - | 0 |
| 07642 | 2 | 1 | no | - | - | 1 |
| 08233 | 5 | 1 | no | 524531 | - | 0 |
| 08256 | 3 | 1 | no | 524298 | - | 0 |
| 09401 | 3 | 1 | no | 529206 | - | 0 |
| 09434 | 2 | 1 | no | 544221 | - | 0 |
| 90848 | 1 | 1 | no | - | - | 1 |
| 91304 | 1 | 1 | no | 506133 | - | 0 |
| 91307 | 4 | 1 | no | 506583 | - | 0 |
| 91311 | 2 | 2 | no | 506168,545741 | - | 0 |
| 91322 | 1 | 1 | no | 506591 | - | 0 |
| 91909 | 1 | 1 | no | 506796 | - | 0 |
| 91924 | 0 | 1 | yes | 556483 | - | 0 |
| 91935 | 0 | 1 | yes | 581020 | - | 0 |
| 92501 | 1 | 1 | no | - | - | 1 |
| 92502 | 1 | 1 | no | - | - | 1 |
| 93010 | 1 | 1 | no | - | - | 1 |
| 93052 | 3 | 1 | no | 501859 | - | 0 |
| 93541 | 2 | 1 | no | - | - | 1 |
| 95144 | 1 | 1 | no | 500941 | - | 0 |
| 95175 | 1 | 1 | no | - | - | 1 |
| 95177 | 1 | 1 | no | 500429 | - | 0 |
| 95641 | 4 | 1 | no | 505811 | - | 0 |
| 95653 | 5 | 1 | no | 505480 | - | 0 |
| 96265 | 5 | 1 | no | 518531 | - | 0 |
| 96623 | 0 | 1 | yes | 517038 | - | 0 |
| 96681 | 7 | 1 | no | - | - | 1 |
| 96901 | 8 | 2 | no | - | - | 2 |
| 97212 | 0 | 1 | yes | 514209 | - | 0 |
| 97232 | 1 | 1 | no | 514021 | - | 0 |
| 97244 | 0 | 1 | yes | 514063 | - | 0 |
| 97251 | 2 | 1 | no | - | - | 1 |
| 97401 | 7 | 1 | no | 508977 | - | 0 |
| 97653 | 4 | 2 | no | - | - | 2 |
| 97681 | 1 | 1 | no | - | - | 1 |
| 98251 | 4 | 1 | no | - | - | 1 |
| 98252 | 5 | 2 | no | - | - | 2 |
| 98545 | 2 | 1 | no | - | - | 1 |
| 99102 | 6 | 1 | no | - | - | 1 |
| 99201 | 1 | 2 | no | - | - | 2 |
