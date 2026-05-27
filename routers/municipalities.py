from fastapi import APIRouter, HTTPException, Query, Response

from schemas.common import GEOGRAPHY_SEED_SOURCE, MUNICIPALITIES_LAST_UPDATED, STATIC_CACHE_CONTROL, error_detail, success_response
from services.geography_service import GeographyInvalidFormatError, GeographyNotFoundError, get_municipality, list_municipalities


router = APIRouter(prefix="/municipalities", tags=["municipalities"])


@router.get(
    "",
    summary="List municipalities",
    description="Returns the static municipalities seed dataset, optionally filtered by region or district code.",
)
def list_municipalities_endpoint(
    response: Response,
    regionCode: str | None = Query(default=None, description="Optional region code filter."),
    districtCode: str | None = Query(default=None, description="Optional district code filter."),
) -> dict[str, object]:
    try:
        municipalities = list_municipalities(region_code=regionCode, district_code=districtCode)
    except GeographyInvalidFormatError:
        raise HTTPException(
            status_code=400,
            detail=error_detail(
                code="INVALID_FORMAT",
                message="Region and district filters must use valid Slovak geography codes",
                message_sk="Filtre regionCode a districtCode musia byť platné slovenské geografické kódy",
            ),
            headers={"Cache-Control": STATIC_CACHE_CONTROL},
        )
    except GeographyNotFoundError:
        if districtCode is not None:
            normalized = districtCode.replace(" ", "")
            message = f"No municipality data available for district {normalized}"
            message_sk = f"Pre okres {normalized} nie sú dostupné údaje o obciach"
        else:
            normalized = regionCode.replace(" ", "") if regionCode is not None else ""
            message = f"No municipality data available for region {normalized}"
            message_sk = f"Pre kraj {normalized} nie sú dostupné údaje o obciach"

        raise HTTPException(
            status_code=404,
            detail=error_detail(
                code="NOT_FOUND",
                message=message,
                message_sk=message_sk,
            ),
            headers={"Cache-Control": STATIC_CACHE_CONTROL},
        )

    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(
        data=municipalities,
        source=GEOGRAPHY_SEED_SOURCE,
        last_updated=MUNICIPALITIES_LAST_UPDATED,
    )


@router.get(
    "/{code}",
    summary="Municipality lookup by code",
    description="Returns one Slovak municipality from the static geography seed dataset.",
)
def get_municipality_by_code(code: str, response: Response) -> dict[str, object]:
    try:
        municipality = get_municipality(code)
    except GeographyInvalidFormatError:
        raise HTTPException(
            status_code=400,
            detail=error_detail(
                code="INVALID_FORMAT",
                message="Municipality code must be 6 digits",
                message_sk="Kód obce musí byť 6-ciferný",
            ),
            headers={"Cache-Control": STATIC_CACHE_CONTROL},
        )
    except GeographyNotFoundError:
        normalized = code.replace(" ", "")
        raise HTTPException(
            status_code=404,
            detail=error_detail(
                code="NOT_FOUND",
                message=f"No municipality data available for {normalized}",
                message_sk=f"Pre obec {normalized} nie sú dostupné údaje",
            ),
            headers={"Cache-Control": STATIC_CACHE_CONTROL},
        )

    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(
        data=municipality,
        source=GEOGRAPHY_SEED_SOURCE,
        last_updated=MUNICIPALITIES_LAST_UPDATED,
    )
