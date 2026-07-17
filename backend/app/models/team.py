"""
QShield Enterprise
==================

Team Model

Defines organizational teams.

Examples
--------
- SOC
- Blue Team
- Red Team
- DevSecOps
- Infrastructure
- Compliance
- Executive

A team belongs to exactly one organization and can contain multiple
users through the TeamMember association table.
"""

from __future__ import annotations

import uuid

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base import Base
from app.database.mixins import (
    DescriptionMixin,
    NameMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)
from app.database.types import GUID


class Team(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    DescriptionMixin,
    NameMixin,
    Base,
):
    """
    Organizational Team.

    Teams provide a logical grouping of users for ownership,
    collaboration, and access control.
    """

    __tablename__ = "teams"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "name",
            name="uq_team_org_name",
        ),
        Index(
            "idx_team_org",
            "organization_id",
        ),
        Index(
            "idx_team_enabled",
            "enabled",
        ),
    )

    # ==========================================================
    # Ownership
    # ==========================================================

    organization_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    # ==========================================================
    # Metadata
    # ==========================================================

    display_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        default=100,
        nullable=False,
    )

    # ==========================================================
    # Relationships
    # ==========================================================

    organization = relationship(
        "Organization",
        back_populates="teams",
    )

    members = relationship(
        "TeamMember",
        back_populates="team",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # ==========================================================
    # Helper Properties
    # ==========================================================

    @property
    def member_count(self) -> int:
        """
        Number of active memberships.
        """
        return len(self.members)

    # ==========================================================
    # Business Logic
    # ==========================================================

    def has_member(
        self,
        user_id: uuid.UUID,
    ) -> bool:
        """
        Check whether a user belongs to this team.
        """

        return any(
            member.user_id == user_id
            for member in self.members
        )

    # ==========================================================
    # Serialization
    # ==========================================================

    def to_dict(
        self,
        include_members: bool = False,
    ) -> dict:
        """
        Serialize the team.
        """

        data = {
            "id": str(self.id),
            "organization_id": str(self.organization_id),
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "enabled": self.enabled,
            "priority": self.priority,
            "member_count": self.member_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "deleted_at": (
                self.deleted_at.isoformat()
                if self.deleted_at
                else None
            ),
        }

        if include_members:
            data["members"] = [
                member.user.to_dict()
                for member in self.members
                if member.user is not None
            ]

        return data

    # ==========================================================
    # Representation
    # ==========================================================

    def __repr__(self) -> str:
        return (
            "<Team("
            f"id={self.id}, "
            f"name='{self.name}', "
            f"organization_id={self.organization_id}, "
            f"enabled={self.enabled}"
            ")>"
        )