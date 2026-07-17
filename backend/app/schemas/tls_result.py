"""
QShield Enterprise
==================

TLS Result Schemas

Pydantic schemas representing TLS scan results.

Compatible with Pydantic v2.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import Field

from app.schemas.base import (
    BaseSchema,
    UUIDTimestampSchema,
)

# ============================================================
# Enumerations
# ============================================================


class TLSProtocol(str, Enum):
    """
    Supported TLS/SSL protocol versions.
    """

    SSL2 = "SSLv2"
    SSL3 = "SSLv3"
    TLS10 = "TLS1.0"
    TLS11 = "TLS1.1"
    TLS12 = "TLS1.2"
    TLS13 = "TLS1.3"


class CipherStrength(str, Enum):
    """
    Cipher classification.
    """

    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"
    UNKNOWN = "unknown"


class ForwardSecrecyStatus(str, Enum):
    """
    Forward secrecy state.
    """

    ENABLED = "enabled"
    PARTIAL = "partial"
    DISABLED = "disabled"


# ============================================================
# Cipher Suite
# ============================================================


class CipherSuite(BaseSchema):
    """
    Supported cipher suite.
    """

    name: str

    protocol: TLSProtocol

    strength: CipherStrength

    key_length: int | None = None

    forward_secrecy: bool = False

    preferred: bool = False


# ============================================================
# Key Exchange
# ============================================================


class KeyExchange(BaseSchema):
    """
    Key exchange parameters.
    """

    algorithm: str

    key_size: int | None = None

    curve: str | None = None


# ============================================================
# Forward Secrecy
# ============================================================


class ForwardSecrecy(BaseSchema):
    """
    Forward secrecy information.
    """

    status: ForwardSecrecyStatus

    supported_groups: list[str] = Field(
        default_factory=list,
    )


# ============================================================
# Certificate Chain
# ============================================================


class CertificateChain(BaseSchema):
    """
    Certificate chain entry.
    """

    subject: str

    issuer: str

    serial_number: str

    signature_algorithm: str

    valid_from: datetime

    valid_until: datetime

    self_signed: bool = False


# ============================================================
# TLS Configuration
# ============================================================


class TLSConfiguration(BaseSchema):
    """
    TLS configuration snapshot.
    """

    hostname: str

    port: int = 443

    supported_protocols: list[TLSProtocol] = Field(
        default_factory=list,
    )

    cipher_suites: list[CipherSuite] = Field(
        default_factory=list,
    )

    key_exchange: KeyExchange | None = None

    forward_secrecy: ForwardSecrecy | None = None

    certificate_chain: list[CertificateChain] = Field(
        default_factory=list,
    )


# ============================================================
# Base
# ============================================================


class TLSResultBase(BaseSchema):
    """
    Shared TLS result fields.
    """

    asset_id: UUID

    scan_id: UUID

    hostname: str

    port: int = Field(
        default=443,
        ge=1,
        le=65535,
    )

    overall_grade: str | None = None

    score: float = Field(
        default=0,
        ge=0,
        le=100,
    )
    # ============================================================
# Vulnerability
# ============================================================


class TLSVulnerability(BaseSchema):
    """
    TLS-related vulnerability detected during the scan.
    """

    id: str

    name: str

    severity: str

    description: str

    affected_component: str | None = None

    cve: str | None = None

    cwe: str | None = None

    remediation: str | None = None


# ============================================================
# Recommendation
# ============================================================


class TLSRecommendation(BaseSchema):
    """
    Recommended TLS improvement.
    """

    title: str

    priority: str

    description: str

    automated_fix_available: bool = False


# ============================================================
# Summary
# ============================================================


class TLSResultSummary(UUIDTimestampSchema):
    """
    Lightweight TLS result.
    """

    asset_id: UUID

    scan_id: UUID

    hostname: str

    port: int

    overall_grade: str | None = None

    score: float = Field(
        default=0,
        ge=0,
        le=100,
    )


# ============================================================
# Response
# ============================================================


class TLSResultResponse(
    UUIDTimestampSchema,
    TLSResultBase,
):
    """
    Standard TLS scan response.
    """

    configuration: TLSConfiguration

    vulnerabilities: list[TLSVulnerability] = Field(
        default_factory=list,
    )

    recommendations: list[TLSRecommendation] = Field(
        default_factory=list,
    )

    certificate_valid: bool = True

    hostname_matches_certificate: bool = True

    supports_ocsp_stapling: bool = False

    supports_alpn: bool = False

    supports_hsts: bool = False

    scan_duration_seconds: float | None = None


# ============================================================
# Detail
# ============================================================


class TLSResultDetail(TLSResultResponse):
    """
    Detailed TLS result.
    """

    negotiated_protocol: TLSProtocol | None = None

    negotiated_cipher: CipherSuite | None = None

    supported_alpn_protocols: list[str] = Field(
        default_factory=list,
    )

    supported_signature_algorithms: list[str] = Field(
        default_factory=list,
    )

    supported_groups: list[str] = Field(
        default_factory=list,
    )

    session_resumption_supported: bool = False

    secure_renegotiation_supported: bool = True

    compression_enabled: bool = False

    heartbeat_supported: bool = False

    metadata: dict[str, str] = Field(
        default_factory=dict,
    )
    # ============================================================
# Protocol Statistics
# ============================================================


class TLSProtocolSupport(BaseSchema):
    """
    Protocol support summary.
    """

    ssl2: int = 0
    ssl3: int = 0
    tls10: int = 0
    tls11: int = 0
    tls12: int = 0
    tls13: int = 0


# ============================================================
# Cipher Statistics
# ============================================================


class TLSCipherStatistics(BaseSchema):
    """
    Cipher strength summary.
    """

    weak: int = 0

    medium: int = 0

    strong: int = 0

    unknown: int = 0

    forward_secrecy_enabled: int = 0


# ============================================================
# Statistics
# ============================================================


class TLSStatistics(BaseSchema):
    """
    Aggregate TLS statistics.
    """

    total_hosts: int = 0

    average_score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    average_grade: str | None = None

    valid_certificates: int = 0

    expired_certificates: int = 0

    self_signed_certificates: int = 0

    protocol_support: TLSProtocolSupport

    cipher_statistics: TLSCipherStatistics


# ============================================================
# Dashboard
# ============================================================


class TLSDashboard(BaseSchema):
    """
    TLS dashboard payload.
    """

    statistics: TLSStatistics

    highest_scores: list[TLSResultSummary] = Field(
        default_factory=list,
    )

    lowest_scores: list[TLSResultSummary] = Field(
        default_factory=list,
    )

    vulnerable_hosts: list[TLSResultSummary] = Field(
        default_factory=list,
    )


# ============================================================
# Export
# ============================================================


class TLSExportResponse(BaseSchema):
    """
    Export metadata.
    """

    filename: str

    format: str

    generated_at: datetime

    total_records: int

    download_url: str | None = None


# ============================================================
# List Response
# ============================================================


class TLSListResponse(BaseSchema):
    """
    Paginated TLS results.
    """

    results: list[TLSResultSummary] = Field(
        default_factory=list,
    )

    total: int

    page: int = 1

    page_size: int = 25

    total_pages: int = 1


# ============================================================
# End of File
# ============================================================
