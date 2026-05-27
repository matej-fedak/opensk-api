from fastapi import APIRouter, HTTPException, Query, Response

from schemas.common import (
    API_SOURCE,
    PSC_GEOGRAPHY_SOURCE,
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
def get_psc(
    psc: str,
    response: Response,
    include: str | None = Query(default=None, description="Optional response expansion. Supported value: geography."),
) -> dict[str, object]:
    include_geography = False
    if include is not None:
        if include != "geography":
            raise HTTPException(
                status_code=400,
                detail=error_detail(
                    code="INVALID_FORMAT",
                    message="include must be omitted or set to geography",
                    message_sk="Parameter include musí byť vynechaný alebo nastavený na geography",
                ),
                headers={"Cache-Control": STATIC_CACHE_CONTROL},
            )
        include_geography = True

    try:
        psc_data = lookup_psc(psc, include_geography=include_geography)
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
    source = f"{API_SOURCE} static PSC seed dataset"
    if include_geography:
        source = PSC_GEOGRAPHY_SOURCE
    return success_response(
        data=psc_data,
        source=source,
        last_updated=PSC_LAST_UPDATED,
    )
