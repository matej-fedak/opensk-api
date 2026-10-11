# Elections data/schema spike: NRSR2023, NRSR2020 and REF2023

Verified **2026-10-11**, for the OpenSK 0.23.2 spike. This is acquisition/schema research, not a production dataset, endpoint, implementation, or licence clearance. Only this Markdown file is added to the repository. No candidate records, candidate preference-vote files, or bulk archives were downloaded.

**Decision status: licence/acquisition-evidence gated.** The technical feasibility findings below are not acquisition approval. After the downloads had completed, Agent A reported a newly verified explicit automated-collection restriction in ŠÚ SR's general terms. No new scripted download requests were made after that instruction; analysis and hash checks continued only on already retrieved local files. Existing raw evidence was retained, not discarded or re-labelled as authorized acquisition.

## Retrospective acquisition restriction

Agent A's supplied official terms URL: <https://slovak.statistics.sk/wps/portal/ext/aboutus/webpage/terms/>. Reported exact wording:

> používanie robotov, pavúkov (spiders, crawlers) a ďalších podobných nástrojov na zhromažďovanie a sťahovanie dát, je výslovne zakázané.

This document records the finding as supplied by Agent A; this agent did not make a further HTTP request to independently retrieve the terms after receiving the stop instruction. Applicability of those general terms to the election-specific downloadable files remains unresolved. Public links, successful HTTP responses, and source publication alone do not establish permission for scripted acquisition or redistribution.

Acquisition was performed with Python `urllib.request` before the restriction was communicated: the retained NRSR2023 manifest records responses completed **2026-10-11 19:31:45.955098–19:31:48.704778 UTC**; the retained historical/referendum sample manifest records final responses completed **19:33:27.340238–19:33:28.033326 UTC**. Earlier exploratory/retry requests also occurred before these retained final downloads, including a first completed drift-sample acquisition at approximately **19:32:27–19:32:28 UTC**. Encoding/delimiter analysis was corrected and those small drift samples were fetched again before the stop instruction; the final retained hashes remained unchanged. Discovery requests and failed guessed URLs also preceded the instruction. These timestamps document actual acquisition timing, not retrospective permission.

Historical sampling described below was already completed before the stop, so none of its reported tables is an unperformed download. No further historical sampling, terms retrieval, horizontal-party-table retrieval, or candidate/bulk acquisition was undertaken after the instruction. Final offline rehash of all 17 raw files at **19:37:43 UTC** matched both retained manifests. Further automated acquisition/refresh should remain blocked pending evidence that the election-download use is permitted (for example publisher clarification or election-specific terms/permission); reuse/redistribution clearance is a separate unresolved requirement.

## Findings for the importer lead

- NRSR2023 `tab0c` and `tab02d`: **2,927 rows each**, consisting of 2,926 domestic units and one foreign-vote pseudo-unit. They join exactly on the six-digit municipality code and agree on every territory field and precinct count.
- Join to `data/municipalities.json`: **2,926 matches**, one official-only `599999 / Cudzina`, one local-only `518638 / Valaškovce (vojenský obvod)`. Both lists happen to contain 2,927 units; equal counts do **not** mean identical coverage.
- NRSR2023 CSVs are strictly valid **UTF-8, no BOM, comma delimiter, LF newlines, double-quoted text, dot decimal**, one header record. No blank or duplicate column names. Do not assume CP1250 or semicolon CSV.
- `tab03e`: **44,272 rows**, 14 columns, **6,009,826 bytes**, manageable without giant candidate tables. It contains only positive party-vote rows, not a rectangular 2,927 × 25 grid. Every municipality is represented; all municipality and national party totals reconcile exactly.
- Official domestic district codes are three-digit election codes, not the repository's `SK…` identifiers. All **79 districts and 8 regions** have an unambiguous code crosswalk via municipality membership. Retain foreign voting separately, not as an invented Slovak municipality/region/district.
- Percentages consistently **truncate to two decimals**, not round half-up. Aggregate valid-vote percentages use **participating voters**, not envelopes, as the denominator.
- NRSR2020 and REF2023 sampled CSVs are **pipe-delimited**, technical uppercase headers, decimal **comma**, UTF-8/no BOM/LF, no quote bytes. Some numeric-only files are pure ASCII, so their bytes cannot distinguish ASCII-compatible encodings. Table names and semantics also drift; a single generic CSV dialect/schema is unsafe.

## Discovery and evidence boundaries

Official publisher/host: Štatistický úrad SR, `https://volby.statistics.sk/`.

