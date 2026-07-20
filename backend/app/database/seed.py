"""Database bootstrap orchestration for the synchronous SQLAlchemy layer."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database.seeders.organization import seed_organization
from app.database.seeders.permissions import seed_permissions
from app.database.seeders.role_permissions import seed_role_permissions
from app.database.seeders.roles import seed_roles
from app.database.seeders.users import seed_users
from app.database.seeders.verify import verify_bootstrap
from app.database.session import SessionLocal

logger = logging.getLogger(__name__)


class SeedSummary:
    """Summary of an idempotent bootstrap execution."""

    def __init__(self) -> None:
        self.started_at = datetime.now(timezone.utc)
        self.finished_at: datetime | None = None
        self.organization = None
        self.permissions = 0
        self.roles = 0
        self.users = 0

    @property
    def duration(self) -> float | None:
        if self.finished_at is None:
            return None
        return (self.finished_at - self.started_at).total_seconds()

    def finish(self) -> None:
        self.finished_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, object]:
        return {
            "started_at": self.started_at.isoformat(),
            "finished_at": (
                self.finished_at.isoformat() if self.finished_at else None
            ),
            "duration_seconds": self.duration,
            "organization": (
                self.organization.name if self.organization else None
            ),
            "permissions": self.permissions,
            "roles": self.roles,
            "users": self.users,
        }


def seed_database(db: Session) -> SeedSummary:
    """Run all seeders using the caller-owned transaction."""
    logger.info("Starting QShield database bootstrap.")
    summary = SeedSummary()

    summary.organization = seed_organization(db)
    permissions = seed_permissions(db)
    summary.permissions = len(permissions)

    roles = seed_roles(db)
    summary.roles = len(roles)

    seed_role_permissions(db)
    summary.users = 1 if seed_users(db) else 0

    verify_bootstrap(db)
    summary.finish()

    logger.info(
        "Database bootstrap finished: organization=%s permissions=%d roles=%d "
        "users=%d duration=%.2fs",
        summary.organization.name,
        summary.permissions,
        summary.roles,
        summary.users,
        summary.duration or 0,
    )
    return summary


def initialize_database() -> SeedSummary:
    """Create a session and own the single bootstrap transaction."""
    db = SessionLocal()

    try:
        summary = seed_database(db)
        db.commit()
        logger.info("Database bootstrap committed successfully.")
        return summary
    except Exception:
        db.rollback()
        logger.exception("Database bootstrap failed; transaction rolled back.")
        raise
    finally:
        db.close()
