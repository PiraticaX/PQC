"""
QShield Enterprise
==================

Finding History Model

Maintains an immutable audit trail of all significant changes made to
a Finding.

Examples
--------
- Status changed
- Severity updated
- Assignment changed
- Risk accepted
- Finding resolved
- Finding reopened
"""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import (
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base import Base
from app.database.mixins import (
    TimestampMixin,
    UUIDMixin,
)
from app.database.types import GUID


# ============================================================
# ENUMS
# ============================================================


class FindingHistoryEvent(str, enum.Enum):
    CREATED = "created"
    UPDATED = "updated"
    STATUS_CHANGED = "status_changed"
    SEVERITY_CHANGED = "severity_changed"
    ASSIGNED = "assigned"
    UNASSIGNED = "unassigned"
    COMMENT_ADDED = "comment_added"
    RESOLVED = "resolved"
    REOPENED = "reopened"
    RISK_ACCEPTED = "risk_accepted"
    FALSE_POSITIVE = "false_positive"


# ============================================================
# MODEL
# ============================================================


class FindingHistory(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    """
    Immutable audit history for a Finding.
    """

    __tablename__ = "finding_history"

    __table_args__ = (
        Index("idx_finding_history_finding", "finding_id"),
        Index("idx_finding_history_actor", "actor_id"),
        Index("idx_finding_history_event", "event"),
    )

    # ============================================================
    # Relationships
    # ============================================================

    finding_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey(
            "findings.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    # ============================================================
    # Event
    # ============================================================

    event: Mapped[FindingHistoryEvent] = mapped_column(
        Enum(FindingHistoryEvent),
        nullable=False,
    )

    field_name: Mapped[str | None] = mapped_column(
        String(100),
        doc="Field that changed, if applicable.",
    )

    old_value: Mapped[str | None] = mapped_column(
        Text,
    )

    new_value: Mapped[str | None] = mapped_column(
        Text,
    )

    message: Mapped[str | None] = mapped_column(
        Text,
        doc="Human-readable description of the change.",
    )

    # ============================================================
    # Relationships
    # ============================================================

    finding = relationship(
        "Finding",
        back_populates="history",
    )

    actor = relationship(
        "User",
        back_populates="finding_history",
    )

    # ============================================================
    # Serialization
    # ============================================================

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "finding_id": str(self.finding_id),
            "actor_id": (
                str(self.actor_id)
                if self.actor_id
                else None
            ),
            "event": self.event.value,
            "field_name": self.field_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "message": self.message,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    # ============================================================
    # Representation
    # ============================================================

    def __repr__(self) -> str:
        return (
            "<FindingHistory("
            f"id={self.id}, "
            f"event='{self.event.value}', "
            f"finding_id={self.finding_id}"
            ")>"
        )