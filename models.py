import datetime
from enum import IntEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, condecimal


class LineStatus(IntEnum):
    NOT_FINISHED = 1
    WON = 2  # 1st team won
    LOST = 3  # 1st team lost


class Line(BaseModel):
    uid: UUID = Field(default_factory=uuid4)
    coefficient: condecimal(decimal_places=2)
    deadline: datetime.datetime
    status: LineStatus = LineStatus.NOT_FINISHED
