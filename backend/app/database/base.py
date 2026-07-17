"""
QShield Enterprise
==================

SQLAlchemy Declarative Base

This module defines the application's global declarative base.

Every ORM model in the project must inherit (directly or indirectly)
from this Base class.

Example
-------
from app.database.base import Base

class Asset(Base):
    __tablename__ = "assets"
"""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Root declarative base for all SQLAlchemy ORM models.

    Additional SQLAlchemy-wide configuration can be added here in the
    future if required.
    """

    pass