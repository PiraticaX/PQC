"""
QShield Enterprise
==================

User Schemas

Pydantic schemas for User authentication and CRUD operations.

Compatible with Pydantic v2.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, Field, SecretStr, field_validator

from app.schemas.base import (
    BaseSchema,
    UUIDTimestampSchema,
)


# ============================================================
# Base
# ============================================================


class UserBase(BaseSchema):
    """
    Fields shared across user schemas.
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=64,
        examples=["jdoe"],
    )

    email: EmailStr

    first_name: str | None = Field(
        default=None,
        max_length=100,
    )

    last_name: str | None = Field(
        default=None,
        max_length=100,
    )

    organization_id: UUID

    is_active: bool = True
    is_verified: bool = False


# ============================================================
# Create
# ============================================================


class UserCreate(UserBase):
    """
    User creation payload.
    """

    password: SecretStr = Field(
        ...,
        min_length=8,
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        value = value.strip()

        if " " in value:
            raise ValueError("Username cannot contain spaces.")

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: SecretStr) -> SecretStr:
        password = value.get_secret_value()

        if len(password) < 8:
            raise ValueError("Password must contain at least 8 characters.")

        return value


# ============================================================
# Update
# ============================================================


class UserUpdate(BaseSchema):
    """
    Partial update payload.
    """

    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = None
    is_active: bool | None = None
    is_verified: bool | None = None


# ============================================================
# Authentication
# ============================================================


class UserLogin(BaseSchema):
    """
    Login request.
    """

    username: str
    password: SecretStr


class UserPasswordChange(BaseSchema):
    """
    Password change request.
    """

    current_password: SecretStr
    new_password: SecretStr = Field(
        ...,
        min_length=8,
    )


# ============================================================
# Response
# ============================================================


class UserResponse(
    UUIDTimestampSchema,
    UserBase,
):
    """
    Full user response.
    """

    last_login_at: datetime | None = None


# ============================================================
# Summary
# ============================================================


class UserSummary(BaseSchema):
    """
    Lightweight user representation.
    """

    id: UUID
    username: str
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool


# ============================================================
# Profile
# ============================================================


class UserProfile(UserResponse):
    """
    Extended profile response.
    """

    roles: list[str] = Field(default_factory=list)
    teams: list[str] = Field(default_factory=list)


# ============================================================
# List Response
# ============================================================


class UserListResponse(BaseSchema):
    """
    Collection of users.
    """

    users: list[UserSummary]
    total: int