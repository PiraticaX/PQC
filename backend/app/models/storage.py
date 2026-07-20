"""
QShield Enterprise
==================

Storage Object Model
"""

from __future__ import annotations

import uuid

from sqlalchemy import String, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.database.mixins import (
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
)


class StorageObject(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Base,
):
    """
    Storage metadata registry.
    """

    __tablename__ = "storage_objects"

    __table_args__ = (
        Index(
            "idx_storage_owner",
            "owner_id",
        ),
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    storage_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    storage_type: Mapped[str] = mapped_column(
        String(50),
        default="local",
        nullable=False,
    )

    mime_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    size_bytes: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )

    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        nullable=True,
    )

    checksum: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )


    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "filename": self.filename,
            "storage_path": self.storage_path,
            "storage_type": self.storage_type,
            "mime_type": self.mime_type,
            "size_bytes": self.size_bytes,
        }