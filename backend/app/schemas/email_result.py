"""
QShield Enterprise
==================

Email Result Schemas

Pydantic schemas representing email security assessment results.

Compatible with Pydantic v2.
"""

from __future__ import annotations

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


class SMTPEncryption(str, Enum):
    """
    SMTP transport encryption.
    """

    NONE = "NONE"
    STARTTLS = "STARTTLS"
    SMTPS = "SMTPS"


class SPFPolicy(str, Enum):
    """
    SPF policy.
    """

    PASS = "PASS"
    SOFTFAIL = "SOFTFAIL"
    FAIL = "FAIL"
    NEUTRAL = "NEUTRAL"
    NONE = "NONE"


class DMARCPolicy(str, Enum):
    """
    DMARC enforcement policy.
    """

    NONE = "none"
    QUARANTINE = "quarantine"
    REJECT = "reject"


# ============================================================
# MX Records
# ============================================================


class MXServer(BaseSchema):
    """
    Mail exchanger.
    """

    hostname: str

    priority: int

    ipv4_addresses: list[str] = Field(
        default_factory=list,
    )

    ipv6_addresses: list[str] = Field(
        default_factory=list,
    )

    supports_starttls: bool = False

    encryption: SMTPEncryption = (
        SMTPEncryption.NONE
    )

    response_time_ms: float | None = None


# ============================================================
# SMTP Information
# ============================================================


class SMTPServerInformation(BaseSchema):
    """
    SMTP server information.
    """

    banner: str | None = None

    software: str | None = None

    version: str | None = None

    tls_version: str | None = None

    cipher_suite: str | None = None


class SMTPCapabilities(BaseSchema):
    """
    SMTP EHLO capabilities.
    """

    pipelining: bool = False

    size: bool = False

    starttls: bool = False

    auth: bool = False

    chunking: bool = False

    dsn: bool = False

    smtp_utf8: bool = False

    eight_bit_mime: bool = False


# ============================================================
# Base
# ============================================================


class EmailResultBase(BaseSchema):
    """
    Shared email result fields.
    """

    asset_id: UUID

    scan_id: UUID

    domain: str

    mx_servers: list[MXServer] = Field(
        default_factory=list,
    )

    smtp_information: SMTPServerInformation

    smtp_capabilities: SMTPCapabilities
    # ============================================================
# SPF
# ============================================================


class EmailSPFResult(BaseSchema):
    """
    SPF evaluation.
    """

    present: bool = False

    valid: bool = False

    record: str | None = None

    policy: SPFPolicy = SPFPolicy.NONE

    lookup_count: int = 0

    exceeds_lookup_limit: bool = False

    includes: list[str] = Field(
        default_factory=list,
    )


# ============================================================
# DKIM
# ============================================================


class DKIMSelector(BaseSchema):
    """
    DKIM selector details.
    """

    selector: str

    present: bool = False

    valid: bool = False

    algorithm: str | None = None

    key_size: int | None = None


class EmailDKIMResult(BaseSchema):
    """
    DKIM evaluation.
    """

    enabled: bool = False

    selectors: list[DKIMSelector] = Field(
        default_factory=list,
    )


# ============================================================
# DMARC
# ============================================================


class EmailDMARCResult(BaseSchema):
    """
    DMARC evaluation.
    """

    present: bool = False

    valid: bool = False

    policy: DMARCPolicy = DMARCPolicy.NONE

    percentage: int = 100

    rua: list[str] = Field(
        default_factory=list,
    )

    ruf: list[str] = Field(
        default_factory=list,
    )

    adkim: str | None = None

    aspf: str | None = None


# ============================================================
# MTA-STS
# ============================================================


class MTASTSResult(BaseSchema):
    """
    MTA-STS configuration.
    """

    present: bool = False

    valid: bool = False

    mode: str | None = None

    max_age: int | None = None

    mx_patterns: list[str] = Field(
        default_factory=list,
    )


# ============================================================
# TLS-RPT
# ============================================================


class TLSRPTResult(BaseSchema):
    """
    SMTP TLS reporting.
    """

    present: bool = False

    valid: bool = False

    report_uris: list[str] = Field(
        default_factory=list,
    )


# ============================================================
# BIMI
# ============================================================


class BIMIResult(BaseSchema):
    """
    BIMI configuration.
    """

    present: bool = False

    valid: bool = False

    logo_url: str | None = None

    authority_certificate: str | None = None


# ============================================================
# Relay Test
# ============================================================


class OpenRelayTest(BaseSchema):
    """
    Open relay assessment.
    """

    tested: bool = False

    vulnerable: bool = False

    accepted_external_relay: bool = False

    notes: str | None = None


