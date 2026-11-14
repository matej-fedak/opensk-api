from collections.abc import Callable
import re


def normalize_iban(iban: str) -> str:
    return iban.replace(" ", "").upper()


def extract_country_code(iban: str) -> str | None:
    normalized = normalize_iban(iban)
    if len(normalized) < 2:
        return None
    return normalized[:2]


def extract_slovak_bank_code(iban: str) -> str | None:
    normalized = normalize_iban(iban)
    if not iban.isascii() or not re.fullmatch(r"SK[0-9]{22}", normalized):
        return None
    return normalized[4:8]


def iban_checksum_valid(iban: str) -> bool:
    normalized = normalize_iban(iban)
    # Unicode digit/letter predicates include characters outside ISO 13616,
    # some of which int() cannot parse or upper() maps into ASCII letters.
    if not iban.isascii() or not re.fullmatch(r"[A-Z]{2}[0-9]{2}[A-Z0-9]{0,30}", normalized):
        return False

    rearranged = normalized[4:] + normalized[:4]
    numeric = "".join(str(ord(character) - 55) if character.isalpha() else character for character in rearranged)

    remainder = 0
    for digit in numeric:
        remainder = (remainder * 10 + int(digit)) % 97

    return remainder == 1


def validate_iban(
    iban: str,
    bank_lookup: Callable[[str], dict[str, str | bool | None]] | None = None,
) -> dict[str, object]:
    normalized = normalize_iban(iban)
    country_code = extract_country_code(normalized)
    checksum_valid = iban_checksum_valid(iban)
    supported_country = country_code == "SK"
    slovak_structure = iban.isascii() and re.fullmatch(r"SK[0-9]{22}", normalized) is not None
    bank_code = extract_slovak_bank_code(iban) if slovak_structure else None
    bank_name = None

    if bank_code and bank_lookup is not None:
        try:
            bank = bank_lookup(bank_code)
        except Exception:
            bank = None
        if bank is not None:
            bank_name = bank.get("name")

    return {
        "inputIban": iban,
        "normalizedIban": normalized,
        "countryCode": country_code,
        "supportedCountry": supported_country,
        "checksumValid": checksum_valid,
        "bankCode": bank_code,
        "bankName": bank_name,
        "valid": slovak_structure and checksum_valid,
    }
