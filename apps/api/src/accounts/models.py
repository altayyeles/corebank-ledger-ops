
from __future__ import annotations

from sqlalchemy import String, DateTime, text, ForeignKey, Numeric, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(128))
    type: Mapped[str] = mapped_column(String(16), nullable=False, server_default='DDA')
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default='TRY')
    rules_json: Mapped[dict] = mapped_column(JSON, nullable=False, server_default=text("'{}'::json"))


class Account(Base):
    __tablename__ = 'accounts'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey('customers.id'))
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey('products.id'))
    iban: Mapped[str] = mapped_column(String(34), unique=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default='ACTIVE')
    opened_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))

    balance: Mapped['AccountBalance'] = relationship('AccountBalance', uselist=False, back_populates='account')


class AccountBalance(Base):
    __tablename__ = 'account_balances'

    account_id: Mapped[str] = mapped_column(String(36), ForeignKey('accounts.id', ondelete='CASCADE'), primary_key=True)
    ledger_balance: Mapped[Numeric] = mapped_column(Numeric(18,2), nullable=False, server_default='0')
    available_balance: Mapped[Numeric] = mapped_column(Numeric(18,2), nullable=False, server_default='0')
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))

    account: Mapped[Account] = relationship('Account', back_populates='balance')


class Hold(Base):
    __tablename__ = 'holds'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    account_id: Mapped[str] = mapped_column(String(36), ForeignKey('accounts.id', ondelete='CASCADE'))
    amount: Mapped[Numeric] = mapped_column(Numeric(18,2), nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default='ACTIVE')
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))


class Limit(Base):
    __tablename__ = 'limits'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    account_id: Mapped[str] = mapped_column(String(36), ForeignKey('accounts.id', ondelete='CASCADE'), unique=True)
    daily_out_limit: Mapped[Numeric] = mapped_column(Numeric(18,2), nullable=False, server_default='0')
    per_tx_limit: Mapped[Numeric] = mapped_column(Numeric(18,2), nullable=False, server_default='0')
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))
