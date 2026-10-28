#!/usr/bin/env python3
"""Offline research aggregates only; no classifier based on names or identifiers.

Search arrays have no documented buyer join/completeness guarantee. Consequently
this tool cannot approve any row, including synthetic all-false arrays. It never
writes production, raw rows, publication IDs, names, titles or identifier values.
"""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.acquire_procurement_notices import (
    PROFILE, PRIVACY_PROFILE, PROFILE_FIELDS, TED_SEARCH_URL,
    encoded, sha, request_payload, query_for, validate_scope,
)


def verified_capture(directory, profile):
    """Verify bytes, requests, PIT token chain, identity and terminal total.

    Do not run the production importer: source optional fields are relevant to
    this research even when the production validator would reject a candidate.
    """
    directory = Path(directory)
    manifest_raw = (directory / "manifest.json").read_bytes()
    m = json.loads(manifest_raw)
    if (m.get("profile") != profile or m.get("fields") != PROFILE_FIELDS[profile]
            or m.get("apiUrl") != TED_SEARCH_URL or m.get("complete") is not True
            or m.get("onlyLatestVersions") is not True or m.get("paginationMode") != "ITERATION"
            or m.get("query") != query_for(m["cutoff"], m.get("startDate"))):
        raise ValueError("capture profile/scope/options mismatch")
    pages = m.get("pages")
    if (not isinstance(pages, list) or not pages or len(pages) != m.get("pageCount")
            or sha(encoded(pages)) != m.get("pagesSha256")
            or not 1 <= m["limit"] <= 250 or not len(pages) <= m["maxPages"] <= 2000
            or type(m.get("reportedTotal")) is not int or m["reportedTotal"] < 0
            or m.get("duplicates") != 0 or m.get("malformed") != 0):
        raise ValueError("invalid capture ledger")
    rows, tokens, token, total_bytes = {}, set(), None, 0
    for number, entry in enumerate(pages, 1):
        if entry["file"] != f"page-{number:04d}.json":
            raise ValueError("page path/order mismatch")
        raw = (directory / entry["file"]).read_bytes()
        if len(raw) != entry["bytes"] or sha(raw) != entry["sha256"]:
            raise ValueError("page hash/size mismatch")
        total_bytes += len(raw)
        if entry["contentType"].split(";", 1)[0].lower() != "application/json":
            raise ValueError("unexpected content type")
        request = request_payload(m["cutoff"], m["limit"], token, m.get("startDate"), profile=profile)
        if sha(encoded(request)) != entry["requestSha256"]:
            raise ValueError("request/token chain mismatch")
        body = json.loads(raw)
        batch = body.get("notices")
        if (body.get("timedOut") is not False or type(body.get("totalNoticeCount")) is not int
                or body["totalNoticeCount"] != m["reportedTotal"] or not isinstance(batch, list)
                or len(batch) != entry["rows"] or len(batch) > m["limit"]
                or (not batch and number != len(pages))):
            raise ValueError("page total/rows/timeout mismatch")
        for row in batch:
            identity = validate_scope(row, m["cutoff"], m.get("startDate"))
            if identity in rows:
                raise ValueError("duplicate canonical identity")
            if set(row) - (set(PROFILE_FIELDS[profile]) | {"links"}):
                raise ValueError("unexpected field in capture")
            # Drop automatic format links immediately; never dereference them.
            rows[identity] = {k: v for k, v in row.items() if k != "links"}
        next_token = body.get("iterationNextToken")
        if batch:
            if not isinstance(next_token, str) or not next_token or next_token in tokens:
                raise ValueError("missing/repeated token")
            tokens.add(next_token)
        token = next_token
    if (pages[-1]["rows"] != 0 or len(rows) != m["acquiredTotal"]
            or len(rows) != m["reportedTotal"] or total_bytes != m["rawBytes"]):
        raise ValueError("incomplete capture")
    summary = {k: v for k, v in m.items() if k != "pages"}
    summary["privateManifestSha256"] = sha(manifest_raw)
    return rows, summary


def marker_state(row):
    if "buyer-person" not in row or row["buyer-person"] == []:
        return "missing"
    values = row["buyer-person"]
    if not isinstance(values, list) or any(type(v) is not bool for v in values):
        return "malformed"
    if all(values):
        return "trueOnly"
    if not any(values):
        return "falseOnly"
    return "mixed"


def string_array_state(row, key):
    if key not in row or row[key] == []:
        return "missing"
    value = row[key]
    if not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value):
        return "malformed"
    return "present"


def schema_evidence(row):
    value = row.get("customization-id")
    if isinstance(value, str) and re.fullmatch(r"eforms-sdk-\d+\.\d+(?:\.\d+)?", value):
        return "eForms-explicit-SDK"
    # Missing customization/subtype is not proof of a legacy XML schema.
    return "generation-unresolved"


def name_count_proxy(row):
    value = row.get("buyer-name")
    if value is None or value == {}:
        return "no-name-values", 0, 0
    if not isinstance(value, dict):
        return "malformed-name", None, None
    sizes = []
    for names in value.values():
        if isinstance(names, str):
            sizes.append(1)
        elif isinstance(names, list) and all(isinstance(n, str) for n in names):
            sizes.append(len(names))
        else:
            return "malformed-name", None, None
    maximum = max(sizes, default=0)
    label = "multiple-name-values" if maximum > 1 else "one-name-value" if maximum else "no-name-values"
    return label, maximum, sum(sizes)


