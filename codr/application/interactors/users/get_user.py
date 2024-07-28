from dataclasses import dataclass

from codr.application.entities import User
from codr.storage.user_repository import UserRepository
from codr.utils import Id


@dataclass
class GetUserRequest:
    id: Id


@dataclass
class GetUserResponse:
    user: User


class GetUser:
    def __init__(self, user_repository: UserRepository):
        self.__user_repository = user_repository

    def execute(self, request: GetUserRequest) -> GetUserResponse:
        user = self.__user_repository.get(request.id)
        return GetUserResponse(user=user)


# Code: c066b8da3aa7198e0928
