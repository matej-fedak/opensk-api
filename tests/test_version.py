"""Project version single-sourcing regression tests.

`version.PROJECT_VERSION` is the only authoritative SemVer value. The FastAPI
app, root metadata, and the smoke-test expectations must all derive from it,
while the public `/v1` namespace and envelope `metadata.version == "v1"`
remain independent and unchanged.
"""

from fastapi.testclient import TestClient

from main import app
from scripts import smoke_test
from version import PROJECT_VERSION


client = TestClient(app)


def test_fastapi_app_version_matches_authoritative_source() -> None:
    assert app.version == PROJECT_VERSION


def test_root_reports_authoritative_version_and_unchanged_api_namespace() -> None:
    body = client.get("/").json()
    assert body["data"]["version"] == PROJECT_VERSION
    assert body["data"]["apiVersion"] == "v1"
    assert body["data"]["apiNamespace"] == "/v1"
    assert body["metadata"]["version"] == "v1"


def test_openapi_info_version_matches_authoritative_source() -> None:
    schema = client.get("/openapi.json").json()
    assert schema["info"]["version"] == PROJECT_VERSION


def test_smoke_script_derives_expected_version_from_authoritative_source() -> None:
    assert smoke_test.EXPECTED_PROJECT_VERSION == PROJECT_VERSION
