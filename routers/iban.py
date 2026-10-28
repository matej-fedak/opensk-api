from fastapi import APIRouter, Response

from schemas.common import STATIC_CACHE_CONTROL
from schemas.banks import IbanValidationResponse
from schemas.openapi import contract
from services.bank_service import bank_response_metadata, lookup_bank
from services.iban_service import validate_iban


router = APIRouter(prefix="/iban", tags=["iban"])


@router.get(
    "/validate/{iban}",
    summary="Validate IBAN",
    description="OpenSK performs ISO 13616 checksum validation; NBS does not validate the checksum. Slovak bank-code resolution uses the local NBS converter only. Metadata on every validation result declares that resolution dataset's version, effective/download provenance, NBS attribution and OpenSK transformation. NBS Terms of Use govern bank data; MIT covers code.",
    **contract("validate_iban", IbanValidationResponse, 429, exclude_unset=False),
)
def validate_iban_endpoint(iban: str, response: Response) -> dict[str, object]:
    result = validate_iban(iban, bank_lookup=lookup_bank)
    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return {"data": result, "metadata": bank_response_metadata(iban=True), "error": None}
