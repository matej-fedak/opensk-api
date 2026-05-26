import json
import re
from functools import lru_cache
from pathlib import Path


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
def load_banks_data() -> dict[str, object]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_banks() -> list[dict[str, str]]:
    data = load_banks_data()
    banks = data.get("banks", [])
    return list(banks)


def lookup_bank(code: str) -> dict[str, str]:
    normalized = validate_bank_code_format(code)

    for bank in load_banks():
        if bank.get("code") == normalized:
            return bank

    raise BankNotFoundError(normalized)
