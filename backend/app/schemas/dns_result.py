"""
QShield Enterprise
==================

DNS Result Schemas

Pydantic schemas representing DNS scan results.

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


class DNSRecordType(str, Enum):
    """
    Supported DNS record types.
    """

    A = "A"
    AAAA = "AAAA"
    CNAME = "CNAME"
    MX = "MX"
    TXT = "TXT"
    NS = "NS"
    SOA = "SOA"
    SRV = "SRV"
    PTR = "PTR"
    CAA = "CAA"


# ============================================================
# Record Models
# ============================================================


class ARecord(BaseSchema):
    """
    IPv4 record.
    """

    address: str

    ttl: int


class AAAARecord(BaseSchema):
    """
    IPv6 record.
    """

    address: str

    ttl: int


class CNAMERecord(BaseSchema):
    """
    Canonical name record.
    """

    target: str

    ttl: int


class MXRecord(BaseSchema):
    """
    Mail exchanger.
    """

    priority: int

    exchange: str

    ttl: int


class TXTRecord(BaseSchema):
    """
    TXT record.
    """

    value: str

    ttl: int


class NSRecord(BaseSchema):
    """
    Name server.
    """

    hostname: str

    ttl: int


class SOARecord(BaseSchema):
    """
    Start of Authority.
    """

    primary_ns: str

    responsible_party: str

    serial: int

    refresh: int

    retry: int

    expire: int

    minimum_ttl: int


class SRVRecord(BaseSchema):
    """
    Service record.
    """

    service: str

    protocol: str

    priority: int

    weight: int

    port: int

    target: str


class PTRRecord(BaseSchema):
    """
    Reverse DNS.
    """

    hostname: str


class CAARecord(BaseSchema):
    """
    Certification Authority Authorization.
    """

    flags: int

    tag: str

    value: str


# ============================================================
# DNSSEC
# ============================================================


class DNSSECStatus(BaseSchema):
    """
    DNSSEC validation.
    """

    enabled: bool = False

    validated: bool = False

    algorithm: str | None = None

    digest_algorithm: str | None = None

    key_size: int | None = None


# ============================================================
# Zone Transfer
# ============================================================


class ZoneTransferResult(BaseSchema):
    """
    AXFR test result.
    """

    attempted: bool = False

    allowed: bool = False

    server: str | None = None


# ============================================================
# Base
# ============================================================


class DNSResultBase(BaseSchema):
    """
    Shared DNS result fields.
    """

    asset_id: UUID

    scan_id: UUID

    hostname: str

    authoritative: bool = False

    recursive: bool = False

    response_time_ms: float = 0

    # ============================================================
# SPF
# ============================================================


class SPFResult(BaseSchema):
    """
    SPF validation results.
    """

    present: bool = False

    valid: bool = False

    record: str | None = None

    policy: str | None = None

    mechanisms: list[str] = Field(
        default_factory=list,
    )

    qualifiers: list[str] = Field(
        default_factory=list,
    )

    lookup_count: int = 0

    exceeds_lookup_limit: bool = False


# ============================================================
# DKIM
# ============================================================


class DKIMResult(BaseSchema):
    """
    DKIM configuration.
    """

    present: bool = False

    valid: bool = False

    selector: str | None = None

    algorithm: str | None = None

    key_size: int | None = None

    public_key: str | None = None


# ============================================================
# DMARC
# ============================================================


class DMARCResult(BaseSchema):
    """
    DMARC policy evaluation.
    """

    present: bool = False

    valid: bool = False

    policy: str | None = None

    subdomain_policy: str | None = None

    percentage: int | None = None

    rua: list[str] = Field(
        default_factory=list,
    )

    ruf: list[str] = Field(
        default_factory=list,
    )

    alignment_dkim: str | None = None

    alignment_spf: str | None = None


# ============================================================
# Vulnerabilities
# ============================================================


class DNSVulnerability(BaseSchema):
    """
    DNS security finding.
    """

    id: str

    title: str

    severity: str

    description: str

    affected_record: str | None = None

    remediation: str | None = None


# ============================================================
# Recommendations
# ============================================================


class DNSRecommendation(BaseSchema):
    """
    DNS improvement recommendation.
    """

    title: str

    description: str

    priority: str

    automated_fix_available: bool = False


# ============================================================
# Response
# ============================================================


class DNSResultResponse(
    UUIDTimestampSchema,
    DNSResultBase,
):
    """
    Standard DNS analysis response.
    """

    a_records: list[ARecord] = Field(
        default_factory=list,
    )

    aaaa_records: list[AAAARecord] = Field(
        default_factory=list,
    )

    cname_records: list[CNAMERecord] = Field(
        default_factory=list,
    )

    mx_records: list[MXRecord] = Field(
        default_factory=list,
    )

    txt_records: list[TXTRecord] = Field(
        default_factory=list,
    )

    ns_records: list[NSRecord] = Field(
        default_factory=list,
    )

    soa_record: SOARecord | None = None

    srv_records: list[SRVRecord] = Field(
        default_factory=list,
    )

    ptr_records: list[PTRRecord] = Field(
        default_factory=list,
    )

    caa_records: list[CAARecord] = Field(
        default_factory=list,
    )

    dnssec: DNSSECStatus

    zone_transfer: ZoneTransferResult

    spf: SPFResult | None = None

    dkim: DKIMResult | None = None

    dmarc: DMARCResult | None = None

    vulnerabilities: list[
        DNSVulnerability
    ] = Field(default_factory=list)

    recommendations: list[
        DNSRecommendation
    ] = Field(default_factory=list)


# ============================================================
# Detail
# ============================================================


class DNSResultDetail(
    DNSResultResponse
):
    """
    Detailed DNS analysis.
    """

    raw_response: dict[str, str] = Field(
        default_factory=dict,
    )

    metadata: dict[str, str] = Field(
        default_factory=dict,
    )

    # ============================================================
# Record Distribution
# ============================================================


class DNSRecordDistribution(BaseSchema):
    """
    Distribution of DNS record types.
    """

    a: int = 0

    aaaa: int = 0

    cname: int = 0

    mx: int = 0

    txt: int = 0

    ns: int = 0

    soa: int = 0

    srv: int = 0

    ptr: int = 0

    caa: int = 0


# ============================================================
# DNSSEC Statistics
# ============================================================


class DNSSECStatistics(BaseSchema):
    """
    DNSSEC deployment summary.
    """

    enabled: int = 0

    validated: int = 0

    unsigned: int = 0

    validation_failed: int = 0


# ============================================================
# Statistics
# ============================================================


class DNSStatistics(BaseSchema):
    """
    Aggregate DNS statistics.
    """

    total_hosts: int = 0

    average_response_time_ms: float = 0

    authoritative_servers: int = 0

    recursive_servers: int = 0

    zone_transfer_enabled: int = 0

    dnssec: DNSSECStatistics

    record_distribution: DNSRecordDistribution


# ============================================================
# Dashboard
# ============================================================


class DNSDashboard(BaseSchema):
    """
    DNS dashboard payload.
    """

    statistics: DNSStatistics

    vulnerable_hosts: list[
        DNSResultResponse
    ] = Field(default_factory=list)

    dnssec_enabled_hosts: list[
        DNSResultResponse
    ] = Field(default_factory=list)

    zone_transfer_hosts: list[
        DNSResultResponse
    ] = Field(default_factory=list)


# ============================================================
# Export
# ============================================================


class DNSExportResponse(BaseSchema):
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


class DNSListResponse(BaseSchema):
    """
    Paginated DNS analysis results.
    """

    results: list[
        DNSResultResponse
    ] = Field(default_factory=list)

    total: int

    page: int = 1

    page_size: int = 25

    total_pages: int = 1


# ============================================================
# End of File
# ============================================================