"""
QShield Enterprise
==================

Report Model

Stores generated assessment reports.

Reports may be produced in multiple formats and are associated with
a single scan. They may optionally record the user that generated
or requested the report.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
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


class ReportType(str, enum.Enum):
    EXECUTIVE = "Executive"
    TECHNICAL = "Technical"
    COMPLIANCE = "Compliance"
    PQC = "Post-Quantum"
    CUSTOM = "Custom"


class ReportFormat(str, enum.Enum):
    PDF = "PDF"
    HTML = "HTML"
    JSON = "JSON"
    CSV = "CSV"


class ReportStatus(str, enum.Enum):
    PENDING = "Pending"
    GENERATING = "Generating"
    COMPLETED = "Completed"
    FAILED = "Failed"
    EXPIRED = "Expired"


# ============================================================
# MODEL
# ============================================================


class Report(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    """
    Generated security assessment report.
    """

    __tablename__ = "reports"

    __table_args__ = (
        Index("idx_report_scan", "scan_id"),
        Index("idx_report_status", "status"),
        Index("idx_report_type", "report_type"),
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

    generated_by_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
    )

    # ============================================================
    # Metadata
    # ============================================================

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    report_type: Mapped[ReportType] = mapped_column(
        Enum(ReportType),
        nullable=False,
    )

    report_format: Mapped[ReportFormat] = mapped_column(
        Enum(ReportFormat),
        nullable=False,
    )

    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus),
        default=ReportStatus.PENDING,
        nullable=False,
    )

    # ============================================================
    # Content
    # ============================================================

    executive_summary: Mapped[str | None] = mapped_column(
        Text,
    )

    file_path: Mapped[str | None] = mapped_column(
        String(1024),
    )

    checksum: Mapped[str | None] = mapped_column(
        String(128),
    )

    file_size_bytes: Mapped[int | None] = mapped_column(
        Integer,
    )

    # ============================================================
    # Timing
    # ============================================================

    generated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    # ============================================================
    # Relationships
    # ============================================================

    scan = relationship(
        "Scan",
        back_populates="reports",
    )

    generated_by = relationship(
        "User",
        back_populates="reports",
    )
        # ============================================================
    # Helper Properties
    # ============================================================

    @property
    def is_completed(self) -> bool:
        """
        Returns True when report generation completed successfully.
        """

        return self.status == ReportStatus.COMPLETED

    @property
    def is_expired(self) -> bool:
        """
        Returns True when the report has passed its expiration time.
        """

        if self.expires_at is None:
            return False

        return datetime.utcnow() > self.expires_at

    @property
    def file_size_mb(self) -> float | None:
        """
        Returns the report size in megabytes.
        """

        if self.file_size_bytes is None:
            return None

        return round(self.file_size_bytes / (1024 * 1024), 2)

    @property
    def is_downloadable(self) -> bool:
        """
        Returns True when the report is available for download.
        """

        return (
            self.is_completed
            and not self.is_expired
            and bool(self.file_path)
        )

    # ============================================================
    # Serialization
    # ============================================================

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "scan_id": str(self.scan_id),
            "generated_by_id": (
                str(self.generated_by_id)
                if self.generated_by_id
                else None
            ),
            "title": self.title,
            "report_type": self.report_type.value,
            "report_format": self.report_format.value,
            "status": self.status.value,
            "executive_summary": self.executive_summary,
            "file_path": self.file_path,
            "checksum": self.checksum,
            "file_size_bytes": self.file_size_bytes,
            "file_size_mb": self.file_size_mb,
            "generated_at": (
                self.generated_at.isoformat()
                if self.generated_at
                else None
            ),
            "expires_at": (
                self.expires_at.isoformat()
                if self.expires_at
                else None
            ),
            "is_completed": self.is_completed,
            "is_expired": self.is_expired,
            "is_downloadable": self.is_downloadable,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    # ============================================================
    # Representation
    # ============================================================

    def __repr__(self) -> str:
        return (
            "<Report("
            f"id={self.id}, "
            f"title='{self.title}', "
            f"status='{self.status.value}', "
            f"format='{self.report_format.value}'"
            ")>"
        )