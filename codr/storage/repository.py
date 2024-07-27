from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic
from uuid import uuid4

from sqlalchemy import Column, String

from codr.application.entities import Entity
from codr.storage.dao.abstract_dao import DAO
from codr.utils import Kwargs, Id

E = TypeVar('E', bound=Entity)


class Factory(Generic[E]):
    def __init__(self, entity: type[E]) -> None:
        self.__entity = entity

    @property
    def entity(self) -> type[E]:
        return self.__entity

    def construct(self, kwargs: Kwargs) -> E:
        id_ = str(uuid4())
        kwargs['id'] = id_
        return self.__entity(**kwargs)

    def reconstitute(self, kwargs: Kwargs) -> E:
        return self.__entity(**kwargs)

    @staticmethod
    def deconstruct(entity: E) -> Kwargs:
        return entity.model_dump()


class AbstractRepository(Generic[E], metaclass=ABCMeta):
    @abstractmethod
    def add(self, entity: E) -> E:
        raise NotImplementedError

    @abstractmethod
    def create(self, kwargs: Kwargs) -> E:
        raise NotImplementedError

    @abstractmethod
    def create_and_add(self, kwargs: Kwargs) -> E:
        raise NotImplementedError

    @abstractmethod
    def remove(self, id_: Id) -> E:
        raise NotImplementedError

    @abstractmethod
    def get(self, id_: Id) -> E:
        raise NotImplementedError

    @abstractmethod
    def update(self, entity: E) -> E:
        raise NotImplementedError


class Repository(AbstractRepository[E], Generic[E]):
    def __init__(self, dao: DAO, factory: Factory[E]):
        self.__dao = dao
        self.__factory = factory

    def add(self, entity: E) -> E:
        self.__dao.insert(entity)
        return entity

    def create(self, kwargs: Kwargs) -> E:
        return self.__factory.construct(kwargs)

    def create_and_add(self, kwargs: Kwargs) -> E:
        entity = self.create(kwargs)
        return self.add(entity)

    def remove(self, id_: Id) -> E:
        entity = self.__dao.get(id_)
        self.__dao.remove(id_)
        return entity

    def get(self, id_: Id) -> E:
        return self.__dao.get(id_)

    def update(self, entity: E) -> E:
        return self.__dao.update(entity)
