"""
QShield Enterprise
==================

Compliance Result Model

Stores compliance assessment results discovered during a scan.

Each record represents the evaluation of a single control,
requirement, or recommendation from a compliance framework.
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


class ComplianceFramework(str, enum.Enum):
    ISO27001 = "ISO/IEC 27001"
    NIST_CSF = "NIST CSF"
    NIST_800_53 = "NIST SP 800-53"
    PCI_DSS = "PCI DSS"
    CIS_CONTROLS = "CIS Controls"
    SOC2 = "SOC 2"
    OWASP_ASVS = "OWASP ASVS"
    PQC_GUIDANCE = "NIST PQC Guidance"
    CUSTOM = "Custom"


class ComplianceStatus(str, enum.Enum):
    PASS = "Pass"
    FAIL = "Fail"
    PARTIAL = "Partial"
    NOT_APPLICABLE = "Not Applicable"


# ============================================================
# MODEL
# ============================================================


class ComplianceResult(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    """
    Compliance control assessment.
    """

    __tablename__ = "compliance_results"

    __table_args__ = (
        Index("idx_compliance_scan", "scan_id"),
        Index("idx_compliance_framework", "framework"),
        Index("idx_compliance_control", "control_id"),
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

    # ============================================================
    # Framework
    # ============================================================

    framework: Mapped[ComplianceFramework] = mapped_column(
        Enum(ComplianceFramework),
        nullable=False,
    )

    framework_version: Mapped[str | None] = mapped_column(
        String(64),
    )

    control_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    control_name: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )

    # ============================================================
    # Result
    # ============================================================

    status: Mapped[ComplianceStatus] = mapped_column(
        Enum(ComplianceStatus),
        nullable=False,
    )

    score: Mapped[int | None] = mapped_column(
        Integer,
    )

    severity: Mapped[str | None] = mapped_column(
        String(32),
    )

    # ============================================================
    # Details
    # ============================================================

    evidence: Mapped[str | None] = mapped_column(
        Text,
    )

    remediation: Mapped[str | None] = mapped_column(
        Text,
    )

    reference: Mapped[str | None] = mapped_column(
        Text,
    )

    automated: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    # ============================================================
    # Relationships
    # ============================================================

    scan = relationship(
        "Scan",
        back_populates="compliance_results",
    )
        # ============================================================
    # Helper Properties
    # ============================================================

    @property
    def is_compliant(self) -> bool:
        """
        Returns True when the evaluated control passes.
        """

        return self.status == ComplianceStatus.PASS

    @property
    def requires_remediation(self) -> bool:
        """
        Returns True when remediation work is required.
        """

        return self.status in (
            ComplianceStatus.FAIL,
            ComplianceStatus.PARTIAL,
        )

    @property
    def normalized_score(self) -> float | None:
        """
        Return a normalized score in the range [0.0, 1.0].

        Assumes the stored score is a percentage (0-100).
        """

        if self.score is None:
            return None

        return max(0.0, min(self.score / 100.0, 1.0))

    @property
    def compliance_summary(self) -> str:
        """
        Human-readable compliance summary.
        """

        return (
            f"{self.framework.value} | "
            f"{self.control_id} | "
            f"{self.status.value}"
        )

    # ============================================================
    # Serialization
    # ============================================================

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "scan_id": str(self.scan_id),
            "framework": self.framework.value,
            "framework_version": self.framework_version,
            "control_id": self.control_id,
            "control_name": self.control_name,
            "status": self.status.value,
            "score": self.score,
            "normalized_score": self.normalized_score,
            "severity": self.severity,
            "evidence": self.evidence,
            "remediation": self.remediation,
            "reference": self.reference,
            "automated": self.automated,
            "is_compliant": self.is_compliant,
            "requires_remediation": self.requires_remediation,
            "compliance_summary": self.compliance_summary,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    # ============================================================
    # Representation
    # ============================================================

    def __repr__(self) -> str:
        return (
            "<ComplianceResult("
            f"id={self.id}, "
            f"framework='{self.framework.value}', "
            f"control='{self.control_id}', "
            f"status='{self.status.value}'"
            ")>"
        )