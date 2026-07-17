"""
QShield Enterprise
==================

Permission Schemas

Pydantic schemas for RBAC permissions.

Compatible with Pydantic v2.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseSchema, UUIDTimestampSchema


# ============================================================
# Base
# ============================================================


class PermissionBase(BaseSchema):
    """
    Fields shared across permission schemas.
    """

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["Create Assets"],
    )

    slug: str = Field(
        ...,
        min_length=3,
        max_length=100,
        examples=["asset:create"],
    )

    resource: str = Field(
        ...,
        min_length=2,
        max_length=50,
        examples=["asset"],
    )

    action: str = Field(
        ...,
        min_length=2,
        max_length=50,
        examples=["create"],
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )


# ============================================================
# Create
# ============================================================


class PermissionCreate(PermissionBase):
    """
    Create permission payload.
    """

    pass


# ============================================================
# Update
# ============================================================


class PermissionUpdate(BaseSchema):
    """
    Partial update payload.
    """

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    slug: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
    )

    resource: str | None = Field(
        default=None,
        max_length=50,
    )

    action: str | None = Field(
        default=None,
        max_length=50,
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )


# ============================================================
# Response
# ============================================================


class PermissionResponse(
    UUIDTimestampSchema,
    PermissionBase,
):
    """
    Standard permission response.
    """

    pass


# ============================================================
# Summary
# ============================================================


class PermissionSummary(BaseSchema):
    """
    Lightweight permission representation.
    """

    id: UUID
    name: str
    slug: str
    resource: str
    action: str


# ============================================================
# Assignment
# ============================================================


class PermissionAssignment(BaseSchema):
    """
    Assign permissions to a role.
    """

    permission_ids: list[UUID] = Field(
        default_factory=list,
    )


# ============================================================
# List Response
# ============================================================


class PermissionListResponse(BaseSchema):
    """
    Collection of permissions.
    """

    permissions: list[PermissionSummary]
    total: int