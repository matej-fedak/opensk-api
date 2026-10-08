from datetime import UTC, datetime

from fastapi import APIRouter, Response

from schemas.common import NO_STORE_CACHE_CONTROL, success_response


router = APIRouter(prefix="/health", tags=["health"])


@router.get("", summary="Service health", description="Returns a simple health check payload with a UTC timestamp.")
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
