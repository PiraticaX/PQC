"""
QShield Enterprise
==================

Database Engine

This module is responsible ONLY for creating the SQLAlchemy engine.

No business logic belongs here.

Every database interaction should go through a Session created by
session.py.

Supported databases

- SQLite (Development)
- PostgreSQL (Production)
"""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from app.core.logging import get_logger
from app.core.settings import settings

logger = get_logger(__name__)


def _sqlite_connect_args() -> dict:
    """
    Returns SQLite specific connection arguments.

    SQLite requires check_same_thread=False because FastAPI
    handles requests using multiple threads.
    """

    if settings.database_url.startswith("sqlite"):
        return {"check_same_thread": False}

    return {}


logger.info("Initializing database engine...")

engine: Engine = create_engine(
    settings.database_url,
    connect_args=_sqlite_connect_args(),
    pool_pre_ping=True,
    future=True,
)

logger.info("Database engine initialized.")
logger.info("Database URL: %s", settings.database_url)