def safe_gate(row):
    """Disjoint whole-notice exclusions; never zip independent arrays."""
    state = marker_state(row)
    if state in {"trueOnly", "mixed"}:
        return "excludedExplicitNatural"
    if state == "missing":
        return "excludedUnknown"
    return "excludedAmbiguous"  # malformed OR false array without complete buyer association


def analyze(original, metadata):
    if original.keys() != metadata.keys():
        raise ValueError("capture identity sets differ")
    groups = {dimension: defaultdict(Counter) for dimension in ("year", "noticeType", "schema", "yearSchema", "nameCardinalityProxy")}
    base_counts = dict.fromkeys(("total", "trueOnly", "falseOnly", "missing", "mixed", "malformed",
                                "legalTypePresent", "legalTypeMissing", "legalTypeMalformed",
                                "identifierPresent", "identifierMissing", "identifierMalformed"), 0)
    totals = Counter(base_counts)
    gates = Counter(dict.fromkeys(("excludedExplicitNatural", "excludedUnknown", "excludedAmbiguous"), 0))
    association_counts = Counter()
    cardinalities = {key: Counter() for key in (
        "buyer-person", "buyer-legal-type", "buyer-identifier", "buyer-name-max-per-language", "buyer-name-all-languages",
    )}
    legal_codes, customization, subtype = Counter(), Counter(), Counter()
    dates = []
    for identity, row in metadata.items():
        old = original[identity]
        if row["publication-date"] != old["publication-date"] or row["buyer-country"] != old["buyer-country"]:
            raise ValueError("joined publication date/country drift")
        dates.append(row["publication-date"][:10])
        state = marker_state(row)
        proxy, maximum, name_total = name_count_proxy(old)
        counts = Counter(base_counts)
        counts.update({"total": 1, state: 1})
        for key, label in (("buyer-legal-type", "legalType"), ("buyer-identifier", "identifier")):
            counts[label + string_array_state(row, key).capitalize()] = 1
        totals.update(counts)
        for dimension, label in (("year", row["publication-date"][:4]), ("noticeType", old["notice-type"]),
                                 ("schema", schema_evidence(row)),
                                 ("yearSchema", row["publication-date"][:4] + ":" + schema_evidence(row)),
                                 ("nameCardinalityProxy", proxy)):
            groups[dimension][label].update(counts)
        for key in ("buyer-person", "buyer-legal-type", "buyer-identifier"):
            label = "absent" if key not in row else str(len(row[key])) if isinstance(row[key], list) else "malformed"
            cardinalities[key][label] += 1
        cardinalities["buyer-name-max-per-language"][str(maximum)] += 1
        cardinalities["buyer-name-all-languages"][str(name_total)] += 1
        if maximum == 1 and isinstance(row.get("buyer-identifier"), list) and len(row["buyer-identifier"]) > 1:
            association_counts["oneNameValueMultipleIdentifiers"] += 1
        if maximum is not None and isinstance(row.get("buyer-legal-type"), list) and len(row["buyer-legal-type"]) != maximum:
            association_counts["nameMaxLegalTypeLengthMismatch"] += 1
        if string_array_state(row, "buyer-legal-type") == "present":
            legal_codes.update(row["buyer-legal-type"])
        # Only source schema/category metadata, not identifier/name values.
        customization[json.dumps(row.get("customization-id"), sort_keys=True)] += 1
        subtype[json.dumps(row.get("notice-subtype"), sort_keys=True)] += 1
        gates[safe_gate(row)] += 1
    return {"total": len(metadata), "counts": dict(totals), "groups": {
        dim: {label: dict(count) for label, count in sorted(values.items())} for dim, values in groups.items()},
        "cardinalities": {key: dict(sorted(value.items())) for key, value in cardinalities.items()},
        "associationDiagnostics": dict(association_counts),
        "legalTypeValueOccurrences": dict(sorted(legal_codes.items())), "customizationValues": dict(customization),
        "subtypeValues": dict(subtype), "acquiredDateRange": [min(dates), max(dates)] if dates else [None, None],
        "candidateA": {"eligible": 0, **dict(gates)}, "candidateBEligible": 0, "candidateCEligible": 0,
        "eligibleDateRange": [None, None], "eligibleByYear": {y: 0 for y in groups["year"]},
        "buyerIdentityAssociation": "not-established", "actualSingleBuyerCount": None, "actualMultiBuyerCount": None,
        "verdict": "NO_GO_PROCUREMENT_EXPANSION"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve().is_relative_to(ROOT / "data"):
        raise ValueError("research cannot write data")
    original, old_summary = verified_capture(args.original, PROFILE)
    metadata, new_summary = verified_capture(args.metadata, PRIVACY_PROFILE)
    if any(old_summary[k] != new_summary[k] for k in ("query", "cutoff", "startDate", "onlyLatestVersions")):
        raise ValueError("capture scopes differ")
    report = analyze(original, metadata)
    report["acquisitions"] = {"original": old_summary, "metadata": new_summary}
    args.output.write_bytes(encoded(report))
    print(json.dumps({"counts": report["counts"], "gate": report["candidateA"], "verdict": report["verdict"]}, indent=2))


if __name__ == "__main__":
    main()
