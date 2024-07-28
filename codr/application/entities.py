from dataclasses import dataclass
from datetime import datetime, timedelta
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


@dataclass
class SetTokenRequest:
    access_token: str
    refresh_token: str
    access_token_expires_in: int
    refresh_token_expires_in: int
    version_control_type: VersionControlType


class User(Entity):
    username: str
    version_control_infos: list[VersionControlInfo] = []
    repos: list[Repo] = []

    def has_valid_access_token(self, version_control_type: VersionControlType) -> bool:
        return any(vci.version_control_type == version_control_type and vci.is_valid for vci in self.version_control_infos)

    def get_access_token(self, version_control_type: VersionControlType) -> str:
        for vci in self.version_control_infos:
            if vci.version_control_type == version_control_type:
                return vci.access_token
        raise ValueError(f"No access token found for {version_control_type}")

    def get_refresh_token(self, version_control_type: VersionControlType) -> str:
        for vci in self.version_control_infos:
            if vci.version_control_type == version_control_type:
                return vci.refresh_token
        raise ValueError(f"No refresh token found for {version_control_type}")

    def has_version_control_info(self, version_control_type: VersionControlType) -> bool:
        return any(vci.version_control_type == version_control_type for vci in self.version_control_infos)

    def set_access_token(self, set_token_request: SetTokenRequest):
        if self.has_version_control_info(set_token_request.version_control_type):
            self.update_access_token(set_token_request)
        else:
            self.add_access_token(set_token_request)

    def update_access_token(self, set_token_request: SetTokenRequest):
        for vci in self.version_control_infos:
            if vci.version_control_type == set_token_request.version_control_type:
                vci.access_token = set_token_request.access_token
                vci.refresh_token = set_token_request.refresh_token
                vci.access_token_expires_at = datetime.now() + timedelta(seconds=set_token_request.access_token_expires_in)
                vci.refresh_token_expires_at = datetime.now() + timedelta(seconds=set_token_request.refresh_token_expires_in)
                return
        raise ValueError(f"No version control info found for {set_token_request.version_control_type}")

    def add_access_token(self, set_token_request: SetTokenRequest):
        vci = VersionControlInfo(
            access_token=set_token_request.access_token,
            refresh_token=set_token_request.refresh_token,
            access_token_expires_at=datetime.now() + timedelta(seconds=set_token_request.access_token_expires_in),
            refresh_token_expires_at=datetime.now() + timedelta(seconds=set_token_request.refresh_token_expires_in),
            version_control_type=set_token_request.version_control_type
        )
        self.version_control_infos.append(vci)
        return vci
