
from __future__ import annotations

from sqlalchemy import String, DateTime, text, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base


class Notification(Base):
    __tablename__ = 'notifications'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    channel: Mapped[str] = mapped_column(String(16), nullable=False)  # EMAIL/SLACK
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(String(4000), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default='PENDING')  # PENDING/RETRY/SENT/FAILED
    meta_json: Mapped[dict] = mapped_column(JSON, nullable=False, server_default=text("'{}'::json"))
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default='0')
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, server_default='5')
    next_attempt_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))
    last_error: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))
