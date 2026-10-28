"""Typed public models for the ECB euro reference-rate endpoints.

Rates stay decimal strings end to end: OpenSK reproduces ECB reference values
verbatim and performs no financial arithmetic on them.
"""

from typing import Literal

from pydantic import BaseModel, Field


class ExchangeRatesData(BaseModel):
    date: str = Field(
        description="ECB publication date of this rate set (exact date only, no fallback).",
        examples=["2026-10-12"],
    )
    base: Literal["EUR"] = Field(description="Base currency of every rate in this object.")
    directionSemantics: str = Field(
        description="Rate direction: `1 EUR = rate units of the foreign currency`. "
        "Example: USD = \"1.16\" means 1 EUR = 1.16 USD. OpenSK does not invert values, "
        "compute cross rates, or multiply amounts.",
    )
    rates: dict[str, str] = Field(
        description="Official ECB reference rates as exact decimal strings, keyed by ISO 4217 "
        "alpha-3 currency code. Strings preserve the official lexeme/precision; these are "
        "informational reference values, not tradable/settlement prices.",
        examples=[{"USD": "1.1181"}],
    )
    notice: str = Field(
        description="ECB use notice reproduced with the materialized snapshot.",
    )


class ExchangeRatesResponseMetadata(BaseModel):
    source: str
    lastUpdated: str = Field(
        description="Freshness of the materialized OpenSK snapshot: the newest ECB "
        "publication date it contains (not necessarily this response's `data.date`).",
    )
    version: Literal["v1"]


class ExchangeRateDayResponse(BaseModel):
    data: ExchangeRatesData
    metadata: ExchangeRatesResponseMetadata
    error: None
