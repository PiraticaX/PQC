"""
QShield Enterprise
==================

Permission Model

A Permission represents a single atomic capability within the platform.

Permissions are stored as normalized string identifiers rather than
resource/action enums.

Examples
--------
asset:create
asset:read
asset:update
asset:delete

scan:create
scan:run
scan:cancel

finding:update

report:export

Advantages
----------
- No schema changes when introducing new resources.
- Compatible with enterprise RBAC systems.
- Easy wildcard matching.
- Future-proof.
"""

from __future__ import annotations

from sqlalchemy import Boolean, Index, String

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base import Base
from app.database.mixins import (
    DescriptionMixin,
    TimestampMixin,
    UUIDMixin,
)


class Permission(
    UUIDMixin,
    TimestampMixin,
    DescriptionMixin,
    Base,
):
    """
    Atomic permission.

    A permission represents exactly one capability inside QShield.
    """

    __tablename__ = "permissions"

    __table_args__ = (
        Index("idx_permission_name", "name"),
        Index("idx_permission_enabled", "enabled"),
    )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    name: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        doc="Canonical permission identifier (e.g. asset:create).",
    )

    display_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Human readable permission name.",
    )

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        doc="Logical grouping (Asset, Scan, Report, etc.).",
    )

    system_permission: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="True if shipped with QShield.",
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    role_permissions = relationship(
        "RolePermission",
        back_populates="permission",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def resource(self) -> str:
        """
        Returns the resource portion.

        Example:
            asset:create -> asset
        """
        return self.name.split(":", 1)[0]

    @property
    def action(self) -> str:
        """
        Returns the action portion.

        Example:
            asset:create -> create
        """
        parts = self.name.split(":", 1)
        return parts[1] if len(parts) == 2 else ""

    def __repr__(self) -> str:
        return (
            f"<Permission("
            f"name='{self.name}', "
            f"enabled={self.enabled}"
            f")>"
        )

    def to_dict(self) -> dict:
        """
        Serialize permission.
        """

        return {
            "id": str(self.id),
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "category": self.category,
            "resource": self.resource,
            "action": self.action,
            "system_permission": self.system_permission,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }