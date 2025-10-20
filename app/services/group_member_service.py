from __future__ import annotations

from sqlalchemy import select

from app.models import GroupMember
from app.services.base_service import BaseService


class GroupMemberService(BaseService):
    
    def get_by_id(self, _id: int) -> type[GroupMember] | None:
        return self.session.get(GroupMember, _id)
    
    def get_all(self, group_id: int):
       group_members = self.session.execute(select(GroupMember).where(GroupMember.group_id==group_id)).scalars().all()
       return group_members