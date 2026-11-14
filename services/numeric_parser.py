"""Bounded ASCII integer parsing for user-controlled numeric parameters."""


class ASCIIIntegerFormatError(ValueError):
    pass


def parse_ascii_integer(value: str, *, minimum: int = 0, maximum: int, signed: bool = False) -> int:
    """Reject non-ASCII digits and oversized input before calling ``int``.

    Ten digits cover all runtime pagination bounds. Bounding the representation
    also avoids Python's integer-string conversion limit, including zero padding.
    Callers retain their own whitespace and HTTP error policies.
    """
    digits = value[1:] if signed and value.startswith("-") else value
    if not 1 <= len(digits) <= 10 or not digits.isascii() or not digits.isdecimal():
        raise ASCIIIntegerFormatError("Expected at most ten ASCII digits")
    parsed = int(value)
    if not minimum <= parsed <= maximum:
        raise ValueError("Integer outside supported range")
    return parsed
