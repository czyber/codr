from abc import ABC, abstractmethod

from codr.utils import Kwargs, Id


class DAO(ABC):
    @abstractmethod
    def insert(self, kwargs: Kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, id_: Id) -> Kwargs:
        raise NotImplementedError

    @abstractmethod
    def update(self, id_: Id, kwargs: Kwargs) -> Kwargs:
        raise NotImplementedError

    @abstractmethod
    def remove(self, id_: Id) -> Kwargs:
        raise NotImplementedError
