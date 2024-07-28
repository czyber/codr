from dataclasses import dataclass
from uuid import uuid4

from codr.application.entities import User
from codr.storage.user_repository import UserRepository


@dataclass
class CreateUserRequest:
    username: str


@dataclass
class CreateUserResponse:
    user: User


class CreateUser:
    def __init__(self, user_repository: UserRepository) -> None:
        self.__user_repository = user_repository

    def execute(self, request: CreateUserRequest) -> CreateUserResponse:
        user = self.__user_repository.create_and_add({"username": request.username})
        return CreateUserResponse(user=user)
