from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import condecimal
from sqlmodel import SQLModel, Field


class Bet(SQLModel, table=True):
    uid: Optional[UUID] = Field(None, primary_key=True)
    event_uid: UUID
    amount: condecimal(decimal_places=2, gt=Decimal(0))
    coefficient: condecimal(decimal_places=2, gt=Decimal(1))
