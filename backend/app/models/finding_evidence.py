"""
QShield Enterprise
==================

Finding Evidence Model

Stores evidence supporting a finding.

Examples
--------
- HTTP request/response
- Screenshot
- TLS certificate
- DNS record
- Command output
- Log snippet
- JSON payload
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


class EvidenceType(str, enum.Enum):
    SCREENSHOT = "screenshot"
    HTTP_REQUEST = "http_request"
    HTTP_RESPONSE = "http_response"
    TLS_CERTIFICATE = "tls_certificate"
    DNS_RECORD = "dns_record"
    LOG = "log"
    COMMAND_OUTPUT = "command_output"
    JSON = "json"
    TEXT = "text"
    OTHER = "other"


# ============================================================
# MODEL
# ============================================================


class FindingEvidence(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    """
    Evidence attached to a finding.
    """

    __tablename__ = "finding_evidence"

    __table_args__ = (
        Index("idx_finding_evidence_finding", "finding_id"),
        Index("idx_finding_evidence_type", "evidence_type"),
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
    # Evidence
    # ============================================================

    evidence_type: Mapped[EvidenceType] = mapped_column(
        Enum(EvidenceType),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    content: Mapped[str | None] = mapped_column(
        Text,
    )

    file_name: Mapped[str | None] = mapped_column(
        String(255),
    )

    mime_type: Mapped[str | None] = mapped_column(
        String(100),
    )

    checksum: Mapped[str | None] = mapped_column(
        String(128),
        doc="SHA-256 checksum of the evidence file/content.",
    )

    # ============================================================
    # Relationships
    # ============================================================

    finding = relationship(
        "Finding",
        back_populates="evidence",
    )

    # ============================================================
    # Serialization
    # ============================================================

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "finding_id": str(self.finding_id),
            "evidence_type": self.evidence_type.value,
            "title": self.title,
            "content": self.content,
            "file_name": self.file_name,
            "mime_type": self.mime_type,
            "checksum": self.checksum,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    # ============================================================
    # Representation
    # ============================================================

    def __repr__(self) -> str:
        return (
            "<FindingEvidence("
            f"id={self.id}, "
            f"type='{self.evidence_type.value}', "
            f"title='{self.title}'"
            ")>"
        )