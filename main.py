from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from starlette.exceptions import HTTPException as StarletteHTTPException

from routers.banks import router as banks_router
from routers.business_days import router as business_days_router
from routers.companies import router as companies_router
from routers.districts import router as districts_router
from routers.exchange_rates import router as exchange_rates_router
from routers.eu_funds import router as eu_funds_router
from routers.elections import router as elections_router
from routers.health import router as health_router
from routers.holidays import router as holidays_router
from routers.iban import router as iban_router
from routers.municipalities import router as municipalities_router
from routers.phone_areas import router as phone_areas_router
from routers.procurement_notices import router as procurement_notices_router
from routers.psc import router as psc_router
from routers.regions import router as regions_router
from routers.school_facility_counts import router as school_facility_counts_router
from routers.sources import router as sources_router
from routers.vehicle_registration_codes import router as vehicle_registration_codes_router
from schemas.common import API_SOURCE, META_CACHE_CONTROL, error_detail, error_response, success_response
from schemas.common import SuccessResponse
from schemas.meta import ProjectInfo
from schemas.openapi import contract, document_parameters
from services.http_cache import ConditionalCachingMiddleware
from services.rate_limit import RateLimitMiddleware
from version import PROJECT_VERSION


app = FastAPI(
    title="OpenSK API",
    description="One consistent developer interface to Slovakia's fragmented public data. Local materialized snapshots only; coverage and reuse conditions vary by source. Pre-1.0: review /v1/sources and dataset limitations. Project SemVer is independent of /v1 and metadata.version=v1. Quickstart: https://github.com/matej-fedak/opensk-api/blob/main/docs/quickstart.md",
    version=PROJECT_VERSION,
    contact={"name": "OpenSK API", "url": "https://github.com/matej-fedak/opensk-api"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    openapi_tags=[
        {"name": "meta", "description": "Project metadata."},
        {"name": "health", "description": "Basic service health checks."},
        {"name": "sources", "description": "Curated public source and licence provenance for the served datasets."},
        {"name": "business-days", "description": "Monday–Friday minus statutory Slovak days of rest from the local calendar; working holidays remain business days."},
        {"name": "banks", "description": "Static Slovak bank data and lookup endpoints."},
        {"name": "iban", "description": "IBAN validation and bank resolution."},
        {"name": "holidays", "description": "Statutory Slovak holiday calendar, including working holidays with separate state-holiday and day-of-rest flags."},
        {"name": "regions", "description": "Static Slovak regions dataset."},
        {"name": "districts", "description": "Complete Slovak districts dataset materialized from PortalVS / IS Číselníky successor geography data."},
        {"name": "municipalities", "description": "Static Slovak municipalities dataset."},
        {"name": "psc", "description": "Partial historical local PSC lookup; not an address validator or municipality-wide validity guarantee."},
        {"name": "companies", "description": "Local company lookup endpoints backed by the checked-in dataset."},
        {"name": "phone-areas", "description": "Static Slovak primary telephone area lookups."},
        {"name": "vehicle-registration-codes", "description": "Static legacy Slovak vehicle registration district abbreviations; not a current plate lookup."},
        {"name": "school-facility-counts", "description": "Static MŠVVaM school facility aggregate counts; not an institution-level school directory."},
        {"name": "procurement-notices", "description": "Static partial TED Slovak-buyer procurement notice snapshot; not the complete national ÚVO register."},
        {"name": "exchange-rates", "description": "Materialized ECB euro foreign exchange reference rates (EUR base, exact publication dates, informational use only)."},
        {"name": "eu-funds", "description": "Materialized ITMS21+ 2021–2027 project references for positively reviewed legal-entity beneficiaries only; titles and privacy-unsafe projects excluded."},
        {"name": "elections", "description": "NRSR2023 aggregate historical unit summaries and national party results; manual acquisition, CC BY 4.0, no candidate/person, precinct or municipality-party records."},
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
        last_updated=None,
    )
    return JSONResponse(status_code=exc.status_code, content=payload, headers=exc.headers)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    payload = error_response(
        error=error_detail("VALIDATION_ERROR", "Request validation failed", "Validácia požiadavky zlyhala"),
        source=API_SOURCE,
        last_updated=None,
    )
    return JSONResponse(status_code=422, content=payload)


# Middleware order (outermost last): CORS -> rate limiter -> conditional
# caching -> application. CORS wraps 429s for browsers, and rejected
# requests never reach routing or ETag hashing.
app.add_middleware(ConditionalCachingMiddleware)
app.add_middleware(RateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
    allow_credentials=False,
    expose_headers=[
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
        "Retry-After",
    ],
)


@app.get("/", tags=["meta"], summary="Project info", description="Returns project SemVer, API namespace version, and the documentation URL. Project version is not the v1 contract version.", **contract("get_root", SuccessResponse[ProjectInfo], 429))
def root(response: Response) -> dict[str, object]:
    response.headers["Cache-Control"] = META_CACHE_CONTROL
    return success_response(
        data={
            "name": app.title,
            "version": app.version,
            "apiVersion": "v1",
            "apiNamespace": "/v1",
            "docs_url": app.docs_url or "/docs",
        },
        source=API_SOURCE,
        last_updated=None,
    )


app.include_router(health_router, prefix="/v1")
app.include_router(banks_router, prefix="/v1")
app.include_router(iban_router, prefix="/v1")
app.include_router(holidays_router, prefix="/v1")
app.include_router(psc_router, prefix="/v1")
app.include_router(companies_router, prefix="/v1")
app.include_router(regions_router, prefix="/v1")
app.include_router(districts_router, prefix="/v1")
app.include_router(municipalities_router, prefix="/v1")
app.include_router(phone_areas_router, prefix="/v1")
app.include_router(vehicle_registration_codes_router, prefix="/v1")
app.include_router(school_facility_counts_router, prefix="/v1")
app.include_router(procurement_notices_router, prefix="/v1")
app.include_router(sources_router, prefix="/v1")
app.include_router(business_days_router, prefix="/v1")
app.include_router(exchange_rates_router, prefix="/v1")
app.include_router(eu_funds_router, prefix="/v1")
app.include_router(elections_router, prefix="/v1")


def public_openapi():
    if app.openapi_schema is None:
        schema = get_openapi(title=app.title, version=app.version, description=app.description,
                             routes=app.routes, tags=app.openapi_tags, contact=app.contact,
                             license_info=app.license_info)
        document_parameters(schema)
        app.openapi_schema = schema
    return app.openapi_schema


app.openapi = public_openapi
