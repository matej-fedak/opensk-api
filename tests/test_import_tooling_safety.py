"""Small synthetic regressions: no network, large allocations or repository writes."""

import io
import zipfile
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock
from urllib.request import Request

import pytest

from scripts import fetch_source, fetch_vat_registrations, fetch_procurement_notices
from scripts import import_utils, import_vat_registrations, import_exchange_rates
from scripts import source_safety
from scripts.import_itms21_projects import money_string


@pytest.mark.parametrize("reference", ["ZZZZZZ1", "XFE1", "A0", "1", "é1", "A-1"])
def test_xlsx_rejects_invalid_or_out_of_range_column_before_allocation(reference):
    with pytest.raises(ValueError, match="limit|reference"):
        import_utils._xlsx_column_index(reference)


def test_xlsx_last_supported_column():
    assert import_utils._xlsx_column_index("XFD1048576") == 16383


@pytest.mark.parametrize("members,kwargs,message", [
    ([SimpleNamespace(file_size=11, compress_size=10)], {"member_limit": 10, "total_limit": 20}, "member uncompressed"),
    ([SimpleNamespace(file_size=6, compress_size=6)] * 2, {"member_limit": 10, "total_limit": 10}, "uncompressed size"),
    ([SimpleNamespace(file_size=21, compress_size=1)], {"member_limit": 30, "total_limit": 30, "max_ratio": 20}, "ratio"),
    ([SimpleNamespace(file_size=1, compress_size=1)] * 2, {"member_limit": 10, "total_limit": 10, "max_members": 1}, "too many"),
])
def test_zip_metadata_limits_without_decompression(members, kwargs, message):
    archive = SimpleNamespace(infolist=lambda: members)
    with pytest.raises(ValueError, match=message):
        source_safety.check_zip_limits(archive, **kwargs)


def _xlsx(tmp_path, cells):
    path = tmp_path / "test.xlsx"
    ns = import_utils.XLSX_NS["main"]
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("xl/workbook.xml", f'<workbook xmlns="{ns}" xmlns:r="{import_utils.XLSX_NS["officeRel"]}"><sheets><sheet name="SK" r:id="r1"/></sheets></workbook>')
        archive.writestr("xl/_rels/workbook.xml.rels", f'<Relationships xmlns="{import_utils.XLSX_NS["rel"]}"><Relationship Id="r1" Target="worksheets/sheet1.xml"/></Relationships>')
        archive.writestr("xl/worksheets/sheet1.xml", f'<worksheet xmlns="{ns}"><sheetData>{cells}</sheetData></worksheet>')
    return path


def test_xlsx_actual_and_expanded_cell_limits(tmp_path, monkeypatch):
    path = _xlsx(tmp_path, '<row><c r="C1"><v>1</v></c></row>')
    monkeypatch.setattr(import_utils, "XLSX_MAX_OUTPUT_CELLS", 2)
    with pytest.raises(ValueError, match="expanded cell"):
        import_utils._xlsx_rows(path)
    monkeypatch.setattr(import_utils, "XLSX_MAX_OUTPUT_CELLS", 10)
    monkeypatch.setattr(import_utils, "XLSX_MAX_CELLS", 1)
    path = _xlsx(tmp_path, '<row><c r="A1"/><c r="B1"/></row>')
    with pytest.raises(ValueError, match="element count"):
        import_utils._xlsx_rows(path)


def test_vat_zip_rejects_member_before_read(tmp_path, monkeypatch):
    path = tmp_path / "vat.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("vat.xml", "<root>test</root>")
    monkeypatch.setattr(import_vat_registrations, "MAX_XML_BYTES", 4)
    read = Mock(side_effect=AssertionError("must not decompress"))
    monkeypatch.setattr(zipfile.ZipFile, "open", read)
    result = import_vat_registrations.run_import(path)
    assert not result.ok
    assert "uncompressed size" in result.errors[0]
    read.assert_not_called()


@pytest.mark.parametrize("value", [Decimal("1e200"), Decimal("1e-200"), Decimal("0e-200")])
def test_fixed_point_money_is_bounded_before_formatting(value):
    with pytest.raises(ValueError, match="fixed-point length"):
        money_string({"amount": value}, "amount", "test", mandatory=True)


def test_money_preserves_exact_significant_digits():
    assert money_string({"amount": Decimal("12345678901234567890.00100")}, "amount", "test", mandatory=True) == "12345678901234567890.001"


@pytest.mark.parametrize("encoding", ["utf-8", "utf-16", "utf-16-le", "utf-16-be"])
def test_encoding_aware_dtd_rejection_at_read_and_direct_parser(tmp_path, encoding):
    raw = '<!DOCTYPE root [<!ENTITY small "test">]><root>&small;</root>'.encode(encoding)
    path = tmp_path / "source.xml"
    path.write_bytes(raw)
    with pytest.raises(ValueError, match="DTD/entity"):
        import_exchange_rates.read_source_bytes(path)
    with pytest.raises(ValueError, match="DTD/entity"):
        import_exchange_rates.parse_eurofxref_xml(raw, "source")


