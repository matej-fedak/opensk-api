"""Offline synthetic CSV fixtures: no official raw CSV committed or downloaded."""

import csv
from copy import deepcopy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from schemas.elections import ElectionDataset, EXPECTED_TOTALS
from scripts import import_elections as importer
from scripts import prepare_elections_manifest as manifest


@pytest.fixture
def party_rows():
    summary = [[str(n), f"Subject, {n}", "4", "4.00", "2", "50.00", "150" if n == 1 else ""]
               for n in range(1, 26)]
    names = [[str(n), f"Subject, {n}", f"S{n}", "10", ""] for n in range(1, 26)]
    return summary, names


def test_national_parties_quoted_labels_blank_mandates_deterministic(party_rows):
    summary, names = party_rows
    result = importer.national_parties(summary, names, 100)
    assert result == importer.national_parties(list(reversed(summary)), list(reversed(names)), 100)
    assert [p["partyNumber"] for p in result] == [str(n) for n in range(1, 26)]
    assert result[0]["seats"] == 150 and result[1]["seats"] is None
    assert set(result[0]) == {"partyNumber", "name", "abbreviation", "validVotes", "votePercent", "seats"}


@pytest.mark.parametrize("column,value", [(2, "-1"), (2, ""), (3, "4.01"), (3, "4,00"),
                                        (4, "5"), (5, "0.00"), (6, " "), (6, "-1"), (6, "149")])
def test_national_party_invalid_counts_percentages_blanks(party_rows, column, value):
    summary, names = party_rows
    summary[0][column] = value
    with pytest.raises(ValueError):
        importer.national_parties(summary, names, 100)


@pytest.mark.parametrize("mutation", ["duplicate-list", "duplicate-summary", "missing", "orphan", "name", "blank-name", "blank-abbreviation", "note"])
def test_party_join_or_blank_semantics_fail(party_rows, mutation):
    summary, names = party_rows
    if mutation == "duplicate-list":
        names.append(names[0])
    elif mutation == "duplicate-summary":
        summary.append(summary[0])
    elif mutation == "missing":
        summary.pop()
    elif mutation == "orphan":
        names.pop()
    elif mutation == "name":
        summary[0][1] = "Wrong name"
    elif mutation == "blank-name":
        names[0][1] = ""
    elif mutation == "blank-abbreviation":
        names[0][2] = ""
    else:
        names[0][4] = "unreviewed note"
    with pytest.raises(ValueError):
        importer.national_parties(summary, names, 100)


@pytest.fixture
def snapshot():
    return json.loads(Path("data/elections_nrsr_2023.json").read_bytes())


def test_production_totals_and_scope(snapshot):
    data = ElectionDataset.model_validate(snapshot)
    assert len(data.units) == 2927
    assert sum(u.unitType == "domestic" for u in data.units) == 2926
    foreign, = [u for u in data.units if u.unitType == "foreign"]
    assert foreign.municipalityCode == "599999" and foreign.validVotes == 57856
    assert {f: getattr(data.national, f) for f in EXPECTED_TOTALS} == EXPECTED_TOTALS
    assert sum(p.validVotes for p in data.parties) == 2967896
    assert sum(p.seats or 0 for p in data.parties) == 150
    assert sum(p.seats is None for p in data.parties) == 18
    assert data.provenance.acquisitionTimePrecision == "approximate-minute"
    assert data.election.sourceSnapshotDate == "2026-10-31"
    acquisition = json.loads(Path("docs/research/elections-nrsr2023-acquisition.json").read_bytes())
    assert {r.filename: r.sha256 for r in data.provenance.files} == {r["filename"]: r["sha256"] for r in acquisition["files"]}
    assert data.provenance.manuallyAcquiredAt == acquisition["manuallyAcquiredAt"]
    assert not any(token in json.dumps(acquisition) for token in ("C:\\\\Users", "/Users/", "Downloads", "matej"))


