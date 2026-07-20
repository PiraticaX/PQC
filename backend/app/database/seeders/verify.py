"""
QShield Enterprise
==================

Database Bootstrap Verification

Performs integrity verification after the bootstrap process.

Verification includes:

- Organization
- Permissions
- Roles
- Role mappings
- Bootstrap administrator
- RBAC integrity
- Duplicate detection
- Orphan detection

This module intentionally raises exceptions on failure so the
bootstrap transaction can be rolled back safely.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.permission import Permission
from app.models.role import Role

logger = logging.getLogger(__name__)


# ==============================================================
# Verification Exception
# ==============================================================


class BootstrapVerificationError(RuntimeError):
    """
    Raised when bootstrap verification fails.
    """


# ==============================================================
# Verification Summary
# ==============================================================


@dataclass(slots=True)
class VerificationSummary:

    checks: int = 0

    passed: int = 0

    failed: int = 0

    warnings: list[str] = field(default_factory=list)

    errors: list[str] = field(default_factory=list)

    def success(self) -> bool:

        return self.failed == 0

    def check(
        self,
        condition: bool,
        success_message: str,
        failure_message: str,
    ) -> None:

        self.checks += 1

        if condition:

            self.passed += 1

            logger.info("✓ %s", success_message)

        else:

            self.failed += 1

            self.errors.append(failure_message)

            logger.error("✗ %s", failure_message)


# ==============================================================
# Organization Verification
# ==============================================================


async def verify_organization(
    db: AsyncSession,
    summary: VerificationSummary,
) -> Organization:

    logger.info("Verifying organization...")

    result = await db.execute(
        select(Organization)
    )

    organizations = result.scalars().all()

    summary.check(
        len(organizations) == 1,
        "Bootstrap organization exists.",
        "Expected exactly one bootstrap organization.",
    )

    if not organizations:
        raise BootstrapVerificationError(
            "Bootstrap organization missing."
        )

    organization = organizations[0]

    summary.check(
        organization.enabled,
        "Organization enabled.",
        "Bootstrap organization is disabled.",
    )

    return organization


# ==============================================================
# Permission Verification
# ==============================================================


async def verify_permissions(
    db: AsyncSession,
    summary: VerificationSummary,
) -> None:

    logger.info("Verifying permissions...")

    result = await db.execute(
        select(func.count(Permission.id))
    )

    permission_count = result.scalar_one()

    summary.check(
        permission_count > 0,
        f"{permission_count} permissions available.",
        "No permissions found.",
    )

    duplicate_names = await db.execute(
        select(
            Permission.name,
            func.count(Permission.id),
        )
        .group_by(Permission.name)
        .having(func.count(Permission.id) > 1)
    )

    duplicates = duplicate_names.all()

    summary.check(
        len(duplicates) == 0,
        "Permission names are unique.",
        "Duplicate permission names detected.",
    )


# ==============================================================
# Role Verification
# ==============================================================


SYSTEM_ROLES = {
    "super-admin",
    "admin",
    "security-analyst",
    "compliance-officer",
    "auditor",
    "operator",
    "viewer",
}


async def verify_roles(
    db: AsyncSession,
    summary: VerificationSummary,
) -> None:

    logger.info("Verifying roles...")

    result = await db.execute(
        select(Role)
    )

    roles = result.scalars().all()

    role_slugs = {
        role.slug
        for role in roles
    }

    missing = SYSTEM_ROLES - role_slugs

    summary.check(
        len(missing) == 0,
        "All system roles exist.",
        f"Missing roles: {', '.join(sorted(missing))}",
    )

    duplicate_slugs = await db.execute(
        select(
            Role.slug,
            func.count(Role.id),
        )
        .group_by(Role.slug)
        .having(func.count(Role.id) > 1)
    )

    duplicates = duplicate_slugs.all()

    summary.check(
        len(duplicates) == 0,
        "Role slugs are unique.",
        "Duplicate role slugs detected.",
    )

    disabled = [
        role.slug
        for role in roles
        if not role.enabled
    ]

    summary.check(
        len(disabled) == 0,
        "All system roles enabled.",
        "One or more system roles are disabled.",
    )

    from sqlalchemy import exists

from app.core.config import settings

from app.models.user import User
from app.models.user_role import UserRole
from app.models.role_permission import RolePermission


# ==============================================================
# Role Permission Verification
# ==============================================================


async def verify_role_permissions(
    db: AsyncSession,
    summary: VerificationSummary,
) -> None:

    logger.info("Verifying role-permission mappings...")

    result = await db.execute(
        select(func.count(RolePermission.role_id))
    )

    mapping_count = result.scalar_one()

    summary.check(
        mapping_count > 0,
        f"{mapping_count} role-permission mappings verified.",
        "No role-permission mappings exist.",
    )

    orphan_roles = await db.execute(
        select(RolePermission)
        .where(
            ~exists().where(
                Role.id == RolePermission.role_id
            )
        )
    )

    summary.check(
        len(orphan_roles.scalars().all()) == 0,
        "No orphan role mappings.",
        "Orphan RolePermission records detected.",
    )

    orphan_permissions = await db.execute(
        select(RolePermission)
        .where(
            ~exists().where(
                Permission.id ==
                RolePermission.permission_id
            )
        )
    )

    summary.check(
        len(orphan_permissions.scalars().all()) == 0,
        "No orphan permission mappings.",
        "Orphan Permission mappings detected.",
    )


# ==============================================================
# Bootstrap Administrator Verification
# ==============================================================


async def verify_bootstrap_user(
    db: AsyncSession,
    summary: VerificationSummary,
) -> User:

    logger.info("Verifying bootstrap administrator...")

    result = await db.execute(
        select(User)
        .where(
            User.email ==
            settings.BOOTSTRAP_ADMIN_EMAIL
        )
    )

    user = result.scalar_one_or_none()

    summary.check(
        user is not None,
        "Bootstrap administrator exists.",
        "Bootstrap administrator missing.",
    )

    if user is None:
        raise BootstrapVerificationError(
            "Bootstrap administrator missing."
        )

    summary.check(
        user.is_active,
        "Administrator account active.",
        "Administrator account disabled.",
    )

    summary.check(
        user.is_verified,
        "Administrator account verified.",
        "Administrator account not verified.",
    )

    summary.check(
        user.is_superuser,
        "Administrator is superuser.",
        "Administrator missing superuser flag.",
    )

    return user


# ==============================================================
# User Role Verification
# ==============================================================


async def verify_user_roles(
    db: AsyncSession,
    summary: VerificationSummary,
    user: User,
) -> None:

    logger.info("Verifying administrator role assignment...")

    result = await db.execute(
        select(UserRole)
        .join(Role)
        .where(
            UserRole.user_id == user.id,
            Role.slug == "super-admin",
        )
    )

    summary.check(
        result.scalar_one_or_none() is not None,
        "Administrator has Super Admin role.",
        "Administrator missing Super Admin role.",
    )


# ==============================================================
# Database Integrity
# ==============================================================


async def verify_integrity(
    db: AsyncSession,
    summary: VerificationSummary,
) -> None:

    logger.info("Running integrity checks...")

    orphan_user_roles = await db.execute(
        select(UserRole)
        .where(
            ~exists().where(
                User.id == UserRole.user_id
            )
        )
    )

    summary.check(
        len(orphan_user_roles.scalars().all()) == 0,
        "No orphan UserRole records.",
        "Orphan UserRole records detected.",
    )


# ==============================================================
# Bootstrap Verification
# ==============================================================


async def verify_bootstrap(
    db: AsyncSession,
) -> VerificationSummary:
    """
    Perform complete bootstrap verification.

    Raises
    ------
    BootstrapVerificationError
        If any verification fails.
    """

    logger.info("")
    logger.info("=" * 70)
    logger.info("Verifying QShield Bootstrap")
    logger.info("=" * 70)

    summary = VerificationSummary()

    await verify_organization(
        db,
        summary,
    )

    await verify_permissions(
        db,
        summary,
    )

    await verify_roles(
        db,
        summary,
    )

    await verify_role_permissions(
        db,
        summary,
    )

    user = await verify_bootstrap_user(
        db,
        summary,
    )

    await verify_user_roles(
        db,
        summary,
        user,
    )

    await verify_integrity(
        db,
        summary,
    )

    logger.info("")
    logger.info("=" * 70)
    logger.info(
        "Verification: %d passed | %d failed",
        summary.passed,
        summary.failed,
    )
    logger.info("=" * 70)

    if not summary.success():

        logger.error("Bootstrap verification failed.")

        for error in summary.errors:
            logger.error(" • %s", error)

        raise BootstrapVerificationError(
            "Database bootstrap verification failed."
        )

    logger.info(
        "Bootstrap verification completed successfully."
    )

    return summary