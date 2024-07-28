from codr.application.entities import User
from codr.models import UserModel
from codr.storage.mapper.base import Mapper
from codr.storage.mapper.repo import MapperRepo
from codr.storage.mapper.version_control_info import MapperVersionControlInfo


class MapperUser(Mapper):
    @staticmethod
    def to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            username=model.username,
            version_control_infos=[
                MapperVersionControlInfo.to_entity(info)
                for info in model.version_control_infos
            ],
            repos=[MapperRepo.to_entity(repo) for repo in model.repos],
        )

    @staticmethod
    def to_model(entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            username=entity.username,
            version_control_infos=[
                MapperVersionControlInfo.to_model(info)
                for info in entity.version_control_infos
            ],
            repos=[MapperRepo.to_model(repo) for repo in entity.repos],
        )
