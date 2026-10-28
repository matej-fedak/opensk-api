"""Capture actual OpenAPI/runtime evidence; never fetch or write production data.

Run from the repository root before annotation changes. Large raw evidence stays
in the explicitly supplied private output directory, not in Git.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from main import app


REQUESTS = {
    "/": "/",
    "/v1/health": "/v1/health",
    "/v1/banks": "/v1/banks",
    "/v1/banks/{code}": "/v1/banks/1100",
    "/v1/iban/validate/{iban}": "/v1/iban/validate/SK3109000000000000000001",
    "/v1/holidays/{year}": "/v1/holidays/2026",
    "/v1/psc": "/v1/psc?psc=01001&limit=1",
    "/v1/psc/search": "/v1/psc/search?q=01001&limit=1",
    "/v1/psc/stats": "/v1/psc/stats",
    "/v1/psc/{psc}": "/v1/psc/01001",
    "/v1/companies/{ico}": "/v1/companies/50158635",
    "/v1/ico/{ico}": "/v1/ico/50158635",
    "/v1/regions": "/v1/regions",
    "/v1/regions/{code}": "/v1/regions/SK010",
    "/v1/districts": "/v1/districts?regionCode=SK010",
    "/v1/districts/{code}": "/v1/districts/SK0101",
    "/v1/municipalities": "/v1/municipalities?districtCode=SK0101",
    "/v1/municipalities/{code}": "/v1/municipalities/528595",
    "/v1/phone-areas": "/v1/phone-areas?limit=1",
    "/v1/phone-areas/search": "/v1/phone-areas/search?q=Bratislava&limit=1",
    "/v1/phone-areas/{code}": "/v1/phone-areas/02",
    "/v1/vehicle-registration-codes": "/v1/vehicle-registration-codes?limit=1",
    "/v1/vehicle-registration-codes/search": "/v1/vehicle-registration-codes/search?q=Trencin&limit=1",
    "/v1/vehicle-registration-codes/{code}": "/v1/vehicle-registration-codes/BA",
    "/v1/school-facility-counts": "/v1/school-facility-counts?limit=1",
    "/v1/school-facility-counts/stats": "/v1/school-facility-counts/stats",
    "/v1/procurement-notices": "/v1/procurement-notices?limit=1",
    "/v1/procurement-notices/search": "/v1/procurement-notices/search?q=Bratislava&limit=1",
    "/v1/procurement-notices/stats": "/v1/procurement-notices/stats",
    "/v1/procurement-notices/{id}": "/v1/procurement-notices/670654-2026",
    "/v1/sources": "/v1/sources?status=historical",
    "/v1/sources/{source_id}": "/v1/sources/psc",
    "/v1/business-days/check": "/v1/business-days/check?date=2026-10-08",
    "/v1/business-days/add": "/v1/business-days/add?date=2026-10-08&days=1",
    "/v1/business-days/between": "/v1/business-days/between?from=2026-10-08&to=2026-10-09",
    "/v1/exchange-rates/latest": "/v1/exchange-rates/latest?currency=USD",
    "/v1/exchange-rates/{date}": "/v1/exchange-rates/1999-01-04?currency=USD",
    "/v1/eu-funds/projects": "/v1/eu-funds/projects?limit=1",
    "/v1/eu-funds/projects/{projectCode}": "/v1/eu-funds/projects/401000B287",
}

# Reviewed against route/service branches, not inferred from HTTP status lists.
APPLICATION_ERRORS = {
    "/v1/banks/{code}": [400, 404], "/v1/holidays/{year}": [404, 422],
    "/v1/psc": [400], "/v1/psc/search": [400], "/v1/psc/{psc}": [400, 404],
    "/v1/companies/{ico}": [400, 404, 503], "/v1/ico/{ico}": [400, 404, 503],
    "/v1/regions/{code}": [400, 404], "/v1/districts": [400, 404],
    "/v1/districts/{code}": [400, 404], "/v1/municipalities": [400, 404],
    "/v1/municipalities/{code}": [400, 404], "/v1/phone-areas": [400],
    "/v1/phone-areas/search": [400], "/v1/phone-areas/{code}": [400, 404],
    "/v1/vehicle-registration-codes": [400], "/v1/vehicle-registration-codes/search": [400],
    "/v1/vehicle-registration-codes/{code}": [400, 404], "/v1/school-facility-counts": [400],
    "/v1/procurement-notices": [400, 422], "/v1/procurement-notices/search": [400, 422],
    "/v1/procurement-notices/{id}": [404], "/v1/sources": [400],
    "/v1/sources/{source_id}": [400, 404], "/v1/business-days/check": [400],
    "/v1/business-days/add": [400], "/v1/business-days/between": [400],
    "/v1/exchange-rates/latest": [400, 404], "/v1/exchange-rates/{date}": [400, 404],
    "/v1/eu-funds/projects": [400], "/v1/eu-funds/projects/{projectCode}": [400, 404],
}


def baseline_report(schema, evidence, hashes):
    lines = [
        "# OpenAPI contract audit — 0.23.12", "",
        "## Before implementation (0.23.11)", "",
        "Base: `500d41824c211060ad77bc8a11b8a750b1966c50`. Captured before route annotations",
        "or PSC implementation changed, using actual `app.openapi()` and TestClient for every GET.",
        "Reproduce capture: `python scripts/audit_openapi_contract.py --output <private-directory>`.",
        "Large raw OpenAPI/runtime bodies are private evidence; compact body digests are committed",
        "in `tests/fixtures/public-contract-baseline.json`. Health clock and root SemVer are normalized",
        "only for comparisons; no other fields or nulls are removed.", "",
        "**39 GET operations; 9 typed success contracts, 30 generic `dict[str, object]` surfaces.**",
        "The latter all publish `additionalProperties: true`, not a discoverable envelope/data model.",
        "**0 explicit stable operation IDs; 0 response examples; 0 documented application errors.**",
        "All 39 have summaries/descriptions/tags, but descriptions often omit scope and parameters",
        "omit examples, formats, parser defaults and limits. FastAPI advertises its default 422",
        "detail schema on parameterized routes even though the application returns an OpenSK envelope.", "",
        "Required/nullability issues: generic contracts cannot express required envelope fields,",
        "nullable metadata.lastUpdated (root/errors), nullable PSC geography/codes/validTo, phone",
        "links, company address/date fields or procurement deadlines. Existing source models mark",
        "some nullable fields optional although current responses include them. Bank additive provenance",
        "and historical array/object/page variations must remain. Query strings stay strings where",
        "manual parsing deliberately produces 400; making them validated ints/enums would change behavior.", "",
        "### Per-operation inventory", "",
        "All entries below are GET. `G` = generic object/additionalProperties; `$ref` = existing typed",
        "contract. No operation has response examples. 429 applies to every operation except health",
        "when the existing per-process client-IP limiter is enabled. 422 is genuinely used for the",
        "holiday integer path and procurement integer year filters; other listed 400s are manual.", "",
    ]
    for path, record in evidence.items():
        operation = schema["paths"][path]["get"]
        success = operation["responses"]["200"]["content"]["application/json"]["schema"]
        errors = APPLICATION_ERRORS.get(path, []) + ([] if path == "/v1/health" else [429])
        lines += [f"#### GET `{path}`", "",
                  f"- Current ID: `{operation['operationId']}`; tag: `{', '.join(operation['tags'])}`.",
                  f"- Summary: {operation['summary']}",
                  f"- Description: {operation['description']}",
                  f"- Success: `{success.get('$ref', 'G: object / additionalProperties=true')}`.",
                  f"- Documented statuses: {', '.join(operation['responses'])}; actual applicable application statuses: {', '.join(map(str, errors)) or 'none'}.",
                  f"- Runtime request: `{record['url']}`; `data` shape: `{shape(record['body']['data'])}`.",
                  "- Parameters (actual OpenAPI; required/default/nullable captured literally):"]
        for parameter in operation.get("parameters", []):
            lines.append(f"  - `{parameter['in']} {parameter['name']}` required={parameter['required']}: `{json.dumps(parameter['schema'], ensure_ascii=False)}`")
        if not operation.get("parameters"):
            lines.append("  - none")
        limitation = "Not explicitly discoverable in operation description."
        if any(word in operation["description"].lower() for word in ("partial", "historical", "aggregate", "seed", "snapshot", "privacy")):
            limitation = "Some scope wording is present; see exact description above."
        lines += [f"- Limitations: {limitation} Examples: none.", ""]
    lines += ["## Production freeze baseline", "", "Working-checkout SHA-256 (Windows bytes; final must match in this checkout).",
              "Git/LF comparison in tests normalizes checkout line endings, not dataset contents.", "",
              "| File | Before SHA-256 |", "| --- | --- |"]
    lines += [f"| data/{name} | `{sha}` |" for name, sha in hashes.items()]
    return "\n".join(lines) + "\n"


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True).encode()).hexdigest()


def normalized_body(path, body):
    body = json.loads(json.dumps(body))
    if path == "/":
        body["data"]["version"] = "<project-semver>"
    if path == "/v1/health":
        body["data"]["timestamp"] = "<utc-now>"
        body["metadata"]["lastUpdated"] = "<today>"
    return body


def shape(value):
    if isinstance(value, dict):
        return "{" + ", ".join(f"{k}: {shape(v)}" for k, v in value.items()) + "}"
    if isinstance(value, list):
        return "[" + (shape(value[0]) if value else "empty") + "]"
    return "null" if value is None else type(value).__name__


def capture(output):
    output.mkdir(parents=True, exist_ok=True)
    schema = app.openapi()
    assert set(schema["paths"]) == set(REQUESTS)
    client = TestClient(app)
    evidence = {}
    for path, url in REQUESTS.items():
        response = client.get(url)
        assert response.status_code == 200, (url, response.text)
        evidence[path] = {"url": url, "body": response.json(), "headers": {
            k: response.headers[k] for k in ("cache-control", "etag", "last-modified") if k in response.headers
        }}
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path("data").glob("*.json"))}
    for name, value in (("openapi.json", schema), ("runtime.json", evidence), ("data-hashes.json", hashes)):
        (output / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return schema, evidence, hashes


def write_examples(schema, evidence, target):
    """Curate small response examples from checked-in data; no upstream access.

    Explicit invocation only. Never use this to overwrite the pre-change audit.
    Non-paginated arrays are excerpts and are labelled as such in OpenAPI.
    """
    examples = {}
    for path, record in evidence.items():
        body = json.loads(json.dumps(record["body"]))
        if path == "/v1/iban/validate/{iban}":
            # Baseline also exercises an invalid checksum (HTTP
            # 200); the copy-paste success example uses the smoke test's valid
            # synthetic account instead, never a real person's account.
            body = TestClient(app).get("/v1/iban/validate/SK5409000000000000000001").json()
        if isinstance(body["data"], list):
            body["data"] = body["data"][:1]
        if path == "/v1/phone-areas/{code}":
            body["data"]["items"] = body["data"]["items"][:1]
        if path == "/":
            body["data"]["version"] = app.version.removesuffix("-dev")
        examples[schema["paths"][path]["get"]["operationId"]] = body
    client = TestClient(app)
    errors = {}
    for path, url, status, code in json.loads(Path("tests/fixtures/public-error-cases.json").read_bytes()):
        response = client.get(url)
        assert response.status_code == status and response.json()["error"]["code"] == code
        operation_id = schema["paths"][path]["get"]["operationId"]
        errors.setdefault(operation_id, {})[str(status)] = response.json()
    examples["__errors__"] = errors
    examples["__psc_geography__"] = client.get("/v1/psc/01001?include=geography").json()
    target.write_text(json.dumps(examples, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--baseline-report", type=Path, help="Generate the initial audit, before implementation only")
    parser.add_argument("--examples", type=Path, help="Explicitly regenerate curated runtime examples after contract implementation")
    args = parser.parse_args()
    if args.baseline_report and args.baseline_report.exists():
        parser.error("Refusing to overwrite an existing pre-implementation audit")
    schema, evidence, hashes = capture(args.output)
    if args.examples:
        write_examples(schema, evidence, args.examples)
    if args.baseline_report:
        args.baseline_report.write_text(baseline_report(schema, evidence, hashes), encoding="utf-8")
        baseline = {path: {"url": r["url"], "bodySha256": digest(normalized_body(path, r["body"])),
                           "cacheControl": r["headers"].get("cache-control"),
                           "lastModified": r["headers"].get("last-modified")}
                    for path, r in evidence.items()}
        fixture = Path("tests/fixtures/public-contract-baseline.json")
        fixture.parent.mkdir(parents=True, exist_ok=True)
        fixture.write_text(json.dumps(baseline, indent=2) + "\n", encoding="utf-8")
    print(f"Captured {len(evidence)} GET operations / {len(hashes)} production hashes in {args.output}")
