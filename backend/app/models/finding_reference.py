"""
QShield Enterprise
==================

Finding Reference Model

Stores external references associated with a finding.

Examples
--------
- CVE
- CWE
- NIST NVD
- GitHub Security Advisory
- OWASP
- Vendor Advisory
- Microsoft Security Bulletin
- Cisco Advisory
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


class ReferenceType(str, enum.Enum):
    CVE = "cve"
    CWE = "cwe"
    NVD = "nvd"
    CVSS = "cvss"
    OWASP = "owasp"
    GITHUB = "github"
    VENDOR = "vendor"
    RFC = "rfc"
    CERT = "cert"
    MITRE = "mitre"
    OTHER = "other"


# ============================================================
# MODEL
# ============================================================


class FindingReference(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    """
    External reference attached to a finding.
    """

    __tablename__ = "finding_references"

    __table_args__ = (
        Index("idx_finding_reference_finding", "finding_id"),
        Index("idx_finding_reference_type", "reference_type"),
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

    # ============================================================
    # Reference Information
    # ============================================================

    reference_type: Mapped[ReferenceType] = mapped_column(
        Enum(ReferenceType),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    reference_id: Mapped[str | None] = mapped_column(
        String(100),
        doc="Example: CVE-2026-12345, CWE-79",
    )

    url: Mapped[str] = mapped_column(
        String(2048),
        nullable=False,
    )

    source: Mapped[str | None] = mapped_column(
        String(255),
        doc="Reference publisher or organization.",
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
    )

    # ============================================================
    # Relationships
    # ============================================================

    finding = relationship(
        "Finding",
        back_populates="references",
    )

    # ============================================================
    # Serialization
    # ============================================================

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "finding_id": str(self.finding_id),
            "reference_type": self.reference_type.value,
            "title": self.title,
            "reference_id": self.reference_id,
            "url": self.url,
            "source": self.source,
            "summary": self.summary,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    # ============================================================
    # Representation
    # ============================================================

    def __repr__(self) -> str:
        return (
            "<FindingReference("
            f"id={self.id}, "
            f"type='{self.reference_type.value}', "
            f"title='{self.title}'"
            ")>"
        )