from datetime import datetime

from pydantic import BaseModel

from codr.application.entities import VersionControlType


class UserBase(BaseModel):
    pass


class UserCreate(UserBase):
    username: str


class Repo(BaseModel):
    owner: str
    name: str


class VersionControlInfo(BaseModel):
    access_token: str
    refresh_token: str
    access_token_expires_at: datetime
    refresh_token_expires_at: datetime
    version_control_type: VersionControlType


class User(UserBase):
    id: str
    username: str
    github_access_token: str | None = None
    repos: list[Repo] = []
    version_control_infos: list[VersionControlInfo] = []

    class Config:
        from_attributes = True


class UserPatch(UserBase):
    username: str | None = None
    github_access_token: str | None = None
