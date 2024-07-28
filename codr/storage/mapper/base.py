from abc import ABC, abstractmethod

from codr.application.entities import Entity
from codr.models import Base


class Mapper(ABC):
    @staticmethod
    @abstractmethod
    def to_entity(model: Base) -> Entity:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def to_model(entity: Entity) -> Base:
        raise NotImplementedError
