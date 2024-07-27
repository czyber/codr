from codr.application.entities import User
from codr.models import UserModel
from codr.storage.mapper.base import Mapper
from codr.storage.mapper.repo import MapperRepo


class MapperUser(Mapper):
    @staticmethod
    def to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            username=model.username,
            github_access_token=model.github_access_token,
            repos=[MapperRepo.to_entity(repo) for repo in model.repos],
        )

    @staticmethod
    def to_model(entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            username=entity.username,
            github_access_token=entity.github_access_token,
            repos=[MapperRepo.to_model(repo) for repo in entity.repos],
        )
