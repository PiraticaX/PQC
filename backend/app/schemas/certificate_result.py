"""
QShield Enterprise
==================

Certificate Result Schemas

Pydantic schemas representing X.509 certificate analysis.

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


class SignatureAlgorithm(str, Enum):
    """
    Certificate signature algorithm.
    """

    RSA_SHA1 = "RSA-SHA1"
    RSA_SHA256 = "RSA-SHA256"
    RSA_SHA384 = "RSA-SHA384"
    RSA_SHA512 = "RSA-SHA512"

    ECDSA_SHA256 = "ECDSA-SHA256"
    ECDSA_SHA384 = "ECDSA-SHA384"
    ECDSA_SHA512 = "ECDSA-SHA512"

    ED25519 = "ED25519"
    UNKNOWN = "UNKNOWN"


class PublicKeyAlgorithm(str, Enum):
    """
    Public key algorithm.
    """

    RSA = "RSA"
    EC = "EC"
    ED25519 = "ED25519"
    ED448 = "ED448"
    DSA = "DSA"
    UNKNOWN = "UNKNOWN"


# ============================================================
# Subject / Issuer
# ============================================================


class DistinguishedName(BaseSchema):
    """
    X.509 Distinguished Name.
    """

    common_name: str | None = None

    organization: str | None = None

    organizational_unit: str | None = None

    locality: str | None = None

    state: str | None = None

    country: str | None = None


# ============================================================
# Subject Alternative Names
# ============================================================


class SubjectAlternativeNames(BaseSchema):
    """
    Subject Alternative Names.
    """

    dns_names: list[str] = Field(
        default_factory=list,
    )

    ip_addresses: list[str] = Field(
        default_factory=list,
    )

    email_addresses: list[str] = Field(
        default_factory=list,
    )

    uris: list[str] = Field(
        default_factory=list,
    )


# ============================================================
# Public Key
# ============================================================


class PublicKeyInformation(BaseSchema):
    """
    Public key details.
    """

    algorithm: PublicKeyAlgorithm

    key_size: int

    curve: str | None = None

    exponent: int | None = None

    fingerprint_sha256: str | None = None


# ============================================================
# Key Usage
# ============================================================


class KeyUsage(BaseSchema):
    """
    X.509 key usage extension.
    """

    digital_signature: bool = False

    key_encipherment: bool = False

    key_agreement: bool = False

    data_encipherment: bool = False

    key_cert_sign: bool = False

    crl_sign: bool = False


class ExtendedKeyUsage(BaseSchema):
    """
    Extended key usage extension.
    """

    server_auth: bool = False

    client_auth: bool = False

    code_signing: bool = False

    email_protection: bool = False

    time_stamping: bool = False

    ocsp_signing: bool = False


# ============================================================
# Base
# ============================================================


class CertificateResultBase(BaseSchema):
    """
    Shared certificate result fields.
    """

    asset_id: UUID

    scan_id: UUID

    hostname: str

    serial_number: str

    version: int = 3

    subject: DistinguishedName

    issuer: DistinguishedName

    signature_algorithm: SignatureAlgorithm

    public_key: PublicKeyInformation

    valid_from: datetime

    valid_until: datetime

    # ============================================================
# Certificate Chain
# ============================================================


class CertificateChainEntry(BaseSchema):
    """
    Certificate chain element.
    """

    position: int

    subject: DistinguishedName

    issuer: DistinguishedName

    serial_number: str

    is_root: bool = False

    is_intermediate: bool = False

    trusted: bool = True


class CertificateChainValidation(BaseSchema):
    """
    Chain validation results.
    """

    valid: bool = True

    complete: bool = True

    trusted_root: bool = True

    path_length: int = 0

    errors: list[str] = Field(
        default_factory=list,
    )


# ============================================================
# Revocation
# ============================================================


class RevocationStatus(BaseSchema):
    """
    OCSP / CRL status.
    """

    ocsp_supported: bool = False

    ocsp_status: str | None = None

    crl_available: bool = False

    revoked: bool = False

    checked_at: datetime | None = None


# ============================================================
# Certificate Transparency
# ============================================================


class CertificateTransparency(BaseSchema):
    """
    Certificate Transparency information.
    """

    logged: bool = False

    log_count: int = 0

    logs: list[str] = Field(
        default_factory=list,
    )


# ============================================================
# Vulnerabilities
# ============================================================


class CertificateVulnerability(BaseSchema):
    """
    Certificate issue detected.
    """

    id: str

    title: str

    severity: str

    description: str

    remediation: str | None = None


# ============================================================
# Recommendations
# ============================================================


class CertificateRecommendation(BaseSchema):
    """
    Recommended improvement.
    """

    title: str

    description: str

    priority: str

    automated_fix_available: bool = False


# ============================================================
# Response
# ============================================================


class CertificateResultResponse(
    UUIDTimestampSchema,
    CertificateResultBase,
):
    """
    Standard certificate response.
    """

    san: SubjectAlternativeNames

    key_usage: KeyUsage

    extended_key_usage: ExtendedKeyUsage

    chain_validation: CertificateChainValidation

    revocation_status: RevocationStatus

    transparency: CertificateTransparency

    expires_in_days: int

    self_signed: bool = False

    expired: bool = False

    weak_signature_algorithm: bool = False

    weak_public_key: bool = False

    vulnerabilities: list[
        CertificateVulnerability
    ] = Field(default_factory=list)

    recommendations: list[
        CertificateRecommendation
    ] = Field(default_factory=list)


# ============================================================
# Detail
# ============================================================


class CertificateResultDetail(
    CertificateResultResponse
):
    """
    Detailed certificate response.
    """

    chain: list[
        CertificateChainEntry
    ] = Field(default_factory=list)

    fingerprint_sha1: str | None = None

    fingerprint_sha256: str | None = None

    fingerprint_sha512: str | None = None

    pem: str | None = None

    metadata: dict[str, str] = Field(
        default_factory=dict,
    )

    # ============================================================
# Expiration Summary
# ============================================================


class CertificateExpirationSummary(BaseSchema):
    """
    Certificate expiration overview.
    """

    expired: int = 0

    expires_within_7_days: int = 0

    expires_within_30_days: int = 0

    expires_within_90_days: int = 0

    valid: int = 0


# ============================================================
# Statistics
# ============================================================


class CertificateStatistics(BaseSchema):
    """
    Aggregate certificate statistics.
    """

    total_certificates: int = 0

    average_validity_days: float = 0

    self_signed: int = 0

    trusted: int = 0

    untrusted: int = 0

    weak_keys: int = 0

    weak_signatures: int = 0

    expiration: CertificateExpirationSummary


# ============================================================
# Dashboard
# ============================================================


class CertificateDashboard(BaseSchema):
    """
    Certificate dashboard.
    """

    statistics: CertificateStatistics

    expiring_soon: list[
        CertificateResultResponse
    ] = Field(default_factory=list)

    expired_certificates: list[
        CertificateResultResponse
    ] = Field(default_factory=list)

    self_signed_certificates: list[
        CertificateResultResponse
    ] = Field(default_factory=list)


# ============================================================
# Export
# ============================================================


class CertificateExportResponse(BaseSchema):
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


class CertificateListResponse(BaseSchema):
    """
    Paginated certificate results.
    """

    results: list[
        CertificateResultResponse
    ] = Field(default_factory=list)

    total: int

    page: int = 1

    page_size: int = 25

    total_pages: int = 1


# ============================================================
# End of File
# ============================================================