Download catalogues actually inspected:

- <https://volby.statistics.sk/nrsr/nrsr2023/sk/subory_na_stiahnutie.html>
- <https://volby.statistics.sk/nrsr/nrsr2023/json/downloadSK.json>
- <https://volby.statistics.sk/nrsr/nrsr2020/sk/download.html>
- <https://volby.statistics.sk/nrsr/nrsr2020/json/downloadSK.json>
- <https://volby.statistics.sk/ref/ref2023/sk/subory_na_stiahnutie.html>
- <https://volby.statistics.sk/ref/ref2023/json/downloadSK.json>

The download tables are populated through JavaScript/JSON: an empty HTML table is not evidence of missing downloads. NRSR2023 uses catalogue keys `Code`, `Name`; NRSR2020 uses `a`, `val`. NRSR2023's guessed `sk/download.html`, and NRSR2020's guessed `sk/subory_na_stiahnutie.html`, return 404; use the observed links above.

NRSR2023 election date: **2023-09-30**. Its official index states definitive results were published **2023-10-01 14:30** and explicitly says Prešov precinct 34 was not included by decision of the State Commission. The downloaded HTTP Last-Modified timestamps differ from that page publication time; retain both rather than treating either as election date. REF2023 page publication time: **2023-01-22 08:50**; referendum date **2023-01-21**. NRSR2020 index gives election date **2020-02-29**.

## Raw-file provenance and exact local paths

