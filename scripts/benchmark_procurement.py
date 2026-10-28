#!/usr/bin/env python3
"""Offline, isolated-process procurement benchmark; never changes datasets."""

import argparse
import gc
import hashlib
import json
from pathlib import Path
import platform
import statistics
import sys
import time
import tracemalloc

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services import procurement_notice_service as service


def elapsed(fn, repeats=5):
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - start) * 1000)
    return {"medianMs": round(statistics.median(samples), 3), "maxMs": round(max(samples), 3)}


def rss():
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes
        class Counters(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [(name, ctypes.c_size_t) for name in (
                "PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage", "QuotaPagedPoolUsage",
                "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]
        counter = Counters()
        counter.cb = ctypes.sizeof(counter)
        ctypes.windll.kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        ctypes.windll.psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD]
        if ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(counter), counter.cb):
            return counter.WorkingSetSize
        return None
    import resource
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1024 if sys.platform != "darwin" else 1)


def benchmark(path):
    raw = path.read_bytes()
    report = {"environment": {"python": sys.version.split()[0], "platform": platform.platform(), "processor": platform.processor()},
              "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
              "jsonParse": elapsed(lambda: json.loads(raw), repeats=3)}
    service.DATA_FILE = path
    service.load_procurement_notice_data.cache_clear()
    service.load_procurement_notice_records.cache_clear()
    start = time.perf_counter()
    records = service.load_procurement_notice_records()
    report["serviceColdLoadMs"] = round((time.perf_counter() - start) * 1000, 3)
    report["records"] = len(records)
    report["rssAfterLoadBytes"] = rss()
    lookup_id = records[-1]["id"]
    year = int(records[len(records) // 2]["publicationDate"][:4])
    notice_type = records[0]["noticeType"]
    report["lookupLast"] = elapsed(lambda: service.get_procurement_notice_by_id(lookup_id))
    report["listFirst"] = elapsed(lambda: service.list_procurement_notices(limit=100))
    report["listMiddle"] = elapsed(lambda: service.list_procurement_notices(limit=100, offset=len(records) // 2))
    report["listEnd"] = elapsed(lambda: service.list_procurement_notices(limit=100, offset=max(0, len(records) - 100)))
    report["listPastEnd"] = elapsed(lambda: service.list_procurement_notices(limit=500, offset=10**9))
    report["yearFilter"] = elapsed(lambda: service.list_procurement_notices({"year": year}, limit=100))
    report["combinedFilter"] = elapsed(lambda: service.list_procurement_notices({"year": year, "noticeType": notice_type}, limit=100))
    report["search"] = {query: elapsed(lambda q=query: service.search_procurement_notices(q, limit=50), repeats=3)
                        for query in (lookup_id, "stavebne", "ministerstvo", "Bratislava", "no-such-needle-xyz")}
    report["rssAfterSearchBytes"] = rss()
    # Separate traced load; tracing overhead is NOT included in cold-load times.
    del records
    service.load_procurement_notice_records.cache_clear()
    service.load_procurement_notice_data.cache_clear()
    gc.collect()
    tracemalloc.start()
    service.load_procurement_notice_records()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    report["retainedLoadHeapBytes"] = current
    report["peakLoadHeapBytes"] = peak
    from fastapi.testclient import TestClient
    from main import app
    client = TestClient(app)
    report["http"] = {url: elapsed(lambda u=url: _request(client, u), repeats=3) for url in (
        "/v1/procurement-notices", f"/v1/procurement-notices?year={year}",
        "/v1/procurement-notices/search?q=Bratislava", f"/v1/procurement-notices/{lookup_id}")}
    return report


def _request(client, url):
    response = client.get(url)
    if response.status_code != 200:
        raise ValueError(f"benchmark endpoint failed: {url} {response.status_code}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = benchmark(args.input.resolve())
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
