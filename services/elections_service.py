"""One local historical NRSR2023 snapshot; no source calls or PortalVS joins."""

from functools import lru_cache
from pathlib import Path

from schemas.common import ELECTIONS_NRSR2023_LAST_UPDATED, Page
from schemas.elections import ElectionCatalogueEntry, ElectionDataset, ElectionUnit


DATA_FILE = Path(__file__).resolve().parents[1] / "data/elections_nrsr_2023.json"


@lru_cache(maxsize=1)
def load_dataset() -> ElectionDataset:
    dataset = ElectionDataset.model_validate_json(DATA_FILE.read_bytes(), strict=True)
    if dataset.provenance.verifiedOn != ELECTIONS_NRSR2023_LAST_UPDATED:
        raise ValueError("election snapshot and freshness constant disagree")
    return dataset


def catalogue() -> list[ElectionCatalogueEntry]:
    dataset = load_dataset()
    return [ElectionCatalogueEntry(**dataset.election.model_dump(), national=dataset.national)]


def results(*, regionCode: str | None, districtCode: str | None,
            municipalityCode: str | None, limit: int, offset: int) -> Page[ElectionUnit]:
    filters = {"regionCode": regionCode, "districtCode": districtCode, "municipalityCode": municipalityCode}
    rows = [unit for unit in load_dataset().units
            if all(value is None or getattr(unit, field) == value for field, value in filters.items())]
    page = rows[offset:offset + limit]
    return Page[ElectionUnit](items=page, count=len(page), total=len(rows), limit=limit, offset=offset)
