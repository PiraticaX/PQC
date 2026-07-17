"""
QShield Enterprise
==================

Asset Group Schemas

Pydantic schemas for organizing assets into hierarchical groups.

Compatible with Pydantic v2.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseSchema, UUIDTimestampSchema


# ============================================================
# Base
# ============================================================


class AssetGroupBase(BaseSchema):
    """
    Fields shared by all Asset Group schemas.
    """

    name: str = Field(
        ...,
        min_length=2,
        max_length=150,
        examples=["Production Servers"],
    )

    slug: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["production-servers"],
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    organization_id: UUID

    parent_group_id: UUID | None = None

    is_active: bool = True


# ============================================================
# Create
# ============================================================


class AssetGroupCreate(AssetGroupBase):
    """
    Create Asset Group payload.
    """

    pass


# ============================================================
# Update
# ============================================================


class AssetGroupUpdate(BaseSchema):
    """
    Partial update payload.
    """

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    slug: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    parent_group_id: UUID | None = None

    is_active: bool | None = None


# ============================================================
# Summary
# ============================================================


class AssetGroupSummary(BaseSchema):
    """
    Lightweight Asset Group representation.
    """

    id: UUID
    name: str
    slug: str

    asset_count: int = 0
    child_count: int = 0

    is_active: bool


# ============================================================
# Response
# ============================================================


class AssetGroupResponse(
    UUIDTimestampSchema,
    AssetGroupBase,
):
    """
    Standard Asset Group response.
    """

    asset_count: int = 0
    child_count: int = 0


# ============================================================
# Tree Node
# ============================================================


class AssetGroupTree(AssetGroupSummary):
    """
    Recursive Asset Group tree.
    """

    children: list["AssetGroupTree"] = Field(
        default_factory=list,
    )


AssetGroupTree.model_rebuild()


# ============================================================
# Move Request
# ============================================================


class AssetGroupMoveRequest(BaseSchema):
    """
    Move an asset group under another parent.
    """

    parent_group_id: UUID | None = None


# ============================================================
# List Response
# ============================================================


class AssetGroupListResponse(BaseSchema):
    """
    Collection of asset groups.
    """

    asset_groups: list[AssetGroupSummary]
    total: int