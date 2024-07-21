from pydantic import BaseModel

from codr.utils import IdType


class Entity(BaseModel):
    id: IdType


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


class User(Entity):
    username: str
    github_access_token: str | None = None
