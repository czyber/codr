from typing import Generator, Generic

from sqlalchemy.orm import Session

from codr.models import Base
from codr.storage.dao.abstract_dao import DAO
from codr.storage.mapper.base import Mapper
from codr.storage.utils import E, M
from codr.utils import Id, Kwargs


class SqlDAO(DAO):
    def __init__(self, model: type[M], session: Session, mapper: Mapper) -> None:
        self.__model = model
        self.__session = session
        self.__mapper = mapper

    def insert(self, entity: type[E]) -> None:
        self.__session.add(self.__mapper.to_model(entity))
        self.__session.commit()

    def get(self, id_: Id) -> E:
        model = self.__session.query(self.__model).filter_by(id=id_).first()
        return self.__mapper.to_entity(model)

    def get_by(self, **kwargs) -> E:
        model = self.__session.query(self.__model).filter_by(**kwargs).first()
        return self.__mapper.to_entity(model)

    def update(self, entity: E) -> E:
        stored_entity = self.get(entity.id)
        if stored_entity is None:
            raise ValueError(f"Entity with id {entity.id} not found")
        model = self.__mapper.to_model(entity)
        self.__session.merge(model)
        self.__session.commit()
        return self.__mapper.to_entity(model)

    def remove(self, id_: Id) -> E:
        entity = self.get(id_)
        model = self.__session.query(self.__model).filter_by(id=id_).first()
        self.__session.delete(model)
        self.__session.commit()
        return entity
