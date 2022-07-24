import datetime
from decimal import Decimal
from enum import IntEnum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import condecimal, BaseModel
from sqlmodel import SQLModel, Field


class EventStatus(IntEnum):
    NOT_FINISHED = 1
    WON = 2  # 1st team won
    LOST = 3  # 1st team lost


class BetCreate(SQLModel):
    event_uid: UUID
    amount: condecimal(decimal_places=2, gt=Decimal(0))


class Bet(BetCreate, table=True):
    uid: Optional[UUID] = Field(primary_key=True, default_factory=uuid4)
    coefficient: condecimal(decimal_places=2, gt=Decimal(1))
    status: EventStatus = EventStatus.NOT_FINISHED


class Event(BaseModel):
    uid: UUID
    deadline: datetime.datetime
    coefficient: condecimal(decimal_places=2, gt=Decimal(1))
    status: EventStatus


class EventStatusUpdate(BaseModel):
    uid: UUID
    status: EventStatus
