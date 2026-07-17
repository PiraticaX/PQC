"""
QShield Enterprise
==================

HTTP Result Model

Stores HTTP/HTTPS assessment results discovered during a scan.

One Scan may generate multiple HTTPResult records for different URLs
or endpoints.
"""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base import Base
from app.database.mixins import (
    TimestampMixin,
    UUIDMixin,
)
from app.database.types import GUID


# ============================================================
# ENUMS
# ============================================================


class HTTPProtocol(str, enum.Enum):
    HTTP_1_0 = "HTTP/1.0"
    HTTP_1_1 = "HTTP/1.1"
    HTTP_2 = "HTTP/2"
    HTTP_3 = "HTTP/3"


# ============================================================
# MODEL
# ============================================================


class HTTPResult(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    """
    HTTP assessment result for a single endpoint.
    """

    __tablename__ = "http_results"

    __table_args__ = (
        Index("idx_http_scan", "scan_id"),
        Index("idx_http_url", "url"),
        Index("idx_http_status", "status_code"),
    )

    # ============================================================
    # Relationships
    # ============================================================

    scan_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey(
            "scans.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    # ============================================================
    # Endpoint
    # ============================================================

    url: Mapped[str] = mapped_column(
        String(2048),
        nullable=False,
    )

    scheme: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    host: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    port: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    path: Mapped[str | None] = mapped_column(
        String(2048),
    )

    # ============================================================
    # Response
    # ============================================================

    status_code: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    protocol: Mapped[HTTPProtocol | None] = mapped_column(
        Enum(HTTPProtocol),
    )

    response_time_ms: Mapped[int | None] = mapped_column(
        Integer,
    )

    content_length: Mapped[int | None] = mapped_column(
        Integer,
    )

    content_type: Mapped[str | None] = mapped_column(
        String(255),
    )

    server: Mapped[str | None] = mapped_column(
        String(255),
    )

    powered_by: Mapped[str | None] = mapped_column(
        String(255),
    )

    # ============================================================
    # Redirects
    # ============================================================

    redirected: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    redirect_location: Mapped[str | None] = mapped_column(
        String(2048),
    )

    redirect_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    # ============================================================
    # Security Headers
    # ============================================================

    hsts: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    csp: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    x_frame_options: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    x_content_type_options: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    referrer_policy: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    permissions_policy: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    # ============================================================
    # Features
    # ============================================================

    compression_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    keep_alive: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    chunked_encoding: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    allowed_methods: Mapped[str | None] = mapped_column(
        Text,
    )

    # ============================================================
    # Relationships
    # ============================================================

    scan = relationship(
        "Scan",
        back_populates="http_results",
    )
        # ============================================================
    # Helper Properties
    # ============================================================

    @property
    def is_success(self) -> bool:
        """
        Returns True for 2xx responses.
        """
        return 200 <= self.status_code < 300

    @property
    def is_redirect(self) -> bool:
        """
        Returns True for 3xx responses.
        """
        return 300 <= self.status_code < 400

    @property
    def is_client_error(self) -> bool:
        """
        Returns True for 4xx responses.
        """
        return 400 <= self.status_code < 500

    @property
    def is_server_error(self) -> bool:
        """
        Returns True for 5xx responses.
        """
        return 500 <= self.status_code < 600

    # ============================================================
    # Header Helpers
    # ============================================================

    @property
    def security_header_score(self) -> int:
        """
        Returns a simple score (0-6) based on the presence of common
        HTTP security headers.
        """

        score = 0

        headers = (
            self.hsts,
            self.csp,
            self.x_frame_options,
            self.x_content_type_options,
            self.referrer_policy,
            self.permissions_policy,
        )

        for enabled in headers:
            if enabled:
                score += 1

        return score

    @property
    def allowed_method_list(self) -> list[str]:
        """
        Parse comma-separated HTTP methods.
        """

        if not self.allowed_methods:
            return []

        return sorted(
            {
                method.strip().upper()
                for method in self.allowed_methods.split(",")
                if method.strip()
            }
        )

    # ============================================================
    # Security Helpers
    # ============================================================

    @property
    def is_secure_configuration(self) -> bool:
        """
        Conservative web security assessment.
        """

        return (
            self.hsts
            and self.csp
            and self.x_frame_options
            and self.x_content_type_options
        )

    # ============================================================
    # Serialization
    # ============================================================

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "scan_id": str(self.scan_id),
            "url": self.url,
            "scheme": self.scheme,
            "host": self.host,
            "port": self.port,
            "path": self.path,
            "status_code": self.status_code,
            "protocol": (
                self.protocol.value
                if self.protocol
                else None
            ),
            "response_time_ms": self.response_time_ms,
            "content_length": self.content_length,
            "content_type": self.content_type,
            "server": self.server,
            "powered_by": self.powered_by,
            "redirected": self.redirected,
            "redirect_location": self.redirect_location,
            "redirect_count": self.redirect_count,
            "hsts": self.hsts,
            "csp": self.csp,
            "x_frame_options": self.x_frame_options,
            "x_content_type_options": self.x_content_type_options,
            "referrer_policy": self.referrer_policy,
            "permissions_policy": self.permissions_policy,
            "compression_enabled": self.compression_enabled,
            "keep_alive": self.keep_alive,
            "chunked_encoding": self.chunked_encoding,
            "allowed_methods": self.allowed_method_list,
            "security_header_score": self.security_header_score,
            "is_secure_configuration": self.is_secure_configuration,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    # ============================================================
    # Representation
    # ============================================================

    def __repr__(self) -> str:
        return (
            "<HTTPResult("
            f"id={self.id}, "
            f"url='{self.url}', "
            f"status={self.status_code}"
            ")>"
        )