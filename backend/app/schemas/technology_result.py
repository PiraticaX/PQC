"""
QShield Enterprise
==================

Technology Result Schemas

Pydantic schemas representing detected technologies,
fingerprints and software inventory.

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


class TechnologyCategory(str, Enum):
    """
    Technology classification.
    """

    WEB_SERVER = "WEB_SERVER"

    FRAMEWORK = "FRAMEWORK"

    CMS = "CMS"

    DATABASE = "DATABASE"

    PROGRAMMING_LANGUAGE = "PROGRAMMING_LANGUAGE"

    RUNTIME = "RUNTIME"

    OPERATING_SYSTEM = "OPERATING_SYSTEM"

    CONTAINER = "CONTAINER"

    ORCHESTRATION = "ORCHESTRATION"

    CDN = "CDN"

    WAF = "WAF"

    LOAD_BALANCER = "LOAD_BALANCER"

    REVERSE_PROXY = "REVERSE_PROXY"

    CACHE = "CACHE"

    SEARCH_ENGINE = "SEARCH_ENGINE"

    ANALYTICS = "ANALYTICS"

    AUTHENTICATION = "AUTHENTICATION"

    MESSAGE_QUEUE = "MESSAGE_QUEUE"

    API_GATEWAY = "API_GATEWAY"

    STORAGE = "STORAGE"

    SECURITY = "SECURITY"

    MONITORING = "MONITORING"

    OTHER = "OTHER"


class DetectionMethod(str, Enum):
    """
    Technology detection source.
    """

    HTTP_HEADER = "HTTP_HEADER"

    HTML = "HTML"

    META_TAG = "META_TAG"

    COOKIE = "COOKIE"

    JAVASCRIPT = "JAVASCRIPT"

    FAVICON = "FAVICON"

    TLS = "TLS"

    DNS = "DNS"

    RESPONSE_BODY = "RESPONSE_BODY"

    FINGERPRINT = "FINGERPRINT"

    API = "API"

    MANUAL = "MANUAL"


# ============================================================
# Fingerprints
# ============================================================


class TechnologyFingerprint(BaseSchema):
    """
    Evidence used to identify a technology.
    """

    method: DetectionMethod

    source: str

    matched_pattern: str

    confidence: float = Field(
        ge=0,
        le=100,
    )


# ============================================================
# CPE
# ============================================================


class CPEInformation(BaseSchema):
    """
    Common Platform Enumeration.
    """

    cpe23: str

    vendor: str

    product: str

    version: str | None = None


# ============================================================
# Version Information
# ============================================================


class VersionInformation(BaseSchema):
    """
    Software version information.
    """

    detected_version: str | None = None

    latest_version: str | None = None

    supported: bool | None = None

    end_of_life: bool = False

    confidence: float = Field(
        default=100,
        ge=0,
        le=100,
    )


# ============================================================
# Base
# ============================================================


class TechnologyResultBase(BaseSchema):
    """
    Shared technology result fields.
    """

    asset_id: UUID

    scan_id: UUID

    hostname: str

    url: str | None = None
    # ============================================================
# CVE Mapping
# ============================================================


class CVEMapping(BaseSchema):
    """
    CVE associated with a detected technology.
    """

    cve_id: str

    cvss_score: float | None = Field(
        default=None,
        ge=0,
        le=10,
    )

    severity: str

    published_date: datetime | None = None

    description: str

    fixed_version: str | None = None

    reference_urls: list[str] = Field(
        default_factory=list,
    )


# ============================================================
# End-of-Life Analysis
# ============================================================


class EndOfLifeAnalysis(BaseSchema):
    """
    Product lifecycle information.
    """

    supported: bool = True

    end_of_life: bool = False

    end_of_support_date: datetime | None = None

    latest_supported_version: str | None = None

    upgrade_recommended: bool = False

    recommendation: str | None = None


# ============================================================
# Technology
# ============================================================


class Technology(BaseSchema):
    """
    Detected technology.
    """

    name: str

    vendor: str | None = None

    category: TechnologyCategory

    version: VersionInformation

    cpe: CPEInformation | None = None

    fingerprints: list[
        TechnologyFingerprint
    ] = Field(default_factory=list)

    end_of_life: EndOfLifeAnalysis | None = None

    cves: list[CVEMapping] = Field(
        default_factory=list,
    )


# ============================================================
# Technology Group
# ============================================================


class TechnologyGroup(BaseSchema):
    """
    Technologies grouped by category.
    """

    category: TechnologyCategory

    technologies: list[
        Technology
    ] = Field(default_factory=list)


# ============================================================
# Technology Relationship
# ============================================================


class TechnologyRelationship(BaseSchema):
    """
    Relationship between technologies.
    """

    source: str

    target: str

    relationship: str

    confidence: float = Field(
        default=100,
        ge=0,
        le=100,
    )


# ============================================================
# Inventory
# ============================================================


class TechnologyInventory(BaseSchema):
    """
    Complete technology inventory.
    """

    total_detected: int = 0

    groups: list[
        TechnologyGroup
    ] = Field(default_factory=list)

    relationships: list[
        TechnologyRelationship
    ] = Field(default_factory=list)
    # ============================================================
# Risk Score
# ============================================================


class TechnologyRiskScore(BaseSchema):
    """
    Overall technology risk assessment.
    """

    score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    grade: str | None = None

    critical_cves: int = 0

    high_cves: int = 0

    medium_cves: int = 0

    low_cves: int = 0

    end_of_life_products: int = 0

    unsupported_products: int = 0


# ============================================================
# Inventory Summary
# ============================================================


class TechnologyInventorySummary(BaseSchema):
    """
    High-level technology inventory summary.
    """

    total_technologies: int = 0

    unique_vendors: int = 0

    unique_products: int = 0

    unique_categories: int = 0

    outdated_products: int = 0

    end_of_life_products: int = 0


# ============================================================
# Vulnerabilities
# ============================================================


class TechnologyVulnerability(BaseSchema):
    """
    Technology-related security finding.
    """

    id: str

    title: str

    severity: str

    technology: str

    description: str

    cve: str | None = None

    fixed_version: str | None = None

    remediation: str | None = None


# ============================================================
# Recommendations
# ============================================================


class TechnologyRecommendation(BaseSchema):
    """
    Technology remediation recommendation.
    """

    title: str

    description: str

    priority: str

    affected_technology: str | None = None

    target_version: str | None = None

    automated_fix_available: bool = False


# ============================================================
# Response
# ============================================================


class TechnologyResultResponse(
    UUIDTimestampSchema,
    TechnologyResultBase,
):
    """
    Standard technology detection response.
    """

    inventory: TechnologyInventory

    summary: TechnologyInventorySummary

    risk_score: TechnologyRiskScore

    vulnerabilities: list[
        TechnologyVulnerability
    ] = Field(default_factory=list)

    recommendations: list[
        TechnologyRecommendation
    ] = Field(default_factory=list)


# ============================================================
# Detail
# ============================================================


class TechnologyResultDetail(
    TechnologyResultResponse
):
    """
    Detailed technology inventory.
    """

    raw_headers: dict[str, str] = Field(
        default_factory=dict,
    )

    fingerprint_sources: list[str] = Field(
        default_factory=list,
    )

    detection_log: list[str] = Field(
        default_factory=list,
    )

    metadata: dict[str, str] = Field(
        default_factory=dict,
    )
    # ============================================================
# Vendor Distribution
# ============================================================


class VendorDistribution(BaseSchema):
    """
    Technology vendor distribution.
    """

    vendor: str

    count: int


# ============================================================
# Category Distribution
# ============================================================


class TechnologyCategoryDistribution(BaseSchema):
    """
    Technology category distribution.
    """

    category: TechnologyCategory

    count: int


# ============================================================
# CVE Severity Distribution
# ============================================================


class CVESeverityDistribution(BaseSchema):
    """
    Distribution of CVEs by severity.
    """

    critical: int = 0

    high: int = 0

    medium: int = 0

    low: int = 0

    informational: int = 0


# ============================================================
# Statistics
# ============================================================


class TechnologyStatistics(BaseSchema):
    """
    Aggregate technology statistics.
    """

    total_assets: int = 0

    total_technologies: int = 0

    unique_products: int = 0

    unique_vendors: int = 0

    end_of_life_products: int = 0

    unsupported_products: int = 0

    average_risk_score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    vendor_distribution: list[
        VendorDistribution
    ] = Field(default_factory=list)

    category_distribution: list[
        TechnologyCategoryDistribution
    ] = Field(default_factory=list)

    cve_distribution: CVESeverityDistribution


# ============================================================
# Dashboard
# ============================================================


class TechnologyDashboard(BaseSchema):
    """
    Technology inventory dashboard.
    """

    statistics: TechnologyStatistics

    highest_risk_assets: list[
        TechnologyResultResponse
    ] = Field(default_factory=list)

    end_of_life_assets: list[
        TechnologyResultResponse
    ] = Field(default_factory=list)

    assets_with_critical_cves: list[
        TechnologyResultResponse
    ] = Field(default_factory=list)


# ============================================================
# Export
# ============================================================


class TechnologyExportResponse(BaseSchema):
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


class TechnologyListResponse(BaseSchema):
    """
    Paginated technology inventory.
    """

    results: list[
        TechnologyResultResponse
    ] = Field(default_factory=list)

    total: int

    page: int = 1

    page_size: int = 25

    total_pages: int = 1


# ============================================================
# End of File
# ============================================================