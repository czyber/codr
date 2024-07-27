from abc import abstractmethod, ABC

from codr.storage.utils import E, M


class Mapper(ABC):
    @staticmethod
    @abstractmethod
    def to_entity(model: M) -> E:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def to_model(entity: E) -> M:
        raise NotImplementedError
