"""Synthetic/offline tests for the ECB eurofxref import prototype."""

from pathlib import Path
from decimal import Decimal
import hashlib
import json
import subprocess
import sys

import pytest

from scripts import import_exchange_rates as importer


GESMES = "http://www.gesmes.org/xml/2002-08-01"
ECB = "http://www.ecb.int/vocabulary/2002-08-01/eurofxref"
URL_DAILY = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"


def fixture(days: dict[str, dict[str, str]], *, quote: str = "'") -> bytes:
    # ElementTree resolves namespace prefixes, so only the URIs matter here; the
    # default prefix names mirror the real ECB feed.
    envelope = "gesmes"
    cubes = "".join(
        f"<Cube time={quote}{day}{quote}>"
        + "".join(f"<Cube currency={quote}{ccy}{quote} rate={quote}{rate}{quote}/>"
                  for ccy, rate in rates.items())
        + "</Cube>"
        for day, rates in days.items()
    )
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<{envelope}:Envelope xmlns:{envelope}="{GESMES}" xmlns="{ECB}">'
        f"<{envelope}:subject>Reference rates</{envelope}:subject>"
        f"<{envelope}:Sender><{envelope}:name>European Central Bank</{envelope}:name></{envelope}:Sender>"
        f"<Cube>{cubes}</Cube></{envelope}:Envelope>"
    ).encode("utf-8")


def tiny() -> bytes:
    return fixture({
        "2026-10-08": {"USD": "1.1186", "CZK": "24.391", "GBP": "0.84712"},
        "2026-10-09": {"USD": "1.1206", "CZK": "24.369", "GBP": "0.84763"},
    })


def write_source(tmp_path: Path, name: str, raw: bytes) -> tuple[Path, str]:
    path = tmp_path / name
    path.write_bytes(raw)
    return path, URL_DAILY


def import_ok(tmp_path: Path, *fixtures: tuple[str, bytes], **kwargs) -> importer.ImportResult:
    sources = [write_source(tmp_path, name, raw) for name, raw in fixtures]
    return importer.import_exchange_rates(sources, **kwargs)


def import_errors(*args, **kwargs) -> str:
    result = import_ok(*args, **kwargs)
    assert not result.ok
    return " | ".join(result.errors)


def test_valid_fixture_parses_and_merges(tmp_path: Path) -> None:
    result = import_ok(tmp_path, ("daily.xml", tiny()))
    assert result.ok, result.errors
    merged = result.report["merged"]
    assert (merged["dates"], merged["rows"], merged["skippedDuplicateRows"]) == (2, 6, 0)
    assert merged["earliestDate"] == "2026-10-08" and merged["latestDate"] == "2026-10-09"
    assert merged["currencies"] == ["CZK", "GBP", "USD"]
    assert result.payload["baseCurrency"] == "EUR"
    rates = {row["date"]: row["rates"] for row in result.payload["dates"]}
    assert rates["2026-10-09"] == {"CZK": "24.369", "GBP": "0.84763", "USD": "1.1206"}


def test_double_quote_attributes_accepted() -> None:
    days = importer.parse_eurofxref_xml(fixture({"2026-10-09": {"USD": "1.1206"}}, quote='"'), "q.xml")
    assert days == {"2026-10-09": {"USD": "1.1206"}}


@pytest.mark.parametrize("raw,match", [
    (b'<?xml version="1.0"?><env:Envelope xmlns:env="http://example.org/drift"'
     b' xmlns="http://www.ecb.int/vocabulary/2002-08-01/eurofxref">'
     b"<env:subject>Reference rates</env:subject></env:Envelope>", "root must be gesmes:Envelope"),
    (b"not xml", "not well-formed XML"),
    (b'<?xml version="1.0"?><gesmes:Envelope xmlns:gesmes="http://www.gesmes.org/xml/2002-08-01"'
     b' xmlns="http://www.ecb.int/vocabulary/2002-08-01/eurofxref">'
     b"<gesmes:subject>Other rates</gesmes:subject></gesmes:Envelope>", "subject"),
    (b'<?xml version="1.0"?><gesmes:Envelope xmlns:gesmes="http://www.gesmes.org/xml/2002-08-01"'
     b' xmlns="http://www.ecb.int/vocabulary/2002-08-01/eurofxref">'
     b"<gesmes:subject>Reference rates</gesmes:subject>"
     b"<gesmes:Sender><gesmes:name>Some Other Bank</gesmes:name></gesmes:Sender>"
     b"<Cube></Cube></gesmes:Envelope>", "Sender"),
    (b"<!DOCTYPE r><r/>".replace(b"<!DOCTYPE r>", b""), "root must be gesmes:Envelope"),
])
def test_schema_drift_is_rejected(raw: bytes, match: str) -> None:
    with pytest.raises(ValueError, match=match):
        importer.parse_eurofxref_xml(raw, "drift.xml")


