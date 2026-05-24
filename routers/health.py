from datetime import UTC, datetime

from fastapi import APIRouter

from schemas.common import success_response


router = APIRouter(prefix="/health", tags=["health"])


@router.get("", summary="Service health", description="Returns a simple health check payload with a UTC timestamp.")
def health() -> dict[str, object]:
    now = datetime.now(UTC)
    return success_response(
        data={
            "status": "ok",
            "timestamp": now.isoformat(),
        },
        source="OpenSK API",
        last_updated=now.date().isoformat(),
    )
