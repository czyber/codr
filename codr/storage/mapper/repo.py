from codr.application.entities import Repo
from codr.models import RepoModel
from codr.storage.mapper.base import Mapper


class MapperRepo(Mapper):
    @staticmethod
    def to_entity(model: RepoModel) -> Repo | None:
        if model is None:
            return None
        return Repo(
            id=model.id,
            name=model.name,
            owner=model.owner,
            sha=model.sha,
            embeddings_created=model.embeddings_created,
        )

    @staticmethod
    def to_model(entity: Repo) -> RepoModel:
        return RepoModel(
            id=entity.id,
            name=entity.name,
            owner=entity.owner,
            sha=entity.sha,
            embeddings_created=entity.embeddings_created,
        )
