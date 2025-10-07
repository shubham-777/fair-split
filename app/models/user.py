"""
User model
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    created_groups = relationship("Group", back_populates="creator", foreign_keys="Group.creator_id")
    group_memberships = relationship("GroupMember", back_populates="user")
    expenses_paid = relationship("Expense", back_populates="payer", foreign_keys="Expense.payer_id")
    expense_splits = relationship("ExpenseSplit", back_populates="user")
    settlements_from = relationship("Settlement", back_populates="payer", foreign_keys="Settlement.payer_id")
    settlements_to = relationship("Settlement", back_populates="payee", foreign_keys="Settlement.payee_id")
    notifications = relationship("Notification", back_populates="user")