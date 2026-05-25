from datetime import date

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from routers.banks import router as banks_router
from routers.health import router as health_router
from routers.holidays import router as holidays_router
from routers.iban import router as iban_router
from routers.psc import router as psc_router
from schemas.common import API_SOURCE, error_detail, error_response, success_response


app = FastAPI(
    title="OpenSK API",
    description="OpenSK API is a small FastAPI service that exposes Slovak public data through a consistent JSON envelope.",
    version="0.1.1",
    contact={"name": "OpenSK API", "url": "https://github.com/matej-fedak/opensk-api"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    openapi_tags=[
        {"name": "health", "description": "Basic service health checks."},
        {"name": "banks", "description": "Static Slovak bank data and lookup endpoints."},
        {"name": "iban", "description": "IBAN validation and bank resolution."},
        {"name": "holidays", "description": "Static Slovak public holiday data."},
        {"name": "psc", "description": "Static Slovak postal code lookups."},
    ],
)


def _http_error_detail(status_code: int, detail: object) -> dict[str, str]:
    if isinstance(detail, dict):
        code = detail.get("code")
        message = detail.get("message")
        message_sk = detail.get("messageSk")
        if isinstance(code, str) and isinstance(message, str) and isinstance(message_sk, str):
            return detail

    if status_code == 400:
        return error_detail("BAD_REQUEST", str(detail), "Neplatná požiadavka")
    if status_code == 404:
        return error_detail("NOT_FOUND", str(detail), "Nenájdené")
    if status_code == 405:
        return error_detail("METHOD_NOT_ALLOWED", str(detail), "Metóda nie je povolená")
    if status_code == 422:
        return error_detail("VALIDATION_ERROR", "Request validation failed", "Validácia požiadavky zlyhala")

    return error_detail(f"HTTP_{status_code}", str(detail), "Chyba API")


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    payload = error_response(
        error=_http_error_detail(exc.status_code, exc.detail),
        source=API_SOURCE,
        last_updated=date.today().isoformat(),
    )
    return JSONResponse(status_code=exc.status_code, content=payload, headers=exc.headers)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    payload = error_response(
        error=error_detail("VALIDATION_ERROR", "Request validation failed", "Validácia požiadavky zlyhala"),
        source=API_SOURCE,
        last_updated=date.today().isoformat(),
    )
    return JSONResponse(status_code=422, content=payload)

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
        source=API_SOURCE,
        last_updated=date.today().isoformat(),
    )


app.include_router(health_router, prefix="/v1")
app.include_router(banks_router, prefix="/v1")
app.include_router(iban_router, prefix="/v1")
app.include_router(holidays_router, prefix="/v1")
app.include_router(psc_router, prefix="/v1")
