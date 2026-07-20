"""
QShield Enterprise
==================

Role Seeder

Seeds all built-in system roles.

Features
--------
- Synchronous SQLAlchemy
- Idempotent
- Enterprise RBAC
- Safe to execute multiple times
- Automatic updates
- Global system roles

Execution Order
---------------
1. Organization Seeder
2. Permission Seeder
3. Role Seeder
4. Role-Permission Seeder
5. User Seeder
"""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.role import Role

logger = logging.getLogger(__name__)

# ==========================================================
# Built-in System Roles
# ==========================================================

SYSTEM_ROLES: list[dict] = [

    {
        "name": "Super Administrator",
        "display_name": "Super Administrator",
        "slug": "super-admin",
        "description": (
            "Full unrestricted access to every feature "
            "across the platform."
        ),
        "priority": 1,
        "editable": False,
        "system_role": True,
        "enabled": True,
    },

    {
        "name": "Administrator",
        "display_name": "Administrator",
        "slug": "admin",
        "description": (
            "Administrative access to the organization."
        ),
        "priority": 10,
        "editable": False,
        "system_role": True,
        "enabled": True,
    },

    {
        "name": "Security Analyst",
        "display_name": "Security Analyst",
        "slug": "security-analyst",
        "description": (
            "Performs assessments, triages findings, "
            "and manages assets."
        ),
        "priority": 30,
        "editable": True,
        "system_role": True,
        "enabled": True,
    },

    {
        "name": "Compliance Officer",
        "display_name": "Compliance Officer",
        "slug": "compliance-officer",
        "description": (
            "Responsible for compliance, reporting "
            "and policy management."
        ),
        "priority": 40,
        "editable": True,
        "system_role": True,
        "enabled": True,
    },

    {
        "name": "Auditor",
        "display_name": "Auditor",
        "slug": "auditor",
        "description": (
            "Read-only access to reports, audit logs "
            "and compliance information."
        ),
        "priority": 50,
        "editable": True,
        "system_role": True,
        "enabled": True,
    },

    {
        "name": "Operator",
        "display_name": "Operator",
        "slug": "operator",
        "description": (
            "Day-to-day operations including scans "
            "and asset inventory."
        ),
        "priority": 60,
        "editable": True,
        "system_role": True,
        "enabled": True,
    },

    {
        "name": "Viewer",
        "display_name": "Viewer",
        "slug": "viewer",
        "description": (
            "Read-only access throughout the platform."
        ),
        "priority": 100,
        "editable": True,
        "system_role": True,
        "enabled": True,
    },
]
def seed_roles(
    db: Session,
) -> list[Role]:
    """
    Seed all built-in system roles.

    Existing roles are updated.
    Missing roles are created.

    Safe to execute multiple times.
    """

    logger.info("Seeding system roles...")

    seeded_roles: list[Role] = []

    for item in SYSTEM_ROLES:

        result = db.execute(
            select(Role).where(
                Role.slug == item["slug"]
            )
        )

        role = result.scalar_one_or_none()

        if role is None:

            role = Role(
                organization_id=None,
                name=item["name"],
                display_name=item["display_name"],
                slug=item["slug"],
                description=item["description"],
                priority=item["priority"],
                editable=item["editable"],
                system_role=item["system_role"],
                enabled=item["enabled"],
            )

            db.add(role)

            logger.info(
                "Created system role: %s",
                role.name,
            )

        else:

            role.name = item["name"]
            role.display_name = item["display_name"]
            role.description = item["description"]
            role.priority = item["priority"]
            role.editable = item["editable"]
            role.system_role = item["system_role"]
            role.enabled = item["enabled"]

            logger.info(
                "Updated system role: %s",
                role.name,
            )

        seeded_roles.append(role)

    # Refresh all instances so IDs and timestamps are available
    db.flush()

    for role in seeded_roles:
        db.refresh(role)

    logger.info(
        "Successfully seeded %d system roles.",
        len(seeded_roles),
    )

    return seeded_roles


def get_system_role(
    db: Session,
    slug: str,
) -> Role | None:
    """
    Retrieve a built-in system role by slug.

    Parameters
    ----------
    db:
        Active Session.

    slug:
        System role slug.

    Returns
    -------
    Role | None
    """

    result = db.execute(
        select(Role).where(
            Role.slug == slug,
            Role.system_role.is_(True),
        )
    )

    return result.scalar_one_or_none()


def list_system_roles(
    db: Session,
) -> list[Role]:
    """
    Return all built-in system roles ordered by priority.
    """

    result = db.execute(
        select(Role)
        .where(
            Role.system_role.is_(True),
            Role.deleted_at.is_(None),
        )
        .order_by(
            Role.priority.asc(),
            Role.name.asc(),
        )
    )

    return list(result.scalars().all())
