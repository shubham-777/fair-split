"""
Authentication API routes
"""
from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from app.dependencies import SessionDep
from app.models.user import User
from app.schemas.group_member import CreateGroupMember, ReadGroupMember
from app.services.group_member_service import GroupMemberService
from app.utils.security import CurrentUser, get_current_user, validate_request

router = APIRouter(prefix="/groups/{group_id}/members", tags=["Group Members"],
                   dependencies=[Depends(validate_request)])


# ---- List Members ----
@router.get("/", response_model=List[ReadGroupMember], status_code=HTTP_200_OK)
def list_members(group_id: int, db: SessionDep, current_user: User = Depends(get_current_user)):
    
    with GroupMemberService(session=db, current_user=current_user) as service:
        members = service.get_all(group_id)
    return members


@router.post("/", response_model=ReadGroupMember, status_code=HTTP_201_CREATED)
def add_member(group_id: int, member_data: CreateGroupMember, db: SessionDep,
               current_user: CurrentUser):
    
    with GroupMemberService(session=db, current_user=current_user.) as service:
        members = service.add_member(group_id=group_id, data=member_data)
    return members


# ---- Remove Member ----
@router.delete("/{user_id}", status_code=204)
def remove_member(group_id: int, user_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Only creator or admin can remove members
    current_member = db.query(GroupMember).filter_by(group_id=group_id, user_id=current_user.id).first()
    if not current_member or (current_member.user_id != group.creator_id and not current_member.is_admin):
        raise HTTPException(status_code=403, detail="Not authorized to remove members")

    member_to_remove = db.query(GroupMember).filter_by(group_id=group_id, user_id=user_id).first()
    if not member_to_remove:
        raise HTTPException(status_code=404, detail="Member not found")

    # Prevent removing the creator
    if member_to_remove.user_id == group.creator_id:
        raise HTTPException(status_code=400, detail="Cannot remove group creator")

    db.delete(member_to_remove)
    db.commit()
    return