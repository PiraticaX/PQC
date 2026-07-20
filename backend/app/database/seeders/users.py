"""
QShield Enterprise
==================

Bootstrap User Seeder

Creates the initial Super Administrator account.

Execution Order
---------------
1. organization.py
2. permissions.py
3. roles.py
4. role_permissions.py
5. users.py

Features
--------
- Async SQLAlchemy
- Idempotent
- Environment driven
- Secure password hashing
- Automatic Super Admin role assignment
"""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password

from app.models.organization import Organization
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole

logger = logging.getLogger(__name__)


# ============================================================
# Bootstrap Configuration
# ============================================================

BOOTSTRAP_ADMIN = {

    "email": settings.BOOTSTRAP_ADMIN_EMAIL,

    "password": settings.BOOTSTRAP_ADMIN_PASSWORD,

    "first_name": settings.BOOTSTRAP_ADMIN_FIRST_NAME,

    "last_name": settings.BOOTSTRAP_ADMIN_LAST_NAME,

    "display_name": (
        f"{settings.BOOTSTRAP_ADMIN_FIRST_NAME} "
        f"{settings.BOOTSTRAP_ADMIN_LAST_NAME}"
    ),

    "verified": True,

    "active": True,

    "superuser": True,
}


# ============================================================
# Helper Functions
# ============================================================

async def get_default_organization(
    db: AsyncSession,
) -> Organization:
    """
    Returns the bootstrap organization.

    Raises
    ------
    RuntimeError
        If the organization has not yet been seeded.
    """

    result = await db.execute(
        select(Organization)
    )

    organization = result.scalar_one_or_none()

    if organization is None:
        raise RuntimeError(
            "Bootstrap organization not found."
        )

    return organization


async def get_super_admin_role(
    db: AsyncSession,
) -> Role:
    """
    Returns the Super Administrator role.

    Raises
    ------
    RuntimeError
        If roles have not yet been seeded.
    """

    result = await db.execute(
        select(Role).where(
            Role.slug == "super-admin"
        )
    )

    role = result.scalar_one_or_none()

    if role is None:
        raise RuntimeError(
            "Super Administrator role not found."
        )

    return role


async def get_existing_admin(
    db: AsyncSession,
    organization_id,
) -> User | None:
    """
    Returns the bootstrap administrator
    if already present.
    """

    result = await db.execute(
        select(User).where(
            User.organization_id == organization_id,
            User.email == BOOTSTRAP_ADMIN["email"],
        )
    )

    return result.scalar_one_or_none()

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

        return summary

    except Exception:

        logger.exception(
            "Database bootstrap failed."
        )

        await db.rollback()

        raise