"""Synthetic/offline tests for the ITMS21+ projects import prototype (0.23.6).

Local shapes mirror the official manual v1.0 (25.6.2025) and the live
2026-10-14 captures; no network access, no real beneficiaries.
"""

import json
from decimal import Decimal, localcontext
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import import_itms21_projects as importer


LIST_URL = "https://api.itms21.sk/public/v1/projekt?offset=0&limit=100"
DETAIL_URL = "https://api.itms21.sk/public/v1/projekt/id/25001"

GOVERNMENT_FORM = {"kod": "1009321", "kodZdroj": "321",
                   "nazovSk": "Rozpočtová organizácia"}
SOLE_TRADER_FORM = {"kod": "1009101", "kodZdroj": "101",
                    "nazovSk": "Podnikateľ-fyzická osoba-nezapísaný v obchodnom registri"}
CITIZEN_FORM = {"kod": "100900000", "kodZdroj": "000",
                "nazovSk": "Fyzická osoba, občan - nepodnikateľ"}
UNSPECIFIED_FORM = {"kod": "1009995", "kodZdroj": "995",
                    "nazovSk": "Nešpecifikovaná právna forma"}
ASSOCIATION_FORM = {"kod": "1009701", "kodZdroj": "701",
                    "nazovSk": "Združenie (zväz, spolok, spoločnosť, klub ai.)"}

REGION = {"id": 9, "kod": "1006SK010", "kodZdroj": "SK010",
          "nazovSk": "Bratislavský kraj", "nazovEn": "Region of Bratislava"}
PROGRAMME = {"id": 4, "href": "/program/id/4", "kod": "408030",
             "nazovSk": "Nástroj finančnej podpory", "skratka": "NFPR",
             "kodCCI": "2021SK65BVPR001"}
CALL = {"id": 3782, "href": "/vyzva/id/3782", "kod": "FVZ-2026-001",
        "nazovSk": "Modernizácia IS", "program": PROGRAMME}


def beneficiary(form: dict = GOVERNMENT_FORM, name: str = "Testovacia agentúra",
                ico: str | None = "00151866") -> dict:
    record = {"id": 100001, "href": "/subjekt/id/100001", "nazov": name,
              "pravnaForma": form,
              "adresa": {"ulica": "Domáca 1", "psc": "84501", "obec": "Bratislava"}}
    if ico is not None:
        record["ico"] = ico
    return record


def row(kod: str = "408030I900", source_id: int = 25001,
        prijimatel: dict | None = None, **overrides) -> dict:
    record = {
        "id": source_id,
        "href": f"/projekt/id/{source_id}",
        "kod": kod,
        "nazov": f"Projekt {kod}",
        "vyzva": CALL,
        "miestoRealizacie": [REGION],
        "obsahujeMiestoRealizacieZahranicie": False,
        "prijimatel": prijimatel if prijimatel is not None else beneficiary(),
        "partner": [],
        "vrealizacii": True,
        "ukonceny": False,
        "stav": "Zmluva uzavretá",
        "zonfp": {"id": 9001, "href": "/zonfp/id/9001"},
        "celkovaZazmluvnenaSuma": 1200.5,
        "skutocnaRealizaciaZaciatok": 1735689600000,
        "createdAt": 1727601600000,
        "updatedAt": 1727688000000,
        # free-text upstream fields that must never be projected:
        "popis": "<p>Popis s menom Ján Novák</p>",
    }
    record.update(overrides)
    return record


def page_bytes(*rows: dict, offset: int = 0, size: int | None = None) -> bytes:
    return json.dumps({"offset": offset, "limit": len(rows),
                       "size": len(rows) if size is None else size,
                       "results": list(rows)}, ensure_ascii=False).encode("utf-8")


