"""
QShield Enterprise
==================

TLS Result Model

Stores TLS/SSL assessment results produced during a scan.

One Scan may generate multiple TLS results if multiple services or
ports expose TLS.
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


class TLSGrade(str, enum.Enum):
    A_PLUS = "A+"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"


# ============================================================
# MODEL
# ============================================================


class TLSResult(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    """
    TLS assessment for one endpoint.
    """

    __tablename__ = "tls_results"

    __table_args__ = (
        Index("idx_tls_scan", "scan_id"),
        Index("idx_tls_grade", "grade"),
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
    # Endpoint
    # ============================================================

    hostname: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(64),
    )

    port: Mapped[int] = mapped_column(
        Integer,
        default=443,
        nullable=False,
    )

    # ============================================================
    # Protocol Support
    # ============================================================

    ssl2_supported: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    ssl3_supported: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    tls10_supported: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    tls11_supported: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    tls12_supported: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    tls13_supported: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    # ============================================================
    # Cryptography
    # ============================================================

    preferred_cipher: Mapped[str | None] = mapped_column(
        String(255),
    )

    key_exchange: Mapped[str | None] = mapped_column(
        String(100),
    )

    signature_algorithm: Mapped[str | None] = mapped_column(
        String(100),
    )

    key_size: Mapped[int | None] = mapped_column(
        Integer,
    )

    forward_secrecy: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    # ============================================================
    # Certificate
    # ============================================================

    certificate_subject: Mapped[str | None] = mapped_column(
        String(512),
    )

    certificate_issuer: Mapped[str | None] = mapped_column(
        String(512),
    )

    valid_from: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    valid_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    certificate_valid: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    self_signed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    expired: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    # ============================================================
    # Security Features
    # ============================================================

    hsts_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    ocsp_stapling: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    alpn_supported: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    sni_supported: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    session_resumption: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    # ============================================================
    # Assessment
    # ============================================================

    grade: Mapped[TLSGrade | None] = mapped_column(
        Enum(TLSGrade),
    )

    score: Mapped[float | None] = mapped_column(
        Float,
    )

    # ============================================================
    # Relationships
    # ============================================================

    scan = relationship(
        "Scan",
        back_populates="tls_results",
    )
        # ============================================================
    # Helper Properties
    # ============================================================

    @property
    def supports_modern_tls(self) -> bool:
        """
        Returns True if TLS 1.2 or TLS 1.3 is supported.
        """
        return self.tls12_supported or self.tls13_supported

    @property
    def supports_legacy_tls(self) -> bool:
        """
        Returns True if legacy protocols are enabled.
        """
        return (
            self.ssl2_supported
            or self.ssl3_supported
            or self.tls10_supported
            or self.tls11_supported
        )

    @property
    def certificate_expired(self) -> bool:
        """
        Returns True if the certificate has expired.
        """

        if self.valid_until is None:
            return False

        return datetime.utcnow() > self.valid_until

    @property
    def certificate_days_remaining(self) -> int | None:
        """
        Number of days until certificate expiration.
        """

        if self.valid_until is None:
            return None

        return (self.valid_until - datetime.utcnow()).days

    @property
    def pqc_ready(self) -> bool:
        """
        Conservative PQC readiness heuristic.

        True when only modern TLS is enabled, forward secrecy is
        available, and no legacy protocols are exposed.
        """

        return (
            self.tls13_supported
            and self.forward_secrecy
            and not self.supports_legacy_tls
        )

    # ============================================================
    # Assessment Helpers
    # ============================================================

    def calculate_grade(self) -> None:
        """
        Simple grading heuristic.

        Intended as a baseline. Production deployments can replace this
        with a more comprehensive grading engine.
        """

        if (
            self.supports_legacy_tls
            or self.self_signed
            or self.certificate_expired
        ):
            self.grade = TLSGrade.C

        elif (
            self.tls13_supported
            and self.forward_secrecy
            and self.certificate_valid
        ):
            self.grade = TLSGrade.A

        elif self.tls12_supported:
            self.grade = TLSGrade.B

        else:
            self.grade = TLSGrade.D

    # ============================================================
    # Serialization
    # ============================================================

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "scan_id": str(self.scan_id),
            "hostname": self.hostname,
            "ip_address": self.ip_address,
            "port": self.port,
            "ssl2_supported": self.ssl2_supported,
            "ssl3_supported": self.ssl3_supported,
            "tls10_supported": self.tls10_supported,
            "tls11_supported": self.tls11_supported,
            "tls12_supported": self.tls12_supported,
            "tls13_supported": self.tls13_supported,
            "preferred_cipher": self.preferred_cipher,
            "key_exchange": self.key_exchange,
            "signature_algorithm": self.signature_algorithm,
            "key_size": self.key_size,
            "forward_secrecy": self.forward_secrecy,
            "certificate_subject": self.certificate_subject,
            "certificate_issuer": self.certificate_issuer,
            "valid_from": (
                self.valid_from.isoformat()
                if self.valid_from
                else None
            ),
            "valid_until": (
                self.valid_until.isoformat()
                if self.valid_until
                else None
            ),
            "certificate_valid": self.certificate_valid,
            "self_signed": self.self_signed,
            "expired": self.expired,
            "hsts_enabled": self.hsts_enabled,
            "ocsp_stapling": self.ocsp_stapling,
            "alpn_supported": self.alpn_supported,
            "sni_supported": self.sni_supported,
            "session_resumption": self.session_resumption,
            "grade": (
                self.grade.value
                if self.grade
                else None
            ),
            "score": self.score,
            "pqc_ready": self.pqc_ready,
            "certificate_days_remaining": (
                self.certificate_days_remaining
            ),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    # ============================================================
    # Representation
    # ============================================================

    def __repr__(self) -> str:
        return (
            "<TLSResult("
            f"id={self.id}, "
            f"host='{self.hostname}', "
            f"port={self.port}, "
            f"grade='{self.grade.value if self.grade else None}'"
            ")>"
        )