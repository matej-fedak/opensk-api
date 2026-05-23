from fastapi import FastAPI

from routers.holidays import router as holidays_router


app = FastAPI(title="OpenSK API", version="0.1.0")


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": app.title,
        "version": app.version,
        "docs_url": app.docs_url or "/docs",
    }


app.include_router(holidays_router, prefix="/v1")
