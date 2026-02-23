
from __future__ import annotations

from sqlalchemy import String, DateTime, text, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base


class Transfer(Base):
    __tablename__ = 'transfers'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    from_account_id: Mapped[str] = mapped_column(String(36), ForeignKey('accounts.id'))
    to_account_id: Mapped[str] = mapped_column(String(36), ForeignKey('accounts.id'))
    amount: Mapped[Numeric] = mapped_column(Numeric(18,2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default='INITIATED')
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True)
    reference: Mapped[str | None] = mapped_column(String(140), nullable=True)
    transfer_type: Mapped[str] = mapped_column(String(16), nullable=False, server_default='INTERNAL')
    hold_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))
