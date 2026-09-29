from __future__ import annotations

import json
from pathlib import Path

from scripts.import_procurement_notices import (
    build_procurement_notices_payload,
    normalize_procurement_notice_record,
    run_import,
)


def _sample_notice(**overrides):
    notice = {
        "publication-number": "669481-2026",
        "publication-date": "2026-09-29+02:00",
        "dispatch-date": "2026-09-26+02:00",
        "notice-type": "can-standard",
        "notice-title": {"slk": "Slovenské oznámenie", "eng": "Slovak notice"},
        "buyer-name": {"slk": ["Slovenský verejný obstarávateľ"]},
        "buyer-country": ["SVK"],
        "place-of-performance-city-proc": ["Bratislava"],
        "place-of-performance-post-code-proc": ["811 01"],
        "place-of-performance-country-proc": ["SVK"],
        "deadline-date-lot": ["2026-10-15+02:00"],
        "links": {"xml": {"MUL": "https://ted.europa.eu/en/notice/669481-2026/xml"}},
    }
    notice.update(overrides)
    return notice


def test_normalize_procurement_notice_record_prefers_slovak_and_normalizes_values() -> None:
    record = normalize_procurement_notice_record(_sample_notice(), row_number=1)

    assert record["id"] == "669481-2026"
    assert record["title"] == "Slovenské oznámenie"
    assert record["publicationDate"] == "2026-09-29"
    assert record["dispatchDate"] == "2026-09-26"
    assert record["buyerNames"] == ["Slovenský verejný obstarávateľ"]
    assert record["buyerCountry"] == "SK"
    assert record["placeOfPerformance"] == {"city": "Bratislava", "postalCode": "81101", "country": "SK"}
    assert record["tenderDeadline"] == "2026-10-15"
    assert record["municipalityCode"] is None


def test_procurement_notice_import_payload_marks_partial_metadata_and_deduplicates() -> None:
    notices = [_sample_notice(), _sample_notice()]

    payload, result = build_procurement_notices_payload(notices, total_notice_count=74693)

    assert result.imported_records == 1
    assert result.duplicate_records == 1
    assert payload["metadata"]["coverage"] == "partial"
    assert payload["metadata"]["coverageDecision"] == "TED_PARTIAL"
    assert payload["metadata"]["acquisitionDecision"] == "PRODUCTION_IMPORT_APPROVED"
    assert payload["metadata"]["totalNoticesAtSource"] == 74693
    assert payload["procurementNotices"][0]["placeOfPerformance"]["postalCode"] == "81101"


def test_procurement_notice_import_rejects_forbidden_source_fields() -> None:
    payload, result = build_procurement_notices_payload([_sample_notice(contactPerson="Jane")], total_notice_count=1)

    assert result.imported_records == 1
    assert result.errors
    assert any("contactPerson" in error for error in result.errors)


def test_procurement_notice_import_rejects_wrong_country() -> None:
    notice = _sample_notice(**{"buyer-country": ["CZE"]})

    payload, result = build_procurement_notices_payload([notice], total_notice_count=1)

    assert result.imported_records == 0
    assert result.errors
    assert any("buyer country" in error for error in result.errors)


def test_procurement_notice_importer_validates_and_writes(tmp_path: Path) -> None:
    input_path = tmp_path / "ted.json"
    output_path = tmp_path / "procurement_notices.json"
    input_path.write_text(json.dumps({"notices": [_sample_notice()], "totalNoticeCount": 74693}, ensure_ascii=False), encoding="utf-8")

    result = run_import(input_path=input_path, output_path=output_path, write=True)

    assert result.ok
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["metadata"]["lastUpdated"] == "2026-09-29"
    assert payload["procurementNotices"][0]["id"] == "669481-2026"
