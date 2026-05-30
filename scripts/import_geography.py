#!/usr/bin/env python3
"""Import geography datasets from local JSON, CSV, or XLSX files.

JSON is the primary input format. CSV is also supported for flat record lists.
Municipalities can also be imported from a local XLSX workbook.
For `--dataset all`, pass either a directory containing `regions`, `districts`,
and `municipalities` files, or a JSON manifest with those keys.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_CONTEXT_DIR = ROOT / "data"

from scripts.import_utils import (
    build_dataset_payload,
    collect_referential_integrity_errors,
    backup_existing_file,
    copy_existing_file,
    dataset_file_name,
    load_all_dataset_records,
    load_dataset_records,
    write_json,
)
from scripts.validate_datasets import (
    ValidationReport,
    validate_districts_dataset,
    validate_municipalities_dataset,
    validate_regions_dataset,
)


VALID_DATASETS = ("regions", "districts", "municipalities", "all")
VALIDATORS = {
    "regions": validate_regions_dataset,
    "districts": validate_districts_dataset,
    "municipalities": validate_municipalities_dataset,
}


@dataclass
class ImportResult:
    dataset: str
    source: str
    input_path: Path
    output_path: Path
    dry_run: bool
    wrote_files: list[Path] = field(default_factory=list)
    validation_reports: list[ValidationReport] = field(default_factory=list)
    integrity_errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(report.ok for report in self.validation_reports) and not self.integrity_errors


def _resolve_output_root(output: Path, dataset: str) -> Path:
    if dataset == "all":
        return output

    if output.suffix.lower() == ".json":
        return output.parent

    return output


def _resolve_single_output_path(output: Path, dataset: str) -> Path:
    if output.suffix.lower() == ".json":
        return output
    return output / dataset_file_name(dataset)


def _build_payloads(dataset: str, input_path: Path, source: str) -> dict[str, dict[str, object]]:
    if dataset == "all":
        records_by_dataset = load_all_dataset_records(input_path)
        return {
            name: build_dataset_payload(name, records, source, complete=(name == "regions"))
            for name, records in records_by_dataset.items()
        }

    records = load_dataset_records(dataset, input_path)
    return {
        dataset: build_dataset_payload(dataset, records, source, complete=(dataset == "regions")),
    }


def _stage_existing_context(stage_dir: Path, output_root: Path, dataset: str) -> None:
    base_dir = DEFAULT_CONTEXT_DIR

    for name in ("regions", "districts", "municipalities", "psc"):
        if dataset != "all" and name == dataset:
            continue
        source = output_root / dataset_file_name(name)
        if not source.is_file():
            source = base_dir / dataset_file_name(name)
        destination = stage_dir / dataset_file_name(name)
        copy_existing_file(source, destination)


def _stage_payloads(stage_dir: Path, payloads: dict[str, dict[str, object]]) -> list[Path]:
    written: list[Path] = []
    for dataset, payload in payloads.items():
        path = stage_dir / dataset_file_name(dataset)
        write_json(path, payload)
        written.append(path)
    return written


def _validate_stage(stage_dir: Path, payloads: dict[str, dict[str, object]]) -> list[ValidationReport]:
    reports: list[ValidationReport] = []
    for dataset in payloads:
        validator = VALIDATORS[dataset]
        reports.append(validator(stage_dir / dataset_file_name(dataset)))
    return reports


def run_import(
    *,
    dataset: str,
    source: str,
    input_path: Path,
    output_path: Path,
    write: bool = False,
    allow_incomplete: bool = False,
) -> ImportResult:
    if dataset not in VALID_DATASETS:
        raise ValueError(f"Unsupported dataset: {dataset}")
    if dataset == "all" and output_path.suffix.lower() == ".json":
        raise ValueError("--dataset all requires an output directory")

    input_path = input_path.resolve()
    output_path = output_path.resolve()
    output_root = _resolve_output_root(output_path, dataset)

    payloads = _build_payloads(dataset, input_path, source)

    with tempfile.TemporaryDirectory(prefix="opensk-geography-") as temp_dir_name:
        stage_dir = Path(temp_dir_name)
        _stage_existing_context(stage_dir, output_root, dataset)
        staged_files = _stage_payloads(stage_dir, payloads)

        validation_reports = _validate_stage(stage_dir, payloads)
        if any(not report.ok for report in validation_reports):
            return ImportResult(
                dataset=dataset,
                source=source,
                input_path=input_path,
                output_path=output_path,
                dry_run=not write,
                validation_reports=validation_reports,
            )

        integrity_errors = collect_referential_integrity_errors(stage_dir)
        if integrity_errors and not allow_incomplete:
            return ImportResult(
                dataset=dataset,
                source=source,
                input_path=input_path,
                output_path=output_path,
                dry_run=not write,
                validation_reports=validation_reports,
                integrity_errors=integrity_errors,
            )

        wrote_files: list[Path] = []
        if write:
            if dataset == "all":
                output_root.mkdir(parents=True, exist_ok=True)
                for staged_file in staged_files:
                    destination = output_root / staged_file.name
                    backup_existing_file(destination)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(staged_file, destination)
                    wrote_files.append(destination)
            else:
                destination = _resolve_single_output_path(output_path, dataset)
                backup_existing_file(destination)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(staged_files[0], destination)
                wrote_files.append(destination)

        return ImportResult(
            dataset=dataset,
            source=source,
            input_path=input_path,
            output_path=output_path,
            dry_run=not write,
            wrote_files=wrote_files,
            validation_reports=validation_reports,
            integrity_errors=integrity_errors,
        )


def _print_result(result: ImportResult) -> None:
    print(f"dataset={result.dataset} source={result.source} input={result.input_path} output={result.output_path}")
    for report in result.validation_reports:
        status = "OK" if report.ok else "FAIL"
        print(f"{report.dataset}: {status} records={report.record_count} errors={report.error_count} warnings={report.warning_count}")
        for issue in report.errors:
            print(f"- validation: {issue.path}: {issue.message}")
        for issue in report.warnings:
            print(f"- warning: {issue.path}: {issue.message}")

    if result.integrity_errors:
        print("Referential integrity issues:")
        for error in result.integrity_errors:
            print(f"- {error}")

    if result.wrote_files:
        print("Wrote:")
        for path in result.wrote_files:
            print(f"- {path}")
    elif result.dry_run:
        print("Dry run only; no files written.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import geography datasets from local JSON, CSV, or XLSX files.")
    parser.add_argument("--source", default="local file import", help="Source label stored in dataset metadata")
    parser.add_argument("--input", required=True, type=Path, help="Input file or directory (JSON, CSV, or XLSX for municipalities)")
    parser.add_argument("--output", required=True, type=Path, help="Output file or directory")
    parser.add_argument(
        "--dataset",
        choices=VALID_DATASETS,
        default="all",
        help="Dataset to import: regions, districts, municipalities, or all",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Validate only; do not write files")
    mode.add_argument("--write", action="store_true", help="Write imported files if validation passes")
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Allow writing when referential integrity is incomplete",
    )
    args = parser.parse_args(argv)

    result = run_import(
        dataset=args.dataset,
        source=args.source,
        input_path=args.input,
        output_path=args.output,
        write=bool(args.write),
        allow_incomplete=args.allow_incomplete,
    )
    _print_result(result)

    if any(not report.ok for report in result.validation_reports):
        return 1
    if result.integrity_errors and not args.allow_incomplete:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
