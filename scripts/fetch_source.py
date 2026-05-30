#!/usr/bin/env python3
"""Fetch a configured source URL into `data/raw/`.

Expected config format:

```json
{
  "url": "https://example.com/source.json",
  "filename": "source.json"
}
```

The `filename` field is optional. If omitted, the script falls back to the
final path segment of the URL or `downloaded_source` when no basename exists.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error, parse, request


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
DEFAULT_CONFIG_PATH = RAW_DATA_DIR / "source.json"


@dataclass(frozen=True)
class SourceConfig:
    url: str
    filename: str | None = None


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT_DIR))
    except ValueError:
        return str(path)


def _load_config(path: Path) -> SourceConfig:
    if not path.is_file():
        raise FileNotFoundError(f"Config file not found: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, str):
        url = payload.strip()
        if not url:
            raise ValueError("Config URL must be a non-empty string")
        return SourceConfig(url=url)

    if not isinstance(payload, dict):
        raise ValueError("Config must be a JSON object or string URL")

    url_value = payload.get("url") or payload.get("source_url") or payload.get("sourceUrl")
    if not isinstance(url_value, str) or not url_value.strip():
        raise ValueError('Config must define a non-empty "url" value')

    filename_value = payload.get("filename") or payload.get("output") or payload.get("file")
    if filename_value is not None and (not isinstance(filename_value, str) or not filename_value.strip()):
        raise ValueError('Config "filename" must be a non-empty string when provided')

    return SourceConfig(url=url_value.strip(), filename=filename_value.strip() if isinstance(filename_value, str) else None)


def _derive_filename(config: SourceConfig) -> str:
    if config.filename:
        return Path(config.filename).name

    parsed = parse.urlparse(config.url)
    candidate = Path(parsed.path).name.strip()
    if candidate:
        return candidate

    return "downloaded_source"


def _output_paths(config: SourceConfig) -> tuple[Path, Path]:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    filename = _derive_filename(config)
    output_path = RAW_DATA_DIR / filename
    metadata_path = output_path.with_name(f"{output_path.name}.meta.json")
    return output_path, metadata_path


def _fetch_bytes(url: str, timeout: int) -> tuple[bytes, str]:
    try:
        with request.urlopen(url, timeout=timeout) as response:
            return response.read(), response.geturl()
    except error.HTTPError as exc:
        raise RuntimeError(f"HTTP error {exc.code} while fetching {url}: {exc.reason}") from exc
    except (error.URLError, TimeoutError, OSError) as exc:
        reason = getattr(exc, "reason", exc)
        raise RuntimeError(f"Network/offline error while fetching {url}: {reason}") from exc


def fetch_source(config_path: Path = DEFAULT_CONFIG_PATH, *, force: bool = False, timeout: int = 30) -> int:
    try:
        config = _load_config(config_path)
        output_path, metadata_path = _output_paths(config)

        if output_path.exists() and not force:
            print(
                f"Refusing to overwrite existing file: {_display_path(output_path)}. "
                "Use --force to replace it."
            )
            return 1

        payload, resolved_url = _fetch_bytes(config.url, timeout)
        output_path.write_bytes(payload)

        fetched_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        metadata = {
            "sourceUrl": config.url,
            "resolvedUrl": resolved_url,
            "fetchedAt": fetched_at,
            "bytes": len(payload),
        }
        metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    except FileNotFoundError as exc:
        print(str(exc))
        return 1
    except ValueError as exc:
        print(f"Invalid source config: {exc}")
        return 1
    except RuntimeError as exc:
        print(str(exc))
        return 1
    except OSError as exc:
        print(f"Unable to write fetched data: {exc}")
        return 1

    print(f"Fetched {_display_path(output_path)}")
    print(f"Recorded metadata {_display_path(metadata_path)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch a configured source URL into data/raw/")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH, help="Path to the source config JSON")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing download")
    parser.add_argument("--timeout", type=int, default=30, help="Network timeout in seconds")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return fetch_source(args.config, force=args.force, timeout=args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())
