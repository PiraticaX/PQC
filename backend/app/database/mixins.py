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
- Audit helpers
- Lifecycle helpers

Compatible with SQLAlchemy 2.0.
"""

from __future__ import annotations


import uuid

from datetime import UTC
from datetime import datetime


from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import Text


from sqlalchemy.orm import (
    Mapped,
    declared_attr,
    mapped_column,
    declarative_mixin,
)


from app.database.types import GUID



# ============================================================
# UUID
# ============================================================


@declarative_mixin
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


@declarative_mixin
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


@declarative_mixin
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

        return self.deleted_at is not None



    @property
    def is_active(self) -> bool:

        return self.deleted_at is None



    def soft_delete(self) -> None:

        self.deleted_at = datetime.now(UTC)



    def restore(self) -> None:

        self.deleted_at = None



    def mark_deleted(self) -> None:

        self.soft_delete()



# ============================================================
# Description
# ============================================================


@declarative_mixin
class DescriptionMixin:
    """
    Optional description field.
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


@declarative_mixin
class NameMixin:
    """
    Generic name field.
    """


    @declared_attr
    def name(cls) -> Mapped[str]:

        return mapped_column(
            String(255),
            nullable=False,
        )



# ============================================================
# Created By
# ============================================================


@declarative_mixin
class CreatedByMixin:
    """
    Creator tracking.
    """


    @declared_attr
    def created_by(cls) -> Mapped[uuid.UUID | None]:

        return mapped_column(
            GUID(),
            nullable=True,
        )



# ============================================================
# Updated By
# ============================================================


@declarative_mixin
class UpdatedByMixin:
    """
    Modifier tracking.
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


@declarative_mixin
class EnableDisableMixin:
    """
    Enabled state helper.
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


@declarative_mixin
class AuditMixin:
    """
    Marker mixin.

    Intentionally does not inherit UUIDMixin
    or TimestampMixin.

    Models should explicitly declare:

    UUIDMixin,
    TimestampMixin,
    AuditMixin

    if required.
    """

    pass



# ============================================================
# Lifecycle Helpers
# ============================================================


@declarative_mixin
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


@declarative_mixin
class EntityMixin(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    DescriptionMixin,
):
    """
    Common entity mixin.
    """

    pass



# ============================================================
# End of File
# =========================================================