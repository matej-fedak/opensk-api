from collections.abc import Callable


def normalize_iban(iban: str) -> str:
    return iban.replace(" ", "").upper()


def extract_country_code(iban: str) -> str | None:
    normalized = normalize_iban(iban)
    if len(normalized) < 2:
        return None
    return normalized[:2]


def extract_slovak_bank_code(iban: str) -> str | None:
    normalized = normalize_iban(iban)
    if not normalized.startswith("SK") or len(normalized) < 8:
        return None
    return normalized[4:8]


def iban_checksum_valid(iban: str) -> bool:
    normalized = normalize_iban(iban)
    if len(normalized) < 4 or not normalized.isalnum():
        return False

    rearranged = normalized[4:] + normalized[:4]
    numeric = "".join(str(ord(character) - 55) if character.isalpha() else character for character in rearranged)

    remainder = 0
    for digit in numeric:
        remainder = (remainder * 10 + int(digit)) % 97

    return remainder == 1


def validate_iban(
    iban: str,
    bank_lookup: Callable[[str], dict[str, str]] | None = None,
) -> dict[str, object]:
    normalized = normalize_iban(iban)
    country_code = extract_country_code(normalized)
    checksum_valid = iban_checksum_valid(normalized)
    supported_country = country_code == "SK"
    bank_code = extract_slovak_bank_code(normalized) if supported_country else None
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
        "valid": supported_country and checksum_valid,
    }
