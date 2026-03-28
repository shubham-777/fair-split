from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_serializer

from app.schemas.users import ReadUserMin
from app.utils.constants import COMMON_DATE_TIME_FORMAT


class ExpenseSplitBase(BaseModel):
    user_id: int
    share: Optional[int] = Field(None, gt=0)


class CreateExpenseSplit(ExpenseSplitBase):
    pass


class UpdateExpenseSplit(BaseModel):
    user_id: int = None
    share: Optional[int] = Field(None, gt=0)

class ReadExpenseSplit(CreateExpenseSplit):
    id: int
    user: ReadUserMin
    created_at: datetime = Field(...,example="2025-10-20 09:30:00",
                                 description=f"Datetime in format {COMMON_DATE_TIME_FORMAT}")
    updated_at: Optional[datetime] = Field(..., example="2025-10-20 09:30:00",
                                 description=f"Datetime in format {COMMON_DATE_TIME_FORMAT}")
    
    @field_serializer("created_at", "updated_at")
    def serialize_created_at(self, dt: datetime, _info):
        if not dt:
            return dt
        return dt.strftime(COMMON_DATE_TIME_FORMAT)


    class Config:
        from_attributes = True