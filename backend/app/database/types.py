"""
QShield Enterprise
==================

Custom SQLAlchemy Types

This module provides database-independent SQLAlchemy column types.

Currently implemented
---------------------

GUID
    UUID type that automatically selects the appropriate database type.

    PostgreSQL
        Native UUID

    SQLite
        CHAR(36)

This allows the same ORM models to work on both SQLite (development)
and PostgreSQL (production) without modification.
"""

from __future__ import annotations

import uuid

from sqlalchemy import CHAR
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.types import TypeDecorator


class GUID(TypeDecorator):
    """
    Platform-independent UUID type.

    Examples
    --------

    id = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid.uuid4,
    )
    """

    impl = CHAR

    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect):
        """
        Select the appropriate database type.
        """

        if dialect.name == "postgresql":
            return dialect.type_descriptor(
                UUID(as_uuid=True)
            )

        return dialect.type_descriptor(
            CHAR(36)
        )

    def process_bind_param(
        self,
        value,
        dialect: Dialect,
    ):
        """
        Convert Python UUID into database representation.
        """

        if value is None:
            return None

        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(str(value))

        if dialect.name == "postgresql":
            return value

        return str(value)

    def process_result_value(
        self,
        value,
        dialect: Dialect,
    ):
        """
        Convert database value back into Python UUID.
        """

        if value is None:
            return None

        if isinstance(value, uuid.UUID):
            return value

        return uuid.UUID(str(value))