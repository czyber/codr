from datetime import datetime
from enum import Enum, auto
from uuid import uuid4

from pydantic import BaseModel

from codr.common.utils import BaseEnum
from codr.utils import IdType


def new_uuid():
    return str(uuid4())


class Entity(BaseModel):
    id: IdType = new_uuid()


class Embedding(Entity):
    embedding: str


class Codebase(Entity):
    sha: str
    slug: str
    embedding_id: str


class Document(Entity):
    content: str
    source: str
    sha: str


class Repo(Entity):
    owner: str
    name: str


class VersionControlType(BaseEnum):
    GITHUB = auto()
    GITLAB = auto()
    BITBUCKET = auto()


class VersionControlInfo(Entity):
    access_token: str
    refresh_token: str
    access_token_expires_at: datetime
    refresh_token_expires_at: datetime
    version_control_type: VersionControlType

    @classmethod
    def create_github(cls, access_token: str, refresh_token: str, access_token_expires_at: datetime, refresh_token_expires_at: datetime):
        return cls(
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_expires_at=access_token_expires_at,
            refresh_token_expires_at=refresh_token_expires_at,
            version_control_type=VersionControlType.GITHUB
        )

    @property
    def is_valid(self) -> bool:
        return datetime.now() < self.access_token_expires_at


class User(Entity):
    username: str
    version_control_infos: list[VersionControlInfo] = []
    repos: list[Repo] = []

    def is_authenticated(self, version_control_type: VersionControlType) -> bool:
        return any(vci.version_control_type == version_control_type and vci.is_valid for vci in self.version_control_info)

    def get_access_token(self, version_control_type: VersionControlType) -> str:
        for vci in self.version_control_info:
            if vci.version_control_type == version_control_type:
                return vci.access_token
        raise ValueError(f"No access token found for {version_control_type}")