def test_dtd_and_entity_declarations_forbidden(tmp_path: Path) -> None:
    for name, prefix in (("dtd.xml", b'<?xml version="1.0"?><!DOCTYPE r []>'),
                         ("entity.xml", b'<?xml version="1.0"?><!ENTITY amp2 "x">')):
        path = tmp_path / name
        path.write_bytes(prefix + tiny())
        with pytest.raises(ValueError, match="DTD/entity declarations are forbidden"):
            importer.read_source_bytes(path)


@pytest.mark.parametrize("day", ["2026-13-09", "2026-02-30", "not-a-date", "2026-10-9",
                                 "2026-10-09T00:00:00Z", ""])
def test_malformed_dates_rejected(day: str) -> None:
    with pytest.raises(ValueError, match="date"):
        importer.parse_eurofxref_xml(fixture({day: {"USD": "1.1206"}}), "date.xml")


@pytest.mark.parametrize("currency", ["usd", "US", "USD2", "USD ", "EU R", ""])
def test_malformed_currency_codes_rejected(currency: str) -> None:
    with pytest.raises(ValueError, match="currency code"):
        importer.parse_eurofxref_xml(fixture({"2026-10-09": {currency: "1.1206"}}), "ccy.xml")


def test_eur_must_never_be_listed(tmp_path: Path) -> None:
    errors = import_errors(tmp_path, ("eur.xml", fixture({"2026-10-09": {"EUR": "1.0"}})))
    assert "implied base currency" in errors


@pytest.mark.parametrize("rate", ["0", "-1.1206", "+1.1206", "1.12 06", "nan", "inf",
                                  "1,1206", "1.1206 ", ".5", "1.", "0.0", ""])
def test_nonpositive_or_malformed_rates_rejected(rate: str) -> None:
    with pytest.raises(ValueError, match="rate"):
        importer.parse_eurofxref_xml(fixture({"2026-10-09": {"USD": rate}}), "rate.xml")


def test_duplicate_currency_within_date_rejected() -> None:
    raw = (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<gesmes:Envelope xmlns:gesmes="{GESMES}" xmlns="{ECB}">'
        f"<gesmes:subject>Reference rates</gesmes:subject>"
        f"<gesmes:Sender><gesmes:name>European Central Bank</gesmes:name></gesmes:Sender>"
        f"<Cube><Cube time='2026-10-09'>"
        f"<Cube currency='USD' rate='1.1206'/><Cube currency='USD' rate='1.1207'/>"
        f"</Cube></Cube></gesmes:Envelope>"
    ).encode("utf-8")
    with pytest.raises(ValueError, match="duplicate currency USD on 2026-10-09"):
        importer.parse_eurofxref_xml(raw, "dup.xml")


def test_duplicate_date_cube_within_file_rejected() -> None:
    raw = (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<gesmes:Envelope xmlns:gesmes="{GESMES}" xmlns="{ECB}">'
        f"<gesmes:subject>Reference rates</gesmes:subject>"
        f"<gesmes:Sender><gesmes:name>European Central Bank</gesmes:name></gesmes:Sender>"
        f"<Cube><Cube time='2026-10-09'><Cube currency='USD' rate='1.1206'/></Cube>"
        f"<Cube time='2026-10-09'><Cube currency='CZK' rate='24.369'/></Cube></Cube>"
        f"</gesmes:Envelope>"
    ).encode("utf-8")
    with pytest.raises(ValueError, match="duplicate date Cube"):
        importer.parse_eurofxref_xml(raw, "dupdate.xml")


