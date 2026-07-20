"""
QShield Enterprise
==================

Asset Group Model

Logical grouping of assets.

Supports:

- Asset organization
- Multi-tenancy
- Asset inventory management
"""

from __future__ import annotations


import uuid


from sqlalchemy import (
    ForeignKey,
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
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    NameMixin,
    DescriptionMixin,
)



class AssetGroup(
    Base,
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    NameMixin,
    DescriptionMixin,
):
    """
    Logical collection of security assets.
    """


    __tablename__ = "asset_groups"


    __table_args__ = (

        Index(
            "idx_asset_group_name",
            "name",
        ),

    )



    # ========================================================
    # Organization
    # ========================================================


    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )


    # ========================================================
    # Metadata
    # ========================================================


    asset_count: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
    )


    # ========================================================
    # Relationships
    # ========================================================


    organization = relationship(
        "Organization",
        back_populates="asset_groups",
    )


    assets = relationship(
        "Asset",
        back_populates="group",
        cascade="all, delete-orphan",
    )


    # ========================================================
    # Serialization
    # ========================================================


    def to_dict(self) -> dict:

        return {

            "id": str(self.id),

            "name": self.name,

            "description": self.description,

            "organization_id": str(
                self.organization_id
            ),

            "asset_count": self.asset_count,

        }