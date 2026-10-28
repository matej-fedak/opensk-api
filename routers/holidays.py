import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Response
from schemas.common import SuccessResponse
from schemas.holidays import Holiday
from schemas.openapi import contract

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
    description="Returns the local Slovak public-holiday array for a verified year (2024–2026 only). Other years return 404, not an assertion that there are no holidays. Not a bank settlement or employer-specific calendar.",
    **contract("get_holidays", SuccessResponse[list[Holiday]], 404, 422, 429),
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
        source=f"{API_SOURCE} static holidays dataset",
        last_updated=HOLIDAYS_LAST_UPDATED,
    )