**All official raw files exist only under** `C:\Users\matej\AppData\Local\Temp\opencode\elections\`. The local path of each file below is that directory plus the exact filename. All requests returned HTTP **200**, with final URL equal to requested URL. Sizes are the actual response-body bytes written, not rounded catalogue labels. SHA-256 is over these unchanged bytes.

Local machine-readable evidence, also outside the repository:

- `C:\Users\matej\AppData\Local\Temp\opencode\elections\manifest.json`: NRSR2023 URLs, retrieval UTC, HTTP type/Last-Modified, sizes, hashes, strict encoding tests, byte prefixes, line counts, widths and sample records.
- `C:\Users\matej\AppData\Local\Temp\opencode\elections\drift-manifest.json`: same metadata for drift samples, including extracted XLSX cell addresses/values.
- `C:\Users\matej\AppData\Local\Temp\opencode\elections\relationships.json`: full municipality name differences, district/region crosswalks and relationship measurements.
- Temporary analysis scripts: `election_probe.py`, `drift_probe.py`, `relationships.py` in the same directory. These are exploratory evidence tools, not repository/production code.

### NRSR2023 files

Every file in this subsection has HTTP Content-Type **`text/csv`**. Retrieval date is **2026-10-11 UTC**; times below are UTC. Every URL is provided literally, rather than inferred from a filename pattern.

| Filename | Bytes | Retrieved UTC | HTTP Last-Modified UTC | SHA-256 |
| --- | ---: | --- | --- | --- |
| `NRSR2023_SK_tab0c.csv` | 231229 | 19:31:46.425001 | 2023-10-01 07:30:22 | `479fe57712c4a1500e466ddd2bf7b967e1aeec69fceb34326a2683f29519fa1f` |
| `NRSR2023_SK_tab02d.csv` | 361393 | 19:31:46.500915 | 2023-10-01 07:30:18 | `cbabf05cf3d64bd92106670363c538fbaf0b9ea3a547339b917c022c1f484a5e` |
| `NRSR2023_SK_tab03e.csv` | 6009826 | 19:31:48.704778 | 2023-10-01 07:31:53 | `f560181346e002fbe287d5a34b5e20db09da85bfa9e93ea04026b1cce13ef887` |
| `NRSR2023_SK_tab01.csv` | 423 | 19:31:45.955098 | 2023-10-01 07:31:02 | `539bce1f2141b9bb789ad1ea627bfa9acc1ce40d9414e3f992b387abc0f4b0fd` |
| `NRSR2023_SK_tab02a.csv` | 1111 | 19:31:46.114191 | 2023-10-01 07:29:34 | `0bbd315e397aa76c4b1147cb361bf4024a6bb7f7a450984e150af1d494360b8d` |
| `NRSR2023_SK_tab02c.csv` | 9369 | 19:31:46.278236 | 2023-10-01 07:29:57 | `5e8685076c7885f6247c55674819d1c921d8e91b611d21703894601e0e74afa8` |
| `NRSR2023_SK_tab03a.csv` | 1953 | 19:31:46.436640 | 2023-10-01 07:31:52 | `53a48342f14008941fd06ad7cf70a3de332336b80971841afc01ce92bc03a289` |
| `NRSR2023_SK_tab0a.csv` | 1596 | 19:31:46.581948 | 2023-10-01 07:31:54 | `832f6bbcd6c85a01c77bcbdc4483762c5ae059491e5ad4ce5eccfc55efac9df1` |

```text
https://volby.statistics.sk/nrsr/nrsr2023/files/csv/NRSR2023_SK_tab0c.csv
https://volby.statistics.sk/nrsr/nrsr2023/files/csv/NRSR2023_SK_tab02d.csv
https://volby.statistics.sk/nrsr/nrsr2023/files/csv/NRSR2023_SK_tab03e.csv
https://volby.statistics.sk/nrsr/nrsr2023/files/csv/NRSR2023_SK_tab01.csv
https://volby.statistics.sk/nrsr/nrsr2023/files/csv/NRSR2023_SK_tab02a.csv
https://volby.statistics.sk/nrsr/nrsr2023/files/csv/NRSR2023_SK_tab02c.csv
https://volby.statistics.sk/nrsr/nrsr2023/files/csv/NRSR2023_SK_tab03a.csv
https://volby.statistics.sk/nrsr/nrsr2023/files/csv/NRSR2023_SK_tab0a.csv
```

### Small schema-drift samples

Retrieved **2026-10-11 UTC**. CSV HTTP Content-Type is `text/csv`; XLSX HTTP Content-Type is `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`. XLSX files are binary ZIP/OOXML, not CSV text; BOM/delimiter/newline assertions below apply to CSV only. XLSX XML was read with Python stdlib ZIP/XML tools, preserving cell addresses, not flattened into an assumed header row.

| Filename | Bytes | Retrieved UTC | HTTP Last-Modified UTC | SHA-256 |
| --- | ---: | --- | --- | --- |
| `NRSR_2020_SK_tab0c.csv` | 213589 | 19:33:27.636021 | 2020-03-01 10:01:01 | `38787953f5559f727c91badac640605d64aa07795962eb02cc47ee24e40f70de` |
| `NRSR_2020_SK_tab0a.csv` | 1501 | 19:33:27.340238 | 2020-03-01 10:01:01 | `317462ef2f98e9673c6f25ebf11acb5f37b2e881ccc6b02b63d92dbaa22e3db0` |
| `NRSR_2020_SK_tab02e.csv` | 304766 | 19:33:27.741401 | 2020-03-01 10:01:01 | `19f0a4efa13896c23be4432b24bda5809af0aaa2444a631f5e288655276fdf05` |
| `REF2023_SK_tab0b.csv` | 207723 | 19:33:27.633045 | 2023-01-22 00:11:32 | `19325c1c112ff7e10a133c1ae063dae100b3b755786a4cca625d47134ab6a2f1` |
| `REF2023_SK_tab02e.csv` | 277834 | 19:33:27.824288 | 2023-01-22 00:11:32 | `4dc6f6d1fc5d85f53867ba72eb9494324190d9edf3de26138fe58182ab36788c` |
| `REF2023_SK_tab03f.csv` | 149960 | 19:33:28.033326 | 2023-01-22 00:11:32 | `177a2d9585ef951d5068e272a4db03d425947ea74d3838d32a388c1b7eb32895` |
| `NRSR_2020_SK_tab01.xlsx` | 10661 | 19:33:27.807721 | 2020-03-01 13:56:29 | `c3904685ae57cc431ec4d8fbdc974722bc416cafb80c4175dca6141d1385ef25` |
| `REF2023_SK_tab01.xlsx` | 10635 | 19:33:27.898158 | 2023-01-22 00:09:55 | `89e04a19b6b0ef94c444bf14312808cc8c4cddb1001b9ffbaf835d0488bb4faf` |
| `REF2023_SK_tab03a.xlsx` | 10317 | 19:33:27.952935 | 2023-01-22 00:10:11 | `f50e93b6c3b75b04bb314532463cb07116e89c1a24cbd0d64d1455960a708b0e` |

```text
https://volby.statistics.sk/nrsr/nrsr2020/files/csv/NRSR_2020_SK_tab0c.csv
https://volby.statistics.sk/nrsr/nrsr2020/files/csv/NRSR_2020_SK_tab0a.csv
https://volby.statistics.sk/nrsr/nrsr2020/files/csv/NRSR_2020_SK_tab02e.csv
https://volby.statistics.sk/ref/ref2023/files/csv/REF2023_SK_tab0b.csv
https://volby.statistics.sk/ref/ref2023/files/csv/REF2023_SK_tab02e.csv
https://volby.statistics.sk/ref/ref2023/files/csv/REF2023_SK_tab03f.csv
https://volby.statistics.sk/nrsr/nrsr2020/files/xlsx/NRSR_2020_SK_tab01.xlsx
https://volby.statistics.sk/ref/ref2023/files/xlsx/REF2023_SK_tab01.xlsx
https://volby.statistics.sk/ref/ref2023/files/xlsx/REF2023_SK_tab03a.xlsx
```

## Byte-level CSV validation

Every CSV was decoded with `errors='strict'`; no replacement characters were inserted. Every record was parsed using Python `csv.reader(..., strict=True)` with the observed delimiter. Record widths below are invariant, including the header. Every file ends with LF; there are **zero CRLF sequences and zero bare CR bytes** across all sampled CSVs. LF counts equal record counts including the header, so no embedded multiline text was observed.

| Table | Data rows | Columns | LF bytes / total records | Dialect |
| --- | ---: | ---: | ---: | --- |
| NRSR2023 `tab0c` | 2927 | 9 | 2928 | comma, quoted text |
| NRSR2023 `tab02d` | 2927 | 18 | 2928 | comma, quoted text |
| NRSR2023 `tab03e` | 44272 | 14 | 44273 | comma, quoted text |
| NRSR2023 `tab01` | 1 | 10 | 2 | comma, quoted header |
| NRSR2023 `tab02a` | 9 | 12 | 10 | comma, quoted text |
| NRSR2023 `tab02c` | 80 | 16 | 81 | comma, quoted text |
| NRSR2023 `tab03a` | 25 | 7 | 26 | comma, quoted text |
| NRSR2023 `tab0a` | 25 | 5 | 26 | comma, quoted text |
| NRSR2020 `tab0c` | 2927 | 10 | 2928 | pipe, unquoted |
| NRSR2020 `tab0a` | 25 | 6 | 26 | pipe, unquoted |
| NRSR2020 `tab02e` | 5998 | 11 | 5999 | pipe, unquoted, decimal comma |
| REF2023 `tab0b` | 2927 | 9 | 2928 | pipe, unquoted |
| REF2023 `tab02e` | 5748 | 11 | 5749 | pipe, unquoted, decimal comma |
| REF2023 `tab03f` | 5748 | 6 | 5749 | pipe, unquoted, decimal comma |

All CSVs pass strict UTF-8 and have no BOM. NRSR2023 territory/municipality byte prefix is `224bc3b364206b72616a61222c224ec3` (UTF-8 `"Kód kraja","Ná…`). Strict CP1250 **fails** on NRSR2023 `tab0c`, `tab02d`, `tab03e`, `tab02c`, `tab03a`, `tab0a`, NRSR2020 `tab0c`/`tab0a`, and REF2023 `tab0b`. For example NRSR2023 `tab0c` fails CP1250 at byte offset 549, undefined byte `0x88`; its UTF-8 `Vrakuňa` is readable. Small NRSR2023 `tab01`/`tab02a` happen to decode under CP1250 but produce mojibake (`PoÄŤet`, `KĂłd`); strict success alone is not sufficient encoding identification. Some even-length files can similarly decode as nonsensical UTF-16 without a BOM. No UTF-16 interpretation is supported by their bytes/headers.

