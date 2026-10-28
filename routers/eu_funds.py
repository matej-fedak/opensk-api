import re

from fastapi import APIRouter, HTTPException, Query, Response

from schemas.common import STATIC_CACHE_CONTROL, error_detail
from schemas.eu_funds import DetailResponse, ListData, ListResponse, ResponseMetadata
from schemas.openapi import contract
from services import eu_funds_service as service
from services.eu_funds_policy import LICENCE_NOTICE, NUTS_PATTERN, PROJECT_CODE_PATTERN, SOURCE_NOTICE

router = APIRouter(prefix="/eu-funds/projects", tags=["eu-funds"])
NOTICE = (
    "MIRRI SR / ITMS21+ project references, 2021–2027 only. " + LICENCE_NOTICE + ". "
    "OpenSK transformed/privacy-minimized the source; not an official representation. "
    "Only positively reviewed legal-entity beneficiary projects are exposed; natural-person, "
    "ambiguous/missing/unreviewed forms are wholly excluded. Titles are omitted. "
    "Manual local snapshot, not live; can lag upstream. No ITMS2014+, payment, procurement "
    "or irregularity/receivable surface. contractedTotal is an exact decimal string of "
    "celkovaZazmluvnenaSuma (total contracted amount), not paid funds; the manual does not "
    "separately establish currency, so no EUR claim is made."
)


def invalid(parameter: str):
    return HTTPException(400, detail=error_detail("INVALID_FORMAT", f"Invalid {parameter}",
                                                f"Neplatný parameter {parameter}"),
                         headers={"Cache-Control": STATIC_CACHE_CONTROL})


def integer(value: str, parameter: str, minimum: int, maximum: int):
    value = value.strip()
    if not re.fullmatch(r"[0-9]{1,10}", value) or not minimum <= int(value) <= maximum:
        raise invalid(parameter)
    return int(value)


def optional_code(value: str | None, parameter: str, pattern: str):
    if value is None:
        return None
    value = value.strip()
    if not re.fullmatch(pattern, value):
        raise invalid(parameter)
    return value


def optional_boolean(value: str | None, parameter: str):
    if value is None:
        return None
    value = value.strip().lower()
    if value not in {"true", "false"}:
        raise invalid(parameter)
    return value == "true"


def metadata(response: Response):
    response.headers["Cache-Control"] = STATIC_CACHE_CONTROL
    return ResponseMetadata(source=SOURCE_NOTICE, lastUpdated=service.load_dataset().metadata.snapshotDate)


@router.get("", summary="List privacy-approved ITMS21+ project references", description=NOTICE,
            **contract("list_eu_funds_projects", ListResponse, 400, 429, exclude_unset=False))
def list_projects(
    response: Response,
    limit: str = Query("50", description="Page size 1–200 (default 50)."),
    offset: str = Query("0", description="Nonnegative offset (default 0)."),
    programmeCode: str | None = Query(None, description="Exact six-digit programme code."),
    callCode: str | None = Query(None, description="Exact source call code; case-sensitive, printable, max 256 characters."),
    beneficiaryIco: str | None = Query(None, description="Exact eight-digit IČO after the legal-entity privacy gate."),
    inImplementation: str | None = Query(None, description="true/false, case-insensitive; AND with other filters."),
    completed: str | None = Query(None, description="true/false, case-insensitive; AND with other filters."),
    nuts: str | None = Query(None, description="Exact verified implementation NUTS reference; no seat/geography inference."),
) -> ListResponse:
    if callCode is not None:
        callCode = callCode.strip()
        if not callCode or len(callCode) > 256 or not callCode.isprintable() or any(c in callCode for c in "<>"):
            raise invalid("callCode")
    data = service.list_projects(
        limit=integer(limit, "limit", 1, 200), offset=integer(offset, "offset", 0, 2**31-1),
        programmeCode=optional_code(programmeCode, "programmeCode", r"[0-9]{6}"), callCode=callCode,
        beneficiaryIco=optional_code(beneficiaryIco, "beneficiaryIco", r"[0-9]{8}"),
        inImplementation=optional_boolean(inImplementation, "inImplementation"),
        completed=optional_boolean(completed, "completed"),
        nuts=optional_code(nuts, "nuts", NUTS_PATTERN),
    )
    return ListResponse(data=ListData(**data), metadata=metadata(response))


@router.get("/{projectCode}", summary="Look up an ITMS21+ project by official project code", description=NOTICE,
            **contract("get_eu_funds_project", DetailResponse, 400, 404, 429, exclude_unset=False))
def get_project(projectCode: str, response: Response) -> DetailResponse:
    code = projectCode.strip()
    if not re.fullmatch(PROJECT_CODE_PATTERN, code):
        raise invalid("projectCode")
    project = service.get_project(code)
    if project is None:
        raise HTTPException(404, detail=error_detail("NOT_FOUND", "Project not found", "Projekt sa nenašiel"),
                            headers={"Cache-Control": STATIC_CACHE_CONTROL})
    return DetailResponse(data=project, metadata=metadata(response))