def test_consistent_cross_file_duplicates_are_skipped(tmp_path: Path) -> None:
    result = import_ok(tmp_path, ("daily.xml", tiny()),
                       ("daily-copy.xml", fixture({"2026-10-09": {"USD": "1.1206", "CZK": "24.369",
                                                                  "GBP": "0.84763"}})))
    assert result.ok, result.errors
    assert result.report["merged"]["skippedDuplicateRows"] == 3
    assert result.report["merged"]["dates"] == 2 and result.report["merged"]["rows"] == 6


def test_conflicting_cross_file_duplicates_rejected(tmp_path: Path) -> None:
    errors = import_errors(tmp_path, ("a.xml", tiny()),
                           ("b.xml", fixture({"2026-10-09": {"USD": "9.9999"}})))
    assert "conflicting duplicate 2026-10-09 USD" in errors


def test_numerically_equal_lexemes_across_feeds_are_consistent(tmp_path: Path) -> None:
    # Real-feed anomaly: daily feed pads trailing zeros (136.80), history feed does not (136.8).
    result = import_ok(tmp_path, ("daily.xml", fixture({"2026-10-09": {"ISK": "136.80"}})),
                       ("hist.xml", fixture({"2026-10-09": {"ISK": "136.8"}})))
    assert result.ok, result.errors
    assert result.report["merged"]["skippedDuplicateRows"] == 1
    assert result.payload["dates"][0]["rates"]["ISK"] == "136.80"  # first lexeme wins, value-equal


def test_decimal_precision_lexeme_preserved() -> None:
    days = importer.parse_eurofxref_xml(tiny() + b"", "tiny.xml")  # sanity parse
    assert Decimal(days["2026-10-09"]["GBP"]) == Decimal("0.84763")
    fixed = importer.parse_eurofxref_xml(fixture({"2025-12-31": {"BGN": "1.9558"}}), "bgn.xml")
    assert fixed["2025-12-31"]["BGN"] == "1.9558"  # Bulgarian lev fixed rate stays exact
    assert Decimal(fixed["2025-12-31"]["BGN"]) == Decimal("0.0000") + Decimal("1.9558")


def test_rate_lexemes_never_serialized_as_floats(tmp_path: Path) -> None:
    result = import_ok(tmp_path, ("h.xml", fixture({"2021-01-04": {"IDR": "20036.94"}})))
    assert result.ok
    out = importer.serialize_payload(result.payload)
    assert b'"20036.94"' in out and b"20036.94," not in out.replace(b'"20036.94"', b"")


def test_serialization_is_deterministic_regardless_of_input_order(tmp_path: Path) -> None:
    forward = import_ok(tmp_path, ("f.xml", fixture({"2026-10-08": {"USD": "1.1186", "CZK": "24.391"},
                                                     "2026-10-09": {"GBP": "0.84763", "USD": "1.1206"}})))
    reversed_order = import_ok(tmp_path, ("r.xml", fixture({"2026-10-09": {"USD": "1.1206", "GBP": "0.84763"},
                                                            "2026-10-08": {"CZK": "24.391", "USD": "1.1186"}})))
    assert forward.ok and reversed_order.ok
    # Merged date/rate content and its serialization are order-independent.
    assert forward.payload["dates"] == reversed_order.payload["dates"]
    assert importer.serialize_payload({"dates": forward.payload["dates"]}) == \
        importer.serialize_payload({"dates": reversed_order.payload["dates"]})


def test_dry_run_writes_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    result = import_ok(tmp_path, ("f.xml", tiny()), output=importer.DEFAULT_OUTPUT, dry_run=True)
    assert result.ok and result.report["dryRun"] is True and result.report["wrotePreview"] is False
    assert not result.wrote_files
    preview = importer.DEFAULT_OUTPUT
    before = preview.read_bytes() if preview.exists() else None
    import_ok(tmp_path, ("f2.xml", tiny()), dry_run=True)
    assert (preview.read_bytes() if preview.exists() else None) == before
    monkeypatch.undo() if False else None


