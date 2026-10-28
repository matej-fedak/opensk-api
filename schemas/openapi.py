"""Small shared documentation helpers; never change request parsing.

Parameter schema refinements happen on the generated document only, so manual
400 validation remains manual and existing FastAPI 422 paths remain unchanged.
"""

import json
from pathlib import Path

from schemas.common import ErrorResponse


EXAMPLES = json.loads(Path(__file__).with_name("examples.json").read_text(encoding="utf-8"))


def error_example(operation_id, status):
    captured = EXAMPLES["__errors__"].get(operation_id, {}).get(str(status))
    if captured:
        return captured
    # Middleware/availability examples, exact strings from the existing handlers.
    code, message, message_sk = {
        429: ("RATE_LIMITED", "Rate limit exceeded. Retry after the number of seconds in Retry-After.",
              "Prekročený limit požiadaviek. Skúste znova po počte sekúnd v Retry-After."),
        503: ("DATASET_UNAVAILABLE", "Local company dataset is not available",
              "Lokálny dataset spoločností nie je k dispozícii"),
    }[status]
    return {"data": None, "metadata": {"source": "OpenSK API", "lastUpdated": None, "version": "v1"},
            "error": {"code": code, "message": message, "messageSk": message_sk}}


def contract(operation_id, model, *statuses, exclude_unset=True):
    responses = {200: {"content": {"application/json": {"examples": {
        "snapshot": {"summary": "Local snapshot example (long arrays shortened)", "value": EXAMPLES[operation_id]}
    }}}}}
    error_info = {
        400: "INVALID_FORMAT: invalid input; application validation (not FastAPI 422).",
        404: "NOT_FOUND: absent from the local snapshot, not a universal validity decision.",
        422: "VALIDATION_ERROR: framework integer/path validation, wrapped in the standard OpenSK envelope.",
        429: "RATE_LIMITED: 100 requests / 60 seconds / client IP when enabled; per-process limit. Health is exempt.",
        503: "DATASET_UNAVAILABLE: local company dataset unavailable.",
    }
    if operation_id in {"check_business_day", "add_business_days", "count_business_days"}:
        error_info[400] = "INVALID_FORMAT for missing/malformed/out-of-bounds input; UNSUPPORTED_YEAR outside verified holiday years."
    if operation_id in {"get_exchange_rates_latest", "get_exchange_rates_by_date"}:
        error_info[400] = "INVALID_FORMAT for malformed date/currency; UNSUPPORTED_CURRENCY for EUR or codes absent from snapshot history."
        error_info[404] = "RATE_NOT_AVAILABLE: currency exists historically but not on this publication date."
        if operation_id == "get_exchange_rates_by_date":
            error_info[404] += " RATE_DATE_NOT_FOUND: no exact publication date; no nearest-date fallback."
    for status in statuses:
        description = error_info[status]
        responses[status] = {
            "model": ErrorResponse,
            "description": description,
            "content": {"application/json": {"example": error_example(operation_id, status)}},
        }
        if status == 429:
            responses[status]["headers"] = {
                name: {"description": description, "schema": {"type": "integer"}}
                for name, description in {
                    "Retry-After": "Seconds until retry is allowed.",
                    "X-RateLimit-Limit": "Window budget (100).",
                    "X-RateLimit-Remaining": "Remaining requests (0 on rejection).",
                    "X-RateLimit-Reset": "Unix epoch seconds when the window resets.",
                }.items()
            }
    return {"operation_id": operation_id, "response_model": model,
            "response_model_exclude_unset": exclude_unset, "responses": responses}


