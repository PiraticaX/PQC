"""
QShield Enterprise
==================

Finding Exception Model

Stores approved exceptions for findings.

Examples
--------
- Risk Acceptance
- Temporary Waiver
- Compensating Control
- False Positive Approval
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
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


class ExceptionType(str, enum.Enum):
    RISK_ACCEPTANCE = "risk_acceptance"
    TEMPORARY_WAIVER = "temporary_waiver"
    COMPENSATING_CONTROL = "compensating_control"
    FALSE_POSITIVE = "false_positive"


class ExceptionStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


# ============================================================
# MODEL
# ============================================================


class FindingException(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    """
    Approved or pending exception for a finding.
    """

    __tablename__ = "finding_exceptions"

    __table_args__ = (
        Index("idx_exception_finding", "finding_id"),
        Index("idx_exception_status", "status"),
        Index("idx_exception_type", "exception_type"),
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

    requested_by: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
    )

    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
    )

    # ============================================================
    # Exception Details
    # ============================================================

    exception_type: Mapped[ExceptionType] = mapped_column(
        Enum(ExceptionType),
        nullable=False,
    )

    status: Mapped[ExceptionStatus] = mapped_column(
        Enum(ExceptionStatus),
        default=ExceptionStatus.PENDING,
        nullable=False,
    )

    justification: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    compensating_control: Mapped[str | None] = mapped_column(
        Text,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    auto_close: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Automatically close the finding when the exception is approved.",
    )

    # ============================================================
    # Relationships
    # ============================================================

    finding = relationship(
        "Finding",
        back_populates="exceptions",
    )

    requester = relationship(
        "User",
        foreign_keys=[requested_by],
    )

    approver = relationship(
        "User",
        foreign_keys=[approved_by],
    )

    # ============================================================
    # Helper Properties
    # ============================================================

    @property
    def is_active(self) -> bool:
        return self.status == ExceptionStatus.APPROVED

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False

        return datetime.utcnow() > self.expires_at

    # ============================================================
    # Workflow
    # ============================================================

    def approve(
        self,
        approver_id: uuid.UUID,
    ) -> None:
        self.status = ExceptionStatus.APPROVED
        self.approved_by = approver_id
        self.approved_at = datetime.utcnow()

    def reject(self) -> None:
        self.status = ExceptionStatus.REJECTED

    def expire(self) -> None:
        self.status = ExceptionStatus.EXPIRED

    # ============================================================
    # Serialization
    # ============================================================

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "finding_id": str(self.finding_id),
            "requested_by": (
                str(self.requested_by)
                if self.requested_by
                else None
            ),
            "approved_by": (
                str(self.approved_by)
                if self.approved_by
                else None
            ),
            "exception_type": self.exception_type.value,
            "status": self.status.value,
            "justification": self.justification,
            "compensating_control": self.compensating_control,
            "expires_at": (
                self.expires_at.isoformat()
                if self.expires_at
                else None
            ),
            "approved_at": (
                self.approved_at.isoformat()
                if self.approved_at
                else None
            ),
            "auto_close": self.auto_close,
            "is_expired": self.is_expired,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    # ============================================================
    # Representation
    # ============================================================

    def __repr__(self) -> str:
        return (
            "<FindingException("
            f"id={self.id}, "
            f"type='{self.exception_type.value}', "
            f"status='{self.status.value}'"
            ")>"
        )