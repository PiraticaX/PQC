"""
QShield Enterprise
==================

Cookie Result Model

Stores HTTP cookies discovered during a scan.

Each HTTP response may contain multiple cookies.
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
    Integer,
    String,
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


class SameSitePolicy(str, enum.Enum):
    STRICT = "Strict"
    LAX = "Lax"
    NONE = "None"
    UNKNOWN = "Unknown"


# ============================================================
# MODEL
# ============================================================


class CookieResult(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    """
    Cookie discovered during HTTP assessment.
    """

    __tablename__ = "cookie_results"

    __table_args__ = (
        Index("idx_cookie_scan", "scan_id"),
        Index("idx_cookie_name", "name"),
        Index("idx_cookie_domain", "domain"),
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
    # Identity
    # ============================================================

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    value: Mapped[str | None] = mapped_column(
        String(4096),
    )

    domain: Mapped[str | None] = mapped_column(
        String(255),
    )

    path: Mapped[str | None] = mapped_column(
        String(1024),
    )

    # ============================================================
    # Attributes
    # ============================================================

    secure: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    http_only: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    same_site: Mapped[SameSitePolicy] = mapped_column(
        Enum(SameSitePolicy),
        default=SameSitePolicy.UNKNOWN,
    )

    persistent: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    max_age: Mapped[int | None] = mapped_column(
        Integer,
    )

    # ============================================================
    # Prefix Validation
    # ============================================================

    host_prefix: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        doc="Cookie uses the __Host- prefix.",
    )

    secure_prefix: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        doc="Cookie uses the __Secure- prefix.",
    )

    # ============================================================
    # Relationships
    # ============================================================

    scan = relationship(
        "Scan",
        back_populates="cookie_results",
    )

    # ============================================================
    # Helper Properties
    # ============================================================

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False

        return datetime.utcnow() > self.expires_at

    @property
    def is_secure_cookie(self) -> bool:
        """
        Conservative security assessment.
        """

        return (
            self.secure
            and self.http_only
            and self.same_site
            != SameSitePolicy.NONE
        )

    # ============================================================
    # Serialization
    # ============================================================

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "scan_id": str(self.scan_id),
            "name": self.name,
            "value": self.value,
            "domain": self.domain,
            "path": self.path,
            "secure": self.secure,
            "http_only": self.http_only,
            "same_site": self.same_site.value,
            "persistent": self.persistent,
            "expires_at": (
                self.expires_at.isoformat()
                if self.expires_at
                else None
            ),
            "max_age": self.max_age,
            "host_prefix": self.host_prefix,
            "secure_prefix": self.secure_prefix,
            "is_expired": self.is_expired,
            "is_secure_cookie": self.is_secure_cookie,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    # ============================================================
    # Representation
    # ============================================================

    def __repr__(self) -> str:
        return (
            "<CookieResult("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"domain='{self.domain}'"
            ")>"
        )