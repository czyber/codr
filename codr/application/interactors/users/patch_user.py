from dataclasses import dataclass

from codr.api.schemas.users import UserPatch
from codr.application.entities import User
from codr.storage.user_repository import UserRepository
from codr.utils import Id


@dataclass
class PatchUserRequest:
    user_id: Id
    patch_user: UserPatch


@dataclass
class PatchUserResponse:
    user: User


class PatchUser:
    def __init__(self, user_repository: UserRepository) -> None:
        self.__user_repository = user_repository

    def execute(self, request: PatchUserRequest) -> PatchUserResponse:
        stored_user = self.__user_repository.get(request.user_id)
        update_data = request.patch_user.model_dump(exclude_unset=True)
        updated_user = stored_user.model_copy(update=update_data)
        user = self.__user_repository.update(updated_user)
        return PatchUserResponse(user=user)
