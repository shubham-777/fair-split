from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException
from typing import Sequence

from sqlalchemy import select
from starlette import status

from app.models import Expense, ExpenseSplit
from app.schemas.expense import CreateExpense, UpdateExpense
from app.schemas.expense_split import UpdateExpenseSplit
from app.services.base_service import BaseService
from app.services.group_service import GroupService
from app.utils.constants import COMMON_DATE_TIME_FORMAT


class ExpenseService(BaseService):
    
    def get_by_id(self, _id: int) -> type[Expense] | None:
        return self.session.get(Expense, _id)
    
    def get_all(self, group_id: int) ->  Sequence[Expense]:
       expenses = self.session.execute(select(Expense).where(Expense.group_id==group_id)).scalars().all()
       return expenses
    
    def validate_and_get_expense_split_by_user(self, expense_id: int, user_id: int) -> type[ExpenseSplit]:
        statement = select(ExpenseSplit).where(ExpenseSplit.user_id == user_id,
                                               ExpenseSplit.expense_id==expense_id)
        expense_split = self.session.execute(statement).scalars().first()
        if not expense_split:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense split not found")
        return expense_split
    
    def get_all_by_user(self, group_id: int) -> Sequence[Expense]:
        statement = select(Expense).where(Expense.group_id == group_id, Expense.payer_id == self.user.id)
        expenses = self.session.execute(statement).scalars().all()
        return expenses
    
    def delete_expense(self, expense_id: int) -> None:
        expense = self.get_by_id(_id=expense_id)
        if not expense:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        
        self.delete_and_commit(obj=expense)
    
    def add_expense(self, group_id: int, data: CreateExpense) -> Expense:
        group = GroupService(session=self.session, current_user=self.user).validate_and_get_by_id(_id=group_id)
        group_member_ids = [member.user_id for member in group.members]
        
        if data.payer_id == -1:
            data.payer_id = self.user.id
        
        for split in data.splits:
            if split.user_id not in group_member_ids:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"User with id {split.user_id} is not a member of group with id {group_id}")
        
        expense = Expense(**data.model_dump(exclude={'splits'}), group_id=group_id)
        expense = self.add_and_commit(obj=expense)
        
        for split in data.splits:
            expense_split = ExpenseSplit(expense_id=expense.id, user_id=split.user_id, share=split.share)
            self.add_and_commit(obj=expense_split)
        
        self.session.refresh(expense)
        return expense
    
    def delete_expense_split_by_user(self,expense_id: int, user_id: int) -> None:
        expense_split = self.validate_and_get_expense_split_by_user(expense_id=expense_id,
                                                                  user_id=user_id)
        self.delete_and_commit(obj=expense_split)
    
    def update_expense_split(self, expense_id: int, expense_split: UpdateExpenseSplit) -> ExpenseSplit:
        user_share = self.validate_and_get_expense_split_by_user(expense_id=expense_id,
                                                                 user_id=expense_split.user_id)
        
        for field, value in expense_split.model_dump(exclude_unset=True, exclude={'id'}).items():
            setattr(user_share, field, value)
        
        user_share = self.update_and_commit(obj=user_share)
        return user_share
    
    def update_expense(self, expense_id: int, data: UpdateExpense) -> Expense:
        expense = self.get_by_id(_id=expense_id)
        if not expense:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        
        users_in_splits = [split.user_id for split in expense.splits]
        new_splits_user_ids = [split.user_id for split in data.splits]
        splits_to_delete = set(users_in_splits) - set(new_splits_user_ids)
        
        # Delete removed splits
        for user_id in splits_to_delete:
            self.delete_expense_split_by_user(expense_id=expense_id, user_id=user_id)
        
        # Update expense fields
        for field, value in data.model_dump(exclude_unset=True, exclude={'splits'}).items():
            setattr(expense, field, value)
        
        #  Update or add splits
        for split in data.splits:
            if split.user_id in users_in_splits:
                self.update_expense_split(expense_id=expense_id, expense_split=split)
                continue
                
            expense_split = ExpenseSplit(expense_id=expense.id, user_id=split.user_id, share=split.share)
            self.add_and_commit(obj=expense_split)
        
        expense = self.update_and_commit(obj=expense)
        self.session.refresh(expense)
        return expense