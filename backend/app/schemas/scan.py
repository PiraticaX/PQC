"""
QShield Enterprise
==================

Scan Schemas

Pydantic schemas for scan management.

Compatible with Pydantic v2.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.base import BaseSchema, UUIDTimestampSchema


# ============================================================
# Enumerations
# ============================================================


class ScanType(str, Enum):
    """
    Supported scan types.
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
    FULL = "full"


class ScanStatus(str, Enum):
    """
    Scan lifecycle state.
    """

    QUEUED = "queued"
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ScanPriority(str, Enum):
    """
    Scan priority.
    """

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class ScanTrigger(str, Enum):
    """
    How a scan was initiated.
    """

    MANUAL = "manual"
    SCHEDULED = "scheduled"
    API = "api"
    WEBHOOK = "webhook"
    SYSTEM = "system"


# ============================================================
# Base
# ============================================================


class ScanBase(BaseSchema):
    """
    Shared scan fields.
    """

    asset_id: UUID

    scan_type: ScanType

    priority: ScanPriority = ScanPriority.NORMAL

    trigger: ScanTrigger = ScanTrigger.MANUAL

    profile: str | None = Field(
        default=None,
        max_length=100,
    )

    configuration: dict[str, str] = Field(
        default_factory=dict,
    )

    notes: str | None = Field(
        default=None,
        max_length=5000,
    )


# ============================================================
# Create
# ============================================================


class ScanCreate(ScanBase):
    """
    Request to create a new scan.
    """

    start_immediately: bool = True


# ============================================================
# Update
# ============================================================


class ScanUpdate(BaseSchema):
    """
    Update mutable scan fields.
    """

    priority: ScanPriority | None = None

    notes: str | None = Field(
        default=None,
        max_length=5000,
    )

    configuration: dict[str, str] | None = None


# ============================================================
# Run Request
# ============================================================


class ScanRunRequest(BaseSchema):
    """
    Execute one or more scans.
    """

    asset_ids: list[UUID] = Field(
        min_length=1,
    )

    scan_types: list[ScanType] = Field(
        min_length=1,
    )

    priority: ScanPriority = ScanPriority.NORMAL

    trigger: ScanTrigger = ScanTrigger.MANUAL

    start_immediately: bool = True


# ============================================================
# Cancel
# ============================================================


class ScanCancelRequest(BaseSchema):
    """
    Cancel one or more scans.
    """

    scan_ids: list[UUID] = Field(
        min_length=1,
    )

    reason: str | None = Field(
        default=None,
        max_length=1000,
    )


# ============================================================
# Retry
# ============================================================


class ScanRetryRequest(BaseSchema):
    """
    Retry failed scans.
    """

    scan_ids: list[UUID] = Field(
        min_length=1,
    )

    priority: ScanPriority = ScanPriority.NORMAL


# ============================================================
# Validators
# ============================================================


class ScanConfigurationValidator:
    """
    Shared configuration validation.
    """

    @staticmethod
    def validate_configuration(
        value: dict[str, str],
    ) -> dict[str, str]:
        if len(value) > 100:
            raise ValueError(
                "Configuration contains too many entries."
            )

        return value


@field_validator("configuration")
@classmethod
def validate_configuration(
    cls,
    value: dict[str, str],
):
    return ScanConfigurationValidator.validate_configuration(
        value
    )
# ============================================================
# Progress
# ============================================================


class ScanProgress(BaseSchema):
    """
    Real-time scan progress.
    """

    current_step: str | None = None

    completed_steps: int = 0

    total_steps: int = 0

    percentage: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    message: str | None = None


# ============================================================
# Execution Metadata
# ============================================================


class ScanExecution(BaseSchema):
    """
    Execution information.
    """

    worker_id: str | None = None

    queue_name: str | None = None

    executor: str | None = None

    backend: str | None = None

    retry_count: int = 0

    max_retries: int = 3

    timeout_seconds: int | None = None


# ============================================================
# Timing
# ============================================================


class ScanTiming(BaseSchema):
    """
    Scan timing information.
    """

    queued_at: datetime | None = None

    started_at: datetime | None = None

    completed_at: datetime | None = None

    duration_seconds: float | None = None

    queue_wait_seconds: float | None = None


# ============================================================
# Summary
# ============================================================


class ScanSummary(UUIDTimestampSchema):
    """
    Lightweight scan representation.
    """

    asset_id: UUID

    scan_type: ScanType

    status: ScanStatus

    priority: ScanPriority

    trigger: ScanTrigger

    progress: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    started_at: datetime | None = None

    completed_at: datetime | None = None


# ============================================================
# Response
# ============================================================


class ScanResponse(
    UUIDTimestampSchema,
    ScanBase,
):
    """
    Standard scan response.
    """

    status: ScanStatus

    progress: ScanProgress

    execution: ScanExecution

    timing: ScanTiming

    finding_count: int = 0

    result_count: int = 0

    error_message: str | None = None


# ============================================================
# Detail
# ============================================================


class ScanDetail(ScanResponse):
    """
    Detailed scan response.
    """

    findings: list[UUID] = Field(
        default_factory=list,
    )

    result_ids: list[UUID] = Field(
        default_factory=list,
    )

    logs: list[str] = Field(
        default_factory=list,
    )

    metadata: dict[str, str] = Field(
        default_factory=dict,
    )

from pydantic import Field

# ============================================================
# Statistics
# ============================================================


class ScanStatistics(BaseSchema):
    """
    Aggregate scan statistics.
    """

    total_scans: int = 0

    queued: int = 0

    running: int = 0

    completed: int = 0

    failed: int = 0

    cancelled: int = 0

    timeout: int = 0

    success_rate: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    average_duration_seconds: float = 0

    findings_discovered: int = 0

    assets_scanned: int = 0


