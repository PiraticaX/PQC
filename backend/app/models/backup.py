"""
Backup Model
"""

from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.database.mixins import (
    UUIDMixin,
    TimestampMixin,
)


class Backup(
    UUIDMixin,
    TimestampMixin,
    Base,
):

    __tablename__ = "backups"


    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )


    location: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )


    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
    )


    metadata_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )