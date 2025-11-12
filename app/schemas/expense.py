from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, field_serializer

from app.schemas.expense_split import CreateExpenseSplit, ReadExpenseSplit, UpdateExpenseSplit
from app.utils.constants import COMMON_DATE_TIME_FORMAT, DEFAULT_CURRENCY


class ExpenseBase(BaseModel):
    payer_id: int = -1
    amount: float = Field(..., gt=0)
    currency: Optional[str] = DEFAULT_CURRENCY
    description: Optional[str] = None
    receipt_url: Optional[str] = None
    paid_at: datetime = Field(..., example="2025-10-20 09:30:00",
                                 description=f"Datetime in format {COMMON_DATE_TIME_FORMAT}")


class CreateExpense(ExpenseBase):
    splits: List[CreateExpenseSplit]


class UpdateExpense(BaseModel):
    payer_id: Optional[int] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    receipt_url: Optional[str] = None
    paid_at: datetime = Field(None, example="2025-10-20 09:30:00",
                              description=f"Datetime in format {COMMON_DATE_TIME_FORMAT}")
    splits: Optional[List[UpdateExpenseSplit]] = None


class ReadExpense(ExpenseBase):
    id: int
    splits: List[ReadExpenseSplit]
    created_at: datetime = Field(..., example="2025-10-20 09:30:00",
                                 description=f"Datetime in format {COMMON_DATE_TIME_FORMAT}")
    updated_at: Optional[datetime] = Field(..., example="2025-10-20 09:30:00",
                                 description=f"Datetime in format {COMMON_DATE_TIME_FORMAT}")

    class Config:
        from_attributes = True
        
    @field_serializer("created_at", "paid_at", "updated_at")
    def serialize_created_at(self, dt: datetime, _info):
        if not dt:
            return dt
        return dt.strftime(COMMON_DATE_TIME_FORMAT)