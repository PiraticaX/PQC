"""
QShield Enterprise
==================

DNS Result Model

Stores DNS assessment results discovered during a scan.

A single scan may generate multiple DNSResult records for different
hostnames or zones.
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


class DNSResult(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    """
    DNS assessment for a hostname or DNS zone.
    """

    __tablename__ = "dns_results"

    __table_args__ = (
        Index("idx_dns_scan", "scan_id"),
        Index("idx_dns_hostname", "hostname"),
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

    hostname: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    zone: Mapped[str | None] = mapped_column(
        String(255),
    )

    # ============================================================
    # DNS Records
    # ============================================================

    a_records: Mapped[str | None] = mapped_column(
        Text,
    )

    aaaa_records: Mapped[str | None] = mapped_column(
        Text,
    )

    cname_records: Mapped[str | None] = mapped_column(
        Text,
    )

    mx_records: Mapped[str | None] = mapped_column(
        Text,
    )

    txt_records: Mapped[str | None] = mapped_column(
        Text,
    )

    ns_records: Mapped[str | None] = mapped_column(
        Text,
    )

    soa_record: Mapped[str | None] = mapped_column(
        Text,
    )

    ptr_records: Mapped[str | None] = mapped_column(
        Text,
    )

    caa_records: Mapped[str | None] = mapped_column(
        Text,
    )

    # ============================================================
    # Security
    # ============================================================

    dnssec_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    zone_transfer_allowed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    recursion_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    wildcard_dns: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    # ============================================================
    # Email Security
    # ============================================================

    spf_record: Mapped[str | None] = mapped_column(
        Text,
    )

    spf_valid: Mapped[bool] = mapped_column(
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

    dkim_selector: Mapped[str | None] = mapped_column(
        String(255),
    )

    dkim_valid: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    # ============================================================
    # Metadata
    # ============================================================

    ttl: Mapped[int | None] = mapped_column(
        Integer,
    )

    authoritative: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    # ============================================================
    # Relationships
    # ============================================================

    scan = relationship(
        "Scan",
        back_populates="dns_results",
    )
        # ============================================================
    # Record Helpers
    # ============================================================

    @staticmethod
    def _parse_records(records: str | None) -> list[str]:
        """
        Parse a comma-separated record list.
        """

        if not records:
            return []

        return sorted(
            {
                record.strip()
                for record in records.split(",")
                if record.strip()
            }
        )

    @property
    def a_record_list(self) -> list[str]:
        return self._parse_records(self.a_records)

    @property
    def aaaa_record_list(self) -> list[str]:
        return self._parse_records(self.aaaa_records)

    @property
    def cname_record_list(self) -> list[str]:
        return self._parse_records(self.cname_records)

    @property
    def mx_record_list(self) -> list[str]:
        return self._parse_records(self.mx_records)

    @property
    def ns_record_list(self) -> list[str]:
        return self._parse_records(self.ns_records)

    @property
    def txt_record_list(self) -> list[str]:
        return self._parse_records(self.txt_records)

    @property
    def caa_record_list(self) -> list[str]:
        return self._parse_records(self.caa_records)

    # ============================================================
    # Security Helpers
    # ============================================================

    @property
    def email_security_enabled(self) -> bool:
        """
        Returns True when SPF, DKIM and DMARC all validate.
        """

        return (
            self.spf_valid
            and self.dkim_valid
            and self.dmarc_valid
        )

    @property
    def has_dns_risk(self) -> bool:
        """
        Returns True if common DNS security issues are detected.
        """

        return (
            self.zone_transfer_allowed
            or self.recursion_enabled
            or not self.dnssec_enabled
        )

    # ============================================================
    # Serialization
    # ============================================================

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "scan_id": str(self.scan_id),
            "hostname": self.hostname,
            "zone": self.zone,
            "a_records": self.a_record_list,
            "aaaa_records": self.aaaa_record_list,
            "cname_records": self.cname_record_list,
            "mx_records": self.mx_record_list,
            "txt_records": self.txt_record_list,
            "ns_records": self.ns_record_list,
            "soa_record": self.soa_record,
            "ptr_records": self._parse_records(self.ptr_records),
            "caa_records": self.caa_record_list,
            "dnssec_enabled": self.dnssec_enabled,
            "zone_transfer_allowed": self.zone_transfer_allowed,
            "recursion_enabled": self.recursion_enabled,
            "wildcard_dns": self.wildcard_dns,
            "spf_record": self.spf_record,
            "spf_valid": self.spf_valid,
            "dmarc_record": self.dmarc_record,
            "dmarc_valid": self.dmarc_valid,
            "dkim_selector": self.dkim_selector,
            "dkim_valid": self.dkim_valid,
            "email_security_enabled": self.email_security_enabled,
            "ttl": self.ttl,
            "authoritative": self.authoritative,
            "has_dns_risk": self.has_dns_risk,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    # ============================================================
    # Representation
    # ============================================================

    def __repr__(self) -> str:
        return (
            "<DNSResult("
            f"id={self.id}, "
            f"hostname='{self.hostname}'"
            ")>"
        )