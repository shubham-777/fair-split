"""
User Pydantic schemas
"""
from pydantic import BaseModel, EmailStr, Field, field_serializer
from typing import Optional
from datetime import datetime

from app.utils.constants import COMMON_DATE_TIME_FORMAT


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=255)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    avatar_url: Optional[str] = None
    
    
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

    
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class ReadUser(UserBase):
    id: int
    avatar_url: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime = Field(..., example="2025-10-20 09:30:00",
                                 description=f"Datetime in format {COMMON_DATE_TIME_FORMAT}")
    
    class Config:
        from_attributes = True
    
    @field_serializer("created_at")
    def serialize_created_at(self, dt: datetime, _info):
        if not dt:
            return dt
        return dt.strftime(COMMON_DATE_TIME_FORMAT)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None