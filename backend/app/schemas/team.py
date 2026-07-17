"""
QShield Enterprise
==================

Team Schemas

Pydantic schemas for Team management.

Compatible with Pydantic v2.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseSchema, UUIDTimestampSchema
from app.schemas.user import UserSummary


# ============================================================
# Team Member Summary
# ============================================================


class TeamMemberSummary(BaseSchema):
    """
    Lightweight team member representation.
    """

    id: UUID
    user_id: UUID
    username: str
    first_name: str | None = None
    last_name: str | None = None
    email: str
    role: str | None = None


# ============================================================
# Base
# ============================================================


class TeamBase(BaseSchema):
    """
    Fields shared by all team schemas.
    """

    name: str = Field(
        ...,
        min_length=2,
        max_length=150,
        examples=["Security Operations"],
    )

    slug: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["security-operations"],
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    organization_id: UUID

    is_active: bool = True


# ============================================================
# Create
# ============================================================


class TeamCreate(TeamBase):
    """
    Team creation payload.
    """

    member_ids: list[UUID] = Field(default_factory=list)


# ============================================================
# Update
# ============================================================


class TeamUpdate(BaseSchema):
    """
    Partial team update payload.
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

    is_active: bool | None = None


# ============================================================
# Response
# ============================================================


class TeamResponse(
    UUIDTimestampSchema,
    TeamBase,
):
    """
    Standard team response.
    """

    member_count: int = 0


# ============================================================
# Summary
# ============================================================


class TeamSummary(BaseSchema):
    """
    Lightweight team representation.
    """

    id: UUID
    name: str
    slug: str
    member_count: int
    is_active: bool


# ============================================================
# Detailed Response
# ============================================================


class TeamWithMembers(TeamResponse):
    """
    Team including members.
    """

    members: list[TeamMemberSummary] = Field(default_factory=list)


# ============================================================
# Membership
# ============================================================


class TeamMembershipUpdate(BaseSchema):
    """
    Add or remove members from a team.
    """

    member_ids: list[UUID] = Field(default_factory=list)


# ============================================================
# User Teams
# ============================================================


class UserTeamsResponse(BaseSchema):
    """
    Teams for a given user.
    """

    user: UserSummary
    teams: list[TeamSummary] = Field(default_factory=list)


# ============================================================
# List Response
# ============================================================


class TeamListResponse(BaseSchema):
    """
    Collection of teams.
    """

    teams: list[TeamSummary]
    total: int