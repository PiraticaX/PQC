"""Bootstrap user seeder for the synchronous database transaction."""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole

logger = logging.getLogger(__name__)

BOOTSTRAP_ADMIN = {
    "email": settings.BOOTSTRAP_ADMIN_EMAIL,
    "password": settings.BOOTSTRAP_ADMIN_PASSWORD,
    "first_name": settings.BOOTSTRAP_ADMIN_FIRST_NAME,
    "last_name": settings.BOOTSTRAP_ADMIN_LAST_NAME,
    "display_name": (
        f"{settings.BOOTSTRAP_ADMIN_FIRST_NAME} "
        f"{settings.BOOTSTRAP_ADMIN_LAST_NAME}"
    ),
    "is_verified": True,
    "is_active": True,
    "is_superuser": True,
}


def get_default_organization(db: Session) -> Organization:
    """Return the organization created by the organization seeder."""
    organization = db.execute(select(Organization)).scalar_one_or_none()
    if organization is None:
        raise RuntimeError("Bootstrap organization not found.")
    return organization


def get_super_admin_role(db: Session) -> Role:
    """Return the built-in Super Administrator role."""
    role = db.execute(
        select(Role).where(Role.slug == "super-admin")
    ).scalar_one_or_none()
    if role is None:
        raise RuntimeError("Super Administrator role not found.")
    return role


def get_existing_admin(db: Session, organization_id: object) -> User | None:
    """Return an existing bootstrap administrator for the organization."""
    return db.execute(
        select(User).where(
            User.organization_id == organization_id,
            User.email == BOOTSTRAP_ADMIN["email"],
        )
    ).scalar_one_or_none()


def seed_users(db: Session) -> User:
    """Seed the bootstrap administrator and its Super Administrator role."""
    organization = get_default_organization(db)
    role = get_super_admin_role(db)
    user = get_existing_admin(db, organization.id)

    if user is None:
        user = User(
            organization_id=organization.id,
            email=BOOTSTRAP_ADMIN["email"],
            password_hash=hash_password(BOOTSTRAP_ADMIN["password"]),
            first_name=BOOTSTRAP_ADMIN["first_name"],
            last_name=BOOTSTRAP_ADMIN["last_name"],
            display_name=BOOTSTRAP_ADMIN["display_name"],
            is_verified=BOOTSTRAP_ADMIN["is_verified"],
            is_active=BOOTSTRAP_ADMIN["is_active"],
            is_superuser=BOOTSTRAP_ADMIN["is_superuser"],
        )
        db.add(user)
        db.flush()
        logger.info("Created bootstrap administrator %s.", user.email)
    else:
        logger.info("Bootstrap administrator already exists: %s.", user.email)

    user_role = db.execute(
        select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == role.id,
        )
    ).scalar_one_or_none()

    if user_role is None:
        db.add(UserRole(user_id=user.id, role_id=role.id))
        db.flush()
        logger.info("Assigned Super Administrator role to %s.", user.email)

    db.refresh(user)
    return user
