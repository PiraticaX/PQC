"""
QShield Enterprise
==================

Database Mixins

Reusable SQLAlchemy mixins shared across ORM models.

Provides:

- UUID primary key
- Created/Updated timestamps
- Soft delete support
- Description field

Compatible with SQLAlchemy 2.0.
"""

from __future__ import annotations

import uuid
from datetime import UTC
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import mapped_column

from app.database.types import GUID


# ============================================================
# UUID
# ============================================================


class UUIDMixin:
    """
    UUID primary key.

    Every model inherits a UUID id column.
    """

    @declared_attr
    def id(cls) -> Mapped[uuid.UUID]:
        return mapped_column(
            GUID(),
            primary_key=True,
            default=uuid.uuid4,
            nullable=False,
        )


# ============================================================
# Timestamp
# ============================================================


class TimestampMixin:
    """
    Automatic timestamps.
    """

    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            default=lambda: datetime.now(UTC),
            nullable=False,
        )

    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            default=lambda: datetime.now(UTC),
            onupdate=lambda: datetime.now(UTC),
            nullable=False,
        )


# ============================================================
# Soft Delete
# ============================================================


class SoftDeleteMixin:
    """
    Soft deletion support.
    """

    @declared_attr
    def deleted_at(cls) -> Mapped[datetime | None]:
        return mapped_column(
            DateTime(timezone=True),
            nullable=True,
            default=None,
        )

    @property
    def is_deleted(self) -> bool:
        """
        Returns True if the row has been soft deleted.
        """
        return self.deleted_at is not None

    @property
    def is_active(self) -> bool:
        """
        Returns True if the row is active.
        """
        return self.deleted_at is None

    def soft_delete(self) -> None:
        """
        Mark the row as deleted.
        """
        self.deleted_at = datetime.now(UTC)

    def restore(self) -> None:
        """
        Restore a previously deleted row.
        """
        self.deleted_at = None

    def mark_deleted(self) -> None:
        """
        Alias for soft_delete().
        """
        self.soft_delete()
        # ============================================================
# Description
# ============================================================


class DescriptionMixin:
    """
    Optional description field shared by many entities.
    """

    @declared_attr
    def description(cls) -> Mapped[str | None]:
        return mapped_column(
            Text,
            nullable=True,
        )


# ============================================================
# Name
# ============================================================


class NameMixin:
    """
    Generic human-readable name.
    """

    @declared_attr
    def name(cls) -> Mapped[str]:
        return mapped_column(
            String(255),
            nullable=False,
        )


# ============================================================
# Created / Updated By
# ============================================================


class CreatedByMixin:
    """
    Optional creator tracking.
    """

    @declared_attr
    def created_by(cls) -> Mapped[uuid.UUID | None]:
        return mapped_column(
            GUID(),
            nullable=True,
        )


class UpdatedByMixin:
    """
    Optional last-modifier tracking.
    """

    @declared_attr
    def updated_by(cls) -> Mapped[uuid.UUID | None]:
        return mapped_column(
            GUID(),
            nullable=True,
        )


# ============================================================
# Enable / Disable
# ============================================================


class EnableDisableMixin:
    """
    Generic enabled/disabled state.
    """

    @declared_attr
    def enabled(cls) -> Mapped[bool]:
        return mapped_column(
            default=True,
            nullable=False,
        )

    def enable(self) -> None:
        self.enabled = True

    def disable(self) -> None:
        self.enabled = False


# ============================================================
# Audit
# ============================================================


class AuditMixin(
    UUIDMixin,
    TimestampMixin,
):
    """
    Convenience mixin combining the most common
    auditing columns.
    """

    pass


# ============================================================
# Lifecycle Helpers
# ============================================================


class LifecycleMixin(
    TimestampMixin,
    SoftDeleteMixin,
):
    """
    Timestamp + soft-delete convenience mixin.
    """

    pass


# ============================================================
# Full Entity Mixin
# ============================================================


class EntityMixin(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    DescriptionMixin,
):
    """
    Common base used by most QShield entities.
    """

    pass


# ============================================================
# End of File
# ============================================================