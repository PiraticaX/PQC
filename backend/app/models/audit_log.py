"""
QShield Enterprise
==================

Audit Log Model

Stores immutable security and operational audit events.

Audit logs provide traceability for authentication, authorization,
administrative actions, scan execution, report generation, API
activity, and configuration changes.
"""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    Index,
    Integer,
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


class AuditOutcome(str, enum.Enum):
    SUCCESS = "Success"
    FAILURE = "Failure"
    WARNING = "Warning"


class AuditResourceType(str, enum.Enum):
    USER = "User"
    ROLE = "Role"
    TEAM = "Team"
    ORGANIZATION = "Organization"
    ASSET = "Asset"
    ASSET_GROUP = "Asset Group"
    SCAN = "Scan"
    FINDING = "Finding"
    REPORT = "Report"
    SCHEDULE = "Scheduled Scan"
    SYSTEM = "System"
    API = "API"
    OTHER = "Other"


# ============================================================
# MODEL
# ============================================================


class AuditLog(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    """
    Immutable audit log entry.
    """

    __tablename__ = "audit_logs"

    __table_args__ = (
        Index("idx_audit_user", "user_id"),
        Index("idx_audit_action", "action"),
        Index("idx_audit_resource", "resource_type"),
        Index("idx_audit_created", "created_at"),
    )

    # ============================================================
    # Relationships
    # ============================================================

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
    )

    # ============================================================
    # Event
    # ============================================================

    action: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Human-readable action identifier.",
    )

    resource_type: Mapped[AuditResourceType] = mapped_column(
        Enum(AuditResourceType),
        nullable=False,
    )

    resource_id: Mapped[str | None] = mapped_column(
        String(255),
    )

    outcome: Mapped[AuditOutcome] = mapped_column(
        Enum(AuditOutcome),
        nullable=False,
    )

    # ============================================================
    # Request Context
    # ============================================================

    ip_address: Mapped[str | None] = mapped_column(
        String(64),
    )

    user_agent: Mapped[str | None] = mapped_column(
        Text,
    )

    request_id: Mapped[str | None] = mapped_column(
        String(128),
    )

    # ============================================================
    # Details
    # ============================================================

    message: Mapped[str | None] = mapped_column(
        Text,
    )

    event_data: Mapped[str | None] = mapped_column(
        Text,
        doc="Serialized JSON payload describing the event.",
    )

    success: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    duration_ms: Mapped[int | None] = mapped_column(
        Integer,
    )

    # ============================================================
    # Relationships
    # ============================================================

    user = relationship(
        "User",
        back_populates="audit_logs",
    )
        # ============================================================
    # Helper Properties
    # ============================================================

    @property
    def is_success(self) -> bool:
        """
        Returns True when the audit event completed successfully.
        """

        return (
            self.success
            and self.outcome == AuditOutcome.SUCCESS
        )

    @property
    def is_failure(self) -> bool:
        """
        Returns True when the audit event represents a failure.
        """

        return self.outcome == AuditOutcome.FAILURE

    @property
    def has_request_context(self) -> bool:
        """
        Returns True when request metadata is available.
        """

        return any(
            (
                self.ip_address,
                self.user_agent,
                self.request_id,
            )
        )

    @property
    def has_event_data(self) -> bool:
        """
        Returns True when structured event metadata exists.
        """

        return bool(
            self.event_data
            and self.event_data.strip()
        )

    # ============================================================
    # Serialization
    # ============================================================

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user_id": (
                str(self.user_id)
                if self.user_id
                else None
            ),
            "action": self.action,
            "resource_type": self.resource_type.value,
            "resource_id": self.resource_id,
            "outcome": self.outcome.value,
            "success": self.success,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "request_id": self.request_id,
            "message": self.message,
            "event_data": self.event_data,
            "duration_ms": self.duration_ms,
            "is_success": self.is_success,
            "is_failure": self.is_failure,
            "has_request_context": self.has_request_context,
            "has_event_data": self.has_event_data,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    # ============================================================
    # Representation
    # ============================================================

    def __repr__(self) -> str:
        return (
            "<AuditLog("
            f"id={self.id}, "
            f"action='{self.action}', "
            f"resource='{self.resource_type.value}', "
            f"outcome='{self.outcome.value}'"
            ")>"
        )