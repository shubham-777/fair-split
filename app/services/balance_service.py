"""
Balance calculation service
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Dict, List
from decimal import Decimal
from app.models.expense import Expense, ExpenseSplit
from app.models.settlement import Settlement


class BalanceService:
    """
    Service for calculating balances within a group
    """
    
    @staticmethod
    def calculate_group_balances(db: Session, group_id: int) -> Dict[int, Dict[int, Decimal]]:
        """
        Calculate all balances in a group
        Returns: {user_id: {other_user_id: amount_owed}}
        Positive amount = user owes other_user
        Negative amount = other_user owes user
        """
        balances: Dict[int, Dict[int, Decimal]] = {}
        
        # Get all expenses in the group
        expenses = db.query(Expense).filter(Expense.group_id == group_id).all()
        
        for expense in expenses:
            payer_id = expense.payer_id
            
            # Initialize payer in balances if not exists
            if payer_id not in balances:
                balances[payer_id] = {}
            
            # Process each split
            for split in expense.splits:
                debtor_id = split.user_id
                amount = split.amount
                
                # Skip if payer is splitting with themselves
                if payer_id == debtor_id:
                    continue
                
                # Initialize debtor in balances if not exists
                if debtor_id not in balances:
                    balances[debtor_id] = {}
                
                # Debtor owes payer
                if payer_id not in balances[debtor_id]:
                    balances[debtor_id][payer_id] = Decimal('0')
                balances[debtor_id][payer_id] += amount
        
        # Apply settlements
        settlements = db.query(Settlement).filter(Settlement.group_id == group_id).all()
        
        for settlement in settlements:
            payer_id = settlement.payer_id
            payee_id = settlement.payee_id
            amount = settlement.amount
            
            # Initialize if not exists
            if payer_id not in balances:
                balances[payer_id] = {}
            if payee_id not in balances[payer_id]:
                balances[payer_id][payee_id] = Decimal('0')
            
            # Reduce debt: payer settled with payee
            balances[payer_id][payee_id] -= amount
        
        # Clean up zero balances and simplify bidirectional debts
        simplified = {}
        for user_id, debts in balances.items():
            simplified[user_id] = {}
            for other_id, amount in debts.items():
                if amount != 0:
                    simplified[user_id][other_id] = amount
        
        return simplified
    
    @staticmethod
    def get_user_summary(db: Session, user_id: int, group_id: int) -> Dict:
        """
        Get balance summary for a specific user in a group
        """
        balances = BalanceService.calculate_group_balances(db, group_id)
        
        total_owed = Decimal('0')  # What user owes to others
        total_owing = Decimal('0')  # What others owe to user
        
        # Check what user owes
        if user_id in balances:
            for other_id, amount in balances[user_id].items():
                if amount > 0:
                    total_owed += amount
        
        # Check what others owe to user
        for other_id, debts in balances.items():
            if user_id in debts and debts[user_id] > 0:
                total_owing += debts[user_id]
        
        return {
            "user_id": user_id,
            "total_owed": float(total_owed),
            "total_owing": float(total_owing),
            "net_balance": float(total_owing - total_owed)
        }