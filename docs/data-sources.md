# Data Sources

## Geography

- Source chosen: public Slovak administrative division references and the National Open Data Catalog at `https://data.slovensko.sk/`.
- Regions in v0.3.0 follow the 8 Slovak self-governing region code set.
- Districts and municipalities in this release are seed datasets, not full national imports.
- Municipality codes are provisional seed identifiers where not fully verified.
- PSC responses in v0.4.0 link to local geography codes where a seed mapping exists.
- PSC geography expansion is static and local; it does not call upstream services.
- PSC mappings are intentionally partial and should be treated as seed data.
- License/attribution should be confirmed against the exact dataset used before any production-grade expansion.

## Notes

- No upstream API calls happen at request time.
- The API serves static JSON datasets from the repository at runtime.
