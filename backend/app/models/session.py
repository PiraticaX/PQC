"""
QShield Enterprise
==================

User Session Model

Tracks authenticated user sessions.

Responsibilities:

- JWT/session tracking
- Device tracking
- Token lifecycle
- Session revocation
"""

from __future__ import annotations

import uuid

from datetime import datetime

from sqlalchemy import (
    String,
    Boolean,
    DateTime,
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


class Session(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Base,
):

    """
    Authentication session registry.
    """

    __tablename__ = "sessions"


    __table_args__ = (

        Index(
            "idx_session_user",
            "user_id",
        ),

        Index(
            "idx_session_token",
            "token_hash",
        ),

    )


    # ========================================================
    # Ownership
    # ========================================================


    user_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False,
    )


    # ========================================================
    # Authentication
    # ========================================================


    token_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )


    refresh_token_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )


    # ========================================================
    # Device Information
    # ========================================================


    ip_address: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )


    user_agent: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )


    device_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )


    # ========================================================
    # Lifecycle
    # ========================================================


    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


    revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )


    # ========================================================
    # Helpers
    # ========================================================


    def revoke(self):

        self.revoked = True



    def is_valid(self) -> bool:

        return (
            not self.revoked
            and
            self.expires_at > datetime.utcnow()
        )



    def to_dict(self):

        return {

            "id": str(self.id),

            "user_id": str(self.user_id),

            "revoked": self.revoked,

            "expires_at": self.expires_at.isoformat(),

        }