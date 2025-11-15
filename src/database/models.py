from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from .base import Base
from typing import Any
from sqlalchemy.orm import relationship


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    category = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(255))

    # chiave esterna verso Account
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="SET NULL"))

    # relazione verso Account
    account = relationship("Account", back_populates="expenses")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "category": self.category,
            "amount": self.amount,
            "description": self.description,
        }


class MonthlyTarget(Base):
    __tablename__ = "monthly_targets"

    id = Column(Integer, primary_key=True)
    category = Column(String(100), unique=True, nullable=False)
    target_amount = Column(Float, nullable=False)
    created_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)

    # relazione inversa verso le spese
    expenses = relationship("Expense", back_populates="account")
    incomes = relationship("Income", back_populates="account")

class Income(Base):
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="SET NULL"))
    account = relationship("Account", back_populates="incomes")