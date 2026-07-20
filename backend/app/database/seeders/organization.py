"""
QShield Enterprise
==================

Organization Seeder

Seeds the default QShield organization.

Features
--------
- Async SQLAlchemy
- Idempotent
- Safe to run multiple times
- Returns Organization instance
"""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import (
    Organization,
    OrganizationStatus,
    SubscriptionTier,
)

from app.core.config import settings

logger = logging.getLogger(__name__)


DEFAULT_ORGANIZATION = {
    "name": settings.BOOTSTRAP_ORGANIZATION_NAME,
    "legal_name": settings.BOOTSTRAP_ORGANIZATION_LEGAL_NAME,
    "description": settings.BOOTSTRAP_ORGANIZATION_DESCRIPTION,
    "primary_domain": settings.BOOTSTRAP_DOMAIN,
    "website": settings.BOOTSTRAP_WEBSITE,
    "contact_name": settings.BOOTSTRAP_CONTACT_NAME,
    "contact_email": settings.BOOTSTRAP_CONTACT_EMAIL,
    "contact_phone": settings.BOOTSTRAP_CONTACT_PHONE,
    "country": settings.BOOTSTRAP_COUNTRY,
    "timezone": settings.BOOTSTRAP_TIMEZONE,
    "status": OrganizationStatus.ACTIVE,
    "subscription": SubscriptionTier.ENTERPRISE,
    "enabled": True,
    "max_users": 100000,
    "max_assets": 1000000,
    "max_scans_per_day": 1000000,
}


async def seed_organization(
    db: AsyncSession,
) -> Organization:
    """
    Seed the default organization.

    Safe to execute multiple times.

    Returns
    -------
    Organization
        Existing or newly created organization.
    """

    result = await db.execute(
        select(Organization).where(
            Organization.primary_domain
            == DEFAULT_ORGANIZATION["primary_domain"]
        )
    )

    organization = result.scalar_one_or_none()

    if organization:
        logger.info(
            "Organization already exists: %s",
            organization.name,
        )
        return organization

    organization = Organization(
        **DEFAULT_ORGANIZATION,
    )

    db.add(organization)

    await db.commit()

    await db.refresh(organization)

    logger.info(
        "Created default organization '%s'",
        organization.name,
    )

    return organization