"""Synthetic complete-acquisition, projection and refresh tests. No HTTP."""

import copy
import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from schemas.eu_funds import Dataset
from scripts import itms21_production as importer


def source_row(code="TEST000001", source_id=1, form="1009321"):
    return {"id": source_id, "href": f"/projekt/id/{source_id}", "kod": code,
            "nazov": "SYNTHETIC OMITTED PROJECT TITLE", "popis": "SYNTHETIC OMITTED DESCRIPTION",
            "prijimatel": {"nazov": "Synthetic public test organization", "ico": "12345678",
                           "pravnaForma": {"kod": form, "nazovSk": "Rozpočtová organizácia"},
                           "dic": "SYNTHETIC PRIVATE TAX VALUE", "adresa": {"ulica": "SYNTHETIC PRIVATE ADDRESS"}},
            "vyzva": {"kod": "CALL-1", "nazovSk": "Synthetic public call",
                      "program": {"kod": "401000", "nazovSk": "Synthetic programme"}},
            "vrealizacii": True, "ukonceny": False, "stav": "Zmluva uzavretá",
            "miestoRealizacie": [{"kodZdroj": "SK010", "nazovSk": "Bratislavský kraj"}],
            "celkovaZazmluvnenaSuma": 12345.5, "updatedAt": 1700000000123}


