"""Local, title-free ITMS21+ references. No network, joins or database."""

import json
from functools import lru_cache
from pathlib import Path

from schemas.eu_funds import Dataset

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "eu_funds_projects.json"


@lru_cache(maxsize=1)
def load_dataset() -> Dataset:
    return Dataset.model_validate(json.loads(DATA_FILE.read_text(encoding="utf-8")))


@lru_cache(maxsize=1)
def project_index():
    return {project.projectCode: project for project in load_dataset().projects}


def clear_cache() -> None:
    project_index.cache_clear()
    load_dataset.cache_clear()


def get_project(code: str):
    # Excluded source projects are absent, exactly like any other unknown code.
    return project_index().get(code)


def list_projects(*, limit=50, offset=0, programmeCode=None, callCode=None,
                  beneficiaryIco=None, inImplementation=None, completed=None, nuts=None):
    matches = []
    for project in load_dataset().projects:
        if programmeCode is not None and project.programme.code != programmeCode:
            continue
        if callCode is not None and project.call.code != callCode:
            continue
        if beneficiaryIco is not None and project.beneficiary.ico != beneficiaryIco:
            continue
        if inImplementation is not None and project.status.inImplementation != inImplementation:
            continue
        if completed is not None and project.status.completed != completed:
            continue
        if nuts is not None and not any(place.nuts == nuts for place in project.implementationRegions):
            continue
        matches.append(project)
    items = matches[offset:offset + limit]
    return {"items": items, "count": len(items), "total": len(matches), "limit": limit, "offset": offset}
