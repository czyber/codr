from abc import ABC, abstractmethod

from codr.storage.utils import E
from codr.utils import Id


class DAO(ABC):
    @abstractmethod
    def insert(self, entity: E) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, id_: Id) -> E:
        raise NotImplementedError

    @abstractmethod
    def update(self, entity: E) -> E:
        raise NotImplementedError

    @abstractmethod
    def remove(self, id_: Id) -> E:
        raise NotImplementedError

    @abstractmethod
    def get_by(self, **kwargs) -> E:
        raise NotImplementedError
