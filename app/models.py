

from typing import Optional
from sqlalchemy import Float, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True,)
    transaction_type: Mapped[str] = mapped_column(String(20), nullable = False,)
    amount: Mapped[float] = mapped_column(Float, nullable = False,)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable = True,)
    date: Mapped[Optional[str]] = mapped_column(String(20), nullable = True,)
    merchant: Mapped[Optional[str]] = mapped_column(String(255), nullable = True,)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable = True,)
    payment_method: Mapped[Optional[str]] = mapped_column(String(50), nullable = True,)

class UserContext(Base):
    __tablename__ = "user_context"
    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True,)
    profile: Mapped[dict] = mapped_column(JSONB, nullable = False, default = dict,)
    goals: Mapped[dict] = mapped_column(JSONB, nullable = False, default = dict,)
    study: Mapped[dict] = mapped_column(JSONB, nullable = False, default = dict,)
    time: Mapped[dict] = mapped_column(JSONB, nullable = False, default = dict,)
    current: Mapped[dict] = mapped_column(JSONB, nullable = False, default = dict,)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable = False, default = datetime.utcnow, onupdate = datetime.utcnow,)