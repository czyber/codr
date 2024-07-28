from pydantic import BaseModel

from codr.api.schemas.users import User
from codr.utils import Id


class GitHubBase(BaseModel):
    pass


class GitHubAccessTokenCreate(BaseModel):
    code: str
    user_id: str


class GitHubAccessToken(GitHubBase):
    access_token: str

    class Config:
        from_attributes = True


class RepoAdd(BaseModel):
    name: str
    owner: str
