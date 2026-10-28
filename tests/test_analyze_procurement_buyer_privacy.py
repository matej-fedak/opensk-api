import json

import pytest

from scripts.acquire_procurement_notices import acquire, encoded, PROFILE, PRIVACY_PROFILE, sha
from scripts.analyze_procurement_buyer_privacy import (
    analyze, marker_state, name_count_proxy, safe_gate, schema_evidence, verified_capture,
)


def notice():
    return {"publication-number": "000001-2026", "publication-date": "2026-10-28Z", "buyer-country": ["SVK"]}


@pytest.mark.parametrize("value,state", [
    ([], "missing"), ([True], "trueOnly"), ([False], "falseOnly"),
    ([True, True], "trueOnly"), ([False, False], "falseOnly"), ([False, True], "mixed"),
    ([0], "malformed"), ([1], "malformed"), (["false"], "malformed"),
    (False, "malformed"), (None, "malformed"), ([False, None], "malformed"),
])
def test_strict_boolean_partition(value, state):
    assert marker_state({"buyer-person": value}) == state
    assert marker_state({}) == "missing"


def test_no_positional_join_or_missing_approval():
    row = {**notice(), "buyer-person": [False], "buyer-identifier": ["synthetic"], "buyer-legal-type": ["cga"]}
    assert safe_gate(row) == "excludedAmbiguous"
    assert safe_gate(notice()) == "excludedUnknown"
    assert safe_gate({**row, "buyer-person": [False, True]}) == "excludedExplicitNatural"
    # Equal lengths and apparently institutional codes cannot prove association.
    old = {**notice(), "notice-type": "cn-standard", "buyer-name": {"slk": ["Synthetic organisation"]}}
    report = analyze({"id": old}, {"id": row})
    assert report["candidateA"]["eligible"] == report["candidateBEligible"] == report["candidateCEligible"] == 0
    assert report["actualSingleBuyerCount"] is None
    assert "synthetic" not in json.dumps(report)
    assert "Synthetic organisation" not in json.dumps(report)


def test_name_language_counts_not_identity_or_legal_status():
    assert name_count_proxy({"buyer-name": {"slk": ["X"], "eng": ["X"]}}) == ("one-name-value", 1, 2)
    assert name_count_proxy({"buyer-name": {"slk": ["X", "Y"]}}) == ("multiple-name-values", 2, 2)
    assert schema_evidence({"customization-id": "eforms-sdk-1.13"}) == "eForms-explicit-SDK"
    assert schema_evidence({}) == schema_evidence({"notice-subtype": "16"}) == "generation-unresolved"


def test_join_fail_closed_on_identity_or_date_drift():
    old = {**notice(), "notice-type": "cn-standard"}
    with pytest.raises(ValueError, match="identity"):
        analyze({"a": old}, {"b": notice()})
    with pytest.raises(ValueError, match="drift"):
        analyze({"a": old}, {"a": {**notice(), "publication-date": "2026-10-27Z"}})


def capture(tmp_path, profile=PRIVACY_PROFILE):
    bodies = iter([
        {"notices": [notice()], "totalNoticeCount": 1, "timedOut": False, "iterationNextToken": "token"},
        {"notices": [], "totalNoticeCount": 1, "timedOut": False, "iterationNextToken": "token"},
    ])
    def fetcher(payload, statuses):
        body = next(bodies)
        statuses["200"] = statuses.get("200", 0) + 1
        return encoded(body), body, "application/json"
    acquire(tmp_path, "2026-10-28", profile=profile, fetcher=fetcher, delay=0)
    return tmp_path


def test_verified_capture_checks_profile_hash_and_terminal(tmp_path):
    directory = capture(tmp_path / "capture")
    rows, summary = verified_capture(directory, PRIVACY_PROFILE)
    assert len(rows) == 1 and summary["pageCount"] == 2
    with pytest.raises(ValueError, match="profile"):
        verified_capture(directory, PROFILE)
    (directory / "page-0001.json").write_text("{}")
    with pytest.raises(ValueError, match="hash"):
        verified_capture(directory, PRIVACY_PROFILE)


def test_research_capture_is_not_a_production_import_profile(tmp_path):
    from scripts.import_procurement_notices import load_acquisition
    directory = capture(tmp_path / "metadata")
    with pytest.raises(ValueError, match="profile"):
        load_acquisition(directory)


@pytest.mark.parametrize("fault", ["token", "total", "terminal", "duplicate", "unexpected-field"])
def test_resealed_ledger_cannot_hide_inconsistent_pages(tmp_path, fault):
    directory = capture(tmp_path / fault)
    m = json.loads((directory / "manifest.json").read_bytes())
    page_path = directory / "page-0002.json"
    body = json.loads(page_path.read_bytes())
    if fault == "token":
        m["pages"][1]["requestSha256"] = sha(b"wrong-request")
    elif fault == "total":
        body["totalNoticeCount"] = 2
    elif fault in {"terminal", "duplicate"}:
        body["notices"] = [notice() if fault == "duplicate" else {**notice(), "publication-number": "000002-2026"}]
    else:
        body["notices"] = [{**notice(), "publication-number": "000002-2026", "buyer-email": ["not-retained"]}]
    if fault != "token":
        raw = encoded(body)
        page_path.write_bytes(raw)
        m["pages"][1].update(bytes=len(raw), sha256=sha(raw), rows=len(body["notices"]))
    m["rawBytes"] = sum(p["bytes"] for p in m["pages"])
    m["pagesSha256"] = sha(encoded(m["pages"]))
    (directory / "manifest.json").write_bytes(encoded(m))
    with pytest.raises(ValueError):
        verified_capture(directory, PRIVACY_PROFILE)
