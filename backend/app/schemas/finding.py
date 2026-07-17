"""
QShield Enterprise
==================

Finding Schemas

Pydantic schemas for vulnerability findings.

Compatible with Pydantic v2.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import (
    Field,
    field_validator,
)

from app.schemas.base import (
    BaseSchema,
    UUIDTimestampSchema,
)

# ============================================================
# Enumerations
# ============================================================


class FindingSeverity(str, Enum):
    """
    Finding severity.
    """

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class FindingStatus(str, Enum):
    """
    Lifecycle state.
    """

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ACCEPTED = "accepted"
    FALSE_POSITIVE = "false_positive"
    SUPPRESSED = "suppressed"


class FindingCategory(str, Enum):
    """
    Finding category.
    """

    TLS = "tls"
    CERTIFICATE = "certificate"
    DNS = "dns"
    HTTP = "http"
    COOKIE = "cookie"
    EMAIL = "email"
    TECHNOLOGY = "technology"
    PQC = "pqc"
    COMPLIANCE = "compliance"
    CONFIGURATION = "configuration"
    NETWORK = "network"
    OTHER = "other"


class RiskRating(str, Enum):
    """
    Business risk.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================================
# CVSS
# ============================================================


class CVSSMetrics(BaseSchema):
    """
    CVSS metrics.
    """

    version: str = "3.1"

    vector: str | None = None

    base_score: float = Field(
        default=0,
        ge=0,
        le=10,
    )

    temporal_score: float | None = Field(
        default=None,
        ge=0,
        le=10,
    )

    environmental_score: float | None = Field(
        default=None,
        ge=0,
        le=10,
    )


# ============================================================
# CWE
# ============================================================


class CWEReference(BaseSchema):
    """
    CWE mapping.
    """

    id: int

    name: str

    url: str | None = None


# ============================================================
# CVE
# ============================================================


class CVEReference(BaseSchema):
    """
    CVE mapping.
    """

    id: str

    description: str | None = None

    cvss_score: float | None = None

    published_at: datetime | None = None


# ============================================================
# Base
# ============================================================


class FindingBase(BaseSchema):
    """
    Shared finding fields.
    """

    asset_id: UUID

    scan_id: UUID

    title: str = Field(
        ...,
        min_length=3,
        max_length=300,
    )

    description: str

    severity: FindingSeverity

    status: FindingStatus = FindingStatus.OPEN

    category: FindingCategory

    risk: RiskRating = RiskRating.MEDIUM

    cvss: CVSSMetrics | None = None

    remediation: str | None = None

    references: list[str] = Field(
        default_factory=list,
    )

    tags: list[str] = Field(
        default_factory=list,
    )


# ============================================================
# Create
# ============================================================


class FindingCreate(FindingBase):
    """
    Create finding request.
    """

    pass


# ============================================================
# Update
# ============================================================


class FindingUpdate(BaseSchema):
    """
    Partial update.
    """

    title: str | None = Field(
        default=None,
        max_length=300,
    )

    description: str | None = None

    severity: FindingSeverity | None = None

    status: FindingStatus | None = None

    risk: RiskRating | None = None

    remediation: str | None = None

    tags: list[str] | None = None


# ============================================================
# Validators
# ============================================================


class FindingValidators:

    @staticmethod
    def normalize_tags(
        tags: list[str],
    ) -> list[str]:
        normalized: list[str] = []

        for tag in tags:
            tag = tag.strip().lower()

            if tag and tag not in normalized:
                normalized.append(tag)

        return normalized


class FindingCreateValidated(FindingCreate):

    @field_validator("tags")
    @classmethod
    def validate_tags(
        cls,
        value: list[str],
    ):
        return FindingValidators.normalize_tags(value)
    # ============================================================
# Supporting Response Models
# ============================================================


class FindingAssetSummary(BaseSchema):
    """
    Minimal asset information.
    """

    id: UUID

    name: str

    value: str

    asset_type: str


class FindingScanSummary(BaseSchema):
    """
    Minimal scan information.
    """

    id: UUID

    scan_type: str

    started_at: datetime | None = None

    completed_at: datetime | None = None


class FindingRiskScore(BaseSchema):
    """
    Risk scoring details.
    """

    score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    exploitability: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    impact: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    confidence: float = Field(
        default=100,
        ge=0,
        le=100,
    )


class FindingAIRecommendationSummary(BaseSchema):
    """
    AI recommendation reference.
    """

    id: UUID

    title: str

    confidence: float = Field(
        ge=0,
        le=100,
    )


# ============================================================
# Summary
# ============================================================


class FindingSummary(UUIDTimestampSchema):
    """
    Lightweight finding representation.
    """

    asset_id: UUID

    scan_id: UUID

    title: str

    severity: FindingSeverity

    status: FindingStatus

    category: FindingCategory

    risk: RiskRating

    risk_score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    first_seen: datetime | None = None

    last_seen: datetime | None = None


