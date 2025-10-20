from __future__ import annotations

from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from starlette import status

from app.models import Group, GroupMember
from app.schemas.group import CreateGroup, UpdateGroup
from app.services.base_service import BaseService


class GroupService(BaseService):
    
    def get_by_id(self, _id: int) -> type[Group] | None:
        return self.session.get(Group, _id)
    
    def create(self, data: CreateGroup) -> Group:
        group = Group(name=data.name, description=data.description, creator_id=self.user.id)
        group = self.add_and_commit(group)
        
        group_member = GroupMember(group_id=group.id, user_id=self.user.id, is_admin=True)
        self.add_and_commit(group_member)
        return group
    
    def get_all_for_user(self, user_id: int = None):
        if not user_id:
            user_id = self.user.id
        
        return self.session.execute(select(Group).join(GroupMember).filter(GroupMember.user_id==user_id)).scalars().all()
        
    def delete_group(self, group_id: int):
        group = self.get_by_id(_id=group_id)
        
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
        if group.creator_id != self.user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the creator can delete this group")
        
        self.delete_and_commit(group)
        
    def update_group(self, data: UpdateGroup):
        group = self.get_by_id(_id=data.id)
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
        if group.creator_id != self.user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the creator can delete this group")
        
        for key, value in data.model_dump(exclude={'id'}, exclude_unset=True).items():
            setattr(group, key, value)
        
        group = self.update_and_commit(obj=group)
        return group
        
            