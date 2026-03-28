"""
Authentication API routes
"""
from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from starlette import status

from app.dependencies import SessionDep
from app.schemas.group_member import CreateGroupMember, ReadGroupMember
from app.services.group_member_service import GroupMemberService
from app.utils.security import CurrentUser, validate_request

router = APIRouter(prefix="/groups/{group_id}/members", tags=["Group Members"],
                   dependencies=[Depends(validate_request)])


# ---- List Members ----
@router.get("/", response_model=List[ReadGroupMember], status_code=status.HTTP_200_OK)
def list_members(group_id: int, db: SessionDep, current_user: CurrentUser):
    
    with GroupMemberService(session=db, current_user=current_user) as service:
        members = service.get_all(group_id)
    return members


@router.post("/", response_model=ReadGroupMember, status_code=status.HTTP_201_CREATED)
def add_member(group_id: int, member_data: CreateGroupMember, db: SessionDep,
               current_user: CurrentUser):
    
    with GroupMemberService(session=db, current_user=current_user) as service:
        members = service.add_member(group_id=group_id, data=member_data)
    return members


# ---- Remove Member ----
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(group_id: int, user_id: int, db: SessionDep , current_user: CurrentUser):
    
    with GroupMemberService(session=db, current_user=current_user) as service:
        service.remove_member(group_id=group_id, user_id=user_id)