NRSR2020 `tab02e` and REF2023 `tab02e`/`tab03f` are numeric/ASCII-header files: strict UTF-8 is valid, but CP1250/CP1252 are also valid because the files contain no non-ASCII bytes. The companion territory/party files provide positive non-ASCII UTF-8 evidence. Do not claim that ASCII-only bytes uniquely prove UTF-8.

For NRSR2023, headers and text values are quoted with `"`, integer/decimal values are unquoted, and quoted party names contain commas. `tab03e` has 442,748 double-quote bytes; no doubled-quote escape sequence or embedded newline was observed there. Use a real CSV parser, not `split(',')`; retain standard double-quote escape support for future files. Older sampled CSVs have **zero double-quote bytes**. Percentages are plain numeric values without `%` signs; NRSR2023 uses dot and two fractional digits, older samples comma and two fractional digits. Counts/codes have no thousands separators.

No sampled CSV has blank or duplicate headers, preamble/title records, trailing empty header columns, or ragged records. NRSR2023 `tab0c`, `tab02d`, `tab03e` have **zero blank cells**. `tab0a` has 25 blank `Poznámka` cells. `tab03a` has 18 blank `Počet získaných mandátov` cells (the seven populated mandate values sum to 150). Preserve those raw blanks rather than silently treating every blank field as numeric zero. Older sampled precinct aggregates have zero blank cells.

