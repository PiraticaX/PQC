"""
QShield Enterprise
==================

Role Model

Defines security roles used by the RBAC system.

A Role is a reusable collection of permissions that can be assigned to
one or more users.

Features
--------
- Multi-tenant
- System roles
- Organization-specific custom roles
- Soft delete
- UUID primary keys
- SQLAlchemy 2.x typed ORM
"""

from __future__ import annotations

import uuid

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base import Base
from app.database.mixins import (
    DescriptionMixin,
    NameMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)
from app.database.types import GUID


class Role(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    DescriptionMixin,
    NameMixin,
    Base,
):
    """
    Security role.

    A role contains a collection of permissions.

    Roles may either be:

    - System Roles (shared globally)
    - Organization Roles (tenant specific)

    Users receive effective permissions through one or more assigned
    roles.
    """

    __tablename__ = "roles"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "name",
            name="uq_role_org_name",
        ),
        Index(
            "idx_role_name",
            "name",
        ),
        Index(
            "idx_role_org",
            "organization_id",
        ),
        Index(
            "idx_role_enabled",
            "enabled",
        ),
    )

    # ===============================================================
    # Ownership
    # ===============================================================

    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        doc="NULL indicates a global system role.",
    )

    # ===============================================================
    # Display
    # ===============================================================

    display_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        doc="Machine-friendly unique identifier.",
    )

    # ===============================================================
    # Configuration
    # ===============================================================

    system_role: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    editable: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        default=100,
        nullable=False,
        doc="Lower number means higher precedence.",
    )

    # ===============================================================
    # Relationships
    # ===============================================================

    organization = relationship(
        "Organization",
        back_populates="roles",
    )

    role_permissions = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    user_roles = relationship(
        "UserRole",
        back_populates="role",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
        # ===============================================================
    # Helper Properties
    # ===============================================================

    @property
    def is_system_role(self) -> bool:
        """
        Returns True if this role is a built-in system role.
        """
        return self.system_role

    @property
    def is_custom_role(self) -> bool:
        """
        Returns True if this role belongs to an organization.
        """
        return not self.system_role

    @property
    def permission_count(self) -> int:
        """
        Number of permissions assigned to this role.
        """
        return len(self.role_permissions)

    @property
    def user_count(self) -> int:
        """
        Number of users assigned to this role.
        """
        return len(self.user_roles)

    # ===============================================================
    # Permission Helpers
    # ===============================================================

    def has_permission(self, permission_name: str) -> bool:
        """
        Check whether this role grants a permission.

        Supports wildcard permissions.

        Examples
        --------
        asset:create
        asset:*
        system:*
        *
        """

        for rp in self.role_permissions:
            permission = rp.permission

            if permission is None or not permission.enabled:
                continue

            name = permission.name

            if name == "*":
                return True

            if name == permission_name:
                return True

            if name.endswith(":*"):
                resource = name.split(":", 1)[0]

                if permission_name.startswith(f"{resource}:"):
                    return True

        return False

    def add_permission(self, permission) -> None:
        """
        Attach a Permission to this role.

        Duplicate permissions are ignored.
        """

        for rp in self.role_permissions:
            if rp.permission_id == permission.id:
                return

        from app.models.role_permission import RolePermission

        self.role_permissions.append(
            RolePermission(
                role=self,
                permission=permission,
            )
        )

    def remove_permission(self, permission_id: uuid.UUID) -> None:
        """
        Remove a permission from this role.
        """

        self.role_permissions = [
            rp
            for rp in self.role_permissions
            if rp.permission_id != permission_id
        ]

    def list_permissions(self) -> list[str]:
        """
        Returns sorted permission names.
        """

        permissions = [
            rp.permission.name
            for rp in self.role_permissions
            if rp.permission is not None
        ]

        permissions.sort()

        return permissions

    # ===============================================================
    # Serialization
    # ===============================================================

    def to_dict(
        self,
        include_permissions: bool = False,
    ) -> dict:
        """
        Serialize this role.

        Parameters
        ----------
        include_permissions:
            Include permission names.
        """

        data = {
            "id": str(self.id),
            "organization_id": (
                str(self.organization_id)
                if self.organization_id
                else None
            ),
            "name": self.name,
            "slug": self.slug,
            "display_name": self.display_name,
            "description": self.description,
            "system_role": self.system_role,
            "editable": self.editable,
            "enabled": self.enabled,
            "priority": self.priority,
            "permission_count": self.permission_count,
            "user_count": self.user_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "deleted_at": (
                self.deleted_at.isoformat()
                if self.deleted_at
                else None
            ),
        }

        if include_permissions:
            data["permissions"] = self.list_permissions()

        return data

    # ===============================================================
    # Representation
    # ===============================================================

    def __repr__(self) -> str:
        return (
            "<Role("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"organization_id={self.organization_id}, "
            f"system_role={self.system_role}, "
            f"enabled={self.enabled}"
            ")>"
        )