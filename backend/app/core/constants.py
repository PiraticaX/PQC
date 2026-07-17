"""
QShield Enterprise
==================

Application-wide constants.

Do NOT hardcode strings or numeric values throughout the codebase.
Everything shared across multiple modules should live here.

This file intentionally contains no business logic.
"""

from __future__ import annotations

from enum import Enum


# ============================================================================
# Application
# ============================================================================

APP_VENDOR = "QShield"

DEFAULT_USER_AGENT = (
    "QShield Enterprise Security Scanner "
    "(Authorized Defensive Assessment Platform)"
)


# ============================================================================
# Asset Status
# ============================================================================


class AssetStatus(str, Enum):
    """
    Current lifecycle state of an asset.
    """

    PENDING = "pending"

    QUEUED = "queued"

    SCANNING = "scanning"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"


# ============================================================================
# Scan Status
# ============================================================================


class ScanStatus(str, Enum):
    """
    Scan execution state.
    """

    PENDING = "pending"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    PARTIAL = "partial"

    CANCELLED = "cancelled"


# ============================================================================
# Finding Severity
# ============================================================================


class Severity(str, Enum):
    """
    Finding severity.

    Numerical values are intentionally not stored here.
    The scoring engine maps these to weights.
    """

    CRITICAL = "critical"

    HIGH = "high"

    MEDIUM = "medium"

    LOW = "low"

    INFORMATIONAL = "informational"


# ============================================================================
# Overall Risk
# ============================================================================


class RiskLevel(str, Enum):
    """
    Overall organizational risk.
    """

    CRITICAL = "critical"

    HIGH = "high"

    MEDIUM = "medium"

    LOW = "low"

    MINIMAL = "minimal"


# ============================================================================
# Scanner Names
# ============================================================================

SCANNER_TLS = "tls"

SCANNER_CERTIFICATE = "certificate"

SCANNER_HTTP = "http"

SCANNER_DNS = "dns"

SCANNER_EMAIL = "email"

SCANNER_PQC = "pqc"

SCANNER_TECHNOLOGY = "technology"

SCANNER_CLOUD = "cloud"

SCANNER_AI = "ai"

ALL_SCANNERS = (
    SCANNER_TLS,
    SCANNER_CERTIFICATE,
    SCANNER_HTTP,
    SCANNER_DNS,
    SCANNER_EMAIL,
    SCANNER_PQC,
    SCANNER_TECHNOLOGY,
    SCANNER_CLOUD,
)


# ============================================================================
# TLS
# ============================================================================

SUPPORTED_TLS = (
    "TLSv1.3",
)

LEGACY_TLS = (
    "TLSv1",
    "TLSv1.1",
    "TLSv1.2",
)

INSECURE_TLS = (
    "SSLv2",
    "SSLv3",
)

# Cipher keywords that should be considered legacy.
WEAK_CIPHER_KEYWORDS = (
    "RSA",
    "3DES",
    "DES",
    "RC2",
    "RC4",
    "NULL",
    "EXPORT",
    "MD5",
)


# ============================================================================
# HTTP Security Headers
# ============================================================================

RECOMMENDED_SECURITY_HEADERS = {
    "strict-transport-security": "Enable HSTS with a long max-age.",
    "content-security-policy": "Deploy a restrictive Content Security Policy.",
    "x-content-type-options": "Set X-Content-Type-Options: nosniff.",
    "x-frame-options": "Protect against clickjacking.",
    "referrer-policy": "Control referrer leakage.",
    "permissions-policy": "Restrict browser capabilities.",
    "cross-origin-opener-policy": "Enable process isolation.",
    "cross-origin-embedder-policy": "Protect embedded resources.",
    "cross-origin-resource-policy": "Restrict cross-origin access.",
}


# ============================================================================
# Secure Cookie Attributes
# ============================================================================

COOKIE_FLAGS = (
    "Secure",
    "HttpOnly",
    "SameSite",
)


# ============================================================================
# DNS
# ============================================================================

DNS_RECORD_TYPES = (
    "A",
    "AAAA",
    "CAA",
    "CNAME",
    "MX",
    "NS",
    "SOA",
    "TXT",
)


# ============================================================================
# PQC Algorithms
# ============================================================================

SUPPORTED_PQC_KEMS = (
    "ML-KEM-512",
    "ML-KEM-768",
    "ML-KEM-1024",
)

SUPPORTED_PQC_SIGNATURES = (
    "ML-DSA-44",
    "ML-DSA-65",
    "ML-DSA-87",
    "SLH-DSA",
)


# ============================================================================
# Classical Algorithms
# ============================================================================

CLASSICAL_KEY_EXCHANGE = (
    "RSA",
    "DH",
    "ECDH",
    "ECDHE",
    "X25519",
)

CLASSICAL_SIGNATURES = (
    "RSA",
    "ECDSA",
    "Ed25519",
)


# ============================================================================
# Compliance Frameworks
# ============================================================================

COMPLIANCE = (
    "OWASP ASVS",
    "OWASP Top 10",
    "NIST CSF",
    "NIST PQC",
    "PCI DSS",
    "ISO 27001",
    "CIS Controls",
)


# ============================================================================
# Scoring Categories
# ============================================================================

CATEGORY_TLS = "tls"

CATEGORY_CERTIFICATE = "certificate"

CATEGORY_HTTP = "http"

CATEGORY_DNS = "dns"

CATEGORY_EMAIL = "email"

CATEGORY_PQC = "pqc"

CATEGORY_TECHNOLOGY = "technology"

CATEGORY_CLOUD = "cloud"


# ============================================================================
# Score Weights
# Total = 100
# ============================================================================

DEFAULT_SCORE_WEIGHTS = {
    CATEGORY_TLS: 25,
    CATEGORY_CERTIFICATE: 15,
    CATEGORY_HTTP: 15,
    CATEGORY_DNS: 15,
    CATEGORY_EMAIL: 10,
    CATEGORY_PQC: 20,
}


# ============================================================================
# Default Timeouts
# ============================================================================

NETWORK_TIMEOUT = 15

DNS_TIMEOUT = 5

TLS_TIMEOUT = 10

HTTP_TIMEOUT = 15


# ============================================================================
# Report Types
# ============================================================================

REPORT_EXECUTIVE = "executive"

REPORT_TECHNICAL = "technical"

REPORT_JSON = "json"

REPORT_CSV = "csv"

REPORT_PDF = "pdf"


# ============================================================================
# Finding Types
# ============================================================================

FINDING_CONFIGURATION = "configuration"

FINDING_CRYPTOGRAPHY = "cryptography"

FINDING_CERTIFICATE = "certificate"

FINDING_DNS = "dns"

FINDING_HTTP = "http"

FINDING_EMAIL = "email"

FINDING_PQC = "post_quantum"

FINDING_INFORMATION = "information"


# ============================================================================
# Default Recommendation
# ============================================================================

DEFAULT_PQC_RECOMMENDATION = (
    "Adopt hybrid cryptography using X25519 + ML-KEM-768 for key "
    "establishment and ML-DSA-65 for digital signatures where supported."
)