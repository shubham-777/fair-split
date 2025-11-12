from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_serializer

from app.schemas.users import ReadUser
from app.utils.constants import COMMON_DATE_TIME_FORMAT


class BaseGroup(BaseModel):
    class Config:
        from_attributes = True
    
    group_id: int
    user_id: int
    is_admin: bool = False
    
class CreateGroupMember(BaseModel):
    user_email: EmailStr
    is_admin: bool = False
    

class ReadGroupMember(BaseGroup):
    id: int
    joined_at: datetime = Field(...,
                                example="2025-10-20 09:30:00",
                                description=f"Datetime in format {COMMON_DATE_TIME_FORMAT}")
    
    @field_serializer("joined_at")
    def serialize_created_at(self, dt: datetime, _info):
        if not dt:
            return dt
        return dt.strftime(COMMON_DATE_TIME_FORMAT)


class ReadGroupMember(BaseModel):
    id: int
    is_admin: bool = False
    joined_at: datetime = Field(..., example="2025-10-20 09:30:00",
                                description=f"Datetime in format {COMMON_DATE_TIME_FORMAT}")
    user: ReadUser
    
    @field_serializer("joined_at")
    def serialize_created_at(self, dt: datetime, _info):
        if not dt:
            return dt
        return dt.strftime(COMMON_DATE_TIME_FORMAT)