import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Response

from schemas.common import (
    API_SOURCE,
    HOLIDAYS_LAST_UPDATED,
    STATIC_CACHE_CONTROL,
    error_detail,
    success_response,
)


router = APIRouter(prefix="/holidays", tags=["holidays"])

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "holidays.json"


def load_holidays() -> dict[str, list[dict[str, str]]]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


@router.get(
    "/{year}",
    summary="Holiday calendar by year",
    description="Returns Slovak public holidays for the requested year from the static seed dataset.",
)
def get_holidays(year: int, response: Response) -> dict[str, object]:
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
            headers={"Cache-Control": STATIC_CACHE_CONTROL},
        )

    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(
        data=holidays_data[year_key],
        source=f"{API_SOURCE} static dataset",
        last_updated=HOLIDAYS_LAST_UPDATED,
    )
