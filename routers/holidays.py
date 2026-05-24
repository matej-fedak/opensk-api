import json
from datetime import date
from pathlib import Path

from fastapi import APIRouter, HTTPException

from schemas.common import error_detail, success_response


router = APIRouter(prefix="/holidays", tags=["holidays"])

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "holidays.json"


def load_holidays() -> dict[str, list[dict[str, str]]]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


@router.get("/{year}")
def get_holidays(year: int) -> dict[str, object]:
    holidays_data = load_holidays()
    year_key = str(year)

    if year_key not in holidays_data:
        raise HTTPException(
            status_code=404,
            detail=error_detail(
                code="NOT_FOUND",
                message=f"No holiday data available for year {year}",
                message_sk=f"Nie sú dostupné sviatky pre rok {year}",
            ),
        )

    return success_response(
        data=holidays_data[year_key],
        source="OpenSK API static dataset",
        last_updated=date.today().isoformat(),
    )
