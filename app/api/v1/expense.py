"""
Authentication API routes
"""
from typing import List

from fastapi import APIRouter
from fastapi.params import Depends
from starlette import status

from app.dependencies import SessionDep
from app.schemas.expense import CreateExpense, ReadExpense, UpdateExpense
from app.services.expense_service import ExpenseService
from app.utils.security import CurrentUser, validate_request

router = APIRouter(prefix="/groups/{group_id}/expenses", tags=["Expenses"],
                   dependencies=[Depends(validate_request)])


@router.get("/", response_model=List[ReadExpense], status_code=status.HTTP_200_OK)
def list_expense(group_id: int, db: SessionDep, current_user: CurrentUser):

    with ExpenseService(session=db, current_user=current_user) as service:
        expenses = service.get_all(group_id)
    return expenses


@router.get("/{expense_id}", response_model=ReadExpense, status_code=status.HTTP_200_OK)
def get_expense(group_id: int, expense_id: int, db: SessionDep, current_user: CurrentUser):

    with ExpenseService(session=db, current_user=current_user) as service:
        expenses = service.get_by_id(_id=expense_id)
    return expenses


@router.post("/", response_model=ReadExpense, status_code=status.HTTP_201_CREATED)
def add_expense(group_id: int, expense_data: CreateExpense, db: SessionDep,
               current_user: CurrentUser):
    
    with ExpenseService(session=db, current_user=current_user) as service:
        expense = service.add_expense(group_id=group_id, data=expense_data)
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(group_id: int, expense_id: int, expense_data: UpdateExpense, db: SessionDep,
                   current_user: CurrentUser):
    
    with ExpenseService(session=db, current_user=current_user) as service:
        service.delete_expense(expense_id=expense_id)


@router.put("/{expense_id}", response_model=ReadExpense, status_code=status.HTTP_200_OK)
def update_expense(group_id: int, expense_id: int, expense_data: UpdateExpense, db: SessionDep, current_user: CurrentUser):
    
    with ExpenseService(session=db, current_user=current_user) as service:
        expense = service.update_expense(expense_id=expense_id, data=expense_data)
    return expense


@router.delete("/{expense_id}/splits/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user_from_split(group_id: int, expense_id: int, user_id: int, db: SessionDep,
                   current_user: CurrentUser):
    
    with ExpenseService(session=db, current_user=current_user) as service:
        service.delete_expense_split_by_user(expense_id=expense_id, user_id=user_id)