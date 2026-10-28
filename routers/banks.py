from fastapi import APIRouter, HTTPException, Response

from schemas.common import STATIC_CACHE_CONTROL, error_detail
from schemas.banks import BankResponse, BanksResponse
from schemas.openapi import contract
from services.bank_service import BankInvalidCodeError, BankNotFoundError, bank_response_metadata, load_banks, lookup_bank


router = APIRouter(prefix="/banks", tags=["banks"])


@router.get(
    "",
    summary="List Slovak banks",
    description="Returns the local Národná banka Slovenska converter snapshot, transformed by OpenSK. Metadata carries NBS source/version/effective/download provenance and attribution. NBS Terms of Use apply to data, not MIT. Participation fields are OpenSK-derived from SIPS, not general bank operating status.",
    **contract("list_banks", BanksResponse, 429, exclude_unset=False),
)
def list_banks(response: Response) -> dict[str, object]:
    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return {"data": load_banks(), "metadata": bank_response_metadata(), "error": None}


@router.get(
    "/{code}",
    summary="Bank lookup by code",
    description="Returns one bank from the local NBS converter snapshot. Additive metadata identifies NBS, source version/effective/download provenance, attribution and OpenSK transformation/derived fields. JSON is not the original NBS file; MIT covers code, not NBS data.",
    **contract("get_bank", BankResponse, 400, 404, 429, exclude_unset=False),
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
    return {"data": bank, "metadata": bank_response_metadata(), "error": None}
