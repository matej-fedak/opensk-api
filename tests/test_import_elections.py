"""Synthetic/offline tests for the NR SR 2023 aggregate spike importer."""

from pathlib import Path
from decimal import Decimal, ROUND_DOWN
import csv
import json
import subprocess
import sys

import pytest

from scripts import import_elections as importer


@pytest.mark.parametrize("text,expected", [("0", 0), ("123", 123), ("1 234", 1234)])
def test_count_conversion(text: str, expected: int) -> None:
    assert importer.parse_count(text) == expected


@pytest.mark.parametrize("text", ["", "-1", "1,2", "1 2", "nan", "1e3"])
def test_invalid_counts_fail(text: str) -> None:
    with pytest.raises(ValueError):
        importer.parse_count(text)


@pytest.mark.parametrize("text,expected", [("0.00", "0.00"), ("68.51", "68.51"), ("100.00", "100.00")])
def test_percentage_conversion(text: str, expected: str) -> None:
    assert importer.parse_percentage(text) == Decimal(expected)


@pytest.mark.parametrize("text", ["", "-1", "100.01", "68,51", "NaN", "Infinity", "1.2", "1e1", "0", " 1.00"])
def test_invalid_percentages_fail(text: str) -> None:
    with pytest.raises(ValueError):
        importer.parse_percentage(text)


def test_preview_path_cannot_promote_to_production_or_escape(tmp_path: Path) -> None:
    for path in (importer.ROOT / "data" / "elections.json", tmp_path / "preview.json",
                 importer.GENERATED_DIR / ".." / "elections.json"):
        with pytest.raises(ValueError, match="production writes are forbidden"):
            importer.validate_preview_path(path)


def test_preview_path_accepts_only_generated_json() -> None:
    assert importer.validate_preview_path(importer.DEFAULT_OUTPUT) == importer.DEFAULT_OUTPUT.resolve()


def test_serialization_is_deterministic_utf8() -> None:
    assert importer.serialize_payload({"name": "Žilina", "code": "500011"}) == importer.serialize_payload(
        {"code": "500011", "name": "Žilina"}
    )


def test_code_joins_report_unmatched_without_fuzzy_matching(tmp_path: Path) -> None:
    path = tmp_path / "municipalities.json"
    path.write_text(json.dumps({"municipalities": [
        {"code": "500011", "name": "Žilina"}, {"code": "500020", "name": "Other"},
    ]}), encoding="utf-8")
    records = [
        {"municipalityCode": "500011", "municipalityName": "Žilina old label"},
        {"municipalityCode": "599999", "municipalityName": "Other"},
    ]
    report = importer.municipality_join_report(records, path)
    assert report["matched"] == 1
    assert report["unmatchedCount"] == 1
    assert report["matchRate"] == 0.5
    assert report["nameMismatches"][0]["code"] == "500011"
    assert report["referenceOnlyCodes"] == ["500020"]
    assert "referenceName" not in str(records)


def test_missing_reference_does_not_make_native_data_invalid(tmp_path: Path) -> None:
    records = [{"municipalityCode": "500011", "municipalityName": "Žilina"}]
    assert importer.municipality_join_report(records, None)["available"] is False
    assert importer.municipality_join_report(records, tmp_path / "absent.json")["available"] is False