def detail(kod: str = "408030I900", source_id: int = 25001, **overrides) -> dict:
    record = {"id": source_id, "href": f"/projekt/id/{source_id}", "kod": kod,
              "nazov": f"Projekt {kod}",
              "zazmluvnenaSumaNfp": 1000.25,
              "poskytnuteProstriedky": 750.125,
              "planovanaRealizaciaZaciatok": 1727654400000,
              "planovanaRealizaciaKoniec": 1759190400000}
    record.update(overrides)
    return record


def write_list(tmp_path: Path, raw: bytes, name: str = "list.json") -> tuple[Path, str]:
    path = tmp_path / name
    path.write_bytes(raw)
    return path, LIST_URL


def write_detail(tmp_path: Path, kod: str = "408030I900") -> tuple[Path, str]:
    path = tmp_path / "detail.json"
    path.write_bytes(json.dumps(detail(kod), ensure_ascii=False).encode("utf-8"))
    return path, DETAIL_URL


def import_ok(tmp_path: Path, *list_payloads: bytes, details: list = (), **kwargs) -> object:
    lists = [write_list(tmp_path, raw, f"list{index}.json") for index, raw in enumerate(list_payloads)]
    return importer.import_itms21_projects(lists, list(details), **kwargs)


def projected(result, kod: str = "408030I900") -> dict:
    records = {project["projectCode"]: project for project in result.payload["projects"]}
    return records[kod]


def test_valid_list_page_projects_allowlist_record(tmp_path: Path) -> None:
    result = import_ok(tmp_path, page_bytes(row()))
    assert result.ok and result.report["merged"]["includedProjects"] == 1
    record = projected(result)
    assert record["projectCode"] == "408030I900"
    assert record["sourceId"] == 25001
    assert record["status"] == {"label": "Zmluva uzavretá", "inImplementation": True, "completed": False}
    assert record["programme"] == {"code": "408030", "nameSk": "Nástroj finančnej podpory",
                                    "shortName": "NFPR", "cci": "2021SK65BVPR001"}
    assert record["call"] == {"code": "FVZ-2026-001", "nameSk": "Modernizácia IS"}
    assert record["financials"] == {"contractedTotalEur": "1200.5"}
    assert record["implementationRegions"] == [{"nuts": "SK010", "nameSk": "Bratislavský kraj"}]
    assert record["dates"]["actualImplementationStartAt"] == "2025-01-01T00:00:00Z"
    assert record["sourceUpdatedAt"] == "2024-09-30T09:20:00Z"
    assert record["sourceUrl"] == "https://api.itms21.sk/public/v1/projekt/id/25001"
    assert record["beneficiary"] == {"name": "Testovacia agentúra", "ico": "00151866",
                                     "legalForm": {"code": "1009321",
                                                   "nameSk": "Rozpočtová organizácia"}}


def test_allowlist_never_leaks_personal_or_unreachable_fields(tmp_path: Path) -> None:
    result = import_ok(tmp_path, page_bytes(row()))
    assert result.ok
    text = json.dumps(result.payload["projects"], ensure_ascii=False)
    for leaked in ("popis", "adresa", "Domáca 1", "84501", "partner", "dodavatel",
                   "dic", "icDph", "email", "telefon"):
        assert leaked not in text


def test_money_bigdecimal_lexeme_projected_as_plain_decimal_string(tmp_path: Path) -> None:
    record = row()
    record.pop("celkovaZazmluvnenaSuma")
    page = json.dumps({"offset": 0, "limit": 1, "size": 1, "results": [record]},
                      ensure_ascii=False)
    marker = '"nazov": "Projekt 408030I900"'
    raw = page.replace(
        marker, marker + ', "celkovaZazmluvnenaSuma": 46973094.50000000000000000000'
    ).encode("utf-8")
    result = import_ok(tmp_path, raw)
    assert result.ok and "celkovaZazmluvnenaSuma" in raw.decode("utf-8")
    financials = projected(result)["financials"]
    assert financials["contractedTotalEur"] == "46973094.5"
    assert isinstance(financials["contractedTotalEur"], str)


