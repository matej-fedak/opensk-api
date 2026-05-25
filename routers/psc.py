from fastapi import APIRouter, HTTPException, Response

from schemas.common import (
    API_SOURCE,
    PSC_LAST_UPDATED,
    STATIC_CACHE_CONTROL,
    error_detail,
    success_response,
)
from services.psc_service import (
    PSCInvalidFormatError,
    PSCNotFoundError,
    lookup_psc,
)


router = APIRouter(prefix="/psc", tags=["psc"])


@router.get(
    "/{psc}",
    summary="Postal code lookup",
    description="Looks up a Slovak postal code in the static PSC seed dataset.",
)
def get_psc(psc: str, response: Response) -> dict[str, object]:
    try:
        psc_data = lookup_psc(psc)
    except PSCInvalidFormatError:
        raise HTTPException(
            status_code=400,
            detail=error_detail(
                code="INVALID_FORMAT",
                message="PSC must be a 5-digit Slovak postal code",
                message_sk="PSČ musí byť 5-ciferné slovenské poštové číslo",
            ),
            headers={"Cache-Control": STATIC_CACHE_CONTROL},
        )
    except PSCNotFoundError:
        normalized = psc.replace(" ", "")
        raise HTTPException(
            status_code=404,
            detail=error_detail(
                code="NOT_FOUND",
                message=f"No PSC data available for {normalized}",
                message_sk=f"Pre PSČ {normalized} nie sú dostupné údaje",
            ),
            headers={"Cache-Control": STATIC_CACHE_CONTROL},
        )

    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(
        data=psc_data,
        source=f"{API_SOURCE} static PSC seed dataset",
        last_updated=PSC_LAST_UPDATED,
    )
