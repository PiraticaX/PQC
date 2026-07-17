"""
QShield Enterprise
==================

Cookie Result Schemas

Pydantic schemas representing HTTP cookie security analysis.

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


class SameSitePolicy(str, Enum):
    """
    SameSite attribute.
    """

    STRICT = "Strict"
    LAX = "Lax"
    NONE = "None"
    UNSPECIFIED = "Unspecified"


class CookiePriority(str, Enum):
    """
    Cookie Priority attribute.
    """

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    UNSPECIFIED = "Unspecified"


class CookieClassification(str, Enum):
    """
    Cookie purpose classification.
    """

    SESSION = "Session"
    PERSISTENT = "Persistent"
    AUTHENTICATION = "Authentication"
    ANALYTICS = "Analytics"
    TRACKING = "Tracking"
    ADVERTISING = "Advertising"
    FUNCTIONAL = "Functional"
    UNKNOWN = "Unknown"


# ============================================================
# Cookie Model
# ============================================================


class Cookie(BaseSchema):
    """
    HTTP cookie.
    """

    name: str

    value: str | None = None

    domain: str

    path: str

    secure: bool = False

    http_only: bool = False

    same_site: SameSitePolicy = SameSitePolicy.UNSPECIFIED

    priority: CookiePriority = CookiePriority.UNSPECIFIED

    partitioned: bool = False

    host_only: bool = False

    persistent: bool = False

    classification: CookieClassification = (
        CookieClassification.UNKNOWN
    )

    expires_at: datetime | None = None

    max_age: int | None = None

    size_bytes: int | None = None


# ============================================================
# Expiration
# ============================================================


class CookieExpiration(BaseSchema):
    """
    Cookie lifetime information.
    """

    session_cookie: bool = False

    expires_at: datetime | None = None

    max_age: int | None = None

    expired: bool = False

    expires_in_days: int | None = None


# ============================================================
# Base
# ============================================================


class CookieResultBase(BaseSchema):
    """
    Shared cookie result fields.
    """

    asset_id: UUID

    scan_id: UUID

    hostname: str

    url: str

    total_cookies: int = 0

    # ============================================================
# Cookie Security Analysis
# ============================================================


class CookieSecurityAnalysis(BaseSchema):
    """
    Aggregate cookie security analysis.
    """

    secure_cookies: int = 0

    insecure_cookies: int = 0

    http_only_cookies: int = 0

    missing_http_only: int = 0

    missing_secure: int = 0

    same_site_strict: int = 0

    same_site_lax: int = 0

    same_site_none: int = 0

    same_site_unspecified: int = 0

    persistent_cookies: int = 0

    session_cookies: int = 0

    partitioned_cookies: int = 0


# ============================================================
# Vulnerabilities
# ============================================================


class CookieVulnerability(BaseSchema):
    """
    Cookie security finding.
    """

    id: str

    title: str

    severity: str

    description: str

    cookie_name: str | None = None

    remediation: str | None = None


# ============================================================
# Recommendations
# ============================================================


class CookieRecommendation(BaseSchema):
    """
    Cookie security recommendation.
    """

    title: str

    description: str

    priority: str

    automated_fix_available: bool = False


# ============================================================
# Response
# ============================================================


class CookieResultResponse(
    UUIDTimestampSchema,
    CookieResultBase,
):
    """
    Standard cookie scan response.
    """

    cookies: list[Cookie] = Field(
        default_factory=list,
    )

    analysis: CookieSecurityAnalysis

    vulnerabilities: list[
        CookieVulnerability
    ] = Field(default_factory=list)

    recommendations: list[
        CookieRecommendation
    ] = Field(default_factory=list)


# ============================================================
# Detail
# ============================================================


class CookieResultDetail(
    CookieResultResponse
):
    """
    Detailed cookie analysis.
    """

    cookie_expirations: list[
        CookieExpiration
    ] = Field(default_factory=list)

    raw_set_cookie_headers: list[str] = Field(
        default_factory=list,
    )

    metadata: dict[str, str] = Field(
        default_factory=dict,
    )

    # ============================================================
# SameSite Distribution
# ============================================================


class SameSiteDistribution(BaseSchema):
    """
    Distribution of SameSite cookie policies.
    """

    strict: int = 0

    lax: int = 0

    none: int = 0

    unspecified: int = 0


# ============================================================
# Cookie Classification Distribution
# ============================================================


class CookieClassificationDistribution(BaseSchema):
    """
    Distribution of cookie classifications.
    """

    session: int = 0

    persistent: int = 0

    authentication: int = 0

    analytics: int = 0

    tracking: int = 0

    advertising: int = 0

    functional: int = 0

    unknown: int = 0


# ============================================================
# Statistics
# ============================================================


class CookieStatistics(BaseSchema):
    """
    Aggregate cookie statistics.
    """

    total_hosts: int = 0

    total_cookies: int = 0

    average_cookies_per_host: float = 0

    secure_cookie_percentage: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    http_only_percentage: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    same_site_distribution: SameSiteDistribution

    classification_distribution: (
        CookieClassificationDistribution
    )


# ============================================================
# Dashboard
# ============================================================


class CookieDashboard(BaseSchema):
    """
    Cookie security dashboard.
    """

    statistics: CookieStatistics

    most_vulnerable_hosts: list[
        CookieResultResponse
    ] = Field(default_factory=list)

    hosts_missing_secure: list[
        CookieResultResponse
    ] = Field(default_factory=list)

    hosts_missing_http_only: list[
        CookieResultResponse
    ] = Field(default_factory=list)


# ============================================================
# Export
# ============================================================


class CookieExportResponse(BaseSchema):
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


class CookieListResponse(BaseSchema):
    """
    Paginated cookie scan results.
    """

    results: list[
        CookieResultResponse
    ] = Field(default_factory=list)

    total: int

    page: int = 1

    page_size: int = 25

    total_pages: int = 1


# ============================================================
# End of File
# ============================================================