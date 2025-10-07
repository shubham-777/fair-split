"""
Balance calculation and settlement API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.models.group import GroupMember
from app.models.settlement import Settlement
from app.services.balance_service import BalanceService
from app.services.debt_simplifier import DebtSimplifier
from app.dependencies import get_current_user


router = APIRouter(tags=["Balances & Settlements"])


# Schemas
class SettlementCreate(BaseModel):
    group_id: int
    payee_id: int
    amount: Decimal
    notes: str | None = None
    payment_method: str | None = None


class SettlementResponse(BaseModel):
    id: int
    group_id: int
    payer_id: int
    payee_id: int
    amount: Decimal
    currency: str
    notes: str | None
    payment_method: str | None
    date: datetime
    
    class Config:
        from_attributes = True


@router.get("/groups/{group_id}/balances")
async def get_group_balances(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all balances in the group
    """
    # Verify membership
    membership = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )
    
    # Calculate balances
    balances = BalanceService.calculate_group_balances(db, group_id)
    
    # Format response
    balance_list = []
    for user_id, debts in balances.items():
        for other_id, amount in debts.items():
            if amount > 0:
                balance_list.append({
                    "from_user_id": user_id,
                    "to_user_id": other_id,
                    "amount": float(amount)
                })
    
    return {
        "group_id": group_id,
        "balances": balance_list
    }


@router.get("/groups/{group_id}/balances/simplified")
async def get_simplified_balances(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get simplified settlement plan for the group
    """
    # Verify membership
    membership = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )
    
    # Calculate and simplify balances
    balances = BalanceService.calculate_group_balances(db, group_id)
    settlement_plan = DebtSimplifier.calculate_settlement_plan(balances)
    
    return {
        "group_id": group_id,
        "settlement_plan": settlement_plan
    }


@router.get("/users/me/balances")
async def get_user_balances(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's balance summary across all groups
    """
    # Get all groups user is member of
    memberships = db.query(GroupMember).filter(
        GroupMember.user_id == current_user.id
    ).all()
    
    user_balances = []
    total_owed = Decimal('0')
    total_owing = Decimal('0')
    
    for membership in memberships:
        group_id = membership.group_id
        summary = BalanceService.get_user_summary(db, current_user.id, group_id)
        
        user_balances.append({
            "group_id": group_id,
            "group_name": membership.group.name,
            **summary
        })
        
        total_owed += Decimal(str(summary["total_owed"]))
        total_owing += Decimal(str(summary["total_owing"]))
    
    return {
        "user_id": current_user.id,
        "total_owed": float(total_owed),
        "total_owing": float(total_owing),
        "net_balance": float(total_owing - total_owed),
        "group_balances": user_balances
    }


@router.post("/settlements", response_model=SettlementResponse, status_code=status.HTTP_201_CREATED)
async def record_settlement(
    settlement_data: SettlementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record a settlement/payment
    """
    # Verify membership
    membership = db.query(GroupMember).filter(
        GroupMember.group_id == settlement_data.group_id,
        GroupMember.user_id == current_user.id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this group"
        )
    
    # Validate payer is current user
    if current_user.id == settlement_data.payee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot settle with yourself"
        )
    
    # Create settlement
    new_settlement = Settlement(
        group_id=settlement_data.group_id,
        payer_id=current_user.id,
        payee_id=settlement_data.payee_id,
        amount=settlement_data.amount,
        notes=settlement_data.notes,
        payment_method=settlement_data.payment_method
    )
    
    db.add(new_settlement)
    db.commit()
    db.refresh(new_settlement)
    
    return new_settlement


@router.get("/settlements", response_model=list[SettlementResponse])
async def list_settlements(
    group_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """
    List settlements (optionally filtered by group)
    """
    query = db.query(Settlement).filter(
        (Settlement.payer_id == current_user.id) | (Settlement.payee_id == current_user.id)
    )
    
    if group_id:
        # Verify membership if group specified
        membership = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == current_user.id
        ).first()
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a member of this group"
            )
        
        query = query.filter(Settlement.group_id == group_id)
    
    settlements = query.order_by(Settlement.date.desc()).offset(skip).limit(limit).all()
    
    return settlements