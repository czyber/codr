from typing import Generator

from sqlalchemy.orm import Session

from codr.models import Base
from codr.storage.dao.abstract_dao import DAO
from codr.utils import Kwargs, Id


class SqlDAO(DAO):
    def __init__(self, model: type[Base], session: Session) -> None:
        self.__model = model
        self.__session = session

    def insert(self, kwargs: Kwargs) -> None:
        self.__session.add(self.__model(**kwargs))
        self.__session.commit()

    def get(self, id_: Id) -> Kwargs:
        return self.__session.query(self.__model).filter_by(id=id_).first().to_dict()

    def update(self, id_: Id, kwargs: Kwargs) -> Kwargs:
        self.__session.query(self.__model).filter_by(id=id_).update(kwargs)
        self.__session.commit()
        return kwargs

    def remove(self, id_: Id) -> Kwargs:
        kwargs = self.get(id_)
        self.__session.query(self.__model).filter_by(id=id_).delete()
        self.__session.commit()
        return kwargs
