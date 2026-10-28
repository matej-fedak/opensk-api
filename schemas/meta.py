from typing import Literal

from schemas.common import PublicModel


class ProjectInfo(PublicModel):
    name: str
    version: str
    apiVersion: Literal["v1"]
    apiNamespace: Literal["/v1"]
    docs_url: str


class Health(PublicModel):
    status: Literal["ok"]
    timestamp: str
