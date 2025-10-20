from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr, Field, field_serializer

from app.schemas.group_member import ReadGroupMember
from app.schemas.users import ReadUser
from app.utils.constants import COMMON_DATE_TIME_FORMAT


class BaseGroup(BaseModel):
    class Config:
        from_attributes = True
        
    name: str
    description: str | None = None


class CreateGroup(BaseGroup):
    pass

class UpdateGroup(CreateGroup):
    id: int
    name: str | None = None
    description: str | None = None

class ReadGroup(BaseGroup):
    id: int
    creator_id: int
    created_at: datetime = Field(...,example="2025-10-20 09:30:00",description=f"Datetime in format {COMMON_DATE_TIME_FORMAT}")
    updated_at: datetime | None = Field(...,example="2025-10-20 09:30:00",description=f"Datetime in format {COMMON_DATE_TIME_FORMAT}")
    
    @field_serializer("created_at", "updated_at")
    def serialize_created_at(self, dt: datetime, _info):
        if not dt:
            return dt
        return dt.strftime(COMMON_DATE_TIME_FORMAT)
    
class ReadGroupWithUserRelation(ReadGroup):
    creator: ReadUser


class ReadGroupWithMembersRelation(ReadGroup):
    members: List[ReadGroupMember]


        