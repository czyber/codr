from pydantic import BaseModel

from codr.api.schemas.users import User


class GitHubBase(BaseModel):
    pass


class GitHubAccessTokenCreate(BaseModel):
    code: str
    user_id: str


class GitHubAccessToken(GitHubBase):
    user: User

    class Config:
        from_attributes = True
