from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from codr.application.entities import User

T = TypeVar('T')


class UserCreateRequiredFields:
    pass


class UserFactory(ABC):
    @abstractmethod
    def create(self, fields: UserCreateRequiredFields) -> User:
        raise NotImplementedError