## Exact NRSR2023 header → proposed importer-field mapping

These field names are recommendations for an importer contract, not an implemented public API. **Positions are one-based.** Codes should remain strings, including party numbers scoped to an election. Counts are non-negative integers; percentages should be decimal values or preserved source decimal strings, not recomputed with binary floating-point rounding.

### Shared territory prefix: columns 1–8

Present unchanged in `tab0c`, `tab02d` and `tab03e`:

| Position | Exact header | Proposed field |
| ---: | --- | --- |
| 1 | `Kód kraja` | `sourceRegionCode` |
| 2 | `Názov kraja` | `sourceRegionName` |
| 3 | `Kód územného obvodu` | `sourceTerritorialCircuitCode` |
| 4 | `Názov územného obvodu` | `sourceTerritorialCircuitName` |
| 5 | `Kód okresu` | `sourceDistrictCode` |
| 6 | `Názov okresu` | `sourceDistrictName` |
| 7 | `Kód obce` | `sourceMunicipalityCode` |
| 8 | `Názov obce` | `sourceMunicipalityName` |

`tab0c` column 9: `Počet volebných okrskov` → `precinctCount`.

### Municipality aggregate: `tab02d`, columns 9–18

| Position | Exact header | Proposed field / meaning |
| ---: | --- | --- |
| 9 | `Počet volebných okrskov` | `precinctCount` |
| 10 | `Počet potvrdených okrskových zápisníc` | `confirmedPrecinctCount` |
| 11 | `Podiel potvrdených okrskových zápisníc v %` | `confirmedPrecinctPercent` |
| 12 | `Počet zapísaných voličov` | `registeredVoters` |
| 13 | `Počet zúčastnených voličov` | `participatingVoters` |
| 14 | `Účasť voličov v %` | `turnoutPercent` |
| 15 | `Počet odovzdaných obálok na hlasovanie` | `submittedEnvelopes` |
| 16 | `Podiel odovzdaných obálok v %` | `submittedEnvelopePercent` |
| 17 | `Počet platných hlasov spolu` | `validVotes` |
| 18 | `Podiel platných hlasov spolu v %` | `validVotePercent` |

### Party-by-municipality: `tab03e`, columns 9–14

| Position | Exact header | Proposed field / meaning |
| ---: | --- | --- |
| 9 | `Číslo politického subjektu` | `sourcePartyNumber` (election-local) |
| 10 | `Názov politického subjektu` | `sourcePartyName` |
| 11 | `Počet platných hlasov` | `validVotes` for this party |
| 12 | `Podiel platných hlasov v %` | `partyVotePercent` of municipality valid votes |
| 13 | `Počet voličov, ktorí využili právo prednostného hlasovania` | `preferentialVoters` (voters, not summed candidate preferences) |
| 14 | `Podiel voličov, ktorí využili právo prednostného hlasovania v %` | `preferentialVoterPercent` of this party's votes |

Suggested keys: `(electionId, sourceMunicipalityCode)` for territory/aggregate; `(electionId, sourceMunicipalityCode, sourcePartyNumber)` for party results. Do not use party names/numbers as globally stable party IDs.

Supporting tables: `tab01` has exactly the ten aggregate headers in the `tab02d` suffix above (positions 9–18). `tab02a` prepends the first two territory headers to that suffix; `tab02c` prepends the first six. `tab03a` has, in order, party number, party name, valid votes, vote percent, preferential voters, preferential-voter percent (same exact headers as `tab03e` 9–14), then `Počet získaných mandátov`. `tab0a` has, in order, `Číslo politického subjektu`, `Názov politického subjektu`, `Skratka politického subjektu`, `Počet kandidátov`, `Poznámka`. Only this aggregate party list was acquired; no candidate/person table was acquired.

## Join measurements and city/foreign-vote handling

Measured against the checked-out `data/municipalities.json` (2,927), `data/districts.json` (79), `data/regions.json` (8), not against an external assumed geography version.

