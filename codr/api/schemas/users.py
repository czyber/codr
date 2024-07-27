from pydantic import BaseModel


class UserBase(BaseModel):
    pass


class UserCreate(UserBase):
    username: str


class Repo(BaseModel):
    owner: str
    name: str


class User(UserBase):
    id: str
    username: str
    github_access_token: str | None = None
    repos: list[Repo] = []

    class Config:
        from_attributes = True


class UserPatch(UserBase):
    username: str | None = None
    github_access_token: str | None = None


