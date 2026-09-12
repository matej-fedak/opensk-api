# Source Licence Questions

These are draft clarification questions only. Do not send emails automatically.

## PortalVS Classifier Datasets

Applies to classifier 9 (`Obce`), classifier 10 (`Okres`), and classifier 42 (`PSČ obcí SR a ČR`).

1. Is reuse of these classifier datasets allowed outside the PortalVS website/API?
2. Is redistribution of normalized classifier data through an open-source public API allowed?
3. Is local caching of classifier snapshots allowed for runtime use without live upstream calls?
4. Is transformation allowed, including filtering Slovak rows, normalizing field names, deriving links, or converting to JSON?
5. What attribution wording is required?
6. Are commercial downstream users allowed to consume redistributed data?
7. Are there restrictions on bulk download, bulk caching, or repeated refreshes?
8. Are there restrictions on partial datasets or derived/backfilled fields such as PSC `districtCode`?
9. Are there required notices, disclaimers, or version identifiers that must be preserved?
10. Are there privacy restrictions for any classifier rows?

## ŠÚ SR / RPO

Applies to future company/RPO expansion and any broader IČO lookup work.

1. Is reuse of RPO data allowed in an open-source project?
2. Is redistribution through a public API allowed?
3. Is local caching of RPO snapshots allowed for runtime use without live upstream calls?
4. Is commercial downstream use allowed?
5. Are there restrictions on bulk data use, bulk downloads, or mirroring?
6. What attribution wording is required?
7. Which fields, if any, must be excluded for privacy reasons?
8. Are natural-person entrepreneurs subject to additional privacy restrictions?
9. Are role-holder, stakeholder, statutory-body, or address fields subject to additional restrictions?
10. Are there required update cadences, stale-data notices, or deletion obligations?

## NBS Bank-Code Directory

Applies to the NBS directory of domestic payment-system identification codes.

1. Is reuse of the directory data allowed outside the NBS website?
2. Is redistribution of normalized bank-code data through an open-source public API allowed?
3. Is local caching of directory snapshots allowed for runtime use without live upstream calls?
4. Is transformation allowed, including converting CSV to JSON, normalizing field names, adding `activeParty`, or filtering non-SK BIC rows?
5. What attribution wording is required?
6. Are commercial downstream users allowed to consume redistributed data?
7. Are there restrictions on bulk download, mirroring, or periodic refreshes?
8. Are inactive rows allowed to be redistributed with an explicit inactive marker?
9. Are there required version, effective-date, or disclaimer notices that must be preserved?
10. Does any no-modification clause apply to normalized machine-readable datasets?

## Telecom Regulator Phone-Area Workbook

Applies to the machine-processable Excel file for municipalities assigned to primary telephone areas.

1. Is reuse of the workbook data allowed outside the regulator website?
2. Is redistribution of normalized phone-area data through an open-source public API allowed?
3. Is local caching of workbook snapshots allowed for runtime use without live upstream calls?
4. Is transformation allowed, including converting XLSX/CSV to JSON, normalizing field names, and linking rows to local municipality codes?
5. What attribution wording is required?
6. Are commercial downstream users allowed to consume redistributed data?
7. Are there restrictions on bulk download, mirroring, or periodic refreshes?
8. Are partial seed subsets allowed while a full import is pending?
9. Are there required version, effective-date, update-date, or disclaimer notices that must be preserved?
10. Are there any privacy or operational-security restrictions for municipality-to-primary-area mappings?
