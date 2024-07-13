from abc import ABC, abstractmethod

from codr.entities import Codebase
from codr.models import CodebaseModel
from codr.storage.storage import SessionLocal


class CodebaseStorage(ABC):
    @abstractmethod
    def create(self, codebase: Codebase) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, slug: str, sha: str) -> Codebase:
        raise NotImplementedError


class SqlCodebaseStorage(CodebaseStorage):
    def create(self, codebase: Codebase) -> None:
        with SessionLocal() as session:
            codebase_model = CodebaseModel(
                id=codebase.embedding_id,
                name=codebase.slug,
                sha=codebase.sha
            )
            session.add(codebase_model)
            session.commit()

    def get(self, slug: str, sha: str) -> Codebase | None:
        with SessionLocal() as session:
            codebase_model = session.query(CodebaseModel).filter_by(name=slug, sha=sha).first()
            if codebase_model is None:
                return None
            return Codebase(sha=codebase_model.sha, slug=codebase_model.name, embedding_id=codebase_model.id)