def test_integer_amount_normalizes_without_exponent(tmp_path: Path) -> None:
    result = import_ok(tmp_path, page_bytes(row(celkovaZazmluvnenaSuma=2000000)))
    assert result.ok
    assert projected(result)["financials"]["contractedTotalEur"] == "2000000"


def test_money_preserves_precision_beyond_decimal_context() -> None:
    text = "123456789012345678901234567890.12345678901234567890123456789"
    with localcontext() as context:
        context.prec = 8
        assert importer.money_string({"amount": Decimal(text)}, "amount", "test",
                                     mandatory=True) == text


@pytest.mark.parametrize("value", [Decimal("NaN"), Decimal("Infinity"), Decimal("-1"), True, 1.25])
def test_invalid_money_rejected(value) -> None:
    with pytest.raises(ValueError):
        importer.money_string({"amount": value}, "amount", "test", mandatory=True)


def test_nonfinite_json_is_rejected_even_in_unknown_fields(tmp_path: Path) -> None:
    raw = page_bytes(row()).replace(b'"createdAt": 1727601600000', b'"createdAt": NaN')
    assert not import_ok(tmp_path, raw).ok


def test_missing_contracted_total_rejected(tmp_path: Path) -> None:
    broken = row()
    del broken["celkovaZazmluvnenaSuma"]
    result = import_ok(tmp_path, page_bytes(broken))
    assert not result.ok and "celkovaZazmluvnenaSuma" in result.errors[0]


def test_sole_trader_project_excluded_entirely(tmp_path: Path) -> None:
    result = import_ok(tmp_path, page_bytes(
        row(prijimatel=beneficiary(SOLE_TRADER_FORM, "Fiktívna Anna Osoba", "12345678"),
            nazov="Projekt Fiktívnej Anny Osoby")))
    assert result.ok and result.report["merged"]["includedProjects"] == 0
    assert result.report["merged"]["excludedNaturalPersonProjects"] == 1
    assert result.payload["projects"] == []
    text = importer.serialize_payload(result.payload).decode("utf-8")
    assert "Fiktív" not in text and "408030I900" not in text


def test_plain_citizen_without_ico_excluded(tmp_path: Path) -> None:
    result = import_ok(tmp_path, page_bytes(
        row(prijimatel=beneficiary(CITIZEN_FORM, "Fiktívny Občan", None))))
    assert result.ok and result.report["merged"]["excludedNaturalPersonProjects"] == 1
    assert result.payload["projects"] == []


def test_missing_pravna_forma_excludes_project(tmp_path: Path) -> None:
    subject = beneficiary()
    del subject["pravnaForma"]
    result = import_ok(tmp_path, page_bytes(row(prijimatel=subject)))
    assert result.ok and result.report["merged"]["excludedUnreviewedBeneficiaryProjects"] == 1
    assert result.payload["projects"] == []


@pytest.mark.parametrize("subject", [None, "invalid subject", {}])
def test_unclassifiable_beneficiary_excludes_project(tmp_path: Path, subject) -> None:
    project = row()
    project["prijimatel"] = subject
    result = import_ok(tmp_path, page_bytes(project))
    assert result.ok and result.payload["projects"] == []
    assert result.payload["counts"]["excludedUnreviewedBeneficiaryProjects"] == 1


def test_absent_beneficiary_excludes_project(tmp_path: Path) -> None:
    project = row()
    project.pop("prijimatel")
    result = import_ok(tmp_path, page_bytes(project))
    assert result.ok and result.payload["projects"] == []


@pytest.mark.parametrize("code", ["", "1009NEW", "1009AT000"])
def test_unknown_legal_form_fails_closed(tmp_path: Path, code: str) -> None:
    result = import_ok(tmp_path, page_bytes(row(
        prijimatel=beneficiary({"kod": code, "nazovSk": "Unreviewed"}),
        nazov="Potential personal identity in title")))
    assert result.ok and result.report["merged"]["excludedUnreviewedBeneficiaryProjects"] == 1
    assert result.payload["projects"] == []


