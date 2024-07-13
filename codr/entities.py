from dataclasses import dataclass


@dataclass
class Embedding:
    id: str
    embedding: str


@dataclass
class Codebase:
    sha: str
    slug: str
    embedding_id: str


@dataclass
class Document:
    id: str
    content: str
    source: str
    sha: str


@dataclass
class User:
    id: str
    username: str
