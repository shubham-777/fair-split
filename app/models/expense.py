from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.utils.constants import DEFAULT_CURRENCY


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    payer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(10), default=DEFAULT_CURRENCY)
    description = Column(Text, nullable=True)
    receipt_url = Column(String(500), nullable=True)
    paid_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_onupdate=func.now())


    # Relationships
    group = relationship("Group", back_populates="expenses")
    payer = relationship("User", back_populates="expenses_paid", foreign_keys=[payer_id])
    splits = relationship("ExpenseSplit", back_populates="expense", cascade="all, delete-orphan")
