
from __future__ import annotations

from sqlalchemy import String, DateTime, text, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base


class CoaAccount(Base):
    __tablename__ = 'coa_accounts'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(32))


class JournalEntry(Base):
    __tablename__ = 'journal_entries'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    entry_no: Mapped[str] = mapped_column(String(32), unique=True)
    business_tx_id: Mapped[str] = mapped_column(String(36), index=True)
    description: Mapped[str] = mapped_column(String(255))
    currency: Mapped[str] = mapped_column(String(3))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))


class JournalLine(Base):
    __tablename__ = 'journal_lines'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    entry_id: Mapped[str] = mapped_column(String(36), ForeignKey('journal_entries.id', ondelete='CASCADE'))
    coa_account_id: Mapped[str] = mapped_column(String(36), ForeignKey('coa_accounts.id'))
    debit: Mapped[Numeric] = mapped_column(Numeric(18,2), nullable=False, server_default='0')
    credit: Mapped[Numeric] = mapped_column(Numeric(18,2), nullable=False, server_default='0')
    account_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('accounts.id'), nullable=True)
