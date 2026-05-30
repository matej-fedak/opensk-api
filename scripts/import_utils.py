#!/usr/bin/env python3
"""Shared helpers for local dataset import scripts."""

from __future__ import annotations

import csv
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from scripts.validate_datasets import validate_all_datasets


DATASET_NAMES = ("regions", "districts", "municipalities")
DATASET_COLUMNS: dict[str, tuple[str, ...]] = {
    "regions": ("code", "name", "nameEn", "country"),
    "districts": ("code", "name", "regionCode", "country"),
    "municipalities": ("code", "name", "districtCode", "regionCode", "country"),
}


@dataclass(frozen=True)
class LocalImportFile:
    dataset: str
    path: Path
    records: list[dict[str, Any]]


def _coerce_path(path: str | os.PathLike[str] | Path) -> Path:
    return path if isinstance(path, Path) else Path(path)


def normalize_whitespace(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def today_iso() -> str:
    return date.today().isoformat()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


read_json = load_json


def read_csv(path: str | os.PathLike[str] | Path) -> list[dict[str, str | None]]:
    file_path = _coerce_path(path)
    with file_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        rows: list[dict[str, str | None]] = []
        for row in reader:
            if row is None:
                continue
            normalized = {key: normalize_whitespace(value) or None for key, value in row.items()}
            if not any(value is not None for value in normalized.values()):
                continue
            rows.append(normalized)
        return rows


def backup_existing_file(path: str | os.PathLike[str] | Path) -> Path | None:
    file_path = _coerce_path(path)
    if not file_path.is_file():
        return None

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_path = file_path.with_name(f"{file_path.name}.bak.{timestamp}")
    shutil.copy2(file_path, backup_path)
    return backup_path


def write_json_atomic(path: str | os.PathLike[str] | Path, payload: Any) -> None:
    file_path = _coerce_path(path)
    validate_before_write(file_path.stem, payload)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        delete=False,
        dir=str(file_path.parent),
        prefix=f".{file_path.name}.",
        suffix=".tmp",
    ) as handle:
        temp_path = Path(handle.name)
        try:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        except Exception:
            temp_path.unlink(missing_ok=True)
            raise

    os.replace(temp_path, file_path)


def write_json(path: Path, payload: Any) -> None:
    write_json_atomic(path, payload)


def validate_before_write(dataset_name: str, data: Any) -> None:
    normalized_name = normalize_whitespace(dataset_name)
    if not normalized_name:
        raise ValueError("dataset_name must be a non-empty string")

    if data is None:
        raise ValueError(f"{normalized_name} data must not be None")

    if isinstance(data, (str, bytes, bytearray)):
        if not normalize_whitespace(data):
            raise ValueError(f"{normalized_name} data must not be empty")
    elif hasattr(data, "__len__") and len(data) == 0:
        raise ValueError(f"{normalized_name} data must not be empty")

    try:
        json.dumps(data, ensure_ascii=False)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{normalized_name} data is not JSON serializable") from exc


def copy_existing_file(source: Path, destination: Path) -> bool:
    if not source.is_file():
        return False

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return True


def dataset_file_name(dataset: str, suffix: str = ".json") -> str:
    return f"{dataset}{suffix}"


def _normalize_records(records: Any, dataset: str) -> list[dict[str, Any]]:
    if not isinstance(records, list):
        raise ValueError(f"{dataset} records must be an array")

    normalized: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"{dataset}[{index}] must be an object")
        normalized.append({key: value for key, value in record.items()})
    return normalized


def load_dataset_records_from_json(path: Path, dataset: str) -> list[dict[str, Any]]:
    payload = load_json(path)

    if isinstance(payload, list):
        return _normalize_records(payload, dataset)

    if isinstance(payload, dict):
        if dataset in payload:
            return _normalize_records(payload[dataset], dataset)

        if "data" in payload and isinstance(payload["data"], list):
            return _normalize_records(payload["data"], dataset)

    raise ValueError(f"Unable to locate {dataset} records in {path}")


