from datetime import date

from fastapi import APIRouter, HTTPException

from schemas.common import error_detail, success_response
from services.psc_service import (
    PSCInvalidFormatError,
    PSCNotFoundError,
    lookup_psc,
)


router = APIRouter(prefix="/psc", tags=["psc"])


@router.get("/{psc}")
def get_psc(psc: str) -> dict[str, object]:
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
        )

    return success_response(
        data=psc_data,
        source="OpenSK API static PSC seed dataset",
        last_updated=date.today().isoformat(),
    )