# ============================================================
# Response
# ============================================================


class FindingResponse(
    UUIDTimestampSchema,
    FindingBase,
):
    """
    Standard finding response.
    """

    risk_score: FindingRiskScore

    asset: FindingAssetSummary

    scan: FindingScanSummary

    first_seen: datetime | None = None

    last_seen: datetime | None = None

    resolved_at: datetime | None = None

    ai_recommendation_id: UUID | None = None


# ============================================================
# Detail
# ============================================================


class FindingDetail(FindingResponse):
    """
    Detailed finding response.
    """

    cwe: list[CWEReference] = Field(
        default_factory=list,
    )

    cve: list[CVEReference] = Field(
        default_factory=list,
    )

    ai_recommendation: (
        FindingAIRecommendationSummary | None
    ) = None

    related_findings: list[UUID] = Field(
        default_factory=list,
    )

    duplicate_of: UUID | None = None

    supersedes: UUID | None = None

    metadata: dict[str, str] = Field(
        default_factory=dict,
    )
    # ============================================================
# Comment Models
# ============================================================


class FindingCommentCreate(BaseSchema):
    """
    Create a new finding comment.
    """

    comment: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )


class FindingCommentResponse(UUIDTimestampSchema):
    """
    Finding comment.
    """

    finding_id: UUID

    user_id: UUID

    username: str

    comment: str

    edited: bool = False

    edited_at: datetime | None = None


# ============================================================
# Evidence Models
# ============================================================


class FindingEvidenceResponse(UUIDTimestampSchema):
    """
    Supporting evidence.
    """

    finding_id: UUID

    evidence_type: str

    title: str

    description: str | None = None

    filename: str | None = None

    mime_type: str | None = None

    size_bytes: int | None = None

    checksum: str | None = None

    storage_path: str | None = None


# ============================================================
# History Models
# ============================================================


class FindingHistoryResponse(UUIDTimestampSchema):
    """
    Finding audit history.
    """

    finding_id: UUID

    user_id: UUID | None = None

    username: str | None = None

    action: str

    field: str | None = None

    old_value: str | None = None

    new_value: str | None = None

    reason: str | None = None


# ============================================================
# References
# ============================================================


class FindingReferenceResponse(UUIDTimestampSchema):
    """
    External reference.
    """

    finding_id: UUID

    title: str

    url: str

    reference_type: str | None = None


# ============================================================
# Exception
# ============================================================


class FindingExceptionCreate(BaseSchema):
    """
    Create an exception request.
    """

    reason: str = Field(
        ...,
        min_length=5,
        max_length=5000,
    )

    expires_at: datetime | None = None


class FindingExceptionResponse(UUIDTimestampSchema):
    """
    Exception details.
    """

    finding_id: UUID

    approved_by: UUID | None = None

    reason: str

    expires_at: datetime | None = None

    active: bool


# ============================================================
# Assignment
# ============================================================


class FindingAssignment(BaseSchema):
    """
    Assign finding ownership.
    """

    assignee_id: UUID | None = None


# ============================================================
# Status Update
# ============================================================


class FindingStatusUpdate(BaseSchema):
    """
    Update finding status.
    """

    status: FindingStatus

    reason: str | None = None


# ============================================================
# Severity Update
# ============================================================


class FindingSeverityUpdate(BaseSchema):
    """
    Override severity.
    """

    severity: FindingSeverity

    justification: str | None = None


# ============================================================
# Bulk Update
# ============================================================


class FindingBulkUpdate(BaseSchema):
    """
    Bulk update multiple findings.
    """

    finding_ids: list[UUID] = Field(
        min_length=1,
    )

    status: FindingStatus | None = None

    severity: FindingSeverity | None = None

    risk: RiskRating | None = None

    assignee_id: UUID | None = None

    tags: list[str] | None = None


class FindingBulkUpdateResponse(BaseSchema):
    """
    Bulk operation result.
    """

    processed: int

    updated: int

    failed: int

    errors: list[str] = Field(
        default_factory=list,
    )
    # ============================================================
# Statistics
# ============================================================


class FindingStatistics(BaseSchema):
    """
    Aggregate finding statistics.
    """

    total_findings: int = 0

    open_findings: int = 0

    in_progress_findings: int = 0

    resolved_findings: int = 0

    accepted_findings: int = 0

    false_positive_findings: int = 0

    suppressed_findings: int = 0

    average_risk_score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    average_cvss_score: float = Field(
        default=0,
        ge=0,
        le=10,
    )

    mean_time_to_resolution_days: float = 0

    findings_last_24_hours: int = 0

    findings_last_7_days: int = 0

    findings_last_30_days: int = 0