def test_duplicate_reference_codes_are_not_silently_overwritten(tmp_path: Path) -> None:
    path = tmp_path / "municipalities.json"
    path.write_text(json.dumps({"municipalities": [
        {"code": "500011", "name": "A"}, {"code": "500011", "name": "B"},
    ]}), encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate municipality reference"):
        importer.municipality_join_report([], path)


def test_input_size_guard_is_enforced_before_decode(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(importer, "MAX_INPUT_BYTES", 4)
    path = tmp_path / "large.csv"
    path.write_bytes(b"12345")
    with pytest.raises(ValueError, match="spike limit"):
        importer.read_source_bytes(path)


def percent(numerator: int, denominator: int) -> str:
    return str((Decimal(numerator) * 100 / denominator).quantize(Decimal(".01"), rounding=ROUND_DOWN))


def aggregate(precincts=2, confirmed=1, registered=10, participating=5, envelopes=4, valid=3):
    return [str(precincts), str(confirmed), percent(confirmed, precincts), str(registered),
            str(participating), percent(participating, registered), str(envelopes),
            percent(envelopes, participating), str(valid), percent(valid, participating)]


def write_csv(path: Path, headers, rows, delimiter=",") -> Path:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter=delimiter, lineterminator="\n")
        writer.writerow(headers)
        writer.writerows(rows)
    return path


@pytest.fixture
def inputs(tmp_path):
    parents = [
        ["1", "Bratislavský kraj", "101", "Bratislava", "101", "Bratislava I", "528595", "Žilina test"],
        ["1", "Bratislavský kraj", "101", "Bratislava", "101", "Bratislava I", "500020", "Obec dva"],
        ["9", "Cudzina", "900", "Cudzina", "900", "Cudzina", "599999", "Cudzina"],
    ]
    results = [parents[0] + aggregate(), parents[1] + aggregate(1, 1, 20, 10, 9, 9),
               parents[2] + aggregate(1, 1, 4, 4, 4, 4)]
    territory = [row[:8] + [row[8]] for row in results]
    parties = [parents[0] + ["1", "Strana, jedna", "1", "33.33", "0", "0.00"],
               parents[0] + ["2", "Strana dva", "2", "66.66", "1", "50.00"],
               parents[1] + ["1", "Strana, jedna", "9", "100.00", "9", "100.00"],
               parents[2] + ["2", "Strana dva", "4", "100.00", "4", "100.00"]]
    paths = {
        "territory": write_csv(tmp_path / "territory.csv", importer.TERRITORY_HEADERS, territory),
        "results": write_csv(tmp_path / "results.csv", importer.RESULT_HEADERS, results),
        "party_results": write_csv(tmp_path / "parties.csv", importer.PARTY_HEADERS, parties),
        "national_results": write_csv(tmp_path / "national.csv", importer.NATIONAL_HEADERS,
                                      [aggregate(4, 3, 34, 19, 17, 16)]),
    }
    return {"paths": paths, "rows": {"territory": territory, "results": results,
                                     "party_results": parties}, "tmp": tmp_path}


def run(inputs, **options):
    return importer.import_elections(**dict(inputs["paths"], **options))


def change(inputs, table, rows=None, headers=None, delimiter=","):
    if headers is None:
        headers = {"territory": importer.TERRITORY_HEADERS, "results": importer.RESULT_HEADERS,
                   "party_results": importer.PARTY_HEADERS, "national_results": importer.NATIONAL_HEADERS}[table]
    return write_csv(inputs["paths"][table], headers,
                     inputs["rows"][table] if rows is None else rows, delimiter)


def test_native_full_import_and_privacy_allowlist(inputs):
    result = run(inputs)
    assert result.ok, result.errors
    assert result.payload["electionId"] == "NRSR2023"
    assert result.report["encoding"] == "utf-8"
    assert result.report["delimiter"] == ","
    assert result.report["nativeJoins"]["matched"] == 3
    assert result.report["totals"]["all"]["validVotes"] == 16
    assert result.report["totals"]["foreign"]["validVotes"] == 4
    assert result.report["unconfirmedMunicipalities"] == ["528595"]
    assert result.report["partyResults"]["sparsePositiveVotes"]
    assert result.payload["foreignResults"][0]["municipalityCode"] == "599999"
    assert len(result.payload["municipalities"]) == 2
    for record in result.payload["municipalities"] + result.payload["foreignResults"]:
        assert set(record) == importer.MUNICIPALITY_OUTPUT_FIELDS
        assert not record["regionCode"].startswith("SK")
    for record in result.payload["partyResults"]:
        assert set(record) == importer.PARTY_OUTPUT_FIELDS
    encoded = importer.serialize_payload(result.payload)
    assert b"preferential" not in encoded and b"candidate" not in encoded and b"referenceName" not in encoded
    assert result.payload["municipalities"][1]["validVotePercent"] == "60.00"
    assert result.wrote_files == []


def test_required_only_optional_controls_absent(inputs):
    result = importer.import_elections(inputs["paths"]["territory"], inputs["paths"]["results"])
    assert result.ok
    assert result.payload["partyResults"] == [] and result.payload["nationalControls"] is None


def test_reference_diagnostics_cannot_change_preview(inputs):
    path = inputs["tmp"] / "municipalities.json"
    path.write_text(json.dumps({"municipalities": [{"code": "528595", "name": "Different",
                                                  "districtCode": "SK0101"}]}), encoding="utf8")
    without = run(inputs)
    with_reference = run(inputs, municipalities=path)
    assert with_reference.ok
    assert with_reference.report["currentGeography"]["matched"] == 1
    assert with_reference.report["currentGeography"]["unmatchedCount"] == 2
    assert importer.serialize_payload(without.payload) == importer.serialize_payload(with_reference.payload)
    assert without.report["previewSha256"] == with_reference.report["previewSha256"]
    path.write_text("{malformed", encoding="utf8")
    malformed = run(inputs, municipalities=path)
    assert malformed.ok and "error" in malformed.report["currentGeography"]
    assert importer.serialize_payload(malformed.payload) == importer.serialize_payload(without.payload)


def test_repeat_and_order_are_deterministic_without_clock_or_paths(inputs):
    first = run(inputs)
    for table in ("territory", "results", "party_results"):
        change(inputs, table, list(reversed(inputs["rows"][table])))
    reordered = run(inputs)
    assert first.ok and reordered.ok
    # Raw input hashes intentionally change when source byte order changes.
    assert first.payload["municipalities"] == reordered.payload["municipalities"]
    assert first.payload["partyResults"] == reordered.payload["partyResults"]
    repeat = run(inputs)
    assert importer.serialize_payload(reordered.payload) == importer.serialize_payload(repeat.payload)
    serialized = importer.serialize_payload(repeat.payload).decode("utf8")
    assert str(inputs["tmp"]) not in serialized and "retrieved" not in serialized


@pytest.mark.parametrize("encoding", ["cp1250", "utf-8-sig", "utf-16"])
def test_non_profile_encoding_is_rejected(inputs, encoding):
    path = inputs["paths"]["territory"]
    path.write_bytes(path.read_text(encoding="utf8").encode(encoding))
    result = run(inputs)
    assert not result.ok and not result.payload and not result.wrote_files


@pytest.mark.parametrize("delimiter", [";", "|"])
def test_delimiter_drift_rejected(inputs, delimiter):
    change(inputs, "territory", delimiter=delimiter)
    assert "schema/header mismatch" in run(inputs).errors[0]


def test_header_and_width_drift_rejected(inputs):
    change(inputs, "territory", headers=list(importer.TERRITORY_HEADERS[:-1]) + [""])
    assert not run(inputs).ok
    change(inputs, "territory", rows=[inputs["rows"]["territory"][0] + ["extra"]])
    assert "width" in run(inputs).errors[0]


def test_person_level_schema_expansion_fails_closed(inputs):
    change(inputs, "territory", headers=importer.TERRITORY_HEADERS + ("candidateName",),
           rows=[inputs["rows"]["territory"][0] + ["Synthetic person"]])
    result = run(inputs)
    assert not result.ok and not result.payload and not result.wrote_files
    assert "schema/header mismatch" in result.errors[0]


def test_malformed_quote_rejected(inputs):
    path = inputs["paths"]["territory"]
    path.write_bytes(path.read_bytes() + b'"unclosed\n')
    assert not run(inputs).ok


@pytest.mark.parametrize("value", ["-1", "1 000", "NaN", "1.0", " 10"])
def test_bad_numeric_source_counts_rejected(inputs, value):
    inputs["rows"]["results"][0][11] = value
    change(inputs, "results")
    assert not run(inputs).ok


@pytest.mark.parametrize("value", ["50,00", "50.01", "101.00", "50", "NaN"])
def test_bad_source_percentages_rejected(inputs, value):
    inputs["rows"]["results"][0][13] = value
    change(inputs, "results")
    assert not run(inputs).ok


@pytest.mark.parametrize("table", ["territory", "results", "party_results"])
def test_duplicate_keys_rejected(inputs, table):
    change(inputs, table, inputs["rows"][table] + [inputs["rows"][table][0]])
    assert "duplicate" in run(inputs).errors[0]


@pytest.mark.parametrize("table", ["results", "party_results"])
def test_native_parent_name_mismatch_rejected(inputs, table):
    inputs["rows"][table][0][3] = "Altered circuit"
    change(inputs, table)
    assert "membership/name mismatch" in run(inputs).errors[0]


def test_inconsistent_territory_parent_rejected(inputs):
    inputs["rows"]["territory"][1][1] = "Altered region"
    change(inputs, "territory")
    assert "inconsistent native parent" in run(inputs).errors[0]


@pytest.mark.parametrize("table", ["results", "party_results"])
def test_orphan_native_membership_rejected(inputs, table):
    inputs["rows"][table][0][6] = "123456"
    change(inputs, table)
    assert "orphan" in run(inputs).errors[0]


def test_missing_native_membership_rejected(inputs):
    change(inputs, "results", inputs["rows"]["results"][1:])
    assert "missing native results" in run(inputs).errors[0]


def test_invalid_foreign_scope_rejected(inputs):
    inputs["rows"]["territory"][-1][1] = "Zahraničie"
    change(inputs, "territory")
    assert "foreign 599999" in run(inputs).errors[0]


def test_national_control_mismatch_rejected(inputs):
    change(inputs, "national_results", [aggregate(4, 3, 35, 19, 17, 16)])
    assert "national aggregate control" in run(inputs).errors[0]


def test_party_control_mismatch_rejected(inputs):
    change(inputs, "party_results", inputs["rows"]["party_results"][1:])
    assert "party municipality aggregate totals" in run(inputs).errors[0]


def test_party_zero_and_preference_validation(inputs):
    inputs["rows"]["party_results"][0][10] = "0"
    change(inputs, "party_results")
    assert "positive votes" in run(inputs).errors[0]
    inputs["rows"]["party_results"][0][10] = "1"
    inputs["rows"]["party_results"][0][12] = "2"
    change(inputs, "party_results")
    assert not run(inputs).ok


@pytest.mark.parametrize("column,value", [(11, "33.34"), (13, "1.00"), (9, "Changed party")])
def test_party_percentage_and_name_consistency(inputs, column, value):
    inputs["rows"]["party_results"][0][column] = value
    change(inputs, "party_results")
    assert not run(inputs).ok


def test_precinct_count_membership_and_confirmation_constraints(inputs):
    inputs["rows"]["territory"][0][8] = "3"
    change(inputs, "territory")
    assert "precinct count mismatch" in run(inputs).errors[0]
    inputs["rows"]["territory"][0][8] = "2"
    change(inputs, "territory")
    inputs["rows"]["results"][0][9] = "3"
    change(inputs, "results")
    assert "confirmed precinct count" in run(inputs).errors[0]


def test_count_inequality_rejected(inputs):
    inputs["rows"]["results"][0][16] = "6"
    change(inputs, "results")
    assert "count relationships" in run(inputs).errors[0]


def test_national_multiple_rows_rejected(inputs):
    control = aggregate(4, 3, 34, 19, 17, 16)
    change(inputs, "national_results", [control, control])
    assert "exactly one" in run(inputs).errors[0]


def test_combined_input_size_limit(inputs, monkeypatch):
    cap = max(path.stat().st_size for path in inputs["paths"].values())
    monkeypatch.setattr(importer, "MAX_INPUT_BYTES", cap)
    assert "combined input exceeds" in run(inputs).errors[0]


def test_root_output_allowlist(inputs):
    assert set(run(inputs).payload) == {"profile", "electionId", "electionDate", "status", "inputs",
                                       "municipalities", "foreignResults", "partyResults", "nationalControls", "totals"}


def test_dry_run_no_file_and_explicit_preview_only(inputs, monkeypatch):
    generated = inputs["tmp"] / "generated"
    monkeypatch.setattr(importer, "GENERATED_DIR", generated)
    output = generated / "preview.json"
    result = run(inputs, output=output)
    assert result.ok and not output.exists() and not generated.exists()
    result = run(inputs, output=output, write_preview=True, dry_run=False)
    assert result.ok and result.wrote_files == [output.resolve()]
    assert output.read_bytes() == importer.serialize_payload(result.payload)
    assert len(output.read_bytes()) == result.report["previewBytes"]
    assert not run(inputs, output=output, write_preview=True).ok


def test_production_output_denied_even_dryrun(inputs):
    assert not run(inputs, output=importer.ROOT / "data" / "elections.json").ok


def test_cli_default_dryrun_stdout_json_and_exit_status(inputs):
    command = [sys.executable, str(importer.ROOT / "scripts" / "import_elections.py"),
               "--territory", str(inputs["paths"]["territory"]),
               "--results", str(inputs["paths"]["results"])]
    completed = subprocess.run(command, capture_output=True, check=False)
    assert completed.returncode == 0, completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] and report["dryRun"] and not report["wrotePreview"]
    rejected = subprocess.run(command + ["--output", str(importer.ROOT / "data" / "elections.json")],
                              capture_output=True, check=False)
    assert rejected.returncode == 1
    assert not json.loads(rejected.stdout)["ok"]
