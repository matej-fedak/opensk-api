import json
from pathlib import Path
from typing import Any

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


def load_holidays() -> dict[str, list[dict[str, Any]]]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


@router.get(
    "/{year}",
    summary="Holiday calendar by year",
    description="Returns the statutory Slovak holiday calendar for a verified year (2024–2030). Includes state holidays and other statutory holiday dates, even legally working holidays; use isDayOfRest, not membership, to identify holiday-related non-working status. Rules verified 2026-10-28; future years subject to legislative change. Other years return 404, not an assertion that there are no holidays. Not a settlement, employer, shop-opening or authority-opening calendar.",
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