# ============================================================
# Distribution Models
# ============================================================


class SeverityDistribution(BaseSchema):
    """
    Distribution by severity.
    """

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    informational: int = 0


class StatusDistribution(BaseSchema):
    """
    Distribution by status.
    """

    open: int = 0
    in_progress: int = 0
    resolved: int = 0
    accepted: int = 0
    false_positive: int = 0
    suppressed: int = 0


class CategoryDistribution(BaseSchema):
    """
    Distribution by category.
    """

    categories: dict[str, int] = Field(
        default_factory=dict,
    )


class RiskDistribution(BaseSchema):
    """
    Distribution by business risk.
    """

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0


# ============================================================
# Trend Models
# ============================================================


class FindingTrendPoint(BaseSchema):
    """
    Time-series data point.
    """

    timestamp: datetime

    created: int = 0

    resolved: int = 0

    active: int = 0


class FindingTrend(BaseSchema):
    """
    Finding trend.
    """

    period: str

    points: list[FindingTrendPoint] = Field(
        default_factory=list,
    )


# ============================================================
# Search / Filters
# ============================================================


class FindingFilter(BaseSchema):
    """
    Search and filter criteria.
    """

    asset_id: UUID | None = None

    scan_id: UUID | None = None

    severity: FindingSeverity | None = None

    status: FindingStatus | None = None

    category: FindingCategory | None = None

    risk: RiskRating | None = None

    assignee_id: UUID | None = None

    discovered_after: datetime | None = None

    discovered_before: datetime | None = None

    tag: str | None = None

    search: str | None = None


# ============================================================
# Dashboard
# ============================================================


class FindingDashboard(BaseSchema):
    """
    Dashboard payload.
    """

    statistics: FindingStatistics

    severity_distribution: SeverityDistribution

    status_distribution: StatusDistribution

    category_distribution: CategoryDistribution

    risk_distribution: RiskDistribution

    trend: FindingTrend

    newest_findings: list[FindingSummary] = Field(
        default_factory=list,
    )

    critical_findings: list[FindingSummary] = Field(
        default_factory=list,
    )


# ============================================================
# Analytics
# ============================================================


class FindingAnalytics(BaseSchema):
    """
    Full analytics payload.
    """

    dashboard: FindingDashboard

    top_assets: dict[str, int] = Field(
        default_factory=dict,
    )

    top_categories: dict[str, int] = Field(
        default_factory=dict,
    )

    remediation_rate: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    recurrence_rate: float = Field(
        default=0,
        ge=0,
        le=100,
    )
    # ============================================================
# Timeline
# ============================================================


class FindingTimelineEvent(BaseSchema):
    """
    Timeline event for a finding.
    """

    timestamp: datetime

    event: str

    actor: str | None = None

    message: str

    metadata: dict[str, str] = Field(
        default_factory=dict,
    )


class FindingTimeline(BaseSchema):
    """
    Complete lifecycle timeline.
    """

    finding_id: UUID

    events: list[FindingTimelineEvent] = Field(
        default_factory=list,
    )


# ============================================================
# Remediation
# ============================================================


class FindingRemediationSummary(BaseSchema):
    """
    Remediation overview.
    """

    remediation: str

    estimated_effort: str | None = None

    priority: RiskRating

    automation_available: bool = False

    references: list[str] = Field(
        default_factory=list,
    )


# ============================================================
# Notification
# ============================================================


class FindingNotification(BaseSchema):
    """
    Notification payload.
    """

    finding_id: UUID

    title: str

    severity: FindingSeverity

    status: FindingStatus

    recipients: list[str] = Field(
        default_factory=list,
    )

    sent_at: datetime | None = None


# ============================================================
# Search Response
# ============================================================


class FindingSearchResponse(BaseSchema):
    """
    Search results.
    """

    query: str

    total_matches: int

    findings: list[FindingSummary] = Field(
        default_factory=list,
    )


# ============================================================
# Export
# ============================================================


class FindingExportResponse(BaseSchema):
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


class FindingListResponse(BaseSchema):
    """
    Paginated finding collection.
    """

    findings: list[FindingSummary] = Field(
        default_factory=list,
    )

    total: int

    page: int = 1

    page_size: int = 25

    total_pages: int = 1


# ============================================================
# Dashboard Widgets
# ============================================================


class FindingOverviewWidget(BaseSchema):
    """
    Dashboard overview widget.
    """

    critical_open: int = 0

    high_open: int = 0

    sla_breaches: int = 0

    newly_discovered_today: int = 0

    resolved_today: int = 0


class FindingActivityWidget(BaseSchema):
    """
    Recent activity widget.
    """

    recent_comments: int = 0

    recent_status_changes: int = 0

    recent_exceptions: int = 0

    recent_assignments: int = 0


# ============================================================
# End of File
# ============================================================
