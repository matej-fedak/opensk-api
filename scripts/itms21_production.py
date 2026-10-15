"""Offline, manifest-verified ITMS21+ production materialization. No HTTP code."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from pydantic import ValidationError

from schemas.eu_funds import Dataset, Project, valid_instant
from services.eu_funds_policy import (
    AMBIGUOUS_LEGAL_FORMS, APPROVED_LEGAL_FORMS, COLLECTION_URL, LICENCE_NOTICE,
    PRIVACY_POLICY, REVIEWED_NUTS_LABELS, SOURCE_NOTICE, TERMS_URL,
)
from scripts import import_itms21_projects as base

PRODUCTION_OUTPUT = base.ROOT / "data" / "eu_funds_projects.json"
PROFILE = "itms21-project-references-v1"
# Only reviewed NUTS3 implementation codes; no district/municipality inference.
REVIEWED_NUTS = frozenset(REVIEWED_NUTS_LABELS)


def manifest_digest(manifest: dict) -> str:
    body = {k: v for k, v in manifest.items() if k != "manifestSha256"}
    return hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode("utf-8")).hexdigest()


def load_manifest(path: Path):
    """Validate the complete page plan before exposing a streaming row iterator."""
    path = path.resolve()
    base.require(not path.is_relative_to(base.ROOT), "raw manifest must stay outside repository")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    base.require(isinstance(manifest, dict), "manifest must be an object")
    base.require(manifest.get("profile") == "itms21-project-list-acquisition-v1", "unknown acquisition profile")
    base.require(manifest.get("collectionUrl") == COLLECTION_URL, "manifest source must be official project collection")
    base.require(manifest.get("manifestSha256") == manifest_digest(manifest), "manifest hash mismatch")
    base.require(manifest.get("completeAcquisition") is True, "production requires complete acquisition")
    population, page_size = manifest.get("sourceProjectCount"), manifest.get("pageSize")
    base.require(type(population) is int and population > 0, "invalid source population")
    base.require(type(page_size) is int and 1 <= page_size <= 250, "invalid bounded page size")
    base.require(manifest.get("rowsAcquired") == population, "acquired count differs from population")
    for key in ("startedAt", "completedAt"):
        valid_instant(manifest[key])
    base.require(manifest["startedAt"] <= manifest["completedAt"], "invalid acquisition window")
    pages = manifest.get("pages")
    base.require(isinstance(pages, list) and pages, "missing manifest pages")
    expected_offset, filenames = 0, set()
    for page in pages:
        base.require(isinstance(page, dict), "invalid page manifest object")
        count = min(page_size, population - expected_offset)
        expected_url = f"{COLLECTION_URL}?offset={expected_offset}&limit={page_size}"
        base.require(page.get("offset") == expected_offset and page.get("url") == expected_url,
                     "missing/overlapping page range or unexpected request URL")
        base.require(count > 0 and page.get("size") == population and page.get("limit") == page_size
                     and page.get("rows") == count, "inconsistent page totals")
        filename = page.get("file", "")
        base.require(isinstance(filename, str) and re.fullmatch(r"page-[0-9]{5}\.json", filename), "unsafe raw page filename")
        base.require(filename not in filenames and (path.parent / filename).resolve().parent == path.parent,
                     "duplicate or escaped page path")
        filenames.add(filename)
        valid_instant(page["retrievedAt"])
        expected_offset += count
    base.require(expected_offset == population, "incomplete page coverage")
    base.require(manifest.get("boundaryRecheckSha256") == pages[0].get("sha256"), "boundary recheck mismatch")

    def rows():
        ids, codes = set(), set()
        for page in pages:
            raw = base.read_source_bytes(path.parent / page["file"])
            base.require(len(raw) == page["bytes"] and hashlib.sha256(raw).hexdigest() == page["sha256"],
                         "raw page byte/hash mismatch")
            size, items = base.parse_list_page(raw, "manifest page")
            envelope = base.parse_json(raw, "manifest page")
            base.require(size == population and len(items) == page["rows"]
                         and envelope["offset"] == page["offset"] and envelope["limit"] == page_size,
                         "raw page differs from manifest coverage")
            for row in items:
                source_id, code = base.extract_identity(row, "source project")
                base.require(source_id not in ids and code not in codes, "duplicate project ID/code")
                ids.add(source_id)
                codes.add(code)
                yield row
        base.require(len(codes) == population, "source population mismatch")
    return manifest, rows()


def classify(row):
    subject = row.get("prijimatel")
    form = subject.get("pravnaForma") if isinstance(subject, dict) else None
    code = form.get("kod") if isinstance(form, dict) else None
    label = form.get("nazovSk") if isinstance(form, dict) else None
    base.require(code is None or isinstance(code, str), "invalid legal-form code type")
    base.require(label is None or isinstance(label, str), "invalid legal-form label type")
    if code in APPROVED_LEGAL_FORMS:
        decision = "APPROVED_LEGAL_ENTITY"
    elif code == "1009995":
        decision = "EXCLUDE_UNSPECIFIED"
    elif code in base.NATURAL_PERSON_FORMS:
        decision = "EXCLUDE_NATURAL_PERSON"
    elif code in AMBIGUOUS_LEGAL_FORMS:
        decision = "EXCLUDE_AMBIGUOUS"
    else:
        decision = "EXCLUDE_UNREVIEWED"
    return code, label, decision


def project_record(row, report):
    """Explicit production allowlist: never reads project title or descriptions."""
    where = "approved project"
    source_id, code = base.extract_identity(row, where)
    base.require("stav" in row, "missing source status label field")
    subject, call = row["prijimatel"], row.get("vyzva")
    base.require(isinstance(call, dict) and isinstance(call.get("program"), dict), "missing programme/call")
    programme = call["program"]
    programme_out = {"code": base.require_str(programme, "kod", where),
                     "nameSk": base.require_str(programme, "nazovSk", where)}
    for old, new in (("skratka", "shortName"), ("kodCCI", "cci")):
        if programme.get(old) is not None:
            programme_out[new] = base.require_str(programme, old, where)
    beneficiary = {"name": base.require_str(subject, "nazov", where),
                   "legalForm": {"code": subject["pravnaForma"]["kod"],
                                 "nameSk": base.require_str(subject["pravnaForma"], "nazovSk", where)}}
    ico = subject.get("ico")
    if ico is not None:
        base.require(isinstance(ico, str), "IČO must remain a source string")
        if re.fullmatch(r"[0-9]{8}", ico):
            beneficiary["ico"] = ico
        else:
            report["omittedInvalidIco"] += 1  # never truncate/strip significant digits
    locations = row.get("miestoRealizacie")
    base.require(isinstance(locations, list), "missing implementation locations")
    regions = {}
    for item in locations:
        base.require(isinstance(item, dict) and isinstance(item.get("kodZdroj"), str), "invalid source location")
        nuts = item["kodZdroj"]
        base.require(re.fullmatch(r"[A-Z]{2}[A-Z0-9]{0,3}", nuts), "unrecognized geography code shape; value not logged")
        if nuts not in REVIEWED_NUTS:
            report["unexpectedGeography"][nuts] += 1
            continue
        regions[nuts] = {"nuts": nuts, "nameSk": base.require_str(item, "nazovSk", where)}
    result = {"projectCode": code, "sourceId": source_id,
              "status": {"label": row.get("stav"),
                         "inImplementation": base.require_bool(row, "vrealizacii", where),
                         "completed": base.require_bool(row, "ukonceny", where)},
              "programme": programme_out,
              "call": {"code": base.require_str(call, "kod", where), "nameSk": base.require_str(call, "nazovSk", where)},
              "beneficiary": beneficiary, "implementationRegions": [regions[k] for k in sorted(regions)],
              "financials": {"contractedTotal": base.money_string(row, "celkovaZazmluvnenaSuma", where, mandatory=True)},
              "sourceUpdatedAt": base.iso_datetime_from_ms(base.require_int(row, "updatedAt", where), where, "updatedAt"),
              "sourceUrl": f"{COLLECTION_URL}/id/{source_id}"}
    try:
        return Project.model_validate(result).model_dump(exclude_none=True)
    except ValidationError:
        raise ValueError("approved production field schema drift; no source row logged") from None


def build_snapshot(manifest_path: Path):
    manifest, rows = load_manifest(manifest_path)
    report = {"sourceProjectCount": manifest["sourceProjectCount"], "pageCount": len(manifest["pages"]),
              "includedProjects": 0, "excludedNaturalPersonProjects": 0,
              "excludedUnreviewedBeneficiaryProjects": 0, "legalForms": {},
              "omittedInvalidIco": 0, "unexpectedGeography": Counter()}
    projects, source_codes, excluded_codes = [], set(), set()
    for row in rows:
        code, label, decision = classify(row)
        key = code if isinstance(code, str) else "MISSING"
        info = report["legalForms"].setdefault(key, {"count": 0, "sourceLabel": label, "decision": decision})
        base.require(info["sourceLabel"] == label, "legal-form label drift within source snapshot")
        info["count"] += 1
        source_codes.add(row["kod"])
        if decision != "APPROVED_LEGAL_ENTITY":
            counter = "excludedNaturalPersonProjects" if decision == "EXCLUDE_NATURAL_PERSON" else "excludedUnreviewedBeneficiaryProjects"
            report[counter] += 1
            excluded_codes.add(row["kod"])
            continue
        projects.append(project_record(row, report))
        report["includedProjects"] += 1
    projects.sort(key=lambda row: row["projectCode"])
    metadata = {"source": SOURCE_NOTICE, "sourceUrl": COLLECTION_URL, "termsUrl": TERMS_URL,
                "licence": LICENCE_NOTICE,
                "attribution": "MIRRI SR / ITMS21+; CC BY per catalogue. OpenSK transformed/minimized the data; not an official representation.",
                "snapshotDate": manifest["completedAt"][:10], "retrievedAt": manifest["completedAt"],
                "sourceProjectCount": manifest["sourceProjectCount"], "includedProjectCount": len(projects),
                "privacyExcludedProjectCount": len(excluded_codes),
                "excludedNaturalPersonProjects": report["excludedNaturalPersonProjects"],
                "excludedUnreviewedBeneficiaryProjects": report["excludedUnreviewedBeneficiaryProjects"],
                "privacyPolicy": PRIVACY_POLICY, "completeAcquisition": True,
                "pageCount": len(manifest["pages"]), "sourceManifestSha256": manifest["manifestSha256"],
                "importerProfile": PROFILE}
    payload = {"metadata": metadata, "projects": projects}
    Dataset.model_validate(payload)
    report["privacyExcludedProjectCount"] = len(excluded_codes)
    report["legalFormCodeCount"] = len(report["legalForms"])
    report["unexpectedGeography"] = dict(sorted(report["unexpectedGeography"].items()))
    codes = [p["projectCode"] for p in projects]
    report["projectCodeReview"] = {"minLength": min(map(len, codes), default=0),
                                  "maxLength": max(map(len, codes), default=0),
                                  "characters": "".join(sorted(set("".join(codes))))}
    return payload, report, source_codes, excluded_codes


def materialize(manifest: Path, *, write_production=False, write_preview=False, output=None,
                previous_manifest: Path | None = None, acknowledge_removals=False):
    result = base.ImportResult(report={"profile": PROFILE, "errors": [], "dryRun": True})
    try:
        base.require(not (write_production and write_preview), "production/preview modes are exclusive")
        if write_production:
            destination = Path(output or PRODUCTION_OUTPUT).resolve()
            base.require(destination == PRODUCTION_OUTPUT.resolve(), "production output is fixed to data/eu_funds_projects.json")
        else:
            destination = base.validate_preview_path(Path(output or base.DEFAULT_OUTPUT))
        base.require(previous_manifest is None or PRODUCTION_OUTPUT.exists(),
                     "optional previous manifest requires an existing production baseline")
        payload, report, source_codes, excluded = build_snapshot(manifest)
        result.report.update(report)
        if PRODUCTION_OUTPUT.exists():
            old = json.loads(PRODUCTION_OUTPUT.read_text(encoding="utf-8"))
            Dataset.model_validate(old)
            before = {p["projectCode"]: p for p in old["projects"]}
            after = {p["projectCode"]: p for p in payload["projects"]}
            removed, added = before.keys() - after.keys(), after.keys() - before.keys()
            # The committed public baseline + NEW complete source population
            # suffice for safety. Never require retention of old personal data.
            base.require(not ((removed & source_codes) - excluded),
                         "unexplained disappearance of published projects still present upstream")
            old_public_forms = {p["beneficiary"]["legalForm"]["code"] for p in before.values()}
            new_public_forms = {p["beneficiary"]["legalForm"]["code"] for p in after.values()}
            refresh = {
                "previousIncludedCount": len(before), "newIncludedCount": len(after),
                "addedPublishedProjectCodesCount": len(added), "removedPublishedProjectCodesCount": len(removed),
                "projectsBecomingPrivacyExcludedCount": len(removed & excluded),
                "projectsRemovedUpstreamCount": len(removed - source_codes),
                "changedPublishedLegalFormCodeSet": {
                    "added": sorted(new_public_forms - old_public_forms),
                    "removed": sorted(old_public_forms - new_public_forms),
                },
                "sourcePopulationChange": payload["metadata"]["sourceProjectCount"] - old["metadata"]["sourceProjectCount"],
                "changedPublishedProjectsCount": sum(before[c] != after[c] for c in before.keys() & after.keys()),
                "previousRawAcquisitionUsed": False,
                # An addition might be newly created OR previously excluded.
                # No IDs/timestamps/form heuristics can establish that split.
                "projectsBecomingNewlyEligibleCount": None,
            }
            result.report["refresh"] = refresh
            if previous_manifest is not None:
                old_manifest, old_rows = load_manifest(previous_manifest)
                base.require(old_manifest["manifestSha256"] == old["metadata"]["sourceManifestSha256"],
                             "previous manifest does not match served snapshot")
                old_source_codes, old_source_forms = set(), set()
                for row in old_rows:
                    old_source_codes.add(row["kod"])
                    form_code, _, _ = classify(row)
                    old_source_forms.add(form_code or "MISSING")
                new_source_forms = set(report["legalForms"])
                refresh.update({
                    "previousRawAcquisitionUsed": True,
                    "projectsBecomingNewlyEligibleCount": len(added & old_source_codes),
                    "newUpstreamPublishedProjectsCount": len(added - old_source_codes),
                    "changedSourceLegalFormCodeSet": {
                        "added": sorted(new_source_forms - old_source_forms),
                        "removed": sorted(old_source_forms - new_source_forms),
                    },
                })
            if write_production and removed and not acknowledge_removals:
                raise ValueError("published projects disappear/become excluded; review refresh report and use --acknowledge-removals")
        raw = base.serialize_payload(payload)
        result.report.update({"outputBytes": len(raw), "outputSha256": hashlib.sha256(raw).hexdigest()})
        result.payload = payload
        if write_production or write_preview:
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary = destination.with_suffix(".json.tmp")
            temporary.write_bytes(raw)
            temporary.replace(destination)
            result.wrote_files.append(destination)
            result.report["dryRun"] = False
    except (ValueError, OSError, KeyError, TypeError) as exc:
        # Validation errors must not print a rich source record into logs.
        message = "production dataset schema validation failed" if isinstance(exc, ValidationError) else str(exc)
        result.errors.append(message)
        result.report["errors"] = result.errors
        result.payload = {}
    return result
