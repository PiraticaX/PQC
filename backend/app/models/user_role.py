"""
QShield Enterprise
==================

User Role Association

Associates users with roles.

A user may have multiple roles.
A role may be assigned to multiple users.

This table intentionally uses a composite primary key instead of
a surrogate UUID.
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.database.types import GUID


class UserRole(Base):
    """
    Many-to-many association between User and Role.
    """

    __tablename__ = "user_roles"

    __table_args__ = (
        Index(
            "idx_user_role_user",
            "user_id",
        ),
        Index(
            "idx_user_role_role",
            "role_id",
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
        nullable=False,
    )

    role_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey(
            "roles.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="user_roles",
    )

    role = relationship(
        "Role",
        back_populates="user_roles",
    )

    def to_dict(self) -> dict:
        return {
            "user_id": str(self.user_id),
            "role_id": str(self.role_id),
        }

    def __repr__(self) -> str:
        return (
            "<UserRole("
            f"user_id={self.user_id}, "
            f"role_id={self.role_id}"
            ")>"
        )