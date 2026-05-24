import json
import re
from functools import lru_cache
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "psc.json"


class PSCInvalidFormatError(ValueError):
    pass


class PSCNotFoundError(KeyError):
    pass


def normalize_psc(psc: str) -> str:
    return psc.replace(" ", "")


def validate_psc_format(psc: str) -> str:
    normalized = normalize_psc(psc)
    if not re.fullmatch(r"\d{5}", normalized):
        raise PSCInvalidFormatError(psc)
    return normalized


@lru_cache(maxsize=1)
def load_psc_data() -> dict[str, dict[str, str]]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def lookup_psc(psc: str) -> dict[str, str]:
    normalized = validate_psc_format(psc)
    psc_data = load_psc_data()

    if normalized not in psc_data:
        raise PSCNotFoundError(normalized)

    return psc_data[normalized]
