import datetime
from decimal import Decimal
from enum import IntEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, condecimal
from abc import ABC, abstractmethod


class HasID(ABC, BaseModel):
    @abstractmethod
    def get_id(self) -> str: ...


class EventStatus(IntEnum):
    NOT_FINISHED = 1
    WON = 2  # 1st team won
    LOST = 3  # 1st team lost


class EventPut(BaseModel):
    coefficient: condecimal(decimal_places=2, gt=Decimal(1))
    status: EventStatus = EventStatus.NOT_FINISHED


class EventCreate(EventPut):
    deadline: datetime.datetime


class Event(EventCreate, HasID):
    uid: UUID = Field(default_factory=uuid4)

    def get_id(self) -> str:
        return str(self.uid)