def test_unspecified_legal_form_1009995_excluded(tmp_path: Path) -> None:
    result = import_ok(tmp_path, page_bytes(
        row(prijimatel=beneficiary(UNSPECIFIED_FORM, "Niečo n.t.b."))))
    assert result.ok and result.report["merged"]["excludedUnreviewedBeneficiaryProjects"] == 1
    assert result.payload["projects"] == []


def test_legal_entity_form_included_and_counted_for_review(tmp_path: Path) -> None:
    result = import_ok(tmp_path, page_bytes(
        row(prijimatel=beneficiary(ASSOCIATION_FORM, "Kultúrne združenie"))))
    assert result.ok and projected(result)["beneficiary"]["legalForm"]["code"] == "1009701"
    assert result.report["includedPravnaFormaCodes"] == {"1009701": 1}


def test_all_denylist_codes_excluded_across_countries(tmp_path: Path) -> None:
    for code in importer.NATURAL_PERSON_FORMS:
        form = {"kod": code, "kodZdroj": code[4:], "nazovSk": "denylist test"}
        result = import_ok(tmp_path, page_bytes(
            row(prijimatel=beneficiary(form, f"Men{code}", None))))
        assert result.ok, code
        assert result.payload["projects"] == [], code
        assert result.payload["counts"]["includedProjects"] == 0


@pytest.mark.parametrize("form", [CITIZEN_FORM, SOLE_TRADER_FORM, UNSPECIFIED_FORM,
                                  {"kod": "1009NEW"}, {}, None])
def test_unsafe_project_has_no_linkable_or_fact_leak_anywhere_in_preview(tmp_path: Path, form) -> None:
    unsafe = row("UNSAFEFIXTUREONLY", 987654321012345,
                 prijimatel=beneficiary(form, "Synthetic excluded identity", "12345678"),
                 nazov="Synthetic excluded title", stav="UNSAFE_STATUS_SENTINEL",
                 celkovaZazmluvnenaSuma=999987654.321,
                 miestoRealizacie=[{"kodZdroj": "UNSAFE_LOCATION_SENTINEL"}],
                 updatedAt=1800000000000)
    source = write_list(tmp_path, page_bytes(row(), unsafe), "UNSAFEFIXTUREONLY.json")
    # Even a supplied list URL/filter or filename must not leak the excluded ID.
    url = LIST_URL + "&kod=UNSAFEFIXTUREONLY"
    result = importer.import_itms21_projects([(source[0], url)], [])
    assert result.ok and len(result.payload["projects"]) == 1
    assert result.payload["counts"]["includedProjects"] == 1
    assert projected(result)["beneficiary"]["legalForm"]["code"] in importer.LEGAL_ENTITY_FORMS
    preview = importer.serialize_payload(result.payload).decode("utf-8")
    for forbidden in ("UNSAFEFIXTUREONLY", "987654321012345", "Synthetic excluded identity",
                      "Synthetic excluded title", "UNSAFE_STATUS_SENTINEL", "999987654.321",
                      "UNSAFE_LOCATION_SENTINEL", "2027-01-15T08:00:00Z"):
        assert forbidden not in preview
    assert "redactedRows" not in preview
    assert not any("file" in source for source in result.payload["sources"])


def test_only_reviewed_projects_contribute_to_included_count(tmp_path: Path) -> None:
    rows = [row(), row("NATURAL0001", 25002, prijimatel=beneficiary(CITIZEN_FORM)),
            row("SOLE0000001", 25003, prijimatel=beneficiary(SOLE_TRADER_FORM)),
            row("UNKNOWN0001", 25004, prijimatel=beneficiary({"kod": "NEW"})),
            row("UNSPEC00001", 25005, prijimatel=beneficiary(UNSPECIFIED_FORM)),
            row("MISSING0001", 25006, prijimatel={"nazov": "Synthetic missing form"}),
            row("LEGAL000001", 25007, prijimatel=beneficiary(ASSOCIATION_FORM))]
    result = import_ok(tmp_path, page_bytes(*rows, size=4571))
    assert result.ok
    assert result.payload["counts"] == {
        "inputRows": 7, "sourcePopulationObserved": 4571, "includedProjects": 2,
        "excludedNaturalPersonProjects": 2, "excludedUnreviewedBeneficiaryProjects": 3}
    assert result.report["merged"] == {
        "totalRows": 7, "includedProjects": 2, "excludedNaturalPersonProjects": 2,
        "excludedUnreviewedBeneficiaryProjects": 3}
    assert {r["projectCode"] for r in result.payload["projects"]} == {"408030I900", "LEGAL000001"}


