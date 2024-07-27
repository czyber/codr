from uuid import uuid4

from pydantic import BaseModel

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


class User(Entity):
    username: str
    github_access_token: str | None = None
    repos: list[Repo] = []
