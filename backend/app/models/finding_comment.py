"""
QShield Enterprise
==================

Finding Comment Model

Stores analyst comments and investigation notes for findings.

Examples
--------
- Initial triage notes
- Remediation updates
- Risk acceptance discussion
- Verification comments
- Internal analyst communication
"""

from __future__ import annotations

import uuid

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    Text,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base import Base
from app.database.mixins import (
    TimestampMixin,
    UUIDMixin,
)
from app.database.types import GUID


class FindingComment(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    """
    Analyst comment attached to a finding.
    """

    __tablename__ = "finding_comments"

    __table_args__ = (
        Index("idx_finding_comment_finding", "finding_id"),
        Index("idx_finding_comment_author", "author_id"),
    )

    # ============================================================
    # Relationships
    # ============================================================

    finding_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey(
            "findings.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    author_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    # ============================================================
    # Comment
    # ============================================================

    comment: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    internal: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Internal comments are not exposed to external users.",
    )

    edited: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ============================================================
    # Relationships
    # ============================================================

    finding = relationship(
        "Finding",
        back_populates="comments",
    )

    author = relationship(
        "User",
        back_populates="finding_comments",
    )

    # ============================================================
    # Helper Methods
    # ============================================================

    def mark_edited(self) -> None:
        """
        Mark the comment as edited.
        """
        self.edited = True

    # ============================================================
    # Serialization
    # ============================================================

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "finding_id": str(self.finding_id),
            "author_id": (
                str(self.author_id)
                if self.author_id
                else None
            ),
            "comment": self.comment,
            "internal": self.internal,
            "edited": self.edited,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    # ============================================================
    # Representation
    # ============================================================

    def __repr__(self) -> str:
        return (
            "<FindingComment("
            f"id={self.id}, "
            f"finding_id={self.finding_id}"
            ")>"
        )