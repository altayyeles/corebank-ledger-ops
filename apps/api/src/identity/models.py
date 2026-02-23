
from __future__ import annotations

from sqlalchemy import String, DateTime, text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default='ACTIVE')
    customer_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=text('now()'))

    roles: Mapped[list['Role']] = relationship('Role', secondary='user_roles', back_populates='users')


class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)

    users: Mapped[list[User]] = relationship('User', secondary='user_roles', back_populates='roles')


class UserRole(Base):
    __tablename__ = 'user_roles'

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    role_id: Mapped[str] = mapped_column(String(36), ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
