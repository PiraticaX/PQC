"""
QShield Enterprise
==================

Technology Result Model

Stores technology fingerprinting results discovered during a scan.

One scan may identify multiple technologies associated with a single
asset or endpoint.
"""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import (
    Boolean,
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


class TechnologyCategory(str, enum.Enum):
    WEB_SERVER = "Web Server"
    OPERATING_SYSTEM = "Operating System"
    FRAMEWORK = "Framework"
    PROGRAMMING_LANGUAGE = "Programming Language"
    DATABASE = "Database"
    CMS = "CMS"
    CDN = "CDN"
    WAF = "WAF"
    REVERSE_PROXY = "Reverse Proxy"
    LOAD_BALANCER = "Load Balancer"
    CONTAINER = "Container"
    ORCHESTRATION = "Orchestration"
    JAVASCRIPT_LIBRARY = "JavaScript Library"
    API = "API"
    OTHER = "Other"


# ============================================================
# MODEL
# ============================================================


class TechnologyResult(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    """
    Technology fingerprint identified during a scan.
    """

    __tablename__ = "technology_results"

    __table_args__ = (
        Index("idx_tech_scan", "scan_id"),
        Index("idx_tech_name", "name"),
        Index("idx_tech_category", "category"),
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
    # Technology Identity
    # ============================================================

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    category: Mapped[TechnologyCategory] = mapped_column(
        Enum(TechnologyCategory),
        nullable=False,
    )

    vendor: Mapped[str | None] = mapped_column(
        String(255),
    )

    version: Mapped[str | None] = mapped_column(
        String(128),
    )

    latest_version: Mapped[str | None] = mapped_column(
        String(128),
    )

    # ============================================================
    # Detection
    # ============================================================

    detection_method: Mapped[str | None] = mapped_column(
        String(255),
    )

    confidence: Mapped[int] = mapped_column(
        default=100,
    )

    evidence: Mapped[str | None] = mapped_column(
        Text,
    )

    # ============================================================
    # Lifecycle
    # ============================================================

    end_of_life: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    supported: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    vulnerable_version: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    # ============================================================
    # Relationships
    # ============================================================

    scan = relationship(
        "Scan",
        back_populates="technology_results",
    )
        # ============================================================
    # Helper Properties
    # ============================================================

    @property
    def has_version_information(self) -> bool:
        """
        Returns True when a version was successfully identified.
        """

        return bool(self.version)

    @property
    def update_available(self) -> bool:
        """
        Returns True if a newer version is known.

        Note:
            This performs a simple string comparison. A dedicated
            semantic version comparison utility should replace this
            implementation in future revisions.
        """

        if not self.version or not self.latest_version:
            return False

        return self.version != self.latest_version

    @property
    def is_high_risk(self) -> bool:
        """
        Conservative technology risk assessment.
        """

        return (
            self.vulnerable_version
            or self.end_of_life
            or not self.supported
        )

    @property
    def lifecycle_status(self) -> str:
        """
        Human-readable lifecycle status.
        """

        if self.end_of_life:
            return "End of Life"

        if not self.supported:
            return "Unsupported"

        if self.update_available:
            return "Update Available"

        return "Current"

    # ============================================================
    # Serialization
    # ============================================================

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "scan_id": str(self.scan_id),
            "name": self.name,
            "category": self.category.value,
            "vendor": self.vendor,
            "version": self.version,
            "latest_version": self.latest_version,
            "detection_method": self.detection_method,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "end_of_life": self.end_of_life,
            "supported": self.supported,
            "vulnerable_version": self.vulnerable_version,
            "has_version_information": self.has_version_information,
            "update_available": self.update_available,
            "is_high_risk": self.is_high_risk,
            "lifecycle_status": self.lifecycle_status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    # ============================================================
    # Representation
    # ============================================================

    def __repr__(self) -> str:
        return (
            "<TechnologyResult("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"version='{self.version}'"
            ")>"
        )