def test_preview_path_cannot_promote_to_production_or_escape(tmp_path: Path) -> None:
    for path in (importer.ROOT / "data" / "exchange_rates.json", tmp_path / "preview.json",
                 importer.GENERATED_DIR / ".." / "exchange_rates.json",
                 importer.GENERATED_DIR / "preview.xml"):
        with pytest.raises(ValueError, match="preview output must be"):
            importer.validate_preview_path(path)


def test_preview_path_accepts_only_generated_json() -> None:
    assert importer.validate_preview_path(importer.DEFAULT_OUTPUT) == importer.DEFAULT_OUTPUT.resolve()


def test_write_preview_only_into_generated(tmp_path: Path) -> None:
    target = importer.GENERATED_DIR / "exchange_rates_test_preview.json"
    try:
        if target.exists():
            target.unlink()
        result = import_ok(tmp_path, ("f.xml", tiny()), dry_run=False, write_preview=True, output=target)
        assert result.ok and result.report["dryRun"] is False and result.report["wrotePreview"] is True
        assert result.wrote_files == [target.resolve()]
        written = json.loads(target.read_text(encoding="utf-8"))
        assert written["status"] == "unapproved-research-preview"
        assert written["baseCurrency"] == "EUR"
    finally:
        if target.exists():
            target.unlink()


def test_source_hash_and_url_recorded(tmp_path: Path) -> None:
    raw = tiny()
    path, url = write_source(tmp_path, "sha.xml", raw)
    result = importer.import_exchange_rates([(path, url)],
                                            retrieved_at="2026-10-11T21:27:46Z", dry_run=True)
    assert result.ok, result.errors
    source = result.payload["sources"][0]
    assert source["sha256"] == hashlib.sha256(raw).hexdigest()
    assert source["sourceUrl"] == URL_DAILY
    assert source["bytes"] == len(raw)
    assert source["retrievedAt"] == "2026-10-11T21:27:46Z"
    assert source["earliestDate"] == "2026-10-08" and source["latestDate"] == "2026-10-09"


def test_retrieved_at_must_be_iso_timestamp(tmp_path: Path) -> None:
    path, url = write_source(tmp_path, "f.xml", tiny())
    result = importer.import_exchange_rates([(path, url)], retrieved_at="last tuesday")
    assert not result.ok and "ISO-8601" in result.errors[0]


def test_source_argument_requires_path_equals_https_url() -> None:
    assert importer.parse_source_argument(f"a.xml={URL_DAILY}") == (Path("a.xml"), URL_DAILY)
    for bad in ("a.xml", "=https://x/", "a.xml=http://insecure", "a.xml="):
        with pytest.raises(ValueError):
            importer.parse_source_argument(bad)


def test_cli_dry_run_and_write_preview_are_mutually_exclusive(tmp_path: Path) -> None:
    path, url = write_source(tmp_path, "cli.xml", tiny())
    script = importer.ROOT / "scripts" / "import_exchange_rates.py"
    base = [sys.executable, str(script), "--source", f"{path}={url}"]
    both = subprocess.run(base + ["--dry-run", "--write-preview"], capture_output=True, text=True)
    assert both.returncode != 0 and "not allowed" in both.stderr
    dry = subprocess.run(base + ["--dry-run"], capture_output=True)
    assert dry.returncode == 0
    report = json.loads(dry.stdout.decode("utf-8"))
    assert report["ok"] is True and report["dryRun"] is True
    assert report["merged"]["dates"] == 2


URL_HIST = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.xml"


def hist_source(tmp_path: Path, raw: bytes) -> tuple[Path, str]:
    path = tmp_path / "eurofxref-hist.xml"
    path.write_bytes(raw)
    return path, URL_HIST


