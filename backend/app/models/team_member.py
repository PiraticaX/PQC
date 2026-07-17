"""
QShield Enterprise
==================

Team Member Association

Associates users with teams.

Unlike a simple association table, TeamMember stores metadata about the
membership itself.

Examples
--------
- Team Lead
- Primary Team
- Joined Date
- Active Membership
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from sqlalchemy.sql import func

from app.database.base import Base
from app.database.types import GUID


class TeamMember(Base):
    """
    Associates a User with a Team.
    """

    __tablename__ = "team_members"

    __table_args__ = (
        Index(
            "idx_team_member_team",
            "team_id",
        ),
        Index(
            "idx_team_member_user",
            "user_id",
        ),
    )

    # ==========================================================
    # Composite Primary Key
    # ==========================================================

    team_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey(
            "teams.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    # ==========================================================
    # Membership Metadata
    # ==========================================================

    is_team_lead: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Indicates whether the user leads this team.",
    )

    is_primary_team: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Marks this as the user's primary team.",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ==========================================================
    # Relationships
    # ==========================================================

    team = relationship(
        "Team",
        back_populates="members",
    )

    user = relationship(
        "User",
        back_populates="team_memberships",
    )

    # ==========================================================
    # Serialization
    # ==========================================================

    def to_dict(self) -> dict:
        return {
            "team_id": str(self.team_id),
            "user_id": str(self.user_id),
            "is_team_lead": self.is_team_lead,
            "is_primary_team": self.is_primary_team,
            "is_active": self.is_active,
            "joined_at": self.joined_at.isoformat(),
        }

    # ==========================================================
    # Representation
    # ==========================================================

    def __repr__(self) -> str:
        return (
            "<TeamMember("
            f"team_id={self.team_id}, "
            f"user_id={self.user_id}, "
            f"team_lead={self.is_team_lead}"
            ")>"
        )