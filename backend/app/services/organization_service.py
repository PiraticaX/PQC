"""
QShield Enterprise

Organization Service

Business logic for organization management.
"""

from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.organization import Organization


class OrganizationService:
    """
    Organization CRUD operations.
    """


    def __init__(
        self,
        db: Session,
    ):
        self.db = db


    async def create(
        self,
        data: dict,
    ) -> Organization:

        organization = Organization(
            **data
        )

        self.db.add(
            organization
        )

        self.db.commit()

        self.db.refresh(
            organization
        )

        return organization



    async def get(
        self,
        organization_id,
    ):

        result = self.db.execute(
            select(Organization)
            .where(
                Organization.id == organization_id
            )
        )

        return result.scalar_one_or_none()



    async def list(self):

        result = self.db.execute(
            select(Organization)
        )

        return result.scalars().all()



    async def delete(
        self,
        organization: Organization,
    ):

        organization.soft_delete()

        self.db.commit()

        return True