- Municipality codes join directly, with **2,926 / 2,927 official rows matched (99.966%)** and 100% of domestic election rows matched.
- Official-only row: region `9`, territorial circuit `900`, district `900`, municipality `599999`, all named **Cudzina**, 18 precincts. This is a foreign-voting aggregate, not a physical municipality. Keep its results in national totals and expose/normalize its scope separately if later required. Filtering to local municipality matches alone loses **57,856 valid votes**.
- Local-only row: municipality `518638`, **Valaškovce (vojenský obvod)**, district `SK0412`, region `SK041`. No election row is present. This observation does not establish the legal reason and must not be synthesized as a zero-turnout result.
- **270 joined names differ** exactly. Bratislava's 17 and Košice's 22 city parts match by code despite omitted `mestská časť` in election names. Other differences include local district disambiguators, hyphen spacing, and `Nechválova  Polianka` versus single-space local spelling. Name matching would create avoidable failures. Full differences are in `relationships.json`.
- No whole-city Bratislava/Košice aggregate rows are added on top of these city parts in `tab0c`/`tab02d`. City-part rows must not be added twice to city-level derived totals.
- Official coverage is **9 region codes, 80 district codes, 50 territorial-circuit codes** including foreign scope. Therefore domestic coverage is 8 regions, 79 districts, 49 territorial circuits. A territorial circuit (`územný obvod`) is **not** an administrative district: Bratislava has circuit `101` across district codes `101`–`105`, and other circuits also group multiple districts. Do not join the circuit code to `data/districts.json`.
- Region code crosswalk: `1 → SK010`, `2 → SK021`, `3 → SK022`, `4 → SK023`, `5 → SK031`, `6 → SK032`, `7 → SK041`, `8 → SK042`. Every domestic municipality agrees with this crosswalk; no hierarchy mismatches.
- All 79 domestic district codes map to exactly one local district through municipality membership, cover all local districts, and their source/local district names agree exactly. The observed mapping can be reproduced by `regionCrosswalk[sourceRegionCode] + str(int(sourceDistrictCode[-2:]))`, **without left-padding the district suffix**. Examples: `101 → SK0101`, `510 → SK03110`, `613 → SK03213`, `713 → SK04113`, `811 → SK04211`. This formula is verified for this checkout/sample, not a guaranteed universal geography standard. Prefer membership validation or the complete measured crosswalk in `relationships.json`; foreign `900` has no local target.

## National totals and relationship checks

All six integer measures below match independently between national `tab01`, sum of municipality `tab02d`, sum of district `tab02c`, and sum of region `tab02a`. Every individual district and region also equals the sum of its child municipality counts; zero group mismatches.

| Measure | National including foreign voting | Domestic only | Foreign row |
| --- | ---: | ---: | ---: |
| Precincts | 6014 | 5996 | 18 |
| Confirmed precincts | 6013 | 5995 | 18 |
| Registered voters | 4388872 | 4329142 | 59730 |
| Participating voters | 3007123 | 2948344 | 58779 |
| Submitted envelopes | 3002948 | 2944615 | 58333 |
| Valid votes | 2967896 | 2910040 | 57856 |

National percentages in source order: confirmed precincts **99.98**, turnout **68.51**, envelope share **99.86**, valid-vote share **98.69**. Only municipality `524140 / Prešov` has fewer confirmed than configured precincts: 66 configured, 65 confirmed. This agrees with the official exclusion notice for precinct 34; definitive publication is not equivalent to every precinct being counted. Do not fail ingestion merely because confirmation is below 100%.

Verified across every municipality:

- `validVotes ≤ submittedEnvelopes ≤ participatingVoters ≤ registeredVoters`: zero violations.
- `tab0c` has no duplicate municipality code; `tab02d` has none; their code sets and all shared fields are identical.
- `confirmedPrecinctPercent = truncate2(100 × confirmedPrecinctCount / precinctCount)`.
- `turnoutPercent = truncate2(100 × participatingVoters / registeredVoters)`.
- `submittedEnvelopePercent = truncate2(100 × submittedEnvelopes / participatingVoters)`.
- **`validVotePercent = truncate2(100 × validVotes / participatingVoters)`**, not `/ submittedEnvelopes`.
- All four percentage rules have zero mismatches and zero zero-denominators. Half-up rounding would disagree in 1,425 turnout, 363 envelope-share, and 1,320 valid-share rows. Preserve published values and test with decimal arithmetic.

Verified across `tab03e`:

