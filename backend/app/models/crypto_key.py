"""
QShield Enterprise

Cryptographic Key Model
"""

from __future__ import annotations

import uuid

from sqlalchemy import (
    String,
    Boolean,
    Index,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.database.base import Base

from app.database.mixins import (
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
)


class CryptoKey(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Base,
):

    __tablename__ = "crypto_keys"


    __table_args__ = (
        Index(
            "idx_crypto_key_type",
            "key_type",
        ),
    )


    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )


    key_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


    algorithm: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


    key_reference: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )


    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )


    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        nullable=True,
    )


    def deactivate(self):

        self.active = False