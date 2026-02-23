
from __future__ import annotations

from sqlalchemy import String, DateTime, text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base


class Case(Base):
    __tablename__ = 'cases'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    alert_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('alerts.id'), nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default='OPEN')
    priority: Mapped[str] = mapped_column(String(16), nullable=False, server_default='MEDIUM')
    assignee_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('users.id'), nullable=True)
    assigned_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sla_due_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sla_breached: Mapped[str] = mapped_column(String(8), nullable=False, server_default='NO')
    breached_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    tags_json: Mapped[dict] = mapped_column(JSON, nullable=False, server_default=text("'{}'::json"))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))


class CaseNote(Base):
    __tablename__ = 'case_notes'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey('cases.id', ondelete='CASCADE'))
    author_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('users.id'), nullable=True)
    note: Mapped[str] = mapped_column(String(2000), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))


class SarReport(Base):
    __tablename__ = 'sar_reports'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey('cases.id', ondelete='CASCADE'))
    content_json: Mapped[dict] = mapped_column(JSON, nullable=False, server_default=text("'{}'::json"))
    exported_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))