- 44,272 unique `(municipalityCode, partyNumber)` keys, zero duplicates; 25 party numbers (`1`–`25`), 2,927 municipality codes.
- **Every row has positive valid votes**; municipalities contain between **4 and 25** party rows. A full grid would have 73,175 pairs, so **28,903 pairs are absent**. Each municipality's positive rows sum exactly to its aggregate valid votes; each party's votes and preferential-voter count sum exactly to `tab03a`. This supports treating an omitted pair as zero votes for this verified complete positive-vote table, but do not conflate omission with missing ingestion or a party absent from an election.
- Party votes sum to **2,967,896**. Preferential-voter counts sum to **2,470,782**; no row has preferential voters exceeding party votes. These counts are not candidate preference-vote totals.
- `partyVotePercent = truncate2(100 × partyVotes / municipalityValidVotes)` and `preferentialVoterPercent = truncate2(100 × preferentialVoters / partyVotes)` match every row (zero mismatches). The complete source has no zero-party-vote denominator because those pairs are omitted.
- National `tab03a` has seven populated mandate counts, summing to **150**; other mandate cells are blank. No candidate election results were needed to validate this.

## Schema drift: sampled parliamentary election and referendum

These are bounded samples, not full historical normalization. Do not extrapolate their exact schemas to all election years/types.

### NRSR2020

Observed file prefix is **`NRSR_2020_SK_`**, unlike NRSR2023's `NRSR2023_SK_`. Catalogue publishes CSV for selected tables only; `tab01`, `tab02a`–`tab02d` have null CSV links, so national schema was inspected in the small XLSX file rather than guessing CSV URLs or downloading the archive.

Exact pipe-delimited CSV headers:

```text
tab0c:  KRAJ|NKRAJ|OBVOD|NOBVOD|OKRES|NOKRES|OBEC|NOBEC|TYP_OBCE|P_ALL_OKRSOK
tab0a:  PS|NPS|SNPS|P_STR|P_KAN|POZNAMKA
tab02e: OBEC|OKRSOK|P_ZAP|P_ZUC|UCAST|P_OOO|P_OOO_PCT|P_NOC|P_NOC_PCT|P_HL|P_HL_PCT
```

Territory code/name pairs map respectively to NRSR2023's region, circuit, district, municipality fields. `P_ALL_OKRSOK` maps to precinct count. `TYP_OBCE` is an **additional column absent from the sampled NRSR2023 territory CSV**; observed city-part value is `2`, ordinary sample value `3`, foreign `4`. A complete authoritative enumeration was not inspected, so do not assign meanings to all values from examples alone. `PS`, `NPS`, `SNPS` are party number/name/short-name; `P_KAN` is candidate count, `POZNAMKA` note. `P_STR` is an additional older party-list field whose authoritative interpretation was not established here.

`tab02e` is precinct-grained: key `(OBEC, OKRSOK)`, not municipality-grained. Its national sums match XLSX exactly: registered **4,432,419**, participating **2,916,840**, in-person envelope voters `P_OOO` **2,865,284**, return-envelope voters from abroad `P_NOC` **48,925**, valid votes `P_HL` **2,881,511**. There are 5,998 rows, no duplicate precinct keys or blank cells. `UCAST`, `P_OOO_PCT`, `P_NOC_PCT`, `P_HL_PCT` have decimal commas. `P_OOO` and `P_NOC` are separately published counts; neither alone is the 2023 combined-envelope concept.

NRSR2020 territory contains exactly the same 2,927 municipality codes as NRSR2023's territory (including `599999`), but precinct counts sum to **5,998**, not 6,014. Foreign scope is named **Zahraničie**, with codes `9 / 900 / 900 / 599999`, **one** precinct. Its precinct result contains 4,116 registered, 3,861 participating, `P_OOO=0`, `P_NOC=3861`, valid votes 3,825. Foreign votes also exist in ordinary domestic municipality rows; the pseudo-unit is not the total of the national mail-vote column.

National XLSX `sheet1.xml`: title at A1, headers A3:L3, values A5:L5 (blank intervening rows), **12 columns**, whereas NRSR2023 CSV national result has 10. Columns A–F are precincts, delivered precinct reports, delivered-report percent, registered voters, participating voters, turnout. G–J are separate in-person and foreign return-envelope counts/percentages. K–L are valid votes and valid-vote percent. Exact original cells/headers are retained in `drift-manifest.json`, including a duplicated `obálku obálku` typo in H3 and Excel `_x000D_` newline escape in F3. Do not assume all XLSX files have CSV-style row-one headers.

### REF2023

Catalogue's territory table is **`tab0b`**, not parliamentary `tab0c`; referendum `tab0c` denotes special precincts, and `tab0a` denotes the question. CSV links are null for national summaries and municipality aggregates/results; small national XLSX tables and selected precinct CSVs were sampled instead.

