"""Curated projection of the internal source registry for the public API.

`data/sources.json` is a maintainer-facing registry containing workflow notes,
risk levels, next actions, and speculative wording. The public `/v1/sources`
surface exposes only a curated subset through deterministic mapping rules plus
per-id curated names, cadences, and limitations defined here. The registry
file itself is not served verbatim. See `docs/source-catalogue.md`.
"""

import json
import re
from functools import lru_cache
from pathlib import Path

from schemas.common import (
    BANKS_LAST_UPDATED,
    DISTRICTS_LAST_UPDATED,
    HOLIDAYS_LAST_UPDATED,
    MUNICIPALITIES_LAST_UPDATED,
    PHONE_AREAS_LAST_UPDATED,
    PROCUREMENT_NOTICES_LAST_UPDATED,
    PSC_LAST_UPDATED,
    REGIONS_LAST_UPDATED,
    SCHOOL_FACILITY_COUNTS_LAST_UPDATED,
    VEHICLE_REGISTRATION_CODES_LAST_UPDATED,
)
from schemas.sources import PublicSourceEntry, SourceIdentity, SourceLicence


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SOURCES_FILE = DATA_DIR / "sources.json"

SOURCE_ID_PATTERN = r"[a-zA-Z][a-zA-Z0-9]*"

# Ids backed by a checked-in runtime dataset. Presence here means the dataset
# is served by the API; absence means the domain is research/blocked only.
_RUNTIME_DATASET_IDS = frozenset(
    {
        "regions",
        "districts",
        "municipalities",
        "psc",
        "banks",
        "holidays",
        "companies",
        "phoneAreas",
        "vehicleRegistrationCodes",
        "schoolFacilityCounts",
        "procurementNotices",
    }
)

# Public display names. API consumers should not have to read maintainer
# prose to understand what a domain contains.
_PUBLIC_NAMES: dict[str, str] = {
    "regions": "Regions",
    "districts": "Districts",
    "municipalities": "Municipalities",
    "psc": "Postal codes (PSC)",
    "banks": "Bank identification codes",
    "holidays": "Public holidays",
    "companies": "Companies and ICO lookup",
    "vatRegistrations": "VAT registrations",
    "tradeRegistrations": "Trade registrations (ZRSR)",
    "streets": "Streets and addresses",
    "healthcareFacilities": "Healthcare facilities",
    "procurementNotices": "Public procurement notices",
    "schoolsDirectory": "School directory (institution level)",
    "phoneAreas": "Telephone primary areas",
    "vehicleRegistrationCodes": "Vehicle registration district codes",
    "courtDecisions": "Court decisions",
    "schoolFacilityCounts": "School facility counts",
}

_UPDATE_CADENCE: dict[str, str] = {
    "regions": "upstream release cycle",
    "districts": "manual",
    "municipalities": "manual",
    "psc": "unknown",
    "banks": "manual",
    "holidays": "annual",
    "companies": "manual",
    "vatRegistrations": "upstream daily",
    "tradeRegistrations": "unknown",
    "streets": "unknown",
    "healthcareFacilities": "unknown",
    "procurementNotices": "manual",
    "schoolsDirectory": "unknown",
    "phoneAreas": "manual",
    "vehicleRegistrationCodes": "static (historical)",
    "courtDecisions": "unknown",
    "schoolFacilityCounts": "semiannual",
}

_LIMITATIONS: dict[str, list[str]] = {
    "regions": [],
    "districts": ["PortalVS redistribution terms are unresolved."],
    "municipalities": ["PortalVS redistribution terms are unresolved."],
    "psc": [
        "Not national coverage.",
        "PortalVS redistribution terms are unresolved.",
    ],
    "banks": [],
    "holidays": ["Covers only the years present in the local dataset."],
    "companies": [
        "Seed-backed sample only, not full RPO coverage.",
        "Personal, stakeholder, and statutory-body fields are excluded.",
    ],
    "vatRegistrations": ["Blocked by a privacy gate; no runtime dataset is served."],
    "tradeRegistrations": ["No approved machine-readable source; no runtime dataset is served."],
    "streets": ["No approved machine-readable source; no runtime dataset is served."],
    "healthcareFacilities": ["No approved machine-readable source; no runtime dataset is served."],
    "procurementNotices": [
        "Includes only Slovak-buyer notices in the current 100-record TED snapshot.",
        "Not the national UVO procurement register.",
    ],
    "schoolsDirectory": ["No approved institution-level source; only aggregate counts are served elsewhere."],
    "phoneAreas": ["Redistribution terms of the regulator workbook are unresolved."],
    "vehicleRegistrationCodes": [
        "Historical legacy district codes only; not a current plate lookup.",
        "Does not decode full plates or identify vehicles or owners.",
    ],
    "courtDecisions": ["Reuse and privacy gates unresolved; no runtime dataset is served."],
    "schoolFacilityCounts": ["Aggregate counts only; not an institution-level school directory."],
}