def production_target(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    target = tmp_path / "exchange_rates.json"
    monkeypatch.setattr(importer, "PRODUCTION_OUTPUT", target)
    return target


def production_import(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, raw: bytes,
                      **kwargs) -> importer.ImportResult:
    target = production_target(tmp_path, monkeypatch)
    source = hist_source(tmp_path, raw)
    return importer.import_exchange_rates([source], dry_run=False, write_production=True,
                                          output=target, **kwargs)


def test_production_output_path_is_restricted(tmp_path: Path) -> None:
    assert importer.validate_production_path(importer.PRODUCTION_OUTPUT) == \
        importer.PRODUCTION_OUTPUT.resolve()
    for path in (tmp_path / "exchange_rates.json", importer.DEFAULT_OUTPUT,
                 importer.ROOT / "data" / "exchange_rates_preview.json"):
        with pytest.raises(ValueError, match="restricted to data/exchange_rates.json"):
            importer.validate_production_path(path)


def test_production_mode_requires_single_canonical_source(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target = production_target(tmp_path, monkeypatch)
    wrong_url = import_errors(tmp_path, ("hist.xml", tiny()), dry_run=False, write_production=True,
                              output=target)
    assert "canonical URL" in wrong_url
    path_a = tmp_path / "a.xml"
    path_a.write_bytes(tiny())
    path_b = tmp_path / "b.xml"
    path_b.write_bytes(tiny())
    two = importer.import_exchange_rates([(path_a, URL_HIST), (path_b, URL_HIST)], dry_run=False,
                                         write_production=True, output=target)
    assert not two.ok and "canonical URL" in two.errors[0]


def test_production_modes_are_mutually_exclusive(tmp_path: Path) -> None:
    path, url = write_source(tmp_path, "modes.xml", tiny())
    for kwargs in (dict(dry_run=True, write_preview=True),
                   dict(dry_run=True, write_production=True),
                   dict(write_preview=True, write_production=True),
                   dict(dry_run=False, write_preview=False, write_production=False)):
        result = importer.import_exchange_rates([(path, url)], **kwargs)
        assert not result.ok and "exactly one" in result.errors[0]


def test_production_write_creates_house_payload(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target = production_target(tmp_path, monkeypatch)
    source = hist_source(tmp_path, tiny())
    result = importer.import_exchange_rates([source], dry_run=False, write_production=True,
                                            output=target)
    assert result.ok, result.errors
    assert result.report["dryRun"] is False and result.report["wroteProduction"] is True
    assert result.report["refresh"] is None
    written = json.loads(target.read_text(encoding="utf-8"))
    metadata = written["metadata"]
    assert metadata["publisher"] == "European Central Bank"
    assert metadata["sourceUrl"] == URL_HIST
    assert metadata["sourceSha256"] == hashlib.sha256(tiny()).hexdigest()
    assert metadata["baseCurrency"] == "EUR"
    assert metadata["directionSemantics"] == "1 EUR = rate units of the foreign currency"
    assert "information purposes only" in metadata["notice"]
    assert metadata["earliestDate"] == "2026-10-08" and metadata["latestDate"] == "2026-10-09"
    assert metadata["lastUpdated"] == metadata["latestDate"] and metadata["complete"] is True
    assert (metadata["dateCount"], metadata["rateRowCount"]) == (2, 6)
    dates = written["dates"]
    assert [entry["date"] for entry in dates] == ["2026-10-08", "2026-10-09"]
    assert dates[1]["rates"] == {"CZK": "24.369", "GBP": "0.84763", "USD": "1.1206"}
    # No research-preview marker, no floats, no local machine paths.
    blob = target.read_bytes()
    payload_text = blob.decode("utf-8")
    assert "unapproved-research-preview" not in payload_text
    assert '"1.1206"' in payload_text
    assert str(tmp_path) not in payload_text and str(source[0]) not in payload_text
    assert set(written) == {"metadata", "dates"}
    assert result.payload == written
    assert result.report["outputBytes"] == len(blob)
    assert result.report["outputSha256"] == hashlib.sha256(blob).hexdigest()


def test_production_write_is_deterministic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    first = production_import(tmp_path, monkeypatch, tiny())
    assert first.ok
    blob = (tmp_path / "exchange_rates.json").read_bytes()
    again = production_import(tmp_path, monkeypatch, tiny())
    assert again.ok
    assert (tmp_path / "exchange_rates.json").read_bytes() == blob


def test_production_refresh_reports_append_only_growth(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    first = production_import(tmp_path, monkeypatch, tiny())
    assert first.ok
    grown = fixture({
        "2026-10-08": {"USD": "1.1186", "CZK": "24.391", "GBP": "0.84712"},
        "2026-10-09": {"USD": "1.1206", "CZK": "24.369", "GBP": "0.84763"},
        "2026-10-12": {"USD": "1.1300", "CZK": "24.350", "GBP": "0.84800", "CHF": "0.9000"},
    })
    refresh = production_import(tmp_path, monkeypatch, grown)
    assert refresh.ok, refresh.errors
    diff = refresh.report["refresh"]
    assert diff["oldLatestDate"] == "2026-10-09" and diff["newLatestDate"] == "2026-10-12"
    assert (diff["oldDateCount"], diff["newDateCount"], diff["addedDates"]) == (2, 3, 1)
    assert diff["addedDatesSample"] == ["2026-10-12"]
    assert diff["removedDates"] == 0 and diff["historicalChanges"] == 0
    assert diff["currenciesNewlySeen"] == ["CHF"]
    assert diff["currenciesNoLongerOnLatest"] == []


def test_production_refresh_reports_currency_leaving_latest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    first = production_import(tmp_path, monkeypatch, tiny())
    assert first.ok
    grown = fixture({
        "2026-10-08": {"USD": "1.1186", "CZK": "24.391", "GBP": "0.84712"},
        "2026-10-09": {"USD": "1.1206", "CZK": "24.369", "GBP": "0.84763"},
        "2026-10-12": {"USD": "1.1300", "CZK": "24.350"},
    })
    refresh = production_import(tmp_path, monkeypatch, grown)
    assert refresh.ok, refresh.errors
    assert refresh.report["refresh"]["currenciesNoLongerOnLatest"] == ["GBP"]


def test_production_refresh_blocks_historical_rewrite(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    first = production_import(tmp_path, monkeypatch, tiny())
    assert first.ok
    before = (tmp_path / "exchange_rates.json").read_bytes()
    rewritten = fixture({
        "2026-10-08": {"USD": "1.9999", "CZK": "24.391", "GBP": "0.84712"},
        "2026-10-09": {"USD": "1.1206", "CZK": "24.369", "GBP": "0.84763"},
    })
    blocked = production_import(tmp_path, monkeypatch, rewritten)
    assert not blocked.ok
    assert "rewrite or remove existing history" in blocked.errors[0]
    assert "--acknowledge-changes" in blocked.errors[0]
    assert (tmp_path / "exchange_rates.json").read_bytes() == before  # untouched
    acknowledged = production_import(tmp_path, monkeypatch, rewritten, acknowledge_changes=True)
    assert acknowledged.ok, acknowledged.errors
    diff = acknowledged.report["refresh"]
    assert diff["historicalChanges"] == 1
    assert diff["historicalChangesSample"] == [
        {"date": "2026-10-08", "currency": "USD", "from": "1.1186", "to": "1.9999"}]


def test_production_refresh_blocks_truncated_history(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    first = production_import(tmp_path, monkeypatch, tiny())
    assert first.ok
    truncated = fixture({"2026-10-09": {"USD": "1.1206", "CZK": "24.369", "GBP": "0.84763"}})
    blocked = production_import(tmp_path, monkeypatch, truncated)
    assert not blocked.ok and "removedDates=1" in blocked.errors[0]
    acknowledged = production_import(tmp_path, monkeypatch, truncated, acknowledge_changes=True)
    assert acknowledged.ok
    assert acknowledged.report["refresh"]["removedDatesSample"] == ["2026-10-08"]


def test_cli_production_mode_guardrails(tmp_path: Path) -> None:
    # Library-level production writes are covered above; CLI checks stay parser-level
    # so tests never write into the real data/exchange_rates.json.
    source = tmp_path / "hist.xml"
    source.write_bytes(tiny())
    script = importer.ROOT / "scripts" / "import_exchange_rates.py"
    base = [sys.executable, str(script), "--source", f"{source}={URL_HIST}"]
    stray_flag = subprocess.run(base + ["--dry-run", "--acknowledge-changes"],
                                capture_output=True, text=True)
    assert stray_flag.returncode != 0 and "only applies" in stray_flag.stderr
    custom_output = subprocess.run(
        base + ["--write-production", "--output", str(tmp_path / "elsewhere.json")],
        capture_output=True, text=True)
    assert custom_output.returncode != 0 and "not configurable" in custom_output.stderr
