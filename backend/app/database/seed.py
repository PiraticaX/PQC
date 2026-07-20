"""
QShield Enterprise
==================

Database Seeder

Master database bootstrap.

This module orchestrates all database seeders and ensures the
database is initialized in the correct order.

Execution Order
---------------
1. Organization
2. Permissions
3. Roles
4. Role Permissions
5. Users
6. Verification

Safe to execute multiple times.
"""

from __future__ import annotations

import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.seeders.organization import (
    seed_organization,
)
from app.database.seeders.permissions import (
    seed_permissions,
)
from app.database.seeders.roles import (
    seed_roles,
)
from app.database.seeders.role_permissions import (
    seed_role_permissions,
)
from app.database.seeders.users import (
    seed_users,
)
from app.database.seeders.verify import (
    verify_bootstrap,
)

logger = logging.getLogger(__name__)


class SeedSummary:
    """
    Summary of a bootstrap execution.
    """

    def __init__(self) -> None:

        self.started_at = datetime.utcnow()
        self.finished_at: datetime | None = None

        self.organization = None
        self.permissions = 0
        self.roles = 0
        self.users = 0

    @property
    def duration(self) -> float | None:

        if self.finished_at is None:
            return None

        return (
            self.finished_at -
            self.started_at
        ).total_seconds()

    def finish(self) -> None:
        self.finished_at = datetime.utcnow()

    def to_dict(self) -> dict:

        return {

            "started_at": self.started_at.isoformat(),

            "finished_at": (
                self.finished_at.isoformat()
                if self.finished_at
                else None
            ),

            "duration_seconds": self.duration,

            "permissions": self.permissions,

            "roles": self.roles,

            "users": self.users,

            "organization": (
                self.organization.name
                if self.organization
                else None
            ),
        }


async def seed_database(
    db: AsyncSession,
) -> SeedSummary:
    """
    Execute complete database bootstrap.

    This function should be called exactly once
    after database schema creation.

    Returns
    -------
    SeedSummary
    """

    logger.info("")
    logger.info("=" * 70)
    logger.info("Starting QShield Bootstrap")
    logger.info("=" * 70)

    summary = SeedSummary()

    # ---------------------------------------------------------
    # Organization
    # ---------------------------------------------------------

    logger.info("Seeding Organization...")

    summary.organization = await seed_organization(
        db,
    )

    # ---------------------------------------------------------
    # Permissions
    # ---------------------------------------------------------

    logger.info("Seeding Permissions...")

    permissions = await seed_permissions(
        db,
    )

    summary.permissions = len(
        permissions,
    )

    # ---------------------------------------------------------
    # Roles
    # ---------------------------------------------------------

    logger.info("Seeding Roles...")

    roles = await seed_roles(
        db,
    )

    summary.roles = len(
        roles,
    )

        # ---------------------------------------------------------
    # Role Permissions
    # ---------------------------------------------------------

    logger.info("Seeding Role Permissions...")

    await seed_role_permissions(
        db,
    )

    # ---------------------------------------------------------
    # Users
    # ---------------------------------------------------------

    logger.info("Seeding Bootstrap User...")

    user = await seed_users(
        db,
    )

    summary.users = 1 if user else 0

    # ---------------------------------------------------------
    # Verification
    # ---------------------------------------------------------

    logger.info("Running Bootstrap Verification...")

    await verify_bootstrap(
        db,
    )

    summary.finish()

    logger.info("")
    logger.info("=" * 70)
    logger.info("QShield Bootstrap Completed Successfully")
    logger.info("=" * 70)
    logger.info("Organization : %s", summary.organization.name)
    logger.info("Permissions  : %d", summary.permissions)
    logger.info("Roles        : %d", summary.roles)
    logger.info("Users        : %d", summary.users)
    logger.info("Duration     : %.2f seconds", summary.duration)
    logger.info("=" * 70)
    await db.commit()
    return summary


async def initialize_database(
    db: AsyncSession,
) -> SeedSummary:
    """
    Initialize the QShield database.

    This is the public entry point used by
    application startup.

    Parameters
    ----------
    db:
        Active AsyncSession.

    Returns
    -------
    SeedSummary
    """

    try:

        summary = await seed_database(db)

        logger.info(
            "Database bootstrap completed successfully."
        )
        await db.commit()
        return summary

    except Exception:

        logger.exception(
            "Database bootstrap failed."
        )

        await db.rollback()

        raise