def load_dataset_records_from_csv(path: Path, dataset: str) -> list[dict[str, Any]]:
    required_columns = DATASET_COLUMNS[dataset]
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError(f"{path} has no CSV header")

        missing = [column for column in required_columns if column not in reader.fieldnames]
        if missing:
            raise ValueError(f"{path} is missing required columns: {', '.join(missing)}")

        records: list[dict[str, Any]] = []
        for row in reader:
            record = {key: value for key, value in row.items() if value not in (None, "")}
            records.append(record)
        return records


def load_dataset_records(dataset: str, path: Path) -> list[dict[str, Any]]:
    if path.is_dir():
        json_path = path / dataset_file_name(dataset, ".json")
        csv_path = path / dataset_file_name(dataset, ".csv")
        if json_path.is_file():
            return load_dataset_records_from_json(json_path, dataset)
        if csv_path.is_file():
            return load_dataset_records_from_csv(csv_path, dataset)
        raise FileNotFoundError(f"Missing {dataset} input file in {path}")

    if path.suffix.lower() == ".json":
        return load_dataset_records_from_json(path, dataset)
    if path.suffix.lower() == ".csv":
        return load_dataset_records_from_csv(path, dataset)

    raise ValueError(f"Unsupported input format: {path.suffix or path}")


def load_all_dataset_records(path: Path) -> dict[str, list[dict[str, Any]]]:
    if path.is_dir():
        return {dataset: load_dataset_records(dataset, path) for dataset in DATASET_NAMES}

    if path.suffix.lower() != ".json":
        raise ValueError("--dataset all supports a directory or a JSON manifest")

    payload = read_json(path)
    if not isinstance(payload, dict):
        raise ValueError("all-dataset JSON input must be an object")

    records_by_dataset: dict[str, list[dict[str, Any]]] = {}
    for dataset in DATASET_NAMES:
        if dataset not in payload:
            raise ValueError(f"all-dataset JSON input is missing {dataset}")
        records_by_dataset[dataset] = _normalize_records(payload[dataset], dataset)
    return records_by_dataset


def build_dataset_payload(dataset: str, records: list[dict[str, Any]], source: str, complete: bool) -> dict[str, Any]:
    ordered_records = records
    if records and all(isinstance(record, dict) for record in records):
        ordered_records = sorted(
            records,
            key=lambda record: (
                normalize_whitespace(record.get("code")),
                normalize_whitespace(record.get("name")),
            ),
        )

    return {
        "metadata": {
            "source": source,
            "lastUpdated": today_iso(),
            "complete": complete,
        },
        dataset: ordered_records,
    }


