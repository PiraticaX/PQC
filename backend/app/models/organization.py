"""
QShield Enterprise
==================

Organization Model

The Organization is the root entity for the entire platform.

Every asset, scan, finding, report, user, and team belongs to an
organization.

This enables:

- Multi-tenancy
- Customer isolation
- Managed Security Service Providers (MSSP)
- Enterprise deployments
- Team collaboration
"""

from __future__ import annotations

import enum

from sqlalchemy import (
    Boolean,
    Enum,
    Index,
    String,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base import Base
from app.database.mixins import (
    AuditMixin,
    DescriptionMixin,
    NameMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)


# ============================================================================
# ENUMERATIONS
# ============================================================================


class OrganizationStatus(str, enum.Enum):
    """
    Current lifecycle status of an organization.
    """

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    ARCHIVED = "archived"


class SubscriptionTier(str, enum.Enum):
    """
    Commercial subscription tier.
    """

    COMMUNITY = "community"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


# ============================================================================
# MODEL
# ============================================================================


class Organization(
    Base,
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    AuditMixin,
    NameMixin,
    DescriptionMixin,
):
    """
    Root entity of the QShield platform.
    """

    __tablename__ = "organizations"

    __table_args__ = (
        Index("idx_org_name", "name"),
        Index("idx_org_status", "status"),
        Index("idx_org_domain", "primary_domain"),
    )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    legal_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    primary_domain: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )

    website: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    status: Mapped[OrganizationStatus] = mapped_column(
        Enum(OrganizationStatus),
        default=OrganizationStatus.TRIAL,
        nullable=False,
    )

    subscription: Mapped[SubscriptionTier] = mapped_column(
        Enum(SubscriptionTier),
        default=SubscriptionTier.COMMUNITY,
        nullable=False,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Contact
    # ------------------------------------------------------------------

    contact_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    contact_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    contact_phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    country: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    timezone: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        default="UTC",
    )

    # ------------------------------------------------------------------
    # License Limits
    # ------------------------------------------------------------------

    max_users: Mapped[int] = mapped_column(
        default=10,
        nullable=False,
    )

    max_assets: Mapped[int] = mapped_column(
        default=100,
        nullable=False,
    )

    max_scans_per_day: Mapped[int] = mapped_column(
        default=1000,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    users = relationship(
        "User",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    teams = relationship(
        "Team",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    asset_groups = relationship(
        "AssetGroup",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    assets = relationship(
        "Asset",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    scheduled_scans = relationship(
        "ScheduledScan",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    reports = relationship(
        "Report",
        back_populates="organization",
    )

    roles = relationship(
        "Role",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def is_active(self) -> bool:
        return (
            self.enabled
            and self.status == OrganizationStatus.ACTIVE
        )

    @property
    def is_trial(self) -> bool:
        return self.status == OrganizationStatus.TRIAL

    def __repr__(self) -> str:
        return (
            f"<Organization("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"status='{self.status.value}', "
            f"subscription='{self.subscription.value}'"
            f")>"
        )

    def to_dict(self) -> dict:
        """
        Serialize organization metadata.

        Relationship collections are intentionally excluded.
        """

        return {
            "id": str(self.id),
            "name": self.name,
            "legal_name": self.legal_name,
            "description": self.description,
            "primary_domain": self.primary_domain,
            "website": self.website,
            "status": self.status.value,
            "subscription": self.subscription.value,
            "enabled": self.enabled,
            "contact_name": self.contact_name,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "country": self.country,
            "timezone": self.timezone,
            "max_users": self.max_users,
            "max_assets": self.max_assets,
            "max_scans_per_day": self.max_scans_per_day,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "deleted_at": (
                self.deleted_at.isoformat()
                if self.deleted_at
                else None
            ),
        }