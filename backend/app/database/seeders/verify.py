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

from sqlalchemy import exists, func, select
from sqlalchemy.orm import Session

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


def verify_organization(
    db: Session,
    summary: VerificationSummary,
) -> Organization:

    logger.info("Verifying organization...")

    result = db.execute(
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


def verify_permissions(
    db: Session,
    summary: VerificationSummary,
) -> None:

    logger.info("Verifying permissions...")

    result = db.execute(
        select(func.count(Permission.id))
    )

    permission_count = result.scalar_one()

    summary.check(
        permission_count > 0,
        f"{permission_count} permissions available.",
        "No permissions found.",
    )

    duplicate_names = db.execute(
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


def verify_roles(
    db: Session,
    summary: VerificationSummary,
) -> None:

    logger.info("Verifying roles...")

    result = db.execute(
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

    duplicate_slugs = db.execute(
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

from app.core.config import settings

from app.models.user import User
from app.models.user_role import UserRole
from app.models.role_permission import RolePermission


# ==============================================================
# Role Permission Verification
# ==============================================================


def verify_role_permissions(
    db: Session,
    summary: VerificationSummary,
) -> None:

    logger.info("Verifying role-permission mappings...")

    result = db.execute(
        select(func.count(RolePermission.role_id))
    )

    mapping_count = result.scalar_one()

    summary.check(
        mapping_count > 0,
        f"{mapping_count} role-permission mappings verified.",
        "No role-permission mappings exist.",
    )

    orphan_roles = db.execute(
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

    orphan_permissions = db.execute(
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


def verify_bootstrap_user(
    db: Session,
    summary: VerificationSummary,
) -> User:

    logger.info("Verifying bootstrap administrator...")

    result = db.execute(
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


def verify_user_roles(
    db: Session,
    summary: VerificationSummary,
    user: User,
) -> None:

    logger.info("Verifying administrator role assignment...")

    result = db.execute(
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


def verify_integrity(
    db: Session,
    summary: VerificationSummary,
) -> None:

    logger.info("Running integrity checks...")

    orphan_user_roles = db.execute(
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


def verify_bootstrap(
    db: Session,
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

    verify_organization(
        db,
        summary,
    )

    verify_permissions(
        db,
        summary,
    )

    verify_roles(
        db,
        summary,
    )

    verify_role_permissions(
        db,
        summary,
    )

    user = verify_bootstrap_user(
        db,
        summary,
    )

    verify_user_roles(
        db,
        summary,
        user,
    )

    verify_integrity(
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
