from typing import TypeVar

from codr.application.entities import Entity
from codr.models import Base

E = TypeVar('E', bound=Entity)
M = TypeVar('M', bound=Base)