def test_bounded_read_requests_only_limit_plus_one():
    stream = SimpleNamespace(read=Mock(return_value=b"12345"))
    with pytest.raises(ValueError, match="byte limit"):
        source_safety.read_bounded(stream, 4)
    stream.read.assert_called_once_with(5)


def test_streaming_deadline_stops_slow_drip_reads(monkeypatch):
    clock = iter([0, 0, 1, 2, 11])
    monkeypatch.setattr(source_safety.time, "monotonic", lambda: next(clock))
    stream = SimpleNamespace(read=Mock(side_effect=AssertionError("must use read1")),
                             read1=Mock(return_value=b"x"))
    with pytest.raises(TimeoutError, match="time budget"):
        source_safety.read_bounded(stream, 100, max_seconds=10)
    assert stream.read1.call_count == 2
    stream.read.assert_not_called()


def test_bounded_read_accumulates_partial_reads():
    stream = SimpleNamespace(read=Mock(side_effect=[b"ab", b"c", b""]))
    assert source_safety.read_bounded(stream, 3) == b"abc"


@pytest.mark.parametrize("timeout", [0, -1, float("nan"), float("inf"), 301])
def test_all_legacy_fetchers_reject_bad_timeout_without_network(monkeypatch, timeout):
    opener = Mock(side_effect=AssertionError("network must not be used"))
    for module in (fetch_source, fetch_vat_registrations, fetch_procurement_notices):
        monkeypatch.setattr(module, "open_https", opener)
    with pytest.raises(ValueError, match="timeout"):
        fetch_source._fetch_bytes("https://example.com/source", timeout)
    with pytest.raises(ValueError, match="timeout"):
        fetch_vat_registrations.fetch(fetch_vat_registrations.DEFAULT_URL, timeout=timeout, retries=0)
    with pytest.raises(ValueError, match="timeout"):
        fetch_procurement_notices.fetch_search_response(1, timeout=timeout)
    opener.assert_not_called()


@pytest.mark.parametrize("module,url", [
    (fetch_source, "https://example.com/source"),
    (fetch_vat_registrations, fetch_vat_registrations.DEFAULT_URL),
    (fetch_procurement_notices, fetch_procurement_notices.TED_SEARCH_URL),
])
def test_legacy_fetchers_bound_response_before_write(monkeypatch, module, url):
    class Response(io.BytesIO):
        def geturl(self):
            return url

    monkeypatch.setattr(module, "MAX_DOWNLOAD_BYTES", 4)
    monkeypatch.setattr(module, "open_https", lambda *args, **kwargs: Response(b"12345"))
    with pytest.raises(ValueError, match="byte limit"):
        if module is fetch_source:
            module._fetch_bytes(url, 1)
        elif module is fetch_vat_registrations:
            module.fetch(url, timeout=1, retries=0)
        else:
            module.fetch_search_response(1, timeout=1)


@pytest.mark.parametrize("url", ["http://example.com/a", "file:///local", "https://user:secret@example.com/a", "https://example.com:80/a"])
def test_https_policy_rejects_unsafe_sources_and_redirects_before_open(monkeypatch, url):
    builder = Mock()
    monkeypatch.setattr(source_safety.request, "build_opener", builder)
    with pytest.raises(ValueError, match="HTTPS"):
        source_safety.open_https(url, timeout=1)
    builder.assert_not_called()


@pytest.mark.parametrize("destination", ["http://example.com/a", "https://elsewhere.example/a"])
def test_each_redirect_is_checked_before_following(monkeypatch, destination):
    def build_opener(handler):
        with pytest.raises(ValueError):
            handler.redirect_request(Request("https://example.com/a"), None, 302, "Found", {}, destination)
        return SimpleNamespace(open=lambda *args, **kwargs: "not followed")

    monkeypatch.setattr(source_safety.request, "build_opener", build_opener)
    assert source_safety.open_https("https://example.com/a", timeout=1, allowed_hosts={"example.com"}) == "not followed"


def test_atomic_writer_cleans_up_failed_replacement(tmp_path, monkeypatch):
    output = tmp_path / "output.json"
    output.write_bytes(b"existing")
    monkeypatch.setattr(import_utils.os, "replace", Mock(side_effect=OSError("failed")))
    with pytest.raises(OSError, match="failed"):
        import_utils.write_json_atomic(output, {"test": True})
    assert output.read_bytes() == b"existing"
    assert list(tmp_path.iterdir()) == [output]
