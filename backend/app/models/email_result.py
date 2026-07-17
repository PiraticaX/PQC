"""
QShield Enterprise
==================

Email Result Model

Stores email security assessment results discovered during a scan.

One scan may produce multiple EmailResult records for different mail
servers or domains.
"""

from __future__ import annotations

import uuid

from sqlalchemy import (
    Boolean,
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


class EmailResult(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    """
    Email infrastructure assessment.
    """

    __tablename__ = "email_results"

    __table_args__ = (
        Index("idx_email_scan", "scan_id"),
        Index("idx_email_domain", "domain"),
        Index("idx_email_host", "mail_server"),
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
    # Target
    # ============================================================

    domain: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    mail_server: Mapped[str | None] = mapped_column(
        String(255),
    )

    smtp_banner: Mapped[str | None] = mapped_column(
        Text,
    )

    mx_priority: Mapped[int | None] = mapped_column(
        Integer,
    )

    # ============================================================
    # SMTP Capabilities
    # ============================================================

    smtp_available: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    starttls_supported: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    smtp_utf8_supported: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    pipelining_supported: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    auth_supported: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    open_relay: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    # ============================================================
    # Authentication
    # ============================================================

    spf_record: Mapped[str | None] = mapped_column(
        Text,
    )

    spf_valid: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    dkim_selector: Mapped[str | None] = mapped_column(
        String(255),
    )

    dkim_valid: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    dmarc_record: Mapped[str | None] = mapped_column(
        Text,
    )

    dmarc_valid: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    # ============================================================
    # Additional Protection
    # ============================================================

    mta_sts_supported: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    tls_rpt_supported: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    # ============================================================
    # TLS
    # ============================================================

    tls_version: Mapped[str | None] = mapped_column(
        String(64),
    )

    cipher_suite: Mapped[str | None] = mapped_column(
        String(255),
    )

    certificate_valid: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    # ============================================================
    # Relationships
    # ============================================================

    scan = relationship(
        "Scan",
        back_populates="email_results",
    )
        # ============================================================
    # Helper Properties
    # ============================================================

    @property
    def authentication_enabled(self) -> bool:
        """
        Returns True when the three primary email authentication
        mechanisms are correctly configured.
        """

        return (
            self.spf_valid
            and self.dkim_valid
            and self.dmarc_valid
        )

    @property
    def transport_security_enabled(self) -> bool:
        """
        Returns True when encrypted SMTP transport is properly
        configured.
        """

        return (
            self.starttls_supported
            and self.certificate_valid
        )

    @property
    def is_secure_configuration(self) -> bool:
        """
        Conservative overall email security assessment.
        """

        return (
            self.authentication_enabled
            and self.transport_security_enabled
            and self.mta_sts_supported
            and self.tls_rpt_supported
            and not self.open_relay
        )

    @property
    def risk_score(self) -> int:
        """
        Simple additive risk score.

        Higher values indicate weaker security.
        """

        score = 0

        if self.open_relay:
            score += 5

        if not self.starttls_supported:
            score += 2

        if not self.spf_valid:
            score += 1

        if not self.dkim_valid:
            score += 1

        if not self.dmarc_valid:
            score += 1

        if not self.mta_sts_supported:
            score += 1

        if not self.tls_rpt_supported:
            score += 1

        if not self.certificate_valid:
            score += 2

        return score

    # ============================================================
    # Serialization
    # ============================================================

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "scan_id": str(self.scan_id),
            "domain": self.domain,
            "mail_server": self.mail_server,
            "smtp_banner": self.smtp_banner,
            "mx_priority": self.mx_priority,
            "smtp_available": self.smtp_available,
            "starttls_supported": self.starttls_supported,
            "smtp_utf8_supported": self.smtp_utf8_supported,
            "pipelining_supported": self.pipelining_supported,
            "auth_supported": self.auth_supported,
            "open_relay": self.open_relay,
            "spf_record": self.spf_record,
            "spf_valid": self.spf_valid,
            "dkim_selector": self.dkim_selector,
            "dkim_valid": self.dkim_valid,
            "dmarc_record": self.dmarc_record,
            "dmarc_valid": self.dmarc_valid,
            "mta_sts_supported": self.mta_sts_supported,
            "tls_rpt_supported": self.tls_rpt_supported,
            "tls_version": self.tls_version,
            "cipher_suite": self.cipher_suite,
            "certificate_valid": self.certificate_valid,
            "authentication_enabled": self.authentication_enabled,
            "transport_security_enabled": self.transport_security_enabled,
            "is_secure_configuration": self.is_secure_configuration,
            "risk_score": self.risk_score,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    # ============================================================
    # Representation
    # ============================================================

    def __repr__(self) -> str:
        return (
            "<EmailResult("
            f"id={self.id}, "
            f"domain='{self.domain}', "
            f"mail_server='{self.mail_server}'"
            ")>"
        )