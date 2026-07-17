"""
QShield Enterprise
==================

Asset Schemas

Production-ready Pydantic v2 schemas for enterprise asset management.

This module contains:

• Asset CRUD
• Validation
• Bulk Operations
• Search
• Dashboard
• Statistics
• Import / Export

Compatible with:

- Pydantic v2
- FastAPI
- SQLAlchemy 2.0
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from ipaddress import ip_address
from ipaddress import ip_network
from urllib.parse import urlparse
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


class AssetType(str, Enum):
    """
    Asset types supported by QShield.

    NOTE:
    These values intentionally mirror the ORM model exactly.
    """

    DOMAIN = "domain"

    SUBDOMAIN = "subdomain"

    URL = "url"

    IPV4 = "ipv4"

    IPV6 = "ipv6"

    HOSTNAME = "hostname"

    CIDR = "cidr"

    VM = "vm"

    CONTAINER = "container"

    KUBERNETES = "kubernetes"

    CLOUD_RESOURCE = "cloud_resource"

    API = "api"

    EMAIL_DOMAIN = "email_domain"


class AssetStatus(str, Enum):
    """
    Asset lifecycle.
    """

    ACTIVE = "active"

    INACTIVE = "inactive"

    ARCHIVED = "archived"

    DISCOVERED = "discovered"


class Criticality(str, Enum):
    """
    Business criticality.
    """

    LOW = "low"

    MEDIUM = "medium"

    HIGH = "high"

    CRITICAL = "critical"


# ============================================================
# Base Asset
# ============================================================


class AssetBase(BaseSchema):
    """
    Shared asset fields.
    """

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    asset_type: AssetType

    value: str = Field(
        max_length=2048,
        description="Asset identifier",
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    organization_id: UUID

    asset_group_id: UUID | None = None

    owner_id: UUID | None = None

    status: AssetStatus = AssetStatus.ACTIVE

    criticality: Criticality = Criticality.MEDIUM

    tags: list[str] = Field(
        default_factory=list,
    )

    external: bool = True

    scan_enabled: bool = True


# ============================================================
# Validation Helpers
# ============================================================


class _AssetValidator:
    """
    Shared validation helpers.
    """

    @staticmethod
    def validate_ipv4(
        value: str,
    ) -> str:
        ip_address(value)
        return value

    @staticmethod
    def validate_ipv6(
        value: str,
    ) -> str:
        ip_address(value)
        return value

    @staticmethod
    def validate_cidr(
        value: str,
    ) -> str:
        ip_network(
            value,
            strict=False,
        )
        return value

    @staticmethod
    def validate_domain(
        value: str,
    ) -> str:

        value = value.strip().lower()

        if "." not in value:
            raise ValueError(
                "Invalid domain."
            )

        return value

    @staticmethod
    def validate_url(
        value: str,
    ) -> str:

        parsed = urlparse(value)

        if not parsed.scheme:
            raise ValueError(
                "URL requires scheme."
            )

        if not parsed.netloc:
            raise ValueError(
                "Invalid URL."
            )

        return value

    @staticmethod
    def normalize_tags(
        tags: list[str],
    ) -> list[str]:

        result: list[str] = []

        for tag in tags:

            tag = tag.strip().lower()

            if (
                tag
                and tag not in result
            ):
                result.append(tag)

        return sorted(result)


# ============================================================
# Create
# ============================================================


class AssetCreate(AssetBase):
    """
    Asset creation payload.
    """

    @field_validator("value")
    @classmethod
    def validate_asset_value(
        cls,
        value: str,
        info,
    ) -> str:

        asset_type = info.data.get(
            "asset_type",
        )

        if asset_type == AssetType.IPV4:
            return _AssetValidator.validate_ipv4(
                value,
            )

        if asset_type == AssetType.IPV6:
            return _AssetValidator.validate_ipv6(
                value,
            )

        if asset_type == AssetType.CIDR:
            return _AssetValidator.validate_cidr(
                value,
            )

        if asset_type == AssetType.URL:
            return _AssetValidator.validate_url(
                value,
            )

        if asset_type in (
            AssetType.DOMAIN,
            AssetType.SUBDOMAIN,
            AssetType.HOSTNAME,
        ):
            return _AssetValidator.validate_domain(
                value,
            )

        return value

    @field_validator("tags")
    @classmethod
    def validate_tags(
        cls,
        tags: list[str],
    ) -> list[str]:

        return _AssetValidator.normalize_tags(
            tags,
        )


# ============================================================
# Update
# ============================================================


class AssetUpdate(BaseSchema):
    """
    Partial update.
    """

    name: str | None = Field(
        default=None,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    asset_group_id: UUID | None = None

    owner_id: UUID | None = None

    status: AssetStatus | None = None

    criticality: Criticality | None = None

    tags: list[str] | None = None

    external: bool | None = None

    scan_enabled: bool | None = None

    @field_validator(
        "tags",
    )
    @classmethod
    def normalize_update_tags(
        cls,
        value: list[str] | None,
    ) -> list[str] | None:

        if value is None:
            return None

        return _AssetValidator.normalize_tags(
            value,
        )
    # ============================================================
# Asset Import
# ============================================================


class AssetImportRow(BaseSchema):
    """
    Single asset import record.
    """

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    asset_type: AssetType

    value: str = Field(
        min_length=1,
        max_length=2048,
    )

    description: str | None = None

    asset_group_id: UUID | None = None

    owner_id: UUID | None = None

    criticality: Criticality = (
        Criticality.MEDIUM
    )

    external: bool = True

    scan_enabled: bool = True

    tags: list[str] = Field(
        default_factory=list,
    )

    @field_validator("tags")
    @classmethod
    def normalize_tags(
        cls,
        value: list[str],
    ) -> list[str]:

        return _AssetValidator.normalize_tags(
            value,
        )


class AssetImportRequest(BaseSchema):
    """
    Bulk asset import request.
    """

    organization_id: UUID

    assets: list[AssetImportRow] = Field(
        min_length=1,
    )

    skip_duplicates: bool = True

    validate_only: bool = False


class AssetImportResult(BaseSchema):
    """
    Import summary.
    """

    total: int = 0

    imported: int = 0

    skipped: int = 0

    failed: int = 0

    errors: list[str] = Field(
        default_factory=list,
    )


# ============================================================
# Bulk Create
# ============================================================


class AssetBulkCreate(BaseSchema):
    """
    Create multiple assets.
    """

    assets: list[
        AssetCreate
    ] = Field(
        min_length=1,
    )


class AssetBulkCreateResponse(BaseSchema):
    """
    Bulk creation response.
    """

    created: int

    failed: int

    asset_ids: list[UUID] = Field(
        default_factory=list,
    )

    errors: list[str] = Field(
        default_factory=list,
    )


# ============================================================
# Bulk Delete
# ============================================================


class AssetBulkDelete(BaseSchema):
    """
    Delete multiple assets.
    """

    asset_ids: list[UUID] = Field(
        min_length=1,
    )

    hard_delete: bool = False


class AssetBulkDeleteResponse(BaseSchema):
    """
    Bulk delete summary.
    """

    deleted: int

    failed: int

    errors: list[str] = Field(
        default_factory=list,
    )


# ============================================================
# Bulk Update
# ============================================================


class AssetBulkUpdate(BaseSchema):
    """
    Update multiple assets.
    """

    asset_ids: list[UUID] = Field(
        min_length=1,
    )

    asset_group_id: UUID | None = None

    owner_id: UUID | None = None

    status: AssetStatus | None = None

    criticality: (
        Criticality | None
    ) = None

    external: bool | None = None

    scan_enabled: bool | None = None


class AssetBulkActionResult(
    BaseSchema,
):
    """
    Generic bulk action result.
    """

    processed: int

    succeeded: int

    failed: int

    errors: list[str] = Field(
        default_factory=list,
    )


# ============================================================
# Asset Move
# ============================================================


class AssetMoveRequest(BaseSchema):
    """
    Move assets into another group.
    """

    asset_ids: list[UUID] = Field(
        min_length=1,
    )

    destination_group_id: (
        UUID | None
    ) = None


# ============================================================
# Ownership
# ============================================================


class AssetOwnerUpdate(
    BaseSchema,
):
    """
    Change asset owner.
    """

    owner_id: UUID | None = None


# ============================================================
# Tag Operations
# ============================================================


class AssetTagUpdate(
    BaseSchema,
):
    """
    Replace asset tags.
    """

    tags: list[str]

    @field_validator("tags")
    @classmethod
    def normalize(
        cls,
        value: list[str],
    ) -> list[str]:

        return _AssetValidator.normalize_tags(
            value,
        )


class AssetAddTags(
    BaseSchema,
):
    """
    Append tags.
    """

    tags: list[str]

    @field_validator("tags")
    @classmethod
    def normalize(
        cls,
        value: list[str],
    ) -> list[str]:

        return _AssetValidator.normalize_tags(
            value,
        )


class AssetRemoveTags(
    BaseSchema,
):
    """
    Remove tags.
    """

    tags: list[str]

    @field_validator("tags")
    @classmethod
    def normalize(
        cls,
        value: list[str],
    ) -> list[str]:

        return _AssetValidator.normalize_tags(
            value,
        )


# ============================================================
# Scan Configuration
# ============================================================


class AssetScanConfiguration(
    BaseSchema,
):
    """
    Configure automatic scanning.
    """

    scan_enabled: bool = True

    scan_interval_hours: (
        int | None
    ) = Field(
        default=None,
        ge=1,
        le=720,
    )

    auto_discovery: bool = False

    notify_on_findings: bool = True


# ============================================================
# Archive
# ============================================================


class AssetArchiveRequest(
    BaseSchema,
):
    """
    Archive or restore assets.
    """

    asset_ids: list[UUID] = Field(
        min_length=1,
    )

    archive: bool = True
    # ============================================================
# Technology
# ============================================================


class AssetTechnology(BaseSchema):
    """
    Technology detected on an asset.
    """

    name: str

    version: str | None = None

    category: str | None = None


# ============================================================
# Certificate
# ============================================================


class AssetCertificate(BaseSchema):
    """
    TLS certificate summary.
    """

    subject: str

    issuer: str

    valid_from: datetime

    valid_until: datetime

    expires_in_days: int

    self_signed: bool

    trusted: bool


# ============================================================
# Scan Statistics
# ============================================================


class AssetScanStatistics(BaseSchema):
    """
    Scan metrics.
    """

    total_scans: int = 0

    successful_scans: int = 0

    failed_scans: int = 0

    queued_scans: int = 0

    running_scans: int = 0

    average_duration_seconds: float = 0.0

    success_rate: float = Field(
        default=0.0,
        ge=0,
        le=100,
    )

    first_scan_at: datetime | None = None

    last_scan_at: datetime | None = None


# ============================================================
# Finding Statistics
# ============================================================


class AssetFindingStatistics(BaseSchema):
    """
    Finding summary.
    """

    total: int = 0

    critical: int = 0

    high: int = 0

    medium: int = 0

    low: int = 0

    informational: int = 0

    open: int = 0

    resolved: int = 0

    false_positive: int = 0


# ============================================================
# Asset Summary
# ============================================================


class AssetSummary(UUIDTimestampSchema):
    """
    Lightweight asset representation.
    """

    name: str

    asset_type: AssetType

    value: str

    status: AssetStatus

    criticality: Criticality

    asset_group_id: UUID | None = None

    owner_id: UUID | None = None

    tags: list[str] = Field(
        default_factory=list,
    )

    risk_score: float = Field(
        default=0.0,
        ge=0,
        le=100,
    )

    active_findings: int = 0

    total_findings: int = 0

    scan_count: int = 0

    last_scan_at: datetime | None = None

    discovered_at: datetime | None = None


# ============================================================
# Asset Response
# ============================================================


class AssetResponse(
    UUIDTimestampSchema,
    AssetBase,
):
    """
    Standard API response.
    """

    risk_score: float = Field(
        default=0.0,
        ge=0,
        le=100,
    )

    active_findings: int = 0

    total_findings: int = 0

    scan_count: int = 0

    last_scan_at: datetime | None = None

    discovered_at: datetime | None = None


# ============================================================
# Asset Detail
# ============================================================


class AssetDetail(
    AssetResponse,
):
    """
    Complete asset information.
    """

    technologies: list[
        AssetTechnology
    ] = Field(
        default_factory=list,
    )

    certificates: list[
        AssetCertificate
    ] = Field(
        default_factory=list,
    )

    scan_statistics: AssetScanStatistics = Field(
        default_factory=AssetScanStatistics,
    )

    finding_statistics: (
        AssetFindingStatistics
    ) = Field(
        default_factory=AssetFindingStatistics,
    )

    related_assets: list[
        UUID
    ] = Field(
        default_factory=list,
    )

    notes: str | None = None

    metadata: dict[
        str,
        str,
    ] = Field(
        default_factory=dict,
    )
    # ============================================================
# Asset Statistics
# ============================================================


class AssetStatistics(BaseSchema):
    """
    Organization-wide asset statistics.
    """

    total_assets: int = 0

    active_assets: int = 0

    inactive_assets: int = 0

    archived_assets: int = 0

    discovered_assets: int = 0

    external_assets: int = 0

    internal_assets: int = 0

    production_assets: int = 0

    internet_facing_assets: int = 0

    scan_enabled_assets: int = 0

    average_risk_score: float = Field(
        default=0.0,
        ge=0,
        le=100,
    )

    highest_risk_score: float = Field(
        default=0.0,
        ge=0,
        le=100,
    )

    assets_by_type: dict[str, int] = Field(
        default_factory=dict,
    )

    assets_by_status: dict[str, int] = Field(
        default_factory=dict,
    )

    assets_by_criticality: dict[str, int] = Field(
        default_factory=dict,
    )


# ============================================================
# Dashboard
# ============================================================


class AssetDashboard(BaseSchema):
    """
    Asset dashboard payload.
    """

    statistics: AssetStatistics

    recently_added: list[
        AssetSummary
    ] = Field(
        default_factory=list,
    )

    recently_updated: list[
        AssetSummary
    ] = Field(
        default_factory=list,
    )

    highest_risk: list[
        AssetSummary
    ] = Field(
        default_factory=list,
    )

    recently_scanned: list[
        AssetSummary
    ] = Field(
        default_factory=list,
    )


# ============================================================
# Search
# ============================================================


class AssetSearchResponse(BaseSchema):
    """
    Asset search response.
    """

    query: str

    total_matches: int

    assets: list[
        AssetSummary
    ] = Field(
        default_factory=list,
    )


# ============================================================
# Export
# ============================================================


class AssetExportResponse(BaseSchema):
    """
    Asset export metadata.
    """

    filename: str

    format: str

    generated_at: datetime

    record_count: int

    download_url: str | None = None


# ============================================================
# List Response
# ============================================================


class AssetListResponse(BaseSchema):
    """
    Paginated asset collection.
    """

    assets: list[
        AssetSummary
    ] = Field(
        default_factory=list,
    )

    total: int

    page: int = 1

    page_size: int = 25

    total_pages: int = 1

    has_previous: bool = False

    has_next: bool = False
    # ============================================================
# Sorting
# ============================================================


class SortOrder(str, Enum):
    """
    Sort direction.
    """

    ASC = "asc"

    DESC = "desc"


class AssetSortField(str, Enum):
    """
    Supported asset sorting fields.
    """

    NAME = "name"

    VALUE = "value"

    TYPE = "asset_type"

    STATUS = "status"

    CRITICALITY = "criticality"

    RISK_SCORE = "risk_score"

    CREATED_AT = "created_at"

    UPDATED_AT = "updated_at"


# ============================================================
# Filtering
# ============================================================


class AssetFilter(BaseSchema):
    """
    Asset filtering options.
    """

    organization_id: UUID | None = None

    asset_group_id: UUID | None = None

    owner_id: UUID | None = None

    asset_type: AssetType | None = None

    status: AssetStatus | None = None

    criticality: Criticality | None = None

    enabled: bool | None = None

    external: bool | None = None

    production: bool | None = None

    internet_facing: bool | None = None

    min_risk_score: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    max_risk_score: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    tag: str | None = None

    search: str | None = None

    include_deleted: bool = False


# ============================================================
# Pagination / List Request
# ============================================================


class AssetListRequest(BaseSchema):
    """
    Paginated asset listing request.
    """

    filters: AssetFilter = Field(
        default_factory=AssetFilter,
    )

    page: int = Field(
        default=1,
        ge=1,
    )

    page_size: int = Field(
        default=25,
        ge=1,
        le=500,
    )

    sort_by: AssetSortField = (
        AssetSortField.CREATED_AT
    )

    sort_order: SortOrder = (
        SortOrder.DESC
    )


# ============================================================
# Search Request
# ============================================================


class AssetSearchRequest(BaseSchema):
    """
    Full-text asset search.
    """

    query: str = Field(
        min_length=1,
        max_length=255,
    )

    organization_id: UUID | None = None

    page: int = Field(
        default=1,
        ge=1,
    )

    page_size: int = Field(
        default=25,
        ge=1,
        le=100,
    )


# ============================================================
# Export
# ============================================================


class ExportFormat(str, Enum):
    """
    Supported export formats.
    """

    CSV = "csv"

    JSON = "json"

    XLSX = "xlsx"


class AssetExportRequest(BaseSchema):
    """
    Asset export request.
    """

    filters: AssetFilter = Field(
        default_factory=AssetFilter,
    )

    format: ExportFormat = (
        ExportFormat.CSV
    )

    include_deleted: bool = False

    include_notes: bool = False

    include_tags: bool = True

    include_metadata: bool = True
    # ============================================================
# Validation
# ============================================================


class AssetFilter(BaseSchema):
    """
    Asset filtering options.
    """

    organization_id: UUID | None = None

    asset_group_id: UUID | None = None

    owner_id: UUID | None = None

    asset_type: AssetType | None = None

    status: AssetStatus | None = None

    criticality: Criticality | None = None

    enabled: bool | None = None

    external: bool | None = None

    production: bool | None = None

    internet_facing: bool | None = None

    min_risk_score: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    max_risk_score: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    tag: str | None = None

    search: str | None = None

    include_deleted: bool = False

    @field_validator("tag")
    @classmethod
    def normalize_tag(
        cls,
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip().lower()

        return value or None

    @field_validator("search")
    @classmethod
    def normalize_search(
        cls,
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip()

        return value or None


# ============================================================
# Request Validation
# ============================================================


class AssetListRequest(BaseSchema):
    """
    Request for paginated asset listing.
    """

    filters: AssetFilter = Field(
        default_factory=AssetFilter,
    )

    page: int = Field(
        default=1,
        ge=1,
    )

    page_size: int = Field(
        default=25,
        ge=1,
        le=500,
    )

    sort_by: AssetSortField = (
        AssetSortField.CREATED_AT
    )

    sort_order: SortOrder = (
        SortOrder.DESC
    )


# ============================================================
# Utility Responses
# ============================================================


class AssetExistsResponse(BaseSchema):
    """
    Duplicate lookup response.
    """

    exists: bool

    asset_id: UUID | None = None


class AssetCountResponse(BaseSchema):
    """
    Organization asset count.
    """

    organization_id: UUID

    total_assets: int

    active_assets: int

    external_assets: int

    scan_enabled_assets: int


class AssetRiskSummary(BaseSchema):
    """
    Lightweight risk overview.
    """

    asset_id: UUID

    asset_name: str

    risk_score: float = Field(
        ge=0,
        le=100,
    )

    criticality: Criticality


# ============================================================
# Internal Helpers
# ============================================================


class AssetLookup(BaseSchema):
    """
    Generic lookup object.
    """

    id: UUID

    name: str

    value: str


class AssetReference(BaseSchema):
    """
    Minimal asset reference.
    """

    id: UUID

    name: str


# ============================================================
# End of File
# ============================================================