# ============================================================
# STARTTLS
# ============================================================


class STARTTLSValidation(BaseSchema):
    """
    STARTTLS validation.
    """

    supported: bool = False

    negotiated: bool = False

    tls_version: str | None = None

    cipher_suite: str | None = None

    certificate_valid: bool = False

    forward_secrecy: bool = False
    # ============================================================
# Security Score
# ============================================================


class EmailSecurityScore(BaseSchema):
    """
    Overall email security posture.
    """

    score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    grade: str | None = None

    missing_controls: list[str] = Field(
        default_factory=list,
    )

    weak_configurations: list[str] = Field(
        default_factory=list,
    )


# ============================================================
# Domain Reputation
# ============================================================


class DomainReputation(BaseSchema):
    """
    Domain reputation summary.
    """

    score: int | None = None

    blacklisted: bool = False

    blacklist_sources: list[str] = Field(
        default_factory=list,
    )

    disposable_domain: bool = False

    parked_domain: bool = False


# ============================================================
# Vulnerabilities
# ============================================================


class EmailVulnerability(BaseSchema):
    """
    Email security finding.
    """

    id: str

    title: str

    severity: str

    description: str

    affected_component: str | None = None

    remediation: str | None = None


# ============================================================
# Recommendations
# ============================================================


class EmailRecommendation(BaseSchema):
    """
    Recommended remediation.
    """

    title: str

    description: str

    priority: str

    automated_fix_available: bool = False


# ============================================================
# Response
# ============================================================


class EmailResultResponse(
    UUIDTimestampSchema,
    EmailResultBase,
):
    """
    Standard email security response.
    """

    spf: EmailSPFResult

    dkim: EmailDKIMResult

    dmarc: EmailDMARCResult

    mta_sts: MTASTSResult | None = None

    tls_rpt: TLSRPTResult | None = None

    bimi: BIMIResult | None = None

    relay_test: OpenRelayTest

    starttls: STARTTLSValidation

    security_score: EmailSecurityScore

    reputation: DomainReputation

    vulnerabilities: list[
        EmailVulnerability
    ] = Field(default_factory=list)

    recommendations: list[
        EmailRecommendation
    ] = Field(default_factory=list)


# ============================================================
# Detail
# ============================================================


class EmailResultDetail(
    EmailResultResponse
):
    """
    Detailed email security analysis.
    """

    smtp_transcript: list[str] = Field(
        default_factory=list,
    )

    dns_records: dict[str, list[str]] = Field(
        default_factory=dict,
    )

    metadata: dict[str, str] = Field(
        default_factory=dict,
    )
    # ============================================================
# Authentication Statistics
# ============================================================


class EmailAuthenticationStatistics(BaseSchema):
    """
    Email authentication adoption metrics.
    """

    spf_enabled: int = 0

    dkim_enabled: int = 0

    dmarc_enabled: int = 0

    dmarc_reject_policy: int = 0

    mta_sts_enabled: int = 0

    tls_rpt_enabled: int = 0

    bimi_enabled: int = 0


# ============================================================
# STARTTLS Statistics
# ============================================================


class STARTTLSStatistics(BaseSchema):
    """
    STARTTLS deployment statistics.
    """

    supported: int = 0

    negotiated: int = 0

    valid_certificates: int = 0

    invalid_certificates: int = 0

    forward_secrecy_enabled: int = 0


# ============================================================
# Statistics
# ============================================================


class EmailStatistics(BaseSchema):
    """
    Aggregate email security statistics.
    """

    total_domains: int = 0

    average_security_score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    authentication: EmailAuthenticationStatistics

    starttls: STARTTLSStatistics

    open_relays: int = 0

    blacklisted_domains: int = 0


# ============================================================
# Dashboard
# ============================================================


class EmailDashboard(BaseSchema):
    """
    Email security dashboard.
    """

    statistics: EmailStatistics

    highest_scores: list[
        EmailResultResponse
    ] = Field(default_factory=list)

    lowest_scores: list[
        EmailResultResponse
    ] = Field(default_factory=list)

    vulnerable_domains: list[
        EmailResultResponse
    ] = Field(default_factory=list)

    open_relay_hosts: list[
        EmailResultResponse
    ] = Field(default_factory=list)


# ============================================================
# Export
# ============================================================


class EmailExportResponse(BaseSchema):
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


class EmailListResponse(BaseSchema):
    """
    Paginated email security assessment results.
    """

    results: list[
        EmailResultResponse
    ] = Field(default_factory=list)

    total: int

    page: int = 1

    page_size: int = 25

    total_pages: int = 1


# ============================================================
# End of File
# ============================================================