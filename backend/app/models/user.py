"""
QShield Enterprise
==================

User Model

Represents an authenticated user within an organization.

Features
--------
- UUID primary key
- Multi-tenant
- Secure authentication
- MFA support
- Account lockout
- Email verification
- Password lifecycle tracking
- Soft delete
- SQLAlchemy 2.x typed ORM
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
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

from sqlalchemy.sql import func

from app.database.base import Base
from app.database.mixins import (
    DescriptionMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)
from app.database.types import GUID


class User(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    DescriptionMixin,
    Base,
):
    """
    Platform user.

    Every user belongs to exactly one organization.
    """

    __tablename__ = "users"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "email",
            name="uq_user_org_email",
        ),
        Index("idx_user_email", "email"),
        Index("idx_user_org", "organization_id"),
        Index("idx_user_active", "is_active"),
        Index("idx_user_verified", "is_verified"),
    )

    # ==========================================================
    # Organization
    # ==========================================================

    organization_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    # ==========================================================
    # Authentication
    # ==========================================================

    email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Argon2/Bcrypt password hash.",
    )

    # ==========================================================
    # Profile
    # ==========================================================

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    display_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    job_title: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    department: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    avatar_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # ==========================================================
    # Account Status
    # ==========================================================

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ==========================================================
    # Multi-Factor Authentication
    # ==========================================================

    mfa_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    mfa_secret: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="Encrypted TOTP secret.",
    )

    # ==========================================================
    # Login Security
    # ==========================================================

    failed_login_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_login_ip: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    password_changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ==========================================================
    # Relationships
    # ==========================================================

    organization = relationship(
        "Organization",
        back_populates="users",
    )

    user_roles = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    team_memberships = relationship(
        "TeamMember",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    assets = relationship(
        "Asset",
        back_populates="owner",
    )

    scheduled_scans = relationship(
        "ScheduledScan",
        back_populates="created_by_user",
    )
        # ==========================================================
    # Computed Properties
    # ==========================================================

    @property
    def full_name(self) -> str:
        """
        Returns the user's full name.
        """
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_locked(self) -> bool:
        """
        Returns True if the account is currently locked.
        """
        if self.locked_until is None:
            return False

        return self.locked_until > datetime.utcnow()

    @property
    def can_login(self) -> bool:
        """
        Indicates whether the account is allowed to authenticate.
        """
        return (
            self.is_active
            and self.is_verified
            and not self.is_locked
        )

    # ==========================================================
    # Security Helpers
    # ==========================================================

    def record_failed_login(
        self,
        max_attempts: int = 5,
        lock_minutes: int = 30,
    ) -> None:
        """
        Record a failed login attempt.

        Locks the account when the configured threshold
        has been reached.
        """

        from datetime import timedelta

        self.failed_login_attempts += 1

        if self.failed_login_attempts >= max_attempts:
            self.locked_until = (
                datetime.utcnow() +
                timedelta(minutes=lock_minutes)
            )

    def reset_login_attempts(self) -> None:
        """
        Clears failed login counters after a successful login.
        """

        self.failed_login_attempts = 0
        self.locked_until = None

    def mark_login_success(
        self,
        ip_address: str | None = None,
    ) -> None:
        """
        Update login metadata after successful authentication.
        """

        self.last_login_at = datetime.utcnow()
        self.last_login_ip = ip_address

        self.reset_login_attempts()

    # ==========================================================
    # Role Helpers
    # ==========================================================

    def roles(self) -> list:
        """
        Returns assigned Role objects.
        """

        return [
            ur.role
            for ur in self.user_roles
            if ur.role is not None
        ]

    def role_names(self) -> list[str]:
        """
        Returns sorted role names.
        """

        return sorted(
            role.name
            for role in self.roles()
        )

    def permissions(self) -> set[str]:
        """
        Returns the effective permission set for this user.

        Duplicate permissions are automatically removed.
        """

        permissions: set[str] = set()

        for role in self.roles():
            for rp in role.role_permissions:

                if (
                    rp.permission
                    and rp.permission.enabled
                ):
                    permissions.add(
                        rp.permission.name
                    )

        return permissions

    def has_permission(
        self,
        permission: str,
    ) -> bool:
        """
        Checks whether the user has the specified permission.

        Supports:

        *
        asset:*
        asset:create
        """

        perms = self.permissions()

        if "*" in perms:
            return True

        if permission in perms:
            return True

        resource = permission.split(":", 1)[0]

        if f"{resource}:*" in perms:
            return True

        return False

    # ==========================================================
    # Serialization
    # ==========================================================

    def to_dict(
        self,
        include_roles: bool = False,
        include_permissions: bool = False,
    ) -> dict:
        """
        Serialize the user.
        """

        data = {
            "id": str(self.id),
            "organization_id": str(self.organization_id),
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "display_name": self.display_name,
            "phone": self.phone,
            "job_title": self.job_title,
            "department": self.department,
            "avatar_url": self.avatar_url,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_superuser": self.is_superuser,
            "mfa_enabled": self.mfa_enabled,
            "failed_login_attempts": self.failed_login_attempts,
            "last_login_at": (
                self.last_login_at.isoformat()
                if self.last_login_at
                else None
            ),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

        if include_roles:
            data["roles"] = self.role_names()

        if include_permissions:
            data["permissions"] = sorted(
                self.permissions()
            )

        return data

    # ==========================================================
    # Representation
    # ==========================================================

    def __repr__(self) -> str:
        return (
            "<User("
            f"id={self.id}, "
            f"email='{self.email}', "
            f"organization_id={self.organization_id}, "
            f"active={self.is_active}"
            ")>"
        )