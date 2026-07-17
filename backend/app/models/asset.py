"""
QShield Enterprise
==================

Asset Model

The Asset is the core entity of QShield.

Everything revolves around an Asset:

• Scans
• Findings
• TLS Results
• DNS Results
• HTTP Results
• Certificates
• Technologies
• Compliance
• Reports
• AI Recommendations

Supported Assets
----------------

- Domain
- Subdomain
- IPv4
- IPv6
- CIDR
- URL
- Hostname
- VM
- Kubernetes
- Container
- Cloud Resource
- API Endpoint
- Email Domain
"""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import (
    Boolean,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base import Base
from app.database.mixins import (
    DescriptionMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)
from app.database.types import GUID


# ============================================================
# ENUMS
# ============================================================


class AssetType(str, enum.Enum):
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


class AssetStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    DISCOVERED = "discovered"


class Criticality(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================================
# MODEL
# ============================================================


class Asset(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    DescriptionMixin,
    Base,
):
    """
    Cyber Asset.
    """

    __tablename__ = "assets"

    __table_args__ = (

        UniqueConstraint(
            "organization_id",
            "asset_value",
            name="uq_asset_value",
        ),

        Index(
            "idx_asset_org",
            "organization_id",
        ),

        Index(
            "idx_asset_group",
            "asset_group_id",
        ),

        Index(
            "idx_asset_type",
            "asset_type",
        ),

        Index(
            "idx_asset_status",
            "status",
        ),

        Index(
            "idx_asset_enabled",
            "enabled",
        ),
    )

    # ============================================================
    # Ownership
    # ============================================================

    organization_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    asset_group_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey(
            "asset_groups.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    # ============================================================
    # Identity
    # ============================================================

    asset_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    asset_value: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    asset_type: Mapped[AssetType] = mapped_column(
        Enum(AssetType),
        nullable=False,
    )

    display_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # ============================================================
    # Network
    # ============================================================

    hostname: Mapped[str | None] = mapped_column(
        String(255),
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(64),
    )

    port: Mapped[int | None] = mapped_column(
        Integer,
    )

    protocol: Mapped[str | None] = mapped_column(
        String(20),
    )

    scheme: Mapped[str | None] = mapped_column(
        String(20),
    )

    fqdn: Mapped[str | None] = mapped_column(
        String(255),
    )

    # ============================================================
    # Metadata
    # ============================================================

    status: Mapped[AssetStatus] = mapped_column(
        Enum(AssetStatus),
        default=AssetStatus.ACTIVE,
    )

    criticality: Mapped[Criticality] = mapped_column(
        Enum(Criticality),
        default=Criticality.MEDIUM,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    external: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    production: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    internet_facing: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    # ============================================================
    # Risk
    # ============================================================

    risk_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    business_impact: Mapped[int] = mapped_column(
        Integer,
        default=1,
    )

    attack_surface_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    # ============================================================
    # Discovery
    # ============================================================

    discovered_by: Mapped[str | None] = mapped_column(
        String(100),
    )

    source: Mapped[str | None] = mapped_column(
        String(100),
    )

    tags: Mapped[str | None] = mapped_column(
        Text,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
    )

    # ============================================================
    # Relationships
    # ============================================================

    organization = relationship(
        "Organization",
        back_populates="assets",
    )

    asset_group = relationship(
        "AssetGroup",
        back_populates="assets",
    )

    owner = relationship(
        "User",
        back_populates="assets",
    )

    scans = relationship(
        "Scan",
        back_populates="asset",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    reports = relationship(
        "Report",
        back_populates="asset",
    )
        # ============================================================
    # Helper Properties
    # ============================================================

    @property
    def is_active(self) -> bool:
        """
        Returns True if the asset is active.
        """
        return (
            self.enabled
            and self.status == AssetStatus.ACTIVE
        )

    @property
    def is_external(self) -> bool:
        """
        Indicates whether the asset is externally accessible.
        """
        return self.external

    @property
    def is_production(self) -> bool:
        """
        Indicates whether the asset belongs to production.
        """
        return self.production

    @property
    def scan_count(self) -> int:
        """
        Total scans executed for this asset.
        """
        return len(self.scans)

    @property
    def hostname_or_ip(self) -> str:
        """
        Returns the best identifier available.
        """
        return (
            self.hostname
            or self.fqdn
            or self.ip_address
            or self.asset_value
        )

    # ============================================================
    # Risk Helpers
    # ============================================================

    def update_risk_score(
        self,
        score: float,
    ) -> None:
        """
        Updates the calculated risk score.

        Score is automatically clamped between 0 and 100.
        """

        score = max(0.0, min(100.0, score))

        self.risk_score = round(score, 2)

    def increase_risk(
        self,
        value: float,
    ) -> None:
        """
        Increment risk score.
        """

        self.update_risk_score(
            self.risk_score + value
        )

    def decrease_risk(
        self,
        value: float,
    ) -> None:
        """
        Decrement risk score.
        """

        self.update_risk_score(
            self.risk_score - value
        )

    # ============================================================
    # Tag Helpers
    # ============================================================

    def tag_list(self) -> list[str]:
        """
        Converts comma-separated tags into a list.
        """

        if not self.tags:
            return []

        return sorted(
            {
                tag.strip()
                for tag in self.tags.split(",")
                if tag.strip()
            }
        )

    def has_tag(
        self,
        tag: str,
    ) -> bool:
        """
        Check whether a tag exists.
        """

        return tag in self.tag_list()

    # ============================================================
    # URL Helpers
    # ============================================================

    def asset_url(self) -> str:
        """
        Builds a canonical URL for HTTP/HTTPS assets.
        """

        if self.scheme and self.hostname:
            return f"{self.scheme}://{self.hostname}"

        return self.asset_value

    # ============================================================
    # Serialization
    # ============================================================

    def to_dict(
        self,
        include_scans: bool = False,
    ) -> dict:
        """
        Serialize asset.
        """

        data = {
            "id": str(self.id),
            "organization_id": str(self.organization_id),
            "asset_group_id": (
                str(self.asset_group_id)
                if self.asset_group_id
                else None
            ),
            "owner_id": (
                str(self.owner_id)
                if self.owner_id
                else None
            ),
            "asset_name": self.asset_name,
            "asset_value": self.asset_value,
            "display_name": self.display_name,
            "asset_type": self.asset_type.value,
            "status": self.status.value,
            "criticality": self.criticality.value,
            "enabled": self.enabled,
            "external": self.external,
            "production": self.production,
            "internet_facing": self.internet_facing,
            "hostname": self.hostname,
            "fqdn": self.fqdn,
            "ip_address": self.ip_address,
            "port": self.port,
            "protocol": self.protocol,
            "scheme": self.scheme,
            "risk_score": self.risk_score,
            "attack_surface_score": self.attack_surface_score,
            "business_impact": self.business_impact,
            "discovered_by": self.discovered_by,
            "source": self.source,
            "tags": self.tag_list(),
            "notes": self.notes,
            "scan_count": self.scan_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "deleted_at": (
                self.deleted_at.isoformat()
                if self.deleted_at
                else None
            ),
        }

        if include_scans:
            data["scans"] = [
                scan.to_dict()
                for scan in self.scans
            ]

        return data

    # ============================================================
    # Representation
    # ============================================================

    def __repr__(self) -> str:
        return (
            "<Asset("
            f"id={self.id}, "
            f"name='{self.asset_name}', "
            f"type='{self.asset_type.value}', "
            f"value='{self.asset_value}'"
            ")>"
        )