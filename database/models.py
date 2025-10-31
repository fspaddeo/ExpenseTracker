from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from database.base import Base
from typing import Any


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    category = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(255))

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
