"""
QShield Enterprise
==================

Finding Model

A Finding represents a single security issue discovered during a scan.

Examples
--------
- TLS 1.0 Enabled
- Missing HSTS Header
- Weak SSH Cipher
- Expired Certificate
- Open Redis Instance
- CVE-2026-12345
- DNS Zone Transfer Enabled
- Missing SPF Record
- PQC Unsafe Algorithm
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
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
    DescriptionMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)
from app.database.types import GUID


# ============================================================
# ENUMS
# ============================================================


class Severity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"
FindingSeverity = Severity


class FindingStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ACCEPTED = "accepted"
    FALSE_POSITIVE = "false_positive"


class Confidence(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ============================================================
# MODEL
# ============================================================


class Finding(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    DescriptionMixin,
    Base,
):
    """
    Security finding.
    """

    __tablename__ = "findings"

    __table_args__ = (
        Index("idx_finding_scan", "scan_id"),
        Index("idx_finding_asset", "asset_id"),
        Index("idx_finding_severity", "severity"),
        Index("idx_finding_status", "status"),
        Index("idx_finding_cve", "cve"),
    )

    # ============================================================
    # Relationships
    # ============================================================

    scan_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey(
            "scans.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    asset_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey(
            "assets.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
    )

    # ============================================================
    # Identity
    # ============================================================

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    finding_code: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
    )

    plugin: Mapped[str | None] = mapped_column(
        String(100),
    )

    # ============================================================
    # Risk
    # ============================================================

    severity: Mapped[Severity] = mapped_column(
        Enum(Severity),
        nullable=False,
    )

    confidence: Mapped[Confidence] = mapped_column(
        Enum(Confidence),
        default=Confidence.HIGH,
    )

    status: Mapped[FindingStatus] = mapped_column(
        Enum(FindingStatus),
        default=FindingStatus.OPEN,
    )

    cvss_score: Mapped[float | None] = mapped_column(
        Float,
    )

    epss_score: Mapped[float | None] = mapped_column(
        Float,
    )

    exploit_available: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    actively_exploited: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    # ============================================================
    # References
    # ============================================================

    cve: Mapped[str | None] = mapped_column(
        String(50),
    )

    cwe: Mapped[str | None] = mapped_column(
        String(50),
    )

    cpe: Mapped[str | None] = mapped_column(
        String(255),
    )

    owasp_category: Mapped[str | None] = mapped_column(
        String(50),
    )

    # ============================================================
    # Remediation
    # ============================================================

    remediation: Mapped[str | None] = mapped_column(
        Text,
    )

    remediation_effort: Mapped[str | None] = mapped_column(
        String(100),
    )

    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    # ============================================================
    # Relationships
    # ============================================================

    asset = relationship(
        "Asset",
        back_populates="findings",
    )

    scan = relationship(
        "Scan",
        back_populates="findings",
    )

    assignee = relationship(
        "User",
        back_populates="assigned_findings",
    )

    ai_recommendations = relationship(
        "AIRecommendation",
        back_populates="finding",
        cascade="all, delete-orphan",
    )

    evidence = relationship(
        "FindingEvidence",
        back_populates="finding",
        cascade="all, delete-orphan",
    )

    comments = relationship(
        "FindingComment",
        back_populates="finding",
        cascade="all, delete-orphan",
    )

    history = relationship(
        "FindingHistory",
        back_populates="finding",
        cascade="all, delete-orphan",
    )

    references = relationship(
        "FindingReference",
        back_populates="finding",
        cascade="all, delete-orphan",
    )

    exceptions = relationship(
        "FindingException",
        back_populates="finding",
        cascade="all, delete-orphan",
    )
        # ============================================================
    # Helper Properties
    # ============================================================

    @property
    def is_open(self) -> bool:
        """Returns True if the finding requires action."""
        return self.status in (
            FindingStatus.OPEN,
            FindingStatus.IN_PROGRESS,
        )

    @property
    def is_closed(self) -> bool:
        """Returns True if the finding is no longer active."""
        return self.status in (
            FindingStatus.RESOLVED,
            FindingStatus.ACCEPTED,
            FindingStatus.FALSE_POSITIVE,
        )

    @property
    def is_critical(self) -> bool:
        return self.severity == Severity.CRITICAL

    @property
    def is_high(self) -> bool:
        return self.severity == Severity.HIGH

    @property
    def is_medium(self) -> bool:
        return self.severity == Severity.MEDIUM

    @property
    def is_low(self) -> bool:
        return self.severity == Severity.LOW

    @property
    def is_overdue(self) -> bool:
        """
        Returns True if remediation due date has passed.
        """

        if (
            self.due_date is None
            or self.is_closed
        ):
            return False

        return datetime.utcnow() > self.due_date

    # ============================================================
    # Workflow
    # ============================================================

    def assign(
        self,
        user_id: uuid.UUID,
    ) -> None:
        """
        Assign finding to a user.
        """

        self.assigned_to = user_id

    def start_progress(self) -> None:
        """
        Mark finding as in progress.
        """

        self.status = FindingStatus.IN_PROGRESS

    def resolve(self) -> None:
        """
        Resolve finding.
        """

        self.status = FindingStatus.RESOLVED
        self.resolved_at = datetime.utcnow()

    def accept_risk(self) -> None:
        """
        Accept residual risk.
        """

        self.status = FindingStatus.ACCEPTED

    def mark_false_positive(self) -> None:
        """
        Mark finding as false positive.
        """

        self.status = FindingStatus.FALSE_POSITIVE

    # ============================================================
    # Risk Helpers
    # ============================================================

    def severity_weight(self) -> int:
        """
        Numeric severity weighting.
        """

        mapping = {
            Severity.CRITICAL: 5,
            Severity.HIGH: 4,
            Severity.MEDIUM: 3,
            Severity.LOW: 2,
            Severity.INFO: 1,
        }

        return mapping[self.severity]

    # ============================================================
    # Serialization
    # ============================================================

    def to_dict(self) -> dict:
        """
        Serialize finding.
        """

        return {
            "id": str(self.id),
            "scan_id": str(self.scan_id),
            "asset_id": str(self.asset_id),
            "assigned_to": (
                str(self.assigned_to)
                if self.assigned_to
                else None
            ),
            "title": self.title,
            "description": self.description,
            "finding_code": self.finding_code,
            "category": self.category,
            "plugin": self.plugin,
            "severity": self.severity.value,
            "confidence": self.confidence.value,
            "status": self.status.value,
            "cvss_score": self.cvss_score,
            "epss_score": self.epss_score,
            "exploit_available": self.exploit_available,
            "actively_exploited": self.actively_exploited,
            "cve": self.cve,
            "cwe": self.cwe,
            "cpe": self.cpe,
            "owasp_category": self.owasp_category,
            "remediation": self.remediation,
            "remediation_effort": self.remediation_effort,
            "due_date": (
                self.due_date.isoformat()
                if self.due_date
                else None
            ),
            "resolved_at": (
                self.resolved_at.isoformat()
                if self.resolved_at
                else None
            ),
            "is_overdue": self.is_overdue,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "deleted_at": (
                self.deleted_at.isoformat()
                if self.deleted_at
                else None
            ),
        }

    # ============================================================
    # Representation
    # ============================================================

    def __repr__(self) -> str:
        return (
            "<Finding("
            f"id={self.id}, "
            f"severity='{self.severity.value}', "
            f"title='{self.title}'"
            ")>"
        )
