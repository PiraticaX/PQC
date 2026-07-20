"""
QShield Enterprise
==================

Database Bootstrap

Responsible for:

• Creating the database schema
• Running bootstrap seeders
• Verifying database integrity

Called once during application startup.
"""

from __future__ import annotations

import logging

import app.models  # noqa: F401

from app.database.database import engine
from app.database.session import Base
from app.database.seed import initialize_database

logger = logging.getLogger(__name__)


# ============================================================
# Schema Creation
# ============================================================

def create_schema() -> None:
    """
    Create all database tables.

    Safe to execute multiple times.
    """

    logger.info("=" * 70)
    logger.info("Creating database schema...")
    logger.info("=" * 70)

    Base.metadata.create_all(bind=engine)

    logger.info(
        "Database schema ready (%d tables).",
        len(Base.metadata.tables),
    )


# ============================================================
# Bootstrap
# ============================================================

def bootstrap_database() -> None:
    """
    Initialize the database.

    Creates schema.
    Seeds bootstrap data.
    """

    logger.info("")
    logger.info("=" * 70)
    logger.info("QShield Database Bootstrap")
    logger.info("=" * 70)

    create_schema()

    summary = initialize_database()

    logger.info("")
    logger.info("=" * 70)
    logger.info("Bootstrap Completed Successfully")
    logger.info("=" * 70)

    if summary:
        logger.info(
            "Organization : %s",
            getattr(summary, "organization", "OK"),
        )
        logger.info(
            "Permissions : %s",
            getattr(summary, "permissions", "OK"),
        )
        logger.info(
            "Roles : %s",
            getattr(summary, "roles", "OK"),
        )
        logger.info(
            "Users : %s",
            getattr(summary, "users", "OK"),
        )

    logger.info("=" * 70)


# ============================================================
# Startup Hook
# ============================================================

def startup_database() -> None:
    """
    Public startup entrypoint.

    Called from FastAPI lifespan.
    """

    bootstrap_database()
