"""
QShield Enterprise
==================

Base Pydantic Schemas

Common schema definitions shared across all request and response
models.

Compatible with Pydantic v2.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """
    Base schema used by all request/response models.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
    )


class TimestampSchema(BaseSchema):
    """
    Base schema with timestamps.
    """

    created_at: datetime
    updated_at: datetime


class UUIDSchema(BaseSchema):
    """
    Base schema with UUID.
    """

    id: UUID


class UUIDTimestampSchema(
    UUIDSchema,
    TimestampSchema,
):
    """
    Base schema with UUID and timestamps.
    """

    pass


class PaginationSchema(BaseSchema):
    """
    Pagination metadata.
    """

    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_previous: bool
    has_next: bool


class MessageResponse(BaseSchema):
    """
    Generic API message response.
    """

    message: str


class ErrorResponse(BaseSchema):
    """
    Standard API error response.
    """

    error: str
    detail: str | None = None
    code: str | None = None


class HealthResponse(BaseSchema):
    """
    Health endpoint response.
    """

    status: str
    version: str
    timestamp: datetime


class PaginatedResponse[T](BaseSchema):
    """
    Generic paginated response.
    """

    items: list[T]
    pagination: PaginationSchema