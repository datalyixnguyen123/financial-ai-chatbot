

from typing import Optional
from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    transaction_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    category: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    date: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )

    merchant: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    description: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    payment_method: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )