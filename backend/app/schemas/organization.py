"""
QShield Enterprise
==================

Organization Schemas

Pydantic schemas for Organization CRUD operations.

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
# Base
# ============================================================


class OrganizationBase(BaseSchema):
    """
    Fields shared by organization schemas.
    """

    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        examples=["Acme Corporation"],
    )

    slug: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["acme-corp"],
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    website: str | None = Field(
        default=None,
        max_length=255,
    )

    email: str | None = Field(
        default=None,
        max_length=255,
    )

    phone: str | None = Field(
        default=None,
        max_length=50,
    )

    address: str | None = None

    city: str | None = Field(
        default=None,
        max_length=100,
    )

    state: str | None = Field(
        default=None,
        max_length=100,
    )

    country: str | None = Field(
        default=None,
        max_length=100,
    )

    postal_code: str | None = Field(
        default=None,
        max_length=30,
    )

    active: bool = True


# ============================================================
# Create
# ============================================================


class OrganizationCreate(OrganizationBase):
    """
    Payload for creating an organization.
    """

    pass


# ============================================================
# Update
# ============================================================


class OrganizationUpdate(BaseSchema):
    """
    Payload for updating an organization.

    All fields are optional.
    """

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    slug: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    website: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None

    active: bool | None = None


# ============================================================
# Response
# ============================================================


class OrganizationResponse(
    UUIDTimestampSchema,
    OrganizationBase,
):
    """
    Organization response schema.
    """

    pass


# ============================================================
# Summary
# ============================================================


class OrganizationSummary(BaseSchema):
    """
    Lightweight organization representation.
    """

    id: UUID
    name: str
    slug: str
    active: bool


# ============================================================
# List Response
# ============================================================


class OrganizationListResponse(BaseSchema):
    """
    Collection of organizations.
    """

    organizations: list[OrganizationSummary]
    total: int