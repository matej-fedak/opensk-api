from fastapi import APIRouter, HTTPException, Response

from schemas.common import API_SOURCE, BANKS_LAST_UPDATED, STATIC_CACHE_CONTROL, error_detail, success_response
from services.bank_service import BankInvalidCodeError, BankNotFoundError, load_banks, lookup_bank


router = APIRouter(prefix="/banks", tags=["banks"])


@router.get(
    "",
    summary="List Slovak banks",
    description="Returns the static Slovak bank seed dataset.",
)
def list_banks(response: Response) -> dict[str, object]:
    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(
        data=load_banks(),
        source=f"{API_SOURCE} static banks dataset",
        last_updated=BANKS_LAST_UPDATED,
    )


@router.get(
    "/{code}",
    summary="Bank lookup by code",
    description="Returns one Slovak bank from the static seed dataset.",
)
def get_bank(code: str, response: Response) -> dict[str, object]:
    try:
        bank = lookup_bank(code)
    except BankInvalidCodeError:
        raise HTTPException(
            status_code=400,
            detail=error_detail(
                code="INVALID_FORMAT",
                message="Bank code must be 4 digits",
                message_sk="Bankový kód musí byť 4-ciferný",
            ),
            headers={"Cache-Control": STATIC_CACHE_CONTROL},
        )
    except BankNotFoundError:
        normalized = code.replace(" ", "")
        raise HTTPException(
            status_code=404,
            detail=error_detail(
                code="NOT_FOUND",
                message=f"No bank data available for {normalized}",
                message_sk=f"Pre bankový kód {normalized} nie sú dostupné údaje",
            ),
            headers={"Cache-Control": STATIC_CACHE_CONTROL},
        )

    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(
        data=bank,
        source=f"{API_SOURCE} static banks dataset",
        last_updated=BANKS_LAST_UPDATED,
    )