def test_excluded_detail_is_recognized_but_not_projected_or_persisted(tmp_path: Path) -> None:
    kod, source_id = "EXCLUDEDONLY0001", 987654321012345
    path = tmp_path / f"{kod}.json"
    # Rich unsafe fields need not have the approved projection's money schema.
    path.write_text(json.dumps({"id": source_id, "kod": kod,
                               "nazov": "Synthetic private detail title",
                               "popis": "Synthetic private description"}), encoding="utf-8")
    source = (path, f"{importer.API_BASE}/projekt/kod/{kod}")
    result = import_ok(tmp_path, page_bytes(
        row(), row(kod, source_id, prijimatel=beneficiary(SOLE_TRADER_FORM))), details=[source])
    assert result.ok and result.payload["counts"]["includedProjects"] == 1
    assert result.payload["counts"]["excludedNaturalPersonProjects"] == 1
    assert not any(s["role"] == "detail" for s in result.payload["sources"])
    preview = importer.serialize_payload(result.payload).decode("utf-8")
    assert kod not in preview and str(source_id) not in preview and "Synthetic private" not in preview


def test_excluded_project_detail_still_requires_identity_consistency(tmp_path: Path) -> None:
    source = write_detail(tmp_path)
    source[0].write_text(json.dumps(detail(source_id=999)), encoding="utf-8")
    result = import_ok(tmp_path, page_bytes(row(prijimatel=beneficiary(CITIZEN_FORM))), details=[source])
    assert not result.ok and "ID mismatch" in result.errors[0]


def test_detail_cannot_override_gate_with_unsafe_beneficiary(tmp_path: Path) -> None:
    source = write_detail(tmp_path)
    source[0].write_text(json.dumps(detail(prijimatel=beneficiary(SOLE_TRADER_FORM))), encoding="utf-8")
    result = import_ok(tmp_path, page_bytes(row()), details=[source])
    assert result.ok and result.payload["projects"] == []
    assert result.payload["counts"]["excludedNaturalPersonProjects"] == 1
    assert not any(s["role"] == "detail" for s in result.payload["sources"])


def test_excluded_project_is_not_fully_built(tmp_path: Path) -> None:
    unsafe = row(prijimatel=beneficiary(CITIZEN_FORM))
    for key in ("nazov", "vyzva", "miestoRealizacie", "celkovaZazmluvnenaSuma", "updatedAt"):
        unsafe.pop(key)
    result = import_ok(tmp_path, page_bytes(unsafe))
    assert result.ok and result.payload["projects"] == []


def test_duplicate_excluded_project_still_rejected(tmp_path: Path) -> None:
    unsafe = row(prijimatel=beneficiary(CITIZEN_FORM))
    result = import_ok(tmp_path, page_bytes(unsafe), page_bytes(unsafe))
    assert not result.ok and "duplicate project code" in result.errors[0]


def test_exclusion_projection_serializes_deterministically(tmp_path: Path) -> None:
    sources = [write_list(tmp_path, page_bytes(row(), size=2), "approved.json"),
               write_list(tmp_path, page_bytes(row("EXCLUDED0001", 25002,
                          prijimatel=beneficiary(CITIZEN_FORM)), size=2), "unsafe.json")]
    first = importer.import_itms21_projects(sources, [])
    second = importer.import_itms21_projects(list(reversed(sources)), [])
    assert first.ok and second.ok
    assert importer.serialize_payload(first.payload) == importer.serialize_payload(second.payload)


