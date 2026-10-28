from datetime import UTC, datetime

from fastapi import APIRouter, Response

from schemas.common import NO_STORE_CACHE_CONTROL, success_response
from schemas.common import SuccessResponse
from schemas.meta import Health
from schemas.openapi import contract


router = APIRouter(prefix="/health", tags=["health"])


@router.get("", summary="Service health", description="Operational liveness only: status and current UTC timestamp, not dataset availability. Always no-store, no conditional caching and exempt from rate limiting.", **contract("get_health", SuccessResponse[Health]))
def health(response: Response) -> dict[str, object]:
    now = datetime.now(UTC)
    response.headers["Cache-Control"] = NO_STORE_CACHE_CONTROL
    return success_response(
        data={
            "status": "ok",
            "timestamp": now.isoformat(),
        },
        source="OpenSK API",
        last_updated=now.date().isoformat(),
    )
