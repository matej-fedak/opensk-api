#!/usr/bin/env python3
"""Offline NRSR2023 JSON/storage measurements; never changes source/datasets."""

import argparse
import gc
import hashlib
import json
from pathlib import Path
import platform
import sys
import tracemalloc

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.benchmark_procurement import elapsed, rss
from services import elections_service as service


def benchmark():
    raw = service.DATA_FILE.read_bytes()
    def cold():
        service.load_dataset.cache_clear()
        return service.load_dataset()
    report = {
        "environment": {"python": sys.version.split()[0], "platform": platform.platform(), "processor": platform.processor()},
        "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
        "jsonParse": elapsed(lambda: json.loads(raw)),
        "serviceColdLoad": elapsed(cold),
    }
    report["units"] = len(service.load_dataset().units)
    report["parties"] = len(service.load_dataset().parties)
    report["rssAfterLoadBytes"] = rss()
    report["listFirst"] = elapsed(lambda: service.results(regionCode=None, districtCode=None,
                                                          municipalityCode=None, limit=50, offset=0))
    report["filtered"] = elapsed(lambda: service.results(regionCode="9", districtCode="900",
                                                         municipalityCode="599999", limit=50, offset=0))
    report["partiesRead"] = elapsed(lambda: service.load_dataset().parties)
    service.load_dataset.cache_clear()
    gc.collect()
    tracemalloc.start()
    service.load_dataset()
    report["retainedLoadHeapBytes"], report["peakLoadHeapBytes"] = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    from fastapi.testclient import TestClient
    from main import app
    with TestClient(app) as client:
        def request(url):
            response = client.get(url)
            if response.status_code != 200:
                raise ValueError(f"local benchmark request failed: {url}")
        report["http"] = {url: elapsed(lambda u=url: request(u)) for url in (
            "/v1/elections", "/v1/elections/NRSR2023/results",
            "/v1/elections/NRSR2023/results?regionCode=9&municipalityCode=599999",
            "/v1/elections/NRSR2023/parties",
        )}
    report["storageVerdict"] = "JSON_CONTINUE"
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = benchmark()
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