def test_detail_enrichment_adds_nfp_amounts_and_planned_dates(tmp_path: Path) -> None:
    result = import_ok(tmp_path, page_bytes(row()), details=[write_detail(tmp_path)])
    assert result.ok
    financials = projected(result)["financials"]
    assert financials == {"contractedTotalEur": "1200.5",
                          "contractedNfpEur": "1000.25", "providedNfpEur": "750.125"}
    dates = projected(result)["dates"]
    assert dates["plannedImplementationStartAt"] == "2024-09-30T00:00:00Z"
    assert dates["plannedImplementationEndAt"] == "2025-09-30T00:00:00Z"


def test_duplicate_project_code_across_pages_rejected(tmp_path: Path) -> None:
    result = import_ok(tmp_path, page_bytes(row()), page_bytes(row()))
    assert not result.ok and "duplicate project code" in result.errors[0]


def test_duplicate_detail_code_rejected(tmp_path: Path) -> None:
    result = import_ok(tmp_path, page_bytes(row()),
                       details=[write_detail(tmp_path), write_detail(tmp_path)])
    assert not result.ok and "duplicate detail" in result.errors[0]


def test_duplicate_project_id_with_different_codes_rejected(tmp_path: Path) -> None:
    result = import_ok(tmp_path, page_bytes(row(), row("408030OTHER")))
    assert not result.ok and "duplicate project source ID" in result.errors[0]


def test_mismatching_detail_id_rejected(tmp_path: Path) -> None:
    source = write_detail(tmp_path)
    source[0].write_text(json.dumps(detail(source_id=999)), encoding="utf-8")
    result = import_ok(tmp_path, page_bytes(row()), details=[source])
    assert not result.ok and "ID mismatch" in result.errors[0]


def test_unmatched_detail_rejected(tmp_path: Path) -> None:
    result = import_ok(tmp_path, page_bytes(row()), details=[write_detail(tmp_path, "408030OTHER")])
    assert not result.ok and "no matching list project" in result.errors[0]


def test_detail_enrichment_without_actual_dates(tmp_path: Path) -> None:
    project = row()
    project.pop("skutocnaRealizaciaZaciatok")
    result = import_ok(tmp_path, page_bytes(project), details=[write_detail(tmp_path)])
    assert result.ok and "plannedImplementationStartAt" in projected(result)["dates"]


def test_inconsistent_page_totals_rejected(tmp_path: Path) -> None:
    result = import_ok(tmp_path, page_bytes(row(), size=100),
                       page_bytes(row("408030OTHER", 25002), size=101))
    assert not result.ok and "snapshot consistency" in result.errors[0]


def test_instants_not_truncated_to_previous_utc_calendar_date(tmp_path: Path) -> None:
    # 2025-01-01 local midnight in Bratislava is still Dec 31 in UTC.
    result = import_ok(tmp_path, page_bytes(row(skutocnaRealizaciaZaciatok=1735686000000)))
    assert result.ok
    assert projected(result)["dates"]["actualImplementationStartAt"] == "2024-12-31T23:00:00Z"


def test_boolean_timestamp_rejected(tmp_path: Path) -> None:
    assert not import_ok(tmp_path, page_bytes(row(skutocnaRealizaciaZaciatok=True))).ok


def test_direct_import_source_url_validated(tmp_path: Path) -> None:
    source, _ = write_list(tmp_path, page_bytes(row()))
    result = importer.import_itms21_projects([(source, "https://example.org/fake")], [])
    assert not result.ok and "source URL" in result.errors[0]


