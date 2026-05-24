from datetime import date

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.health import router as health_router
from routers.holidays import router as holidays_router
from schemas.common import success_response


app = FastAPI(title="OpenSK API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
    allow_credentials=False,
)


@app.get("/")
def root() -> dict[str, object]:
    return success_response(
        data={
            "name": app.title,
            "version": app.version,
            "docs_url": app.docs_url or "/docs",
        },
        source="OpenSK API",
        last_updated=date.today().isoformat(),
    )


app.include_router(health_router, prefix="/v1")
app.include_router(holidays_router, prefix="/v1")
