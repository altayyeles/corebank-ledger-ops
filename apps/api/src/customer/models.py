
from __future__ import annotations

from sqlalchemy import String, DateTime, text, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base


class Customer(Base):
    __tablename__ = 'customers'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False, server_default='0')
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default='ACTIVE')
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))

    kyc: Mapped['KycProfile'] = relationship('KycProfile', uselist=False, back_populates='customer')


class KycProfile(Base):
    __tablename__ = 'kyc_profiles'

    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey('customers.id', ondelete='CASCADE'), primary_key=True)
    level: Mapped[str] = mapped_column(String(32), nullable=False, server_default='BASIC')
    flags_json: Mapped[dict] = mapped_column(JSON, nullable=False, server_default=text("'{}'::json"))

    customer: Mapped[Customer] = relationship('Customer', back_populates='kyc')
