import datetime
from decimal import Decimal
from enum import IntEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, condecimal
from abc import ABC, abstractmethod


class HasID(ABC):
    @abstractmethod
    def get_id(self) -> str: ...


class LineStatus(IntEnum):
    NOT_FINISHED = 1
    WON = 2  # 1st team won
    LOST = 3  # 1st team lost


class Line(BaseModel, HasID):
    uid: UUID = Field(default_factory=uuid4)
    coefficient: condecimal(decimal_places=2, gt=Decimal(1))
    deadline: datetime.datetime
    status: LineStatus = LineStatus.NOT_FINISHED

    def get_id(self) -> str:
        return str(self.uid)