# ============================================================
# Queue Statistics
# ============================================================


class ScanQueueStatistics(BaseSchema):
    """
    Queue metrics.
    """

    queue_name: str

    pending_jobs: int = 0

    running_jobs: int = 0

    completed_today: int = 0

    failed_today: int = 0

    average_wait_seconds: float = 0


# ============================================================
# Worker Statistics
# ============================================================


class ScanWorkerStatistics(BaseSchema):
    """
    Worker metrics.
    """

    worker_id: str

    hostname: str

    active_jobs: int = 0

    completed_jobs: int = 0

    failed_jobs: int = 0

    cpu_percent: float = 0

    memory_percent: float = 0

    uptime_seconds: int = 0


# ============================================================
# Bulk Operations
# ============================================================


class ScanBulkRunRequest(BaseSchema):
    """
    Launch scans for multiple assets.
    """

    asset_ids: list[UUID] = Field(
        min_length=1,
    )

    scan_types: list[ScanType] = Field(
        min_length=1,
    )

    priority: ScanPriority = ScanPriority.NORMAL


class ScanBulkCancelRequest(BaseSchema):
    """
    Cancel multiple scans.
    """

    scan_ids: list[UUID] = Field(
        min_length=1,
    )


class ScanBulkRetryRequest(BaseSchema):
    """
    Retry multiple scans.
    """

    scan_ids: list[UUID] = Field(
        min_length=1,
    )


class ScanBulkOperationResponse(BaseSchema):
    """
    Bulk operation result.
    """

    processed: int

    successful: int

    failed: int

    errors: list[str] = Field(
        default_factory=list,
    )


# ============================================================
# Search / Filters
# ============================================================


class ScanFilter(BaseSchema):
    """
    Scan filtering options.
    """

    asset_id: UUID | None = None

    scan_type: ScanType | None = None

    status: ScanStatus | None = None

    priority: ScanPriority | None = None

    trigger: ScanTrigger | None = None

    started_after: datetime | None = None

    started_before: datetime | None = None


# ============================================================
# History
# ============================================================


class ScanHistoryEntry(BaseSchema):
    """
    Historical scan entry.
    """

    id: UUID

    started_at: datetime | None = None

    completed_at: datetime | None = None

    status: ScanStatus

    findings: int = 0

    duration_seconds: float | None = None


# ============================================================
# Analytics
# ============================================================


class ScanAnalytics(BaseSchema):
    """
    Scan analytics dashboard.
    """

    statistics: ScanStatistics

    queues: list[ScanQueueStatistics] = Field(
        default_factory=list,
    )

    workers: list[ScanWorkerStatistics] = Field(
        default_factory=list,
    )

    recent_scans: list[ScanSummary] = Field(
        default_factory=list,
    )

    slowest_scans: list[ScanSummary] = Field(
        default_factory=list,
    )

    failed_scans: list[ScanSummary] = Field(
        default_factory=list,
    )
    # ============================================================
# Timeline
# ============================================================


class ScanTimelineEvent(BaseSchema):
    """
    Timeline event generated during scan execution.
    """

    timestamp: datetime

    event: str

    level: str = "info"

    message: str

    source: str | None = None


class ScanTimeline(BaseSchema):
    """
    Complete execution timeline.
    """

    scan_id: UUID

    events: list[ScanTimelineEvent] = Field(
        default_factory=list,
    )


# ============================================================
# Dashboard
# ============================================================


class ScanDashboard(BaseSchema):
    """
    Dashboard payload.
    """

    statistics: ScanStatistics

    running_scans: list[ScanSummary] = Field(
        default_factory=list,
    )

    queued_scans: list[ScanSummary] = Field(
        default_factory=list,
    )

    recent_scans: list[ScanSummary] = Field(
        default_factory=list,
    )

    failed_scans: list[ScanSummary] = Field(
        default_factory=list,
    )


# ============================================================
# Export
# ============================================================


class ScanExportResponse(BaseSchema):
    """
    Scan export metadata.
    """

    filename: str

    format: str

    generated_at: datetime

    total_records: int

    download_url: str | None = None


# ============================================================
# Health
# ============================================================


class ScanHealth(BaseSchema):
    """
    Scan engine health.
    """

    scheduler_running: bool

    workers_online: int

    queues_online: int

    pending_jobs: int

    running_jobs: int

    failed_jobs_last_hour: int

    average_queue_wait_seconds: float

    average_scan_duration_seconds: float


# ============================================================
# Schedule Summary
# ============================================================


class ScanScheduleSummary(BaseSchema):
    """
    Scheduled scan overview.
    """

    scheduled_scan_id: UUID

    asset_id: UUID

    asset_name: str

    scan_type: ScanType

    next_run: datetime | None = None

    last_run: datetime | None = None

    enabled: bool = True


# ============================================================
# List Response
# ============================================================


class ScanListResponse(BaseSchema):
    """
    Paginated scan collection.
    """

    scans: list[ScanSummary] = Field(
        default_factory=list,
    )

    total: int

    page: int = 1

    page_size: int = 25

    total_pages: int = 1


# ============================================================
# Recent Activity
# ============================================================


class ScanRecentActivity(BaseSchema):
    """
    Recent scan activity.
    """

    started_last_hour: int = 0

    completed_last_hour: int = 0

    failed_last_hour: int = 0

    average_duration_last_hour: float = 0

    newest_scans: list[ScanSummary] = Field(
        default_factory=list,
    )


# ============================================================
# End of File
# ============================================================