"""
QShield Enterprise

AI Recommendation Model
"""

from __future__ import annotations


import uuid
from enum import Enum


class RecommendationPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


from sqlalchemy import (
    String,
    Text,
    Index,
)


from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)


from app.database.base import Base

from app.database.mixins import (
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
)



class Recommendation(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Base,
):

    __tablename__ = "recommendations"


    __table_args__ = (

        Index(
            "idx_recommendation_type",
            "category",
        ),

    )


    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )


    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


    severity: Mapped[str] = mapped_column(
        String(50),
        default="medium",
    )


    recommendation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


    asset_id: Mapped[uuid.UUID | None] = mapped_column(
        nullable=True,
    )