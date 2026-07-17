"""
QShield Enterprise
==================

HTTP Result Schemas

Pydantic schemas representing HTTP scan results.

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


class HTTPProtocol(str, Enum):
    """
    HTTP protocol version.
    """

    HTTP_09 = "HTTP/0.9"
    HTTP_10 = "HTTP/1.0"
    HTTP_11 = "HTTP/1.1"
    HTTP_2 = "HTTP/2"
    HTTP_3 = "HTTP/3"


class HTTPMethod(str, Enum):
    """
    Supported HTTP methods.
    """

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"
    CONNECT = "CONNECT"


# ============================================================
# Redirects
# ============================================================


class RedirectEntry(BaseSchema):
    """
    Redirect hop.
    """

    status_code: int

    location: str

    protocol: HTTPProtocol | None = None


# ============================================================
# Headers
# ============================================================


class Header(BaseSchema):
    """
    Generic HTTP header.
    """

    name: str

    value: str


# ============================================================
# Security Headers
# ============================================================


class SecurityHeaders(BaseSchema):
    """
    Security header analysis.
    """

    strict_transport_security: str | None = None

    content_security_policy: str | None = None

    x_frame_options: str | None = None

    x_content_type_options: str | None = None

    referrer_policy: str | None = None

    permissions_policy: str | None = None

    cross_origin_embedder_policy: str | None = None

    cross_origin_opener_policy: str | None = None

    cross_origin_resource_policy: str | None = None

    x_xss_protection: str | None = None


# ============================================================
# Server Information
# ============================================================


class ServerInformation(BaseSchema):
    """
    Server identification.
    """

    server: str | None = None

    powered_by: str | None = None

    application: str | None = None

    operating_system: str | None = None

    reverse_proxy: str | None = None

    cdn: str | None = None


# ============================================================
# Compression
# ============================================================


class CompressionSupport(BaseSchema):
    """
    Compression support.
    """

    gzip: bool = False

    brotli: bool = False

    deflate: bool = False

    zstd: bool = False


# ============================================================
# Cache Information
# ============================================================


class CacheConfiguration(BaseSchema):
    """
    HTTP caching configuration.
    """

    cache_control: str | None = None

    pragma: str | None = None

    expires: str | None = None

    etag: str | None = None

    last_modified: str | None = None

    age: int | None = None


# ============================================================
# Base
# ============================================================


class HTTPResultBase(BaseSchema):
    """
    Shared HTTP result fields.
    """

    asset_id: UUID

    scan_id: UUID

    url: str

    protocol: HTTPProtocol

    status_code: int

    response_time_ms: float

    content_type: str | None = None

    content_length: int | None = None
    # ============================================================
# Request Metadata
# ============================================================


class HTTPRequestMetadata(BaseSchema):
    """
    HTTP request information.
    """

    method: HTTPMethod = HTTPMethod.GET

    user_agent: str | None = None

    host: str | None = None

    accept: str | None = None

    accept_encoding: str | None = None

    accept_language: str | None = None

    request_headers: list[Header] = Field(
        default_factory=list,
    )


# ============================================================
# Response Metadata
# ============================================================


class HTTPResponseMetadata(BaseSchema):
    """
    HTTP response information.
    """

    response_headers: list[Header] = Field(
        default_factory=list,
    )

    redirects: list[RedirectEntry] = Field(
        default_factory=list,
    )

    redirect_count: int = 0

    final_url: str | None = None

    keep_alive: bool = False

    chunked_transfer: bool = False

    connection: str | None = None


# ============================================================
# Protocol Features
# ============================================================


class HTTPProtocolSupport(BaseSchema):
    """
    Supported HTTP protocol features.
    """

    http2_supported: bool = False

    http3_supported: bool = False

    websocket_supported: bool = False

    server_push_supported: bool = False

    alt_svc_present: bool = False


# ============================================================
# Supported Methods
# ============================================================


class SupportedHTTPMethods(BaseSchema):
    """
    Supported HTTP methods.
    """

    methods: list[HTTPMethod] = Field(
        default_factory=list,
    )

    allows_trace: bool = False

    allows_connect: bool = False

    allows_options: bool = False


# ============================================================
# Vulnerabilities
# ============================================================


class HTTPVulnerability(BaseSchema):
    """
    HTTP security finding.
    """

    id: str

    title: str

    severity: str

    description: str

    affected_header: str | None = None

    remediation: str | None = None


# ============================================================
# Recommendations
# ============================================================


class HTTPRecommendation(BaseSchema):
    """
    HTTP security recommendation.
    """

    title: str

    description: str

    priority: str

    automated_fix_available: bool = False


# ============================================================
# Response
# ============================================================


class HTTPResultResponse(
    UUIDTimestampSchema,
    HTTPResultBase,
):
    """
    Standard HTTP scan result.
    """

    request: HTTPRequestMetadata

    response: HTTPResponseMetadata

    security_headers: SecurityHeaders

    server: ServerInformation

    compression: CompressionSupport

    cache: CacheConfiguration

    protocol_support: HTTPProtocolSupport

    supported_methods: SupportedHTTPMethods

    vulnerabilities: list[
        HTTPVulnerability
    ] = Field(default_factory=list)

    recommendations: list[
        HTTPRecommendation
    ] = Field(default_factory=list)
    # ============================================================
# Header Analysis
# ============================================================


class HeaderAnalysis(BaseSchema):
    """
    HTTP header security analysis.
    """

    total_headers: int = 0

    security_headers_present: int = 0

    security_headers_missing: int = 0

    duplicate_headers: list[str] = Field(
        default_factory=list,
    )

    deprecated_headers: list[str] = Field(
        default_factory=list,
    )

    exposed_headers: list[str] = Field(
        default_factory=list,
    )


# ============================================================
# Security Score
# ============================================================


class HTTPSecurityScore(BaseSchema):
    """
    HTTP security posture score.
    """

    score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    grade: str | None = None

    max_score: float = 100

    missing_headers: list[str] = Field(
        default_factory=list,
    )

    weak_headers: list[str] = Field(
        default_factory=list,
    )


# ============================================================
# Technology Exposure
# ============================================================


class TechnologyExposure(BaseSchema):
    """
    Technologies identified through HTTP responses.
    """

    frameworks: list[str] = Field(
        default_factory=list,
    )

    web_servers: list[str] = Field(
        default_factory=list,
    )

    languages: list[str] = Field(
        default_factory=list,
    )

    cms: list[str] = Field(
        default_factory=list,
    )

    libraries: list[str] = Field(
        default_factory=list,
    )


# ============================================================
# Performance
# ============================================================


class HTTPPerformanceMetrics(BaseSchema):
    """
    HTTP performance metrics.
    """

    dns_lookup_ms: float | None = None

    tcp_connect_ms: float | None = None

    tls_handshake_ms: float | None = None

    time_to_first_byte_ms: float | None = None

    download_time_ms: float | None = None

    total_time_ms: float | None = None


# ============================================================
# Detail
# ============================================================


class HTTPResultDetail(
    HTTPResultResponse
):
    """
    Detailed HTTP scan result.
    """

    header_analysis: HeaderAnalysis

    security_score: HTTPSecurityScore

    technology_exposure: TechnologyExposure

    performance: HTTPPerformanceMetrics

    body_hash: str | None = None

    body_size: int | None = None

    favicon_hash: str | None = None

    metadata: dict[str, str] = Field(
        default_factory=dict,
    )


# ============================================================
# Dashboard Summary
# ============================================================


class HTTPDashboardSummary(BaseSchema):
    """
    High-level HTTP dashboard metrics.
    """

    average_security_score: float = 0

    average_response_time_ms: float = 0

    hosts_with_hsts: int = 0

    hosts_with_csp: int = 0

    hosts_with_http2: int = 0

    hosts_with_http3: int = 0

    vulnerable_hosts: int = 0
    # ============================================================
# Status Code Distribution
# ============================================================


class HTTPStatusCodeDistribution(BaseSchema):
    """
    Distribution of HTTP response classes.
    """

    informational: int = 0  # 1xx
    success: int = 0         # 2xx
    redirection: int = 0     # 3xx
    client_error: int = 0    # 4xx
    server_error: int = 0    # 5xx


# ============================================================
# Security Header Statistics
# ============================================================


class HTTPSecurityHeaderStatistics(BaseSchema):
    """
    Security header adoption statistics.
    """

    strict_transport_security: int = 0
    content_security_policy: int = 0
    x_frame_options: int = 0
    x_content_type_options: int = 0
    referrer_policy: int = 0
    permissions_policy: int = 0
    cross_origin_embedder_policy: int = 0
    cross_origin_opener_policy: int = 0
    cross_origin_resource_policy: int = 0
    x_xss_protection: int = 0


# ============================================================
# Protocol Distribution
# ============================================================


class HTTPProtocolDistribution(BaseSchema):
    """
    HTTP protocol usage.
    """

    http09: int = 0
    http10: int = 0
    http11: int = 0
    http2: int = 0
    http3: int = 0


# ============================================================
# Statistics
# ============================================================


class HTTPStatistics(BaseSchema):
    """
    Aggregate HTTP statistics.
    """

    total_hosts: int = 0

    average_response_time_ms: float = 0

    average_security_score: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    protocol_distribution: HTTPProtocolDistribution

    status_codes: HTTPStatusCodeDistribution

    security_headers: HTTPSecurityHeaderStatistics


# ============================================================
# Dashboard
# ============================================================


class HTTPDashboard(BaseSchema):
    """
    HTTP dashboard payload.
    """

    summary: HTTPDashboardSummary

    statistics: HTTPStatistics

    highest_scores: list[HTTPResultResponse] = Field(
        default_factory=list,
    )

    lowest_scores: list[HTTPResultResponse] = Field(
        default_factory=list,
    )

    vulnerable_hosts: list[HTTPResultResponse] = Field(
        default_factory=list,
    )


# ============================================================
# Export
# ============================================================


class HTTPExportResponse(BaseSchema):
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


class HTTPListResponse(BaseSchema):
    """
    Paginated HTTP scan results.
    """

    results: list[HTTPResultResponse] = Field(
        default_factory=list,
    )

    total: int

    page: int = 1

    page_size: int = 25

    total_pages: int = 1


# ============================================================
# End of File
# ============================================================