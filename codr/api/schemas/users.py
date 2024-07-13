from pydantic import BaseModel


class UserBase(BaseModel):
    pass


class UserCreate(UserBase):
    username: str


class User(UserBase):
    id: str
    username: str
    github_access_token: str | None = None

    class Config:
        orm_mode = True
