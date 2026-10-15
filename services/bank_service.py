import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from schemas.banks import BankDatasetMetadata


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "banks.json"


class BankInvalidCodeError(ValueError):
    pass


class BankNotFoundError(KeyError):
    pass


def normalize_bank_code(code: str) -> str:
    return code.replace(" ", "")


def validate_bank_code_format(code: str) -> str:
    normalized = normalize_bank_code(code)
    if not re.fullmatch(r"\d{4}", normalized):
        raise BankInvalidCodeError(code)
    return normalized


@lru_cache(maxsize=1)
def load_banks_data() -> dict[str, Any]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_banks() -> list[dict[str, str | bool | None]]:
    data = load_banks_data()
    banks = data.get("banks", [])
    return list(banks)


def lookup_bank(code: str) -> dict[str, str | bool | None]:
    normalized = validate_bank_code_format(code)

    for bank in load_banks():
        if bank.get("code") == normalized:
            return bank

    raise BankNotFoundError(normalized)


def load_bank_metadata() -> dict[str, Any]:
    return BankDatasetMetadata.model_validate(load_banks_data()["metadata"]).model_dump()


def bank_response_metadata(*, iban: bool = False) -> dict[str, Any]:
    """One local source of truth; NBS does not perform checksum validation."""
    metadata = load_bank_metadata()
    source = (
        "OpenSK API / ISO 13616 IBAN checksum validation; Slovak bank-code resolution "
        "from Národná banka Slovenska converter"
        if iban else f"{metadata['source']}; transformed by OpenSK API"
    )
    result = {key: metadata[key] for key in (
        "sourceVersion", "sourceEffectiveDate", "sourceUrl", "sourceFileUrl",
        "sourceSha256", "sourceBytes", "termsUrl", "attribution", "transformation",
    )}
    result.update(source=source, lastUpdated=metadata["lastUpdated"], version="v1",
                  sourceDownloadedAt=metadata["downloadedAt"])
    return result