def collect_referential_integrity_errors(data_dir: Path) -> list[str]:
    errors: list[str] = []

    def load_records(file_name: str, dataset: str) -> list[dict[str, Any]]:
        path = data_dir / file_name
        if not path.is_file():
            errors.append(f"Missing required file: {file_name}")
            return []

        payload = read_json(path)
        if not isinstance(payload, dict):
            errors.append(f"{file_name}: expected JSON object")
            return []

        records = payload.get(dataset)
        if not isinstance(records, list):
            errors.append(f"{file_name}: missing {dataset} array")
            return []

        normalized: list[dict[str, Any]] = []
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                errors.append(f"{file_name}: {dataset}[{index}] must be an object")
                continue
            normalized.append(record)
        return normalized

    regions = load_records("regions.json", "regions")
    districts = load_records("districts.json", "districts")
    municipalities = load_records("municipalities.json", "municipalities")

    regions_by_code = {str(record.get("code")): record for record in regions if record.get("code") is not None}
    districts_by_code = {str(record.get("code")): record for record in districts if record.get("code") is not None}
    municipalities_by_code = {str(record.get("code")): record for record in municipalities if record.get("code") is not None}

    for district_code, district in districts_by_code.items():
        region_code = district.get("regionCode")
        if not region_code:
            errors.append(f"District {district_code}: missing regionCode")
            continue
        if region_code not in regions_by_code:
            errors.append(f"District {district_code}: unknown regionCode {region_code}")

    for municipality_code, municipality in municipalities_by_code.items():
        district_code = municipality.get("districtCode")
        region_code = municipality.get("regionCode")

        if not district_code:
            errors.append(f"Municipality {municipality_code}: missing districtCode")
        elif district_code not in districts_by_code:
            errors.append(f"Municipality {municipality_code}: unknown districtCode {district_code}")

        if not region_code:
            errors.append(f"Municipality {municipality_code}: missing regionCode")
        elif region_code not in regions_by_code:
            errors.append(f"Municipality {municipality_code}: unknown regionCode {region_code}")

        if district_code in districts_by_code and region_code:
            expected_region_code = districts_by_code[district_code].get("regionCode")
            if expected_region_code != region_code:
                errors.append(
                    "Municipality "
                    f"{municipality_code}: regionCode {region_code} does not match district {district_code} regionCode {expected_region_code}"
                )

    psc_path = data_dir / "psc.json"
    if not psc_path.is_file():
        errors.append("Missing required file: psc.json")
        return errors

    psc_payload = read_json(psc_path)
    if not isinstance(psc_payload, dict):
        errors.append("psc.json: expected JSON object")
        return errors

    for psc_code, record in psc_payload.items():
        if psc_code == "metadata":
            continue
        if not isinstance(record, dict):
            errors.append(f"PSC {psc_code}: record must be an object")
            continue

        region_code = record.get("regionCode")
        district_code = record.get("districtCode")
        municipality_code = record.get("municipalityCode")

        district_region_code = None
        municipality_region_code = None

        if region_code is not None and region_code not in regions_by_code:
            errors.append(f"PSC {psc_code}: unknown regionCode {region_code}")

        if district_code is not None:
            if district_code not in districts_by_code:
                errors.append(f"PSC {psc_code}: unknown districtCode {district_code}")
            else:
                district_region_code = districts_by_code[district_code].get("regionCode")
                if region_code is not None and district_region_code != region_code:
                    errors.append(
                        f"PSC {psc_code}: districtCode {district_code} belongs to regionCode {district_region_code}, "
                        f"but PSC regionCode is {region_code}"
                    )

        if municipality_code is not None:
            if municipality_code not in municipalities_by_code:
                errors.append(f"PSC {psc_code}: unknown municipalityCode {municipality_code}")
            else:
                municipality = municipalities_by_code[municipality_code]
                municipality_district_code = municipality.get("districtCode")
                municipality_region_code = municipality.get("regionCode")

                if district_code is not None and municipality_district_code != district_code:
                    errors.append(
                        f"PSC {psc_code}: municipalityCode {municipality_code} belongs to districtCode {municipality_district_code}, "
                        f"but PSC districtCode is {district_code}"
                    )

                if region_code is not None and municipality_region_code != region_code:
                    errors.append(
                        f"PSC {psc_code}: municipalityCode {municipality_code} belongs to regionCode {municipality_region_code}, "
                        f"but PSC regionCode is {region_code}"
                    )

                if district_code is not None and district_code in districts_by_code:
                    expected_region_code = districts_by_code[district_code].get("regionCode")
                    if municipality_region_code != expected_region_code:
                        errors.append(
                            f"PSC {psc_code}: municipalityCode {municipality_code} belongs to regionCode {municipality_region_code}, "
                            f"but PSC districtCode {district_code} belongs to regionCode {expected_region_code}"
                        )

        if region_code is None and district_region_code is not None and municipality_region_code is not None:
            if district_region_code != municipality_region_code:
                errors.append(
                    f"PSC {psc_code}: districtCode {district_code} regionCode {district_region_code} does not match "
                    f"municipalityCode {municipality_code} regionCode {municipality_region_code}"
                )

    return errors


def validate_datasets_before_write(data_dir: Path) -> None:
    """Refuse to continue when shape or referential checks fail."""

    errors: list[str] = []

    for report in validate_all_datasets(data_dir):
        for issue in report.errors:
            errors.append(f"{report.dataset}:{issue.path}: {issue.message}")

    errors.extend(collect_referential_integrity_errors(data_dir))

    if errors:
        raise ValueError("Dataset validation failed before write:\n- " + "\n- ".join(errors))