def capture(directory: Path, rows, page_size=2):
    directory.mkdir()
    pages = []
    for offset in range(0, len(rows), page_size):
        items = rows[offset:offset+page_size]
        raw = json.dumps({"size": len(rows), "offset": offset, "limit": page_size,
                          "results": items}, ensure_ascii=False).encode()
        name = f"page-{len(pages):05d}.json"
        (directory / name).write_bytes(raw)
        pages.append({"file": name, "url": f"{importer.COLLECTION_URL}?offset={offset}&limit={page_size}",
                      "size": len(rows), "offset": offset, "limit": page_size, "rows": len(items),
                      "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                      "retrievedAt": "2026-10-15T10:00:00Z"})
    manifest = {"profile": "itms21-project-list-acquisition-v1", "collectionUrl": importer.COLLECTION_URL,
                "startedAt": "2026-10-15T10:00:00Z", "completedAt": "2026-10-15T10:01:00Z",
                "sourceProjectCount": len(rows), "rowsAcquired": len(rows), "pageSize": page_size,
                "completeAcquisition": True, "pages": pages, "boundaryRecheckSha256": pages[0]["sha256"]}
    path = directory / "manifest.json"
    save_manifest(path, manifest)
    return path


def save_manifest(path, manifest):
    manifest["manifestSha256"] = importer.manifest_digest(manifest)
    path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")


@pytest.fixture
def production_path(tmp_path, monkeypatch):
    target = tmp_path / "eu_funds_projects.json"
    monkeypatch.setattr(importer, "PRODUCTION_OUTPUT", target)
    return target


def test_full_manifest_dry_run_title_free_exact_schema(tmp_path, production_path):
    manifest = capture(tmp_path / "raw", [source_row()])
    result = importer.materialize(manifest)
    assert result.ok, result.errors
    assert not production_path.exists() and not result.wrote_files
    project = result.payload["projects"][0]
    assert "name" not in project and "dates" not in project
    assert project["financials"] == {"contractedTotal": "12345.5"}
    assert project["sourceUpdatedAt"] == "2023-11-14T22:13:20.123Z"
    text = json.dumps(result.payload)
    assert "SYNTHETIC OMITTED" not in text and "SYNTHETIC PRIVATE" not in text
    Dataset.model_validate(result.payload)


@pytest.mark.parametrize("form", ["1009101", "100900000", "1009995", "1009UNKNOWN", None])
def test_unsafe_rows_entirely_excluded_from_production(tmp_path, production_path, form):
    unsafe = source_row("UNSAFE0001", 987654321, form)
    if form is None:
        unsafe["prijimatel"].pop("pravnaForma")
    unsafe.update({"stav": "UNSAFE STATUS", "updatedAt": 1800000000000,
                   "miestoRealizacie": [{"kodZdroj": "UNSAFE GEO"}], "celkovaZazmluvnenaSuma": 99999999.123})
    result = importer.materialize(capture(tmp_path / "raw", [source_row(), unsafe]), write_production=True)
    assert result.ok, result.errors
    assert len(result.payload["projects"]) == 1
    assert result.payload["metadata"]["sourceProjectCount"] == 2
    assert result.payload["metadata"]["privacyExcludedProjectCount"] == 1
    text = production_path.read_text(encoding="utf-8")
    for forbidden in ("UNSAFE0001", "987654321", "UNSAFE STATUS", "UNSAFE GEO", "99999999.123"):
        assert forbidden not in text


@pytest.mark.parametrize("fault", ["incomplete", "size", "gap", "manifest-hash", "page-hash"])
def test_manifest_integrity_required(tmp_path, production_path, fault):
    path = capture(tmp_path / "raw", [source_row(), source_row("TEST000002", 2), source_row("TEST000003", 3)])
    manifest = json.loads(path.read_text())
    if fault == "incomplete":
        manifest["pages"].pop()
    elif fault == "size":
        manifest["pages"][1]["size"] += 1
    elif fault == "gap":
        manifest["pages"][1]["offset"] += 1
    elif fault == "page-hash":
        (path.parent / "page-00000.json").write_bytes(b"changed")
    else:
        manifest["manifestSha256"] = "0" * 64
        path.write_text(json.dumps(manifest))
    if fault != "manifest-hash":
        save_manifest(path, manifest)
    result = importer.materialize(path, write_production=True)
    assert not result.ok and not production_path.exists()


@pytest.mark.parametrize("duplicate", ["code", "id"])
def test_duplicates_rejected_even_with_consistent_hashes(tmp_path, production_path, duplicate):
    second = source_row("TEST000002", 2)
    second["kod" if duplicate == "code" else "id"] = "TEST000001" if duplicate == "code" else 1
    second["href"] = f"/projekt/id/{second['id']}"
    result = importer.materialize(capture(tmp_path / "raw", [source_row(), second]))
    assert not result.ok and "duplicate" in result.errors[0]


def test_production_path_and_determinism(tmp_path, production_path):
    path = capture(tmp_path / "raw", [source_row()])
    assert not importer.materialize(path, write_production=True, output=tmp_path / "other.json").ok
    first = importer.materialize(path, write_production=True)
    assert first.ok, first.errors
    before = production_path.read_bytes()
    second = importer.materialize(path, write_production=True)
    assert second.ok and production_path.read_bytes() == before


def test_removal_guard_and_eligibility_transition_counts(tmp_path, production_path):
    old = capture(tmp_path / "old", [source_row(), source_row("TEST000002", 2, "1009101")])
    assert importer.materialize(old, write_production=True).ok
    before = production_path.read_bytes()
    new = capture(tmp_path / "new", [source_row(form="1009101"), source_row("TEST000002", 2)])
    result = importer.materialize(new, write_production=True, previous_manifest=old)
    assert not result.ok and "acknowledge-removals" in result.errors[0]
    assert production_path.read_bytes() == before
    refresh = result.report["refresh"]
    assert refresh["removedPublishedProjectCodesCount"] == refresh["projectsBecomingPrivacyExcludedCount"] == 1
    assert refresh["projectsBecomingNewlyEligibleCount"] == 1
    assert importer.materialize(new, write_production=True, previous_manifest=old,
                                acknowledge_removals=True).ok


@pytest.mark.parametrize("key,value", [("celkovaZazmluvnenaSuma", -1), ("vrealizacii", "true"),
                                      ("updatedAt", True), ("kod", "BAD/CODE01")])
def test_approved_field_drift_rejected(tmp_path, production_path, key, value):
    row = source_row()
    row[key] = value
    assert not importer.materialize(capture(tmp_path / "raw", [row])).ok


def test_exact_nested_schema_rejects_forbidden_fields(tmp_path, production_path):
    result = importer.materialize(capture(tmp_path / "raw", [source_row()]))
    for target, key in (((), "raw"), (("projects", 0), "title"),
                        (("projects", 0, "beneficiary"), "address"),
                        (("projects", 0, "financials"), "providedNfpEur"),
                        (("metadata",), "excludedProjectCodes")):
        payload = copy.deepcopy(result.payload)
        node = payload
        for part in target:
            node = node[part]
        node[key] = "SYNTHETIC FORBIDDEN VALUE"
        with pytest.raises(ValidationError):
            Dataset.model_validate(payload)


def test_importer_has_no_network_dependency(tmp_path, production_path, monkeypatch):
    import socket
    monkeypatch.setattr(socket, "create_connection", lambda *a, **kw: pytest.fail("network used"))
    assert importer.materialize(capture(tmp_path / "raw", [source_row()])).ok


def test_production_money_keeps_more_than_decimal_context_precision(tmp_path, production_path):
    path = capture(tmp_path / "raw", [source_row()])
    manifest = json.loads(path.read_text())
    page = manifest["pages"][0]
    precise = "12345678901234567890.12345678901234567890123456789"
    raw = (path.parent / page["file"]).read_bytes().replace(b"12345.5", precise.encode())
    (path.parent / page["file"]).write_bytes(raw)
    page.update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    manifest["boundaryRecheckSha256"] = page["sha256"]
    save_manifest(path, manifest)
    result = importer.materialize(path)
    assert result.ok, result.errors
    assert result.payload["projects"][0]["financials"]["contractedTotal"] == precise


def test_leading_ico_digits_are_not_stripped(tmp_path, production_path):
    row = source_row()
    row["prijimatel"]["ico"] = "00123456"
    result = importer.materialize(capture(tmp_path / "raw", [row]))
    assert result.ok and result.payload["projects"][0]["beneficiary"]["ico"] == "00123456"


def test_ordinary_status_and_money_refresh_requires_no_removal_ack(tmp_path, production_path):
    old = capture(tmp_path / "old", [source_row()])
    assert importer.materialize(old, write_production=True).ok
    row = source_row()
    row.update(ukonceny=True, vrealizacii=False, celkovaZazmluvnenaSuma=54321)
    new = capture(tmp_path / "new", [row])
    discard_capture(old)
    result = importer.materialize(new, write_production=True)
    assert result.ok, result.errors
    assert result.report["refresh"]["removedPublishedProjectCodesCount"] == 0
    assert result.report["refresh"]["changedPublishedProjectsCount"] == 1


@pytest.mark.parametrize("write_production", [False, True])
def test_wrong_previous_manifest_cannot_fabricate_refresh_counts(tmp_path, production_path, write_production):
    old = capture(tmp_path / "old", [source_row()])
    assert importer.materialize(old, write_production=True).ok
    original_bytes = production_path.read_bytes()
    wrong = capture(tmp_path / "wrong", [source_row("TEST000002", 2)])
    result = importer.materialize(wrong, write_production=write_production, previous_manifest=wrong)
    assert not result.ok and "does not match served" in result.errors[0]
    assert production_path.read_bytes() == original_bytes


def test_broad_or_branch_categories_are_not_assumed_legal(tmp_path, production_path):
    for code in importer.AMBIGUOUS_LEGAL_FORMS:
        path = capture(tmp_path / code, [source_row(), source_row("UNSAFE0001", 2, code)])
        result = importer.materialize(path)
        assert result.ok and len(result.payload["projects"]) == 1
        assert result.report["legalForms"][code]["decision"] == "EXCLUDE_AMBIGUOUS"


@pytest.mark.parametrize("key", ["name", "title", "nazov", "address", "street", "postalCode", "email",
                                "phone", "dic", "icDph", "contactPerson", "partner", "supplier", "evaluator",
                                "bankAccount", "description", "purpose", "procurement", "irregularity", "debt"])
def test_every_forbidden_project_key_is_rejected(tmp_path, production_path, key):
    payload = importer.materialize(capture(tmp_path / "raw", [source_row()])).payload
    payload["projects"][0][key] = "SYNTHETIC FORBIDDEN"
    with pytest.raises(ValidationError):
        Dataset.model_validate(payload)


def test_excluded_invalid_identity_is_not_echoed_in_errors(tmp_path, production_path):
    row = source_row("SYNTHETIC EXCLUDED PRIVATE CODE", 2, "1009101")
    result = importer.materialize(capture(tmp_path / "raw", [source_row(), row]))
    assert not result.ok
    assert "SYNTHETIC EXCLUDED PRIVATE CODE" not in json.dumps(result.report)


def test_changed_approved_form_label_fails_closed(tmp_path, production_path):
    row = source_row()
    row["prijimatel"]["pravnaForma"]["nazovSk"] = "Synthetic changed semantics"
    result = importer.materialize(capture(tmp_path / "raw", [row]))
    assert not result.ok


def discard_capture(manifest):
    """Discard only the synthetic acquisition created by this test."""
    for path in manifest.parent.iterdir():
        path.unlink()
    manifest.parent.rmdir()


def test_fresh_clone_refresh_and_normal_addition_without_old_raw(tmp_path, production_path, monkeypatch):
    old = capture(tmp_path / "old", [source_row()])
    assert importer.materialize(old, write_production=True).ok
    original_bytes = production_path.read_bytes()
    discard_capture(old)
    new = capture(tmp_path / "new", [source_row(), source_row("TEST000002", 2)])
    load_manifest = importer.load_manifest

    def only_new_manifest(path):
        assert path == new  # Neither the old manifest nor its pages may be read.
        return load_manifest(path)

    monkeypatch.setattr(importer, "load_manifest", only_new_manifest)
    dry_run = importer.materialize(new)
    assert dry_run.ok, dry_run.errors
    assert len(dry_run.payload["projects"]) == 2
    assert not dry_run.wrote_files and production_path.read_bytes() == original_bytes
    assert dry_run.report["refresh"] == {
        "previousIncludedCount": 1, "newIncludedCount": 2,
        "addedPublishedProjectCodesCount": 1, "removedPublishedProjectCodesCount": 0,
        "projectsBecomingPrivacyExcludedCount": 0, "projectsRemovedUpstreamCount": 0,
        "changedPublishedLegalFormCodeSet": {"added": [], "removed": []},
        "sourcePopulationChange": 1, "changedPublishedProjectsCount": 0,
        "previousRawAcquisitionUsed": False, "projectsBecomingNewlyEligibleCount": None,
    }
    written = importer.materialize(new, write_production=True)
    assert written.ok, written.errors
    assert written.report["refresh"] == dry_run.report["refresh"]
    assert len(json.loads(production_path.read_bytes())["projects"]) == 2


@pytest.mark.parametrize("transition", ["upstream-removal", "privacy-exclusion"])
def test_removals_without_old_raw_require_acknowledgement(tmp_path, production_path, transition):
    old = capture(tmp_path / "old", [source_row(), source_row("TEST000002", 2)])
    assert importer.materialize(old, write_production=True).ok
    original_bytes = production_path.read_bytes()
    discard_capture(old)
    rows = [source_row()]
    if transition == "privacy-exclusion":
        rows.append(source_row("TEST000002", 2, "1009101"))
    new = capture(tmp_path / "new", rows)
    dry_run = importer.materialize(new)
    assert dry_run.ok, dry_run.errors
    assert [p["projectCode"] for p in dry_run.payload["projects"]] == ["TEST000001"]
    refresh = dry_run.report["refresh"]
    assert refresh["removedPublishedProjectCodesCount"] == 1
    assert refresh["projectsBecomingPrivacyExcludedCount"] == (transition == "privacy-exclusion")
    assert refresh["projectsRemovedUpstreamCount"] == (transition == "upstream-removal")
    assert refresh["previousRawAcquisitionUsed"] is False
    assert refresh["projectsBecomingNewlyEligibleCount"] is None
    blocked = importer.materialize(new, write_production=True)
    assert not blocked.ok and "acknowledge-removals" in blocked.errors[0]
    assert blocked.report["refresh"] == refresh
    assert production_path.read_bytes() == original_bytes
    written = importer.materialize(new, write_production=True, acknowledge_removals=True)
    assert written.ok, written.errors
    assert [p["projectCode"] for p in json.loads(production_path.read_bytes())["projects"]] == ["TEST000001"]
    # Routine reports retain counts, not identifiers of the excluded/removed row.
    assert "TEST000002" not in json.dumps(written.report)


@pytest.mark.parametrize("write_production", [False, True])
def test_unexplained_disappearance_fails_closed_even_with_ack(tmp_path, production_path, monkeypatch, write_production):
    old = capture(tmp_path / "old", [source_row(), source_row("TEST000002", 2)])
    assert importer.materialize(old, write_production=True).ok
    original_bytes = production_path.read_bytes()
    discard_capture(old)
    new = capture(tmp_path / "new", [source_row(), source_row("TEST000002", 2, "1009101")])
    build_snapshot = importer.build_snapshot

    def unexplained_snapshot(path):
        payload, report, source_codes, excluded = build_snapshot(path)
        # Simulate a projection bug: B is in source, not public, not excluded.
        excluded.clear()
        return payload, report, source_codes, excluded

    monkeypatch.setattr(importer, "build_snapshot", unexplained_snapshot)
    result = importer.materialize(new, write_production=write_production, acknowledge_removals=True)
    assert not result.ok and "unexplained disappearance" in result.errors[0]
    assert "TEST000002" not in json.dumps(result.report)
    assert production_path.read_bytes() == original_bytes


def test_optional_previous_acquisition_enriches_only_known_transitions(tmp_path, production_path):
    old = capture(tmp_path / "old", [source_row(), source_row("TEST000002", 2, "1009101")])
    assert importer.materialize(old, write_production=True).ok
    original_bytes = production_path.read_bytes()
    new = capture(tmp_path / "new", [source_row(), source_row("TEST000002", 2), source_row("TEST000003", 3)])
    ordinary = importer.materialize(new)
    assert ordinary.ok, ordinary.errors
    report = ordinary.report["refresh"]
    assert report["addedPublishedProjectCodesCount"] == 2
    assert report["previousRawAcquisitionUsed"] is False
    assert report["projectsBecomingNewlyEligibleCount"] is None
    assert "newUpstreamPublishedProjectsCount" not in report
    assert "changedSourceLegalFormCodeSet" not in report
    assert report["changedPublishedLegalFormCodeSet"] == {"added": [], "removed": []}
    enriched = importer.materialize(new, previous_manifest=old)
    assert enriched.ok, enriched.errors
    assert enriched.payload == ordinary.payload
    report = enriched.report["refresh"]
    assert report["addedPublishedProjectCodesCount"] == 2
    assert report["previousRawAcquisitionUsed"] is True
    assert report["projectsBecomingNewlyEligibleCount"] == 1
    assert report["newUpstreamPublishedProjectsCount"] == 1
    assert report["changedSourceLegalFormCodeSet"] == {"added": [], "removed": ["1009101"]}
    assert production_path.read_bytes() == original_bytes


def test_supplied_previous_raw_pages_still_require_valid_hashes(tmp_path, production_path):
    old = capture(tmp_path / "old", [source_row()])
    assert importer.materialize(old, write_production=True).ok
    original_bytes = production_path.read_bytes()
    new = capture(tmp_path / "new", [source_row(), source_row("TEST000002", 2)])
    (old.parent / "page-00000.json").write_bytes(b"synthetic corruption")
    result = importer.materialize(new, write_production=True, previous_manifest=old)
    assert not result.ok and "hash mismatch" in result.errors[0]
    assert production_path.read_bytes() == original_bytes


@pytest.mark.parametrize("write_production", [False, True])
def test_cli_refresh_without_previous_raw(tmp_path, production_path, capfd, write_production):
    from scripts.import_itms21_projects import main

    old = capture(tmp_path / "old", [source_row()])
    assert importer.materialize(old, write_production=True).ok
    original_bytes = production_path.read_bytes()
    discard_capture(old)
    new = capture(tmp_path / "new", [source_row(), source_row("TEST000002", 2)])
    args = ["--manifest", str(new)]
    if write_production:
        args.append("--write-production")
    assert main(args) == 0
    report = json.loads(capfd.readouterr().out)
    assert report["ok"] and report["dryRun"] is not write_production
    assert report["refresh"]["previousRawAcquisitionUsed"] is False
    assert report["refresh"]["projectsBecomingNewlyEligibleCount"] is None
    assert (production_path.read_bytes() != original_bytes) is write_production


def test_optional_previous_manifest_requires_public_baseline(tmp_path, production_path):
    path = capture(tmp_path / "raw", [source_row()])
    result = importer.materialize(path, write_production=True, previous_manifest=path)
    assert not result.ok and "existing production baseline" in result.errors[0]
    assert not production_path.exists()
