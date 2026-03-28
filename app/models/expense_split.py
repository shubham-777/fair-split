from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ExpenseSplit(Base):
    __tablename__ = "expense_splits"

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    share = Column(Numeric(12, 2), nullable=False)  # amount owed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_onupdate=func.now())

    # Relationships
    expense = relationship("Expense", back_populates="splits")
    user = relationship("User", back_populates="expense_splits")
    
    __table_args__ = (UniqueConstraint('expense_id', 'user_id', name='uix_user_split'),)
