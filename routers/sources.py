from fastapi import APIRouter, HTTPException, Query, Response

from schemas.common import API_SOURCE, SOURCES_LAST_UPDATED, STATIC_CACHE_CONTROL, error_detail
from schemas.sources import ResponseMetadata, SourceDetailResponse, SourceListResponse
from services.sources_service import (
    SourceCatalogueInvalidFormatError,
    SourceCatalogueNotFoundError,
    get_source,
    list_sources,
)


router = APIRouter(prefix="/sources", tags=["sources"])

_SOURCE_SOURCE = f"{API_SOURCE} curated source catalogue"

ALLOWED_STATUSES = {"production", "seed", "historical", "research", "blocked"}
ALLOWED_COVERAGES = {"complete", "partial", "seed"}


def _invalid_format(message: str, message_sk: str) -> HTTPException:
    return HTTPException(
        status_code=400,
        detail=error_detail(code="INVALID_FORMAT", message=message, message_sk=message_sk),
        headers={"Cache-Control": STATIC_CACHE_CONTROL},
    )


@router.get(
    "",
    summary="List public source catalogue",
    description="Returns the curated public provenance catalogue for served and researched datasets.",
    response_model=SourceListResponse,
)
def list_sources_endpoint(
    response: Response,
    status: str | None = Query(default=None, description="Optional public status filter."),
    coverage: str | None = Query(default=None, description="Optional coverage filter."),
    q: str | None = Query(default=None, description="Optional name/source substring filter."),
) -> SourceListResponse:
    if status is not None and status not in ALLOWED_STATUSES:
        raise _invalid_format(
            f"status must be one of {sorted(ALLOWED_STATUSES)}",
            f"Parameter status musí byť jeden z {sorted(ALLOWED_STATUSES)}",
        )
    if coverage is not None and coverage not in ALLOWED_COVERAGES:
        raise _invalid_format(
            f"coverage must be one of {sorted(ALLOWED_COVERAGES)}",
            f"Parameter coverage musí byť jeden z {sorted(ALLOWED_COVERAGES)}",
        )
    if q is not None and not q.strip():
        raise _invalid_format("q must not be empty", "Parameter q nesmie byť prázdny")

    entries = list_sources(status=status, coverage=coverage, q=q)

    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return SourceListResponse(
        data=entries,
        metadata=ResponseMetadata(source=_SOURCE_SOURCE, lastUpdated=SOURCES_LAST_UPDATED, version="v1"),
        error=None,
    )


@router.get(
    "/{source_id}",
    summary="Source catalogue entry",
    description="Returns one curated public source provenance entry by its stable registry id.",
    response_model=SourceDetailResponse,
)
def get_source_endpoint(source_id: str, response: Response) -> SourceDetailResponse:
    try:
        entry = get_source(source_id)
    except SourceCatalogueInvalidFormatError:
        raise _invalid_format(
            "source id must start with a letter and contain only letters and digits",
            "Identifikátor zdroja musí začínať písmenom a obsahovať len písmená a číslice",
        )
    except SourceCatalogueNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=error_detail(
                code="NOT_FOUND",
                message=f"No source catalogue entry available for {source_id}",
                message_sk=f"Pre zdroj {source_id} nie sú dostupné údaje",
            ),
            headers={"Cache-Control": STATIC_CACHE_CONTROL},
        )

    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return SourceDetailResponse(
        data=entry,
        metadata=ResponseMetadata(source=_SOURCE_SOURCE, lastUpdated=SOURCES_LAST_UPDATED, version="v1"),
        error=None,
    )
