from __future__ import annotations

import json
import zipfile
from pathlib import Path

from scripts.import_vat_registrations import PRODUCTION_OUTPUT, run_import
from scripts.validate_datasets import validate_vat_registrations_payload


def _xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<ZoznamSubjektovRegistrovanychkDPH>
  <DatumAktualizacieZoznamu>28092026</DatumAktualizacieZoznamu>
  <DS_DPHS>
    <ITEM>
      <IC_DPH>SK2121623757</IC_DPH>
      <ICO>54307945</ICO>
      <NAZOV_DS>Hidden Person Or Entity</NAZOV_DS>
      <OBEC>Liptovský Mikuláš</OBEC>
      <PSC>03101</PSC>
      <ULICA_CISLO>Hidden 1</ULICA_CISLO>
      <STAT>Slovensko</STAT>
      <DRUH_REG_DPH>§4</DRUH_REG_DPH>
      <DATUM_REG>14.12.2023</DATUM_REG>
      <PLAT_DPH_OD>14.12.2023</PLAT_DPH_OD>
    </ITEM>
    <ITEM>
      <IC_DPH>SK2020273497</IC_DPH>
      <ICO>35760788</ICO>
      <NAZOV_DS>Hidden Name</NAZOV_DS>
      <OBEC>Bratislava</OBEC>
      <PSC>81105</PSC>
      <ULICA_CISLO>Hidden 2</ULICA_CISLO>
      <STAT>Slovensko</STAT>
      <DRUH_REG_DPH>§7a</DRUH_REG_DPH>
      <DATUM_REG>08.07.2026</DATUM_REG>
    </ITEM>
  </DS_DPHS>
</ZoznamSubjektovRegistrovanychkDPH>
"""


def _write_zip(path: Path, xml_text: str = "") -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("ds_dphs.xml", xml_text or _xml())
        archive.writestr("ds_dphs.xsd", "<schema />")
    return path


def test_vat_importer_writes_deterministic_generated_json(tmp_path: Path) -> None:
    source = _write_zip(tmp_path / "ds_dphs.zip")
    output_one = tmp_path / "one.json"
    output_two = tmp_path / "two.json"

    result_one = run_import(source, output_path=output_one, write=True)
    result_two = run_import(source, output_path=output_two, write=True)

    assert result_one.ok
    assert result_two.ok
    assert output_one.read_text(encoding="utf-8") == output_two.read_text(encoding="utf-8")

    payload = json.loads(output_one.read_text(encoding="utf-8"))
    assert payload["metadata"]["lastUpdated"] == "2026-09-28"
    assert payload["metadata"]["privacyGate"] == "PRIVACY_IMPORT_BLOCKED"
    assert [record["ico"] for record in payload["vatRegistrations"]] == ["35760788", "54307945"]
    assert payload["vatRegistrations"][0]["registrations"][0] == {
        "registrationType": "§7a",
        "registrationTypeChangedOn": None,
        "registeredOn": "2026-07-08",
        "vatId": "SK2020273497",
        "vatPayerFrom": None,
    }
    encoded = json.dumps(payload, ensure_ascii=False)
    assert "NAZOV_DS" not in encoded
    assert "Hidden" not in encoded
    assert "ULICA_CISLO" not in encoded


def test_vat_importer_reports_invalid_values(tmp_path: Path) -> None:
    source = tmp_path / "broken.xml"
    source.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<ZoznamSubjektovRegistrovanychkDPH><DatumAktualizacieZoznamu>28092026</DatumAktualizacieZoznamu><DS_DPHS>
<ITEM><IC_DPH>BAD</IC_DPH><ICO>123</ICO><DRUH_REG_DPH>§4</DRUH_REG_DPH><DATUM_REG>bad</DATUM_REG></ITEM>
<ITEM><IC_DPH>SK2121623757</IC_DPH><DRUH_REG_DPH>§4</DRUH_REG_DPH><DATUM_REG>14.12.2023</DATUM_REG></ITEM>
</DS_DPHS></ZoznamSubjektovRegistrovanychkDPH>
""",
        encoding="utf-8",
    )

    result = run_import(source, output_path=tmp_path / "out.json", write=False)

    assert result.ok
    assert result.invalid_icos == 1
    assert result.records_without_ico == 1
    assert result.record_count == 0


def test_vat_importer_refuses_production_promotion(monkeypatch, tmp_path: Path) -> None:
    source = _write_zip(tmp_path / "ds_dphs.zip")
    production_path = tmp_path / "data" / "vat_registrations.json"
    monkeypatch.setattr("scripts.import_vat_registrations.PRODUCTION_OUTPUT", production_path)

    result = run_import(source, output_path=production_path, write=True)

    assert not result.ok
    assert not production_path.exists()
    assert any("privacy gate is blocked" in error for error in result.errors)


def test_vat_validation_rejects_personal_fields() -> None:
    report = validate_vat_registrations_payload(
        {
            "metadata": {"source": "unit-test", "lastUpdated": "2026-09-28"},
            "vatRegistrations": [
                {
                    "ico": "12345678",
                    "name": "Hidden Name",
                    "registrations": [
                        {
                            "vatId": "SK2121623757",
                            "registrationType": "§4",
                            "registeredOn": "2023-12-14",
                            "vatPayerFrom": "2023-12-14",
                            "registrationTypeChangedOn": None,
                        }
                    ],
                }
            ],
        }
    )

    assert not report.ok
    assert any("forbidden" in issue.message and "name" in issue.message for issue in report.errors)


def test_vat_validation_rejects_duplicate_registration() -> None:
    registration = {
        "vatId": "SK2121623757",
        "registrationType": "§4",
        "registeredOn": "2023-12-14",
        "vatPayerFrom": "2023-12-14",
        "registrationTypeChangedOn": None,
    }
    report = validate_vat_registrations_payload(
        {
            "metadata": {"source": "unit-test", "lastUpdated": "2026-09-28"},
            "vatRegistrations": [{"ico": "12345678", "registrations": [registration, dict(registration)]}],
        }
    )

    assert not report.ok
    assert any("duplicate VAT registration" in issue.message for issue in report.errors)
