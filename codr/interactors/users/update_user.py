from dataclasses import dataclass

from codr.entities import User
from codr.storage.user_repository import UserRepository


@dataclass
class UpdateUserRequest:
    user: User


@dataclass
class UpdateUserResponse:
    user: User


class UpdateUser:
    def __init__(self, user_repository: UserRepository) -> None:
        self.__user_repository = user_repository

    def execute(self, request: UpdateUserRequest) -> UpdateUserResponse:
        user = self.__user_repository.update_user(request.user)
        return UpdateUserResponse(user=user)
