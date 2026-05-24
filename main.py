from datetime import date

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.health import router as health_router
from routers.holidays import router as holidays_router
from routers.psc import router as psc_router
from schemas.common import success_response


app = FastAPI(
    title="OpenSK API",
    description="OpenSK API is a small FastAPI service that exposes Slovak public data through a consistent JSON envelope.",
    version="0.1.0",
    contact={"name": "OpenSK API", "url": "https://github.com/matej-fedak/opensk-api"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    openapi_tags=[
        {"name": "health", "description": "Basic service health checks."},
        {"name": "holidays", "description": "Static Slovak public holiday data."},
        {"name": "psc", "description": "Static Slovak postal code lookups."},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
    allow_credentials=False,
)


@app.get("/", summary="Project info", description="Returns basic project metadata and the documentation URL.")
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
app.include_router(psc_router, prefix="/v1")
