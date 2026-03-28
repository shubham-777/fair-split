"""
Security utilities: JWT and password hashing
"""
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional, TypeAlias

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from starlette import status

from app.config import settings
from app.dependencies import SessionDep
from app.models.user import User
from app.utils.helper import today_datetime

# Password hashing context
password_hash = PasswordHash.recommended()
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password"""
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(tz=timezone.utc) + expires_delta
    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.now(tz=timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_reset_token(email: str):
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": email, "exp": expire}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

def decode_reset_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        if today_datetime() > datetime.fromtimestamp(payload['exp'], tz=timezone.utc):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def decode_token(token: str) -> Optional[dict]:
    """
    Decode and verify JWT token
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except InvalidTokenError as e:
        raise e
    
def validate_request(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]):
        token = credentials.credentials
        try:
            payload = decode_token(token=token)
            if today_datetime() > datetime.fromtimestamp(payload['exp'], tz=timezone.utc):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        

ValidateRequest: TypeAlias = Annotated[dict, Depends(validate_request)]


def get_current_user(payload: Annotated[dict, Depends(validate_request)], db: SessionDep) -> User:
    user_email: str = payload.get("sub")
    
    if user_email is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: missing email", )
    
    # Query user from database
    user = db.query(User).filter(User.email == user_email).first()
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found", )
    
    return user

CurrentUser: TypeAlias = Annotated[User, Depends(get_current_user)]