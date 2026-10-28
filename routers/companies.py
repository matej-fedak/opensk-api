from fastapi import APIRouter, HTTPException, Response

from schemas.common import API_SOURCE, STATIC_CACHE_CONTROL, error_detail, success_response
from services.company_service import CompanyDatasetUnavailableError, CompanyInvalidIcoError, CompanyNotFoundError, load_company_metadata, lookup_company
from schemas.common import SuccessResponse
from schemas.companies import Company
from schemas.openapi import contract


router = APIRouter(tags=["companies"])


def _company_response(ico: str, response: Response) -> dict[str, object]:
    try:
        company = lookup_company(ico)
        metadata = load_company_metadata()
    except CompanyInvalidIcoError:
        raise HTTPException(
            status_code=400,
            detail=error_detail(
                code="INVALID_FORMAT",
                message="IČO must be 8 digits",
                message_sk="IČO musí byť 8-ciferné",
            ),
            headers={"Cache-Control": STATIC_CACHE_CONTROL},
        )
    except CompanyNotFoundError:
        normalized = ico.replace(" ", "")
        raise HTTPException(
            status_code=404,
            detail=error_detail(
                code="NOT_FOUND",
                message=f"No company data available for {normalized}",
                message_sk=f"Pre IČO {normalized} nie sú dostupné údaje",
            ),
            headers={"Cache-Control": STATIC_CACHE_CONTROL},
        )
    except CompanyDatasetUnavailableError:
        raise HTTPException(
            status_code=503,
            detail=error_detail(
                code="DATASET_UNAVAILABLE",
                message="Local company dataset is not available",
                message_sk="Lokálny dataset spoločností nie je k dispozícii",
            ),
        )

    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    source = f"{API_SOURCE} local company dataset"
    last_updated = metadata.get("lastUpdated") if isinstance(metadata.get("lastUpdated"), str) else None
    return success_response(
        data=company,
        source=source,
        last_updated=last_updated,
    )


@router.get(
    "/companies/{ico}",
    summary="Company lookup by IČO",
    description="Looks up one company in a small local seed set, not a complete or live Slovak business register. Nullable fields mean unknown in this snapshot. 404 means absent locally, not a legally invalid IČO; redistribution status remains pending (see /v1/sources/companies).",
    **contract("get_company", SuccessResponse[Company], 400, 404, 429, 503),
)
def get_company(ico: str, response: Response) -> dict[str, object]:
    return _company_response(ico, response)


@router.get(
    "/ico/{ico}",
    summary="Company lookup by IČO alias",
    description="Existing alias of /v1/companies/{ico}; identical small seed-set lookup and errors, not a complete or live business register. A local 404 does not establish legal invalidity of an IČO. See /v1/sources/companies for coverage/reuse limitations.",
    **contract("get_company_by_ico", SuccessResponse[Company], 400, 404, 429, 503),
)
def get_company_by_ico(ico: str, response: Response) -> dict[str, object]:
    return _company_response(ico, response)
