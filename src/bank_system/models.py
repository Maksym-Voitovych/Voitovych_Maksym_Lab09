from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

class Base(DeclarativeBase):
    pass

class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    accounts: Mapped[list["Account"]] = relationship(
        back_populates="client",
        cascade="all, delete-orphan",
    )

class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        CheckConstraint("balance >= 0", name="check_positive_balance"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    balance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    account_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)

    client: Mapped["Client"] = relationship(back_populates="accounts")
    transactions_sent: Mapped[list["Transaction"]] = relationship(
        foreign_keys="[Transaction.sender_account_id]",
        back_populates="sender_account",
    )
    transactions_received: Mapped[list["Transaction"]] = relationship(
        foreign_keys="[Transaction.receiver_account_id]",
        back_populates="receiver_account",
    )

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sender_account_id: Mapped[Optional[int]] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    receiver_account_id: Mapped[Optional[int]] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    sender_account: Mapped[Optional["Account"]] = relationship(
        foreign_keys=[sender_account_id],
        back_populates="transactions_sent",
    )
    receiver_account: Mapped[Optional["Account"]] = relationship(
        foreign_keys=[receiver_account_id],
        back_populates="transactions_received",
    )