@pytest.mark.parametrize("mutation", ["unit-duplicate", "unit-missing", "unit-order", "foreign", "national", "party-total", "mandates", "party-duplicate", "person-field", "precinct-equality", "blank-percentage", "bad-date", "manifest-file", "boolean-count", "extra-root"])
def test_dataset_validation_fails_closed(snapshot, mutation):
    if mutation == "unit-duplicate":
        snapshot["units"][1] = deepcopy(snapshot["units"][0])
    elif mutation == "unit-missing":
        snapshot["units"].pop()
    elif mutation == "unit-order":
        snapshot["units"].reverse()
    elif mutation == "foreign":
        snapshot["units"][-1]["unitType"] = "domestic"
    elif mutation == "national":
        snapshot["national"]["validVotes"] -= 1
    elif mutation == "party-total":
        snapshot["parties"][0]["validVotes"] -= 1
    elif mutation == "mandates":
        snapshot["parties"][0]["seats"] = 1
    elif mutation == "party-duplicate":
        snapshot["parties"][1]["partyNumber"] = "1"
    elif mutation == "person-field":
        snapshot["units"][0]["candidateName"] = "Synthetic forbidden field"
    elif mutation == "precinct-equality":
        snapshot["national"]["confirmedPrecinctCount"] = 6014
    elif mutation == "blank-percentage":
        snapshot["units"][0]["turnoutPercent"] = ""
    elif mutation == "bad-date":
        snapshot["election"]["sourceSnapshotDate"] = "2026-02-30"
    elif mutation == "manifest-file":
        snapshot["provenance"]["files"][0]["filename"] = "candidate.csv"
    elif mutation == "boolean-count":
        snapshot["parties"][0]["seats"] = True
    else:
        snapshot["municipalityPartyVotes"] = []
    with pytest.raises(ValidationError):
        ElectionDataset.model_validate(snapshot)


@pytest.fixture
def synthetic_sources(tmp_path, snapshot):
    """Regenerate test-only CSV rows offline from aggregate public JSON.

    No dependency on Downloads/private artifacts; no giant committed CSV fixture.
    Preferential-voter/candidate counts here are synthetic test values only.
    """
    rows = {
        "tab0c": [[u[f] for f in importer.NATIVE_FIELDS] + [u["precinctCount"]] for u in snapshot["units"]],
        "tab02d": [[u[f] for f in importer.NATIVE_FIELDS + importer.AGGREGATE_FIELDS] for u in snapshot["units"]],
        "tab01": [[snapshot["national"][f] for f in importer.AGGREGATE_FIELDS]],
        "tab03a": [[p["partyNumber"], p["name"], p["validVotes"], p["votePercent"], "0", "0.00",
                    "" if p["seats"] is None else p["seats"]] for p in snapshot["parties"]],
        "tab0a": [[p["partyNumber"], p["name"], p["abbreviation"], "1", ""] for p in snapshot["parties"]],
    }
    for key, records in rows.items():
        with (tmp_path / f"NRSR2023_SK_{key}.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(manifest.TABLES[key][0]); writer.writerows(records)
    doc = manifest.prepare_manifest(tmp_path, "2026-10-31T17:20:00Z", attest_manual_download=True)
    m = tmp_path / "manifest.json"
    m.write_bytes(importer.serialize_payload(doc))
    paths = [tmp_path / f"NRSR2023_SK_{key}.csv" for key in manifest.TABLES]
    return paths, m


def test_full_import_dry_run_determinism_and_explicit_atomic_production(synthetic_sources, tmp_path, monkeypatch):
    paths, m = synthetic_sources
    output = tmp_path / "production.json"
    monkeypatch.setattr(importer, "PRODUCTION_OUTPUT", output)
    options = dict(verified_on="2026-10-31", output=output, acknowledge_source_revision=True)
    first = importer.import_production(*paths, m, **options)
    assert first.ok, first.errors
    assert first.wrote_files == [] and not output.exists()
    second = importer.import_production(*paths, m, write_production=True, **options)
    assert second.ok, second.errors
    assert second.payload == first.payload
    assert output.read_bytes() == importer.serialize_payload(first.payload)
    assert not list(tmp_path.glob("*.election-candidate"))


def test_manifest_drift_and_unacknowledged_revision_block_writes(synthetic_sources, tmp_path, monkeypatch):
    paths, m = synthetic_sources
    output = tmp_path / "production.json"
    monkeypatch.setattr(importer, "PRODUCTION_OUTPUT", output)
    result = importer.import_production(*paths, m, verified_on="2026-10-31", output=output, write_production=True)
    assert not result.ok and "source bytes" in result.errors[0] and not output.exists()
    doc = json.loads(m.read_bytes()); doc["files"][0]["sha256"] = "0" * 64
    m.write_bytes(importer.serialize_payload(doc))
    result = importer.import_production(*paths, m, verified_on="2026-10-31", output=output,
                                        write_production=True, acknowledge_source_revision=True)
    assert not result.ok and "hash mismatch" in result.errors[0] and not output.exists()


def test_wrong_profile_and_production_path_rejected_without_reading(tmp_path):
    paths = [tmp_path / "missing"] * 6
    result = importer.import_production(*paths, verified_on="2026-10-31", profile="NRSR2020")
    assert not result.ok and "profile" in result.errors[0]
    result = importer.import_production(*paths, verified_on="2026-10-31", output=tmp_path / "wrong.json")
    assert not result.ok and "production output" in result.errors[0]
