from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from pydantic import condecimal
from sqlmodel import SQLModel, Field


class Bet(SQLModel, table=True):
    uid: Optional[UUID] = Field(primary_key=True, default_factory=uuid4)
    event_uid: UUID
    amount: condecimal(decimal_places=2, gt=Decimal(0))
    coefficient: condecimal(decimal_places=2, gt=Decimal(1))
