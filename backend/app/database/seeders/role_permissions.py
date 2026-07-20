"""
QShield Enterprise
==================

Role Permission Seeder

Assigns built-in permissions to built-in system roles.

Execution Order
---------------
1. organization.py
2. permissions.py
3. roles.py
4. role_permissions.py
5. users.py
"""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission

logger = logging.getLogger(__name__)

# ============================================================
# Built-in Role Permission Matrix
# ============================================================

ROLE_PERMISSION_MAP: dict[str, list[str]] = {

    # --------------------------------------------------------
    # Super Administrator
    # --------------------------------------------------------

    "super-admin": [
        "*",
    ],

    # --------------------------------------------------------
    # Administrator
    # --------------------------------------------------------

    "admin": [

        # Organization
        "organization:manage",

        # Users
        "user:manage",
        "user:assign-role",
        "user:reset-password",

        # Roles
        "role:manage",

        # Teams
        "team:manage",

        # Assets
        "asset:manage",

        # Asset Groups
        "asset-group:manage",

        # Scans
        "scan:manage",

        # Scheduled Scans
        "scheduled-scan:manage",

        # Findings
        "finding:manage",

        # Reports
        "report:manage",

        # Compliance
        "compliance:manage",

        # Policies
        "policy:manage",

        # API Keys
        "api-key:manage",

        # Integrations
        "integration:manage",

        # Notifications
        "notification:manage",

        # Audit
        "audit:read",
        "audit:export",

        # Settings
        "settings:read",
        "settings:update",

        # PQC
        "pqc:manage",

        # AI
        "ai:manage",
    ],

    # --------------------------------------------------------
    # Security Analyst
    # --------------------------------------------------------

    "security-analyst": [

        "dashboard:view",
        "dashboard:analytics",

        "asset:read",
        "asset:update",
        "asset:list",
        "asset:discover",

        "asset-group:read",
        "asset-group:list",

        "scan:create",
        "scan:run",
        "scan:cancel",
        "scan:list",
        "scan:read",

        "scheduled-scan:create",
        "scheduled-scan:update",
        "scheduled-scan:list",

        "finding:read",
        "finding:update",
        "finding:assign",
        "finding:resolve",
        "finding:list",

        "report:create",
        "report:read",
        "report:export",

        "notification:send",

        "pqc:view",
        "pqc:scan",
        "pqc:recommend",

        "ai:chat",
        "ai:recommend",
        "ai:triage",
    ],

    # --------------------------------------------------------
    # Compliance Officer
    # --------------------------------------------------------

    "compliance-officer": [

        "dashboard:view",

        "report:read",
        "report:list",
        "report:export",
        "report:share",

        "finding:read",
        "finding:list",

        "compliance:manage",

        "policy:manage",

        "audit:read",
        "audit:export",

        "settings:read",
    ],

        # --------------------------------------------------------
    # Auditor
    # --------------------------------------------------------

    "auditor": [

        "dashboard:view",

        "asset:read",
        "asset:list",

        "asset-group:read",
        "asset-group:list",

        "scan:read",
        "scan:list",

        "finding:read",
        "finding:list",

        "report:read",
        "report:list",
        "report:export",

        "audit:read",
        "audit:export",

        "compliance:read",

        "policy:read",
    ],

    # --------------------------------------------------------
    # Operator
    # --------------------------------------------------------

    "operator": [

        "dashboard:view",

        "asset:read",
        "asset:update",
        "asset:list",

        "asset-group:read",

        "scan:create",
        "scan:run",
        "scan:cancel",
        "scan:read",
        "scan:list",

        "scheduled-scan:create",
        "scheduled-scan:update",
        "scheduled-scan:list",

        "finding:read",
        "finding:update",
        "finding:list",

        "report:read",

        "notification:send",
    ],

    # --------------------------------------------------------
    # Viewer
    # --------------------------------------------------------

    "viewer": [

        "dashboard:view",

        "asset:read",
        "asset:list",

        "asset-group:read",
        "asset-group:list",

        "scan:read",
        "scan:list",

        "finding:read",
        "finding:list",

        "report:read",
        "report:list",

        "compliance:read",

        "policy:read",
    ],
}


def seed_role_permissions(
    db: Session,
) -> None:
    """
    Seed built-in role permissions.

    Existing mappings are preserved.
    Missing mappings are created.

    Safe to execute multiple times.
    """

    logger.info("Seeding role permissions...")

    roles_result = db.execute(select(Role))
    roles = {
        role.slug: role
        for role in roles_result.scalars().all()
    }

    permissions_result = db.execute(select(Permission))
    permissions = {
        permission.name: permission
        for permission in permissions_result.scalars().all()
    }

    created = 0

    for role_slug, permission_names in ROLE_PERMISSION_MAP.items():

        role = roles.get(role_slug)

        if role is None:
            logger.warning(
                "Role '%s' not found.",
                role_slug,
            )
            continue

        for permission_name in permission_names:

            permission = permissions.get(permission_name)

            if permission is None:
                logger.warning(
                    "Permission '%s' not found.",
                    permission_name,
                )
                continue

            existing = db.execute(
                select(RolePermission).where(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == permission.id,
                )
            )

            if existing.scalar_one_or_none():
                continue

            db.add(
                RolePermission(
                    role_id=role.id,
                    permission_id=permission.id,
                )
            )

            created += 1

    db.flush()

    logger.info(
        "Created %d role-permission mappings.",
        created,
    )


def get_role_permissions(
    db: Session,
    role_slug: str,
) -> list[str]:
    """
    Return permission names assigned to a role.
    """

    result = db.execute(
        select(Role)
        .where(Role.slug == role_slug)
    )

    role = result.scalar_one_or_none()

    if role is None:
        return []

    db.refresh(role)

    return sorted(
        [
            rp.permission.name
            for rp in role.role_permissions
            if rp.permission is not None
        ]
    )
