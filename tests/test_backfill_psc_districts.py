from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import backfill_psc_districts as importer
from scripts.backfill_psc_districts import backfill_psc_districts


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_backfill_psc_districts_uses_municipality_mapping(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    input_path = data_dir / "psc.json"
    _write_json(data_dir / "regions.json", {"regions": [{"code": "SK010", "name": "Bratislavský kraj"}]})
    _write_json(data_dir / "districts.json", {"districts": [{"code": "SK0101", "name": "Bratislava I", "regionCode": "SK010"}]})
    _write_json(
        data_dir / "municipalities.json",
        {"municipalities": [{"code": "528595", "name": "Staré Mesto", "districtCode": "SK0101", "regionCode": "SK010"}]},
    )
    _write_json(
        input_path,
        {
            "metadata": {"source": "unit-test"},
            "81101": {
                "psc": "81101",
                "municipalityCode": "528595",
                "districtCode": None,
                "regionCode": "SK010",
                "matches": [
                    {"psc": "81101", "municipalityCode": "528595", "districtCode": None, "regionCode": "SK010"}
                ],
            },
        },
    )

    payload, stats = backfill_psc_districts(input_path, data_dir)

    assert stats.ok
    assert stats.total_records == 1
    assert stats.successfully_backfilled == 1
    assert stats.unresolved_municipality_code_count == 0
    assert stats.region_conflict_count == 0
    assert stats.district_code_coverage_before == 0
    assert stats.district_code_coverage_after == 1
    assert payload["81101"]["districtCode"] == "SK0101"
    assert payload["81101"]["matches"][0]["districtCode"] == "SK0101"


def test_backfill_psc_districts_leaves_conflicts_unmapped(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    input_path = data_dir / "psc.json"
    _write_json(data_dir / "regions.json", {"regions": [{"code": "SK010", "name": "Bratislavský kraj"}, {"code": "SK021", "name": "Trnavský kraj"}]})
    _write_json(data_dir / "districts.json", {"districts": [{"code": "SK0101", "name": "Bratislava I", "regionCode": "SK010"}]})
    _write_json(
        data_dir / "municipalities.json",
        {"municipalities": [{"code": "528595", "name": "Staré Mesto", "districtCode": "SK0101", "regionCode": "SK010"}]},
    )
    _write_json(
        input_path,
        {"metadata": {"source": "unit-test"}, "81101": {"psc": "81101", "municipalityCode": "528595", "districtCode": None, "regionCode": "SK021"}},
    )

    payload, stats = backfill_psc_districts(input_path, data_dir)

    assert not stats.ok
    assert stats.successfully_backfilled == 0
    assert stats.region_conflict_count == 1
    assert payload["81101"]["districtCode"] is None


@pytest.mark.parametrize("other", ["--dry-run", "--write"])
def test_promote_is_exclusive_with_other_modes(other):
    with pytest.raises(SystemExit) as exc:
        importer.main(["--promote", other])
    assert exc.value.code == 2


def _cli_fixture(tmp_path, monkeypatch, *, region="SK010"):
    data = tmp_path / "data"
    monkeypatch.setattr(importer, "ROOT", tmp_path)
    monkeypatch.setattr(importer, "DEFAULT_DATA_DIR", data)
    _write_json(data / "regions.json", {"regions": [{"code": "SK010"}]})
    _write_json(data / "districts.json", {"districts": [{"code": "SK0101", "regionCode": "SK010"}]})
    _write_json(data / "municipalities.json", {"municipalities": [
        {"code": "528595", "districtCode": "SK0101", "regionCode": "SK010"}]})
    source = data / "source.json"
    _write_json(source, {"81101": {"psc": "81101", "country": "Slovakia",
                                  "municipalityCode": "528595", "regionCode": region}})
    return data, source


@pytest.mark.parametrize("mode", ["--write", "--promote"])
def test_cli_conflicts_never_replace_existing_output(tmp_path, monkeypatch, mode):
    data, source = _cli_fixture(tmp_path, monkeypatch, region="SK021")
    target = data / "psc.json" if mode == "--promote" else tmp_path / "candidate.json"
    target.write_bytes(b"pre-existing output")
    assert importer.main(["--input", str(source), "--output", str(target), mode]) == 1
    assert target.read_bytes() == b"pre-existing output"


def test_candidate_validation_precedes_write(tmp_path, monkeypatch):
    data, source = _cli_fixture(tmp_path, monkeypatch)
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["81101"]["matchCount"] = 1
    payload["81101"]["matches"] = []
    _write_json(source, payload)
    target = tmp_path / "candidate.json"
    target.write_bytes(b"existing")
    assert importer.main(["--input", str(source), "--output", str(target), "--write"]) == 1
    assert target.read_bytes() == b"existing"


def test_validated_promotion_is_atomic_and_only_touches_temp_production(tmp_path, monkeypatch):
    from scripts import import_utils
    data, source = _cli_fixture(tmp_path, monkeypatch)
    production = data / "psc.json"
    production.write_bytes(b"existing")
    replacements = []
    original = import_utils.os.replace

    def replace(src, dst):
        if Path(dst) == production:
            assert production.read_bytes() == b"existing"
            assert json.loads(Path(src).read_text(encoding="utf-8"))["81101"]["districtCode"] == "SK0101"
        replacements.append(Path(dst))
        return original(src, dst)

    monkeypatch.setattr(import_utils.os, "replace", replace)
    assert importer.main(["--input", str(source), "--promote"]) == 0
    assert replacements.count(production) == 1
    assert json.loads(production.read_text(encoding="utf-8"))["81101"]["districtCode"] == "SK0101"


def test_dry_run_preserves_existing_target(tmp_path, monkeypatch):
    _, source = _cli_fixture(tmp_path, monkeypatch)
    target = tmp_path / "candidate.json"
    target.write_bytes(b"existing")
    assert importer.main(["--input", str(source), "--output", str(target), "--dry-run"]) == 0
    assert target.read_bytes() == b"existing"