@pytest.mark.parametrize("mutation,match", [
    (lambda r: r.update({"kod": "!!!"}), "invalid project code"),
    (lambda r: r.update({"href": "/project/id/1"}), "invalid 'href'"),
    (lambda r: r.update({"nazov": ""}), "missing/invalid 'nazov'"),
    (lambda r: r.update({"vrealizacii": "yes"}), "missing/invalid 'vrealizacii'"),
    (lambda r: r.update({"miestoRealizacie": [{"kod": "1006SK010"}]}),
     "missing NUTS code"),
    (lambda r: r["prijimatel"].update({"ico": "12-34"}), "invalid 'ico'"),
    (lambda r: r.pop("vyzva"), "missing 'vyzva' link"),
])
def test_schema_drift_rejected(tmp_path: Path, mutation, match: str) -> None:
    broken = row()
    mutation(broken)
    result = import_ok(tmp_path, page_bytes(broken))
    assert not result.ok and match in result.errors[0]


def test_malformed_list_page_rejected(tmp_path: Path) -> None:
    assert not import_ok(tmp_path, b"[1,2,3]").ok
    assert "missing/invalid 'size'" in import_ok(tmp_path, b'{"results": []}').errors[0]
    assert not import_ok(tmp_path, b"not json").ok


def test_regions_deduplicated_and_sorted(tmp_path: Path) -> None:
    other = {"kodZdroj": "SK032", "nazovSk": "Banskobystrický kraj"}
    result = import_ok(tmp_path, page_bytes(
        row(miestoRealizacie=[REGION, dict(other), dict(REGION)])))
    assert result.ok
    assert projected(result)["implementationRegions"] == [
        {"nuts": "SK010", "nameSk": "Bratislavský kraj"},
        {"nuts": "SK032", "nameSk": "Banskobystrický kraj"}]


def test_output_deterministic_regardless_of_row_order(tmp_path: Path) -> None:
    rows = (row("AAA0000001", 1), row("MBB0000002", 2), row("ZZZ0000003", 3))
    first = import_ok(tmp_path, page_bytes(*rows))
    second = import_ok(tmp_path, page_bytes(*reversed(rows)))
    assert first.ok and second.ok
    serialized = [json.dumps(r.payload["projects"], sort_keys=True, ensure_ascii=False)
                  for r in (first, second)]
    assert serialized[0] == serialized[1]
    assert [p["projectCode"] for p in first.payload["projects"]] == [
        "AAA0000001", "MBB0000002", "ZZZ0000003"]


def test_preview_payload_carries_privacy_and_licence_metadata(tmp_path: Path) -> None:
    raw = page_bytes(row(), row("408030IAG0", 25002,
                                prijimatel=beneficiary(ASSOCIATION_FORM, "Klub")))
    result = import_ok(tmp_path, raw)
    assert result.ok
    privacy = result.payload["privacy"]
    assert privacy["unsafeProjectsExcluded"] is True
    assert privacy["policy"] == "REVIEWED_LEGAL_ENTITY_PROJECTS_ONLY"
    assert set(privacy["denylist"]) == set(sorted(importer.NATURAL_PERSON_FORMS))
    assert "CC BY" in result.payload["licence"] and "MIRRI" in result.payload["licence"]
    assert result.payload["status"] == "unapproved-research-preview"
    assert result.payload["counts"] == {
        "inputRows": 2, "sourcePopulationObserved": 2, "includedProjects": 2,
        "excludedNaturalPersonProjects": 0, "excludedUnreviewedBeneficiaryProjects": 0}
    assert result.payload["sources"][0]["sourceUrl"] == f"{importer.API_BASE}/projekt"
    assert len(result.payload["sources"][0]["sha256"]) == 64


def test_dry_run_writes_nothing(tmp_path: Path) -> None:
    result = import_ok(tmp_path, page_bytes(row()), dry_run=True)
    assert result.ok and result.report["dryRun"] is True and not result.report["wrotePreview"]
    assert not result.wrote_files


