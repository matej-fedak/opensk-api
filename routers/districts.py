from fastapi import APIRouter, HTTPException, Query, Response

from schemas.common import DISTRICTS_LAST_UPDATED, GEOGRAPHY_SOURCE, STATIC_CACHE_CONTROL, error_detail, success_response
from services.geography_service import GeographyInvalidFormatError, GeographyNotFoundError, get_district, list_districts


router = APIRouter(prefix="/districts", tags=["districts"])


@router.get(
    "",
    summary="List districts",
    description="Returns the static districts dataset, optionally filtered by region code.",
)
def list_districts_endpoint(
    response: Response,
    regionCode: str | None = Query(default=None, description="Optional region code filter."),
) -> dict[str, object]:
    try:
        districts = list_districts(region_code=regionCode)
    except GeographyInvalidFormatError:
        raise HTTPException(
            status_code=400,
            detail=error_detail(
                code="INVALID_FORMAT",
                message="Region filter must match the SK### format",
                message_sk="Filter regionCode musí mať formát SK###",
            ),
            headers={"Cache-Control": STATIC_CACHE_CONTROL},
        )
    except GeographyNotFoundError:
        normalized = regionCode.replace(" ", "") if regionCode is not None else ""
        raise HTTPException(
            status_code=404,
            detail=error_detail(
                code="NOT_FOUND",
                message=f"No district data available for region {normalized}",
                message_sk=f"Pre kraj {normalized} nie sú dostupné údaje o okresoch",
            ),
            headers={"Cache-Control": STATIC_CACHE_CONTROL},
        )

    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(
        data=districts,
        source=GEOGRAPHY_SOURCE,
        last_updated=DISTRICTS_LAST_UPDATED,
    )


@router.get(
    "/{code}",
    summary="District lookup by code",
    description="Returns one Slovak district from the static geography dataset.",
)
def get_district_by_code(code: str, response: Response) -> dict[str, object]:
    try:
        district = get_district(code)
    except GeographyInvalidFormatError:
        raise HTTPException(
            status_code=400,
            detail=error_detail(
                code="INVALID_FORMAT",
                message="District code must match the SK#### format",
                message_sk="Kód okresu musí mať formát SK####",
            ),
            headers={"Cache-Control": STATIC_CACHE_CONTROL},
        )
    except GeographyNotFoundError:
        normalized = code.replace(" ", "")
        raise HTTPException(
            status_code=404,
            detail=error_detail(
                code="NOT_FOUND",
                message=f"No district data available for {normalized}",
                message_sk=f"Pre kód okresu {normalized} nie sú dostupné údaje",
            ),
            headers={"Cache-Control": STATIC_CACHE_CONTROL},
        )

    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(
        data=district,
        source=GEOGRAPHY_SOURCE,
        last_updated=DISTRICTS_LAST_UPDATED,
    )
