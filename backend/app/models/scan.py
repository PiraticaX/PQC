"""
QShield Enterprise
==================

Scan Model

Represents a single execution of the scanning engine.

A Scan belongs to exactly one Asset.

Scanner result tables are intentionally normalized.

A Scan itself stores only execution metadata while detailed results are
stored in dedicated tables.

Relationships
-------------
Asset
Finding
TLSResult
CertificateResult
DNSResult
HTTPResult
CookieResult
EmailResult
TechnologyResult
PQCResult
ComplianceResult
AIRecommendation
Report
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
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


class ScanStatus(str, enum.Enum):
    """
    Current lifecycle state of a scan.
    """

    PENDING = "pending"

    QUEUED = "queued"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"

    TIMEOUT = "timeout"


class ScanTrigger(str, enum.Enum):
    """
    Source that initiated the scan.
    """

    MANUAL = "manual"

    SCHEDULED = "scheduled"

    API = "api"

    WEBHOOK = "webhook"

    DISCOVERY = "discovery"


class ScanEngine(str, enum.Enum):
    """
    Scanner backend.
    """

    INTERNAL = "internal"

    NMAP = "nmap"

    SSLYZE = "sslyze"

    CUSTOM = "custom"


# ============================================================
# MODEL
# ============================================================


class Scan(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    DescriptionMixin,
    Base,
):
    """
    Scan execution metadata.

    Scanner outputs are stored in dedicated result tables.
    """

    __tablename__ = "scans"

    __table_args__ = (
        Index("idx_scan_asset", "asset_id"),
        Index("idx_scan_status", "status"),
        Index("idx_scan_started", "started_at"),
        Index("idx_scan_finished", "completed_at"),
    )

    # ============================================================
    # Ownership
    # ============================================================

    asset_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey(
            "assets.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    # ============================================================
    # Execution
    # ============================================================

    status: Mapped[ScanStatus] = mapped_column(
        Enum(ScanStatus),
        default=ScanStatus.PENDING,
        nullable=False,
    )

    trigger: Mapped[ScanTrigger] = mapped_column(
        Enum(ScanTrigger),
        default=ScanTrigger.MANUAL,
        nullable=False,
    )

    engine: Mapped[ScanEngine] = mapped_column(
        Enum(ScanEngine),
        default=ScanEngine.INTERNAL,
        nullable=False,
    )

    # ============================================================
    # Timing
    # ============================================================

    queued_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    duration_seconds: Mapped[float | None] = mapped_column(
        Float,
    )

    # ============================================================
    # Worker
    # ============================================================

    worker_name: Mapped[str | None] = mapped_column(
        String(255),
    )

    worker_version: Mapped[str | None] = mapped_column(
        String(100),
    )

    # ============================================================
    # Statistics
    # ============================================================

    total_findings: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    critical_findings: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    high_findings: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    medium_findings: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    low_findings: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    informational_findings: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # ============================================================
    # Metadata
    # ============================================================

    configuration: Mapped[str | None] = mapped_column(
        Text,
        doc="Serialized scan configuration.",
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
    )

    # ============================================================
    # Relationships
    # ============================================================

    asset = relationship(
        "Asset",
        back_populates="scans",
    )

    findings = relationship(
        "Finding",
        back_populates="scan",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    tls_results = relationship(
        "TLSResult",
        back_populates="scan",
        cascade="all, delete-orphan",
    )

    certificate_results = relationship(
        "CertificateResult",
        back_populates="scan",
        cascade="all, delete-orphan",
    )

    dns_results = relationship(
        "DNSResult",
        back_populates="scan",
        cascade="all, delete-orphan",
    )

    http_results = relationship(
        "HTTPResult",
        back_populates="scan",
        cascade="all, delete-orphan",
    )

    cookie_results = relationship(
        "CookieResult",
        back_populates="scan",
        cascade="all, delete-orphan",
    )

    email_results = relationship(
        "EmailResult",
        back_populates="scan",
        cascade="all, delete-orphan",
    )

    technology_results = relationship(
        "TechnologyResult",
        back_populates="scan",
        cascade="all, delete-orphan",
    )

    pqc_results = relationship(
        "PQCResult",
        back_populates="scan",
        cascade="all, delete-orphan",
    )

    compliance_results = relationship(
        "ComplianceResult",
        back_populates="scan",
        cascade="all, delete-orphan",
    )

    ai_recommendations = relationship(
        "AIRecommendation",
        back_populates="scan",
        cascade="all, delete-orphan",
    )

    reports = relationship(
        "Report",
        back_populates="scan",
    )
        # ============================================================
    # Helper Properties
    # ============================================================

    @property
    def is_pending(self) -> bool:
        """Returns True if the scan has not started."""
        return self.status == ScanStatus.PENDING

    @property
    def is_running(self) -> bool:
        """Returns True while the scan is executing."""
        return self.status == ScanStatus.RUNNING

    @property
    def is_finished(self) -> bool:
        """Returns True if the scan has reached a terminal state."""
        return self.status in (
            ScanStatus.COMPLETED,
            ScanStatus.FAILED,
            ScanStatus.CANCELLED,
            ScanStatus.TIMEOUT,
        )

    @property
    def success(self) -> bool:
        """Returns True if the scan completed successfully."""
        return self.status == ScanStatus.COMPLETED

    @property
    def has_errors(self) -> bool:
        """Returns True if an error message is present."""
        return bool(self.error_message)

    # ============================================================
    # Lifecycle
    # ============================================================

    def mark_queued(self) -> None:
        """Mark scan as queued."""
        self.status = ScanStatus.QUEUED
        self.queued_at = datetime.utcnow()

    def start(self) -> None:
        """Mark scan as running."""
        self.status = ScanStatus.RUNNING
        self.started_at = datetime.utcnow()

    def complete(self) -> None:
        """Mark scan as completed."""
        self.status = ScanStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.calculate_duration()

    def fail(
        self,
        message: str,
    ) -> None:
        """Mark scan as failed."""
        self.status = ScanStatus.FAILED
        self.error_message = message
        self.completed_at = datetime.utcnow()
        self.calculate_duration()

    def cancel(self) -> None:
        """Cancel the scan."""
        self.status = ScanStatus.CANCELLED
        self.completed_at = datetime.utcnow()
        self.calculate_duration()

    def timeout(self) -> None:
        """Mark scan as timed out."""
        self.status = ScanStatus.TIMEOUT
        self.completed_at = datetime.utcnow()
        self.calculate_duration()

    # ============================================================
    # Statistics
    # ============================================================

    def calculate_duration(self) -> None:
        """Calculate total runtime in seconds."""

        if self.started_at and self.completed_at:
            self.duration_seconds = (
                self.completed_at - self.started_at
            ).total_seconds()

    def update_finding_statistics(self) -> None:
        """
        Recalculate finding counters from related findings.
        """

        self.total_findings = len(self.findings)

        self.critical_findings = sum(
            1 for f in self.findings
            if getattr(f, "severity", None) == "critical"
        )

        self.high_findings = sum(
            1 for f in self.findings
            if getattr(f, "severity", None) == "high"
        )

        self.medium_findings = sum(
            1 for f in self.findings
            if getattr(f, "severity", None) == "medium"
        )

        self.low_findings = sum(
            1 for f in self.findings
            if getattr(f, "severity", None) == "low"
        )

        self.informational_findings = sum(
            1 for f in self.findings
            if getattr(f, "severity", None) == "info"
        )

    # ============================================================
    # Serialization
    # ============================================================

    def to_dict(
        self,
        include_findings: bool = False,
    ) -> dict:
        """
        Serialize the scan.
        """

        data = {
            "id": str(self.id),
            "asset_id": str(self.asset_id),
            "status": self.status.value,
            "trigger": self.trigger.value,
            "engine": self.engine.value,
            "queued_at": (
                self.queued_at.isoformat()
                if self.queued_at
                else None
            ),
            "started_at": (
                self.started_at.isoformat()
                if self.started_at
                else None
            ),
            "completed_at": (
                self.completed_at.isoformat()
                if self.completed_at
                else None
            ),
            "duration_seconds": self.duration_seconds,
            "worker_name": self.worker_name,
            "worker_version": self.worker_version,
            "configuration": self.configuration,
            "error_message": self.error_message,
            "total_findings": self.total_findings,
            "critical_findings": self.critical_findings,
            "high_findings": self.high_findings,
            "medium_findings": self.medium_findings,
            "low_findings": self.low_findings,
            "informational_findings": self.informational_findings,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "deleted_at": (
                self.deleted_at.isoformat()
                if self.deleted_at
                else None
            ),
        }

        if include_findings:
            data["findings"] = [
                finding.to_dict()
                for finding in self.findings
            ]

        return data

    # ============================================================
    # Representation
    # ============================================================

    def __repr__(self) -> str:
        return (
            "<Scan("
            f"id={self.id}, "
            f"status='{self.status.value}', "
            f"asset_id={self.asset_id}"
            ")>"
        )
    