"""
QShield Enterprise
==================

Asset Group Model

Asset Groups provide hierarchical organization of assets.

Examples
--------
Production
├── AWS
│   ├── us-east-1
│   └── eu-west-1
├── Azure
└── On-Prem

Development
├── QA
└── Sandbox
"""

from __future__ import annotations

import uuid

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    Integer,
    String,
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
    NameMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)
from app.database.types import GUID


class AssetGroup(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    DescriptionMixin,
    NameMixin,
    Base,
):
    """
    Logical grouping of assets.

    Groups may be nested to create hierarchical structures.
    """

    __tablename__ = "asset_groups"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "parent_id",
            "name",
            name="uq_asset_group_name",
        ),
        Index("idx_asset_group_org", "organization_id"),
        Index("idx_asset_group_parent", "parent_id"),
        Index("idx_asset_group_enabled", "enabled"),
    )

    # ==========================================================
    # Ownership
    # ==========================================================

    organization_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    # ==========================================================
    # Hierarchy
    # ==========================================================

    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey(
            "asset_groups.id",
            ondelete="CASCADE",
        ),
        nullable=True,
    )

    # ==========================================================
    # Metadata
    # ==========================================================

    display_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=100,
        nullable=False,
    )

    color: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        doc="Hex color used by dashboards.",
    )

    icon: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        doc="Optional UI icon identifier.",
    )

    # ==========================================================
    # Relationships
    # ==========================================================

    organization = relationship(
        "Organization",
        back_populates="asset_groups",
    )

    parent = relationship(
        "AssetGroup",
        remote_side="AssetGroup.id",
        back_populates="children",
    )

    children = relationship(
        "AssetGroup",
        back_populates="parent",
        cascade="all, delete-orphan",
    )

    assets = relationship(
        "Asset",
        back_populates="asset_group",
    )

    # ==========================================================
    # Helpers
    # ==========================================================

    @property
    def child_count(self) -> int:
        return len(self.children)

    @property
    def asset_count(self) -> int:
        return len(self.assets)

    # ==========================================================
    # Serialization
    # ==========================================================

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "organization_id": str(self.organization_id),
            "parent_id": (
                str(self.parent_id)
                if self.parent_id
                else None
            ),
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "enabled": self.enabled,
            "sort_order": self.sort_order,
            "color": self.color,
            "icon": self.icon,
            "child_count": self.child_count,
            "asset_count": self.asset_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "deleted_at": (
                self.deleted_at.isoformat()
                if self.deleted_at
                else None
            ),
        }

    # ==========================================================
    # Representation
    # ==========================================================

    def __repr__(self) -> str:
        return (
            "<AssetGroup("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"organization_id={self.organization_id}"
            ")>"
        )