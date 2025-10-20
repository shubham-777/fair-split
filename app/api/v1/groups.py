"""
Authentication API routes
"""
from typing import List

from fastapi import APIRouter, status
from fastapi.params import Depends

from app.dependencies import SessionDep
from app.schemas.group import CreateGroup, ReadGroup, ReadGroupWithMembersRelation, ReadGroupWithUserRelation, \
    UpdateGroup
from app.services.group_service import GroupService
from app.utils.security import get_current_user, validate_request, ValidateRequest

router = APIRouter(prefix="/group", tags=["Group"], dependencies=[Depends(validate_request)])


@router.post("/", response_model=ReadGroup, status_code=status.HTTP_200_OK)
async def create_group(group: CreateGroup, db: SessionDep, payload: ValidateRequest):
    current_user = get_current_user(payload=payload, db=db)
    
    with GroupService(session=db, current_user=current_user) as service:
        new_group = service.create(data=group)
    
    return new_group


@router.get("/", response_model=List[ReadGroup], status_code=status.HTTP_200_OK)
async def list_groups(db: SessionDep, payload: ValidateRequest):
    current_user = get_current_user(payload=payload, db=db)
    
    with GroupService(session=db, current_user=current_user) as service:
        all_groups = service.get_all_for_user()
    
    return all_groups


@router.get("/{group_id}", response_model=ReadGroupWithMembersRelation, status_code=status.HTTP_200_OK)
async def get_group(group_id: int, db: SessionDep):
    with GroupService(session=db) as service:
        group = service.get_by_id(_id=group_id)
    return group


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(group_id: int, db: SessionDep, payload: ValidateRequest):
    current_user = get_current_user(payload=payload, db=db)
    
    with GroupService(session=db, current_user=current_user) as service:
        service.delete_group(group_id=group_id)


@router.put("/", response_model=ReadGroup, status_code=status.HTTP_200_OK)
async def update_group(group: UpdateGroup, db: SessionDep, payload: ValidateRequest):
    current_user = get_current_user(payload=payload, db=db)
    
    with GroupService(session=db, current_user=current_user) as service:
        group = service.update_group(data=group)
    
    return group