Exact pipe-delimited CSV headers:

```text
tab0b:  KRAJ|NKRAJ|OBVOD|NOBVOD|OKRES|NOKRES|OBEC|NOBEC|P_ALL_OKRSOK
tab02e: OBEC|OKRSOK|P_ZAP|P_ZUC|UCAST|P_OOO|P_OOO_PCT|P_NOC|P_NOC_PCT|P_HL|P_PHL
tab03f: OBEC|OKRSOK|P_ANO|P_ANO_PCT|P_NIE|P_NIE_PCT
```

Territory has the same code set as both parliamentary territory samples, **5,761 configured precincts**, foreign codes `9 / 900 / 900 / 599999`, name **Zahraničie**, one foreign precinct. The two precinct CSVs each contain **5,748 result rows**: 13 fewer than configured. No universal configured-precinct-equals-result-row assertion is appropriate. A later importer would need to inspect the special-precinct table and official completeness context rather than guessing the reason for every absent row.

`P_HL` here is **all voting ballots**, not parliamentary valid votes; `P_PHL` is valid voting ballots. This is semantic drift, not merely a renamed field. Sums from precinct aggregate match national XLSX: registered **4,377,565**, participating **1,193,198**, in-person envelope voters **1,191,962**, return-envelope voters **760**, all ballots **1,192,249**, valid ballots **1,181,984**. `tab03f` sums to **1,163,586 yes** and **18,398 no**, whose sum equals valid ballots. National published yes/no percentages (**97.51 / 1.54**) use participating voters as denominator, not just valid yes/no votes.

National summary XLSX: title A1, headers A3:L3, values A4:L4; columns A–J resemble the older parliamentary report/participation/separate-envelope layout, but K–L are **all ballots / valid ballots**, not valid votes / percent. National referendum-result XLSX: headers A3:H3, values A4:H4: yes count, yes percent, no count, no percent, participating voters, turnout, invalid votes, invalid percent. Published invalid count **11,214** equals participating voters minus yes minus no; it is **not** simply all ballots minus valid ballots (10,265). A shared abstraction must preserve this distinction.

Foreign precinct result: registered **75**, participating **62**, in-person envelope voters **0**, return-envelope voters **62**, all/valid ballots **62**, yes **53**, no **9**. National return-envelope count 760 again exceeds the foreign pseudo-unit's 62; do not interpret `599999` as every vote mailed from abroad.

## Size/cost boundaries and suggested validation gates

Measured NRSR2023 core (`tab0c` + `tab02d` + `tab03e`) is **6,602,448 bytes** (~6.30 MiB). All eight acquired NRSR2023 files total **6,616,900 bytes** (~6.31 MiB). Long party names and repeated territory names dominate raw long-form rows; a compact normalized representation may be smaller, but no production serialization-size claim was measured. The full party-municipality CSV is small enough for a streaming importer; no spreadsheet library or archive is necessary for the 2023 core.

Catalogue-only sizes, **not downloaded or measured**: party-precinct `tab03f` CSV **12.0 MB**, horizontal municipality party table `tab08d` CSV **628.9 kB**, candidate municipality-preference `tab07e` CSV **804.2 MB**, candidate precinct-preference `tab07f` CSV **1.7 GB**. Full NRSR2023 CSV archive is advertised **215.5 MB** compressed. Avoid archives and personal/candidate tables for the aggregate spike. A horizontal party table may be smaller but requires its own wide-header inspection; no equivalence claim is made without reading it.

Before later importer acceptance, suggested gates derived from these measurements:

1. Pin election/table/dialect and expected headers explicitly; fail on unknown header signatures or record widths. Keep raw official codes/names and acquisition provenance.
2. Use strict UTF-8 for these verified files, real CSV quoting, and an explicit comma versus pipe delimiter. Do not silently fall back to CP1250 when parsing fails.
3. Check unique keys, exact territory→aggregate membership, complete domestic code join, and explicitly separate foreign scope from geography foreign keys.
4. Reconcile integer child counts, national totals and sparse party sums; allow definitive-but-excluded precincts and preserve confirmation counts.
5. Scope party numbers to election; distinguish preferential voters from individual candidate preferences. Do not invent candidate data.
6. Preserve published decimal percentages, with type/year-specific denominators and truncation rules. Distinguish referendum invalid-voter measure from invalid physical-ballot difference.
7. Treat historical/election-type adapters and licence/reuse verification as separate future work. This investigation does not authorize redistribution or establish all-year schemas.
