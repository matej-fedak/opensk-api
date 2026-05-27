from fastapi import APIRouter, HTTPException, Response

from schemas.common import GEOGRAPHY_SOURCE, REGIONS_LAST_UPDATED, STATIC_CACHE_CONTROL, error_detail, success_response
from services.geography_service import GeographyInvalidFormatError, GeographyNotFoundError, get_region, load_regions


router = APIRouter(prefix="/regions", tags=["regions"])


@router.get(
    "",
    summary="List regions",
    description="Returns the complete static regions dataset.",
)
def list_regions(response: Response) -> dict[str, object]:
    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(
        data=load_regions(),
        source=GEOGRAPHY_SOURCE,
        last_updated=REGIONS_LAST_UPDATED,
    )


@router.get(
    "/{code}",
    summary="Region lookup by code",
    description="Returns one Slovak region from the static geography dataset.",
)
def get_region_by_code(code: str, response: Response) -> dict[str, object]:
    try:
        region = get_region(code)
    except GeographyInvalidFormatError:
        raise HTTPException(
            status_code=400,
            detail=error_detail(
                code="INVALID_FORMAT",
                message="Region code must match the SK### format",
                message_sk="Kód kraja musí mať formát SK###",
            ),
            headers={"Cache-Control": STATIC_CACHE_CONTROL},
        )
    except GeographyNotFoundError:
        normalized = code.replace(" ", "")
        raise HTTPException(
            status_code=404,
            detail=error_detail(
                code="NOT_FOUND",
                message=f"No region data available for {normalized}",
                message_sk=f"Pre kód kraja {normalized} nie sú dostupné údaje",
            ),
            headers={"Cache-Control": STATIC_CACHE_CONTROL},
        )

    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(
        data=region,
        source=GEOGRAPHY_SOURCE,
        last_updated=REGIONS_LAST_UPDATED,
    )
