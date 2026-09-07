from __future__ import annotations

import json
from pathlib import Path

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
