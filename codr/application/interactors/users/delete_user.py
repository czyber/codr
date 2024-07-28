from dataclasses import dataclass

from codr.application.entities import User
from codr.storage.user_repository import UserRepository
from codr.utils import Id


@dataclass
class DeleteUserRequest:
    user_id: Id


@dataclass
class DeleteUserResponse:
    user: User


class DeleteUser:
    def __init__(self, user_repository: UserRepository) -> None:
        self.__user_repository = user_repository

    def execute(self, request: DeleteUserRequest) -> DeleteUserResponse:
        user = self.__user_repository.remove(request.user_id)
        return DeleteUserResponse(user=user)
