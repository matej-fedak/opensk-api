from __future__ import annotations

import csv
import json
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from scripts.import_geography import run_import
from scripts.import_utils import load_dataset_records


def _write_xlsx(path: Path, rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    def cell(ref: str, value: str) -> str:
        return f'<c r="{ref}" t="inlineStr"><is><t>{escape(value)}</t></is></c>'

    def row_xml(row_number: int, values: list[str]) -> str:
        cells = "".join(cell(f"{chr(65 + index)}{row_number}", value) for index, value in enumerate(values))
        return f'<row r="{row_number}">{cells}</row>'

    file_info_sheet = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>File info</t></is></c></row></sheetData>'
        '</worksheet>'
    )
    sk_sheet = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{row_xml(1, ["LAU CODE", "LAU NAME NATIONAL", "NUTS3", "COUNTRY"])}'
        + "".join(row_xml(index + 2, row) for index, row in enumerate(rows))
        + '</sheetData></worksheet>'
    )

    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets>'
        '<sheet name="File_info" sheetId="1" r:id="rId1"/>'
        '<sheet name="SK" sheetId="2" r:id="rId2"/>'
        '</sheets>'
        '</workbook>'
    )

    workbook_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>'
        '</Relationships>'
    )

    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        '</Relationships>'
    )

    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '</Types>'
    )

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", root_rels)
        archive.writestr("xl/workbook.xml", workbook_xml)
        archive.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        archive.writestr("xl/worksheets/sheet1.xml", file_info_sheet)
        archive.writestr("xl/worksheets/sheet2.xml", sk_sheet)


def _regions_payload() -> list[dict[str, str]]:
    return [
        {"code": "SK010", "name": "Bratislavský kraj", "nameEn": "Bratislava Region", "country": "SK"},
        {"code": "SK021", "name": "Trnavský kraj", "nameEn": "Trnava Region", "country": "SK"},
        {"code": "SK022", "name": "Trenčiansky kraj", "nameEn": "Trenčín Region", "country": "SK"},
        {"code": "SK023", "name": "Nitriansky kraj", "nameEn": "Nitra Region", "country": "SK"},
        {"code": "SK031", "name": "Žilinský kraj", "nameEn": "Žilina Region", "country": "SK"},
        {"code": "SK032", "name": "Banskobystrický kraj", "nameEn": "Banská Bystrica Region", "country": "SK"},
        {"code": "SK041", "name": "Prešovský kraj", "nameEn": "Prešov Region", "country": "SK"},
        {"code": "SK042", "name": "Košický kraj", "nameEn": "Košice Region", "country": "SK"},
    ]


def _municipality_rows() -> list[list[str]]:
    return [
        ["507814", "Bernolákovo", "SK010", "SK"],
        ["507822", "Blatné", "SK010", "SK"],
        ["503681", "Boldog", "SK010", "SK"],
        ["528595", "Bratislava - Staré Mesto", "SK010", "SK"],
        ["581001", "Trnava", "SK021", "SK"],
        ["581002", "Smolenice", "SK021", "SK"],
    ]


def test_json_import_validates_without_writing(tmp_path: Path) -> None:
    input_file = tmp_path / "regions.json"
    input_file.write_text(json.dumps(_regions_payload(), ensure_ascii=False), encoding="utf-8")

    output_dir = tmp_path / "output"
    result = run_import(
        dataset="regions",
        source="unit-test",
        input_path=input_file,
        output_path=output_dir,
        write=False,
        allow_incomplete=True,
    )

    assert result.validation_reports[0].ok
    assert result.wrote_files == []
    assert not result.integrity_errors
    assert not (output_dir / "regions.json").exists()


def test_csv_import_writes_single_dataset(tmp_path: Path) -> None:
    input_file = tmp_path / "regions.csv"
    with input_file.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["code", "name", "nameEn", "country"])
        writer.writeheader()
        for record in _regions_payload():
            writer.writerow(record)

    records = load_dataset_records("regions", input_file)
    assert len(records) == 8

    output_dir = tmp_path / "output"
    result = run_import(
        dataset="regions",
        source="unit-test",
        input_path=input_file,
        output_path=output_dir,
        write=True,
        allow_incomplete=True,
    )

    output_file = output_dir / "regions.json"
    assert output_file.exists()
    assert result.wrote_files == [output_file]

    payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert payload["metadata"]["source"] == "unit-test"
    assert payload["regions"] == _regions_payload()


def test_xlsx_import_supports_partial_municipalities(tmp_path: Path) -> None:
    input_file = tmp_path / "municipalities.xlsx"
    _write_xlsx(input_file, _municipality_rows())

    records = load_dataset_records("municipalities", input_file)
    assert len(records) == len(_municipality_rows())
    assert all(record["districtCode"] is None for record in records)

    output_dir = tmp_path / "output"
    result = run_import(
        dataset="municipalities",
        source="Eurostat LAU 2025 correspondence table",
        input_path=input_file,
        output_path=output_dir,
        write=True,
        allow_incomplete=False,
    )

    output_file = output_dir / "municipalities.json"
    assert result.ok
    assert result.wrote_files == [output_file]

    payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert payload["metadata"]["complete"] is False
    assert payload["municipalities"] == sorted(records, key=lambda record: (record["regionCode"], record.get("districtCode") or "", record["name"], record["code"]))


def test_duplicate_municipality_codes_are_rejected(tmp_path: Path) -> None:
    input_file = tmp_path / "municipalities.json"
    input_file.write_text(
        json.dumps(
            [
                {"code": "507814", "name": "Bernolákovo", "regionCode": "SK010", "districtCode": None, "country": "SK"},
                {"code": "507814", "name": "Bernolákovo", "regionCode": "SK010", "districtCode": None, "country": "SK"},
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_import(
        dataset="municipalities",
        source="unit-test",
        input_path=input_file,
        output_path=tmp_path / "output",
        write=False,
        allow_incomplete=False,
    )

    assert not result.validation_reports[0].ok
    assert any("duplicate municipality code" in issue.message for issue in result.validation_reports[0].errors)
