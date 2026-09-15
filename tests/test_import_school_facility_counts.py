from pathlib import Path

from scripts.import_school_facility_counts import run_import


CSV_HEADER = "Druh školy skrátený;Typ školy skrátený;Druh 1;Druh 2;Kraj názov;NUTS3;Okres názov;LAU1;Počet organizačných zložiek;Zriaďovateľ - Forma vlastníctva názov;Zriaďovateľ - Typ názov;"


def _write_fixture(path: Path, rows: list[str]) -> None:
    path.write_text(CSV_HEADER + "\n" + "\n".join(rows) + "\n", encoding="utf-8")


def test_school_facility_import_maps_headers_and_alpha_lau(tmp_path: Path) -> None:
    source = tmp_path / "schools.csv"
    output = tmp_path / "school_facility_counts.json"
    _write_fixture(
        source,
        ["MŠ;MŠ;MŠ;MŠ;Žilinský;SK031;Žilina;SK031B;78;štátna;obec, mesto;"],
    )

    result = run_import(input_path=source, output_path=output, last_updated="2025-09-15", write=True)

    assert result.ok
    assert result.total_source_rows == 1
    assert result.imported_records == 1
    assert result.district_links == 1
    assert output.is_file()
    assert '"districtCode": "SK03111"' in output.read_text(encoding="utf-8")


def test_school_facility_import_skips_duplicate_aggregate_rows(tmp_path: Path) -> None:
    source = tmp_path / "schools.csv"
    output = tmp_path / "school_facility_counts.json"
    row = "GYM;GYM;SŠ;GYM;Trenčiansky;SK022;Trenčín;SK0229;1;štátna;samosprávny kraj;"
    _write_fixture(source, [row, row])

    result = run_import(input_path=source, output_path=output, last_updated="2025-09-15", write=False)

    assert result.ok
    assert result.total_source_rows == 2
    assert result.imported_records == 1
    assert result.duplicate_records == 1
    assert result.skipped_records == 1


def test_school_facility_import_rejects_unexpected_headers(tmp_path: Path) -> None:
    source = tmp_path / "schools.csv"
    output = tmp_path / "school_facility_counts.json"
    source.write_text("schoolCode;schoolName\n1;Name\n", encoding="utf-8")

    try:
        run_import(input_path=source, output_path=output, last_updated="2025-09-15", write=False)
    except ValueError as exc:
        assert "unexpected CSV headers" in str(exc)
    else:
        raise AssertionError("expected unexpected school-level headers to fail")
