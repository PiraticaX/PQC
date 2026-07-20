"""
QShield Enterprise
==================

Analytics Models

Stores platform analytics events.
"""

from __future__ import annotations

import uuid
from datetime import datetime, UTC

from sqlalchemy import (
    String,
    Text,
    JSON,
    DateTime,
    Index,
)

from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.database.types import GUID


class AnalyticsEvent(Base):
    """
    Stores application analytics events.
    """

    __tablename__ = "analytics_events"

    __table_args__ = (
        Index(
            "idx_analytics_event_type",
            "event_type",
        ),
        Index(
            "idx_analytics_created",
            "created_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        nullable=True,
    )

    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        nullable=True,
    )

    payload: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )


    def to_dict(self):
        return {
            "id": str(self.id),
            "event_type": self.event_type,
            "user_id": str(self.user_id) if self.user_id else None,
            "organization_id": str(self.organization_id)
            if self.organization_id
            else None,
            "payload": self.payload,
            "description": self.description,
            "created_at": self.created_at.isoformat()
            if self.created_at
            else None,
        }