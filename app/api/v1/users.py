"""
Authentication API routes
"""
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends

from app.dependencies import SessionDep
from app.schemas.users import ReadUser
from app.utils.security import get_current_user, validate_request, ValidateRequest

router = APIRouter(prefix="/user", tags=["User"], dependencies=[Depends(validate_request)])


@router.get("/profile", response_model=ReadUser, status_code=status.HTTP_200_OK)
async def profile(db: SessionDep, payload: ValidateRequest):
    current_user = get_current_user(payload=payload, db=db)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
  
    return current_user
   