def document_parameters(schema):
    """Refine wire formats without feeding constraints into FastAPI validators."""
    # These FastAPI defaults describe a detail-list body that our exception
    # handler never emits. All actual 422 routes use ErrorResponse instead.
    for name in ("HTTPValidationError", "ValidationError"):
        schema["components"]["schemas"].pop(name, None)
    shared = {
        "regionCode": ("Exact region code SK plus three digits; spaces removed, case-sensitive.", "SK010"),
        "districtCode": ("Exact district code SK plus four OR five digits (e.g. SK03111); spaces removed, case-sensitive.", "SK0101"),
        "municipalityCode": ("Exact six-digit administrative municipality code; spaces removed.", "528595"),
        "municipalityName": ("Municipality-name substring; case- and diacritic-insensitive.", "Bratislava"),
        "districtName": ("District-name substring; case- and diacritic-insensitive.", "Bratislava"),
        "regionName": ("Region-name substring; case- and diacritic-insensitive.", "Bratislavsky"),
        "deliveryPost": ("Delivery-post substring; case- and diacritic-insensitive.", "Zilina"),
        "currency": ("Optional three-letter ISO 4217 code, trimmed and case-insensitive. EUR is the base, not a quoted currency; unsupported codes return 400.", "USD"),
        "include": ("Optional expansion; only the exact case-sensitive value geography is accepted.", "geography"),
        "hasGeography": ("Presence of any geography code. Trimmed, case-insensitive true/1/yes/on or false/0/no/off.", "true"),
        "noticeType": ("Exact TED notice type after trimming, case-insensitive; unknown values return an empty collection.", "can-standard"),
        "year": ("Publication year 2000–2100; malformed/out-of-range input retains framework 422.", 2026),
        "ico": ("Eight-digit IČO; spaces removed. Seed lookup only, not a live register.", "50158635"),
        "iban": ("IBAN text, normalized to uppercase without spaces; invalid checksums return 200 with valid=false, not an application error. Synthetic checksum-valid example, not a payment instruction.", "SK5409000000000000000001"),
        "id": ("Exact TED publication number from the partial local snapshot.", "670654-2026"),
        "source_id": ("Case-sensitive registry ID, starting with a letter and containing only ASCII letters/digits.", "psc"),
        "status": ("Exact case-sensitive source status: production, seed, historical, research or blocked.", "historical"),
        "coverage": ("Exact case-sensitive source coverage: complete, partial or seed.", "partial"),
        "schoolKind": ("Exact case-sensitive source school-kind abbreviation; blank value ignored.", "GYM"),
        "schoolType": ("Exact case-sensitive source school-type abbreviation; blank value ignored.", "GYM"),
        "founderOwnershipType": ("Exact case-sensitive founder ownership label; accents significant, blank ignored.", "cirkevná"),
        "founderType": ("Exact case-sensitive founder type label; accents significant, blank ignored.", "cirkev, náboženská spoločnosť"),
        "programmeCode": ("Exact six-digit programme code, trimmed; AND with other filters.", "401000"),
        "callCode": ("Exact case-sensitive source call code, trimmed, printable, 1–256 characters, excluding < and >.", "PSK-MIRRI-619-2024-ITI-EFRR"),
        "beneficiaryIco": ("Exact eight-digit beneficiary IČO after privacy review; trimmed.", "00306185"),
        "inImplementation": ("Trimmed case-insensitive true or false; AND with other filters.", "true"),
        "completed": ("Trimmed case-insensitive true or false; AND with other filters.", "false"),
        "nuts": ("Exact verified implementation NUTS reference: two uppercase letters followed by zero to three uppercase letters/digits; trimmed, not inferred from beneficiary seat.", "SK023"),
        "projectCode": ("Exact official project code: ten uppercase letters/digits; trimmed, case-sensitive.", "401000B287"),
        "days": ("Required signed integer -366 through 366 (no leading +); trimmed. Zero returns the start date unchanged, including weekends.", "1"),
    }
    for path, item in schema["paths"].items():
        operation = item["get"]
        if path != "/v1/health":
            headers = {
                "ETag": {"description": "Strong validator derived from exact response-body SHA-256 (first 32 hex characters).", "schema": {"type": "string"}},
                "Cache-Control": {"description": "Existing endpoint cache policy; dataset freshness is not advanced by a request.", "schema": {"type": "string"}},
            }
            if path != "/":
                headers["Last-Modified"] = {"description": "Dataset snapshot freshness, not request time.", "schema": {"type": "string"}}
            operation["responses"]["200"]["headers"] = headers
            operation["responses"]["304"] = {"description": "Unchanged conditional representation; empty body. Conditional requests still consume rate-limit budget.", "headers": headers}
        # FastAPI encodes OpenAPI with exclude_none=True, which would strip
        # required nulls even inside literal example payloads. Restore only the
        # captured example values after generation, not schema nullability.
        operation["responses"]["200"]["content"]["application/json"]["examples"]["snapshot"]["value"] = EXAMPLES[operation["operationId"]]
        if operation["operationId"] == "get_psc":
            operation["responses"]["200"]["content"]["application/json"]["examples"]["geography"] = {
                "summary": "01001 with include=geography (local resolution per flat match)",
                "value": EXAMPLES["__psc_geography__"],
            }
        for status, response in operation["responses"].items():
            if status in {"400", "404", "429", "503"} or (status == "422" and path in {"/v1/holidays/{year}", "/v1/procurement-notices", "/v1/procurement-notices/search"}):
                response["content"]["application/json"]["example"] = error_example(operation["operationId"], int(status))
        # Auto-generated FastAPI detail schemas are wrong for our handler; only
        # genuine framework integer-validation paths advertise a typed 422.
        if path not in {"/v1/holidays/{year}", "/v1/procurement-notices", "/v1/procurement-notices/search"}:
            operation["responses"].pop("422", None)
        for parameter in operation.get("parameters", []):
            name = parameter["name"]
            info = shared.get(name)
            extra = {}
            if name == "psc":
                info = ("Five-digit postal code including leading zeros; spaces removed. Exact local-snapshot lookup/filter, not address validation.", "01001")
            elif name == "code":
                if "/banks" in path:
                    info = ("Four-digit domestic bank code, including leading zeros; spaces removed.", "1100")
                elif "/regions" in path:
                    info = shared["regionCode"]
                elif "/districts" in path:
                    info = shared["districtCode"]
                elif "/municipalities" in path:
                    info = shared["municipalityCode"]
                elif "/phone-areas" in path:
                    info = ("Domestic primary telephone area code: 0 plus one or two digits; spaces removed.", "02")
                else:
                    info = ("Two-letter historical district abbreviation; spaces removed and uppercased (case-insensitive). Not a full plate.", "BA")
            elif name in {"date", "from", "to"}:
                if "/exchange-rates" in path:
                    info = ("Exact calendar/publication date YYYY-MM-DD; no nearest-date fallback. Malformed date returns 400.", "1999-01-04")
                    extra = {"format": "date"}
                else:
                    info = ("Required ISO calendar date (prefer YYYY-MM-DD; Python ISO basic/week-date forms also accepted). Verified years 2024–2030 only. Interval endpoints inclusive, from <= to, at most 366 days apart.", "2026-10-08" if name != "to" else "2026-10-09")
                    parameter["required"] = True
            elif name == "year" and "/holidays" in path:
                info = ("Calendar year; verified statutory holiday coverage 2024–2030 only. Other integers return 404; malformed values retain 422.", 2026)
            elif name == "q":
                if "/sources" in path:
                    info = ("Optional nonempty name/source/ID substring; case-insensitive, accents are not stripped.", "psc")
                elif "/procurement" in path:
                    info = ("Required nonempty substring of ID, title, buyer name or city; case- and diacritic-insensitive.", "Bratislava")
                    parameter["required"] = True
                elif "/psc" in path:
                    info = ("Required query, at least two characters; numeric input is a 2–5 digit PSC prefix (spaces removed); text is a case- and diacritic-insensitive municipality/delivery-post substring.", "01001")
                    parameter["required"] = True
                else:
                    info = ("Required query, at least two characters; case- and diacritic-insensitive substring of " + ("area code, name, municipality name or municipality code." if "/phone" in path else "abbreviation, district name, district code or region code."), "Bratislava" if "/phone" in path else "Trencin")
                    parameter["required"] = True
            elif name in {"limit", "offset"}:
                eu = "/eu-funds" in path
                search = path.endswith("/search")
                default, maximum, minimum = (50, 200, 1) if eu else ((50, 200, 0) if search else (100, 500, 0))
                if name == "offset":
                    default, maximum, minimum = 0, (2**31 - 1 if eu else 10**9), 0
                info = (f"Decimal integer string; default {default}, range {minimum}–{maximum}. " + ("Whitespace trimmed." if eu else "Digits only; zero allowed."), str(default))
                extra = {"default": str(default), "pattern": r"^\s*[0-9]{1,10}\s*$" if eu else "^[0-9]+$"}
            if info is None:
                raise ValueError(f"Undocumented parameter: {path} {name}")
            description, example = info
            parameter["description"] = description
            parameter["example"] = example
            parameter["schema"].update(extra)
            enums = {
                "include": ["geography"],
                "status": ["production", "seed", "historical", "research", "blocked"],
                "coverage": ["complete", "partial", "seed"],
            }
            if name in enums:
                parameter["schema"]["enum"] = enums[name] + [None]
