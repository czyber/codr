from codr.application.entities import Repo
from codr.models import RepoModel
from codr.storage.mapper.base import Mapper


class MapperRepo(Mapper):
    @staticmethod
    def to_entity(model: RepoModel) -> Repo:
        return Repo(
            id=model.id,
            name=model.name,
            owner=model.owner,
        )

    @staticmethod
    def to_model(entity: Repo) -> RepoModel:
        return RepoModel(
            id=entity.id,
            name=entity.name,
            owner=entity.owner,
        )
