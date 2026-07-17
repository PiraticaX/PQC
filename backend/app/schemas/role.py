"""
QShield Enterprise
==================

Role Schemas

Pydantic schemas for Role CRUD operations and RBAC management.

Compatible with Pydantic v2.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from app.schemas.base import (
    BaseSchema,
    UUIDTimestampSchema,
)


# ============================================================
# Permission Summary
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
# Base
# ============================================================


class RoleBase(BaseSchema):
    """
    Shared role fields.
    """

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["Security Administrator"],
    )

    slug: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["security-admin"],
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    organization_id: UUID

    is_system: bool = False
    is_active: bool = True


# ============================================================
# Create
# ============================================================


class RoleCreate(RoleBase):
    """
    Payload for creating a role.
    """

    permission_ids: list[UUID] = Field(
        default_factory=list,
    )


# ============================================================
# Update
# ============================================================


class RoleUpdate(BaseSchema):
    """
    Partial role update.
    """

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
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

    permission_ids: list[UUID] | None = None

    is_active: bool | None = None


# ============================================================
# Response
# ============================================================


class RoleResponse(
    UUIDTimestampSchema,
    RoleBase,
):
    """
    Standard role response.
    """

    permission_count: int = 0


# ============================================================
# Summary
# ============================================================


class RoleSummary(BaseSchema):
    """
    Lightweight role representation.
    """

    id: UUID
    name: str
    slug: str
    is_system: bool
    is_active: bool


# ============================================================
# Extended Response
# ============================================================


class RoleWithPermissions(RoleResponse):
    """
    Role including resolved permissions.
    """

    permissions: list[PermissionSummary] = Field(
        default_factory=list,
    )


# ============================================================
# List Response
# ============================================================


class RoleListResponse(BaseSchema):
    """
    Collection of roles.
    """

    roles: list[RoleSummary]
    total: int