def test_preview_path_rejects_escape_and_non_json(tmp_path: Path) -> None:
    for path in (importer.ROOT / "data" / "eu_funds_projects.json",
                 tmp_path / "preview.json",
                 importer.GENERATED_DIR / ".." / "preview.json",
                 importer.GENERATED_DIR / "preview.xml"):
        with pytest.raises(ValueError, match="preview output must be"):
            importer.validate_preview_path(path)


def test_write_preview_only_into_generated(tmp_path: Path) -> None:
    target = importer.GENERATED_DIR / "itms21_projects_test_preview.json"
    try:
        if target.exists():
            target.unlink()
        result = import_ok(tmp_path, page_bytes(row()), dry_run=False,
                           write_preview=True, output=target)
        assert result.ok and result.report["wrotePreview"] is True
        assert result.wrote_files == [target.resolve()]
        written = json.loads(target.read_text(encoding="utf-8"))
        assert written["status"] == "unapproved-research-preview"
        assert written["projects"][0]["projectCode"] == "408030I900"
    finally:
        if target.exists():
            target.unlink()


def test_write_preview_bytes_match_report(tmp_path: Path) -> None:
    target = importer.GENERATED_DIR / "itms21_projects_test_bytes.json"
    try:
        if target.exists():
            target.unlink()
        result = import_ok(tmp_path, page_bytes(row()), dry_run=False,
                           write_preview=True, output=target)
        assert result.ok
        raw = target.read_bytes()
        assert len(raw) == result.report["previewBytes"]
        import hashlib
        assert hashlib.sha256(raw).hexdigest() == result.report["previewSha256"]
    finally:
        if target.exists():
            target.unlink()


def test_modes_are_mutually_exclusive(tmp_path: Path) -> None:
    result = importer.import_itms21_projects([write_list(tmp_path, page_bytes(row()))], [],
                                             dry_run=True, write_preview=True)
    assert not result.ok and "exactly one" in result.errors[0]


def test_at_least_one_list_capture_required() -> None:
    result = importer.import_itms21_projects([], [], retrieved_at=None)
    assert not result.ok and "at least one" in result.errors[0]


def test_retrieved_at_must_be_iso_timestamp(tmp_path: Path) -> None:
    result = import_ok(tmp_path, page_bytes(row()), retrieved_at="14.10.2026")
    assert not result.ok and "ISO-8601" in result.errors[0]
    ok = import_ok(tmp_path, page_bytes(row()), retrieved_at="2026-10-14T18:00:00Z")
    assert ok.ok


def test_source_argument_url_patterns(capsys) -> None:
    with pytest.raises(SystemExit):
        importer.main(["--projects", "x.json=https://api.itms21.sk/public/v1/subjekt",
                       "--dry-run"])
    captured = capsys.readouterr()
    assert "must be path=" in captured.err


def test_cli_dry_run_and_modes(tmp_path: Path) -> None:
    path = tmp_path / "capture.json"
    path.write_bytes(page_bytes(row()))
    argv = ["--projects", f"{path}={LIST_URL}"]
    assert importer.main(argv + ["--dry-run"]) == 0
    with pytest.raises(SystemExit):
        importer.main(argv + ["--dry-run", "--write-preview"])
    script = Path(importer.__file__)
    proc = subprocess.run([sys.executable, str(script), *argv],
                          capture_output=True, text=True)
    assert proc.returncode == 0
    assert '"ok": true' in proc.stdout


def test_research_captures_cannot_write_production(capsys) -> None:
    with pytest.raises(SystemExit):
        importer.main(["--projects", f"capture.json={LIST_URL}", "--write-production"])
    assert "requires --manifest" in capsys.readouterr().err


def test_input_size_limit_enforced(tmp_path: Path) -> None:
    path, url = write_list(tmp_path, page_bytes(row()))
    original = importer.MAX_INPUT_BYTES
    importer.MAX_INPUT_BYTES = 10
    try:
        result = importer.import_itms21_projects([(path, url)], [])
        assert not result.ok and "byte spike limit" in result.errors[0]
    finally:
        importer.MAX_INPUT_BYTES = original
