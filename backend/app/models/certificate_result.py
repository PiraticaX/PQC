"""
QShield Enterprise
==================

Certificate Result Model

Stores parsed X.509 certificate information.

A Scan may discover multiple certificates
(primary certificate + intermediate chain).
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


class PublicKeyAlgorithm(str, enum.Enum):
    RSA = "rsa"
    ECDSA = "ecdsa"
    ED25519 = "ed25519"
    DSA = "dsa"
    OTHER = "other"


# ============================================================
# MODEL
# ============================================================


class CertificateResult(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    """
    Parsed X.509 certificate.
    """

    __tablename__ = "certificate_results"

    __table_args__ = (
        Index("idx_cert_scan", "scan_id"),
        Index("idx_cert_serial", "serial_number"),
        Index("idx_cert_sha256", "sha256_fingerprint"),
        Index("idx_cert_expiry", "valid_until"),
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

    common_name: Mapped[str | None] = mapped_column(
        String(255),
    )

    subject: Mapped[str | None] = mapped_column(
        Text,
    )

    issuer: Mapped[str | None] = mapped_column(
        Text,
    )

    serial_number: Mapped[str | None] = mapped_column(
        String(255),
    )

    version: Mapped[int | None] = mapped_column(
        Integer,
    )

    # ============================================================
    # Validity
    # ============================================================

    valid_from: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    valid_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )

    expired: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    self_signed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    trusted: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    # ============================================================
    # Cryptography
    # ============================================================

    public_key_algorithm: Mapped[
        PublicKeyAlgorithm | None
    ] = mapped_column(
        Enum(PublicKeyAlgorithm),
    )

    public_key_size: Mapped[int | None] = mapped_column(
        Integer,
    )

    signature_algorithm: Mapped[str | None] = mapped_column(
        String(255),
    )

    curve_name: Mapped[str | None] = mapped_column(
        String(100),
    )

    # ============================================================
    # Fingerprints
    # ============================================================

    sha1_fingerprint: Mapped[str | None] = mapped_column(
        String(128),
    )

    sha256_fingerprint: Mapped[str | None] = mapped_column(
        String(128),
    )

    # ============================================================
    # Extensions
    # ============================================================

    subject_alternative_names: Mapped[str | None] = mapped_column(
        Text,
        doc="JSON or comma-separated SAN entries.",
    )

    key_usage: Mapped[str | None] = mapped_column(
        Text,
    )

    extended_key_usage: Mapped[str | None] = mapped_column(
        Text,
    )

    basic_constraints: Mapped[str | None] = mapped_column(
        Text,
    )

    authority_key_identifier: Mapped[str | None] = mapped_column(
        String(255),
    )

    subject_key_identifier: Mapped[str | None] = mapped_column(
        String(255),
    )

    # ============================================================
    # PEM
    # ============================================================

    pem: Mapped[str | None] = mapped_column(
        Text,
    )

    # ============================================================
    # Relationships
    # ============================================================

    scan = relationship(
        "Scan",
        back_populates="certificate_results",
    )
        # ============================================================
    # Helper Properties
    # ============================================================

    @property
    def is_expired(self) -> bool:
        """
        Returns True if the certificate has expired.
        """

        if self.valid_until is None:
            return False

        return datetime.utcnow() > self.valid_until

    @property
    def days_until_expiration(self) -> int | None:
        """
        Remaining validity in days.
        """

        if self.valid_until is None:
            return None

        return (self.valid_until - datetime.utcnow()).days

    @property
    def is_weak_key(self) -> bool:
        """
        Conservative key strength heuristic.
        """

        if self.public_key_size is None:
            return False

        if (
            self.public_key_algorithm
            == PublicKeyAlgorithm.RSA
        ):
            return self.public_key_size < 2048

        return False

    @property
    def san_list(self) -> list[str]:
        """
        Parse Subject Alternative Names.
        """

        if not self.subject_alternative_names:
            return []

        return sorted(
            {
                item.strip()
                for item in self.subject_alternative_names.split(",")
                if item.strip()
            }
        )

    # ============================================================
    # Trust Helpers
    # ============================================================

    def is_valid_certificate(self) -> bool:
        """
        Basic certificate validation state.
        """

        return (
            self.trusted
            and not self.is_expired
            and not self.self_signed
        )

    # ============================================================
    # Serialization
    # ============================================================

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "scan_id": str(self.scan_id),
            "common_name": self.common_name,
            "subject": self.subject,
            "issuer": self.issuer,
            "serial_number": self.serial_number,
            "version": self.version,
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
            "expired": self.expired,
            "is_expired": self.is_expired,
            "days_until_expiration": (
                self.days_until_expiration
            ),
            "self_signed": self.self_signed,
            "trusted": self.trusted,
            "public_key_algorithm": (
                self.public_key_algorithm.value
                if self.public_key_algorithm
                else None
            ),
            "public_key_size": self.public_key_size,
            "signature_algorithm": self.signature_algorithm,
            "curve_name": self.curve_name,
            "sha1_fingerprint": self.sha1_fingerprint,
            "sha256_fingerprint": self.sha256_fingerprint,
            "subject_alternative_names": self.san_list,
            "key_usage": self.key_usage,
            "extended_key_usage": self.extended_key_usage,
            "basic_constraints": self.basic_constraints,
            "authority_key_identifier": self.authority_key_identifier,
            "subject_key_identifier": self.subject_key_identifier,
            "pem": self.pem,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    # ============================================================
    # Representation
    # ============================================================

    def __repr__(self) -> str:
        return (
            "<CertificateResult("
            f"id={self.id}, "
            f"cn='{self.common_name}', "
            f"issuer='{self.issuer}'"
            ")>"
        )