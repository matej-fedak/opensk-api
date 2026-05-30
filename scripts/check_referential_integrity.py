#!/usr/bin/env python3
"""Check PSC and geography referential integrity."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.geography_service import load_districts, load_municipalities, load_regions
from services.psc_service import load_psc_data


def index_by_code(records: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    return {str(record["code"]): record for record in records if record.get("code") is not None}


def collect_errors() -> list[str]:
    errors: list[str] = []

    regions = index_by_code(load_regions())
    districts = index_by_code(load_districts())
    municipalities = index_by_code(load_municipalities())
    psc_records = load_psc_data()

    for district_code, district in districts.items():
        region_code = district.get("regionCode")
        if not region_code:
            errors.append(f"District {district_code}: missing regionCode")
            continue
        if region_code not in regions:
            errors.append(f"District {district_code}: unknown regionCode {region_code}")

    for municipality_code, municipality in municipalities.items():
        district_code = municipality.get("districtCode")
        region_code = municipality.get("regionCode")

        if not district_code:
            errors.append(f"Municipality {municipality_code}: missing districtCode")
        elif district_code not in districts:
            errors.append(f"Municipality {municipality_code}: unknown districtCode {district_code}")

        if not region_code:
            errors.append(f"Municipality {municipality_code}: missing regionCode")
        elif region_code not in regions:
            errors.append(f"Municipality {municipality_code}: unknown regionCode {region_code}")

        if district_code in districts and region_code:
            expected_region_code = districts[district_code]["regionCode"]
            if expected_region_code != region_code:
                errors.append(
                    "Municipality "
                    f"{municipality_code}: regionCode {region_code} does not match district {district_code} regionCode {expected_region_code}"
                )

    for psc_code, record in psc_records.items():
        region_code = record.get("regionCode")
        district_code = record.get("districtCode")
        municipality_code = record.get("municipalityCode")

        district_region_code = None
        municipality_region_code = None

        if region_code is not None and region_code not in regions:
            errors.append(f"PSC {psc_code}: unknown regionCode {region_code}")

        if district_code is not None:
            if district_code not in districts:
                errors.append(f"PSC {psc_code}: unknown districtCode {district_code}")
            else:
                district_region_code = districts[district_code].get("regionCode")
                if region_code is not None and district_region_code != region_code:
                    errors.append(
                        f"PSC {psc_code}: districtCode {district_code} belongs to regionCode {district_region_code}, "
                        f"but PSC regionCode is {region_code}"
                    )

        if municipality_code is not None:
            if municipality_code not in municipalities:
                errors.append(f"PSC {psc_code}: unknown municipalityCode {municipality_code}")
            else:
                municipality = municipalities[municipality_code]
                municipality_district_code = municipality.get("districtCode")
                municipality_region_code = municipality.get("regionCode")

                if district_code is not None and municipality_district_code != district_code:
                    errors.append(
                        f"PSC {psc_code}: municipalityCode {municipality_code} belongs to districtCode {municipality_district_code}, "
                        f"but PSC districtCode is {district_code}"
                    )

                if region_code is not None and municipality_region_code != region_code:
                    errors.append(
                        f"PSC {psc_code}: municipalityCode {municipality_code} belongs to regionCode {municipality_region_code}, "
                        f"but PSC regionCode is {region_code}"
                    )

                if district_code is not None and district_code in districts:
                    expected_region_code = districts[district_code].get("regionCode")
                    if municipality_region_code != expected_region_code:
                        errors.append(
                            f"PSC {psc_code}: municipalityCode {municipality_code} belongs to regionCode {municipality_region_code}, "
                            f"but PSC districtCode {district_code} belongs to regionCode {expected_region_code}"
                        )

        if region_code is None and district_region_code is not None and municipality_region_code is not None:
            if district_region_code != municipality_region_code:
                errors.append(
                    f"PSC {psc_code}: districtCode {district_code} regionCode {district_region_code} does not match "
                    f"municipalityCode {municipality_code} regionCode {municipality_region_code}"
                )

    return errors


def main() -> int:
    errors = collect_errors()

    if errors:
        print("Referential integrity check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Referential integrity check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
