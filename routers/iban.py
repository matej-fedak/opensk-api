from fastapi import APIRouter

from schemas.common import API_SOURCE, BANKS_LAST_UPDATED, success_response
from services.bank_service import lookup_bank
from services.iban_service import validate_iban


router = APIRouter(prefix="/iban", tags=["iban"])


@router.get(
    "/validate/{iban}",
    summary="Validate IBAN",
    description="Validates an IBAN with the ISO 13616 checksum and resolves Slovak bank data when available.",
)
def validate_iban_endpoint(iban: str) -> dict[str, object]:
    result = validate_iban(iban, bank_lookup=lookup_bank)
    return success_response(
        data=result,
        source=f"{API_SOURCE} static banks dataset",
        last_updated=BANKS_LAST_UPDATED,
    )
