"""Aggregate-only NRSR2023 routes, explicitly not a live election feed."""

import re

from fastapi import APIRouter, HTTPException, Query, Response

from schemas.common import (ELECTIONS_NRSR2023_LAST_UPDATED, STATIC_CACHE_CONTROL,
                            Page, SuccessResponse, error_detail, success_response)
from schemas.elections import ElectionCatalogueEntry, ElectionParty, ElectionUnit
from schemas.openapi import contract
from services import elections_service as service


router = APIRouter(prefix="/elections", tags=["elections"])
SOURCE = "Štatistický úrad SR — NR SR 2023; CC BY 4.0; OpenSK CSV→JSON aggregate snapshot; not an official ŠÚ SR service"
NOTICE = (
    "Definitive historical NR SR 2023 results, local materialized snapshot only, not live election reporting. "
    "Source files were manually downloaded; automated website downloading remains prohibited. "
    "ŠÚ SR directly confirmed CC BY 4.0 reuse; retain attribution, source/licence links and modification disclosure "
    "from /v1/sources/elections. OpenSK is not an official ŠÚ SR service and no endorsement is implied. "
    "Election-native unit summaries and national political-subject results only; no municipality-party cells, "
    "precinct results, candidate/preference/elected-person or voter records. Small-area aggregates may permit "
    "contextual inference; no anonymity claim. Unit 599999 / Cudzina is foreign voting, not a Slovak municipality; "
    "native hierarchy 9/900/900 is retained, with no PortalVS dependency."
)


def invalid(parameter: str) -> HTTPException:
    return HTTPException(400, detail=error_detail("INVALID_FORMAT", f"Invalid {parameter}",
                                                 f"Neplatný parameter {parameter}"),
                         headers={"Cache-Control": STATIC_CACHE_CONTROL})


def require_election(election_id: str) -> None:
    if election_id != "NRSR2023":
        raise HTTPException(404, detail=error_detail("NOT_FOUND", "Election not found", "Voľby sa nenašli"),
                            headers={"Cache-Control": STATIC_CACHE_CONTROL})


def code(value: str | None, parameter: str, pattern: str) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if not re.fullmatch(pattern, value):
        raise invalid(parameter)
    return value


def integer(value: str, parameter: str, minimum: int, maximum: int) -> int:
    value = value.strip()
    if not re.fullmatch(r"[0-9]{1,10}", value) or not minimum <= int(value) <= maximum:
        raise invalid(parameter)
    return int(value)


def envelope(data, response: Response):
    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return success_response(data, SOURCE, ELECTIONS_NRSR2023_LAST_UPDATED)


@router.get("", summary="List materialized historical elections", description=NOTICE,
            **contract("list_elections", SuccessResponse[list[ElectionCatalogueEntry]], 429))
def list_elections(response: Response):
    return envelope(service.catalogue(), response)


@router.get("/{electionId}/results", summary="List election-native unit aggregate results",
            description=NOTICE + " Exact native-code filters combine with AND. No matches return an empty 200 page. "
            "Stable region/circuit/district/unit code order; default limit 50, maximum 100. "
            "Unknown elections return 404, invalid filters/pagination 400. Percentages are exact source decimal strings.",
            **contract("list_election_results", SuccessResponse[Page[ElectionUnit]], 400, 404, 429))
def list_election_results(
    electionId: str, response: Response,
    regionCode: str | None = Query(None, description="Exact election-native one-digit region code, including foreign 9."),
    districtCode: str | None = Query(None, description="Exact election-native three-digit district code, including foreign 900."),
    municipalityCode: str | None = Query(None, description="Exact six-digit election-native unit code, including foreign 599999."),
    limit: str = Query("50", description="Page size 1–100; default 50."),
    offset: str = Query("0", description="Nonnegative offset; default 0."),
):
    require_election(electionId)
    data = service.results(regionCode=code(regionCode, "regionCode", r"[1-9]"),
                           districtCode=code(districtCode, "districtCode", r"[0-9]{3}"),
                           municipalityCode=code(municipalityCode, "municipalityCode", r"[0-9]{6}"),
                           limit=integer(limit, "limit", 1, 100), offset=integer(offset, "offset", 0, 2**31 - 1))
    return envelope(data, response)


@router.get("/{electionId}/parties", summary="List national political-subject results",
            description=NOTICE + " All 25 subjects in numeric election-local party-number order. "
            "Party numbers are strings scoped to NRSR2023, not global party identifiers. "
            "seats=null preserves a blank source mandate cell; populated seats sum to 150. No pagination. "
            "Unknown elections return 404. This is not municipality-party or candidate results.",
            **contract("list_election_parties", SuccessResponse[list[ElectionParty]], 404, 429))
def list_election_parties(electionId: str, response: Response):
    require_election(electionId)
    return envelope(service.load_dataset().parties, response)
