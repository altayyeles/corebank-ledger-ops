
from __future__ import annotations

from sqlalchemy import String, DateTime, text, ForeignKey, Numeric, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base


class FraudRule(Base):
    __tablename__ = 'fraud_rules'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rule_type: Mapped[str] = mapped_column(String(64), nullable=False)
    enabled: Mapped[str] = mapped_column(String(8), nullable=False, server_default='YES')
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default='1')
    severity: Mapped[str] = mapped_column(String(16), nullable=False, server_default='MEDIUM')
    weight: Mapped[Numeric] = mapped_column(Numeric(6,2), nullable=False, server_default='10')
    params_json: Mapped[dict] = mapped_column(JSON, nullable=False, server_default=text("'{}'::json"))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))


class Alert(Base):
    __tablename__ = 'alerts'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False)
    customer_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('customers.id'), nullable=True)
    account_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('accounts.id'), nullable=True)
    transfer_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('transfers.id'), nullable=True)
    score: Mapped[Numeric] = mapped_column(Numeric(8,2), nullable=False, server_default='0')
    severity: Mapped[str] = mapped_column(String(16), nullable=False, server_default='MEDIUM')
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default='NEW')
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    explain_json: Mapped[dict] = mapped_column(JSON, nullable=False, server_default=text("'{}'::json"))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))


class AlertHistory(Base):
    __tablename__ = 'alert_history'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    alert_id: Mapped[str] = mapped_column(String(36), ForeignKey('alerts.id', ondelete='CASCADE'))
    from_status: Mapped[str] = mapped_column(String(16), nullable=False)
    to_status: Mapped[str] = mapped_column(String(16), nullable=False)
    changed_by_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('users.id'), nullable=True)
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))
