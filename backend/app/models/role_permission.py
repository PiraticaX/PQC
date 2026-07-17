"""
QShield Enterprise
==================

Role-Permission Association Model

Maps roles to permissions.

A role may contain many permissions.
A permission may belong to many roles.

Composite primary keys are intentionally used instead of
a surrogate UUID for maximum integrity and performance.
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey
from sqlalchemy import Index

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.database.types import GUID


class RolePermission(Base):
    """
    Many-to-many association between Role and Permission.
    """

    __tablename__ = "role_permissions"

    __table_args__ = (
        Index(
            "idx_role_permission_role",
            "role_id",
        ),
        Index(
            "idx_role_permission_permission",
            "permission_id",
        ),
    )

    # ------------------------------------------------------------------
    # Composite Primary Key
    # ------------------------------------------------------------------

    role_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey(
            "roles.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    permission_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey(
            "permissions.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    role = relationship(
        "Role",
        back_populates="role_permissions",
    )

    permission = relationship(
        "Permission",
        back_populates="role_permissions",
    )

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            "<RolePermission("
            f"role_id={self.role_id}, "
            f"permission_id={self.permission_id}"
            ")>"
        )