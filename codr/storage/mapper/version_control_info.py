from codr.application.entities import VersionControlInfo, VersionControlType
from codr.models import VersionControlInfoModel
from codr.storage.mapper.base import Mapper


class MapperVersionControlInfo(Mapper):
    @staticmethod
    def to_entity(model: VersionControlInfoModel) -> VersionControlInfo:
        return VersionControlInfo(
            id=model.id,
            access_token=model.access_token,
            refresh_token=model.refresh_token,
            access_token_expires_at=model.access_token_expires_at,
            refresh_token_expires_at=model.refresh_token_expires_at,
            version_control_type=VersionControlType[model.version_control_type],
        )

    @staticmethod
    def to_model(entity: VersionControlInfo) -> VersionControlInfoModel:
        return VersionControlInfoModel(
            id=entity.id,
            access_token=entity.access_token,
            refresh_token=entity.refresh_token,
            access_token_expires_at=entity.access_token_expires_at,
            refresh_token_expires_at=entity.refresh_token_expires_at,
            version_control_type=entity.version_control_type.value,
        )
