"""
API Key Model
"""

from __future__ import annotations

import uuid

from sqlalchemy import String, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.database.mixins import (
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
)


class APIKey(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Base,
):

    __tablename__ = "api_keys"


    __table_args__ = (
        Index(
            "idx_api_key_hash",
            "key_hash",
        ),
    )


    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )


    key_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )


    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )


    user_id: Mapped[uuid.UUID | None] = mapped_column(
        nullable=True,
    )