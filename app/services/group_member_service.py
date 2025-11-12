from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select
from starlette import status

from app.models import GroupMember
from app.schemas.group import CreateGroup
from app.schemas.group_member import CreateGroupMember
from app.services.base_service import BaseService
from app.services.group_service import GroupService
from app.services.user_service import UserService


class GroupMemberService(BaseService):
    
    def get_by_id(self, _id: int) -> type[GroupMember] | None:
        return self.session.get(GroupMember, _id)
    
    def get_all(self, group_id: int):
       group_members = self.session.execute(select(GroupMember).where(GroupMember.group_id==group_id)).scalars().all()
       return group_members
    
    def add_member(self, group_id: int, data: CreateGroupMember) -> GroupMember:
        group = GroupService(session=self.session, current_user=self.user).get_by_id(_id=group_id)
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
        
        if group.creator_id != self.user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add members")
        
        user = UserService(session=self.session).get_by_email(email=data.user_email)
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
        
        is_member = any(m.id == user.id for m in group.members)
        if is_member:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a member")
        
        group_member = GroupMember(group_id=group_id, user_id=user.id)
        group_member = self.add_and_commit(obj=group_member)
        return group_member



        

        
    