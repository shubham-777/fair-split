"""
Authentication API routes
"""
from fastapi import APIRouter, HTTPException, status

from app.config import settings
from app.dependencies import SessionDep
from app.models.user import User
from app.schemas.users import ForgotPasswordRequest, ReadUser, ResetPasswordRequest, Token, UserCreate, UserLogin
from app.services.user_service import UserService
from app.utils.helper import reset_password_mail_content
from app.utils.plugins import redis_client
from app.utils.security import create_access_token, create_refresh_token, create_reset_token, decode_reset_token, \
    hash_password, verify_password
from app.utils.tasks import send_mail

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=ReadUser, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, db: SessionDep):
    """
    Register a new user
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hash_password(user_data.password)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: SessionDep):
    """
    Authenticate user and return JWT tokens
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: SessionDep):
    """
    Refresh access token using refresh token
    """
    from app.utils.security import decode_token
    try:
        payload = decode_token(refresh_token)
    except Exception:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
        
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    new_access_token = create_access_token(data={"sub": user.email})
    new_refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.post("/forgot-password", status_code=status.HTTP_201_CREATED)
async def forgot_password(forgot_password: ForgotPasswordRequest, db: SessionDep):
    cooldown_key = f"reset_cooldown:{forgot_password.email}"
    if redis_client.exists(cooldown_key):
        return {
            "detail": "Password reset email already sent recently. Please check your inbox or try again later."
        }
    
    with UserService(session=db) as service:
        user = service.get_by_email(email=forgot_password.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        token = create_reset_token(email=user.email)
        send_mail(subject="Password Reset Request",
                  body=reset_password_mail_content(user.username, token),
                  to_emails=[user.email, ])
        
        redis_client.setex(cooldown_key, settings.RESET_TOKEN_EXPIRE_MINUTES * 60, 1)
    
    return {
        "detail": "Password reset email sent"
    }

@router.post("/reset-password", status_code=status.HTTP_201_CREATED)
async def reset_password(reset_password: ResetPasswordRequest, db: SessionDep):
    email = decode_reset_token(reset_password.token)
    with UserService(session=db) as service:
        user = service.get_by_email(email=email)
        service.update_password(user=user, new_password=reset_password.new_password)
    return {"detail": "Password updated successfully"}