_LICENCE_NAMES: dict[str, str] = {
    "regions": "Eurostat reuse policy",
    "procurementNotices": "TED / Publications Office reuse terms",
    "schoolFacilityCounts": "Creative Commons BY (version not specified)",
    "vatRegistrations": "CC0 per export page; CC 4.0 international per catalogue (discrepancy on file)",
    "holidays": "NBS website disclaimer (attribution, no modification)",
}

_RUNTIME_LAST_UPDATED: dict[str, str] = {
    "regions": REGIONS_LAST_UPDATED,
    "districts": DISTRICTS_LAST_UPDATED,
    "municipalities": MUNICIPALITIES_LAST_UPDATED,
    "psc": PSC_LAST_UPDATED,
    "banks": BANKS_LAST_UPDATED,
    "holidays": HOLIDAYS_LAST_UPDATED,
    "phoneAreas": PHONE_AREAS_LAST_UPDATED,
    "vehicleRegistrationCodes": VEHICLE_REGISTRATION_CODES_LAST_UPDATED,
    "schoolFacilityCounts": SCHOOL_FACILITY_COUNTS_LAST_UPDATED,
    "procurementNotices": PROCUREMENT_NOTICES_LAST_UPDATED,
}

_COVERAGE_MAP = {"complete": "complete", "partial": "partial", "seed-backed": "seed", "unknown": None}


class SourceCatalogueInvalidFormatError(ValueError):
    pass


class SourceCatalogueNotFoundError(KeyError):
    pass


@lru_cache(maxsize=1)
def load_sources_registry() -> dict[str, object]:
    with SOURCES_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def _public_status(source_id: str, entry: dict[str, object]) -> str:
    if source_id in _RUNTIME_DATASET_IDS:
        if source_id == "companies":
            return "seed"
        if source_id == "vehicleRegistrationCodes":
            return "historical"
        return "production"
    redistribution = str(entry.get("redistributionStatus") or "").strip().lower()
    if redistribution.startswith("blocked"):
        return "blocked"
    return "research"


def _public_licence_status(entry: dict[str, object]) -> str:
    licence_status = str(entry.get("licenceStatus") or "").strip().lower()
    if licence_status.startswith("blocked"):
        return "blocked"
    if "pending" in licence_status:
        return "pending"
    if any(marker in licence_status for marker in ("identif", "listed", "retained")):
        return "identified"
    if "verified" in licence_status:
        return "verified"
    return "pending"


def _public_terms_url(entry: dict[str, object]) -> str | None:
    terms_url = entry.get("termsUrl")
    if isinstance(terms_url, str) and terms_url.startswith("http"):
        return terms_url
    return None


def project_source(source_id: str, entry: dict[str, object]) -> PublicSourceEntry:
    """Map one internal registry entry to its curated public projection."""

    registry_last_updated = entry.get("lastUpdated")
    last_updated = _RUNTIME_LAST_UPDATED.get(source_id)
    if last_updated is None and isinstance(registry_last_updated, str):
        last_updated = registry_last_updated

    last_checked = entry.get("lastChecked")

    return PublicSourceEntry(
        id=source_id,
        name=_PUBLIC_NAMES.get(source_id, source_id),
        status=_public_status(source_id, entry),  # type: ignore[arg-type]
        coverage=_COVERAGE_MAP.get(str(entry.get("coverage"))),  # type: ignore[arg-type]
        source=SourceIdentity(
            name=str(entry.get("sourceName") or source_id),
            url=str(entry.get("sourceUrl") or ""),
        ),
        licence=SourceLicence(
            status=_public_licence_status(entry),  # type: ignore[arg-type]
            name=_LICENCE_NAMES.get(source_id),
            termsUrl=_public_terms_url(entry),
        ),
        attribution=entry.get("attribution") if isinstance(entry.get("attribution"), str) else None,
        lastUpdated=last_updated,
        lastChecked=last_checked if isinstance(last_checked, str) else None,
        updateCadence=_UPDATE_CADENCE.get(source_id),
        limitations=list(_LIMITATIONS.get(source_id, [])),
    )


def list_sources(
    status: str | None = None,
    coverage: str | None = None,
    q: str | None = None,
) -> list[PublicSourceEntry]:
    registry = load_sources_registry()
    entries = [project_source(source_id, entry) for source_id, entry in registry.items() if isinstance(entry, dict)]

    if status is not None:
        entries = [entry for entry in entries if entry.status == status]
    if coverage is not None:
        entries = [entry for entry in entries if entry.coverage == coverage]
    if q is not None:
        needle = q.strip().casefold()
        entries = [entry for entry in entries
                   if needle in entry.name.casefold() or needle in entry.source.name.casefold() or needle in entry.id.casefold()]

    return entries


def validate_source_id(source_id: str) -> str:
    if not re.fullmatch(SOURCE_ID_PATTERN, source_id):
        raise SourceCatalogueInvalidFormatError(source_id)
    return source_id


def get_source(source_id: str) -> PublicSourceEntry:
    validate_source_id(source_id)
    registry = load_sources_registry()
    entry = registry.get(source_id)
    if not isinstance(entry, dict):
        raise SourceCatalogueNotFoundError(source_id)
    return project_source(source_id, entry)
